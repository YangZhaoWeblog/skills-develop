# 并行判定条件

> **来源**：圆桌 5（Knuth 度量主张）+ SOP L1310 + L1348-1355
> **状态**：✅ 判定规则
> **影响 skill**：init（spec.md 模板）、eval（验证 parallel_tasks 字段）

## 一句话

可并行的充要条件 = 文件集不相交 + 依赖图无环 + 嵌套深度 ≤2；超出任一退回顺序。

## 三条判据

```
sub-task 集合可并行 ⟺
  ∀ i ≠ j: files(i) ∩ files(j) = ∅       （文件不冲突）
  AND DAG(depends_on) 无环                （无逻辑死锁）
  AND nesting_depth ≤ 2                   （物理可达）
```

任一不满足 → 退回顺序执行。

## .pge/spec.md 强制字段

```yaml
parallel_tasks:
  - id: 1
    desc: "实现 foo 函数"
    files: [src/foo.go, src/foo_test.go]
    depends_on: []
  - id: 2
    desc: "实现 bar 函数"
    files: [src/bar.go, src/bar_test.go]
    depends_on: []
  - id: 3
    desc: "用 foo 和 bar 拼装"
    files: [src/baz.go]
    depends_on: [1, 2]
```

机器判定：`{files(1)} ∩ {files(2)} = ∅` ✓ → 1 和 2 并行；3 等 1+2 完成后串行。

## 当 parallel_tasks 字段缺失时

- 默认视为单任务顺序
- td-harness-init 生成的模板**默认隐藏 parallel_tasks**——按需启用，避免小任务过度工程化
- 当任务数 ≥3 时，spec.md 顶部自动提示 "考虑声明 parallel_tasks"

## 度量与门禁

| 度量 | 命令 | 阈值 |
|------|------|------|
| spec.md 是否声明 parallel_tasks | grep | 多任务必填 |
| 文件集相交检测 | yq + 集合运算 | 必须 ∅ |
| 依赖图环检测 | tsort 或 python networkx | 必须 DAG |
| 实际并行宽度 | 单 message Agent call 数 | ≤5（[sub-agent-physics](sub-agent-physics.md)） |

## 依据

[SOP L1310](../SOP-ai_work_flow_v1.0/PGE%20架构说明%20harness-agents.html)
> "并行而非串行：3-5 个并行子 Agent 缩短 90% 耗时"

[SOP L1348-1355 反模式]
```python
# ❌ 串行
for task in tasks:
    await run_agent(task)

# ✅ 并行
await asyncio.gather(*[run_agent(t) for t in tasks])
```

Claude Code 等价物：单 message 内多个 Agent tool call 在同一 `<function_calls>` 块内。

## 反模式

- ❌ 文件集相交还强行并行（写冲突）
- ❌ 有依赖关系也并行（B 拿不到 A 的输出）
- ❌ 把 parallel_tasks 默认必填（小任务过度工程）
- ❌ 不声明 parallel_tasks 也召唤多个 sub-agent（无契约的并行）

## 关联

- [pge-three-tiers.md](pge-three-tiers.md) —— PGE 分形结构
- [sub-agent-physics.md](sub-agent-physics.md) —— 并行的物理边界
- [tools-over-ai.md](tools-over-ai.md) —— 度量门禁哲学
