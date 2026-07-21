# Coding Style

> status: active
> owner: coding-style
> layer: profile
> This fact-generated file owns universal code structure and repository facts. Project-grown positive/negative schemas live in `code-shape.md`.

## Decision Model

- Optimize for the next reader: clarity, simplicity, and local consistency outrank a fashionable pattern.
- Use repository-first naming and structure. Search the same layer and neighboring flows before inventing vocabulary or abstractions.
- Treat a smell as a prompt to investigate, not a verdict. Activate a schema only when its trigger and concrete risk are present, then apply its valid control.
- Treat the confirmed goal, scope, non-goals, acceptance criteria, and cited project hard rules as the behavior boundary.
- Every production behavior change must serve that boundary. Do not improve unrelated code; clean only current-change residue.

## Production Flow

- Keep the visible use-case flow at the entry method: rejection checks, policy decisions, state changes, persistent/external effects, and result/event stages should be reviewable in order.
- Put locally decidable rejection before avoidable external or persistent side effects.
- Keep operation-semantic state policy shared enough to prevent drift and specific enough that each operation's transition remains visible.
- Name the actual object, role, transition, and relevant ordering basis; generic words are acceptable only when their referent is genuinely generic.

## Abstractions And Capabilities

- Prefer existing repository, dependency, or standard-library capabilities when their contracts match.
- Preserve an already-loaded cohesive domain object across a helper boundary when the helper consumes several of its identity or policy fields; avoid a growing tunnel of scalars that can describe different snapshots.
- Apply a deletion or inlining test to a proposed abstraction: keep it when removing it loses independent behavior, a stable boundary, reusable policy, or material clarity.
- Caller count is evidence, not a rule. A one-caller storage/protocol boundary may be valuable; a many-caller pass-through wrapper may still be noise.
- Do not add interfaces solely for mocking, future-only configuration, mirrored enums/ranks without independent semantics, or aggregate layers that only redistribute one use case.

## Layout And Comments

- Format for semantic groups and spatial proximity. Keep a short condition or error path together; split when the groups themselves carry meaning.
- Do not impose a fixed source-line limit. Use the language formatter for syntax and human judgment for readable grouping.
- Use staged navigation comments when they shorten a non-trivial flow. Comments explain purpose, business stage, or surprising order; they do not narrate obvious syntax.
- Follow the project's language and numbered/unnumbered comment convention.

## Errors, Logs, And Defensive Code

- Preserve causes and use project-approved error surfaces.
- Keep detection, diagnostic log, and returned error visually adjacent; include the same decisive business context where appropriate.
- Add evidence-backed defensive checks at real trust boundaries or for observed failures. Do not encode impossible states merely to appear safer.
- Make test doubles obey production interface, storage, and lookup contracts.

## Tests As Design Evidence

- Tests protect behavior and business-significant order, not incidental helper choreography.
- Order constraints are appropriate for authorization-before-write, validation-before-side-effect, write-before-event, transactions, concurrency protocols, and irreversible effects.
- Passing tests do not settle naming, abstraction, visible-flow, or semantic-layout quality; read the complete production diff independently.

## Authoritative Sources

- [Google Go Style Guide](https://google.github.io/styleguide/go/guide.html): clarity, simplicity, consistency, and reader perspective.
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments): mechanical formatting belongs to Go tooling; review guidance covers the non-mechanical remainder.
- [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/): encode enforceable invariants and feedback loops rather than micromanaging every implementation.
- [Martin Fowler, Code Smell](https://martinfowler.com/bliki/CodeSmell.html): a smell is evidence to investigate, not an automatic refactor command.
- [Robert C. Martin, Necessary Comments](https://blog.cleancoder.com/uncle-bob/2017/02/23/NecessaryComments.html): retain comments that carry purpose or otherwise unavailable context; avoid redundant narration.

## Project Growth TODO

- [ ] Replace starter `code-shape.md` examples with provenance-tagged local corrections and valid controls.
- [ ] Add language- and architecture-specific conventions supported by repository evidence.
