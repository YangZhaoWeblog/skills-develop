# Code Review

> status: active
> owner: code-review
> layer: universal
> This file owns review standards; it does not own test implementation details.

## Required Focus

- Correctness and behavior changes.
- Compatibility and migration risk.
- Layering and ownership.
- Error handling and observability.
- Tests and verification evidence.

## Review Rules

- Findings first, ordered by severity.
- Reference files and lines.
- Distinguish blockers from notes.
- Do not use author self-review as a substitute for independent review on non-trivial changes.
- PGE tasks require independent Evaluator review before close; if unavailable, record fallback and residual risk.

## Reject Reasons

- Unverified behavior.
- Missing regression test for bug fix.
- Public API or schema change without owner documentation.
- Unrelated rewrite or formatting noise.
- Workflow gate or circuit breaker bypass.
- PGE Generator / Evaluator silently collapsed into one role on medium+ work.
