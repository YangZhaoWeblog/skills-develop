# Refactoring Boundaries

Read this file only after all tests are green and the refactor check identifies a concrete issue.

Refactor only when:

- the current change introduced duplication, misleading names, or unnecessary structure; or
- existing structure demonstrably obstructs the current goal or makes the current behavior unsafe to change.

These conditions only make a candidate eligible; they do not require a refactor. Name the concrete cost in the current diff before editing. Keep every refactor inside the current task's scope and preserve externally observable behavior. Do not fix adjacent pre-existing issues; report one only when it is a material residual risk for the current task.

For each candidate:

1. Name the concrete problem in the current change.
2. Confirm the structural change will not alter external behavior.
3. Make the smallest change that resolves that problem.
4. Run the relevant tests before considering another refactor.

Do not refactor solely because code is long, a helper might be reusable later, a design pattern could apply, or nearby code could be improved. Use [deep-modules.md](deep-modules.md) only when the identified in-scope problem concerns interface depth.
