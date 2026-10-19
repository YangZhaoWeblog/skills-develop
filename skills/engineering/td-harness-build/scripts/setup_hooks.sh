#!/usr/bin/env bash
# Prepare repository-local hook scripts; preserve every existing installation.
set -euo pipefail
[[ $# -le 1 ]] || { printf '%s\n' '[ERROR] Expected one project directory.' >&2; exit 2; }
start="${1:-$PWD}"
[[ -d "$start" ]] || { printf '[SKIP] Directory is unavailable: %s\n' "$start"; exit 0; }
root="$(git -C "$start" rev-parse --show-toplevel 2>/dev/null)" || {
  printf '%s\n' '[SKIP] Git is not initialized; hooks were not installed.'; exit 0
}
source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$root"
if [[ -L scripts || ( -e scripts && ! -d scripts ) ]]; then
  printf '%s\n' '[MERGE] scripts is not a regular project directory; retain it and choose an installation location.'; exit 0
fi
mkdir -p scripts
for name in pre_commit_check.sh pre_push_check.sh commit_msg_check.sh; do
  if [[ -e "scripts/$name" || -L "scripts/$name" ]]; then
    printf '[KEEP] scripts/%s\n' "$name"
  elif [[ -f "$source_dir/$name" ]]; then
    cp "$source_dir/$name" "scripts/$name"
    chmod +x "scripts/$name"
    printf '[PREPARED] scripts/%s\n' "$name"
  else
    printf '[GAP] Missing hook source: %s\n' "$name" >&2
  fi
done
configured="$(git config --get core.hooksPath || true)"
if [[ -n "$configured" ]]; then
  printf '[KEEP] core.hooksPath=%s; integrate there under project authorization.\n' "$configured"
  exit 0
fi
hooks="$(git rev-parse --git-path hooks)"
[[ "$hooks" == /* ]] || hooks="$root/$hooks"
if [[ -L "$hooks" || ( -e "$hooks" && ! -d "$hooks" ) ]]; then
  printf '[MERGE] Hooks directory retained: %s\n' "$hooks"; exit 0
fi
mkdir -p "$hooks"
for hook in pre-commit pre-push commit-msg; do
  case "$hook" in
    pre-commit) file=pre_commit_check.sh ;;
    pre-push) file=pre_push_check.sh ;;
    commit-msg) file=commit_msg_check.sh ;;
  esac
  destination="$hooks/$hook"
  if [[ -e "$destination" || -L "$destination" ]]; then
    printf '[KEEP] Existing hook: %s\n' "$hook"; continue
  fi
  if [[ ! -f "scripts/$file" || ! -x "scripts/$file" ]]; then
    printf '[GAP] Not executable: scripts/%s\n' "$file"; continue
  fi
  if grep -q '^[[:space:]]*# HARNESS_PROJECT_CHECKS_PENDING$' "scripts/$file"; then
    printf '[PENDING] Configure and verify scripts/%s before activation.\n' "$file"; continue
  fi
  link="$root/scripts/$file"
  [[ "$hooks" != "$root/.git/hooks" ]] || link="../../scripts/$file"
  ln -s "$link" "$destination"
  printf '[LINK] %s\n' "$hook"
done
printf '%s\n' '[NEXT] Verify actual hook execution. Retained or pending entries are not proof of activation.'
