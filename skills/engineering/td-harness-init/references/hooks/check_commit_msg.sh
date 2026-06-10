#!/usr/bin/env bash
# check_commit_msg.sh — Conventional Commits 格式校验
# 触发：commit-msg hook
# 用法：bash check_commit_msg.sh <commit-msg-file>

set -euo pipefail

MSG_FILE="${1:?missing commit msg file}"
HEADER=$(head -n 1 "$MSG_FILE")

# Conventional Commits 正则：type(scope): subject
# type: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert
REGEX='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: .{1,72}$'

# 跳过 merge commit / fixup
if [[ "$HEADER" =~ ^Merge\ |^fixup!\ |^squash!\  ]]; then
    exit 0
fi

if [[ ! "$HEADER" =~ $REGEX ]]; then
    cat >&2 <<EOF
[BLOCK] commit-msg | header: "$HEADER" | reason: 不符合 Conventional Commits
fix: type(scope): subject  (≤72 chars)
     types: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert
     example: feat(auth): add OAuth2 login flow
EOF
    exit 1
fi

exit 0
