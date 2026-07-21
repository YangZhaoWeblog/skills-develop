# Hooks Governance

> status: active
> owner: hook-governance
> layer: universal
> This file owns hook boundaries and enablement guidance; it does not own PGE, testing, review, or commit rules.

## Principles

- Hooks only run machine-decidable, low-cost, low-false-positive checks.
- Semantic judgment belongs to Challenge Gate, Evaluator, or review.
- Git hooks guard commit boundaries; workflow commands guard start boundaries; Codex hooks are enabled only when inputs are stable and no AI judgment is required.

## Not Enabled By Default

- `.git/hooks/pre-commit`: local machine state, not a repository rule source.
- Codex CSC hook: only enable after stable, no-AI transcript/context input is confirmed.
- Stop hook: high frequency and no precise default matcher.
- Spec or Harness drift hook: semantic drift belongs to Planner/Evaluator and human review.

Do not add a Harness-specific hook or checker. Reuse an existing repository hook only for checks the repository already owns.
