# Project Code Shape

> status: active
> owner: project-code-shape
> layer: project-grown
> This project-owned file records local positive, negative, and valid-control schemas. Builder preserves it byte-for-byte; repository facts remain in `coding-style.md`.

## How To Read

- Use a schema only when its `Use when` condition matches concrete code.
- Replace `Avoid` with `Prefer` only after checking `Exception`; do not enforce keywords mechanically.
- Keep incident history and detailed evidence in the project's `failures.md`.

## How To Grow This Profile

- Start from a real review correction or failure, not a stylistic preference.
- Preserve the local vocabulary and nearby code pattern that make the rule actionable.
- Add a valid control so an example does not become a universal prohibition.
- Keep universal guidance in `coding-style.md`; keep repository-specific choices here.
- Replace starter examples with stronger local evidence as the project learns.

## Schema: Object-Role Naming

- **Use when**: a new or renamed identifier represents a request, stored object, result, or transition participant.
- **Prefer**: use the repository's established role name, such as `request` or `storedRecord`, when that is what the value is.
- **Avoid**: use `data`, `item`, or `next` without a concrete object or ordering basis.
- **Exception**: `nextOffset` is precise when an ordered traversal supplies that basis; a new name is valid when it exposes a real distinction absent from nearby vocabulary.

## Schema: Semantic Layout And Spatial Proximity

- **Use when**: formatting splits a short expression or related error path into mechanically uniform lines.
- **Prefer**: keep a short state check on one line; use multiline layout only when it creates meaningful semantic groups.
- **Avoid**: put every argument and nested error detail on its own line solely to satisfy a numeric width rule.
- **Exception**: multiline layout is valid for genuinely distinct semantic groups, long data literals, or clearer alignment.

## Schema: Independent Abstraction Value

- **Use when**: a new helper, wrapper, interface, rank, manager, or aggregate layer mostly renames another operation.
- **Prefer**: retain a helper that owns stable storage encoding, error mapping, protocol translation, a transaction, or reusable domain policy.
- **Avoid**: add a pass-through wrapper, mirror an existing enum without independent semantics, or redistribute one flow across an aggregate core.
- **Exception**: one caller is acceptable when the helper owns an independent boundary; caller count alone neither proves nor disproves value.

## Schema: Cohesive Domain Input

- **Use when**: a caller already owns a cohesive domain object, while a helper consumes two or more of its identity, ownership, version, or policy fields and a change proposes adding another scalar parameter from that same object.
- **Prefer**: pass the existing domain object or a smaller independently meaningful value object, then derive the coupled fields inside the operation that uses them.
- **Avoid**: turn `generatePolicy(productID, orgID)` into `generatePolicy(productID, orgID, productNumber)` when all three values already belong to the loaded `product`.
- **Exception**: keep scalars when they are independently sourced, only one field is needed, the callee is a stable primitive or protocol boundary, or passing the whole object would broaden authority or create an invalid dependency.

## Schema: Visible Use-Case Flow

- **Use when**: orchestration is moved behind generic `core`, `manager`, `builder`, or callback layers, or a rejection follows an avoidable side effect.
- **Prefer**: show validation, authorization, state decision, write/external effect, and response/event stages in use-case order.
- **Avoid**: hide a single use case behind an aggregate object that only forwards calls, or perform persistent/external work before a locally decidable rejection.
- **Exception**: a prerequisite read is valid when the decision cannot be made locally and the read is contractually side-effect free; stable transaction/protocol boundaries may remain helpers.

## Schema: Operation-Semantic State Policy

- **Use when**: a flow adds raw state comparisons in several methods or proposes one generic interpreter with flags, absent sentinels, and invalid parameter combinations.
- **Prefer**: use a small operation-semantic check or shared primitive whose call site states the current object and allowed transition.
- **Avoid**: duplicate raw `state != ...` branches across operations, or encode all lifecycle behavior in one flag-driven helper.
- **Exception**: a direct comparison is valid when it is the sole local rule and is clearer than a named helper; a generic primitive is valid when all parameter combinations are meaningful.

## Schema: Existing Capability Reuse

- **Use when**: new code wraps, recomputes, or re-exposes behavior available nearby.
- **Prefer**: call the existing helper or library operation directly and preserve its established contract.
- **Avoid**: add a thin existence wrapper over a get-with-exists operation or reimplement a standard set/equality primitive.
- **Exception**: a wrapper is valid when it changes the contract, owns stable encoding/error translation, or creates a real policy boundary.

## Schema: Staged Navigation Comments

- **Use when**: a method contains several business stages or a surprising ordering decision that names alone do not expose quickly.
- **Prefer**: add short stage comments in the project's language and format, describing why or the business stage rather than restating syntax.
- **Avoid**: omit navigation from a long multi-stage flow, or comment every obvious line with a paraphrase of the code.
- **Exception**: a short self-explanatory function needs no stage comments; local convention may prefer numbered or unnumbered stage labels.

## Schema: Business Constant Ownership

- **Use when**: production code introduces a business sequence, state, method, event, parameter, or storage identifier.
- **Prefer**: place or reuse the constant in the established package/file for that concept.
- **Avoid**: declare a shared business constant beside one method merely because it has one current use.
- **Exception**: a private algorithmic constant may stay local when it has no domain identity and no established shared owner.

## Schema: Error And Log Visual Grouping

- **Use when**: an error branch contains a log and returned/wrapped error, especially with several context fields.
- **Prefer**: keep the guard, concise log, and return adjacent; wrap only the semantically large part.
- **Avoid**: expand each short function argument onto separate lines or separate a log from its corresponding return.
- **Exception**: multiline construction is valid when it groups distinct context or preserves a clear error-building hierarchy.

## Schema: Tests Protect Business Order

- **Use when**: mocks use broad order chains or implementation-specific call counts while behavior remains unchanged under harmless refactoring.
- **Prefer**: assert authorization-before-write, validation-before-side-effect, write-before-event, and observable results where those orders are contractual.
- **Avoid**: chain every helper call with ordering constraints solely because the current implementation happens to call them that way.
- **Exception**: explicit mock order is valid for business-significant order, transaction boundaries, concurrency protocols, or irreversible effects.

## Schema: Evidence-Backed Defensive Checks

- **Use when**: code adds a nil/existence cross-check, invariant comparison, fallback, or validation not required by the called contract.
- **Prefer**: validate untrusted input and observed failure modes; rely on a documented internal contract after checking its error/existence result.
- **Avoid**: add a check that cannot be reached through the real lookup/interface, then make a mock violate reality so the branch appears tested.
- **Exception**: defense in depth is valid at an untrusted or version-skewed boundary when the failure is possible and the response is specified.
