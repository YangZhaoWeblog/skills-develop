---
name: harness-score
description: Review an existing AI agent harness and produce an offline HTML score report. Use when a user asks to score, audit, review, compare, or assess AGENTS.md and harness/*.md quality, workflow integrity, gates, governance, specificity, and instruction clarity.
---

# Harness Score

Use this skill to perform a read-only harness review and render a single-file HTML report that humans can share and discuss.

## Workflow

1. **Scan**
   Read `AGENTS.md`, `harness/*.md`, relevant `.agents/` or `.codex/` files, and project files needed to verify project specificity.

2. **Profile**
   Identify repo type, language stack, API/DB/deployment signals, existing workflow model, and whether PGE or large-work controls are applicable.

3. **Score**
   Apply [references/rubric.md](references/rubric.md) and [references/dimensions.md](references/dimensions.md). Every non-empty score must cite evidence.

4. **Render HTML**
   Create `harness-score-<project>-<timestamp>.html` using [templates/harness-score-report.html](templates/harness-score-report.html).

5. **Report**
   Summarize the output path, health level, top risks, and top next actions. Do not modify the target project.

## Boundaries

Allowed:
- Score existing harness quality.
- Explain findings with file/line evidence.
- Give migration recommendation level: `none`, `light`, `moderate`, `major`.
- List 1-3 next actions and candidate strengths for human discussion.

Not allowed:
- Modify target repository files.
- Generate patch plans or perform automatic migration.
- Treat the baseline as superior to local project rules.
- Produce cross-project ranking from raw totals.

## Output Contract

The HTML report must be offline, single-file, and contain stable section IDs:

- `summary`
- `project-profile`
- `dimension-scores`
- `findings`
- `migration-recommendation`
- `candidate-strengths`
- `open-questions`
- `verification`
- `embedded-json`

Do not output a pseudo-precise total score. Use health levels:

- `Healthy`
- `Needs Attention`
- `At Risk`
- `Incomplete`
