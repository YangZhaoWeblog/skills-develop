# Coding Style

> status: active
> owner: coding-style
> layer: profile
> This file owns code structure and style; it does not own tests, review, or deployment.

## General

- Follow existing project style before inventing abstractions.
- Keep edits scoped to the requested behavior.
- Prefer clear names and small functions.
- Avoid unrelated refactors.

## Architecture

- Respect existing layers and dependency direction.
- Put shared business logic in the project-approved shared layer.
- Keep external dependencies behind project-approved interfaces or contexts.

## Errors & Logging

- Preserve error causes.
- Return user-facing errors through approved project surfaces.
- Avoid debug prints in committed code.

## Project Growth TODO

- [ ] Add language-specific formatting rules.
- [ ] Add architecture/layering rules.
- [ ] Add naming and error-handling conventions.
