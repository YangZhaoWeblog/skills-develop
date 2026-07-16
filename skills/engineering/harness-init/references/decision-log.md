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
- Bundle a pinned, offline copy of `grill-me`, `grill-with-docs`, `grilling`, and `domain-modeling` from `mattpocock/skills@e9fcdf95b402d360f90f1db8d776d5dd450f9234`, with MIT license and provenance.
- Preserve upstream invocation boundaries: wrappers are user-only; PGE uses `grilling` and adds `domain-modeling` only for explicitly authorized planning-document work.
- Keep installable skill directories as the canonical local snapshot and require baseline copies to remain byte-for-byte identical.
