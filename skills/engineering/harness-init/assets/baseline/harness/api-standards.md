# API Standards

> status: stub
> owner: api-standards
> layer: profile
> This file owns public API rules; it does not own business logic implementation.

## Activation

Activate when the project exposes RPC, HTTP, GraphQL, CLI, SDK, event, or other public interfaces.

## Core Rules

- Change source API definitions before generated code.
- Preserve compatibility unless a breaking change is explicitly approved.
- Document request/response semantics and error surface.
- Keep generated files out of manual edits.

## Project Growth TODO

- [ ] Identify API source files.
- [ ] Define compatibility policy.
- [ ] Define error and authentication rules.
