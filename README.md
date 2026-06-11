# skills-develop

<p align="center"><em>Agent-facing development skills. No study notes, no reference dump.</em></p>

<p align="center">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
  <img alt="Agent Skills Standard" src="https://img.shields.io/badge/Agent%20Skills-Standard-6DA544?style=for-the-badge">
  <img alt="skills.sh Compatible" src="https://img.shields.io/badge/skills.sh-Compatible-1E6FFF?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Claude%20Code%20·%20Codex%20·%20Cursor-8A2BE2?style=for-the-badge">
</p>

<p align="center"><strong>This repository contains the skills agents should discover and execute when they are doing development work.</strong></p>

English | [中文](README.zh-CN.md)

* * *

## What belongs here

- workflows that change code, tests, config, docs, or repo structure
- skills that help agents plan, diagnose, review, triage, or ship
- reusable engineering flows that should stay discoverable

## What stays out

- learning notes and teaching material
- personal reference archives
- one-off external installs

## Install

### Project scope

Install into the current repo.

```bash
npx skills@latest add YangZhaoWeblog/skills-develop -y
```

### Global scope

Install into your user space.

```bash
npx skills@latest add YangZhaoWeblog/skills-develop -g -y
```

Project scope is the default. `-g` switches to user-level installation.

* * *

## Skills

| Skill | What it does |
| --- | --- |
| `td-harness-init` | Bootstraps the td-harness in a repo. |

## Layout

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

Sibling repos:

- [skills-learning](../skills-learning/README.md)
- [skills-common](../skills-common/README.md)

## 中文

这个仓库只放可以被 agent 直接调用的开发类 skill。

### 规则

- 只保留应该被 agent 发现和执行的工作流。
- 不要把学习笔记、知识材料、个人参考库放在这里。
- 学习内容放 `skills-learning`，可复用的通用 skill 放 `skills-common`。
- 使用 `npx skills add <repo-or-path>` 安装时，明确选择项目级或全局级。

### 目录

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

兄弟仓库：

- [skills-learning](../skills-learning/README.md)
- [skills-common](../skills-common/README.md)

### 安装

项目级安装，适合只在当前仓库生效：

```bash
npx skills add /Users/yangzhao/Code/skills-develop -y
```

全局安装，适合所有项目都可用：

```bash
npx skills add /Users/yangzhao/Code/skills-develop -g -y
```

`npx skills add` 默认是项目级，`-g` 会切换成用户级安装。
