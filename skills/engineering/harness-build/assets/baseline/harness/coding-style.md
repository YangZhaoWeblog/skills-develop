# Coding Style

> status: active
> owner: coding-style
> layer: profile
> This file owns code structure and style; it does not own tests, review, or deployment.

## General

- Follow existing project style before inventing abstractions.
- Treat the confirmed goal, scope, non-goals, acceptance criteria, and properties explicitly required by acceptance or a cited project hard rule as the behavior boundary.
- Every production behavior change must directly serve that boundary or a cited project hard rule.
- Do not improve adjacent code; clean only residue introduced by the current change.
- Prefer clear names and small functions.
- Avoid unrelated refactors.
- Do not add defensive branches without evidence from an untrusted boundary, an acceptance-required property, a cited project hard rule, or an observed failure.

## Architecture

- Respect existing layers and dependency direction.
- Put shared business logic in the project-approved shared layer.
- Keep external dependencies behind project-approved interfaces or contexts.
- Judge an abstraction by independent behavior or clarity value, not caller or implementation count alone.
- Do not add an interface only for mocking or possible future implementations when it has no independent architecture or test-boundary value; do not add unused extension points.

## State & Concurrency

- Make the call site clear with the smallest useful combination of function name, result variable, branch, and necessary comment.
- Name the actual object, state transition, and relevant ordering basis; do not hide them behind vague lifecycle or concurrency terms.

## Errors & Logging

- Preserve error causes.
- Return user-facing errors through approved project surfaces.
- Avoid debug prints in committed code.

## Project Growth TODO

- [ ] Add language-specific formatting rules.
- [ ] Add architecture/layering rules.
- [ ] Add naming and error-handling conventions.
