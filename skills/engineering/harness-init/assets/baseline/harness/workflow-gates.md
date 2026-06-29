# Workflow Gates

> status: active
> owner: execution-gates
> layer: universal
> This file owns execution gates; it does not own topic-specific implementation rules.

## Context Gate

Read the smallest context that can make the next decision safe: `AGENTS.md`, relevant harness files, target files, nearby tests, and relevant failure notes.

## Size & Risk Gate

- Small: local bug/config/doc change, usually 1-3 files.
- Medium: multi-file feature, public interface, DB migration, or critical flow.
- Large: new module, cross-module change, new dependency, or high-risk workflow.

Escalate when scope grows, when public API/DB/deployment changes appear, or when the work starts crossing ownership boundaries.

## Path Gate

Small work may proceed after Coding Start Check. Medium+ and critical-flow work must use the relevant protocol in `pge-protocol.md` or a project-specific design process, then return to Verify and Close.

## Coding Start Check

Before production code:

1. Confirm branch is not protected: {{protected_branches}}.
2. Check worktree and preserve unrelated user changes.
3. Confirm required context and design artifacts exist.
4. Confirm verification strategy.

## Dirty Worktree Protocol

- Treat existing changes as user work.
- Read relevant diffs before editing touched files.
- Avoid unrelated formatting.
- Ask before destructive actions.

## Verification Gate

Run the smallest meaningful verification for the change. Record commands and results. Do not silently skip required verification.

## Circuit Breaker Gate

If the same interface or flow fails 3 rounds of tests, reference alignment, or review, stop implementation and return to design or clarification.

## Commit Gate

Before commit, confirm Coding Start Check still holds, verification ran, review requirements are satisfied, and no unrelated files are included.
