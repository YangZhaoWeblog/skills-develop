# PGE Protocol

> status: active
> owner: large-work-protocol
> layer: profile
> This file owns Planner / Generator / Evaluator workflow; it does not replace the main workflow in `AGENTS.md`.

Use `$pge-workflow` as the PGE routing, Challenge Gate, fallback, and parallel-dispatch entrypoint. This file remains the policy source of truth.

## Activation

Use PGE by default for:

- medium / large tasks;
- critical user-data or public-interface behavior;
- multi-module changes;
- batch work, migrations, or repeated failure;
- work that needs independent validation to be trusted.

Small docs/config/single-module changes may stay solo, but still need scoped verification and review.

## Roles

| Role | Responsibility | Output |
|---|---|---|
| Planner | Define and adjudicate the behavior boundary and execution plan | `docs/pge/<sprint>-spec.md` or task-local contract |
| Generator | Choose the smallest implementation inside that boundary | code, tests, `verify_cmd`, implementation evidence |
| Evaluator | Independently challenge the contract and validate the diff | `docs/pge/<sprint>-eval.md`, `PASS`, `PASS_WITH_NOTES`, or `FAIL` |

```mermaid
flowchart LR
    U[User / discovery] --> P[Planner]
    P --> S[Design and spec draft]
    S --> GP[Generator probe]
    S --> EC[Evaluator challenge]
    GP --> P
    EC --> P
    P --> G[Generator: code, tests, evidence]
    G --> E[Evaluator: final evaluation]
    E -->|implementation defect| G
    E -->|boundary or contract defect| P
```

Planner is the single writer for design and spec documents; Evaluator is the single writer for the eval document. Generator writes its assigned code and tests and returns evidence. After Generator handoff, the main agent may fix an integration conflict or make a necessary correction; it must disclose the patch as an implementation change and include it in final verification and evaluation. Do not concurrently edit the same hot zone.

The final Evaluator is also the PGE task's independent AI code review: it checks contract compliance, code quality, tests, and residual risk. Do not dispatch a duplicate generic AI reviewer after normal PGE evaluation. During fallback, a generic AI reviewer may add clearly labeled supplemental findings, but cannot substitute for a missing Evaluator or restore its assurance. This AI gate does not replace human PR review when the repository requires it.

Project-level Codex agents live in:

- `.codex/agents/pge-generator.toml`
- `.codex/agents/pge-evaluator.toml`

If the runtime cannot spawn independent agents, record fallback. Do not silently collapse roles.

## Skill Relationship

- `.agents/skills/pge-workflow/SKILL.md` owns trigger discipline, Challenge Gate coordination, fallback status shape, parallel-dispatch orchestration, and handoff prompts.
- This file owns the PGE policy, role boundaries, contract requirements, fallback rules, and circuit breaker.
- Project-level agents own execution and evaluation only when the runtime explicitly dispatches them.

## Sprint Contract

Each PGE task must define:

1. goal;
2. scope;
3. acceptance criteria;
4. non-goals;
5. implementation order;
6. first tracer bullet: the first failing test or smallest observable verification cut;
7. fallback and restore condition when independent agents are unavailable.

Goal, scope, acceptance criteria, and non-goals lock the behavior boundary. A required property belongs to that boundary only when acceptance states it explicitly or a cited project hard rule requires it. Implementation order, tracer bullets, and `verify_cmd` are an execution projection that Planner may refine and write back to the current contract inside that boundary. The contract does not lock candidate helpers, Guards, function names, or other implementation shapes. A change to the behavior boundary returns to Planner for adjudication; an implementation-only simplification does not rewrite the contract.

Default templates:

- `docs/pge/spec.template.md`
- `docs/pge/eval.template.md`

When `scripts/check_pge_contracts.sh` exists, check the active spec before Challenge Gate and the eval draft before Evaluator acceptance. The script checks structure only; requirement quality, semantic drift, and acceptance sufficiency remain Challenge Gate / Evaluator responsibilities.

## Design / PGE Relationship

- `docs/design/*.md` is the long-lived map for cross-sprint background, route, boundaries, and hard decisions.
- `docs/pge/*-spec.md` is the per-sprint execution contract for goal, scope, acceptance, non-goals, order, and RED plan.
- `docs/pge/*-eval.md` is the per-sprint acceptance report for contract completion, verification commands, and residual risks.
- Create design first for large, cross-sprint, architectural, state-machine, or domain-boundary changes.
- Create a PGE spec for medium+, batch, single public-interface, or critical-flow work.
- One design may produce multiple independently acceptable PGE specs; design does not replace the PGE spec.

## Parallel PGE

Multiple PGE specs under the same design may run in parallel only when the locked contract records slice boundaries, file boundaries, and independently decidable acceptance criteria.

Allowed:

- read-only research, Contract Challenge, and Evaluator checks;
- non-overlapping public-interface, package, or documentation slices;
- implementation slices that do not share generated files, migrations, protocol files, state machines, or shared helper hot zones.

Forbidden:

- same public interface, state machine, migration, or protocol file;
- competing edits to the same file hot zone or shared helper;
- unlocked contracts or acceptance that cannot be decided independently.

The main agent owns the design map, slice list, dispatch prompts, diff integration, conflict resolution, final `verify_cmd`, and Evaluator handoff.

The baseline provides `scripts/check_pge_contracts.sh` as a structure checker. Hook, Make, or CI enablement remains a target-repository decision; do not write `.git/hooks/*` directly.

## Generator Protocol

- Start only after the contract is locked or after an Implementation Probe is requested.
- In pre-contract mode, do not edit production code or tests; output only the first tracer bullet, smallest implementation cut, required fake/mock, and expected verify command.
- Treat confirmed facts and cited security, authorization, and consistency hard rules as constraints on the contract, not lower-priority implementation preferences.
- If implementation reveals a new behavior boundary or required property, stop and return the evidence to Planner; do not silently expand the contract or tests.
- For behavior work, use TDD tracer bullets:
  - RED: write or identify one failing test and confirm the failure reason;
  - GREEN: implement the minimum code for that behavior;
  - REFACTOR: after the relevant verification is green, explicitly check for a concrete issue; no change is valid when none exists, and any refactor must preserve behavior and stay within the current change or goal.
- Do not write all tests first and all implementation later.
- Do not relax existing assertions, delete tests, or change acceptance criteria to pass.
- Keep changes inside the contract; return to Planner if scope expands.
- Do not add adjacent behavior for cleanliness, safety, or possible future needs without evidence inside the locked boundary.

## Evaluator Protocol

Evaluator is independent from implementation. It writes only the assigned eval report and does not edit production code or tests.

Apply `harness/code-review.md` during final evaluation and include a separate code-quality conclusion. Any critical code-review finding requires `FAIL`.

Check in this order:

1. confirmed facts, goal, scope, non-goals, and diff necessity;
2. production behavior stayed inside the locked boundary;
3. contract compliance and tests not weakened;
4. TDD tracer bullet evidence where required;
5. user-data / API / migration safety;
6. code quality, minimality, and local style;
7. manual verification gaps and residual risks.

Any production behavior change outside the locked boundary requires `FAIL`. Judge helpers and interfaces by independent behavior or clarity value, not caller or implementation count alone. For state or concurrency code, review the call site for a clear object, state transition, and relevant ordering basis using the smallest necessary combination of names, branches, and comments.

Return exactly one conclusion:

- `PASS`: contract met, no blocker;
- `PASS_WITH_NOTES`: acceptable only after the owner explicitly accepts the residual risk;
- `FAIL`: blocker, key contract miss, weakened tests, or unsafe scope drift.

## Fallback

When independent Generator or Evaluator is unavailable, write:

```json
{
  "pge_fallback": {
    "enabled": true,
    "reason": "runtime cannot spawn independent PGE agent",
    "roles_collapsed": ["generator", "evaluator"],
    "lost_guarantees": ["context isolation", "implementation and acceptance perspective split"],
    "mitigations": ["declared main-agent checklist self-review", "human confirmation for critical acceptance", "record that independent Evaluator assurance is missing"],
    "restore_condition": "runtime exposes independent PGE agents or user authorizes subagents",
    "main_agent_self_review": "pending",
    "owner_ack_required": false,
    "owner_ack_status": "not_required",
    "independent_evaluator_assurance": "missing"
  }
}
```

Use `not_required | pending | complete` for `main_agent_self_review`, `not_required | pending | confirmed` for `owner_ack_status`, and `available | missing` for `independent_evaluator_assurance`. Before close, update pending statuses.

The example shows both roles unavailable. List only roles and guarantees actually lost. If only Generator is unavailable, preserve the independent Evaluator and mark its assurance `available`. If Evaluator is unavailable, mark its assurance `missing`; supplemental generic review must stay labeled as non-Evaluator evidence.

Close fallback by state:

- `independent_evaluator_assurance: available` requires Evaluator `PASS` or owner-accepted `PASS_WITH_NOTES`; `FAIL` blocks close.
- `independent_evaluator_assurance: missing` requires `main_agent_self_review: complete`.
- `owner_ack_required: true` requires `owner_ack_status: confirmed`; otherwise use `not_required`.

Allowed: fallback with explicit lost guarantees. Forbidden: silent solo.

## Circuit Breaker

If the same interface or flow fails 3 rounds of tests, reference alignment, or evaluator review:

1. stop implementation;
2. record the mismatch and recovery condition;
3. return to Planner / user clarification;
4. add a failure note when it is a reusable pitfall.
