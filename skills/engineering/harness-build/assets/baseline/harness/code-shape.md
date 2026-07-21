# Project Code Shape

> status: active
> owner: project-code-shape
> layer: project-grown
> This project-owned file records local positive, negative, and valid-control schemas. Builder preserves it byte-for-byte; repository facts remain in `coding-style.md`.

## How To Grow This Profile

- Start from a real review correction or failure, not a stylistic preference.
- Preserve the local vocabulary and nearby code pattern that make the rule actionable.
- Add a valid control so an example does not become a universal prohibition.
- Keep universal guidance in `coding-style.md`; keep repository-specific choices here.
- Replace starter examples with stronger local evidence as the project learns.

## Schema: Object-Role Naming

- **Intent**: make each production object recognizable at its use site.
- **Trigger**: a new or renamed identifier represents a request, stored object, result, or transition participant.
- **Risk**: vague or locally novel names force readers to reconstruct the referent.
- **Positive**: use the repository's established role name, such as `request` or `storedRecord`, when that is what the value is.
- **Negative**: use `data`, `item`, or `next` without a concrete object or ordering basis.
- **Allowed exception / valid control**: `nextOffset` is precise when an ordered traversal supplies that basis; a new name is valid when it exposes a real distinction absent from nearby vocabulary.
- **Generator action**: search the same layer and neighboring use cases before naming, then state evidence for a deliberate deviation.
- **Evaluator evidence**: compare the production diff with nearby identifiers and require a concrete referent for each role name.
- **Automation owner**: Generator and Evaluator; naming remains a judgment gate.
- **Provenance**: reader-oriented naming in the [Google Go Style Guide](https://google.github.io/styleguide/go/guide.html) plus project review/failure evidence.

## Schema: Semantic Layout And Spatial Proximity

- **Intent**: let related conditions, logs, and returns form one visual unit.
- **Trigger**: formatting splits a short expression or related error path into mechanically uniform lines.
- **Risk**: excessive vertical fragmentation hides the main condition and separates cause from response.
- **Positive**: keep a short state check on one line; use multiline layout only when it creates meaningful semantic groups.
- **Negative**: put every argument and nested error detail on its own line solely to satisfy a numeric width rule.
- **Allowed exception / valid control**: multiline layout is valid for genuinely distinct semantic groups, long data literals, or clearer alignment.
- **Generator action**: read the rendered block as a unit and regroup only the expressions whose meaning becomes easier to scan.
- **Evaluator evidence**: cite the exact fragmented or overloaded block and explain which related facts are visually separated.
- **Automation owner**: formatter for syntax; Generator, Evaluator, and human review for semantic layout.
- **Provenance**: formatter-versus-judgment boundary in [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) plus project review/failure evidence.

## Schema: Independent Abstraction Value

- **Intent**: keep abstractions that own behavior, a stable boundary, or a meaningful concept.
- **Trigger**: a new helper, wrapper, interface, rank, manager, or aggregate layer mostly renames another operation.
- **Risk**: indirection increases navigation while hiding the use-case skeleton or duplicating an existing capability.
- **Positive**: retain a helper that owns stable storage encoding, error mapping, protocol translation, a transaction, or reusable domain policy.
- **Negative**: add a pass-through wrapper, mirror an existing enum without independent semantics, or redistribute one flow across an aggregate core.
- **Allowed exception / valid control**: one caller is acceptable when the helper owns an independent boundary; caller count alone neither proves nor disproves value.
- **Generator action**: apply the deletion or inlining test and name the behavior, boundary, or clarity that would be lost.
- **Evaluator evidence**: follow the production call chain and show whether deleting or inlining the abstraction loses independent value.
- **Automation owner**: Generator and Evaluator; structural tools may only provide navigation evidence.
- **Provenance**: smell-as-investigation guidance in [Martin Fowler's Code Smell](https://martinfowler.com/bliki/CodeSmell.html) plus project review/failure evidence.

## Schema: Visible Use-Case Flow

- **Intent**: keep the main business stages and rejection points visible in the entry flow.
- **Trigger**: orchestration is moved behind generic `core`, `manager`, `builder`, or callback layers, or a rejection follows an avoidable side effect.
- **Risk**: reviewers cannot see ordering, side effects, or business branches without recursive navigation.
- **Positive**: show validation, authorization, state decision, write/external effect, and response/event stages in use-case order.
- **Negative**: hide a single use case behind an aggregate object that only forwards calls, or perform persistent/external work before a locally decidable rejection.
- **Allowed exception / valid control**: a prerequisite read is valid when the decision cannot be made locally and the read is contractually side-effect free; stable transaction/protocol boundaries may remain helpers.
- **Generator action**: keep the production skeleton at the call site and push down only independently meaningful operations.
- **Evaluator evidence**: trace the rejection and success paths in production code, noting every persistent or external effect in order.
- **Automation owner**: Generator, Evaluator, behavior tests, and side-effect fakes where available.
- **Provenance**: invariant-oriented constraints in [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) plus cross-repository review evidence.

## Schema: Operation-Semantic State Policy

- **Intent**: express allowed state transitions in the vocabulary of the operation.
- **Trigger**: a flow adds raw state comparisons in several methods or proposes one generic interpreter with flags, absent sentinels, and invalid parameter combinations.
- **Risk**: scattered rules drift, while an over-generic interpreter hides which transition each operation permits.
- **Positive**: use a small operation-semantic check or shared primitive whose call site states the current object and allowed transition.
- **Negative**: duplicate raw `state != ...` branches across operations, or encode all lifecycle behavior in one flag-driven helper.
- **Allowed exception / valid control**: a direct comparison is valid when it is the sole local rule and is clearer than a named helper; a generic primitive is valid when all parameter combinations are meaningful.
- **Generator action**: inventory operations and choose the smallest shared policy that leaves each transition legible at its call site.
- **Evaluator evidence**: compare all affected operations for drift, invalid helper combinations, and call-site clarity.
- **Automation owner**: Generator, Evaluator, and state-transition tests.
- **Provenance**: reader-centered clarity from the [Google Go Style Guide](https://google.github.io/styleguide/go/guide.html) plus project lifecycle review evidence.

## Schema: Existing Capability Reuse

- **Intent**: reuse an existing project, dependency, or standard-library capability when its contract already fits.
- **Trigger**: new code wraps, recomputes, or re-exposes behavior available nearby.
- **Risk**: duplicate paths drift and create unnecessary tests, storage reads, or error handling.
- **Positive**: call the existing helper or library operation directly and preserve its established contract.
- **Negative**: add a thin existence wrapper over a get-with-exists operation or reimplement a standard set/equality primitive.
- **Allowed exception / valid control**: a wrapper is valid when it changes the contract, owns stable encoding/error translation, or creates a real policy boundary.
- **Generator action**: search the repository, direct dependencies, and standard library before adding a capability; record why a near match is insufficient.
- **Evaluator evidence**: identify the existing capability and compare semantics, errors, and side effects rather than names alone.
- **Automation owner**: Generator and Evaluator; search/static analysis supplies evidence but does not decide semantic equivalence.
- **Provenance**: simplicity guidance in the [Google Go Style Guide](https://google.github.io/styleguide/go/guide.html) plus project duplication failures.

## Schema: Staged Navigation Comments

- **Intent**: give readers a fast index into a non-trivial production flow.
- **Trigger**: a method contains several business stages or a surprising ordering decision that names alone do not expose quickly.
- **Risk**: readers must parse every statement before locating validation, policy, state change, and side effects.
- **Positive**: add short stage comments in the project's language and format, describing why or the business stage rather than restating syntax.
- **Negative**: omit navigation from a long multi-stage flow, or comment every obvious line with a paraphrase of the code.
- **Allowed exception / valid control**: a short self-explanatory function needs no stage comments; local convention may prefer numbered or unnumbered stage labels.
- **Generator action**: add only comments that shorten navigation or preserve a non-obvious reason, then remove stale narration.
- **Evaluator evidence**: read comments independently and verify they index real stages, remain accurate, and do not compensate for opaque code.
- **Automation owner**: Generator, Evaluator, and human review.
- **Provenance**: necessary-comment reasoning in [Robert C. Martin's Necessary Comments](https://blog.cleancoder.com/uncle-bob/2017/02/23/NecessaryComments.html) plus project review evidence.

## Schema: Business Constant Ownership

- **Intent**: keep shared business vocabulary in the repository's designated owner.
- **Trigger**: production code introduces a business sequence, state, method, event, parameter, or storage identifier.
- **Risk**: local duplicates hide shared meaning and allow values to diverge.
- **Positive**: place or reuse the constant in the established package/file for that concept.
- **Negative**: declare a shared business constant beside one method merely because it has one current use.
- **Allowed exception / valid control**: a private algorithmic constant may stay local when it has no domain identity and no established shared owner.
- **Generator action**: inspect nearby constants and the project index before choosing ownership; avoid creating a new constants layer.
- **Evaluator evidence**: cite the established owner and determine whether the value is domain vocabulary or a local implementation detail.
- **Automation owner**: Generator, Evaluator, and project-specific lint when available.
- **Provenance**: repository organization guidance in [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) plus project convention failures.

## Schema: Error And Log Visual Grouping

- **Intent**: keep detection, diagnostic context, and returned error easy to scan as one path.
- **Trigger**: an error branch contains a log and returned/wrapped error, especially with several context fields.
- **Risk**: mechanical wrapping separates the condition from the diagnostic or buries the business field among formatting noise.
- **Positive**: keep the guard, concise log, and return adjacent; wrap only the semantically large part.
- **Negative**: expand each short function argument onto separate lines or separate a log from its corresponding return.
- **Allowed exception / valid control**: multiline construction is valid when it groups distinct context or preserves a clear error-building hierarchy.
- **Generator action**: compare neighboring error paths and format the branch as one readable unit without dropping causes or context.
- **Evaluator evidence**: cite the branch and verify cause preservation, project error surface, log/return consistency, and visual grouping.
- **Automation owner**: compiler/formatter for syntax; Generator and Evaluator for grouping and error semantics.
- **Provenance**: error-handling review guidance in [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) plus project readability corrections.

## Schema: Tests Protect Business Order

- **Intent**: make tests constrain externally meaningful ordering without freezing incidental helper choreography.
- **Trigger**: mocks use broad order chains or implementation-specific call counts while behavior remains unchanged under harmless refactoring.
- **Risk**: tests become a duplicate implementation and create large false failures during design cleanup.
- **Positive**: assert authorization-before-write, validation-before-side-effect, write-before-event, and observable results where those orders are contractual.
- **Negative**: chain every helper call with ordering constraints solely because the current implementation happens to call them that way.
- **Allowed exception / valid control**: explicit mock order is valid for business-significant order, transaction boundaries, concurrency protocols, or irreversible effects.
- **Generator action**: classify each order assertion as contractual or incidental before adding or relaxing it.
- **Evaluator evidence**: map ordering assertions to acceptance, a hard rule, or an externally observable failure; unmatched internal order is suspect.
- **Automation owner**: behavior tests, Generator, and Evaluator.
- **Provenance**: invariant-over-implementation guidance in [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) plus project mock-coupling failures.

## Schema: Evidence-Backed Defensive Checks

- **Intent**: defend real trust boundaries without accumulating impossible or redundant branches.
- **Trigger**: code adds a nil/existence cross-check, invariant comparison, fallback, or validation not required by the called contract.
- **Risk**: impossible branches disguise interface mismatch, duplicate trusted guarantees, and increase untestable paths.
- **Positive**: validate untrusted input and observed failure modes; rely on a documented internal contract after checking its error/existence result.
- **Negative**: add a check that cannot be reached through the real lookup/interface, then make a mock violate reality so the branch appears tested.
- **Allowed exception / valid control**: defense in depth is valid at an untrusted or version-skewed boundary when the failure is possible and the response is specified.
- **Generator action**: name the threat, broken guarantee, or observed incident before adding the branch; make fakes obey production contracts.
- **Evaluator evidence**: trace the real interface and data path, then verify the branch is reachable and the test double is physically possible.
- **Automation owner**: Generator, Evaluator, contract tests, and security tooling for deterministic boundary checks.
- **Provenance**: evidence-driven constraints in [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) plus project false-invariant failures.
