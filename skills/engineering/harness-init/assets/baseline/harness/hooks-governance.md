# Hooks Governance

> status: active
> owner: hook-governance
> layer: universal
> This file owns hook boundaries and enablement guidance; it does not own PGE, testing, review, or commit rules.

## Principles

- Hooks only run machine-decidable, low-cost, low-false-positive checks.
- Semantic judgment belongs to Challenge Gate, Evaluator, or review.
- Git hooks guard commit boundaries; workflow commands guard start boundaries; Codex hooks are enabled only when inputs are stable and no AI judgment is required.

## Baseline Capability

- PGE document structure: `scripts/check_pge_contracts.sh`.
- Suggested commit guard: call the checker from an existing pre-commit script for staged `docs/pge/*.md`.
- Suggested PGE start guard: `$pge-workflow` runs the checker before Challenge Gate when the script exists.

## Not Enabled By Default

- `.git/hooks/pre-commit`: local machine state, not a repository rule source.
- Codex CSC hook: only enable after stable, no-AI transcript/context input is confirmed.
- Stop hook: high frequency and no precise default matcher.
- Spec drift hook: semantic drift belongs to Evaluator.

When initializing a repository, tell the user the checker is available and can be connected to pre-commit, Make, or CI.
