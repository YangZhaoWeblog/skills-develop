#!/usr/bin/env bash
# check_wip.sh — PROGRESS.md WIP=1 强制约束
# 来源：concepts/five-subsystems.md §状态 + walkinglabs L07

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TARGET="${REPO_ROOT}/PROGRESS.md"

if [[ ! -f "$TARGET" ]]; then
    exit 0
fi

# 计数 in-progress 标记 - [~]
COUNT=$(grep -c '^- \[~\]' "$TARGET" 2>/dev/null || echo 0)

mkdir -p "${REPO_ROOT}/.harness"
echo -e "$(date -u +%Y-%m-%dT%H:%M:%SZ)\twip_count\t${COUNT}" \
    >> "${REPO_ROOT}/.harness/metrics.tsv"

if (( COUNT > 1 )); then
    cat >&2 <<EOF
[BLOCK] wip-equals-one | PROGRESS.md | reason: 同时进行 ${COUNT} 个任务（应 ≤1，Little 法则）
fix: 完成或暂停其他任务，只保留 1 个 - [~] 标记
ref: walkinglabs lecture-07 / concepts/five-subsystems.md
EOF
    exit 1
fi

exit 0
