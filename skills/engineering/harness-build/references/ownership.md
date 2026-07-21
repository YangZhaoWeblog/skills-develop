# Harness Ownership

Classify before editing. Git is the transaction and rollback boundary.

| Class | Treatment | Typical paths |
|---|---|---|
| Universal | Replace from the reviewed baseline, then inspect the diff | `harness/code-review.md`, `harness/pge-protocol.md`, `.codex/agents/*.toml`, `docs/pge/*.template.md` |
| Project-owned | Read and merge intentionally; never blind-copy | `AGENTS.md`, `harness/code-shape.md`, `harness/failures.md`, `harness/glossary.md`, workflow/hook/instruction governance |
| Optional profile | Create only when repository evidence requires it | API, database, deployment documents |
| Retired | Delete the file and every active reference | `harness/testing.md`, `harness/development.md`, `harness/dependency-map.md`, Harness checker/resolver scripts |
| External owner | Preserve byte-for-byte; report concerns to its owner | `.claude/agents/`, unrelated Skills and tool adapters |
| Project knowledge | Preserve unless the owner explicitly replaces it | `ARCHITECTURE.md`, `docs/design/`, diagrams, ordinary project documentation |

Before close, verify:

- every changed path has one owner;
- no retired path remains referenced;
- universal rules are not duplicated in project files;
- project corrections still have positive, negative, and valid-control examples;
- unrelated dirty work and external-owner files are unchanged.
