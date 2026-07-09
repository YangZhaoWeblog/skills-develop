---
name: pge-workflow
description: Coordinate this repository's PGE flow by identifying when to use Sprint Contract, Challenge Gate, pge-generator, and pge-evaluator. Use when work mentions PGE, Generator, Evaluator, Batch, single RPC, key flow, independent acceptance, or Sprint Contract.
---

# PGE Workflow

Use this skill to orchestrate PGE. It does not create independence by itself; independence comes from explicitly spawning project agents.

## Quick Start

1. Read `AGENTS.md` and `harness/pge-protocol.md`.
2. Decide whether the task needs PGE:
   - single RPC or key business flow
   - medium or larger task
   - Batch or cross-module work
   - independent acceptance needed
3. If PGE is needed, confirm user grill has happened or route back to grill.
4. Run Challenge Gate before locking the Contract.
5. Use `pge-generator` for implementation and `pge-evaluator` for challenge or acceptance.

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

## Fallback

If project agents cannot be spawned, record fallback JSON in the Sprint Contract or status document:

```json
{
  "pge_fallback": {
    "enabled": true,
    "reason": "当前环境无法显式分发 pge-generator / pge-evaluator",
    "roles_collapsed": ["generator", "evaluator"],
    "lost_guarantees": ["上下文隔离", "实现与验收视角分离"],
    "mitigations": ["额外独立 review", "人工确认关键验收"],
    "restore_condition": "Codex custom agents 可用并显式分发",
    "owner_ack_required": false
  }
}
```

## Rules

- Do not claim independent Generator or Evaluator ran unless the agents were explicitly used.
- Do not copy TDD rules here; `pge-generator` must use the repo `tdd` skill or `.agents/skills/tdd/SKILL.md`.
- Keep `harness/pge-protocol.md` as the PGE policy source of truth.
