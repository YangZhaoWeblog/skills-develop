# Razor BLOCK at 200 行

> **来源**：walkinglabs L04 + 圆桌 1（razor 模式）
> **状态**：✅ 强约束
> **影响 skill**：init（生成时检查）、eval（周期检查）

## 一句话

AGENTS.md 行数超过 200 行视为设计失败，必须拆分到 `harness/*` 或上报人工调整。

## 经验依据

- 第 300 行约束执行率 ~60%，移到顶部 ~95%（lecture-04）
- 膨胀指令占 10–20K tokens，挤压代码阅读预算
- 多数团队对指令文件"只加不删"——和软件技术债是同一病

## 阈值与动作

| 行数 | 状态 | 动作 |
|------|------|------|
| ≤150 | ✅ 健康 | 无 |
| 151–200 | ⚠️ 警戒 | 评估是否可拆分 |
| 201–250 | 🔴 BLOCK | 强制拆到 harness/* |
| >250 | 💀 设计错误 | 上报人工，AI 不再尝试自动精简 |

## 拆分原则

- 入口文件作为**路由器**（导航、硬约束、Workflow 骨架）
- 详细规约下沉到 `harness/<topic>.md`
- AGENTS.md 仅保留链接 + 一句话摘要
- 对应 lecture-04："位置决定遵循率"——硬约束放顶部

## 测量命令

```bash
wc -l AGENTS.md
```

阈值 ≤200。

## 反模式

- ❌ 每次出问题加一条规则到 AGENTS.md（lecture-04 的毒）
- ❌ 拆分时把"重要约束"也下沉（顶部信息密度反而下降）
- ❌ 通过删除空行缩减行数（投机取巧）

## 当前状态

| 项目 | 行数 | 状态 |
|------|------|------|
| contract-product/AGENTS.md | 244 | 🔴 BLOCK，待拆分 |
| product-service/AGENTS.md | 待测 | - |
| sop.init 模板（公司） | 244 | 🔴 BLOCK，模板自身需精简 |

## 关联

- [five-subsystems.md](five-subsystems.md) §指令子系统
- [td-harness-three-skills.md](td-harness-three-skills.md) §init/eval
