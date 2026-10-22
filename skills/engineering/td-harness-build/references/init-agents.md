# 多 Agent 独立初始化

初始化、升级或首次补齐项目文档时，主 Agent 按本文件派发。各专题使用独立上下文；提示词为 **init-agent-*.md**，产物仍写入项目 **AGENTS.md** 与 **.harness/docs/**。

## 1. 执行顺序

1. **探测**：先派只读 Agent 执行 [能力探测](init-agent-detect.md)。主 Agent 核对证据，取得 **HAS_API / HAS_DB** 后运行构建脚本；未知或探测失败先解决缺口。
2. **入口 → 架构**：骨架就绪后，依次派 [入口 Agent](init-agent-entry.md)、[架构 Agent](init-agent-architecture.md)。主 Agent 读取并核对两份产物，确认项目规则及结构，再交给专题 Agent 使用。入口索引此时只引用实际已有文件，最终由主 Agent 收口。
3. **专题初始化**：按下表派发本次适用的专题；相互独立、写入范围不交叉的任务并行。依赖的产物尚未完成核验时先等待，按平台并发上限分批，不要求同时启动全部角色。
4. **汇总**：全部返回后，主 Agent 核对事实、项目内容保留、跨文档引用、命令归属和索引，处理冲突；汇总各专题结果与缺口，再继续 Hook 和原生开发角色接入。

已有项目初始化或首次补齐时，适用专题使用独立 Agent。空项目无代码时，入口由主 Agent 填明现状，其余专题只保留骨架和缺口，不派 Agent 编造内容。单专题升级或 **05 Docs** 增量维护可直接复用专题指令，不为局部改动重跑整批。

平台不支持独立 Agent，或项目限制子 Agent 写入时，如实说明：能独立读取的返回事实与候选内容，由主 Agent 按相同边界写入；无法独立执行的项报告未完成或由用户决定串行替代，不把主 Agent 自检称为多 Agent 初始化。

## 2. 派发约定

主 Agent 为每个 Agent 指定 **项目与 Skill 的绝对路径、专题指令、原模板、相关证据、唯一负责的文件、允许的操作及结束条件**。按阶段附前置产物：探测读取项目事实；入口读取已有规则及探测结果；架构再读取已核验入口；专题再读取已核验入口和架构。已有文件附其内容归属、允许更新区域和迁移授权。共享命令或配置的取舍由主 Agent 确定，不由多个 Agent 各写一套。

**按操作选择 Agent**：探测用只读角色；直接填文件须用具备写入能力的角色，不能把只读 Explore／Plan 角色当作写入者。只有只读子 Agent 可用时，按上方平台限制处理。

**每个文件只分配一个写入者。** Agent 只处理分配的文件，完整读取原文，按 [升级规则](upgrade-project.md) 保留人工内容、项目区和历史；不可回退其他 Agent 的改动。需要更新其他文件时返回位置、依据及建议，由主 Agent 协调，不越界写入。现有同职责角色可复用，但每个专题使用独立上下文，不继承其他专题的完整对话。

有写入权限的 Agent 在授权范围内按模板填写文档；只读 Agent 返回事实与候选内容。**文档初始化不授予修改源码、契约、Schema、项目配置、安装工具、连接真实数据或发布的权限。** 专题发现这些缺口时报告主 Agent，相关操作另按既有授权推进。

每个 Agent 返回 **负责文件、已处理内容、依据路径、实际核验结果及剩余缺口**，结论为 **已完成／部分完成／不适用／阻塞**。不适用须有证据，不能因此删除已有文档；读取失败不能当作不存在。主 Agent 核对后再确认结果，写入成功不等于 Build 接入完成。

## 3. 专题与依赖

下表路径相对项目 **.harness/docs/**；**AGENTS.md** 位于项目入口。仅派发本次需要生成或更新的专题；迁移涉及额外旧文件时，由主 Agent 明确追加其唯一负责人。

| 独立 Agent 指令 | 负责产物 | 启动条件／依赖 |
|---|---|---|
| [init-agent-entry.md](init-agent-entry.md) | 项目 **AGENTS.md** | 主 Agent 确认目标、已有规则和修改边界；专题结束后主 Agent 再核对索引 |
| [init-agent-architecture.md](init-agent-architecture.md) | **architecture.md** | 入口核对完成；有代码或已确认的技术方案，未实现部分明确标记 |
| [init-agent-product.md](init-agent-product.md) | **product-state/** | 有现状依据；不代替用户确认新需求与 AC |
| [init-agent-dependencies.md](init-agent-dependencies.md) | **dependencies.md** | 入口、架构已核对；依据真实调用与集成 |
| [init-agent-contracts.md](init-agent-contracts.md) | **contracts/** | **HAS_API=true**；字段定义引用实际契约 |
| [init-agent-data.md](init-agent-data.md) | **data/database.md** | **HAS_DB=true**；结构定义引用权威来源 |
| [init-agent-coding-style.md](init-agent-coding-style.md) | **coding-style.md** | 已知语言、项目配置和工具证据；不修改工具配置 |
| [init-agent-testing.md](init-agent-testing.md) | **testing/unit-tests.md** | 有代码及测试工具证据；工具缺失如实记录 |
| [init-agent-logging.md](init-agent-logging.md) | **logging.md** | 有日志机制或已有项目说明 |
| [init-agent-devops.md](init-agent-devops.md) | **devops/** | 读取已核验的测试、日志入口；未建立发布方式只说明现状 |
| [init-agent-integration-test.md](init-agent-integration-test.md) | **testing/integration-test.md** | 依赖、运行与测试入口已核对；无 IT 时只登记未接入 |
| [init-agent-code-review.md](init-agent-code-review.md) | **code-review.md** | 编码、测试及项目门禁已核对；不另维护命令或阈值 |
| [init-agent-glossary.md](init-agent-glossary.md) | **glossary.md** | 每个 Harness 必备；无有效术语时写“暂无” |
| [init-agent-failures.md](init-agent-failures.md) | **failures.md** | 仅使用已授权的相关历史；无证据时不编造记录 |

初始化 Agent 是本轮文档任务，不要求为各专题安装永久原生角色。后续开发的 **Coder / Verifier / Reviewer / Executor** 按 [agent-setup.md](agent-setup.md) 另行接入与核验。
