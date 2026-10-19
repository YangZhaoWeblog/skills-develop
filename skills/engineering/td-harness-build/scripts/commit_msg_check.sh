#!/usr/bin/env bash
# Validate a commit title without changing the message or Git history.
set -euo pipefail
message="${1:-}"
[[ -n "$message" && -f "$message" ]] || exit 0
title="$(awk '!/^#/ && /[^[:space:]]/ { print; exit }' "$message")"
if [[ -z "$title" ]]; then printf '%s\n' '[BLOCK] Write a non-empty commit title.' >&2; exit 1; fi
if [[ ${#title} -lt 10 ]]; then
  printf '%s\n' '[BLOCK] Commit title must contain at least 10 characters and describe the change.' >&2; exit 1
fi
if [[ ${#title} -gt 72 ]]; then printf '%s\n' '[WARN] Keep the title near 72 characters; put details in the body.' >&2; fi
if [[ "${DISABLE_CONV_COMMITS:-}" != 1 ]]; then
  pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|other)(\(.+\))?(!)?:[[:space:]].+'
  if ! printf '%s\n' "$title" | grep -Eq "$pattern"; then
    printf '%s\n' '[BLOCK] Use type(scope): description, for example: fix(parser): handle empty input.' >&2
    exit 1
  fi
fi
