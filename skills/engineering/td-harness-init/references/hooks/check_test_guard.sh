#!/usr/bin/env bash
# check_test_guard.sh — 防止 AI 修改测试断言让自己通过
# 来源：SOP PGE 致命陷阱 §2 测试篡改

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# 仅检查 AI 触发的提交（环境变量约定）
if [[ "${AI_TEST_GUARD:-1}" != "1" ]]; then
    exit 0
fi

# 暂存区中包含 _test 文件的修改？
STAGED_TESTS=$(git diff --cached --name-only --diff-filter=M | grep -E '_test\.(go|ts|py|js|rs)$' || true)

if [[ -z "$STAGED_TESTS" ]]; then
    exit 0
fi

# 检测：被修改的测试文件中，是否有断言相关行被删除/修改
SUSPICIOUS=0
for f in $STAGED_TESTS; do
    # 看 diff 里被删除的行
    DELETED=$(git diff --cached "$f" | grep -E '^-[^-]' | \
              grep -iE '(assert|expect|require|equals?|toBe|fail|error)' || true)
    if [[ -n "$DELETED" ]]; then
        SUSPICIOUS=1
        echo "[WARN] $f 删除了断言行：" >&2
        echo "$DELETED" | head -5 >&2
    fi
done

if (( SUSPICIOUS )); then
    cat >&2 <<EOF
[BLOCK] test-guard | 测试文件断言被修改 | reason: AI 不得修改测试让自己通过
fix: 如确需修改测试（spec 变了），用 'AI_TEST_GUARD=0 git commit' 显式跳过
     人工 review 后通过，并在 DECISIONS.md 记录
ref: SOP-PGE 致命陷阱 §2 / concepts/tools-over-ai.md
EOF
    exit 1
fi

exit 0
