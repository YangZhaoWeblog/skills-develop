---
name: pge-workflow
description: Coordinate this repository's PGE flow by identifying when to use Sprint Contract, Challenge Gate, pge-generator, and pge-evaluator. Use when work mentions PGE, Generator, Evaluator, Batch, single RPC, key flow, independent acceptance, or Sprint Contract.
---

# PGE Workflow

Use this skill to route and orchestrate PGE work. It does not create independence by itself; independence comes from explicitly spawning project agents or runtime-supported subagents.

The project PGE policy source of truth is `harness/pge-protocol.md`. This skill owns trigger discipline, Challenge Gate coordination, fallback recording, and the status shape the main agent must report.

## Quick Start

1. Read `AGENTS.md`, `harness/pge-protocol.md`, and any existing PGE status/spec files named by the task.
2. Decide whether PGE is required.
3. If PGE is required, ensure the task has a Sprint Contract or produce the smallest contract draft.
4. If `scripts/check_pge_contracts.sh` exists, run it against the active spec before Challenge Gate.
5. Run Challenge Gate before locking the contract.
6. Decide whether the locked contract has independent slices that can be dispatched in parallel.
7. Route implementation to `pge-generator` and challenge or acceptance to `pge-evaluator` when those agents are actually available.
8. If independent agents are not available, record fallback before proceeding.

## Structure Check

When the repository provides `scripts/check_pge_contracts.sh`, use it as a machine-only structure check:

```bash
bash scripts/check_pge_contracts.sh docs/pge/<sprint>-spec.md
```

Before Evaluator acceptance starts, check the eval draft too:

```bash
bash scripts/check_pge_contracts.sh docs/pge/<sprint>-eval.md
```

The script only checks required sections and pairing. It does not judge requirement quality, semantic drift, or acceptance sufficiency; those remain Challenge Gate and Evaluator responsibilities.

## Activation

Use PGE by default for:

- medium or larger tasks
- Batch or repeated workflows
- single RPC or key business flow changes
- cross-module or protocol-affecting changes
- migrations or user-data safety risk
- work that needs independent acceptance to be trusted

Small docs, config, or local single-module changes may stay solo when `harness/pge-protocol.md` allows it, but they still need scoped verification and review.

## Challenge Gate

Input: Draft Sprint Contract from user grill and Planner.

Ask `pge-generator` for an Implementation Probe:

- first tracer bullet
- behavior verified by the first failing test
- smallest implementation cut
- required mock or fake
- expected verify command

Ask `pge-evaluator` for a Contract Challenge:

- whether acceptance criteria are testable
- missing positive or negative cases
- scope drift or hidden dependencies
- whether PASS/FAIL can be decided after implementation

The main agent summarizes the result. If there is no blocker, lock the Contract. If there is a blocker, return to user grill. Do not let Generator and Evaluator negotiate indefinitely.

## Parallel Dispatch

Policy lives in `harness/pge-protocol.md`; this skill owns orchestration.

The main agent decides parallel dispatch after the contract is locked:

- Use parallel dispatch only when the contract lists independently testable slices with clear file boundaries.
- Record the dispatch decision in the Sprint Contract or active status document.
- Dispatch one agent per independent slice.
- Give each agent a self-contained prompt: scope, goal, constraints, expected output, spec path, and verify command.
- Prefer one `git worktree` and branch per code-writing PGE slice.
- Keep read-only research, Contract Challenge, and Evaluator checks separate from code-writing slices.
- Do not dispatch parallel code-writing agents for the same RPC, state machine, migration, proto, generated files, or shared helper hot zone.

The main agent remains responsible for integration:

- collect all agent summaries and diffs
- check conflicts and scope drift
- run final `verify_cmd`
- update the active spec/status document
- hand the integrated diff to Evaluator

## Output Contract

When this skill is used, the main agent must report or record:

```json
{
  "pge_required": true,
  "reason": "medium+ task / single RPC / key flow / batch / cross-module / independent acceptance",
  "contract_status": "drafted | challenged | locked | returned_to_planner | not_required",
  "challenge_gate_result": "not_run | pass | blocked",
  "agent_usage": {
    "generator": "independent | unavailable | not_needed",
    "evaluator": "independent | unavailable | not_needed"
  },
  "parallel_dispatch": {
    "enabled": false,
    "reason": "not independent / no code-writing slices / worktree unavailable / enabled by locked contract",
    "slices": [
      {
        "name": "slice name",
        "spec_path": "docs/pge/<sprint>-spec.md",
        "worktree": "path or current workspace",
        "branch": "branch name",
        "scope": "owned files or behavior boundary",
        "verify_cmd": "slice-level command"
      }
    ]
  },
  "fallback": null,
  "verify_cmd": "command to run or expected command",
  "next_action": "lock_contract | grill | implement | evaluate | fallback_review"
}
```

Use `pge_required: false` only when the task is small enough to stay solo under the project protocol, and include the reason.

## Fallback

If either project agent cannot be spawned, record fallback JSON in the Sprint Contract or status document. Record only the roles and guarantees actually lost. The example below shows both roles unavailable:

```json
{
  "pge_fallback": {
    "enabled": true,
    "reason": "runtime cannot explicitly dispatch pge-generator / pge-evaluator",
    "roles_collapsed": ["generator", "evaluator"],
    "lost_guarantees": ["context isolation", "implementation and acceptance perspective split"],
    "mitigations": ["declared main-agent checklist self-review", "human confirmation for critical acceptance", "record that independent Evaluator assurance is missing"],
    "restore_condition": "runtime supports explicit custom agent dispatch",
    "main_agent_self_review": "pending",
    "owner_ack_required": false,
    "owner_ack_status": "not_required",
    "independent_evaluator_assurance": "missing"
  }
}
```

Use `not_required | pending | complete` for `main_agent_self_review`, `not_required | pending | confirmed` for `owner_ack_status`, and `available | missing` for `independent_evaluator_assurance`. Before close, update pending statuses. When only Generator is unavailable, preserve the independent Evaluator and its assurance.

Close fallback by state: `available` Evaluator assurance still requires `PASS` or owner-accepted `PASS_WITH_NOTES`; `missing` assurance requires `main_agent_self_review: complete`; and `owner_ack_required: true` requires `owner_ack_status: confirmed`.

## Rules

- Do not claim independent Generator or Evaluator ran unless the agents were explicitly used.
- The final PGE Evaluator also satisfies the independent AI code-review gate. Do not additionally dispatch a generic AI reviewer after normal PGE evaluation.
- During PGE fallback, a generic AI reviewer may provide clearly labeled supplemental findings, but must not substitute for a missing Evaluator or restore independent Evaluator assurance.
- Evaluator `FAIL` blocks commit and close. `PASS_WITH_NOTES` closes only after the owner explicitly accepts the residual risk.
- PGE AI review does not replace human PR review when the repository requires it.
- Do not copy the full PGE policy here; `harness/pge-protocol.md` remains the policy source of truth.
- Do not copy full testing or TDD rules here; Generator must follow the project's testing and TDD rules.
- Do not edit production code before the contract is locked, except for explicitly scoped probes allowed by `harness/pge-protocol.md`.
- Do not let dispatched agents negotiate scope with each other; the main agent owns dispatch, integration, and final handoff.
- Keep `harness/pge-protocol.md` as the PGE policy source of truth.
