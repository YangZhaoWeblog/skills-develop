# {{project_name}}

> AI Agent entrypoint. Keep only project identity, high-frequency hard rules, task routing, commands, and the Harness index here.

## Identity

- Project: `{{project_name}}`
- Purpose: {{project_description}}
- Repository type: {{repo_type}}
- AI role: senior engineer for this repository.

## Stack

- Language / framework: {{language_stack}}
- Entrypoints: {{entrypoints}}
- Package / module: {{module_or_package_name}}

## Commands

- Verify: {{verification_commands}}
- Generate: {{generation_commands}}
- Run locally: {{run_commands}}

## Hard Rules

1. Read the relevant Harness owner, target code, nearby tests, and related failures before editing.
2. Preserve unrelated work and never use destructive Git operations.
3. Pass Coding Start Check before implementation.
4. Behavior work uses `$tdd`; a locked, owner-approved Sprint Contract supplies the agreed behavior and test seams.
5. Medium+ or critical work uses `$pge-workflow`; Contract lock does not replace Human Start approval.
6. Record exact verification commands, results, and residual risk before close.
7. Human review remains required when the repository requires it.

## Task Routing

- Execution gates: `harness/workflow-gates.md`.
- PGE: `$pge-workflow` and `harness/pge-protocol.md`.
- Code structure: `harness/coding-style.md` plus project schemas in `harness/code-shape.md`.
- Review: `harness/code-review.md`.
- Rule ownership: `harness/instruction-governance.md`.
- Public API, database, storage, deployment, hooks, or glossary rules apply only when the matching Harness profile exists.

## Workflow

1. Intake: goal, acceptance criteria, non-goals.
2. Context: repository facts, current branch/worktree, relevant owners and failures.
3. Size & Risk: choose solo, design, or PGE.
4. Implement: use `$tdd` for behavior; use targeted verification for non-behavior work.
5. Verify: smallest relevant command, then broader checks proportional to risk.
6. Evaluate: independent review or PGE Evaluator.
7. Close: evidence, residual risk, documentation, and human-review handoff.

## Index

- `harness/workflow-gates.md`: execution and verification gates.
- `harness/instruction-governance.md`: owner placement and Harness evolution.
- `harness/coding-style.md`: universal code decisions and detected repository facts.
- `harness/code-shape.md`: project-grown positive/negative schemas.
- `harness/code-review.md`: review order, severity, and conclusions.
- `harness/pge-protocol.md`: PGE state machine and artifacts.
- `harness/failures.md`: real failures and learned rules.
- `docs/pge/`: Sprint Contracts and Evaluator reports.
