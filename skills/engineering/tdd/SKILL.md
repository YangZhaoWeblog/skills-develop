---
name: tdd
description: Test-driven development with a red-green-refactor loop. Use when the user wants to build a feature or fix a bug test-first, mentions red-green-refactor, requests integration tests, or asks for incremental behavior-driven implementation.
---

# Test-Driven Development

## Philosophy

**Core principle**: Tests should verify observable behavior through the narrowest stable boundary appropriate to the change, not implementation details. Follow the project's test strategy when it defines package interfaces, fakes, or integration boundaries. Code can change entirely; tests shouldn't.

**Good tests** exercise a stable, project-approved behavior boundary. Use integration-style tests when several real components matter and focused unit tests when the project declares a dependency boundary. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They test private methods or mock collaborators only to assert internal calls rather than observable results. The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" - treating RED as "write all tests" and GREEN as "write all code."

This produces **crap tests**:

- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things (data structures, function signatures) rather than user-facing behavior
- Tests become insensitive to real changes - they pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

**Correct approach**: Vertical slices via tracer bullets. One test → one implementation → repeat. Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
  ...
```

## Workflow

### 1. Planning

When exploring the codebase, use the project's domain glossary so that test names and interface vocabulary match the project's language, and respect ADRs in the area you're touching.

Before writing any code:

If the project workflow already provides a locked, user-approved Contract or plan, reuse it as the answers below and do not ask for a second approval. Ask only about an unresolved choice that would change behavior or scope.

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Design interfaces for [testability](interface-design.md)
- [ ] List the behaviors to test (not implementation steps)
- [ ] Get user approval on the plan

When no approved artifact answers them, ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Use the approved priorities, or confirm any unresolved priority with the user. Focus testing effort on critical paths and complex logic, not every possible edge case.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:

- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor Check

After all tests pass, perform at least one explicit check of whether refactoring is needed. "No refactor needed" is a valid result; when there is no concrete issue, leave the code unchanged.

Refactor only when the issue was introduced by the current change or is demonstrably obstructing the current goal. These conditions make a change eligible; they do not make it mandatory. Name the concrete cost in the current diff before editing. Preserve externally observable behavior and keep the refactor inside the current task's scope. Do not modify adjacent pre-existing issues; report one only when it is a material residual risk for the current task.

If the check finds a concrete in-scope issue, read [refactoring.md](refactoring.md) before changing structure. Read [deep-modules.md](deep-modules.md) only when that issue specifically concerns interface depth. Run tests after each refactor step.

**Never refactor while RED.** Get to GREEN first.

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses a stable boundary approved by the project
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
