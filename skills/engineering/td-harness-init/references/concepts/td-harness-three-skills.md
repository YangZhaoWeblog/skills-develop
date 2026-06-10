# td-harness 三件套

> **来源**：圆桌 1
> **状态**：✅ 设计纲要
> **公司对应物**：sop.init / sop.eval（缺第三件，是个人差异化）

## 三 skill 职责

| skill | 职责 | 触发 |
|-------|------|------|
| `td-harness-init` | 在新/既有项目落盘五子系统模板 | 项目起步、迁移 |
| `td-harness-eval` | 按五子系统体检 + Scorecard 8 维度评分 | 周期性 / PR 前 |
| `td-harness-update` | 反馈循环：failures → 规约升级 + GC 僵尸规约 | 月度 / 触发式 |

## 与公司 sop 的差异点

1. **razor BLOCK at 200 行**：AGENTS.md 超出强制拆分（公司无）
2. **原生支持 contract.md 模式**：重构项目（公司侧重新功能）
3. **update skill**：反馈循环 + GC 僵尸规约（公司缺）
4. **正负反馈机制**：好习惯沉淀 + 坏习惯失败记录
5. **冷启动测试**：AI 仅读 AGENTS.md 写出可运行代码

## init 必须做的事

参考 [concepts/five-subsystems.md](five-subsystems.md)，落盘：

- AGENTS.md（≤200 行）
- harness/coding-style.md, glossary.md, failures.md, testing.md（必备）
- harness/* 其他按需
- .git/hooks/ 或 lefthook.yml（hook 化验证命令）
- PROGRESS.md / DECISIONS.md 模板
- 环境锁定文件（按语言生态）

## eval 必须做的事

按 Scorecard 8 维度评分，<3 分 = FAIL（待写 [scorecard-8-dim.md](scorecard-8-dim.md)）

冷启动测试：用全新会话只读 AGENTS.md，能否回答下列问题：
1. 项目做什么？
2. 技术栈？
3. 怎么运行？
4. 怎么测试？
5. 关键约束？

## update 必须做的事

- 扫描 failures.md，识别重复出现的 bug 类别 → 升级到 harness 规则
- GC 扫描：>3 月无引用的规约 → archive（[gc-zombie.md](gc-zombie.md) 待写）
- 双向反哺：项目失败 → 模板修改 → 下一项目

## 关联

- [five-subsystems.md](five-subsystems.md)
- [razor-block-200.md](razor-block-200.md)
- [pge-three-tiers.md](pge-three-tiers.md) —— init 生成 .pge/ 模板
