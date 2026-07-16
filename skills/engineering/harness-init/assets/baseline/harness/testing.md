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

For PGE tasks, TDD is owned by the Generator:

- one behavior test or tracer bullet at a time;
- confirm RED before implementation when an automated test is possible;
- after the relevant verification is green, explicitly check whether refactoring is needed; make no refactor when there is no concrete issue;
- refactor only problems introduced by the current change or directly blocking the current goal, and preserve external behavior;
- do not edit adjacent existing problems; report them separately only when they create a material residual risk;
- if no automated test is feasible, record why and use the smallest manual verification cut;
- Evaluator must check that tests were not weakened.

## Verification Selection

- Docs only: whitespace/diff checks.
- Single package/module: targeted test.
- Shared logic: affected packages.
- API/DB/codegen: generation plus relevant tests.

## Project Growth TODO

- [ ] Define coverage expectations.
- [ ] Define integration test command.
- [ ] Define test data and fake/mock strategy.
