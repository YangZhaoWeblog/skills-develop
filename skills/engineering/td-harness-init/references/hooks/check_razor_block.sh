#!/usr/bin/env bash
# check_razor_block.sh — AGENTS.md razor BLOCK at 200 行
# 来源：concepts/razor-block-200.md
# 阈值硬编码于此（v0.1 不做单一来源 drift 检测）

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TARGET="${REPO_ROOT}/AGENTS.md"
THRESHOLD=200

if [[ ! -f "$TARGET" ]]; then
    exit 0  # 项目尚未初始化 AGENTS.md
fi

LINES=$(wc -l < "$TARGET" | tr -d ' ')

# 写入 metrics（采集层 1 — hook 实时）
mkdir -p "${REPO_ROOT}/.harness"
echo -e "$(date -u +%Y-%m-%dT%H:%M:%SZ)\tagents_md_lines\t${LINES}" \
    >> "${REPO_ROOT}/.harness/metrics.tsv"

if (( LINES > THRESHOLD )); then
    cat >&2 <<EOF
[BLOCK] razor-block | AGENTS.md:${LINES} | reason: 超过 ${THRESHOLD} 行视为设计失败
fix: 拆分细节到 harness/*.md，AGENTS.md 仅保留索引和硬约束
ref: harness-notes concepts/razor-block-200.md
EOF
    exit 1
fi

if (( LINES > THRESHOLD * 75 / 100 )); then
    echo "[WARN] AGENTS.md=${LINES} 行（>${THRESHOLD}*75%），考虑拆分" >&2
fi

exit 0
