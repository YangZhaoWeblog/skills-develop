# Testing

> status: active
> owner: testing
> layer: universal
> This file owns test strategy and verification evidence; it does not own code review.

## Core Rules

- Add regression tests for bug fixes.
- Prefer focused tests near changed code.
- Use integration tests when behavior crosses process, DB, network, or service boundaries.
- Record `verify_cmd` for non-trivial changes.

## TDD

For risky behavior, start with a failing test or tracer bullet before broad implementation.

## Verification Selection

- Docs only: whitespace/diff checks.
- Single package/module: targeted test.
- Shared logic: affected packages.
- API/DB/codegen: generation plus relevant tests.

## Project Growth TODO

- [ ] Define coverage expectations.
- [ ] Define integration test command.
- [ ] Define test data and fake/mock strategy.
