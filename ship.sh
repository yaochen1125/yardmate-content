#!/usr/bin/env bash
# ship.sh — 内容全自动发布管线：staging → 校验 → prod → 校验。
#
# 任一步失败立即中止，prod 不动。自动化的门 = 完整性校验（staging 实际服务的
# version.txt 与本地字节一致 + 关键 JSON 可拉取可解析），不替代"内容本身对不对"
# 的人工判断；想中途在 App 里看一眼，用两步流程（publish.sh --staging → publish.sh）。
#
# Usage:
#   ./ship.sh                 全自动 staging→prod（prod 段含 git push + 官网法律页同步）
#   ./ship.sh --staging-only  只发 staging + 校验

set -euo pipefail
cd "$(dirname "$0")"

STAGING_ONLY=0
[[ "${1:-}" == "--staging-only" ]] && STAGING_ONLY=1

green() { printf '\033[32m%s\033[0m\n' "$*"; }
red()   { printf '\033[31m%s\033[0m\n' "$*"; }

# 校验：version.txt 与本地一致（purge 后即时；?cb= 绕 CDN 缓存键）+ 关键 JSON 可解析。
verify() {
    local base="$1" cb="$$-$RANDOM"
    local local_ver remote_ver
    local_ver=$(tr -d '[:space:]' < version.txt)
    remote_ver=$(curl -sf --max-time 15 "$base/version.txt?cb=$cb" | tr -d '[:space:]')
    [[ -n "$remote_ver" && "$remote_ver" == "$local_ver" ]] \
        || { red "FATAL: $base/version.txt='$remote_ver' != 本地 '$local_ver'"; exit 1; }
    echo "    version.txt = $remote_ver ok"
    local f
    for f in plants_index.json diseases.json stories.json plants_names_i18n.json; do
        curl -sf --max-time 30 "$base/$f?cb=$cb" | python3 -c "import json,sys; json.load(sys.stdin)" \
            || { red "FATAL: $base/$f 拉取/解析失败"; exit 1; }
        echo "    $f parse ok"
    done
}

echo "=== [1/4] publish --staging ==="
./publish.sh --staging

echo "=== [2/4] 校验 staging ==="
verify https://images.yardmate.ai/content-staging

if [[ $STAGING_ONLY -eq 1 ]]; then
    green "STAGING ONLY DONE — App(Debug) 切 staging 验证后跑 ./publish.sh 发 prod"
    exit 0
fi

echo "=== [3/4] publish prod ==="
./publish.sh

echo "=== [4/4] 校验 prod ==="
verify https://images.yardmate.ai/content

green "=== SHIP COMPLETE: staging + prod 均已发布并通过校验 ==="
