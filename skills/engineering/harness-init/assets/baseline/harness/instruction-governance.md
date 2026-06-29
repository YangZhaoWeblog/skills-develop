# Instruction Governance

> status: active
> owner: instruction-governance
> layer: universal
> This file owns rule placement and harness evolution; it does not own execution gates.

## Placement Rules

- Put high-frequency hard constraints and workflow routing in `AGENTS.md`.
- Put topic rules in focused `harness/*.md` files.
- Put task-specific plans in project docs, not permanent harness.
- Put real incidents and lessons in `failures.md`.

## Layers

- `universal`: cross-project execution and governance.
- `profile`: activated by project type or stack.
- `project-grown`: local rules proven by this project after real feedback.

## Good Pattern

- Short entrypoint.
- One owner per rule.
- Topic files with narrow scope.
- Failures recorded before abstracting new rules.
- Tables only when they reduce reading cost.

## Bad Pattern

- Adding every new rule to `AGENTS.md`.
- Copying the same rule across files.
- Keeping vague slogans without triggers or actions.
- Letting examples become longer than rules.

## Maintenance

When a harness file grows too large or starts owning multiple topics, split by owner rather than adding more sections.
