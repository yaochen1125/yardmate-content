#!/usr/bin/env bash
# publish.sh — Publish YardMate content JSON to Cloudflare R2 (+ jsDelivr during transition).
#
# Why R2: jsDelivr (@main / unversioned) returns s-maxage=43200 (12h) and sits
# behind GitHub raw (Fastly), so edits take 10+ min to surface even after purge.
# R2 (images.yardmate.ai/content/) is self-hosted: short TTL + CF purge = instant.
#
# Reuses the `yardmate-static` bucket (same one serving plant images) under a
# `content/` prefix, the rclone `r2:` remote, and ~/.config/yardmate-api/cf_purge.env.
#
# Usage:
#   ./publish.sh            upload changed files to R2, purge CF, push git
#   ./publish.sh --staging  publish to content-staging/ instead (staging app 环境；
#                           不 git push、不同步官网法律页 — staging 只是预览通道)
#   ./publish.sh --dry-run  print what would happen; no upload / purge / push

set -euo pipefail

# --- config ---
BUCKET="yardmate-static"
PREFIX="content"
PUBLIC_BASE="https://images.yardmate.ai/${PREFIX}"
CACHE_CONTROL="public, max-age=60"
CF_ENV="${HOME}/.config/yardmate-api/cf_purge.env"

# App-consumed whitelist. Everything else in this repo (toxicity_*, fragrance_*,
# *.backup, audit CSVs, …) is working data and must NOT be published.
FILES=(
  plants_detail.json
  plants_index.json
  plants_names_i18n.json
  plant_image_revs.json
  explore_themes.json
  stories.json
  diseases.json
  privacy_policy.json
  terms_of_use.json
  version.txt
)
LUNAR_DIR="lunar_emotional_fortunes"

DRY_RUN=0
STAGING=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --staging) STAGING=1 ;;
    *) echo "unknown arg: $arg (supported: --staging --dry-run)" >&2; exit 2 ;;
  esac
done
if [[ $STAGING -eq 1 ]]; then
  PREFIX="content-staging"
  PUBLIC_BASE="https://images.yardmate.ai/${PREFIX}"
fi

cd "$(dirname "$0")"

run() { if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $*"; else "$@"; fi; }

# --- 1) upload to R2 (short TTL; --s3-no-check-bucket: scoped token has no bucket-admin) ---
echo "==> Uploading content to r2:${BUCKET}/${PREFIX}/ (Cache-Control: ${CACHE_CONTROL})"
for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || { echo "WARN: missing $f — skipping"; continue; }
  run rclone copy "$f" "r2:${BUCKET}/${PREFIX}/" \
      --header-upload "Cache-Control: ${CACHE_CONTROL}" --s3-no-check-bucket
done
run rclone copy "${LUNAR_DIR}/" "r2:${BUCKET}/${PREFIX}/${LUNAR_DIR}/" \
    --header-upload "Cache-Control: ${CACHE_CONTROL}" --s3-no-check-bucket

# i18n per-locale overlays — App fetches content/i18n/<locale>/<file>; missing
# locale/file falls back to English (the flat whitelist above). Whole tree, paths preserved.
if [[ -d i18n ]]; then
  echo "==> Uploading i18n/ per-locale overlays"
  run rclone copy "i18n/" "r2:${BUCKET}/${PREFIX}/i18n/" \
      --header-upload "Cache-Control: ${CACHE_CONTROL}" --s3-no-check-bucket
fi

# --- 2) Cloudflare purge (instant; short TTL is the fallback) ---
echo "==> Purging Cloudflare cache"
# shellcheck source=/dev/null
source "$CF_ENV"
purge_urls=()
for f in "${FILES[@]}"; do purge_urls+=("${PUBLIC_BASE}/${f}"); done
for y in "${LUNAR_DIR}"/*.json; do [[ -e "$y" ]] && purge_urls+=("${PUBLIC_BASE}/${y}"); done
while IFS= read -r f; do purge_urls+=("${PUBLIC_BASE}/${f}"); done < <(find i18n -type f -name '*.json' 2>/dev/null | sort)
# Cloudflare purge-by-URL caps at 30 URLs per request → send in batches.
purge_batch() {
  local json; json=$(printf '"%s",' "$@"); json="[${json%,}]"
  curl -fsS -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/purge_cache" \
    -H "Authorization: Bearer ${CF_PURGE_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"files\":${json}}" | grep -o '"success":[a-z]*' || true
}
nbatch=$(( (${#purge_urls[@]} + 29) / 30 ))
if [[ $DRY_RUN -eq 1 ]]; then
  echo "[dry-run] purge ${#purge_urls[@]} URL(s) in ${nbatch} batch(es) of <=30"
else
  for ((i=0; i<${#purge_urls[@]}; i+=30)); do
    purge_batch "${purge_urls[@]:i:30}"
  done
  echo "    purged ${#purge_urls[@]} URL(s) in ${nbatch} batch(es)"
fi

# --- 3) transition: keep feeding jsDelivr for app versions shipped pre-R2-cutover ---
# staging 发布不 git push、不碰官网：main 内容基线只由正式 publish 维护。
if [[ $STAGING -eq 1 ]]; then
  echo "==> staging: skip git push + website legal sync"
else
  echo "==> Git push (jsDelivr fallback for old app versions)"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] git add <whitelist> && git commit && git push"
  elif [[ -n "$(git status --porcelain -- "${FILES[@]}" "${LUNAR_DIR}" i18n)" ]]; then
    git add -- "${FILES[@]}" "${LUNAR_DIR}" i18n
    git commit -m "content: publish $(date -u +%Y-%m-%dT%H:%MZ)"
    git push
  else
    echo "    no content changes to push"
  fi

  # 同步官网法律页静态兜底：从刚发布的 CDN 源（privacy_policy/terms_of_use.json）重生成
  # privacy.html / terms.html 并部署，保证无 JS / SEO 看到的静态正文与 CDN 不漂移。
  LEGAL_SYNC="$(dirname "$0")/../yardmate-website/deploy_legal.sh"
  if [[ -x "$LEGAL_SYNC" ]]; then
    echo "==> Syncing website legal static fallback"
    if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $LEGAL_SYNC"; else "$LEGAL_SYNC"; fi
  fi
fi

echo "==> Done."
