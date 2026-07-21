# Project Code-Shape Schemas

`harness/code-shape.md` records only project corrections proven by review or failure. Architecture belongs in `ARCHITECTURE.md`; universal principles belong in `coding-style.md`; incident history belongs in `failures.md`.

Each schema has four fields:

- **Use when**: concrete trigger.
- **Prefer**: local positive shape.
- **Avoid**: observed negative shape and its cost.
- **Exception**: valid control that prevents mechanical enforcement.

Examples:

## Object roles

- **Use when**: naming request, stored, or transition objects.
- **Prefer**: names reveal source and role, such as `resource` and `origin`.
- **Avoid**: generic `next`, `target`, or `data` when the referent is specific.
- **Exception**: `nextSequence` is valid when an ordering basis exists.

## Abstraction

- **Use when**: adding a wrapper, projection, rank, manager, or core layer.
- **Prefer**: reuse an existing capability; keep a helper that owns policy, protocol, storage encoding, transaction, or error mapping.
- **Avoid**: wrappers that only rename or discard returns, and abstractions that hide one use case's flow.
- **Exception**: caller count and file length alone never prove over-abstraction.

## Observable invariants

- **Use when**: comparing old/new identity or modeling a defensive state.
- **Prefer**: require evidence the real interface can observe and the real writer can create.
- **Avoid**: branches reachable only through an impossible mock or an identity already fixed by lookup.
- **Exception**: migrations, external writers, repair paths, or an explicit old/new identity reopen the state.

## Semantic layout

- **Use when**: formatting or comments affect how a business flow is scanned.
- **Prefer**: keep short semantic groups spatially close and use a few stage comments for long flows.
- **Avoid**: mechanical one-argument-per-line formatting or comments that restate syntax.
- **Exception**: distinct semantic groups and long literals may remain multiline; short functions need no stage index.

## Tests

- **Use when**: mocks assert calls, order, or counts.
- **Prefer**: lock observable results and business-significant order.
- **Avoid**: strict helper choreography that fails under behavior-preserving refactors.
- **Exception**: transactions, authorization-before-write, irreversible side effects, CAS, and concurrency protocols justify ordering assertions.
