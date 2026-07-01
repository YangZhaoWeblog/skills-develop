---
name: harness-init
description: Generate a project-specific AI agent harness baseline. Use when a user asks to initialize, create, scaffold, bootstrap, or rebuild AGENTS.md and harness/*.md for a new or existing repository, especially when they want a concise workflow, gates, governance, and project-grown rule structure.
---

# Harness Init

Use this skill to create an evolvable project harness: a short `AGENTS.md` entry, a `harness/` rule set, and lightweight PGE agent/templates for code projects, with clear ownership, active/stub status, and a universal/profile/project-grown layer split.

## Workflow

1. **Scan**
   Inspect the repository before writing:
   - README / docs
   - existing `AGENTS.md`, `.agents/`, `.codex/`, `harness/`
   - build files, package/module files, Makefile/scripts
   - tests, API files, migrations, deployment files

2. **Draft profile**
   Produce a concise project profile using [templates/project-profile.md](templates/project-profile.md). Do not guess unknown facts; mark them `unknown`.

3. **Confirm**
   Show four blocks and ask at most 5 high-leverage questions:
   - Project Profile
   - Planned Files
   - Active / Stub Decisions
   - Open Questions

4. **Generate**
   - If no `AGENTS.md` or `harness/` exists, create the baseline from [assets/baseline](assets/baseline).
   - For code projects, copy the full baseline including `.codex/agents/` and `docs/pge/`.
   - For non-code projects, keep PGE only as explicit stubs; do not omit the PGE files and then patch references piecemeal.
   - If an existing harness exists, do not overwrite by default. Generate an adoption plan from [templates/init-plan.md](templates/init-plan.md).
   - Only overwrite existing harness files when the user explicitly asks for overwrite.

5. **Summarize**
   Finish with changed files, assumptions, TODOs, and the next suggested `harness-score` run. Use [templates/init-summary.md](templates/init-summary.md).

## Baseline Rules

- Keep `AGENTS.md` short: identity, stack, commands, hard rules, task routing, workflow, index.
- Generate all baseline harness files, but mark each as `active` or `stub`.
- For code projects, generate PGE support as a first-class baseline: `harness/pge-protocol.md`, `.codex/agents/pge-generator.toml`, `.codex/agents/pge-evaluator.toml`, `docs/pge/spec.template.md`, and `docs/pge/eval.template.md`.
- PGE is not only a document. It must define Generator and Evaluator roles, TDD tracer bullet expectations, independent evaluation, fallback, and the files used for handoff.
- PGE files being present does not mean every task uses PGE. Small local changes may remain solo under `harness/pge-protocol.md`.
- Every harness file starts with:

```md
> status: active | stub
> owner: <rule-domain>
> layer: universal | profile | project-grown
> 本文件负责 <scope>；不负责 <boundary>。
```

- Use `universal` for cross-project execution and governance rules.
- Use `profile` for files activated by project type, stack, API, DB, deployment, or large-workflow needs.
- Use `project-grown` only for rules that emerged from this project after real feedback.
- Stub files are not empty. Keep them short: purpose, activation condition, and 3-5 TODOs.

## Default Active / Stub

Default active:
- `AGENTS.md`
- `harness/development.md`
- `harness/workflow-gates.md`
- `harness/instruction-governance.md`
- `harness/testing.md`
- `harness/code-review.md`
- `harness/failures.md`
- `harness/glossary.md`

Active for code projects:
- `harness/coding-style.md`

Activate by profile, otherwise keep stub:
- `harness/pge-protocol.md`
- `harness/api-standards.md`
- `harness/database.md`
- `harness/dependency-map.md`
- `harness/deployment.md`

Active for code-project PGE baseline:
- `.codex/agents/pge-generator.toml`
- `.codex/agents/pge-evaluator.toml`
- `docs/pge/spec.template.md`
- `docs/pge/eval.template.md`

## Writing Style

- Prefer the concise style of `AGENTS.md`: short sections, direct rules, action-first wording.
- Avoid long explanations, decorative tables, and generic slogans.
- Put background and incidents in `failures.md`; keep execution files operational.
- Do not invent project-specific commands, APIs, deployment systems, or protected branches. Use TODOs when unknown.
