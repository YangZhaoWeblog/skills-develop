# skills-develop

中文 | [English](README.md)

这个仓库只放可以被 agent 直接调用的开发类 skill。

## 规则

- 只保留应该被 agent 发现和执行的工作流。
- 不要把学习笔记、知识材料、个人参考库放在这里。
- 学习内容放 `skills-learning`，可复用的通用 skill 放 `skills-common`。
- 使用 `npx skills add <repo-or-path>` 安装时，明确选择项目级或全局级。

## 目录

- `skills/engineering/`
- `skills/productivity/`
- `skills/shared/`

兄弟仓库：

- [skills-learning](../skills-learning/README.zh-CN.md)
- [skills-common](../skills-common/README.zh-CN.md)

## 安装

项目级安装，适合只在当前仓库生效：

```bash
npx skills add /Users/yangzhao/Code/skills-develop --agent claude-code --agent codex -y
```

全局安装，适合所有项目都可用：

```bash
npx skills add /Users/yangzhao/Code/skills-develop --agent claude-code --agent codex -g -y
```

`npx skills add` 默认是项目级，`-g` 会切换成用户级安装。
