---
name: harness-init
description: Generate a project-specific AI agent harness baseline for a code repository. Use when a user asks to initialize, create, scaffold, bootstrap, or rebuild AGENTS.md and harness/*.md for a new or existing codebase, especially when they want a concise workflow, gates, governance, and project-grown rule structure.
---

# Harness Init

Use this skill to create an evolvable code-project harness: a short `AGENTS.md` entry, a `harness/` rule set, active PGE v2 support, and a complete Grill skill dependency closure, with clear ownership, active/stub status, and a universal/profile/project-grown layer split.

## Workflow

1. **Scan**
   Inspect the repository before writing:
   - README / docs
   - existing `AGENTS.md`, `.agents/`, `.codex/`, `harness/`
   - build files, package/module files, Makefile/scripts
   - tests, API files, migrations, deployment files
   - evidence that the target is a code repository

   If the target is not a code repository, report that this baseline does not support it and stop before generation. Do not generate a misleading non-code PGE stub.

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
   - Copy the full code-project baseline including `.agents/skills/{pge-workflow,grill-me,grill-with-docs,grilling,domain-modeling}/`, `.codex/agents/`, `docs/pge/`, `harness/hooks-governance.md`, and `scripts/check_pge_contracts.sh`.
   - The Grill directories are the pinned offline snapshot documented in [references/grill-skills.lock.md](references/grill-skills.lock.md). Copy them from the baseline assets; never fetch upstream `main` during target generation.
   - Do not write `.git/hooks/*` directly. Tell the user the PGE checker is available and can be connected to pre-commit, Make, or CI.
   - If an existing harness exists, do not overwrite by default. Generate an adoption plan from [templates/init-plan.md](templates/init-plan.md).
   - Only overwrite existing harness files when the user explicitly asks for overwrite.

5. **Verify**
   - Confirm all generated files named by the active baseline exist.
   - Confirm both Grill wrappers, both model-invoked primitives, every `agents/openai.yaml`, both domain-modeling format files, and their `LICENSE` / `NOTICE` files were copied.
   - Run `scripts/check_pge_contracts.sh` against the generated spec and eval templates.
   - Confirm generated PGE policy keeps Grill Closure separate from current-revision Human Start and does not route the model through user-only wrappers.

6. **Summarize**
   Finish with changed files, assumptions, TODOs, and the next suggested `harness-score` run. Use [templates/init-summary.md](templates/init-summary.md).

## Baseline Rules

- Keep `AGENTS.md` short: identity, stack, commands, hard rules, task routing, workflow, index.
- Generate all baseline harness files, but mark each as `active` or `stub`.
- For code projects, generate PGE support as a first-class baseline: `harness/pge-protocol.md`, `.agents/skills/pge-workflow/SKILL.md`, `.codex/agents/pge-generator.toml`, `.codex/agents/pge-evaluator.toml`, `docs/pge/spec.template.md`, `docs/pge/eval.template.md`, and `scripts/check_pge_contracts.sh`.
- Generate the complete Grill closure: user-only `grill-me` and `grill-with-docs`, model-invoked `grilling` and `domain-modeling`, their metadata/resources, and MIT provenance. PGE internally routes to primitives, never to user-only wrappers.
- The PGE checker is a provided capability, not an enabled hook. The target repository decides whether to connect it to pre-commit, Make, or CI.
- PGE is not only a document. It must define Grill Closure, Challenge, a revision-bound Human Start Gate, Generator and Evaluator roles, TDD tracer bullet expectations, independent evaluation, fallback, parallel dispatch, and the files used for handoff.
- Grill confirmation, Contract lock, and fallback never authorize implementation. Production code, tests, migrations, generated files, implementation workspaces, and code-writing Agents require explicit Human Start approval for the current Contract revision.
- The final PGE Evaluator is also the independent AI code-review gate. Do not add a duplicate reviewer after normal PGE evaluation. During fallback, allow only clearly labeled supplemental review that does not claim Evaluator assurance.
- PGE fallback must name lost guarantees and enforce state-dependent close: available Evaluator assurance requires its accepted conclusion; missing assurance requires completed main-agent self-review; required owner acknowledgement must be confirmed. Human PR review remains separate when the target repository requires it.
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
- `harness/hooks-governance.md`
- `harness/testing.md`
- `harness/code-review.md`
- `harness/pge-protocol.md`
- `harness/failures.md`
- `harness/glossary.md`

Active for code projects:
- `harness/coding-style.md`

Activate by profile, otherwise keep stub:
- `harness/api-standards.md`
- `harness/database.md`
- `harness/dependency-map.md`
- `harness/deployment.md`

Active for code-project PGE baseline:
- `.agents/skills/pge-workflow/SKILL.md`
- `.agents/skills/grill-me/SKILL.md`
- `.agents/skills/grill-with-docs/SKILL.md`
- `.agents/skills/grilling/SKILL.md`
- `.agents/skills/domain-modeling/SKILL.md`
- `.codex/agents/pge-generator.toml`
- `.codex/agents/pge-evaluator.toml`
- `docs/pge/spec.template.md`
- `docs/pge/eval.template.md`
- `scripts/check_pge_contracts.sh`

## Writing Style

- Prefer the concise style of `AGENTS.md`: short sections, direct rules, action-first wording.
- Avoid long explanations, decorative tables, and generic slogans.
- Put background and incidents in `failures.md`; keep execution files operational.
- Do not invent project-specific commands, APIs, deployment systems, or protected branches. Use TODOs when unknown.
