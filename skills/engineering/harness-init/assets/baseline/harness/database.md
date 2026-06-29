# Database

> status: stub
> owner: database
> layer: profile
> This file owns schema, migration, and data consistency rules; it does not own API contracts.

## Activation

Activate when the project owns database schema, migrations, persistence models, or data consistency behavior.

## Core Rules

- Use migrations for schema changes.
- Do not edit already-applied migrations unless explicitly approved.
- Define transaction boundaries.
- Document indexes and compatibility constraints.

## Project Growth TODO

- [ ] Identify database engines.
- [ ] Identify migration tool.
- [ ] Define transaction and rollback expectations.
