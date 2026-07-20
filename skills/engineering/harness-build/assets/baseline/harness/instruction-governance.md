# Instruction Governance

> status: active
> owner: instruction-governance
> layer: universal
> This file owns rule placement and harness evolution; it does not own execution gates.

## Placement Rules

- Put high-frequency hard constraints and workflow routing in `AGENTS.md`.
- Put topic rules in focused `harness/*.md` files.
- Put task-specific plans in project docs, not permanent harness.
- Put real incidents and lessons in `failures.md`.

## Layers

- `universal`: cross-project execution and governance.
- `profile`: activated by project type or stack.
- `project-grown`: local rules proven by this project after real feedback.

## Good Pattern

- Short entrypoint.
- One owner per rule.
- Topic files with narrow scope.
- Failures recorded before abstracting new rules.
- Tables only when they reduce reading cost.

## Bad Pattern

- Adding every new rule to `AGENTS.md`.
- Copying the same rule across files.
- Keeping vague slogans without triggers or actions.
- Letting examples become longer than rules.

## Maintenance

When a harness file grows too large or starts owning multiple topics, split by owner rather than adding more sections.

## Plan Mode Workflow Check

Before outputting `<proposed_plan>`, complete a light workflow check: Intake, Context, Size & Risk, Path, and Verify.

If the plan touches medium+ work, PGE, hooks, commits, cross-repository sync, or harness governance, state which workflow path is used and why full PGE is or is not required.

## Hard-Blocking Clarification

Hard-blocking clarification is only for questions where safe progress is impossible without the answer. It does not own design exploration, PGE planning, or review.

- When clear, write `硬阻塞澄清：无硬阻塞` and continue.
- When uncertainty can be handled by a low-risk assumption, state the assumption and continue with reversible work.
- When continuing would be high-risk or irreversible, stop and ask only the required user question.

When the user explicitly requests analysis only or says not to implement, keep the target repository read-only. Planning artifacts may be written only when the user authorizes that planning output and the active workflow permits it.

## Confirmation And Human Start

- Ordinary short acknowledgements such as “ok” or “continue” advance the current discussion step; they do not create unrelated write authority.
- A short reply may approve PGE Human Start only when it directly answers an explicit question asking whether implementation should begin for the visible current-revision Implement Plan.
- Grill confirmation means shared understanding was reached. It must never be reused as Human Start evidence.
- Silence, timeout, or an approval for an older Contract revision is not approval.

## Multi-Agent Activation

Evaluate multi-agent use when independent evaluation is required, slices are independently acceptable, the task spans multiple modules, or Planner / Generator / Evaluator separation is needed.

PGE tasks use `$pge-workflow` and `harness/pge-protocol.md` to decide independent agents, fallback, or parallel dispatch. Human Start is a fixed PGE confirmation and remains required under fallback. Apart from Human Start, ask the user about Agent setup only when owner acknowledgement, platform permission, extra workspace cost, or irreversible parallel code-writing is involved.
