# Harness Init Decision Log

## v1

- Use two skills: `harness-init` for generation and `harness-score` for evaluation.
- Do not automate harvest or inject. People and the main agent improve skills after discussion.
- Use `scan -> confirm -> generate`.
- Ask at most 5 high-leverage questions.
- Existing `AGENTS.md` or `harness/` triggers adoption-plan mode, not overwrite mode.
- Generate complete framework files, but use `active` / `stub`.
- Preserve universal/profile/project-grown layer distinction.
- Keep writing concise and action-first.

## v2 — Scope Discipline and PGE Ownership

- Keep the baseline self-contained: its Red / Green / Refactor rules do not depend on a separately installed TDD skill.
- Require an explicit refactor check after GREEN, but allow no code change when there is no concrete current-change or goal-blocking issue.
- Lock the Contract's behavior boundary, not candidate helpers, Guards, interfaces, or function shapes; allow execution-projection refinement inside that boundary.
- Keep Planner as the design/spec writer, Generator as the code/test/evidence writer, and Evaluator as the eval writer. After Generator handoff, allow the main agent to fix integration conflicts or make necessary corrections only when the patch is disclosed and evaluated.
- Require Generator to return newly discovered boundaries or required properties to Planner; a property enters the boundary only through explicit acceptance or a cited project hard rule.
- Review confirmed facts, goal, scope, non-goals, and diff necessity before implementation detail; production behavior outside the boundary fails evaluation.
- Judge abstractions and defensive code by evidence and independent value, never by caller or implementation count alone.
- Require state and concurrency behavior to name the actual object, transition, and relevant ordering basis from the call site using the smallest necessary combination of names, branches, and comments.
- Add no new Gate, Contract field, or project-specific business rule for these decisions.

## v3 — Complete Code Baseline And Human Start

- Support code repositories only until a separately accepted non-code profile exists.
- Treat Human Start as part of every active PGE baseline, not as product-specific growth. Contract lock, Grill confirmation, and fallback cannot substitute for current-revision approval.
- Keep Grill Closure and Human Start as separate user confirmations: the first confirms shared understanding; the second authorizes implementation.
- Install `grilling` and `domain-modeling` directly from `mattpocock/skills`; do not vendor or fork upstream skill code.
- Do not install the legacy `grill-me` / `grill-with-docs` wrappers. PGE uses `grilling` and adds `domain-modeling` only for explicitly authorized planning-document work.

## v4 — Validator Foundation

- Make source-owned capability validation authoritative; never use a staged repository's checker to establish final success.
- Freeze revision-bound Human Start, canonical PGE control flow, inherited PGE Agent models, and the four-Skill Grill toolchain as machine-checked capabilities.
- Keep the canonical Mermaid control-flow diagram only in `harness/pge-protocol.md`.
- Supersede v3's wrapper decision: require `grilling`, `domain-modeling`, `grill-me`, and `grill-with-docs`; keep both wrappers as exact one-hop delegations.
- Keep PGE Agent model selection inherited by forbidding a top-level `model` key.
- Future `harness-build` work will replace the current init/adoption behavior with a strong rebuild control plane while preserving project knowledge; this validator Sprint does not change the existing init workflow.

## v5 — Managed Path Symlink Boundary

- Reject any symlinked ancestor of a Builder-managed path, plus symlinks at direct-write paths such as `skills-lock.json`, before staging or apply.
- Require exclusive access to target, overlay, and explicit staging paths; concurrent external mutation is outside the rollback guarantee.
- Recheck the copied staging tree before overlay and the target before each managed apply write as defense in depth.
- Preserve unrelated symlinks and managed leaf symlinks under the existing ownership rules.
- Treat preview writes outside staging as a blocking safety failure because rollback cannot restore external paths.
