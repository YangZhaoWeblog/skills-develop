---
name: td-harness-init
description: Initialize the td-harness in a project — creates AGENTS.md (≤200 lines), harness/* sub-rules, state files (PROGRESS/DECISIONS), git hooks (razor-block / WIP=1 / test-guard), and PGE templates. Use when starting a new project, retrofitting an existing repo, or onboarding AI agents to a codebase that doesn't yet have an AGENTS.md. Triggers when user says "init harness", "build the harness", "set up AGENTS.md", "td-harness", "新项目起 harness", "给项目装 harness", "初始化 harness".
---

# td-harness-init

> Initialize the **td-harness** in a project — five-subsystem AI development harness, distilled from 8 rounds of roundtable discussion + walkinglabs lecture series + SOP/PGE design notes.
>
> **Goal**: Make the repository the single executable source of truth, so AI agents read AGENTS.md and write working code on cold start.

## Core Principles (硬约束，违反即 BLOCK)

1. **Razor BLOCK at 200 lines** — `AGENTS.md` longer than 200 lines = design failure → split to `harness/*.md`
2. **WIP=1** — `PROGRESS.md` may have at most one `- [~]` in-progress marker (Little's law)
3. **Tools beat AI self-check** — verification commands hooked at commit-time, not just documented
4. **Sub-agent physics** — depth ≤2, width ≤5, file handoff only, no SendMessage between short-lived sub-agents
5. **Cold-start test** — a fresh AI session reading only AGENTS.md must answer 5 questions about the project

## Concept Foundation (references/concepts/)

This skill is generated FROM 7 concept atoms — read them when in doubt:

- `five-subsystems.md` — instruction / tools / env / state / feedback
- `tools-over-ai.md` — verification > AI self-evaluation
- `razor-block-200.md` — AGENTS.md size discipline
- `pge-three-tiers.md` — Planner-Generator-Evaluator three-tier physical form (fractal: outer sequential, inner parallel)
- `sub-agent-physics.md` — hard limits on sub-agent calling
- `parallel-decision.md` — when sub-tasks may run in parallel
- `td-harness-three-skills.md` — init / eval / update lifecycle

**These concepts are the spec, this skill is the implementation.** When the spec says "200" the skill hard-codes 200 (v0.1 — no drift detection yet).

---

## Step 1 — Resolve target

Two input modes:

| User says | Action |
|-----------|--------|
| "init harness here" / no path | `REPO_ROOT = $(git rev-parse --show-toplevel)` |
| Path argument given | `REPO_ROOT = <path>`; verify it exists & is a git repo (or `git init` after confirming) |

**Strict separation**: `REPO_ROOT` (target project) vs `SKILL_DIR` (this skill's directory). Never write skill files into REPO_ROOT, never write project files into SKILL_DIR.

```bash
SKILL_DIR="$(dirname "$(readlink -f "$0")")"  # this skill
REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
```

If `REPO_ROOT` already has `AGENTS.md`:
- Confirm with user: re-init / merge / abort?
- Default: **abort and report**, never overwrite silently.

## Step 2 — Probe environment

Detect:
- Language stack (look for `go.mod` / `package.json` / `pyproject.toml` / `Cargo.toml`)
- Build tool (`Makefile` / `pnpm-lock.yaml` / `uv.lock` / `cargo.lock`)
- Existing CI (`.github/workflows/` / `.gitlab-ci.yml`)
- Existing hook system (`lefthook.yml` / `.husky/` / `.pre-commit-config.yaml`)
- Existing AI rule files (`CLAUDE.md` / `GEMINI.md` / `CODEBUDDY.md` — will become symlinks)

Record findings in a probe report; user confirms before generation.

## Step 3 — Generate state files & AGENTS.md

Render `references/templates/AGENTS.md.tmpl` → `${REPO_ROOT}/AGENTS.md` with stack-specific substitution.

**Validate immediately**:
```bash
LINES=$(wc -l < "${REPO_ROOT}/AGENTS.md")
[[ $LINES -le 200 ]] || { echo "[BLOCK] template generated ${LINES} lines, exceeds 200"; exit 1; }
```

Render the rest:
- `PROGRESS.md` (with cold-start guide)
- `DECISIONS.md` (decision-record skeleton)

## Step 4 — Generate harness/ (4 必备 + 按需)

**Always generate** (从踩坑根因看，这 4 个最常被需要):
- `harness/coding-style.md`
- `harness/glossary.md`
- `harness/failures.md` — 反馈循环的关键载体
- `harness/testing.md` — 完成定义

**Conditional** (基于 stack 探测):
- `harness/api-standards.md` (有 API 层)
- `harness/database.md` (有 DB)
- `harness/development.md` (PGE 档位 + Spec 重量决策)
- `harness/deployment.md` (有 deploy/ 或 CI)
- `harness/dependency-map.md` (monorepo 或 多模块)
- `harness/code-review.md` (≥2 人协作)

**信噪比原则**: 不需要的 harness/* 不创建 — 它会变成 lecture-04 的"加新规则就治理"反模式。

## Step 5 — Symlink AI tool entries

```bash
cd "${REPO_ROOT}"
[[ ! -L CLAUDE.md ]]    && ln -s AGENTS.md CLAUDE.md
[[ ! -L GEMINI.md ]]    && ln -s AGENTS.md GEMINI.md
[[ ! -L CODEBUDDY.md ]] && ln -s AGENTS.md CODEBUDDY.md
```

Symlinks ensure single source of truth — `concepts/five-subsystems.md` §instruction.

## Step 6 — Install hooks (反馈子系统 ROI 最高)

Run `references/hooks/install_hooks.sh ${REPO_ROOT}`:

1. Copy hook scripts to `${REPO_ROOT}/scripts/`
2. If `lefthook` is on PATH → render `lefthook.yml.tmpl` → `lefthook install`
3. Otherwise → install directly to `.git/hooks/{pre-commit,commit-msg,pre-push}`
4. Create `.harness/metrics.tsv` for hook-time metric collection (layer 1 of three-layer ledger)

**Hook coverage**:
- `pre-commit`: razor-block / WIP / test-guard / project `make check`
- `commit-msg`: Conventional Commits format
- `pre-push`: `make e2e` + clean-state check

## Step 7 — Generate .pge/ template (按需)

If user expects PGE tier 2/3 work: render `.pge/spec.md.tmpl` → `.pge/spec.md` (skeleton, with `parallel_tasks` section commented out by default — opt-in only).

Otherwise skip; tier-1 tasks need no `.pge/`.

## Step 8 — README footprint + git ignore

Append to top of `${REPO_ROOT}/README.md`:

```markdown
> Harnessed by [td-harness-init](https://github.com/...) v0.1 on YYYY-MM-DD.
> AI agents: read [AGENTS.md](AGENTS.md) before any code change.
```

Append to `.gitignore`:
```
.pge/code/         # PGE intermediate code (use feature branch instead)
.harness/tmp/      # Transient harness state
```

`.harness/metrics.tsv` and `.harness/campaign.json` are committed — they're history.

## Step 9 — Verify (Linus 7-clause machine ship test)

Run all checks; report PASS/FAIL per clause:

| # | Clause | Command |
|---|--------|---------|
| 1 | AGENTS.md generated | `test -f AGENTS.md` |
| 2 | AGENTS.md ≤200 lines | `[ $(wc -l < AGENTS.md) -le 200 ]` |
| 3 | ≥4 harness/ files | `[ $(ls harness/*.md \| wc -l) -ge 4 ]` |
| 4 | Hooks installed | `test -f .git/hooks/pre-commit -o -f lefthook.yml` |
| 5 | PROGRESS.md / DECISIONS.md exist | `test -f PROGRESS.md && test -f DECISIONS.md` |
| 6 | pre_commit_check exits 0 on clean repo | `bash scripts/pre_commit_check.sh` |
| 7 | README footprint added | `head -3 README.md \| grep -q td-harness-init` |

If any clause fails → report which + suggested fix; do NOT silently continue.

## Step 10 — Summary report

Print:
- Files created (count + list)
- Hooks installed (which transport)
- Verification results (7/7 or which failed)
- **Next steps for the user** (1-3 actionable items, e.g., "fill in {{...}} placeholders in AGENTS.md", "run cold-start test in 24h").

---

## What this skill INTENTIONALLY does NOT do (v0.1)

- ❌ No drift detection between concepts/ and SKILL.md (v0.2 — eval skill)
- ❌ No automatic concepts/ → AGENTS.md numerical extraction (200 is hard-coded; this is fine for v0.1)
- ❌ No failures→规约 升级机制 (v0.3 — update skill)
- ❌ No GC of zombie regulations (v0.3)
- ❌ No SpecKit/OpenSpec scaffolding (orthogonal — opt-in via `harness/development.md`)
- ❌ No cross-project template sync (v0.3+, after dogfooding 3+ projects)

These are deliberate omissions — see Carmack's裁决 in roundtable 7: "no real data → no design".

## Roundtable provenance

This skill emerged from 8 rounds of structured discussion (Linus / Knuth / Reinertsen / Dijkstra / Hickey / Meadows / Carmack), recorded in:
- `~/Documents/notes/20260602T120207--*.org`
- `~/Documents/notes/20260602T164525--*.org`

Concept atoms are in `~/Code/Ai-driven-dev/concepts/`. Index at `HARNESS-NOTES.md`.

## Reference layout

```
td-harness-init/
├── SKILL.md                          ← this file (skill entry)
├── references/
│   ├── concepts/                     ← 7 spec atoms (don't modify here; modify in source repo)
│   ├── templates/
│   │   ├── AGENTS.md.tmpl
│   │   ├── PROGRESS.md.tmpl
│   │   ├── DECISIONS.md.tmpl
│   │   ├── lefthook.yml.tmpl
│   │   ├── harness/
│   │   │   ├── coding-style.md
│   │   │   ├── glossary.md
│   │   │   ├── failures.md
│   │   │   ├── testing.md
│   │   │   └── development.md
│   │   └── .pge/spec.md.tmpl
│   └── hooks/
│       ├── install_hooks.sh          ← orchestrator
│       ├── pre_commit_check.sh
│       ├── pre_push_check.sh
│       ├── check_razor_block.sh
│       ├── check_wip.sh
│       ├── check_test_guard.sh
│       └── check_commit_msg.sh
└── assets/                           ← (empty for now — diagrams etc. to come)
```
