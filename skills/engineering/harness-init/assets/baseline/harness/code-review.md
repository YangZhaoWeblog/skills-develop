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
- Use the final Evaluator as the PGE task's independent AI code review; do not add a duplicate generic AI reviewer after normal PGE evaluation.
- Apply state-dependent PGE fallback review: available Evaluator assurance still requires its accepted conclusion; missing assurance requires completed main-agent self-review; required owner acknowledgement must be confirmed. A generic AI reviewer may add clearly labeled supplemental findings, but must not be presented as the missing Evaluator or restore its assurance.
- Use an independent AI reviewer for non-PGE non-trivial changes; do not present author self-review as independent review.
- Keep human PR review separate when the repository requires it; AI review does not replace it.

## Reject Reasons

- Unverified behavior.
- Missing regression test for bug fix.
- Public API or schema change without owner documentation.
- Unrelated rewrite or formatting noise.
- Workflow gate or circuit breaker bypass.
- PGE Generator / Evaluator silently collapsed into one role on medium+ work.
- Generic AI review presented as independent PGE Evaluator acceptance.
- Commit or close attempted after Evaluator `FAIL`, or before owner acceptance of `PASS_WITH_NOTES`.
