# Yardmate Content

Plant content data for the Yardmate iOS app, served via jsDelivr CDN.

## Files

- `plants_detail.json` — Full plant detail (~1000+ entries)
- `plants_index.json` — Quick lookup table (id / scientific_name / common_name)
- `explore_themes.json` — 30 curated collections (300 plant entries)
- `lunar_emotional_fortunes/{year}.json` — Daily plant + moon phase + emotional theme data
- `version.txt` — Content version (bump on every update)

## CDN

Public via jsDelivr:

```
https://cdn.jsdelivr.net/gh/yaochen1125/yardmate-content/<file>
```

Examples:

- `https://cdn.jsdelivr.net/gh/yaochen1125/yardmate-content/version.txt`
- `https://cdn.jsdelivr.net/gh/yaochen1125/yardmate-content/plants_detail.json`
- `https://cdn.jsdelivr.net/gh/yaochen1125/yardmate-content/lunar_emotional_fortunes/2026.json`

## Update workflow

1. Edit JSON files locally
2. Bump `version.txt` (e.g. `v1` → `v2`)
3. `git push`
4. CDN propagates within ~12 hours (or use https://www.jsdelivr.com/tools/purge for instant refresh)
5. Yardmate app on next launch fetches new version automatically

## License

Internal use only. Plant data sourced from public botanical references.
