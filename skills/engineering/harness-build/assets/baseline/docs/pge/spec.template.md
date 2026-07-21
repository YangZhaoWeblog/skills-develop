# Sprint Contract Template

> Fill according to `harness/pge-protocol.md`.
> Copy to `docs/pge/<sprint>-spec.md`; do not write sprint content in this template.

## Metadata

| Field | Value |
|---|---|
| Sprint | TBD |
| PGE protocol version | 2 |
| Goal | TBD |
| Branch | TBD |
| Review base commit | immutable full commit SHA; branch/tag may be recorded separately as a label |
| Review candidate commit | clean immutable full commit SHA; assigned before final evaluation |
| Planner | TBD |
| Generator | TBD |
| Evaluator | TBD |
| Parent design | None / `docs/design/<name>.md` |
| Status | TBD |

## PGE Fallback

```json
{
  "pge_fallback": {
    "enabled": false,
    "reason": "",
    "roles_collapsed": [],
    "lost_guarantees": [],
    "mitigations": [],
    "restore_condition": "",
    "main_agent_self_review": "not_required",
    "owner_ack_required": false,
    "owner_ack_status": "not_required",
    "independent_evaluator_assurance": "available"
  }
}
```

## Design / PGE Relationship

- Parent design: None / `docs/design/<name>.md`
- Sibling PGE specs: None / `docs/pge/<other>-spec.md`
- Independently acceptable: yes / no, reason TBD

## Grill Closure

- Primitives used: `$grilling` / `$grilling` + `$domain-modeling`
- User decisions: TBD
- Repository-confirmed facts: TBD
- Assumptions: TBD
- Residual risks: TBD
- Recommendation: TBD
- Pre-Human planning-document writes: none / exact authorized paths

## Parallel Dispatch

```json
{
  "parallel_dispatch": {
    "enabled": false,
    "reason": "",
    "slices": [
      {
        "name": "",
        "spec_path": "",
        "worktree": "",
        "branch": "",
        "scope": "",
        "verify_cmd": ""
      }
    ]
  }
}
```

## Goal

- TBD

## Scope

- TBD

## Acceptance Criteria

- TBD

## Non-Goals

- TBD

## Implementation Order

1. TBD
2. TBD
3. TBD

## Test / Verification Plan

- Change classification: behavior / non-behavior
- Approved behavior and test seams: TBD / not applicable
- First failing test or smallest targeted verification cut: TBD
- Behavior verified: TBD
- Required mock/fake/fixture: TBD
- Verify command: TBD

## Verification Commands

- `verify_cmd:` TBD

## Risks And Circuit Breaker

- Stop if: TBD
- Return to Planner when: TBD

## Human Start Gate

> Grill confirmation and Contract lock do not approve implementation. This block is execution metadata and may be updated after the behavior boundary is locked.

```json
{
  "contract_revision": 1,
  "human_start_gate": {
    "status": "pending",
    "approved_contract_revision": null,
    "channel": "",
    "evidence": ""
  }
}
```
