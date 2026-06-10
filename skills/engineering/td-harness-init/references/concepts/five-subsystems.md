# Harness 五子系统模型

> **来源**：walkinglabs lecture-03/04/05/07/10/12 + 圆桌 2
> **状态**：✅ 当前判断
> **影响 skill**：init（生成模板）、eval（按子系统体检）

## 一句话

Harness 由五个独立可操纵的子系统构成，缺一即不完整；反馈子系统 ROI 最高。

## 五子系统

| 子系统 | 载体 | 关键产物 |
|--------|------|---------|
| **指令** | AGENTS.md / CLAUDE.md | 项目概览、技术栈、硬约束、文档链接 |
| **工具** | shell / 文件 / 测试 | 最小权限原则下的访问授予 |
| **环境** | 依赖 / 服务 / 版本 | pyproject.toml / package.json / .nvmrc / Dockerfile |
| **状态** | PROGRESS.md / DECISIONS.md / commits | 已完成 / 进行中 / 阻塞 / 决策 why |
| **反馈** | test / lint / build | 验证命令 + hook 强制 |

## 实证数据（来自 walkinglabs）

某团队 GPT-4o + 20k 行 TS/React，模型不变只改 harness：
- 阶段 1（仅 README）：20% 成功率
- 阶段 2（+ AGENTS.md）：60%
- 阶段 3（+ 验证命令）：80%
- 阶段 4（+ 进度文件）：80–100%

## 量化方法（控制变量排除法）

保持模型不变，逐个移除子系统观察性能下降。下降最大者 = 当前任务边际贡献最大者。

**Knuth 修正**：子系统未必正交；定位真正瓶颈要靠失败记录归因，不能仅靠拆除实验。

## 在 td-harness 中的内化

- `init` skill 必须生成五子系统的模板文件
- `eval` skill 按五子系统体检（每项有度量）
- 反馈子系统优先级最高——先确保验证命令写清楚

## 关联

- [tools-over-ai.md](tools-over-ai.md) —— 反馈子系统的核心原则
- [razor-block-200.md](razor-block-200.md) —— 指令子系统的边界
- metric-ledger.md（待写）—— 五子系统的度量
