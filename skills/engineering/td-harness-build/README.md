# TD Harness Build

先把需求讲清楚，再让 AI 分工实现、独立验证与审阅。为项目建立 **协作入口、项目文档和任务模板**，新项目从想法开始，已有项目可直接接入或升级。

## 一、开始使用

按[仓库首页](../../../README.md)安装后，在目标项目目录调用：

```text
$td-harness-build
```

**新项目**可以在命令后说出想法，例如“我想做一个 Obsidian 插件”。AI 先帮你梳理需求、比较方案，你确认后再建立最小工程，接入规则和检查。

**已有项目**直接调用即可。AI 检查现状，复用已有工具与命令，保留代码、有效规则和未完成任务；有冲突时交你决定。

只想预览改动，补充“先检查，不改文件”。接入过程不自动提交、推送或发布。

## 二、开发怎么走

产品讨论按 **Clarify → Design → Confirm** 推进：明确问题、比较方案，再确认需求与验收条件（Acceptance Criteria，AC）。只做产品设计时，到这里结束；继续开发则进入下图的流程，**方案获批再实现，用户验收并授权后再提交**。

[![开发 Workflow 与反馈闭环](assets/workflow-feedback.svg)](assets/workflow-feedback.svg)

<p align="center"><sub>点击图片查看大图。图中列出常见路径，主 Agent 按问题原因、影响和授权安排返工。</sub></p>

与你对话的 **主 Agent** 负责规划和编排，无需另建；**Coder、Verifier、Reviewer、Executor** 独立承担实现、验证、审阅和文档／提交工作。[查看角色职责](assets/project/agent-roles.md)。

接入完成后，直接告诉 AI 下一项需求即可，**不必为每个功能重新 Build**。

## 三、完成与续做

AI 会核验接入结果，并明确报告当前状态：

| 反馈 | 意味着什么 |
|---|---|
| **初始化／升级已完成** | 方向与技术栈已确定；运行、必要检查和适用 Hook 可用，四角色已实际调用核验，产物通过独立审阅 |
| **初始化／升级未完成** | 仍有必要条件未就绪；AI 会说明已完成内容、缺口、影响和下一步 |

未完成时，需求、AC 和已确认选型会保存在项目文档中。**换会话后再次调用，也能接着补齐**，不用复制上一会话。

<details>
<summary><strong>深入了解：规则、模板与接入方式</strong></summary>

| 需要了解什么 | 入口 |
|---|---|
| Skill 执行规则与完整完成条件 | [SKILL.md](SKILL.md) |
| 旧内容保留、升级与冲突处理 | [模板融合规则](references/upgrade-project.md) |
| 多 Agent 初始化顺序、专题职责与读写范围 | [独立初始化派发](references/init-agents.md) |
| 项目事实填充与检查命令接入 | [文档生成指导](references/populate-project.md) |
| 原生 Agent 安装与核验 | [接入说明](references/agent-setup.md) · [角色职责](assets/project/agent-roles.md) |
| 阶段定义、批准条件和反馈规则 | [AGENTS 模板](assets/agents.md) |

</details>
