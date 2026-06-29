# Harness Init Design Notes

## Purpose

`harness-init` creates a seed harness, not a finished institutional rulebook.

## Core Decisions

- Generate a short `AGENTS.md` plus focused `harness/*.md` files.
- Generate all baseline files, but distinguish `active` and `stub`.
- Use `layer: universal | profile | project-grown` to separate common rules from project-specific growth.
- Existing harness files are not overwritten by default.
- Unknown project facts become TODOs, not invented rules.

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
