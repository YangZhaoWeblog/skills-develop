#!/usr/bin/env bash
# Prepare project files. Semantic merging and completion checks belong to the Skill.
set -euo pipefail

api=true
data=true
accept_legacy=false
target=""
for option in "$@"; do
  case "$option" in
    --has-api=*) api="${option#*=}" ;;
    --has-db=*) data="${option#*=}" ;;
    --accept-migrations) accept_legacy=true ;;
    --*) printf '[ERROR] Unknown option: %s\n' "$option" >&2; exit 2 ;;
    *)
      if [[ -n "$target" ]]; then printf '%s\n' '[ERROR] Supply one project directory.' >&2; exit 2; fi
      target="$option"
      ;;
  esac
done
for value in "$api" "$data"; do
  case "$value" in true|false) ;; *) printf '%s\n' '[ERROR] Capability flags must be true or false.' >&2; exit 2 ;; esac
done
target="${target:-$PWD}"
if [[ ! -d "$target" || ! -r "$target" || ! -x "$target" ]]; then
  printf '[ERROR] Project directory is unavailable: %s\n' "$target" >&2; exit 2
fi
target="$(cd "$target" && pwd -P)"
skill="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
for folder in project workflows/product workflows/development; do
  [[ -d "$skill/assets/$folder" ]] || { printf '[ERROR] Missing asset directory: %s\n' "$folder" >&2; exit 2; }
done

# Do not follow directory links while writing the selected project.
safe_parent() {
  local relative="$1" cursor="$target" part
  while [[ "$relative" == */* ]]; do
    part="${relative%%/*}"; relative="${relative#*/}"; cursor="$cursor/$part"
    if [[ -L "$cursor" || ( -e "$cursor" && ! -d "$cursor" ) ]]; then
      printf '[ERROR] Destination parent needs review: %s\n' "$cursor" >&2; return 1
    fi
  done
}
for path in .harness/docs/entry .harness/plans/entry .harness/templates/product/entry .harness/templates/development/entry; do
  safe_parent "$path" || exit 2
done

legacy=false
for path in harness .harness/context .harness/tasks .harness/docs/sqls .harness/docs/apis .harness/docs/devops .harness/docs/unittest .harness/docs/integration_test .harness/docs/database.md .harness/docs/relationship.md .harness/plans/_template .harness/plans/_dev-template .harness/plans/_product-template ARCHITECTURE.md; do
  if [[ -e "$target/$path" || -L "$target/$path" ]]; then
    legacy=true; printf '[MERGE] Existing layout retained: %s\n' "$path"
  fi
done
if [[ "$legacy" == true && "$accept_legacy" != true ]]; then
  printf '%s\n' '[CONFIRM] Review the layout migration before preparing new paths. No files changed.'
  printf '%s\n' 'After approval, rerun with --accept-migrations. Existing content will remain until explicitly merged.'
  exit 3
fi

copy_missing() {
  local source="$1" relative="$2" destination="$target/$2"
  safe_parent "$relative" || return 2
  if [[ -e "$destination" || -L "$destination" ]]; then
    printf '[KEEP] %s\n' "$relative"; return 0
  fi
  mkdir -p "$(dirname "$destination")"
  cp "$source" "$destination"
  printf '[ADD] %s\n' "$relative"
}

# Map only for locating existing material; this script never removes old project files.
legacy_context() {
  local path="$1"
  path="${path#docs/}"
  case "$path" in
    contracts/*) path="apis/${path#contracts/}" ;;
    data/*) path="sqls/${path#data/}" ;;
    runtime/*) path="devops/${path#runtime/}" ;;
    testing/unit-tests.md) path="unittest/unit_test.md" ;;
    testing/integration-test.md) path="integration_test/integration_test.md" ;;
    testing/*) path="unittest/${path#testing/}" ;;
    dependencies.md) path="relationship.md" ;;
  esac
  printf '%s' "$path"
}
while IFS= read -r -d '' source; do
  relative="${source#"$skill/assets/project/"}"
  case "$relative" in
    docs/contracts/*) [[ "$api" == false ]] && continue ;;
    docs/data/*) [[ "$data" == false ]] && continue ;;
  esac
  old="$(legacy_context "$relative")"
  old_found=false
  for candidate in "$target/.harness/docs/$old" "$target/harness/$old" "$target/.harness/context/${relative#docs/}"; do
    [[ "$candidate" != "$target/.harness/$relative" ]] || continue
    if [[ -e "$candidate" || -L "$candidate" ]]; then old_found=true; fi
  done
  case "$relative" in
    docs/architecture.md) [[ ! -e "$target/ARCHITECTURE.md" && ! -L "$target/ARCHITECTURE.md" ]] || old_found=true ;;
    docs/testing/unit-tests.md) [[ ! -e "$target/.harness/docs/unittest/unittest.md" && ! -L "$target/.harness/docs/unittest/unittest.md" ]] || old_found=true ;;
    docs/runtime/local-dev.md)
      for name in local-dev.md development.md env.md; do
        [[ ! -e "$target/.harness/docs/devops/$name" && ! -L "$target/.harness/docs/devops/$name" ]] || old_found=true
      done ;;
    docs/runtime/release.md) [[ ! -e "$target/.harness/docs/devops/deployment.md" && ! -L "$target/.harness/docs/devops/deployment.md" ]] || old_found=true ;;
  esac
  flat_names=""
  case "$relative" in
    docs/data/database.md) flat_names="database.md" ;;
    docs/contracts/api-standards.md) flat_names="api-standards.md" ;;
    docs/runtime/local-dev.md) flat_names="development.md env.md local-dev.md" ;;
    docs/runtime/release.md) flat_names="deployment.md release.md" ;;
  esac
  for name in $flat_names; do
    for base in "$target/.harness/docs" "$target/harness"; do
      [[ ! -e "$base/$name" && ! -L "$base/$name" ]] || old_found=true
    done
  done
  if [[ "$old_found" == true ]]; then
    printf '[MERGE] Populate .harness/%s from existing project material; no blank replacement copied.\n' "$relative"
    continue
  fi
  copy_missing "$source" ".harness/$relative"
done < <(find "$skill/assets/project" -type f ! -name '.DS_Store' -print0)

mkdir -p "$target/.harness/plans"
for kind in product development; do
  while IFS= read -r -d '' source; do
    relative="${source#"$skill/assets/workflows/$kind/"}"
    output=".harness/templates/$kind/$relative"
    safe_parent "$output" || exit 2
    destination="$target/$output"
    if [[ -L "$destination" || ( -e "$destination" && ! -f "$destination" ) ]]; then
      printf '[MERGE] Template destination retained: %s\n' "$output"; continue
    fi
    mkdir -p "$(dirname "$destination")"
    if [[ ! -f "$destination" ]] || ! cmp -s "$source" "$destination"; then
      cp "$source" "$destination"; printf '[TEMPLATE] %s\n' "$output"
    fi
  done < <(find "$skill/assets/workflows/$kind" -type f ! -name '.DS_Store' -print0)
done

# Keep every existing lint configuration, regardless of the supported filename.
if [[ -f "$target/go.mod" ]]; then
  lint_present=false
  for name in .golangci.yml .golangci.yaml .golangci.json .golangci.toml; do
    [[ ! -e "$target/$name" && ! -L "$target/$name" ]] || lint_present=true
  done
  [[ "$lint_present" == true ]] || copy_missing "$skill/assets/.golangci.yml" .golangci.yml
fi
# The standard Workflow is owned by the Skill; project chapters remain intact.
workflow_bounds() {
  awk '
    {
      line = $0
      sub(/^[ \t]*/, "", line)
      if (fence != "") {
        if ($0 ~ /^## 二、/ || $0 ~ /^## 三、/) uncertain = 1
        closing = line
        gsub(fence, "", closing)
        if (substr(line, 1, width) == marker && closing ~ /^[ \t]*$/) fence = ""
        next
      }
      if (line ~ /^```/ || line ~ /^~~~/) {
        fence = substr(line, 1, 1)
        match(line, /^`+|^~+/)
        width = RLENGTH; marker = substr(line, 1, width)
        next
      }
    }
    /^## 二、/ {
      start = NR; starts++
      if ($0 !~ /^## 二、(Workflow|SOP)([[:space:]（(]|$)/) uncertain = 1
    }
    /^## 三、/ { finish = NR; finishes++ }
    END {
      if (uncertain || fence != "" || starts != 1 || finishes != 1 || start >= finish) exit 1
      print start, finish
    }
  ' "$1"
}
refresh_entry() (
  local entry="$target/AGENTS.md" source="$skill/assets/agents.md"
  local old_bounds source_bounds old_start old_end source_start source_end scratch
  if [[ ! -e "$entry" && ! -L "$entry" ]]; then
    copy_missing "$source" AGENTS.md; return
  fi
  if [[ -L "$entry" || ! -f "$entry" ]]; then
    printf '%s\n' '[MERGE] AGENTS.md retained; resolve its file type before merging.'; return
  fi
  if ! old_bounds="$(workflow_bounds "$entry")"; then
    printf '%s\n' '[MERGE] AGENTS.md retained; merge project rules into the source template before retrying.'; return
  fi
  source_bounds="$(workflow_bounds "$source")" || {
    printf '%s\n' '[ERROR] Source Workflow chapter boundaries are invalid.' >&2; return 2
  }
  read -r old_start old_end <<< "$old_bounds"
  read -r source_start source_end <<< "$source_bounds"
  scratch="$(mktemp -d "$target/.harness/entry-refresh.XXXXXX")"
  trap 'rm -rf "$scratch"' EXIT
  cp -p "$entry" "$scratch/AGENTS.md"
  {
    head -n "$((old_start - 1))" "$entry"
    sed -n "${source_start},$((source_end - 1))p" "$source"
    tail -n "+$old_end" "$entry"
  } > "$scratch/AGENTS.md"
  if cmp -s "$entry" "$scratch/AGENTS.md"; then
    printf '%s\n' '[KEEP] AGENTS.md; source Workflow is intact.'
  else
    mv "$scratch/AGENTS.md" "$entry"
    printf '%s\n' '[WORKFLOW] AGENTS.md chapter II restored from source; other chapters retained.'
  fi
)
refresh_entry
if [[ ! -e "$target/CLAUDE.md" && ! -L "$target/CLAUDE.md" ]]; then
  ln -s AGENTS.md "$target/CLAUDE.md"
  printf '%s\n' '[LINK] CLAUDE.md -> AGENTS.md'
else
  printf '%s\n' '[KEEP] CLAUDE.md; verify its connection to the current project rules.'
fi
if [[ -f "$skill/scripts/setup_hooks.sh" ]]; then
  bash "$skill/scripts/setup_hooks.sh" "$target"
fi
printf '%s\n' '[PREPARED] Assets prepared; project integration has not yet been verified.'
printf '%s\n' '[NEXT] Merge project facts, configure native agents and checks, verify their effects, then report COMPLETE or INCOMPLETE with remaining gaps.'
