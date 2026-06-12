# Yardmate Content

Plant content data for the Yardmate iOS app, served via jsDelivr CDN.

## Files

- `plants_detail.json` — Full plant detail (~1000+ entries)
- `plants_index.json` — Quick lookup table (id / scientific_name / common_name)
- `explore_themes.json` — 30 curated collections (300 plant entries)
- `lunar_emotional_fortunes/{year}.json` — Daily plant + moon phase + emotional theme data
- `version.txt` — Content version (bump on every update)

## CDN

Served from Cloudflare R2 (self-hosted, instant purge):

```
https://images.yardmate.ai/content/<file>
```

Examples:

- `https://images.yardmate.ai/content/version.txt`
- `https://images.yardmate.ai/content/plants_detail.json`
- `https://images.yardmate.ai/content/lunar_emotional_fortunes/2026.json`

> **Transition:** content is also pushed to jsDelivr
> (`https://cdn.jsdelivr.net/gh/yaochen1125/yardmate-content/<file>`) so app
> versions shipped before the R2 cutover keep working. Drop the jsDelivr leg
> once those versions are retired.

## Update workflow

1. Edit JSON files locally
2. Bump `version.txt` (e.g. `v1` → `v2`)
3. Run `./publish.sh` — uploads changed files to R2 (short TTL), purges
   Cloudflare, and pushes to git (jsDelivr fallback). `--dry-run` to preview.
4. Yardmate app fetches the new version on next launch: R2 purge is instant;
   the jsDelivr leg still propagates in ~12h (only old app versions read it)

## License

Internal use only. Plant data sourced from public botanical references.
