# skills-develop

English | [中文](README.zh-CN.md)

This repository contains agent-callable skills for development work.

## Rules

- Keep only workflows that should be discoverable by agents.
- Do not place learning notes, study material, or personal reference archives here.
- Put learning content in `skills-learning` and shared reusable skills in `skills-common`.
- Install with `npx skills add <repo-or-path>` and choose project or global scope explicitly.

## Layout

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

Sibling repos:

- [skills-learning](../skills-learning/README.md)
- [skills-common](../skills-common/README.md)

## Install

Use project scope for repo-local installs:

```bash
npx skills add /Users/yangzhao/Code/skills-develop --agent claude-code --agent codex -y
```

Use global scope when you want the skills available across all projects:

```bash
npx skills add /Users/yangzhao/Code/skills-develop --agent claude-code --agent codex -g -y
```

Project scope is the default. `-g` switches to user-level installation.
