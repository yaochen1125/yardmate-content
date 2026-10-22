#!/usr/bin/env python3
"""Regenerate i18n/<locale>/explore_themes.json overlays from the English source.

Why this exists: the English explore_themes.json was wholesale revised
(commit a912d9a — intros/reasons rewritten, 11 themes swapped plants) but the
per-locale overlays were never regenerated. The overlay's plants[] is matched
to the English theme BY INDEX in the app (ExploreThemeLocalization.swift), so
a stale overlay silently attaches descriptions to the wrong plants
(e.g. Helleborus showing Ginkgo's "survived Hiroshima" line).

Run: python3 translate_explore_themes.py            # all locales
     python3 translate_explore_themes.py zh-Hans    # one locale
     python3 translate_explore_themes.py --engine claude
         # translate with the local `claude` CLI (subscription, no tools) instead
         # of DeepSeek — the weekly server job uses this, so no DeepSeek key
         # has to live on the production box
Requires (default engine): ~/.config/yardmate-api/deepseek.env with DEEPSEEK_API_KEY.

Only what changed is translated. A theme's existing overlay entry is kept when it
is provably current: the overlay was made from this exact explore_themes.json
(source.sha256 matches), or from the committed HEAD version and this theme's
English text is identical to HEAD's. Everything else (new themes, edited themes)
is translated — so the weekly job only pays for the new collection, and an edited
theme can never keep a stale, index-misaligned translation. (`--only-missing` is
accepted for compatibility; this is now always the behaviour.)
Resumable: results cached in .translate_cache/ keyed by (locale, theme id, hash of
the English text being translated); delete to redo.
"""
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "explore_themes.json")
CACHE_DIR = os.path.join(ROOT, ".translate_cache", "explore_themes")

LOCALES = {
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "vi": "Vietnamese",
    "zh-Hans": "Simplified Chinese",
    "zh-Hant": "Traditional Chinese (Taiwan conventions)",
}
CJK = {"ja", "ko", "zh-Hans", "zh-Hant"}

SYSTEM = """You are a senior localizer for YardMate, a gardening app. Translate editorial copy about plant collections into {language}.

Rules:
- Natural, idiomatic {language} — magazine quality, never word-by-word machine style.
- Keep Latin scientific names untranslated.
- Mythological / historical / literary proper nouns use their established {language} forms (e.g. Aphrodite, Shakespeare, A Midsummer Night's Dream each have standard renderings).
- "reasons" are one-line card taglines: keep them short and punchy, matching the source register.
- Reply ONLY with a JSON object: {{"title": str, "description": str, "intro": str, "reasons": [str, ...]}} with exactly as many reasons as given, same order."""


def load_key():
    path = os.path.expanduser("~/.config/yardmate-api/deepseek.env")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("DEEPSEEK_API_KEY not found")


API_KEY = None  # loaded on first DeepSeek call, so `--engine claude` runs without the key file


def call_deepseek(system, user):
    global API_KEY
    if API_KEY is None:
        API_KEY = load_key()
    body = json.dumps({
        "model": "deepseek-chat",
        "temperature": 1.3,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.load(resp)
    return json.loads(out["choices"][0]["message"]["content"])


def call_claude(system, user):
    """`claude -p` with no tools / MCP / session (it can only answer text); returns the JSON object."""
    exe = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    cmd = [exe, "-p", "--model", "sonnet", "--tools", "", "--restricted",
           "--strict-mcp-config", "--no-session-persistence"]
    r = subprocess.run(cmd, input=system + "\n\n" + user, text=True, capture_output=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"claude exit {r.returncode}: {(r.stderr or r.stdout)[-300:]}")
    text = r.stdout
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON object in claude output: {text[:200]!r}")
    return json.loads(text[start:end + 1])


CALL = call_deepseek


def theme_key(theme):
    """Hash of exactly the English text that gets translated (not addedAt / number)."""
    src = {"title": theme["title"], "description": theme["description"], "intro": theme["intro"],
           "plants": [[p["scientificName"], p["commonName"], p["reason"]] for p in theme["plants"]]}
    return hashlib.sha256(json.dumps(src, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def cache_path_for(locale, theme):
    return os.path.join(CACHE_DIR, f"{locale}__{theme['id']}__{theme_key(theme)}.json")


def head_source():
    """(sha256, {id: theme}) of the committed HEAD explore_themes.json, or (None, {})."""
    r = subprocess.run(["git", "-C", ROOT, "show", "HEAD:explore_themes.json"], capture_output=True)
    if r.returncode != 0:
        return None, {}
    return hashlib.sha256(r.stdout).hexdigest(), {t["id"]: t for t in json.loads(r.stdout)["themes"]}


def translate_theme(locale, theme):
    """One theme -> localized fields dict. Validates shape; retries on failure."""
    cache_path = cache_path_for(locale, theme)
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cached = json.load(f)
        if len(cached.get("plants") or []) == len(theme["plants"]):
            return theme["id"], cached

    language = LOCALES[locale]
    payload = {
        "title": theme["title"],
        "description": theme["description"],
        "intro": theme["intro"],
        "plants": [
            {
                "scientificName": p["scientificName"],
                "commonName": p["commonName"],
                "reason": p["reason"],
            }
            for p in theme["plants"]
        ],
    }
    user = (
        "Translate title, description, intro, and every plant's reason. "
        "plants[] give scientificName/commonName as context only — translate just each reason.\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    n = len(theme["plants"])
    last_err = None
    for attempt in range(4):
        try:
            got = CALL(SYSTEM.format(language=language), user)
            reasons = got.get("reasons")
            assert isinstance(reasons, list) and len(reasons) == n, f"reasons len {reasons and len(reasons)} != {n}"
            fields = {
                "title": str(got["title"]).strip(),
                "description": str(got["description"]).strip(),
                "intro": str(got["intro"]).strip(),
                "plants": [{"reason": str(r).strip()} for r in reasons],
            }
            texts = [fields["title"], fields["description"], fields["intro"]] + [r.strip() for r in reasons]
            assert all(texts), "empty string in output"
            if locale in CJK:
                cjk_hits = sum(any("぀" <= c <= "鿿" or "가" <= c <= "힯" for c in t) for t in texts)
                assert cjk_hits >= len(texts) - 1, f"only {cjk_hits}/{len(texts)} strings contain CJK — likely untranslated"
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache_path, "w") as f:
                json.dump(fields, f, ensure_ascii=False)
            return theme["id"], fields
        except Exception as e:  # noqa: BLE001 — retry any API/validation failure
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{locale}/{theme['id']}: {last_err}")


def main():
    with open(SOURCE, "rb") as f:
        raw = f.read()
    source_sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw)
    themes = data["themes"]
    global CALL
    args = sys.argv[1:]
    engine = "deepseek"
    if "--engine" in args:
        i = args.index("--engine")
        if i + 1 >= len(args) or args[i + 1] not in ("deepseek", "claude"):
            raise SystemExit("--engine must be deepseek or claude")
        engine = args[i + 1]
        del args[i:i + 2]
    CALL = call_claude if engine == "claude" else call_deepseek
    locales = [a for a in args if a != "--only-missing"] or list(LOCALES)
    unknown = [l for l in locales if l not in LOCALES]
    if unknown:
        raise SystemExit(f"unknown locale(s): {unknown}")

    head_sha, head_themes = head_source()

    for locale in locales:
        t0 = time.time()
        out_path = os.path.join(ROOT, "i18n", locale, "explore_themes.json")
        results = {}
        if os.path.exists(out_path):
            with open(out_path) as f:
                overlay = json.load(f)
            made_from = overlay.get("source", {}).get("sha256")
            existing = overlay["fields"]["themes"]
            for t in themes:
                kept = existing.get(t["id"])
                if not kept or len(kept.get("plants") or []) != len(t["plants"]):
                    continue
                head_t = head_themes.get(t["id"])
                current = made_from == source_sha or (
                    made_from is not None and made_from == head_sha
                    and head_t is not None and theme_key(head_t) == theme_key(t))
                if current:
                    results[t["id"]] = kept
                    os.makedirs(CACHE_DIR, exist_ok=True)  # so a rerun before commit still hits
                    with open(cache_path_for(locale, t), "w") as f:
                        json.dump(kept, f, ensure_ascii=False)
        todo = [t for t in themes if t["id"] not in results]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futs = [pool.submit(translate_theme, locale, t) for t in todo]
            for fut in concurrent.futures.as_completed(futs):
                tid, fields = fut.result()
                results[tid] = fields
        # preserve source theme order in output for stable diffs
        ordered = {t["id"]: results[t["id"]] for t in themes}
        out = {
            "schema_version": 1,
            "locale": locale,
            "source": {"resource": "explore_themes.json", "sha256": source_sha},
            "fields": {"themes": ordered},
        }
        with open(out_path, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"{locale}: {len(ordered)} themes ({len(todo)} translated) in {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
