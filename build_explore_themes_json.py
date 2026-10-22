#!/usr/bin/env python3
"""
Convert explore_themes.md → explore_themes.json with plant IDs from plants_index.json.

explore_themes.md is the human-authored master. Per theme block:

  ## N. Title
  > id: slug          (required — pins the stable theme id)
  <description line>  (required, single line)
  > intro: ...        (required, single line)
  > added: YYYY-MM-DD (optional — UTC date a weekly collection went live)
  N. Sci name — Common name: reason.   (em-dash, one line per plant)

Any line that doesn't parse is a hard error — the build fails loudly and
writes nothing, instead of silently dropping content (a dropped plant or
theme would desync the index-aligned i18n overlays in yardmate-content).

Output order: themes with `> added:` first, newest date first (same date →
higher theme number first), then the undated originals in markdown order.
The app's All Collections list shows data order as-is (old builds too), so
this is what puts the newest weekly collection at the top everywhere.

Dated themes must not share more than MAX_OVERLAP plants with any other
theme (the original 30 already overlap each other and are exempt).

Output schema:
{
  "version": "1.0",
  "totalThemes": 30,
  "themes": [
    {
      "id": "love-tokens",
      "number": 1,
      "title": "Love Tokens",
      "description": "Plants traditionally given as symbols of love and devotion.",
      "intro": "...",
      "plants": [
        {
          "scientificName": "Rosa damascena",
          "commonName": "Damask Rose",
          "id": "AAA0XXX",
          "reason": "..."
        }
      ],
      "addedAt": "2026-10-26"   (only on themes with `> added:`)
    }
  ]
}
"""

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "plants_index.json"
MD_PATH = ROOT / "explore_themes.md"
OUT_PATH = ROOT / "explore_themes.json"

PLANT_RE = re.compile(r"^(\d+)\.\s+(.+?)\s+—\s+(.+?):\s+(.+?)$")
MAX_OVERLAP = 3


def main():
    if not INDEX_PATH.exists():
        sys.exit(f"{INDEX_PATH} not found — run from a full yardmate-content checkout.")
    plants = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    sci_to_plant = {p["scientific_name"]: p for p in plants}
    if len(sci_to_plant) != len(plants):
        sys.exit(
            "plants_index.json has duplicate scientific_name entries — "
            "id resolution would silently pick the last one; fix the index first."
        )

    md = MD_PATH.read_text(encoding="utf-8")

    # Split by `## N. Title` headers; parts[0] is the preamble,
    # then (number, title, body) repeat.
    parts = re.split(r"\n## (\d+)\. (.+?)\n", md)

    themes = []
    errors = []

    # re.split with 2 capture groups always yields 1 + 3*n_matches parts
    for i in range(1, len(parts), 3):
        number = int(parts[i])
        title = parts[i + 1].strip()
        body = parts[i + 2]

        def err(msg):
            errors.append(f"[{number}. {title}] {msg}")

        theme_id = None
        description = None
        intro = None
        added_at = None
        plants_list = []

        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped or stripped == "---":
                continue
            if stripped.startswith(">"):
                if m := re.match(r"^>\s*id:\s*(\S+)\s*$", stripped):
                    if theme_id is not None:
                        err("duplicate `> id:` line")
                    elif not re.fullmatch(r"[a-z0-9-]+", m.group(1)):
                        err(f"`> id:` must be a kebab-case slug: {m.group(1)!r}")
                    else:
                        theme_id = m.group(1)
                elif m := re.match(r"^>\s*intro:\s*(.+)$", stripped):
                    if intro is not None:
                        err("duplicate `> intro:` line")
                    else:
                        intro = m.group(1).strip()
                elif m := re.match(r"^>\s*added:\s*(\S+)\s*$", stripped):
                    value = m.group(1)
                    if added_at is not None:
                        err("duplicate `> added:` line")
                    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        err(f"`> added:` must be YYYY-MM-DD: {value!r}")
                    else:
                        try:
                            day = datetime.date.fromisoformat(value)
                        except ValueError:
                            err(f"`> added:` is not a real date: {value!r}")
                        else:
                            # The app treats a future addedAt as absent → that issue would silently
                            # never be pinned. Dates are UTC (the app counts UTC days).
                            if day > datetime.datetime.now(datetime.timezone.utc).date():
                                err(f"`> added:` is in the future (UTC): {value!r}")
                            else:
                                added_at = value
                else:
                    err(f"unrecognized `>` directive: {stripped[:60]!r}")
            elif re.match(r"^\d+\.", stripped):
                m = PLANT_RE.match(stripped)
                if not m:
                    err(
                        "malformed plant line (need `N. 学名 — 俗名: reason`, "
                        f"em-dash + colon): {stripped[:60]!r}"
                    )
                    continue
                ordinal, sci_name, common_name, reason = (g.strip() for g in m.groups())
                if int(ordinal) != len(plants_list) + 1:
                    err(
                        f"plant ordinal {ordinal} at position {len(plants_list) + 1} "
                        "— renumber the list (array order is what ships and what "
                        "translations align to)"
                    )
                if any(p["scientificName"] == sci_name for p in plants_list):
                    err(f"duplicate plant within theme: {sci_name!r}")
                    continue
                plant = sci_to_plant.get(sci_name)
                if plant is None:
                    err(f"scientific name not in plants_index.json: {sci_name!r}")
                    continue
                plants_list.append({
                    "scientificName": sci_name,
                    "commonName": common_name,
                    "id": plant["id"],
                    "reason": reason,
                })
            elif description is None and not plants_list:
                description = stripped
            else:
                err(f"unexpected extra prose line (wrapped paragraph?): {stripped[:60]!r}")

        if theme_id is None:
            err("missing `> id:` line (ids key the i18n overlays and hero "
                "images — never derive them from the title)")
        if description is None:
            err("missing description line")
        if intro is None:
            err("missing `> intro:` line")
        if len(plants_list) < 4:
            err(
                f"only {len(plants_list)} plants parsed — Discover collages "
                "need at least 4 per theme (the norm is 10)"
            )

        theme = {
            "id": theme_id,
            "number": number,
            "title": title,
            "description": description,
            "intro": intro,
            "plants": plants_list,
        }
        # Key only on dated themes, so a rebuild of the undated originals
        # stays byte-identical to what was published before this field.
        if added_at is not None:
            theme["addedAt"] = added_at
        themes.append(theme)

    if not themes:
        errors.append("no themes parsed — theme headers missing or file structure broken")
    # `##...` but not `###...`: catches malformed theme headers (`##2.`,
    # `## Appendix`) without tripping on legitimate h3+ subheadings
    header_count = len(re.findall(r"^##(?!#)", md, re.MULTILINE))
    if header_count != len(themes):
        errors.append(
            f"{header_count} `##` header lines but {len(themes)} themes parsed "
            "— a malformed `## N. Title` header swallowed a theme"
        )
    numbers = [t["number"] for t in themes]
    if numbers != list(range(1, len(themes) + 1)):
        errors.append(f"theme numbers not sequential 1..{len(themes)}: {numbers}")
    ids = [t["id"] for t in themes if t["id"]]
    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        errors.append(f"duplicate theme ids: {sorted(dupes)}")
    titles = [t["title"].casefold() for t in themes]
    dupe_titles = {x for x in titles if titles.count(x) > 1}
    if dupe_titles:
        errors.append(f"duplicate theme titles: {sorted(dupe_titles)}")
    for t in themes:
        if "addedAt" not in t:
            continue
        mine = {p["id"] for p in t["plants"]}
        for o in themes:
            if o is t:
                continue
            shared = mine & {p["id"] for p in o["plants"]}
            if len(shared) > MAX_OVERLAP:
                errors.append(
                    f"[{t['number']}. {t['title']}] shares {len(shared)} plants with "
                    f"{o['id']!r} (max {MAX_OVERLAP} for dated themes): {sorted(shared)}"
                )

    if errors:
        print(
            f"explore_themes.md failed validation — {OUT_PATH.name} NOT written:",
            file=sys.stderr,
        )
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    dated = sorted(
        (t for t in themes if "addedAt" in t),
        key=lambda t: (t["addedAt"], t["number"]),
        reverse=True,
    )
    themes = dated + [t for t in themes if "addedAt" not in t]

    output = {
        "version": "1.0",
        "totalThemes": len(themes),
        "themes": themes,
    }

    # Targeted retranslation warning: per-plant translations in
    # yardmate-content align by array index, so report exactly which
    # themes changed content vs the previous build.
    changed_plants, changed_text = [], []
    if OUT_PATH.exists():
        old = {t["id"]: t for t in json.loads(OUT_PATH.read_text(encoding="utf-8"))["themes"]}
        for t in themes:
            o = old.get(t["id"])
            if o is None:
                changed_plants.append(f"{t['id']} (new theme)")
            elif [p["scientificName"] for p in o["plants"]] != [p["scientificName"] for p in t["plants"]]:
                changed_plants.append(t["id"])
            elif o != t:
                changed_text.append(t["id"])

    # trailing newline matches the published yardmate-content format,
    # so a clean rebuild is byte-identical to the live file
    OUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Themes: {len(themes)}")
    print(f"Total plant entries: {sum(len(t['plants']) for t in themes)}")
    print(f"Written to: {OUT_PATH}")
    if changed_plants:
        print(
            f"PLANTS CHANGED in {len(changed_plants)} theme(s): "
            f"{', '.join(changed_plants)}\n"
            "  -> per-plant translations align by ARRAY INDEX; you MUST re-run "
            "yardmate-content's translate_explore_themes.py before publish, "
            "or non-English captions will attach to the wrong plants."
        )
    elif changed_text:
        print(
            f"Text changed in {len(changed_text)} theme(s): {', '.join(changed_text)}\n"
            "  -> re-run translate_explore_themes.py so translations stay current "
            "(publish's sha gate will block stale overlays anyway)."
        )


if __name__ == "__main__":
    main()
