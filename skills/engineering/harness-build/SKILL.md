---
name: harness-build
description: Safely force-upgrade an existing Git code repository to the canonical AI agent Harness. Use when a user asks to build, rebuild, upgrade, or refresh AGENTS.md, harness governance, PGE support, and required Grill dependencies while preserving project-grown rules and unrelated work.
---

# Harness Build

Use this Skill to build a complete candidate Harness in clean staging, validate it with source-owned capabilities, and apply only managed paths with full rollback.

## Preconditions

- The target is an existing Git code repository.
- Read its `AGENTS.md`, relevant `harness/*.md`, current dirty work, build files, API/schema/dependency facts, and protected-branch rules.
- State the one-sentence goal and hard blockers.
- For medium-or-larger upgrades, use the target repository's PGE workflow and pass its Human Start Gate before apply.
- Do not infer permission to commit, push, enable hooks, or change product code.

## Workflow

1. For an existing Harness, prepare a reviewed project overlay in an OS temporary directory. Copy the confirmed `AGENTS.md` and every existing standard project-owned `harness/*.md` path listed by `assets/ownership-manifest.json`, preserving bytes and modes. Add `project-overlay.json`:

   ```json
   {
     "schema_version": 1,
     "reviewed": true,
     "project_owned_paths": ["AGENTS.md", "harness/coding-style.md"]
   }
   ```

   The list must cover every existing project-owned path. Do not include Builder-owned `harness/pge-protocol.md`, unknown governance extensions, or unreviewed content. Fresh repositories without `AGENTS.md` or `harness/` may use the baseline without an overlay.

2. Run the source tests:

   ```bash
   python3 -m unittest discover -s scripts/tests -p 'test_*.py'
   ```

3. Preview the exact candidate without writing the target:

   ```bash
   python3 scripts/build_harness.py \
     --target /absolute/path/to/repository \
     --project-overlay /absolute/path/to/reviewed/overlay \
     --staging-only /absolute/path/to/empty/staging
   ```

4. Inspect the candidate, transaction summary, resolved upstream evidence, project-rule anchors, preserved extensions, and target diff. Confirm that overlay paths were strongly copied, inherited Agent reasoning efforts were retained, and no top-level Agent `model` key was introduced.
5. Apply only after the target workflow authorizes implementation:

   ```bash
   python3 scripts/build_harness.py \
     --target /absolute/path/to/repository \
     --project-overlay /absolute/path/to/reviewed/overlay
   ```

6. After Builder returns, run the target repository's structure checks, trusted Human Start checker at Coding Start, tests, lint, and build in the scope required by its harness. These are caller-controlled verification commands; Builder never executes target or staging scripts.
7. Record the resolved upstream commit/tree digest, four Skill digests, offline-resolved `skills` CLI version, exact verification commands, and results in the task's eval or handoff. Do not create a persistent build-state file.

## Safety Boundary

- The Builder resolves `grilling`, `domain-modeling`, `grill-me`, and `grill-with-docs` from one current `mattpocock/skills` snapshot.
- Source validation completes before backup or apply.
- Builder-owned paths come from `assets/ownership-manifest.json`.
- Unrelated installed Skills, ordinary Harness knowledge, project diagrams, symlinks, ignored files, build artifacts, and dirty user work are preserved.
- Unknown Codex Agent execution entries block before staging.
- Unknown Harness files that claim workflow, gate, PGE, Agent, instruction, or governance authority block before staging; ordinary project knowledge remains preserved.
- Apply is serial. Any apply or post-check failure restores the complete non-`.git` target tree by path, type, mode, file content, and symlink target.
- The source validator hashes the trusted Human Start checker but never executes target code.
- The four upstream Skill directories are copied byte-for-byte from one Git snapshot; mixed snapshots block.
- The Builder reads an installed or cached `skills` CLI version offline and never invokes `skills@latest`.
- Network access is used only to clone the one upstream snapshot that supplies the four Grill Skills.

## Files

- `assets/baseline/`: canonical generated Harness files.
- `assets/capability-manifest.json`: source-owned capability assertions.
- `assets/ownership-manifest.json`: strong-overwrite and preserve classifications.
- `scripts/build_harness.py`: staging, validation, transaction, apply, and rollback.
- `scripts/validate_capabilities.py`: read-only source validator.
- `scripts/tests/`: standard-library behavior tests.
