# 工具优于 AI 自检

> **来源**：walkinglabs lecture-08/10 + 圆桌 2（Dijkstra 让步）
> **状态**：✅ 当前判断（带边界）
> **影响 skill**：init（hook 化验证命令）

## 一句话

能用工具验证的优先于 AI 自检——但工具通过 ≠ 正确性。

## 核心论点

- 文档可被忽略，**原语不能被绕过**（lecture-08）
- 验证命令必须 hook 化，不能仅写在 AGENTS.md
- E2E 不只验证缺陷，会**反向改写 agent 编码行为**——它知道要过 E2E 就会写更好的代码（lecture-10）

## Dijkstra 反方与让步

**反方**：测试只能证明 bug 存在，不能证明它不存在。Agent 学到的可能是"骗过工具"而非"做对事"。

**让步**：
- 后端 E2E 难做的解法**不是降级到单元测试**，而是契约测试 + 可重放事件流 + 影子流量
- 工具的**设计方式**决定 agent 学到什么——错误消息要面向 agent（包含"怎么修"步骤）
- 保留批判：通过工具不等于正确，但工具是当前可达的最强约束

## 在 td-harness 中的内化

| 实践 | 落点 |
|------|------|
| 验证命令 hook 化 | `lefthook.yml` 或 `.git/hooks/` |
| 错误消息 agent-friendly | `[BLOCK] check_name \| file:line \| reason \| fix: <command>` |
| E2E 强制于完成定义 | AGENTS.md Workflow 步骤："E2E 通过才算完成" |
| 后端契约测试 | `harness/testing.md` 子节 |
| 重构场景输入-输出快照 | `harness/testing.md` 子节（黄金样本归位于此） |

## 反模式

- ❌ 把验证命令仅写在 AGENTS.md，不 hook 化
- ❌ 用 `--no-verify` 绕过 hook
- ❌ E2E 难做就退回单元测试敷衍
- ❌ 错误消息只说"哪错了"不说"怎么修"

## 关联

- [five-subsystems.md](five-subsystems.md) §反馈子系统
- clean-state-exit.md（待写）—— L12 的应用
