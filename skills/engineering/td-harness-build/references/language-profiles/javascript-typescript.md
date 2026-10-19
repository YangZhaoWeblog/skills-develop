# JavaScript / TypeScript 检查参考

> 建立或补充 JS/TS 检查入口时读取。先核实 package.json、锁文件、Node 版本、测试及 ESLint 配置。门槛见 [verification.md](../../assets/project/docs/verification.md)。

## 工具选择

| 检查 | 选择 / 已评估版本 | 采用理由 / 限制 |
|---|---|---|
| UT / 覆盖 | 已有框架优先；无框架默认 [Vitest](https://vitest.dev/guide/) + 匹配版本的 @vitest/coverage-v8 | 可测 JS/TS，集成断言与 Mock；保留 Jest、Vitest、node:test 等既有方案 |
| 圈复杂度 / 嵌套 | [ESLint](https://eslint.org/docs/latest/rules/) 10.12.0：complexity / max-depth | 使用现有 lint 入口；分别配置 10 / 4 |
| 认知复杂度 | [eslint-plugin-sonarjs](https://github.com/SonarSource/SonarJS) 4.2.2 | 配置 sonarjs/cognitive-complexity 为 15；TS parser 按项目匹配 |
| CRAP | [poly-crap](https://github.com/drew-simmons/poly-crap) 0.8.2 | 与 Python 共用工具，读取覆盖文件；生态较小，作为首版选择，不称行业标准 |
| 变异 | [StrykerJS](https://stryker-mutator.io/docs/stryker-js/introduction/) 10.0.0 | 匹配现有 runner；该评估版本需 Node ≥22，不为安装它擅自升级项目 |

## 命令与配置

**poly-crap 是独立 Rust CLI，不是 pip/npm 包。** 从官方 Release 获取对应平台的固定版本，或用 **cargo install poly-crap --version 0.8.2 --locked --root <工具目录>** 安装；核对校验和／版本，再记录可执行文件路径，不写进 Python 或 Node 依赖清单。

**无测试框架时**：核对 Node 与构建依赖，安装兼容的 Vitest 和同版本覆盖插件，写入项目开发依赖及锁文件。添加固定 **test**、**test:coverage** 入口，分别执行 **vitest run**、**vitest run --coverage**，覆盖输出包含 LCOV。先验证一个实际行为的通过与失败；不把“未找到测试”配置成成功。

当前版本不兼容时选兼容版本或报告缺口，不升级项目运行时来迁就工具。Obsidian 等宿主 API 在 UT 中隔离；界面与真实宿主行为另验。没有 Makefile 直接用 package scripts。

测试规范维护实际 UT、覆盖、CRAP 和 Stryker 入口；编码规范维护实际 lint 和类型检查入口。使用项目包管理器及锁文件，不用每次下载 latest 的临时命令。

合并到已有 ESLint 配置的规则值，插件注册和文件匹配沿用项目配置：

```json
{
  "complexity": ["error", 10],
  "max-depth": ["error", 4],
  "sonarjs/cognitive-complexity": ["error", 15]
}
```

CRAP 命令样例；尖括号须替换成项目真实参数：

```text
poly-crap --path <生产源码目录> --coverage <当前LCOV或Cobertura文件> --threshold 10 --min 0
```

Stryker 使用项目配置固定 runner、源码变异范围、测试排除和终端输出。不能把测试、生成代码、coverage 目录或 `.stryker-tmp` 沙箱纳入普通扫描与测试发现范围。接入后将完整命令和配置位置写入测试规范。

Vitest 项目使用匹配版本的覆盖 provider 和 `vitest run --coverage`，配置 LCOV 输出再交给 poly-crap。隔离试跑中 `c8 ... vitest run` 虽然测试成功，却生成了空 LCOV；不能只凭文件存在就接入 CRAP。Stryker 固定入口可用 `stryker run stryker.config.mjs`，通过项目 npm/pnpm 等脚本调用已锁定工具。

## 结果核对与缺口

先证明当前 UT 成功，再核对覆盖文件确实匹配当前源码；poly-crap 的 `coverage:null` 或输入不匹配不能判通过。它只计算分数，不负责运行 UT；未改动的历史超标单独记录，不使用全仓失败参数扩大修复。

默认在相关模块全量计算，AI 对照 git diff，独立 verifier 核对变化函数；可靠支持自动筛选时可使用。CRAP 只评价生产代码，测试有效性由变异和独立 Review 补充。

Stryker 核对选定范围逐项结果；存活、未覆盖、执行错误分开记录。关键输出直接填 Verify，不要求另建报告文档。

重复和架构依赖检查先复用项目现有入口。首版未预置统一工具；项目需要却缺入口时明确缺口，不能把独立 Review 冒充已执行的确定性检查。
