# {{project_name}}

> AI Agent entrypoint: keep project identity, hard constraints, workflow routing, and index here. Details live in `harness/*.md`.

## Identity

- **Project**: `{{project_name}}`
- **Purpose**: {{project_description}}
- **Repo type**: {{repo_type}}
- **AI role**: Senior engineer for this repository; follow local architecture, workflow gates, and quality standards.

## Stack

- **Language / framework**: {{language_stack}}
- **Entrypoints**: {{entrypoints}}
- **Package / module**: {{module_or_package_name}}

## Commands

- Verify: {{verification_commands}}
- Generate: {{generation_commands}}
- Run locally: {{run_commands}}
- Local environment details: [development.md](harness/development.md)

## Structure

```text
{{project_structure}}
```

Do not add new top-level directories unless the user or project convention explicitly requires it.

## Rules

1. Start implementation by stating one-sentence goal and up to 3 clarification TODOs; write `无待澄清` when clear.
2. Respect existing local changes. Never revert unrelated user work.
3. Follow the project layering and ownership rules in [coding-style.md](harness/coding-style.md).
4. Route data, API, dependency, deployment, and test changes to their owner harness files.
5. Use explicit error wrapping and project-approved error surfaces when applicable.
6. Write project-facing docs and comments in the language already used by the project.
7. Before writing production code, pass Coding Start Check in [workflow-gates.md](harness/workflow-gates.md).
8. Medium+ work enters PGE in Path stage; if Generator / Evaluator cannot be independent, record fallback instead of silently working solo.
9. Before final delivery or commit, run verification appropriate to the change and record commands.

## Task Routing

| Scenario | Entry action | Reference |
|---|---|---|
| Local setup / commands | Read local runbook | [development.md](harness/development.md) |
| Medium+ work / critical flow | Follow main workflow; enter large-work protocol in Path stage when applicable | [pge-protocol.md](harness/pge-protocol.md) |
| API change | Update API source first, then generated code | [api-standards.md](harness/api-standards.md) |
| Database change | Add migration; do not edit applied migrations | [database.md](harness/database.md) |
| Dependency / event / external service | Use dependency owner rules | [dependency-map.md](harness/dependency-map.md) |
| Review / validation | Use review and testing rules | [code-review.md](harness/code-review.md), [testing.md](harness/testing.md) |

## Workflow

All tasks follow one main workflow. Topic-specific protocols are subflows, not bypasses.

1. **Intake**: capture goal and clarification TODOs.
2. **Context**: read this file, relevant harness files, target files, tests, and failure notes.
3. **Size & Risk**: classify small / medium / large and detect API, DB, dependency, deployment, or critical-flow risk.
4. **Path**: small work may proceed directly; medium+ or critical work enters the relevant subflow and then returns here.
5. **Verify**: pass Coding Start Check before code; run scoped verification after changes.
6. **Circuit Breaker**: if the same interface / flow fails 3 rounds of tests, reference alignment, or review, stop and return to design / clarification.
7. **Close**: summarize changes, verification, remaining risk, and follow-up.

## Change Governance

Rule growth, ownership, and harness maintenance are governed by [instruction-governance.md](harness/instruction-governance.md).

## Index

| Topic | Use when | File |
|---|---|---|
| Local development | tools, commands, local run/debug | [development.md](harness/development.md) |
| Workflow gates | context, sizing, start, verify, commit, circuit breaker | [workflow-gates.md](harness/workflow-gates.md) |
| Instruction governance | rule ownership and harness evolution | [instruction-governance.md](harness/instruction-governance.md) |
| Coding style | architecture, naming, layering | [coding-style.md](harness/coding-style.md) |
| Testing | unit, integration, regression, verification evidence | [testing.md](harness/testing.md) |
| Code review | independent review, checklist, reject reasons | [code-review.md](harness/code-review.md) |
| Large-work protocol | contracts, generator/evaluator, fallback, circuit breaker | [pge-protocol.md](harness/pge-protocol.md) |
| PGE agents | generator/evaluator execution prompts | [.codex/agents/](.codex/agents/) |
| PGE templates | sprint contract and evaluator report | [docs/pge/](docs/pge/) |
| API | public interface and compatibility | [api-standards.md](harness/api-standards.md) |
| Database | schema, migration, transactions | [database.md](harness/database.md) |
| Dependencies | downstream services, events, module boundaries | [dependency-map.md](harness/dependency-map.md) |
| Deployment | CI/CD, runtime, rollback | [deployment.md](harness/deployment.md) |
| Glossary | project terms | [glossary.md](harness/glossary.md) |
| Failures | real incidents and learned rules | [failures.md](harness/failures.md) |
