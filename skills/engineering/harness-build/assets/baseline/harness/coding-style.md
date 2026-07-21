# Coding Style

> status: active
> owner: coding-style
> layer: universal
> Owns universal code decisions and detected repository facts. Project corrections live in `code-shape.md`.

## Decisions

- Optimize for the next reader: clarity, simplicity, and local consistency outrank fashionable patterns.
- Search the same layer and neighboring flows before inventing vocabulary, wrappers, or abstractions.
- Keep the use-case flow visible: rejection, policy, state change, side effect, and result/event should be reviewable in order.
- Put locally decidable rejection before avoidable persistent or external effects.
- Name the actual object, role, transition, and ordering basis; generic names require a genuinely generic referent.
- Reuse an existing capability when its contract matches. Keep an abstraction only when removing it loses behavior, a stable boundary, reusable policy, or material clarity.
- Preserve a cohesive loaded domain object when a helper consumes several coupled fields; do not grow scalar tunnels that can describe different snapshots.
- Format for semantic groups and spatial proximity. Do not optimize mechanically for a numeric line limit.
- Use short navigation comments only when they expose business stages or surprising order.
- Add defensive checks only at real trust boundaries or for observed failures. Test doubles must obey production contracts.
- Tests protect observable behavior and business-significant order, not incidental helper choreography.
- Passing tests do not settle naming, abstraction, visible-flow, or semantic-layout quality; review the production diff independently.
- Do not expand beyond the approved goal. Review current-change residue after GREEN; do not clean unrelated code.

## Detected Repository Facts

- No repository facts generated yet.
