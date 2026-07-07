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
# git 白名单（jsDelivr 兜底用）：排除整包 plants_detail.json —— 它真源在 scripts/，只上传 R2、不进 content git。
GIT_FILES=()
for f in "${FILES[@]}"; do [[ "$f" == "plants_detail.json" ]] || GIT_FILES+=("$f"); done

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

# --- 0) i18n overlay freshness gate ---
# explore_themes 的 overlay 在 App 端按 plants[] 下标对齐英文母本，翻译一过期就
# 静默错位（圣诞玫瑰挂银杏的"活化石广岛"）。任一 overlay 的 source.sha256 不等于
# 当前英文母本时拒绝发布；重生成：python3 translate_explore_themes.py
echo "==> Checking i18n overlay freshness (explore_themes)"
python3 - << 'PYEOF'
import glob, hashlib, json, sys
sha = hashlib.sha256(open("explore_themes.json", "rb").read()).hexdigest()
paths = sorted(glob.glob("i18n/*/explore_themes.json"))
stale = [p for p in paths
         if json.load(open(p)).get("source", {}).get("sha256") != sha]
if stale:
    print("FATAL: stale explore_themes overlays — regenerate: python3 translate_explore_themes.py")
    for p in stale:
        print("  " + p)
    sys.exit(1)
print(f"    {len(paths)} overlays match en sha {sha[:12]}")
PYEOF

# --- 0b) stories.json freshness gate ---
# stories.json = 从 plants_detail 母本按 history_text_short（非空才收）派生的首页故事卡源，
# 生成逻辑同 build_stories_json.py / catalog-promote-tool/export_sharded.py。晋升新株后若没
# 同步重生成，这份会落后 → 首页故事卡漏新株。与母本不一致时拒绝发布（按 id 集合 + 逐条文案比对）。
echo "==> Checking stories.json freshness"
python3 - << 'PYEOF'
import json, sys
def norm(r):
    return {"id": r["id"], "common_name": r.get("common_name"),
            "scientific_name": r.get("scientific_name"),
            "history_text_short": (r.get("history_text_short") or "").strip()}
detail = json.load(open("../yardmate-swiftui/scripts/plants_detail.json", encoding="utf-8"))
expected = {r["id"]: norm(r) for r in detail
            if r.get("id") and (r.get("history_text_short") or "").strip()}
cur = {s["id"]: norm(s) for s in json.load(open("stories.json", encoding="utf-8")).get("stories", [])}
if cur != expected:
    missing = sorted(set(expected) - set(cur))
    extra   = sorted(set(cur) - set(expected))
    changed = sorted(i for i in set(expected) & set(cur) if expected[i] != cur[i])
    print(f"FATAL: stories.json stale vs plants_detail (母本 {len(expected)} 条, 文件 {len(cur)} 条)")
    if missing: print(f"  漏 {len(missing)} 株: {missing[:10]}{' …' if len(missing) > 10 else ''}")
    if extra:   print(f"  多 {len(extra)} 株: {extra[:10]}{' …' if len(extra) > 10 else ''}")
    if changed: print(f"  文案变 {len(changed)} 株: {changed[:10]}{' …' if len(changed) > 10 else ''}")
    print("  重生成: (catalog-promote-tool) ./deploy_shards.sh 会回同步；或 build_stories_json.py 后重跑本脚本")
    sys.exit(1)
print(f"    stories.json fresh: {len(cur)} 条与 plants_detail 一致")
PYEOF

# --- 1) upload to R2 (short TTL; --s3-no-check-bucket: scoped token has no bucket-admin) ---
echo "==> Uploading content to r2:${BUCKET}/${PREFIX}/ (Cache-Control: ${CACHE_CONTROL})"
for f in "${FILES[@]}"; do
  src="$f"
  # 整包 plants_detail.json 的真源 = 分片源 scripts/plants_detail.json（app 只读 R2 分片，此整包仅遗留
  # 兜底、已不在 content/ 保留）。从真源上传，杜绝与分片脱节。单一英文 base 源 = scripts/plants_detail.json。
  [[ "$f" == "plants_detail.json" ]] && src="../yardmate-swiftui/scripts/plants_detail.json"
  [[ -f "$src" ]] || { echo "WARN: missing $src — skipping"; continue; }
  run rclone copy "$src" "r2:${BUCKET}/${PREFIX}/" \
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
  elif [[ -n "$(git status --porcelain -- "${GIT_FILES[@]}" "${LUNAR_DIR}" i18n)" ]]; then
    git add -- "${GIT_FILES[@]}" "${LUNAR_DIR}" i18n
    git commit -m "content: publish $(date -u +%Y-%m-%dT%H:%MZ)"
    git push
  else
    echo "    no content changes to push"
  fi

  # 同步官网法律页静态兜底：从刚发布的 CDN 源（privacy_policy/terms_of_use.json）重生成
  # privacy.html / terms.html 并部署，保证无 JS / SEO 看到的静态正文与 CDN 不漂移。
  # deploy_legal.sh 自带幂等：重生成后 md5 对比线上，一致跳过 scp、不一致才部署（自愈）。
  LEGAL_SYNC="$(dirname "$0")/../yardmate-website/deploy_legal.sh"
  if [[ -x "$LEGAL_SYNC" ]]; then
    echo "==> Syncing website legal static fallback"
    if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $LEGAL_SYNC"; else "$LEGAL_SYNC"; fi
  fi
fi

echo "==> Done."
