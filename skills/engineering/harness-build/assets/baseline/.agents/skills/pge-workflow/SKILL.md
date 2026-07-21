---
name: pge-workflow
description: Coordinate this repository's PGE flow through Grill, Sprint Contract, Challenge Gate, Human Start Gate, pge-generator, and pge-evaluator. Use when work mentions PGE, Generator, Evaluator, Batch, single RPC, key flow, independent acceptance, or Sprint Contract.
---

# PGE Workflow

Use this skill to route and orchestrate PGE work. It does not create independence by itself; independence comes from explicitly spawning project agents or runtime-supported subagents.

The project PGE policy source of truth is `harness/pge-protocol.md`. This skill owns trigger discipline, Challenge Gate coordination, fallback recording, and the status shape the main agent must report.

## Quick Start

1. Read `AGENTS.md`, `harness/pge-protocol.md`, and any existing PGE status/spec files named by the task.
2. Decide whether PGE is required.
3. Announce and run the chosen Grill primitive, then record Grill Closure.
4. Produce the smallest Sprint Contract draft and run the repository structure check when available.
5. Announce the read-only Agent roles, then run Challenge Gate and lock the Contract.
6. Decide parallel boundaries, then mirror the locked Contract into a visible Implement Plan.
7. Pass Human Start Gate; only afterward create implementation workspaces or dispatch `pge-generator`.
8. Route acceptance to `pge-evaluator`; record fallback whenever an independent role is unavailable.

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

## Grill Routing

PGE uses the upstream skills directly:

- use `$grilling` for the default plan and risk interview;
- add `$domain-modeling` only when the user explicitly chooses a docs-bearing Grill and the allowed planning-document paths are recorded before the skill writes them;
- keep `$grill-me` and `$grill-with-docs` as installed compatibility entries, but do not route PGE through them.

Before the first question, tell the user which primitive is active and why. Investigate code-answerable facts directly, ask irreducible user decisions one at a time, and cover the branches required by `harness/pge-protocol.md`. Confirmation that Grill reached shared understanding completes Grill Closure only; it is not Human Start approval.

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
- scope drift, missing non-goals, or hidden dependencies
- candidate helpers, Guards, interfaces, or function shapes frozen without independent value
- whether PASS/FAIL can be decided after implementation

Before each dispatch, announce the Agent role, read-only purpose, supplied context, and write boundary. The main agent summarizes the result. If there is no blocker, lock the Contract. If there is a blocker, return it to Planner; only an irreducible user decision returns to Grill. Do not let Generator and Evaluator negotiate indefinitely.

## Required Agent Context

The `@path` lines in Agent TOML are a Harness convention, not a native Codex include. Before every Generator or Evaluator dispatch, create temporary output paths and run from the repository root:

```bash
python3 scripts/resolve_agent_context.py --agent .codex/agents/<role>.toml --repo-root "$PWD" --out <bundle.md> --receipt <receipt.json>
```

Record `receipt.json` and the context receipt SHA-256 printed by the command. Append the emitted bundle bytes exactly to the task, add the receipt digest as task metadata, and require the Agent to echo it in the handoff. A missing or mismatched echo blocks acceptance. Re-resolve after any Agent or referenced-context change; do not manually reproduce the referenced rules in the dispatch prompt.

## Human Start Gate

Follow `harness/pge-protocol.md`; this section maps the gate onto runtime tools.

1. Mirror Contract steps into a visible task list when available. Otherwise show a concise Implement Plan in the message.
2. Ask the start question with the runtime's structured user-input tool when available, offering “开始实现（推荐）” and “继续讨论” while preserving free-form input.
3. If no structured question tool is available, ask the same question directly. Do not switch modes merely to obtain a tool, set an auto-resolution timeout, or infer approval from silence.
4. Record the answer in the Contract's `human_start_gate`; only protocol v2 with `status = approved`, equal revisions, and non-empty channel/evidence permits Coding Start Check or code-writing dispatch.

For a manual root-model switch, stop with the locked Contract still pending and emit a handoff receipt containing repository, branch, HEAD, spec path, and revision. The owner's explicit start message to the new root model is the approval evidence. That model must verify the receipt, update only the matching gate metadata as Planner, run the trusted checker, and only then enter or dispatch Generator. A dispatched `pge-generator` never self-approves. Keep the gate-only change separate when the Contract requires a clean product commit.

The visible plan is a projection of the Contract, not a second artifact. Grill confirmation, Contract lock, fallback, and a prior revision's approval do not pass this gate. A scope-changing reply revokes approval and returns to Planner.

## Parallel Dispatch

Policy lives in `harness/pge-protocol.md`; this skill owns orchestration.

The main agent may design parallel dispatch after the Contract is locked, but may start code-writing slices only after Human Start Gate is valid for the current Contract revision:

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
  "pge_protocol_version": 2,
  "reason": "medium+ task / single RPC / key flow / batch / cross-module / independent acceptance",
  "grill": {
    "primitives_used": ["$grilling"],
    "closure_status": "pending | complete"
  },
  "contract_status": "drafted | challenged | locked | returned_to_planner | not_required",
  "challenge_gate_result": "not_run | pass | blocked",
  "contract_revision": 1,
  "human_start_gate": {
    "status": "pending | approved | revoked | not_required",
    "approved_contract_revision": null,
    "channel": "request_user_input | AskUserQuestion | direct_reply | not_required",
    "evidence": ""
  },
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
  "next_action": "grill | challenge | lock_contract | await_user_approval | implement | evaluate | fallback_review"
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
- A locked Contract is not implementation approval. Do not edit production code or tests, create code-writing worktrees, or dispatch code-writing Agents before Human Start Gate is valid for the current Contract revision.
- Grill Closure and Human Start are separate confirmations. Fallback never bypasses Human Start.
- Announce every Agent's role, purpose, supplied context, and read/write boundary before dispatch.
- Do not let dispatched agents negotiate scope with each other; the main agent owns dispatch, integration, and final handoff.
- Keep `harness/pge-protocol.md` as the PGE policy source of truth.
