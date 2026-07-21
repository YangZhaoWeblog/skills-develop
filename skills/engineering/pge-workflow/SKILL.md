---
name: pge-workflow
description: Coordinate medium-or-larger repository work through Grill, Sprint Contract, Challenge, Human Start, Generator, and Evaluator. Use for PGE, key flows, public interfaces, state/schema changes, batch work, or independent acceptance.
---

# PGE Workflow

`harness/pge-protocol.md` is the policy source. This Skill owns runtime routing and handoffs; it does not duplicate policy, TDD, coding style, or review rules.

## Route

1. Read `AGENTS.md`, the PGE protocol, relevant owner files, existing Contract, target code/tests, and related failures.
2. Decide whether PGE is required. Small work may stay solo only when repository gates allow it.
3. Use `$grilling`, adding `$domain-modeling` only when terminology, state, or ownership is genuinely unresolved.
4. Planner drafts the Sprint Contract and directly checks every required field and decision.
5. Dispatch Generator probe and Evaluator challenge without code writes.
6. Planner resolves findings, locks a Contract revision, and requests explicit Human Start.
7. After approval for the same revision, dispatch Generator in the approved branch/worktree.
8. Integrate into a clean candidate commit, classify untracked paths, run `verify_cmd`, then dispatch the independent Evaluator.
9. Close only under the protocol conclusion and owner-acceptance rules.

## Agent Context

Standalone `@path` lines are a Harness convention, not a native Codex include. Before dispatch, require the selected Agent to read every referenced file directly along with `AGENTS.md`, the locked Contract, and relevant owners. Do not duplicate those files inside the Agent prompt.

## Human Start

Ask after the Contract is locked and challenged. Record the exact user reply as evidence. A manual model handoff records repository, branch, HEAD, Contract path, revision, and pending gate; the new root model may update only matching gate metadata before dispatch.

## Dispatch Boundaries

- Announce role, purpose, context, read/write boundary, branch/worktree, Contract, and verification command.
- Generator writes approved code/tests only; Evaluator writes only the eval report.
- Parallelize only independently acceptable slices with disjoint hot zones.
- The main agent owns Contract changes, integration, conflict resolution, and final verification.
- If an Agent is unavailable, record the exact fallback state; do not silently collapse roles.

## Handoff

Report PGE requirement and reason, Contract/challenge/Human Start state, Agent availability, parallel decision, fallback, `verify_cmd`, conclusion, and next action. Never claim an Agent or assurance that did not run.
