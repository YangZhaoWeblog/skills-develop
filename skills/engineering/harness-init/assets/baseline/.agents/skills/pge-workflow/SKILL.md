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
4. Run Challenge Gate before locking the contract.
5. Route implementation to `pge-generator` and challenge or acceptance to `pge-evaluator` when those agents are actually available.
6. If independent agents are not available, record fallback before proceeding.

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
  "fallback": null,
  "verify_cmd": "command to run or expected command",
  "next_action": "lock_contract | grill | implement | evaluate | fallback_review"
}
```

Use `pge_required: false` only when the task is small enough to stay solo under the project protocol, and include the reason.

## Fallback

If project agents cannot be spawned, record fallback JSON in the Sprint Contract or status document:

```json
{
  "pge_fallback": {
    "enabled": true,
    "reason": "runtime cannot explicitly dispatch pge-generator / pge-evaluator",
    "roles_collapsed": ["generator", "evaluator"],
    "lost_guarantees": ["context isolation", "implementation and acceptance perspective split"],
    "mitigations": ["extra independent review", "human confirmation for critical acceptance"],
    "restore_condition": "runtime supports explicit custom agent dispatch",
    "owner_ack_required": false
  }
}
```

## Rules

- Do not claim independent Generator or Evaluator ran unless the agents were explicitly used.
- Do not copy the full PGE policy here; `harness/pge-protocol.md` remains the policy source of truth.
- Do not copy full testing or TDD rules here; Generator must follow the project's testing and TDD rules.
- Do not edit production code before the contract is locked, except for explicitly scoped probes allowed by `harness/pge-protocol.md`.
- Keep `harness/pge-protocol.md` as the PGE policy source of truth.
