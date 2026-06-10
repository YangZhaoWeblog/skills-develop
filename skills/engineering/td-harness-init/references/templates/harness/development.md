# 开发流程（development）

> 决定**怎么做**：PGE 档位 + Spec 重量 + 短会话原则。

## PGE 档位决策

接到任务先判断档位（见 [pge-three-tiers](../../skill-concepts/pge-three-tiers.md)）：

| 档 | 触发 | 形态 |
|---|------|------|
| 档 1 | ≤2h、单文件、单 harness 子规约 | 单会话角色切换 |
| 档 2 | ≥3 文件 / 多 harness 子规约 / 跨会话 / token>60% | feature branch + sub-agent + `.pge/spec.md` |
| 档 3 | 跨天 / `/loop` / 多 sprint contract | 档 2 + `.harness/campaign.json` |

升档触发任一即升，不可硬扛。

## Spec 重量决策

| 规模 | 工具 | 适用 | 产出位置 |
|------|------|------|---------|
| 大型 | SpecKit（specify→clarify→plan→tasks→implement）| 新模块、新 API、跨多模块 | `specs/<编号>-<名>/` |
| 中型 | OpenSpec（propose→apply→archive）| 现有模块新增/修改、业务设计调整 | `openspec/changes/<名>/` |
| 小型 | 直接做 + 项目小型变更脚手架 | Bug 修复、配置调整、1-3 文件 | PR 描述；bug 修复必带回归测试 |

PGE 档位与 Spec 重量**正交**——可叠加。

## 短会话原则（lecture-05 + lecture-13）

- 一次会话做 2-3 项 → commit → 退出
- token > 60% 即考虑 commit 退出，开新会话
- 每会话尾必须更新 PROGRESS.md / DECISIONS.md
- 上下文焦虑（接近 200K）会让 AI 跳过验证、选简单方案 → 提前 commit

## 干净状态（lecture-12）

- 每会话结束时 `git status` 必须为空（除白名单文件）
- 临时文件 / 调试代码 / TODO 必须清理
- "以后再清理" = 制度性放弃；熵增是默认状态

## 反模式

- ❌ 默认全开 PGE（小任务过度工程）
- ❌ 单会话塞满（token>80% 强行继续）
- ❌ 跨档位硬扛（档 1 任务硬做成跨天）
- ❌ commit 时留未清理的临时文件
