# Sub-agent 物理约束

> **来源**：圆桌 4-5（Dijkstra 钉的硬约束）+ SOP L898/L1340-1342
> **状态**：✅ 强约束（违反即 BLOCK）
> **影响 skill**：init（写入 AGENTS.md）、eval（运行时检查）

## 一句话

Sub-agent 必须无状态、文件交接、深度 ≤2、宽度 ≤5——这是 Claude Code × PGE 的物理约束，不是设计选择。

## 五条硬约束

| # | 约束 | 阈值 | 违反后果 |
|---|------|------|---------|
| 1 | 嵌套深度 | ≤2 层（主→sub→sub-sub） | spawn 爆炸、控制流不可追踪 |
| 2 | 并行宽度 | ≤5（单 message 内 Agent tool call） | API tier 限流、人类审计失能 |
| 3 | 状态性 | 必须无状态 | 短命 sub-agent 退出后状态丢失 |
| 4 | 通信模式 | 文件交接 only，禁止 SendMessage | 死收件箱（SOP 实战踩坑） |
| 5 | 创建时机 | 任何阻塞 I/O 之前完成 Team 创建 | coordinator 死后 SendMessage 无效 |

## 依据

**深度限制** —— [SOP L1340-1342](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "Anthropic 实验中出现 Agent 自行 spawn 50 个子 Agent。解法：Prompt 限制子 Agent 数量 + 嵌套深度 max depth ≤ 2-3 层。"

**宽度限制** —— [SOP L1312](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "asyncio.Semaphore(4)，API Tier 限制下并行 Haiku 上限约 4-5 个"

**通信模式** —— [SOP L898](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "短命 subagent 不能用 SendMessage。AlexAnys 踩坑记录：coordinator 在审批检查点死亡后，SendMessage 打到了死收件箱，安装永远不开始。"

## 通信模式选择表

| 场景 | 用 | 不用 |
|------|---|------|
| 跨 Phase 传递 | 文件 | SendMessage |
| 长生命周期状态 | 文件 | SendMessage |
| 短命 sub-agent 协作 | 文件 | SendMessage |
| 持久 Agent Team 内紧密协作 | SendMessage（罕见） | - |

**默认选文件**——文件交接是冷启动友好的，与 git/PROGRESS.md/DECISIONS.md 一致。

## 在 td-harness 中的内化

**init 写入 AGENTS.md Workflow 节**：
```markdown
## sub-agent 调用约束（违反即 BLOCK）
- 嵌套深度 ≤2 层
- 单 message 并行 ≤5
- 必须文件交接，不用 SendMessage
- 短命 sub-agent 退出后状态写入 .pge/ 或 .harness/
```

**eval 运行时检查**：
- 扫描会话日志：sub-agent 调用深度 + 宽度
- 扫描代码：是否有 SendMessage 在短命 sub-agent 间使用

## 反模式

- ❌ 主会话 → P → P 内 spawn G → G 内 spawn coder（深度 4）
- ❌ 单 message 召唤 8 个 sub-agent（宽度 6+）
- ❌ sub-agent A 给 sub-agent B 发 SendMessage 等回复
- ❌ 让 sub-agent 维护对话历史跨多次召唤

## 关联

- [pge-three-tiers.md](pge-three-tiers.md) —— PGE 应用场景
- [parallel-decision.md](parallel-decision.md) —— 何时启动并行
