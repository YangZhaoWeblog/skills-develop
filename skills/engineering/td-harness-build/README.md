# TD Harness Build

<p align="center"><em>从一个想法，或一个已有项目，开始有依据、可验证的 AI 开发。</em></p>

<p align="center">
  <img alt="Template First" src="https://img.shields.io/badge/Templates-Copy%20First-6DA544?style=for-the-badge">
  <img alt="Project Aware" src="https://img.shields.io/badge/Harness-Project%20Aware-1E6FFF?style=for-the-badge">
  <img alt="Verified Setup" src="https://img.shields.io/badge/Setup-Verify%20Before%20Done-8A2BE2?style=for-the-badge">
</p>

<p align="center"><strong>先明确目标，再适配规则与工具。能用、验证过，才算接入完成。</strong></p>

<p align="center">
  <a href="#一如何使用">如何使用</a> ·
  <a href="#二完成与续做">完成与续做</a> ·
  <a href="#三接入后如何开发">后续开发</a>
</p>

---

## 一、如何使用

安装本 Skill 后，在目标项目目录按下面的场景调用，替换成你自己的项目描述。也可以只输入 **$td-harness-build**，让 AI 先检查现状；位置或必要信息不明确时，它会询问。

### 空项目：从想法开始

```text
$td-harness-build 我想做一个 Obsidian 插件，但还没想清楚具体功能，
技术栈也没定。先带我梳理第一版需求，再确认技术方案和初始化范围。
```

AI 先用产品 Clarify 帮你明确问题与目标，再推荐技术方案。你确认后，它建立最小工程，适配 Harness 并接入必要检查。暂时连方向都没有也可以先讨论，不要求预先写好需求文档。

**产品讨论可以先用，完整接入要等验证通过。** 最小工程只准备开发基础，不实现第一版业务功能；技术栈或必要检查未就绪时，明确报告“初始化未完成”。

### 已有项目：接入或升级

```text
$td-harness-build 为当前项目接入或升级 Harness。
保留已有代码、规则和未完成任务，复用现有检查命令；冲突集中列给我。
```

AI 核实现有工程：没有 Harness 就接入，已有则补缺或升级。沿用有效工具与命令，验证项目内容保留及检查实际生效；不因接入而重构业务代码。

项目里能查到的信息由 AI 查。涉及关键选择时，它给出推荐与理由；创建工程、安装工具及迁移按已批准范围执行。初始化不自动提交、推送或发布。

## 二、完成与续做

**已完成**意味着：项目方向与技术栈明确，规则和模板已适配，当前开发必需的入口已验证，适用的 Hook 按约定生效，四个独立 Agent 已实际调用核验。

> **Harness 初始化已完成。**
> 项目规则、运行入口与必要检查已验证。下一步可按开发 Workflow 核验并计划第一轮任务。

**未完成**时，AI 必须告诉你已完成什么、还缺什么、影响是什么，以及下一步。复制文件成功不能替代这个判断。

> **Harness 初始化未完成。**
> 产品澄清已可使用；技术栈尚未确认，开发检查尚未接入。
> 下一步：确认第一版目标与技术方案，再完成工程和工具接入。

**跨会话也能续做。** 产品讨论的需求、验收条件（Acceptance Criteria，AC）与已确认选型保存在项目文档中。新会话再次调用同一个 Skill，AI 会核对现状，从缺口继续，无需复制上一会话；已有成果保留，难以重新查出的决定或阻塞原因按需简记。

未来发布安排、尚未涉及的集成环境等，可以随项目需要补充。**当前开发必需的工具或验证缺失，仍须报告未完成。**

## 三、接入后如何开发

**Build 完成的是协作环境。** 产品讨论与开发任务使用 Harness 提供的 Workflow，可以在后续会话继续；不需要每做一个功能都重新运行 Build。

| 部分 | 负责什么 | 完成边界 |
|---|---|---|
| **Harness Build** | 建立、适配和验证项目协作环境 | 当前所需规则与工具可用 |
| **产品 Workflow** | Clarify → Design → Confirm | 用户确认本轮需求与 AC |
| **开发 Workflow** | Clarify → Plan → Implement → Verify → Docs → Review → Submit | 在授权范围内完成本轮实现、验证与交付 |

**Agent 分工**：强主控负责澄清、计划和编排；经济模型的 Coder 实现、Executor 更新文档及执行获准提交；强模型的 Verifier 和 Reviewer 分别独立验证、审查。Build 按你使用的平台接入原生角色，不另装调度器。

一个需求可以对应多个开发任务；开发仍需独立核验需求与 AC，已有产品确认不能代替开发 Clarify。

完成接入后，可以这样继续：

```text
继续这个项目。读取当前 Harness 和已确认的产品文档，
进入开发 Clarify，核验第一轮任务的范围与验收条件。
```

## 四、支持范围与文档入口

当前实现基于 **Git**。检查工具参考覆盖 **Go、JavaScript / TypeScript、Python**；其他语言先核对已有工具与缺口，不套用 Go 配置。

**确定性工具优先**：模板通过复制建立，机械代码优先由已有工具生成；项目检查命令在接入时选定，执行时不临时换工具。未配置的 Hook 不自动启用，已有 Hook 与项目脚本按授权保留或融合。

**多 Agent 初始化**：先核对入口与架构，再让独立 Agent 按专题填充适用文档；无写入权限时返回候选，由主控写入并统一核对。空项目不派整批 Agent 填写不存在的事实。

<details>
<summary><strong>查看规则、模板与工具参考</strong></summary>

| 需要了解什么 | 入口 |
|---|---|
| Skill 执行规则与完整完成条件 | [SKILL.md](SKILL.md) |
| 旧内容保留、升级与冲突处理 | [模板融合规则](references/upgrade-project.md) |
| 多 Agent 初始化顺序、专题职责与读写范围 | [独立初始化派发](references/init-agents.md) |
| 项目事实填充与检查命令接入 | [文档生成指导](references/populate-project.md) |
| Go / JS、TS / Python 工具参考 | [Go](references/language-profiles/go.md) · [JS / TS](references/language-profiles/javascript-typescript.md) · [Python](references/language-profiles/python.md) |
| 原生 Agent 安装与核验 | [接入说明](references/agent-setup.md) · [角色职责](assets/project/agent-roles.md) |
| 生成后的项目协作入口 | [AGENTS 模板](assets/agents.md) |

</details>

<details>
<summary><strong>可选：只检查差异，不修改文件</strong></summary>

在默认调用后补充限制即可：

```text
$td-harness-build 只检查当前项目，说明需要补充或修改什么，先不要改文件。
```

</details>
