# skills-develop

<p align="center"><em>面向 agent 的开发类 skill。</em></p>

<p align="center">
  <img alt="Agent Skills Standard" src="https://img.shields.io/badge/Agent%20Skills-Standard-6DA544?style=for-the-badge">
  <img alt="skills.sh Compatible" src="https://img.shields.io/badge/skills.sh-Compatible-1E6FFF?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Claude%20Code%20·%20Codex%20·%20Cursor-8A2BE2?style=for-the-badge">
</p>

<p align="center"><strong>这个仓库只放 agent 应该发现并执行的开发类 skill。</strong></p>

中文 | [English](README.md)

* * *

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
npx skills@latest add YangZhaoWeblog/skills-develop --skill td-harness-build -y
```

规范入口使用 `--skill td-harness-build`。

只安装一个本地 skill 目录：

```bash
npx skills@latest add ./skills/engineering/td-harness-build -y
```

不安装，直接生成单个 skill 的使用 prompt：

```bash
npx skills@latest use YangZhaoWeblog/skills-develop@td-harness-build
```

把 `td-harness-build` 或本地路径换成目标 skill；要全局安装这个单个 skill 时加 `-g`。

* * *

## Skill

| Skill | 作用 |
| --- | --- |
| [td-harness-build](skills/engineering/td-harness-build/README.zh-CN.md) | 为项目搭建或升级 AI harness：AGENTS.md、`.harness` 模板、模板优先融合、内置 TDD 方法和 Git hooks。 |
| [td-coding-retro](skills/engineering/td-coding-retro/README.zh-CN.md) | 复盘单次 AI Coding 会话，区分通用与项目改进，提炼正反例，并生成可离线阅读的 HTML 报告。 |

## 目录

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

兄弟仓库：

- [skills-learning](https://github.com/YangZhaoWeblog/skills-learning/blob/main/README.zh-CN.md)
- [skills-common](https://github.com/YangZhaoWeblog/skills-common/blob/main/README.zh-CN.md)

---

本仓库收录供 agent 长期发现与调用的开发工作流，涵盖规划、诊断、评审、分诊、交付，以及代码、测试、配置、文档和目录结构的修改。学习笔记、教学材料、个人参考档案和外部一次性安装品不在收录范围内。
