# Project Code Shape

> status: active
> owner: project-code-shape
> layer: project-grown
> Records only project-specific rules proven by review or failure. Harness upgrades merge this file intentionally.

Each schema has exactly four fields:

## Schema: <Name>

- **Use when**: the concrete trigger.
- **Prefer**: the local positive shape.
- **Avoid**: the proven negative shape and its cost.
- **Exception**: the valid control that prevents mechanical enforcement.

Keep incident history in `failures.md`, universal principles in `coding-style.md`, and architecture facts in `ARCHITECTURE.md`. Do not add a schema without both a real negative and a valid control.
