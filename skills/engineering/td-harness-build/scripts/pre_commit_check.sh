#!/usr/bin/env bash
# Check the staged snapshot and the project's configured formatting entry.
set -euo pipefail
if [[ "${SKIP_PRE_COMMIT:-}" == 1 ]]; then
  printf '%s\n' '[SKIP] pre-commit was explicitly bypassed; checks not executed.'; exit 0
fi
root="$(git rev-parse --show-toplevel)" || exit 2
cd "$root"
paths=()
while IFS= read -r -d '' path; do paths+=("$path"); done < <(git diff --cached --name-only --diff-filter=ACMR -z)
if [[ ${#paths[@]} -eq 0 ]]; then printf '%s\n' '[OK] No staged files to check.'; exit 0; fi
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
failed=0
block() { printf '[BLOCK] %s | %s\n' "$1" "$2" >&2; failed=1; }

check_formatting() {
  # HARNESS_PROJECT_CHECKS_PENDING
  # Replace with the project's verified read-only command; then remove the marker.
  # An inapplicable check needs an explicit reason and return 0, not a missing-tool bypass.
  printf '%s\n' '[BLOCK] Project formatting check is not configured. Configure check_formatting, verify it, then retry.' >&2
  return 2
}

for path in "${paths[@]}"; do
  # Filenames are a precaution, not a substitute for the project's secret scanner.
  case "$path" in
    docs/*|specs/*|README*|CHANGELOG*|test/fixtures/*|tests/fixtures/*|__fixtures__/*) ;;
    *)
      if printf '%s\n' "$path" | grep -Eiq '(^|/)(\.env([.]|$)|credentials|id_rsa|id_ed25519|token\.json|\.npmrc|\.pypirc|kubeconfig)|\.env($|\.)|\.secret|\.(pem|key|p12|pfx|jks|keystore|cert|crt)$|secrets\.ya?ml$|private.*key|service.account\.json$|\.docker/config\.json$'; then
        block "$path" 'Potential credential file; review it before staging.'
      fi ;;
  esac
  if printf '%s\n' "$path" | grep -Eq '^(vendor|node_modules|dist|build|out|target|\.eggs|\.gradle|obj)/|(^|/)__pycache__/|^bin/(Debug|Release)/|\.egg-info/|cover.*\.out$|\.(pyc|pyo|exe|dll|so|dylib|a|lib|wasm)$'; then
    block "$path" 'Build output or dependency directory; use the project artifact policy.'
  fi
  index_mode="$(git ls-files --stage -- "$path")"
  if [[ "$index_mode" == 160000\ * ]]; then continue; fi
  if ! git show ":$path" > "$work/content"; then
    block "$path" 'Cannot read the staged object.'; continue
  fi
  bytes="$(wc -c < "$work/content" | tr -d ' ')"
  if [[ "$bytes" -gt 5242880 ]]; then block "$path" 'File exceeds 5 MiB; use an approved large-file storage method.'; fi
  # A separator alone can be a Markdown heading; retain conflict boundary/base checks.
  if grep -Iq . "$work/content" && grep -Eq '^(<{7,}|>{7,}|\|{7,})([[:space:]]|$)' "$work/content"; then
    block "$path" 'Unresolved merge markers in the staged content.'
  fi
  git diff --cached --no-ext-diff --no-textconv -U0 -- "$path" > "$work/diff"
  sed -n '/^+++ /d; s/^+//p' "$work/diff" > "$work/added"
  case "$path" in
    test/*|tests/*|*/test/*|*/tests/*|test_*.py|*/test_*.py|*_test.py|*_test.rs|*.test.*|*.spec.*) ;;
    *.rs) if grep -Eq '^[[:space:]]*[^/#]*dbg!\(' "$work/added"; then block "$path" 'Remove the temporary debugger macro.'; fi ;;
    *.py) if grep -Eq '^[[:space:]]*[^#]*breakpoint\(' "$work/added"; then block "$path" 'Remove the temporary breakpoint.'; fi ;;
  esac
  if grep -Eiq '^[[:space:]]*(//|#|/\*|\*)?[[:space:]]*(TODO[[:space:]]*(REMOVE|DELETE|HACK)|FIXME[[:space:]]*(REMOVE|DELETE)|DO NOT COMMIT|DO NOT MERGE|TEMP HACK)' "$work/added"; then
    block "$path" 'A newly added temporary marker requires resolution.'
  fi
  if [[ "${AI_TEST_GUARD:-}" == 1 && "${SKIP_TEST_GUARD:-}" != 1 ]]; then
    case "$path" in
      *_test.go|*.test.*|*.spec.*|test_*.py|*/test_*.py|*_test.py|*Test.java|*_test.rs)
        sed '/^--- /d; /^+++ /d' "$work/diff" > "$work/changes"
        if git cat-file -e "HEAD:$path" 2>/dev/null && grep -Eq '^[-+].*(assert|require\.|expect\(|pytest\.raises|\.EXPECT\(|verify\()' "$work/changes"; then
          block "$path" 'Project test-assertion guard requires an explicitly reviewed expectation change.'
        fi ;;
    esac
  fi
done

# A conditional function call would disable errexit within its body.
set +e
( set -e; check_formatting </dev/null )
format_status=$?
set -e
if [[ "$format_status" -ne 0 ]]; then failed=1; fi
if [[ "$failed" -ne 0 ]]; then
  printf '%s\n' '[BLOCK] Resolve the reported staged-file or project-check failures.' >&2; exit 1
fi
printf '%s\n' '[OK] Staged-file and configured formatting checks passed.'
