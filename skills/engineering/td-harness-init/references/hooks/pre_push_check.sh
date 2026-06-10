#!/usr/bin/env bash
# pre_push_check.sh — push 前的最终门禁
# 比 pre-commit 更严：必须过 e2e

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

cd "$REPO_ROOT"

echo "→ make test"
[[ -f Makefile ]] && grep -q '^test:' Makefile && make test || true

echo "→ make e2e"
if [[ -f Makefile ]] && grep -q '^e2e:' Makefile; then
    make e2e || {
        cat >&2 <<EOF
[BLOCK] e2e | reason: E2E 失败——完成定义未达标
fix: 修复后再 push；后端项目用契约测试 + 影子流量代替
ref: harness/testing.md §完成定义
EOF
        exit 1
    }
fi

# 干净状态检查（lecture-12）
DIRTY=$(git status --porcelain | grep -v -E '\.(harness|pge)/' || true)
if [[ -n "$DIRTY" ]]; then
    cat >&2 <<EOF
[BLOCK] clean-state | reason: 工作区不干净
fix: commit 或 stash 后再 push
ref: walkinglabs lecture-12
EOF
    echo "$DIRTY" >&2
    exit 1
fi

echo "✓ pre-push gate passed"
