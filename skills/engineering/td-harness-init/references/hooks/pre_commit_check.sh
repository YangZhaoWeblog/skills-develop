#!/usr/bin/env bash
# pre_commit_check.sh — 完整本地门禁
# 串联 razor-block / wip / test-guard + project make check

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS="${REPO_ROOT}/scripts"

run() {
    local name="$1" script="$2"
    if [[ -x "$script" ]]; then
        echo "→ $name"
        "$script" || { echo "[BLOCK] $name failed" >&2; exit 1; }
    fi
}

run "razor-block"     "${SCRIPTS}/check_razor_block.sh"
run "wip-equals-one"  "${SCRIPTS}/check_wip.sh"
run "test-guard"      "${SCRIPTS}/check_test_guard.sh"

# 项目级 make check（如存在）
if [[ -f "${REPO_ROOT}/Makefile" ]] && grep -q '^check:' "${REPO_ROOT}/Makefile"; then
    echo "→ make check"
    cd "$REPO_ROOT" && make check
fi

echo "✓ pre-commit gate passed"
