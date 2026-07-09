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
| Planner | Freeze goal, scope, acceptance, non-goals, order, first tracer bullet, fallback | `docs/pge/<sprint>-spec.md` or task-local contract |
| Generator | Implement only the locked contract with TDD tracer bullets | code, tests, `verify_cmd`, contract/status update |
| Evaluator | Independently challenge contract and validate diff | `PASS`, `PASS_WITH_NOTES`, or `FAIL` with findings |

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

Default templates:

- `docs/pge/spec.template.md`
- `docs/pge/eval.template.md`

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

Artifact existence and spec/eval pairing can be checked explicitly with `scripts/check_pge_artifacts.sh`. Prefer Makefile targets named `check-pge`, `check-pge-required`, and `check-pge-design-required` when the repository has a Makefile. Do not attach this check to pre-commit by default; small tasks and in-progress contracts may validly lack PGE close-out artifacts.

## Generator Protocol

- Start only after the contract is locked or after an Implementation Probe is requested.
- In pre-contract mode, do not edit production code or tests; output only the first tracer bullet, smallest implementation cut, required fake/mock, and expected verify command.
- For behavior work, use TDD tracer bullets:
  - RED: write or identify one failing test and confirm the failure reason;
  - GREEN: implement the minimum code for that behavior;
  - REFACTOR: clean only after green.
- Do not write all tests first and all implementation later.
- Do not relax existing assertions, delete tests, or change acceptance criteria to pass.
- Keep changes inside the contract; return to Planner if scope expands.

## Evaluator Protocol

Evaluator is independent from implementation and does not edit files.

Check in this order:

1. contract compliance;
2. tests not weakened;
3. TDD tracer bullet evidence where required;
4. user-data / API / migration safety;
5. code quality, minimality, and local style;
6. manual verification gaps and residual risks.

Return exactly one conclusion:

- `PASS`: contract met, no blocker;
- `PASS_WITH_NOTES`: acceptable with explicit residual risk;
- `FAIL`: blocker, key contract miss, weakened tests, or unsafe scope drift.

## Fallback

When independent Generator or Evaluator is unavailable, write:

```json
{
  "pge_fallback": {
    "enabled": true,
    "reason": "runtime cannot spawn independent PGE agent",
    "roles_collapsed": ["generator"],
    "lost_guarantees": ["context isolation"],
    "mitigations": ["explicit contract", "independent reviewer after implementation"],
    "restore_condition": "runtime exposes independent PGE agents or user authorizes subagents",
    "owner_ack_required": false
  }
}
```

Allowed: fallback with explicit lost guarantees. Forbidden: silent solo.

## Circuit Breaker

If the same interface or flow fails 3 rounds of tests, reference alignment, or evaluator review:

1. stop implementation;
2. record the mismatch and recovery condition;
3. return to Planner / user clarification;
4. add a failure note when it is a reusable pitfall.
