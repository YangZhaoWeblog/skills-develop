---
name: td-harness-build
description: 为 AI Coding 项目初始化、迁移或升级协作规则、项目文档和开发任务模板。当前实现基于 Git。
---

# TD Harness Build

为 AI Coding 项目建立可复用的 Harness。先复制模板，再填项目事实；保留项目规则和历史，不让 AI 每次重新设计骨架。

## 使用入口

裸调用时，先检查当前目录，默认初始化、补缺或升级当前项目。目标明确且无冲突的操作直接执行；目录包含多个独立项目、位于用户主目录或目标不明时，先确认位置。用户只要求检查或预览时，不写文件。

| 起点 | 如何推进 |
|---|---|
| 空项目，尚无需求或技术栈 | 引导用户说明要解决的问题，复用产品 Clarify；明确足以支持选型的目标，推荐并确认技术栈。获准后建立最小工程，再接入 Harness 与检查 |
| 已有需求或原型，尚无代码 | 核对目标和约束，不把外部资料自动当作已确认需求；确认技术方案和最小工程范围后接入 |
| 已有代码或 Harness | 核实现状，保留代码、有效规则、工具与未完成任务；补缺或按授权升级 |
| 再次调用 | 核对当前文件、配置和执行结果，续做缺口；已有记录仅作线索，不重置有效成果或重复询问 |

**跨会话交接**：产品讨论和 Build 可以分会话进行。需求与 AC 保存在本轮产品文档；已确认的技术选型记入 **.harness/docs/architecture.md §6「技术选型与设计决策」**，注明尚未落地的部分，不把选型写成已实现架构。当前产品 Overview 只链接相关决策与剩余阻塞，不复制内容。

再次调用时，沿项目 AGENTS 的恢复规则定位本轮产品文档，读取已确认内容和选型依据，核对工程及工具现状后续做。目标不明才询问，不要求用户复制上一会话。产品 Confirm 不代表 Build 完成；完成接入后回到当前开发任务的 Clarify，保留任务进度与独立核验。

**先查再问**：项目中能查到的自行核对；普通实现细节自行处理。影响产品方向、技术栈或授权的决定，给出推荐与理由，将同批已知问题集中询问。只问影响当前接入的问题；新问题须有新的依据。用户暂不能决定时，说明阻塞并报告未完成，不反复追问。

技术栈未定时可以先复制通用骨架，但不能报告接入完成。最小工程只建立运行与检查基础，不实现业务功能；涉及工程创建、Git 初始化或安装工具时核对授权，不擅自创建远端、提交或发布。

## 工作流

1. 读取目标项目的 AGENTS、Harness、Git 状态、分支及已有规则。多项目仓库先确定目标目录。
2. 按 [upgrade-project.md](references/upgrade-project.md) 判断文件归属和修改边界。需要确认的迁移整批列出；获准后连续执行，出现新的越界操作才停止。
3. 按 [独立初始化派发](references/init-agents.md) 先派只读能力探测 Agent，核对 API 和持久化证据；探测失败先解决缺口，不用默认值冒充结果。成功后使用 `scripts/build_harness.sh` 复制缺失骨架、更新工作流模板及 AGENTS 的标准 Workflow 章。运行前先保留该章中的项目独有规则，按升级规则迁入 Rules；脚本不负责语义融合；迁移遇到 `[CONFIRM]` 时，获准后用 `--accept-migrations` 重跑。
4. 依次派 [入口](references/init-agent-entry.md)、[架构](references/init-agent-architecture.md) 初始化 Agent，按 upgrade-project.md 融合并核对项目规则及结构。AGENTS 作为统一入口；按实际平台连接入口，保留已有内容，冲突交用户决定。
5. 按 init-agents.md 派发适用专题：独立任务并行，有依赖则等待；主控统一核对事实和索引。各 Agent 按 [文档生成指导](references/populate-project.md) 填项目事实；每个 Harness 必须包含术语表 `glossary.md`。空项目、局部更新及平台限制按派发规则处理，缺工具或环境明确报告。
6. 按 [检查命令接入](references/populate-project.md#接入检查命令) 固定项目命令并验证，再运行 `scripts/setup_hooks.sh` 启用 Git hooks。未配置的检查只准备脚本、不启用；已有 Hook、core.hooksPath 和项目脚本按授权融合，不覆盖。
7. 按 [原生 Agent 接入](references/agent-setup.md) 配置并核验 Coder、Verifier、Reviewer、Executor；主 Session 保留规划与编排。职责在项目 .harness/agents.md 维护，平台配置绑定实际模型与权限。
8. 项目融合结束后，以本次已确认的能力参数重跑 `scripts/build_harness.sh`，恢复标准 Workflow、同步模板；`[MERGE]` 缺口先处理，再派未参与本轮生成的独立 **Reviewer**，按 [交付审阅](references/upgrade-project.md#5-独立交付审阅) 核对最终产物与验证证据；主控修正后复审，再按下方“完成与反馈”报告结论。

## 完成与反馈

只有以下条件全部满足，才报告 **“Harness 初始化／升级已完成”**：

- 项目方向、技术栈和运行方式已明确，适用的最小工程与 Git 基础已就绪。
- 规则、模板与项目事实已适配，引用有效，没有影响当前开发的关键占位或未决冲突；最终产物已通过独立交付审阅。
- 当前开发必需的运行、构建、测试与静态检查入口可用；适用 Hook 按约定生效。确实不适用的项说明依据，缺工具或未执行不能算不适用。
- 四个独立角色已通过当前平台实际调用核验；模型、权限及尚需重载的状态如实记录。
- 检查入口已用通过、失败样例验证，相关错误能被发现；项目已有内容与历史保留。历史告警与接入故障按 [检查命令接入](references/populate-project.md#接入检查命令) 分开处理。

缺少必要条件就报告 **“初始化／升级未完成”**，列明已完成内容、缺口、影响及下一步。用户决定暂缓必要接入时仍为未完成。未来发布、尚未涉及的集成环境等可按实际需求后续补充，不要求提前建设。

每次结束都在用户可见回复中给出结论；不能仅藏在工具日志中。成功退出或复制成功不等于完整接入。只做预览时说明“仅检查，未执行初始化／升级”。

不强制新增状态文件。难以从项目重建的决定或阻塞原因，可简记在已有记录或交接文件中；再次执行先核对事实，再继续缺口。

## Workflow（工作流）

### 产品工作流

| # | 步骤 | 产物 | 说明 |
|---|---|---|---|
| 01 | Clarify（澄清） | `01-requirements.md` §1 | 明确问题、目标与范围；用户确认要解决的问题 |
| 02 | Design（方案设计） | `01-requirements.md` §2及原型引用 | 比较方案，按需用原型验证；用户选定方案，关键疑问已解决 |
| 03 | Confirm（确认） | `01-requirements.md` §4、`02-acceptance-criteria.md` | 确认需求与验收条件（Acceptance Criteria，AC）；无影响目标或验收成立的待定项 |

AI 将想法或外部资料整理为 Overview、Requirements 和 AC。外部链接在 Overview 追溯，缺口或冲突交用户确认；开发使用本轮已确认文档。产品 Overview 管本轮安排，各开发任务管自己的进度。只做产品设计时，Confirm 后结束。

### 开发工作流

| # | 步骤 | 产物 | 说明 |
|---|---|---|---|
| 01 | Clarify（澄清） | `01-clarify.md` | 独立核验需求、AC 与实施条件，必要时确认任务拆分；无硬阻塞 |
| 02 | Plan（计划） | `02-plan.md` | 列改动文件，设计测试和验收测试（Acceptance Test，AT），选定检查；用户批准方案与范围 |
| 03 | Implement（实现） | `03-implement.md` | 按计划逐行为红绿循环，获取早期反馈；完成本次实现 |
| 04 | Verify（检查） | `04-verify.md` | 执行适用检查与 AT，记录失败和复验；必要检查通过或例外明确获准 |
| 05 | Docs（文档更新） | `05-docs.md` | 更新受影响的长期事实；无变化则说明不涉及 |
| 06 | Review（独立验收） | `06-review.md` | 独立核对需求、规则和证据，修正复验后复盘；人工确认最终版本 |
| 07 | Submit（提交） | `07-submit.md` | 按授权执行 commit、push 或 PR，报告实际结果 |

产品 Clarify 明确问题，开发 Clarify 独立核验当前任务；产品确认不替代开发核验。开发的主要确认点是 Plan 批准和最终验收/提交授权；范围内连续推进，停止条件见 [AGENTS 模板](assets/agents.md)。

所有开发任务共用一套模板，按行为、范围和风险选择内容与检查；原型按实际不确定性选用。部署作为 Verify 的环境准备，优先复用 CI/CD；必要检查缺环境仍是阻塞。

## 边界

- 修改限于本次获准的 Harness、模板、配置及初始化最小工程；不借接入之名改动业务功能，也不执行未授权的提交或发布。
- 升级按 upgrade-project.md 保护项目内容和历史任务，规则冲突由用户决定。
- 技术栈未定的空项目可先建骨架。事实待定就标明，写生产代码前补齐技术方案和验证入口。
- 模板提供通用流程；项目集成按实际需要接入。

## 按需读取

只读取当前工作需要的材料；专题文档入口集中在文档生成指导中。

| 当前工作 | 读取 |
|---|---|
| 融合旧内容、处理迁移或多项目归属 | [upgrade-project.md](references/upgrade-project.md) |
| 初始化、升级或首次补齐项目文档，派发独立专题 Agent | [init-agents.md](references/init-agents.md) |
| 填项目文档、统一术语、接入检查命令 | [populate-project.md](references/populate-project.md) |
| 接入平台原生角色、核对模型与权限 | [agent-setup.md](references/agent-setup.md) |
| 探测 API 和持久化能力 | [init-agent-detect.md](references/init-agent-detect.md) |
| 产品澄清或开发独立核验 | [clarify.md](assets/project/docs/clarify.md)，按产品或开发部分读取 |
| 设计行为改动的单元测试（Unit Test，UT） | [tdd.md](assets/project/docs/testing/tdd.md) |
| 选择检查、处理失败及判断复验范围 | [verification.md](assets/project/docs/verification.md) |
| 确认项目实际使用 go-zero | [framework-gozero.md](references/framework-gozero.md) |
| 识别到库项目 | [library-context.md](references/library-context.md) |

## 模板与脚本

- `assets/agents.md` 生成项目入口；`assets/project/` 复制到 `.harness/`，包含澄清与 TDD 方法。
- `assets/workflows/development/`、`assets/workflows/product/` 分别复制到 `.harness/templates/development/`、`.harness/templates/product/`。
- `assets/.golangci.yml` 是可选 Go 检查配置，接入前核对项目现有规则。
- `scripts/configure_agents.py` 按已确认参数生成原生 Agent 配置；模板在 `assets/native-agents/`，实际调用另行核验。
- `scripts/build_harness.sh` 准备骨架并更新标准 Workflow 与模板；`scripts/setup_hooks.sh` 安装 hooks。`pre_commit_check.sh`、`pre_push_check.sh`、`commit_msg_check.sh` 分别检查提交前质量、推送前质量和提交消息。
