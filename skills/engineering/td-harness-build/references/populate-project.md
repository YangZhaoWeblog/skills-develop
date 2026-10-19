# 项目文档生成与更新

> 初始化后填充项目事实、补齐现有 Harness 或执行开发工作流的 05 Docs 时读取。独立 Agent 派发顺序与读写边界见 **[init-agents.md](init-agents.md)**；本文件维护共同填写规则。

## 1. 模板与修改边界

先读 [upgrade-project.md](upgrade-project.md)。从 `assets/project/` 复制固定骨架，再填项目事实；已有文档按明确边界融合，不由 AI 另造文件结构。

开发文档按 AGENTS 的 Workflow 更新；初始化和升级按 upgrade-project.md 执行。提交和推送须有明确授权。

- skill-managed 区可以刷新；项目区、人工内容和历史保留。
- 没有明确边界的已有文件，先在升级表标为 MERGE，获准后融合。
- 架构文档仅在升级表的 OVERWRITE 项已获准时直接覆盖。
- 删除旧入口须先保留独有内容并获得相应迁移授权；未知文件不自动删。

## 2. 从真实信息源填充

| 内容 | 优先信息源 |
|---|---|
| 产品现状 | 已确认且已实现的能力、当前产品规则、有效外部资料；不把历史设想写成现状 |
| 架构与上下游 | 入口、模块、调用关系、配置和实际依赖 |
| API / 协议 | proto / IDL / OpenAPI / 路由和注释；维护索引及字段变更历史，不复制字段说明表 |
| 持久化结构 | 引用项目权威 Migration / Schema / ORM 定义，不手工维护完整结构副本；有环境且已授权时核对实际数据库 |
| 测试、编码与运行命令 | Makefile、package scripts、pyproject.toml、锁文件、CI 和项目配置 |

用 `rg --files` 定位真实文件，再读取相关内容。已有确定性生成工具优先复用；没有工具时依据源码和配置填模板，不为写文档另造抽取器或要求所有说明字节级相同。

代码事实、产品意图和待确认项分开。空项目可以先建通用骨架；尚不存在的架构、接口、依赖或环境明确待定，不编造。是否接入完成按 **[SKILL.md](../SKILL.md#完成与反馈)** 判断，骨架生成不能替代完成条件。

### 文档用语

现行文档只写当前职责与操作。淘汰方案和讨论经过留在历史记录；升级所需的兼容处理按 upgrade-project.md 执行，保留项目历史。

每份文档首次引入流程缩写时注明中文与英文全称，例如验收条件（Acceptance Criteria，AC）、验收测试（Acceptance Test，AT）、单元测试（Unit Test，UT）；后文用简称，标题与表头保留必要中文含义。

### 接入检查命令

先核对 Makefile、package.json、pyproject.toml、锁文件和 CI/lint 配置。已有入口能完成检查就保留；只为缺少的能力读取对应语言参考。

| 项目情况 | 接入方式 |
|---|---|
| 空项目，技术栈未定 | 建通用骨架，明确尚无语言检查；技术方案确认后、写生产代码前补齐 |
| 技术栈已定，缺工具或命令 | 按语言参考补兼容的默认方案，锁定版本并验证；不能因缺工具标为不适用 |
| 已有工具与入口 | 复用原命令、工作目录、参数和准备步骤，只补缺失能力；冲突按升级规则处理 |

**命令只在接入时选定，执行时不再猜。** 没有 Makefile 时使用项目已有 package scripts 或脚本，不强制新增 Makefile。项目已有统一检查入口就直接调用；没有时按已确认顺序组合已有命令，不复制工具内部逻辑。

**先记录历史基线，再判断接入是否完成。** 在业务代码未改动的版本运行检查，记录版本、命令和已有问题。新增工具发现的历史质量告警不单独阻断 Build，也不触发无关重构；输出仍记录为失败，不能称为“项目检查全部通过”。工具缺失、入口错误，以及妨碍当前开发的构建或测试故障，仍须解决或报告未完成。

新增门禁按 **verification.md §2.1** 区分历史问题与本次引入或加重的问题。优先用工具原生增量或基线能力；不支持时保留全量结果，由 **Verify** 对照变更核验，不用成功退出码掩盖失败。全量命令尚有历史失败时，不直接把它启用为新的阻断 Hook；说明缺口并确认处理方式。**已有强制门禁保持原规则**。

新建 Hook 使用现有两份脚本中的固定函数：**pre_commit_check.sh / check_formatting** 填只读格式检查，**pre_push_check.sh / run_project_checks** 填已确定的构建、Lint、测试入口。按项目工作目录填写直接命令，不用 eval，不按 PATH 切换工具，不在 Hook 运行时自动安装包。两者调用原有执行源，项目文档记录其位置、用途与范围，不另维护一套实现。

替换占位函数体后删除 **HARNESS_PROJECT_CHECKS_PENDING** 标记。无适用检查时，在函数里说明依据及后续接入条件，再明确返回成功；这表示该类检查不适用，不表示已执行测试。不得把必要检查缺失写成不适用。独立核对实际函数内容，删除标记本身不能证明接入完成。

验证通过路径与失败路径后，再运行 **setup_hooks.sh**。确认失败返回非零且后续输出不能吞掉失败；检查不修改源码、不递归调用 Git commit/push。已有 Hook 的职责划分优先保留，不另建第二套门禁。**core.hooksPath**、已有 Hook 或脚本阻止新入口启用时，报告实际状态并按授权融合；不能只因文件存在就报告“已启用”。

| 项目语言 | 读取 |
|---|---|
| Go | [go.md](language-profiles/go.md) |
| JavaScript / TypeScript | [javascript-typescript.md](language-profiles/javascript-typescript.md) |
| Python | [python.md](language-profiles/python.md) |

参考版本是已评估基线，不代表项目已安装。核对兼容性并按项目包管理方式锁定；不为检查工具升级项目语言或替换测试框架。其他语言先报告缺口与建议，再接入。

实际命令只维护一处：UT/覆盖/CRAP/变异在 `testing/unit-tests.md`，格式/静态/复杂度/重复/依赖在 `coding-style.md`。注明版本、工作目录、完整命令、范围参数和配置位置。AGENTS 索引入口，Plan 选择范围和有效标准，Verify 记录实际结果。

语言参考留在 Skill 内，不整包复制到项目。技术栈未定时先建通用骨架；开发 Clarify/Plan 确认技术方案后，在写生产代码前补齐入口。

## 3. 按职责读取参考

**init-agent-*.md** 是各专题的独立初始化指令，按 **init-agents.md** 派发。后续 **05 Docs** 增量维护也复用同一专题规则，只读取并更新本次受影响部分，不重跑全套初始化。子主题的文件结构、字段和项目事实由对应指令说明，本文件不重复维护。

| 工作 | 读取 |
|---|---|
| 产品现状、长期能力与规则 | [init-agent-product.md](init-agent-product.md) |
| 系统架构 | [init-agent-architecture.md](init-agent-architecture.md) |
| 上下游与故障传播 | [init-agent-dependencies.md](init-agent-dependencies.md) |
| 真实接口契约索引与字段历史 | [init-agent-contracts.md](init-agent-contracts.md) |
| 持久化结构 | [init-agent-data.md](init-agent-data.md) |
| 测试、覆盖、CRAP 和变异入口 | [init-agent-testing.md](init-agent-testing.md) |
| 真实依赖测试 | [init-agent-integration-test.md](init-agent-integration-test.md) |
| 环境、运行与部署 | [init-agent-runtime.md](init-agent-runtime.md) |
| 编码规则和静态检查入口 | [init-agent-coding-style.md](init-agent-coding-style.md) |
| 独立验收标准 | [init-agent-code-review.md](init-agent-code-review.md) |
| 日志、术语、失败记录 | [日志](init-agent-logging.md)、[术语](init-agent-glossary.md)、[失败](init-agent-failures.md) |
| AGENTS 索引与项目规则 | [init-agent-entry.md](init-agent-entry.md) |

长期产品文档固定为 `.harness/docs/product-state/product-map.md`、`user-flows.md`、`business-rules.md`。本轮需求与 AC 在产品任务中维护；长期文档用产品全景图、用户流程图和业务规则图表达现状；精确条件用短表或图注。图形要求见 init-agent-product.md，不复制本轮 AT 步骤和历史结果。

**术语表必建**：每个 Harness 保留 **glossary.md**；没有符合收录标准的术语时注明“暂无”，不为填满模板编造术语。

## 4. 初始化与增量更新

初始化按理解需要先建立项目定位，再补当前需要的契约、结构和运行说明。只填有证据的内容；模板复制不等于项目事实已确认。不因为骨架里有文件就要求空项目立刻写满。

05 Docs 按本次已实现的变化更新相关长期文档。只改日志措辞的任务不重写全套架构；没有文档变化时记录“不涉及”及依据。文档与代码保持同次交付，不强制另开 docs PR。

已有项目或组织规则优先保留：权威原文维护一份，其他位置只做必要摘要和链接。冲突按 upgrade-project.md 处理，不建立两份同步修改的规则。

部署由项目 CI/CD 或既有入口负责。写文档不自动授权部署、数据库访问、外部写入或发布；没有环境时说明待验证条件。

## 5. 核对与记录

核对本次改动涉及的事实，不用随机抽两篇代替检查：

- 接口名、字段注释、默认值、兼容性及历史依据与真实契约一致。
- 命令确实存在；可执行且已授权的入口实跑，缺工具或环境时写明缺口，不标通过。
- 固定命令、数值门槛和结果各有唯一维护位置：测试/编码规范、verification.md、本次 04-verify.md。
- 项目内容和历史未丢失；按 [AGENTS 生成指导](init-agent-entry.md) 完成主题索引填充，核对实际路径及项目专属入口，修复已移除入口的引用。
- 实际扫描或核验的文档更新 Source / Last-verified，不能给未核验内容统一刷时间。

发现文档事实错误，按其来源修正；仅确定性生成的产物才修生成源并重新生成，不禁止对人工维护的说明做最小修改。

独立 Review 核对交付依据，人工在最终审阅时看当前版本；不为每个主题再加一套审批。当前任务只在 05-docs.md 记录更新范围和关键结果，Verify 与 Review 的记录分别留在对应阶段。
