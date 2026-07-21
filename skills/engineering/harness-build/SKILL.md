---
name: harness-build
description: Build or upgrade a repository AI Agent Harness using Git, reviewed Markdown/TOML templates, explicit ownership, and independent review. Use when Codex needs to create, simplify, migrate, or refresh AGENTS.md, harness/*.md, PGE templates, or Generator/Evaluator prompts without introducing a custom installer or validator.
---

# Harness Build

Use the Agent's native Git, file editing, repository inspection, and review abilities. Do not create an installer, checksum system, generated fact layer, rollback framework, or Harness-specific test suite.

## Workflow

1. Read the target `AGENTS.md`, relevant Harness files, Git status, current branch, nearby project rules, and existing failures.
2. Read [ownership.md](references/ownership.md). Classify every existing and proposed Harness path before editing.
3. Work on a normal feature branch from the target integration branch. Preserve unrelated and uncommitted user work.
4. Compare the target with `assets/baseline/`:
   - replace universal files with the reviewed baseline;
   - merge project-owned files intentionally instead of copying either side blindly;
   - generate optional API/database/deployment profiles only when target evidence requires them;
   - delete retired files and stale references;
   - preserve Claude-owned adapters and unrelated extensions byte-for-byte.
5. Keep `AGENTS.md` short: identity, commands, hard rules, routing, workflow, and index only.
6. Keep project corrections in `harness/code-shape.md`. Read [code-shape.md](references/code-shape.md) before adding or rewriting schemas.
7. Install or update `$pge-workflow` and `$tdd` separately from the same reviewed `skills-develop` revision. Do not copy their instructions into the Harness.
8. For `@path` entries in Agent prompts, read those files directly and include them in the handoff. `@` is a Harness convention, not an automatic include.
9. Inspect `git diff --check`, `git status --short`, the full Harness diff, deleted paths, stale references, and preserved project knowledge. Run only the target repository's applicable validation commands.
10. Request an independent Agent review of ownership, instruction conflicts, project-memory loss, positive/negative schemas, and PGE gate integrity.
11. Present one clean review commit. Use Git to amend, revert, or discard the branch when the upgrade is rejected.

## Boundaries

- Harness work is documentation/configuration work and does not use TDD.
- `$tdd` applies later when a Generator changes product behavior.
- Never modify product code while upgrading the Harness.
- Never overwrite project-owned knowledge without reading and merging it.
- Never claim semantic effectiveness from keyword checks. Validate difficult rule changes with fresh Agent tasks that receive the real Contract and project context but not the expected answer.
- Human Start, fixed Review base, clean candidate commit, and human MR review remain explicit decisions; no script substitutes for them.

## Resources

- `assets/baseline/`: output templates; copy or adapt only the files the target needs.
- [ownership.md](references/ownership.md): replacement, merge, retirement, and preservation rules.
- [code-shape.md](references/code-shape.md): compact positive/negative schema design and examples.
