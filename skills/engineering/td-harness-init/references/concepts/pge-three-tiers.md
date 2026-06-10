# PGE 三档制（个人开发落地）

> **来源**：圆桌 3 + 圆桌 4（branch 修正）+ 圆桌 5（分形结构）
> **版本**：v0.5
> **状态**：✅ 设计纲要
> **影响 skill**：init（生成 .pge/ 模板）

## 一句话

PGE 是分形结构——主链顺序 P→G→E，内层任务并行；按规模分三档，默认不启动，按需升档。

## 分形结构（v0.5 核心）

**主链顺序**（因果依赖，无法并行）：
```
P ──spec.md──→ G ──code──→ E ──eval.md──→ 裁决
```

**内层并行**（独立任务，理应并行）：
```
G 内：sub-coder-1 / sub-coder-2 / sub-coder-3   （写不同文件）
E 内：sub-eval-test / sub-eval-a11y / sub-eval-sec  （多维度评估）
```

依据：[SOP/PGE 文档 L1310](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "并行而非串行：3-5 个并行子 Agent 缩短 90% 耗时"

## 三档对照表

| 档位 | 任务规模 | 主链形态 | 内层并行 | 文件 |
|------|---------|---------|---------|------|
| 档 1 | ≤2h 单文件 | 单会话角色切换 | 不并行 | 无额外 |
| 档 2 | 0.5–2 天，多文件 | feature branch + sub-agent | G/E 内按需并行 | `.pge/spec.md` / `.pge/eval.md` |
| 档 3 | ≥3 天，跨模块 | 档 2 + `/loop` | 并行率 >50% | + `.harness/campaign.json` |

**worktree 不再是默认**——降级为可选附加（仅当真并行 + main 同时构建/演示）。

## 升档信号（Knuth 给的）

档 1 → 档 2 触发任一：
- 改动文件数 > 3
- 涉及多个 `harness/*` 子规约
- 改动外部接口/DB schema
- 单会话 token 已用 > 60%
- 任务跨会话

档 2 → 档 3 触发任一：
- 任务跨天
- 需要 `/loop` 自动推进
- 多个 sprint contract 嵌套

档 3 → +worktree 触发：
- 真正需要并行（罕见）
- main 必须同时可构建/演示

## 档 2 物理流（branch + 文件 + sub-agent）

```
1. main 分支起会话
2. 主会话 Agent 工具召唤 Planner sub-agent
   → 输出 .pge/spec.md（含 parallel_tasks 声明）
   → Planner 退出
3. git checkout -b feature/xxx
4. 主会话扮演 Generator
   - 单任务：直接实现
   - 多独立任务：单 message 并行召唤 sub-coder（≤5 个）
5. git commit
6. 主会话召唤 Evaluator sub-agent（冷启动，仅给 spec.md + diff）
   → 输出 .pge/eval.md
7. PASS → merge to main + tag
   FAIL → 修复或删 branch（重试 ≤2-3 轮）
```

依据：[SOP L405](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "每个 Sprint 在独立 git branch 上工作——上下文问题通过'短会话 + 冷启动'解决"

## 档 2 文件契约

```
.pge/
├── spec.md          # P 产出：sprint contract + AC + parallel_tasks（人可改）
├── eval.md          # E 产出：独立会话仅读 spec.md + diff 验证
└── (代码) → feature branch git diff
```

**E 独立性**：sub-agent E 启动 prompt 只能见 spec.md + diff，不能见 P 的推理或 G 的实现笔记。

## 与 SpecKit/OpenSpec 的关系

- SpecKit 大型 spec ≈ PGE 档 3 的 P 阶段
- OpenSpec 中型变更 ≈ PGE 档 2 的 spec.md
- **正交**：PGE 档制 = 物理形态；SpecKit/OpenSpec = spec 重量；可叠加

## 反模式

- ❌ sub-agent 之间互相 SendMessage（短命会打到死收件箱）
- ❌ sub-agent 嵌套深度 >2
- ❌ sub-agent 并行宽度 >5
- ❌ 把 PGE 默认全开（小任务过度工程）
- ❌ E 启动时给完整对话历史（独立性失效）

详见：[sub-agent-physics.md](sub-agent-physics.md)、[parallel-decision.md](parallel-decision.md)

## 关联

- [td-harness-three-skills.md](td-harness-three-skills.md) §init
- [sub-agent-physics.md](sub-agent-physics.md) —— sub-agent 硬约束
- [parallel-decision.md](parallel-decision.md) —— 并行判定条件
- [tools-over-ai.md](tools-over-ai.md) —— E 验证哲学
