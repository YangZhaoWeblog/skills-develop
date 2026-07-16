# Harness Init Design Notes

## Purpose

`harness-init` creates a seed harness for a code repository, not a finished institutional rulebook.

## Core Decisions

- Generate a short `AGENTS.md` plus focused `harness/*.md` files.
- Generate all baseline files, but distinguish `active` and `stub`.
- Use `layer: universal | profile | project-grown` to separate common rules from project-specific growth.
- Existing harness files are not overwritten by default.
- Unknown project facts become TODOs, not invented rules.
- An active PGE profile includes its full control path: Grill Closure, Challenge, Contract lock, revision-bound Human Start, Generator, and Evaluator.
- The offline Grill bundle is dependency-complete. User-only wrappers remain entrypoints; PGE invokes the model-available primitives.

## Product-Service Influence

The baseline is abstracted from a mature backend-service harness:

- short entrypoint
- main workflow with topic subflows
- workflow gates
- circuit breaker
- instruction governance
- failures as institutional memory
- score-friendly ownership and file boundaries

Project-specific details such as concrete service names, Go-only rules, DAO conventions, and product-domain terms are intentionally removed or placed behind profile activation.

The baseline does not claim non-code repository support. A future non-code profile needs its own assets and acceptance evidence instead of partial stubs copied from the code workflow.
