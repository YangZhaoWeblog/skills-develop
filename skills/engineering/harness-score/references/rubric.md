# Harness Score Rubric

Use evidence-bound scoring. Unknown facts do not become high scores.

## Scale

- `5`: Clear, executable, evidenced, and matched to project context.
- `4`: Mostly complete with minor TODOs or ambiguity.
- `3`: Present but scattered, duplicated, or weakly evidenced.
- `2`: Slogan-level guidance; execution path is unstable.
- `1`: Nearly absent; depends on conversation memory.
- `0`: Conflicts with project facts or induces wrong behavior.
- `-`: `not_applicable` or `unknown`.

## Applicability

- `applicable`: score the dimension.
- `not_applicable`: do not score; explain why.
- `unknown`: do not score; add an open question.

## Health Level

- `Healthy`: no critical issue, most applicable dimensions score 4-5, next actions are minor.
- `Needs Attention`: no immediate failure, but one or more dimensions need focused repair.
- `At Risk`: workflow, gates, ownership, or review rules can cause wrong execution.
- `Incomplete`: missing enough harness structure that scoring is mostly blocked.

## Required Evidence

Each scored dimension must cite files, line numbers when practical, and concrete behavior. Do not award `4` or `5` without evidence.
