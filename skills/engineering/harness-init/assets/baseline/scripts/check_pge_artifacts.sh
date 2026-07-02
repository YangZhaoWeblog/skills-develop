#!/usr/bin/env bash
# check_pge_artifacts.sh — lightweight PGE artifact existence check.
#
# Default mode checks changed docs/pge and docs/design files only.
# Strong mode:
#   PGE_REQUIRED=1    require Sprint Contract and matching evaluator report files.
#   DESIGN_REQUIRED=1 require a changed or explicitly provided design doc.
# Optional:
#   PGE_SPEC=docs/pge/<sprint>-spec.md
#   DESIGN_DOC=docs/design/DESIGN-001-example.md

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

fail=0
warn_count=0

block() {
  echo -e "${RED}[BLOCK]${RESET} pge_artifact | $1 | $2" >&2
  fail=1
}

warn() {
  echo -e "${YELLOW}[WARN]${RESET} pge_artifact | $1 | $2" >&2
  warn_count=$((warn_count + 1))
}

info() {
  echo -e "${CYAN}[INFO]${RESET} $*" >&2
}

changed_files=()
while IFS= read -r file; do
  [[ -n "$file" ]] && changed_files+=("$file")
done < <(git diff --name-only --diff-filter=ACMR HEAD -- docs/pge docs/design 2>/dev/null || true)

while IFS= read -r file; do
  [[ -n "$file" ]] && changed_files+=("$file")
done < <(git ls-files --others --exclude-standard docs/pge docs/design 2>/dev/null || true)

specs=()
evals=()
designs=()

if [[ ${#changed_files[@]} -gt 0 ]]; then
  for file in "${changed_files[@]}"; do
    case "$file" in
      docs/pge/*-spec.md) specs+=("$file") ;;
      docs/pge/*-eval.md) evals+=("$file") ;;
      docs/design/DESIGN-[0-9]*-*.md) designs+=("$file") ;;
    esac
  done
fi

if [[ -n "${PGE_SPEC:-}" ]]; then
  [[ -f "$PGE_SPEC" ]] || block "$PGE_SPEC" "file does not exist"
  specs+=("$PGE_SPEC")
fi

if [[ -n "${DESIGN_DOC:-}" ]]; then
  [[ -f "$DESIGN_DOC" ]] || block "$DESIGN_DOC" "file does not exist"
  designs+=("$DESIGN_DOC")
fi

if [[ ${#specs[@]} -eq 0 && ${#evals[@]} -eq 0 && ${PGE_REQUIRED:-0} != "1" && ${DESIGN_REQUIRED:-0} != "1" ]]; then
  echo -e "${GREEN}[OK]${RESET} No changed PGE artifacts"
  exit 0
fi

if [[ ${#specs[@]} -gt 0 ]]; then
  for spec in "${specs[@]}"; do
    eval_file="${spec%-spec.md}-eval.md"
    if [[ ! -f "$eval_file" ]]; then
      if [[ "${PGE_REQUIRED:-0}" == "1" ]]; then
        block "$spec" "PGE_REQUIRED=1 but corresponding eval is missing: ${eval_file}"
      else
        warn "$spec" "corresponding eval not found: ${eval_file}"
      fi
    fi
  done
fi

if [[ ${#evals[@]} -gt 0 ]]; then
  for eval_file in "${evals[@]}"; do
    spec_file="${eval_file%-eval.md}-spec.md"
    if [[ ! -f "$spec_file" ]]; then
      block "$eval_file" "corresponding spec not found: ${spec_file}"
    fi
  done
fi

if [[ "${PGE_REQUIRED:-0}" == "1" && ${#specs[@]} -eq 0 ]]; then
  has_contract=0
  if [[ ${#evals[@]} -gt 0 ]]; then
    for eval_file in "${evals[@]}"; do
      [[ -f "${eval_file%-eval.md}-spec.md" ]] && has_contract=1
    done
  fi
  if [[ "$has_contract" -eq 0 ]]; then
    block "docs/pge" "PGE_REQUIRED=1 but no spec found; set PGE_SPEC=docs/pge/<sprint>-spec.md if reusing an existing contract"
  fi
fi

if [[ "${DESIGN_REQUIRED:-0}" == "1" && ${#designs[@]} -eq 0 ]]; then
  block "docs/design" "DESIGN_REQUIRED=1 but no changed design doc found; set DESIGN_DOC=docs/design/DESIGN-xxx-name.md if reusing an existing design"
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

if [[ "$warn_count" -gt 0 ]]; then
  info "PGE artifact check passed with ${warn_count} warning(s)"
else
  echo -e "${GREEN}[OK]${RESET} PGE artifact check passed"
fi
