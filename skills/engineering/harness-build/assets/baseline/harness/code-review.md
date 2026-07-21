# Code Review

> status: active
> owner: code-review
> layer: universal
> Owns review order, severity, evidence, and conclusions. Domain rules remain in their Harness owner files.

## Review Order

1. Fix the Review base and candidate commit. PGE evaluation requires in-scope changes committed, no staged/unstaged production diff, and every untracked path classified; then read `git diff <base>...<candidate>` completely.
2. **Standards**: freeze findings against `coding-style.md`, triggered `code-shape.md` schemas, and relevant API/storage/database owners before reading tests or author rationale.
3. **Spec**: compare the implementation with the originating Contract, issue, or approved plan; identify missing behavior, incorrect behavior, and scope creep.
4. Read tests and verification evidence; they may confirm behavior but cannot erase production findings.
5. Report both axes separately, then produce the required overall conclusion.

Do not paste a generic smell catalog into every review. A documented repository rule wins, schema valid controls prevent mechanical findings, and tooling-owned formatting is not relitigated manually.

## Severity

- Critical: security, authorization, data/state corruption, deterministic-runtime breach, or implementation outside the approved behavior boundary.
- Major: incorrect behavior, missing acceptance, fake verification, materially harmful design, or a broken workflow gate.
- Minor: maintainability or clarity issue that does not block acceptance.

Every finding cites the file/location, evidence, impact, governing rule or Contract clause, and required action. Do not invent findings to fill a quota.

## Conclusions

- PGE returns exactly `PASS`, `PASS_WITH_NOTES`, or `FAIL`.
- Any unresolved Critical or Major finding requires `FAIL`.
- `PASS_WITH_NOTES` requires explicit owner acceptance before close.
- The PGE Evaluator is the task's independent AI review; do not add a duplicate generic reviewer.
- Non-PGE non-trivial work still needs independent review. Human PR review remains separate.
