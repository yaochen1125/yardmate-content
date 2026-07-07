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
Requires: ~/.config/yardmate-api/deepseek.env with DEEPSEEK_API_KEY.
Resumable: per-(locale,theme) results cached in .translate_cache/; delete to redo.
"""
import concurrent.futures
import hashlib
import json
import os
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


API_KEY = load_key()


def call_deepseek(system, user):
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


def translate_theme(locale, theme):
    """One theme -> localized fields dict. Validates shape; retries on failure."""
    cache_path = os.path.join(CACHE_DIR, f"{locale}__{theme['id']}.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return theme["id"], json.load(f)

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
            got = call_deepseek(SYSTEM.format(language=language), user)
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
    locales = sys.argv[1:] or list(LOCALES)

    for locale in locales:
        t0 = time.time()
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futs = [pool.submit(translate_theme, locale, t) for t in themes]
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
        out_path = os.path.join(ROOT, "i18n", locale, "explore_themes.json")
        with open(out_path, "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"{locale}: {len(ordered)} themes in {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
