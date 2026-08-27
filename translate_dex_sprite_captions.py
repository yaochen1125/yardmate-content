#!/usr/bin/env python3
"""Generate i18n/<locale>/dex_sprite_captions.json overlays for Plantdex foil-card
sprite captions (1676 strings, one flavor line per species).

Source of record is the App bundle resource
`yardmate-swiftui/.../Resources/Content/dex_sprite_captions.json` — English is the
base and ships in the ipa; only the per-locale overlays live on the CDN.

Engine: DeepSeek (same key / same HTTP-direct pattern as translate_explore_themes.py
and catalog-promote-tool/translate_mt.py).

zh-Hant is **derived from zh-Hans** (OpenCC `s2twp`, Taiwan wording) — never a second
API call. Canonical plant names are re-pinned after conversion from plants_names_i18n.

Quality gates per batch: id set intact, no empties, CJK script present (CJK locales),
sprite term present, length budget. Over-long lines get a compression pass; captions
that name the plant but miss the canonical name get a repair pass.

Run: python3 translate_dex_sprite_captions.py             # all 10 locales
     python3 translate_dex_sprite_captions.py ja de       # a subset
Resumable: per-(locale,batch) results cached in .translate_cache/dex_sprite_captions/.
"""
import concurrent.futures
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

import opencc

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT, ".translate_cache", "dex_sprite_captions")
NAMES_PATH = os.path.join(ROOT, "plants_names_i18n.json")
INDEX_PATH = os.path.join(ROOT, "plants_index.json")

# English base lives in the App repo (bundled resource, not a CDN file). Main
# checkout first, then the active worktree — whichever has the file.
SOURCE_CANDIDATES = [
    os.path.join(ROOT, "..", "yardmate-swiftui", "app", "YardMate", "YardMate",
                 "Resources", "Content", "dex_sprite_captions.json"),
    os.path.join(ROOT, "..", "yardmate-swiftui", ".claude", "worktrees",
                 "clever-kepler-05887c", "app", "YardMate", "YardMate",
                 "Resources", "Content", "dex_sprite_captions.json"),
]

BATCH = 20
WORKERS = 16
PROMPT_VERSION = "v2"          # bump to invalidate the cache after a prompt change

_S2T = opencc.OpenCC("s2twp")  # 简→繁（Taiwan 用词），派生 zh-Hant

LANG_NAMES = {
    "de": "German", "es": "Spanish", "fr": "French", "it": "Italian",
    "ja": "Japanese", "ko": "Korean", "pt": "Portuguese (European)",
    "vi": "Vietnamese", "zh-Hans": "Simplified Chinese",
}
MT_LOCALES = list(LANG_NAMES)          # the 9 that actually hit the API
ALL_LOCALES = MT_LOCALES + ["zh-Hant"]

# Frozen rendering of "sprite" per locale — the word appears in all 1676 source
# lines, so one drifting batch is visible as mixed vocabulary across the deck.
SPRITE_TERM = {
    "de": "Elfen", "es": "duendes", "fr": "lutins", "it": "folletti",
    "ja": "妖精", "ko": "요정", "pt": "duendes", "vi": "tinh linh",
    "zh-Hans": "小精灵",
}
# Substring stem used to verify the term survived (covers inflections).
SPRITE_STEM = {
    "de": "elfe", "es": "duende", "fr": "lutin", "it": "follett",
    "ja": "妖精", "ko": "요정", "pt": "duende", "vi": "tinh linh",
    "zh-Hans": "小精灵", "zh-Hant": "小精靈",
}
# Card gives one italic 10pt line ~248pt wide (wraps to 2 lines). TARGET is the
# soft aim quoted in the prompt; HARD is what triggers a compression pass and what
# QA reports against. Two numbers because a single hard "at most N" makes the model
# amputate the imagery — the smoke test came back at 14–20 zh chars, far too terse.
TARGET_LEN = {
    "ja": 30, "ko": 34, "zh-Hans": 28, "zh-Hant": 28,
    "de": 90, "es": 88, "fr": 88, "it": 88, "pt": 88, "vi": 88,
}
MAX_LEN = {
    "ja": 34, "ko": 40, "zh-Hans": 32, "zh-Hant": 32,
    "de": 100, "es": 96, "fr": 96, "it": 96, "pt": 96, "vi": 96,
}

_CJK_LOCALES = {"ja", "ko", "zh-Hans"}
_API = "https://api.deepseek.com/chat/completions"


def load_key():
    path = os.path.expanduser("~/.config/yardmate-api/deepseek.env")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("DEEPSEEK_API_KEY not found")


API_KEY = load_key()


def call_deepseek(system, user, temperature=1.0, timeout=180, retries=4):
    body = json.dumps({
        "model": "deepseek-chat",
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode()
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {API_KEY}"}
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(_API, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                api = json.load(resp)
            return json.loads(api["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as e:
            # 400/401/403/404 = bad request / auth — retrying only adds rate pressure.
            if e.code in (400, 401, 403, 404):
                raise RuntimeError(f"DeepSeek HTTP {e.code} (not retryable): {e}") from e
            last = e
            if attempt < retries - 1:
                ra = (e.headers.get("Retry-After") if e.headers else None) or ""
                time.sleep(float(ra) if ra.strip().isdigit() else 2 ** attempt)
        except Exception as e:  # noqa: BLE001 — network/timeout/JSON: back off and retry
            last = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"DeepSeek call failed: {last}")


def system_prompt(locale):
    lang = LANG_NAMES[locale]
    term = SPRITE_TERM[locale]
    target, hard = TARGET_LEN[locale], MAX_LEN[locale]
    lo = int(target * 0.65)
    unit = "characters (count CJK glyphs)" if locale in _CJK_LOCALES else "characters"
    return (
        f"You localize FLAVOR TEXT for YardMate's Plantdex collectible plant cards into {lang}.\n\n"
        f"Each line is one whimsical, fairy-tale vignette of tiny garden sprites at work on a plant. "
        f"It is printed in small italics on the card face — it is a storybook aside, NOT an "
        f"encyclopedia caption.\n\n"
        "Rules:\n"
        f"1. TONE: playful, storybook, personified. Present tense. Keep the source's concrete, "
        f"tactile imagery (tools, tiny vessels, verbs). Never flatten it into dry botanical prose.\n"
        f"2. TERM LOCK: render \"sprites\" as \"{term}\" every single time — never a synonym, "
        f"never a different word between lines.\n"
        f"3. LENGTH: aim for {lo}\u2013{target} {unit} per line; never exceed {hard}. This is a "
        f"RANGE, not a race to the shortest — do NOT amputate the scene. The concrete detail "
        f"(the tools, the vessels, what the sprites are DOING) must survive; trim ornamental "
        f"adjectives first if you must trim.\n"
        f"4. PLANT NAME: each item may carry \"plant\" — the app's canonical {lang} name for that "
        f"species. If the English line names the plant, use that exact canonical name, verbatim. "
        f"If the English line does NOT name the plant (it just says \"the blossoms\", \"the leaves\"), "
        f"do NOT insert the name — keep the generic wording.\n"
        "5. Keep Latin scientific names unchanged. Keep Arabic numerals.\n"
        f"6. Output natural, idiomatic {lang} — never word-by-word machine style.\n\n"
        "Reply ONLY with a JSON object mapping every input id to its translated line: "
        "{\"id\": \"translation\", ...}. Same ids, nothing else."
    )


def build_user(items, locale):
    payload = []
    for it in items:
        row = {"id": it["id"], "en": it["en"]}
        if it.get("plant"):
            row["plant"] = it["plant"]
        payload.append(row)
    return (f"Translate every \"en\" into {LANG_NAMES[locale]}. Return JSON "
            f"{{id: translation}} with the SAME ids:\n"
            + json.dumps(payload, ensure_ascii=False))


def _has_cjk(s):
    return any("぀" <= c <= "ヿ" or "㐀" <= c <= "鿿"
               or "가" <= c <= "힯" for c in s)


def _validate(out, items, locale):
    """Raise on anything that would poison the overlay. Length is checked later
    (a separate compression pass), so it is not fatal here."""
    for it in items:
        v = out.get(it["id"])
        if not isinstance(v, str) or not v.strip():
            raise RuntimeError(f"{locale}: missing/empty id {it['id']}")
    if locale in _CJK_LOCALES:
        hits = sum(1 for it in items if _has_cjk(out[it["id"]]))
        if hits < len(items):
            raise RuntimeError(f"{locale}: {len(items)-hits} lines lack CJK — untranslated")
    stem = SPRITE_STEM[locale]
    miss = [it["id"] for it in items if stem not in out[it["id"]].lower()]
    # One-off phrasings ("A lone sprite…") can legitimately drop the stem; a whole
    # batch missing it means the term lock broke.
    if len(miss) > max(2, len(items) // 4):
        raise RuntimeError(f"{locale}: sprite term '{stem}' missing in {len(miss)}/{len(items)}")


def translate_batch(locale, items, batch_idx):
    key = hashlib.sha256(
        (PROMPT_VERSION + locale + json.dumps(items, ensure_ascii=False, sort_keys=True))
        .encode()).hexdigest()[:20]
    cache_path = os.path.join(CACHE_DIR, locale, f"{key}.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return batch_idx, json.load(f)

    system, user = system_prompt(locale), build_user(items, locale)
    last = None
    for attempt in range(4):
        try:
            got = call_deepseek(system, user)
            out = {it["id"]: str(got.get(it["id"], "")).strip() for it in items}
            _validate(out, items, locale)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w") as f:
                json.dump(out, f, ensure_ascii=False)
            return batch_idx, out
        except Exception as e:  # noqa: BLE001 — retry API + validation failures alike
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{locale} batch {batch_idx}: {last}")


def compress(locale, entries):
    """Second pass over lines that blew the length budget. entries = [(id, text, en)]."""
    limit = TARGET_LEN[locale]
    payload = [{"id": i, "current": t, "en": en} for i, t, en in entries]
    system = system_prompt(locale)
    user = (
        f"These {LANG_NAMES[locale]} card lines are TOO LONG. Rewrite each to at most "
        f"{limit} characters while keeping the sprites' action, the storybook tone, the term "
        f"\"{SPRITE_TERM[locale]}\", and any canonical plant name already present. Drop "
        f"ornamental adjectives and merge clauses; do not drop the action.\n"
        "Return JSON {id: shortened} with the SAME ids:\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    got = call_deepseek(system, user, temperature=0.8)
    out = {}
    for i, cur, _en in entries:
        v = got.get(i)
        if isinstance(v, str) and v.strip():
            v = v.strip()
            # Keep the rewrite only if it is genuinely shorter and still on-term.
            if len(v) < len(cur) and SPRITE_STEM[locale] in v.lower():
                out[i] = v
    return out


def repair_names(locale, entries):
    """Lines whose English names the plant but whose translation dropped the canonical
    name. entries = [(id, text, en, plant)]."""
    payload = [{"id": i, "current": t, "en": en, "plant": p} for i, t, en, p in entries]
    system = system_prompt(locale)
    user = (
        f"Each of these {LANG_NAMES[locale]} card lines translates an English line that NAMES the "
        f"plant, but the translation does not use the app's canonical name. Rewrite each so it uses "
        f"the app's canonical \"plant\" name, keeping the tone, the term \"{SPRITE_TERM[locale]}\", "
        f"and the {MAX_LEN[locale]}-character ceiling.\n"
        "Decline/inflect the name grammatically if the sentence requires it, but never "
        "substitute a different name, a descriptive paraphrase, or a transliteration.\n"
        "Return JSON {id: rewritten} with the SAME ids:\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    got = call_deepseek(system, user, temperature=0.8)
    out = {}
    for i, _cur, _en, plant in entries:
        v = got.get(i)
        if isinstance(v, str) and v.strip() and name_present(v.strip(), plant, locale):
            out[i] = v.strip()
    return out


# --- plant-name mention heuristic ------------------------------------------------
# Head-noun stoplist: words too generic to prove a caption is naming THIS species.
_STOP = {"the", "and", "common", "garden", "wild", "false", "true", "dwarf",
         "giant", "great", "little", "plant", "tree", "bush", "shrub", "vine",
         "grass", "leaf", "leaves", "flower", "flowers", "weed", "moss",
         "berry", "berries", "wort", "plants", "trees"}


def name_tokens(common_name):
    """The HEAD NOUN of an English common name — the only token whose presence
    proves the caption really is naming that species.

    Head-noun-only on purpose: taking every token made "Glossy Abelia" match a
    caption about "the glossy hedge leaves", which then dragged the canonical name
    into a line the English never named.
    """
    toks = [t.lower() for t in re.findall(r"[A-Za-z]{4,}", common_name or "")]
    toks = [t for t in toks if t not in _STOP]
    return toks[-1:] if toks else []


def _fold(s):
    """lowercase + strip diacritics, so Spanish "ásteres" still matches "aster"."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if not unicodedata.combining(c))


def name_present(text, plant, locale):
    """Is the canonical name really used here?

    Exact substring for CJK. For inflecting languages an exact match is the wrong
    test — German correctly writes "der Chinesischen Abelie" for the canonical
    "Chinesische Abelie", and rejecting that would loop the repair pass forever.
    So there: every content token of the name must appear by stem.
    """
    if not plant:
        return True
    if plant in text:
        return True
    if locale in _CJK_LOCALES or locale == "zh-Hant":
        return False
    low = _fold(text)
    # 2-char floor, not 3: Vietnamese canonical names are routinely two letters
    # ("Lê", "Bí đỏ") and a 3-char floor left them with no tokens at all -> always miss.
    toks = [_fold(t) for t in re.findall(r"[^\W\d_]{2,}", plant, re.UNICODE)]
    toks = [t for t in toks if t]
    if not toks:
        return False
    return all(t[:max(4, len(t) - 2)] in low for t in toks)


def mentions_plant(en, toks):
    low = en.lower()
    for t in toks:
        # crude singular/plural tolerance; 'abelia' matches 'abelias'
        if re.search(rf"\b{re.escape(t)}(s|es)?\b", low):
            return True
    return False


def derive_hant(zh_hans, hans_names, hant_names):
    """zh-Hant from zh-Hans: OpenCC s2twp, then re-pin canonical Taiwan plant names
    (s2twp converts glyphs/wording, it does not know our name table)."""
    out = {}
    for pid, text in zh_hans.items():
        t = _S2T.convert(text)
        hans_name = hans_names.get(pid)
        hant_name = hant_names.get(pid)
        if hans_name and hant_name:
            # Two ways s2twp can leave the caption naming the plant differently from
            # the card title (which reads plants_names_i18n[zh-Hant] verbatim):
            #  a) the two table entries differ  -> the converted zh-Hans name is wrong
            #  b) the entries are IDENTICAL but s2twp still rewrites the wording, e.g.
            #     canonical 意大利紫菀 -> 義大利紫菀. Taiwan-correct, but now title != body.
            # The table wins in both cases: it is what the card title shows.
            converted_name = _S2T.convert(hans_name)
            for candidate in (converted_name, hans_name):
                if candidate and candidate != hant_name and candidate in t:
                    t = t.replace(candidate, hant_name)
                    break
        out[pid] = t
    return out


def write_overlay(locale, captions, source_sha, ordered_ids):
    out = {
        "schema_version": 1,
        "locale": locale,
        "source": {"resource": "dex_sprite_captions.json", "sha256": source_sha},
        "fields": {"captions": {pid: captions[pid] for pid in ordered_ids}},
    }
    d = os.path.join(ROOT, "i18n", locale)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "dex_sprite_captions.json")
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return path


def report(locale, captions, items_by_id):
    target, hard = TARGET_LEN[locale], MAX_LEN[locale]
    over = [i for i, t in captions.items() if len(t) > hard]
    over_target = [i for i, t in captions.items() if len(t) > target]
    stem = SPRITE_STEM[locale]
    noterm = [i for i, t in captions.items() if stem.lower() not in t.lower()]
    namemiss = []
    for pid, it in items_by_id.items():
        if (it.get("plant") and it.get("named")
                and not name_present(captions[pid], it["plant"], locale)):
            namemiss.append(pid)
    lens = sorted(len(t) for t in captions.values())
    print(f"  {locale}: n={len(captions)} len p50={lens[len(lens)//2]} "
          f"p95={lens[int(len(lens)*0.95)]} max={lens[-1]} | >target({target})={len(over_target)} "
          f"| >hard({hard})={len(over)} | no-term={len(noterm)} | name-miss={len(namemiss)}")
    return {"over": over, "noterm": noterm, "namemiss": namemiss}


def main():
    src = next((p for p in SOURCE_CANDIDATES if os.path.exists(p)), None)
    if not src:
        raise SystemExit("dex_sprite_captions.json not found in any known location")
    with open(src, "rb") as f:
        raw = f.read()
    source_sha = hashlib.sha256(raw).hexdigest()
    captions_en = json.loads(raw)["captions"]
    ordered_ids = sorted(captions_en)

    names = json.load(open(NAMES_PATH))
    index = {r["id"]: r for r in json.load(open(INDEX_PATH))}

    locales = sys.argv[1:] or ALL_LOCALES
    bad = [l for l in locales if l not in ALL_LOCALES]
    if bad:
        raise SystemExit(f"unknown locale(s): {bad}")
    mt = [l for l in locales if l != "zh-Hant"]
    if "zh-Hant" in locales and "zh-Hans" not in mt:
        mt.append("zh-Hans")  # zh-Hant is derived — it needs zh-Hans first

    # Per-locale work items (English + canonical name + does-the-English-name-it flag).
    def items_for(locale):
        out = []
        for pid in ordered_ids:
            en = captions_en[pid]
            plant = (names.get(pid) or {}).get(locale)
            named = mentions_plant(en, name_tokens((index.get(pid) or {}).get("common_name", "")))
            row = {"id": pid, "en": en}
            if plant and named:
                row["plant"] = plant
            out.append((row, named, plant))
        return out

    results = {}
    for locale in mt:
        t0 = time.time()
        rows = items_for(locale)
        items = [r[0] for r in rows]
        meta = {r[0]["id"]: {"plant": r[2], "named": r[1], "en": r[0]["en"]} for r in rows}
        batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
        merged = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = [pool.submit(translate_batch, locale, b, i) for i, b in enumerate(batches)]
            done = 0
            for fut in concurrent.futures.as_completed(futs):
                _idx, out = fut.result()
                merged.update(out)
                done += 1
                if done % 20 == 0:
                    print(f"    {locale}: {done}/{len(batches)} batches", flush=True)

        # --- QA passes -------------------------------------------------------
        for _round in range(2):
            over = [(i, merged[i], meta[i]["en"])
                    for i in ordered_ids if len(merged[i]) > MAX_LEN[locale]]
            if not over:
                break
            print(f"    {locale}: compressing {len(over)} over-long lines", flush=True)
            chunks = [over[i:i + BATCH] for i in range(0, len(over), BATCH)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
                for fixed in pool.map(lambda c: compress(locale, c), chunks):
                    merged.update(fixed)

        miss = [(i, merged[i], meta[i]["en"], meta[i]["plant"]) for i in ordered_ids
                if meta[i]["named"] and meta[i]["plant"]
                and not name_present(merged[i], meta[i]["plant"], locale)]
        if miss:
            print(f"    {locale}: re-pinning canonical name on {len(miss)} lines", flush=True)
            chunks = [miss[i:i + BATCH] for i in range(0, len(miss), BATCH)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
                for fixed in pool.map(lambda c: repair_names(locale, c), chunks):
                    merged.update(fixed)

        results[locale] = merged
        print(f"  {locale}: {len(merged)} captions in {time.time()-t0:.0f}s", flush=True)

    if "zh-Hant" in locales:
        hans_names = {k: (v or {}).get("zh-Hans") for k, v in names.items()}
        hant_names = {k: (v or {}).get("zh-Hant") for k, v in names.items()}
        results["zh-Hant"] = derive_hant(results["zh-Hans"], hans_names, hant_names)
        print("  zh-Hant: derived from zh-Hans via OpenCC s2twp (no API call)")

    print("\n=== QA ===")
    for locale in locales:
        rows = items_for(locale if locale != "zh-Hant" else "zh-Hant")
        meta = {r[0]["id"]: {"plant": r[2], "named": r[1]} for r in rows}
        report(locale, results[locale], meta)
        path = write_overlay(locale, results[locale], source_sha, ordered_ids)
        print(f"    -> {path}")


if __name__ == "__main__":
    main()
