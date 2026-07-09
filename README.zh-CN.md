# skills-develop

<p align="center"><em>面向 agent 的开发类 skill。不要放学习笔记，也不要放参考库。</em></p>

<p align="center">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
  <img alt="Agent Skills Standard" src="https://img.shields.io/badge/Agent%20Skills-Standard-6DA544?style=for-the-badge">
  <img alt="skills.sh Compatible" src="https://img.shields.io/badge/skills.sh-Compatible-1E6FFF?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Claude%20Code%20·%20Codex%20·%20Cursor-8A2BE2?style=for-the-badge">
</p>

<p align="center"><strong>这个仓库只放 agent 应该发现并执行的开发类 skill。</strong></p>

中文 | [English](README.md)

* * *

## 放这里

- 会改变代码、测试、配置、文档或目录结构的工作流
- 帮助 agent 做规划、诊断、评审、分诊、交付的 skill
- 需要长期保持可发现的工程流程

## 不放这里

- 学习笔记和教学材料
- 个人参考档案
- 外部一次性安装品

## 安装

### 项目级

装到当前仓库。

```bash
npx skills@latest add YangZhaoWeblog/skills-develop -y
```

### 全局级

装到你的用户空间。

```bash
npx skills@latest add YangZhaoWeblog/skills-develop -g -y
```

`npx skills add` 默认是项目级，`-g` 会切换成用户级安装。

### 单个 skill

只安装仓库里的一个 skill：

```bash
npx skills@latest add YangZhaoWeblog/skills-develop --skill harness-init -y
```

只安装一个本地 skill 目录：

```bash
npx skills@latest add /Users/yangzhao/Code/skills-develop/skills/engineering/harness-init -y
```

不安装，直接生成单个 skill 的使用 prompt：

```bash
npx skills@latest use YangZhaoWeblog/skills-develop@harness-init
```

把 `harness-init` 或本地路径换成目标 skill；要全局安装这个单个 skill 时加 `-g`。

* * *

## Skill

| Skill | 作用 |
| --- | --- |
| `harness-init` | 生成精炼、可演进的 AGENTS.md 与 harness/ 基线。 |
| `harness-score` | 审视现有 harness，并输出离线 HTML 评分报告。 |
| `pge-workflow` | 编排 PGE 分流、Challenge Gate、Generator/Evaluator 分工、fallback 记录与并行派发。 |

## 目录

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

兄弟仓库：

- [skills-learning](../skills-learning/README.zh-CN.md)
- [skills-common](../skills-common/README.zh-CN.md)
