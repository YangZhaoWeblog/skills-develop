# Dependency Map

> status: stub
> owner: dependency-map
> layer: profile
> This file owns upstream/downstream and module-boundary rules; it does not own deployment.

## Activation

Activate when the project calls external services, handles events, has cron jobs, or has important internal module boundaries.

## Core Rules

- List upstream callers and downstream dependencies.
- Keep external dependencies injected or isolated by project convention.
- Document failure modes and degradation behavior.
- Keep event and scheduled workflows idempotent.

## Project Growth TODO

- [ ] List upstream callers.
- [ ] List downstream services.
- [ ] Define timeout/retry/fallback rules.
