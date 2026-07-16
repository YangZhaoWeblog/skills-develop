#!/usr/bin/env bash
# check_pge_contracts.sh - structural checks for PGE spec/eval documents.

set -euo pipefail

MODE="worktree"
FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --staged)
      MODE="staged"
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage:
  bash scripts/check_pge_contracts.sh [--staged] [files...]

Checks only machine-readable PGE document structure. It does not judge
requirements quality, semantic drift, or acceptance sufficiency.
USAGE
      exit 0
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 && "${MODE}" == "staged" ]]; then
  while IFS= read -r file; do
    [[ -n "${file}" ]] && FILES+=("${file}")
  done < <(git diff --cached --name-only --diff-filter=ACMR -- 'docs/pge/*.md')
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "[OK] pge_contracts: no files to check"
  exit 0
fi

FAILED=0
CHECKED=0

block() {
  local file="$1" reason="$2"
  echo "[BLOCK] pge_contract | ${file}:0 | ${reason}" >&2
  FAILED=1
}

is_pge_contract_file() {
  local file="$1"
  [[ "${file}" == docs/pge/spec.template.md ]] && return 0
  [[ "${file}" == docs/pge/eval.template.md ]] && return 0
  [[ "${file}" =~ ^docs/pge/.+-spec\.md$ ]] && return 0
  [[ "${file}" =~ ^docs/pge/.+-eval\.md$ ]] && return 0
  return 1
}

content_has() {
  local file="$1" pattern="$2"
  if [[ "${MODE}" == "staged" ]]; then
    git show ":${file}" 2>/dev/null | grep -Eq "${pattern}"
  else
    grep -Eq "${pattern}" "${file}" 2>/dev/null
  fi
}

path_exists() {
  local file="$1"
  if [[ "${MODE}" == "staged" ]]; then
    git cat-file -e ":${file}" 2>/dev/null || [[ -f "${file}" ]]
  else
    [[ -f "${file}" ]]
  fi
}

exists_in_head() {
  git cat-file -e "HEAD:$1" 2>/dev/null
}

requires_current_protocol() {
  local file="$1" template="$2"
  [[ "${template}" == "1" ]] && return 0
  content_has "${file}" 'PGE.*(protocol|协议).*(version|版本)[^0-9]*2' && return 0
  ! exists_in_head "${file}"
}

require_pattern() {
  local file="$1" label="$2" pattern="$3"
  if ! content_has "${file}" "${pattern}"; then
    block "${file}" "missing required ${label}"
  fi
}

check_spec() {
  local file="$1" template="$2"
  requires_current_protocol "${file}" "${template}" || return 0

  require_pattern "${file}" "PGE protocol version 2" 'PGE.*(protocol|协议).*(version|版本)[^0-9]*2'
  require_pattern "${file}" "goal section" '^##[[:space:]]+.*(目标|Goal)'
  require_pattern "${file}" "scope section" '^##[[:space:]]+.*(范围|Scope)'
  require_pattern "${file}" "acceptance section" '^##[[:space:]]+.*(验收标准|Acceptance)'
  require_pattern "${file}" "non-goals section" '^##[[:space:]]+.*(非目标|Non-Goals?)'
  require_pattern "${file}" "implementation order section" '^##[[:space:]]+.*(实现顺序|Implementation Order)'
  require_pattern "${file}" "RED plan section" '^##[[:space:]]+.*(RED|Tracer|验证计划)'
  require_pattern "${file}" "Grill Closure section" '^##[[:space:]]+.*Grill[[:space:]]+Closure'
  require_pattern "${file}" "verification commands section" '^##[[:space:]]+.*(验证命令|Verification Commands?)'
  require_pattern "${file}" "verify_cmd record" 'verify_cmd'
  require_pattern "${file}" "contract_revision field" '"contract_revision"'
  require_pattern "${file}" "human_start_gate block" '"human_start_gate"'
  require_pattern "${file}" "approved_contract_revision field" '"approved_contract_revision"'
  require_pattern "${file}" "pge_fallback block" '"pge_fallback"'
  require_pattern "${file}" "main-agent self-review status" '"main_agent_self_review"'
  require_pattern "${file}" "owner acknowledgement status" '"owner_ack_status"'
  require_pattern "${file}" "independent Evaluator assurance status" '"independent_evaluator_assurance"'

  require_pattern "${file}" "parallel_dispatch block" '"parallel_dispatch"'
}

check_eval() {
  local file="$1" template="$2"
  requires_current_protocol "${file}" "${template}" || return 0

  require_pattern "${file}" "PGE protocol version 2" 'PGE.*(protocol|协议).*(version|版本)[^0-9]*2'
  require_pattern "${file}" "result section" '^##[[:space:]]+.*(验收结果|Result)'
  require_pattern "${file}" "Contract drift row" 'Contract[[:space:]]*漂移|Contract[[:space:]]*drift'
  require_pattern "${file}" "Human Start Gate row" 'Human[[:space:]]+Start[[:space:]]+Gate'
  require_pattern "${file}" "parallel integration row" '并行集成|Parallel[[:space:]]*integration'
  require_pattern "${file}" "code review row" '代码质量|Code[[:space:]]*(quality|Review)'
  require_pattern "${file}" "owner acceptance record" '负责人确认|Owner[[:space:]]*(acceptance|acknowledgement)'
  require_pattern "${file}" "execution record section" '^##[[:space:]]+.*(执行记录|Verification|Execution)'
  require_pattern "${file}" "verify_cmd record" 'verify_cmd'
  require_pattern "${file}" "conclusion section" '^##[[:space:]]+.*(结论|Conclusion)'
  require_pattern "${file}" "findings section" '^##[[:space:]]+.*(发现|Findings)'

  if [[ "${template}" != "1" ]]; then
    local spec_file="${file%-eval.md}-spec.md"
    if ! path_exists "${spec_file}"; then
      block "${file}" "missing paired spec ${spec_file}"
    elif ! content_has "${spec_file}" 'PGE.*(protocol|协议).*(version|版本)[^0-9]*2'; then
      block "${file}" "paired spec must use PGE protocol version 2: ${spec_file}"
    fi
  fi
}

for file in "${FILES[@]}"; do
  is_pge_contract_file "${file}" || continue

  if ! path_exists "${file}"; then
    block "${file}" "file does not exist"
    continue
  fi

  CHECKED=$((CHECKED + 1))
  case "${file}" in
    docs/pge/spec.template.md)
      check_spec "${file}" "1"
      ;;
    docs/pge/eval.template.md)
      check_eval "${file}" "1"
      ;;
    *-spec.md)
      check_spec "${file}" "0"
      ;;
    *-eval.md)
      check_eval "${file}" "0"
      ;;
  esac
done

if [[ "${FAILED}" -ne 0 ]]; then
  exit 1
fi

echo "[OK] pge_contracts: checked ${CHECKED} file(s)"
