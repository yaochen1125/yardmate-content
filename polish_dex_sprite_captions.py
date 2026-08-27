#!/usr/bin/env python3
"""Targeted second pass over the generated dex_sprite_captions overlays.

The generator's inline QA leaves a tail: lines still over the hard length cap
after two compression rounds, lines that dropped the locked "sprite" term, and
lines whose English names the plant but whose translation lost the canonical name.
This re-attacks only those (a few hundred strings total, not 16k) and rewrites the
overlays in place. zh-Hant is re-derived from the polished zh-Hans afterwards.

Run: python3 polish_dex_sprite_captions.py [locale ...]
"""
import concurrent.futures
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(ROOT, "translate_dex_sprite_captions.py"))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)


def overlay_path(locale):
    return os.path.join(ROOT, "i18n", locale, "dex_sprite_captions.json")


def load(locale):
    with open(overlay_path(locale)) as f:
        doc = json.load(f)
    return doc, doc["fields"]["captions"]


def hard_compress(locale, entries):
    """entries = [(id, text, en)]. Blunter than the generator's pass: names the exact
    budget and licenses dropping a secondary clause, because the polite version has
    already been tried twice and plateaued."""
    hard = G.MAX_LEN[locale]
    target = G.TARGET_LEN[locale]
    payload = [{"id": i, "current": t, "over_by": len(t) - hard, "en": en}
               for i, t, en in entries]
    user = (
        f"Each {G.LANG_NAMES[locale]} line below is over the card's hard limit of {hard} "
        f"characters by \"over_by\". Rewrite each to {target} characters or fewer — this is "
        f"a hard layout constraint, the card clips.\n"
        f"Keep: the term \"{G.SPRITE_TERM[locale]}\", the sprites' main action, any canonical "
        f"plant name already in the line, the storybook tone.\n"
        f"You MAY drop a secondary clause, a subordinate detail, or an adjective phrase "
        f"entirely. Do not summarise into an abstract statement — keep one concrete image.\n"
        "Return JSON {id: shortened} with the SAME ids:\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    got = G.call_deepseek(G.system_prompt(locale), user, temperature=0.7)
    out = {}
    for i, cur, _en in entries:
        v = got.get(i)
        if isinstance(v, str) and v.strip():
            v = v.strip()
            if len(v) < len(cur) and G.SPRITE_STEM[locale].lower() in v.lower():
                out[i] = v
    return out


def fix_term(locale, entries):
    """entries = [(id, text, en)] — lines missing the locked sprite term."""
    payload = [{"id": i, "current": t, "en": en} for i, t, en in entries]
    user = (
        f"Each line below should refer to the garden sprites as \"{G.SPRITE_TERM[locale]}\" "
        f"but does not. Rewrite each so the term appears, keeping the meaning, the tone and "
        f"the {G.MAX_LEN[locale]}-character ceiling.\n"
        "Return JSON {id: rewritten} with the SAME ids:\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    got = G.call_deepseek(G.system_prompt(locale), user, temperature=0.7)
    return {i: got[i].strip() for i, _t, _en in entries
            if isinstance(got.get(i), str) and got[i].strip()
            and G.SPRITE_STEM[locale].lower() in got[i].lower()}


def run_pass(locale, entries, fn, label, rounds=1):
    if not entries:
        return {}
    fixed = {}
    chunks = [entries[i:i + G.BATCH] for i in range(0, len(entries), G.BATCH)]
    print(f"    {locale}: {label} {len(entries)} lines ({len(chunks)} calls)", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=G.WORKERS) as pool:
        for out in pool.map(lambda c: fn(locale, c), chunks):
            fixed.update(out)
    return fixed


def main():
    src = next(p for p in G.SOURCE_CANDIDATES if os.path.exists(p))
    with open(src, "rb") as f:
        raw = f.read()
    captions_en = json.loads(raw)["captions"]
    names = json.load(open(G.NAMES_PATH))
    index = {r["id"]: r for r in json.load(open(G.INDEX_PATH))}
    ordered_ids = sorted(captions_en)

    locales = sys.argv[1:] or G.MT_LOCALES  # zh-Hant is re-derived, never polished
    for locale in locales:
        doc, caps = load(locale)
        meta = {}
        for pid in ordered_ids:
            en = captions_en[pid]
            meta[pid] = {
                "en": en,
                "plant": (names.get(pid) or {}).get(locale),
                "named": G.mentions_plant(
                    en, G.name_tokens((index.get(pid) or {}).get("common_name", ""))),
            }

        for rnd in range(3):
            over = [(i, caps[i], meta[i]["en"])
                    for i in ordered_ids if len(caps[i]) > G.MAX_LEN[locale]]
            if not over:
                break
            caps.update(run_pass(locale, over, hard_compress, f"compress r{rnd+1}"))

        noterm = [(i, caps[i], meta[i]["en"]) for i in ordered_ids
                  if G.SPRITE_STEM[locale].lower() not in caps[i].lower()]
        caps.update(run_pass(locale, noterm, fix_term, "term-fix"))

        for rnd in range(2):
            miss = [(i, caps[i], meta[i]["en"], meta[i]["plant"]) for i in ordered_ids
                    if meta[i]["named"] and meta[i]["plant"]
                    and not G.name_present(caps[i], meta[i]["plant"], locale)]
            if not miss:
                break
            caps.update(run_pass(locale, miss, G.repair_names, f"name-repair r{rnd+1}"))

        doc["fields"]["captions"] = {pid: caps[pid] for pid in ordered_ids}
        with open(overlay_path(locale), "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        G.report(locale, caps, {pid: meta[pid] for pid in ordered_ids})

    # zh-Hant always re-derives from whatever zh-Hans now says.
    if "zh-Hans" in locales:
        _hansdoc, hans = load("zh-Hans")
        hant_doc, _ = load("zh-Hant")
        hans_names = {k: (v or {}).get("zh-Hans") for k, v in names.items()}
        hant_names = {k: (v or {}).get("zh-Hant") for k, v in names.items()}
        hant = G.derive_hant(hans, hans_names, hant_names)
        hant_doc["fields"]["captions"] = {pid: hant[pid] for pid in ordered_ids}
        with open(overlay_path("zh-Hant"), "w") as f:
            json.dump(hant_doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        meta_ht = {pid: {"plant": (names.get(pid) or {}).get("zh-Hant"),
                         "named": G.mentions_plant(
                             captions_en[pid],
                             G.name_tokens((index.get(pid) or {}).get("common_name", "")))}
                   for pid in ordered_ids}
        print("  zh-Hant: re-derived via OpenCC s2twp")
        G.report("zh-Hant", hant, meta_ht)


if __name__ == "__main__":
    main()
