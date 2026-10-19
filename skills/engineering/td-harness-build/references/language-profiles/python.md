# Python 检查参考

> 建立或补充 Python 检查入口时读取。先核实 pyproject.toml、锁文件、测试框架和 CI。门槛见 [verification.md](../../assets/project/docs/verification.md)。以下版本是评估基线。

## 工具选择

| 检查 | 选择 / 已评估版本 | 采用理由 / 限制 |
|---|---|---|
| UT / 覆盖 | 已有框架优先；无框架默认 [pytest](https://docs.pytest.org/en/stable/getting-started.html) + [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) | 断言和 fixture 简洁；生成当前源码覆盖数据，保留既有 unittest 等方案 |
| 圈复杂度 | [Ruff](https://docs.astral.sh/ruff/rules/complex-structure/) 0.16.10 C901 | 成熟 lint 入口；max-complexity 配置为 10 |
| 认知复杂度 | [complexipy](https://github.com/rohaquinlop/complexipy) 8.0.1 | 可直接检查 15 门槛，已测边界 |
| 嵌套 | [Lizard](https://github.com/terryyin/lizard) 1.24.1 NS 扩展 | 已测 4/5 层；只采用 NS 指标，不引入其函数长度等默认标准 |
| CRAP | [poly-crap](https://github.com/drew-simmons/poly-crap) 0.8.2 | 与 JS/TS 共用；读取覆盖文件，生态较小 |
| 变异 | [mutmut](https://mutmut.readthedocs.io/en/latest/) 3.8.0 | 本版需要 pytest 和 fork；Windows 需 WSL。不满足则报告缺口，不强换框架 |

## 命令与配置

**poly-crap 是独立 Rust CLI，不是 pip/npm 包。** 从官方 Release 获取对应平台的固定版本，或用 **cargo install poly-crap --version 0.8.2 --locked --root <工具目录>** 安装；核对校验和／版本，再记录可执行文件路径，不写进 Python 或 Node 依赖清单。

**无测试框架时**：在项目虚拟环境安装兼容的 pytest、pytest-cov，并按现有依赖方式锁定。固定入口为 **python -m pytest**；覆盖命令指定生产模块，例如 **python -m pytest --cov=package_name --cov-report=term-missing --cov-report=xml**。替换示例包名，先验证一个实际行为的通过与失败；未收集到测试不能记为通过。

Anki 等宿主依赖在 UT 中隔离，真实宿主行为另验。没有 Makefile 使用项目既有脚本或记录直接命令。

安装沿用项目虚拟环境及依赖管理方式，锁定兼容版本；不修改系统 Python。测试规范维护 UT/覆盖/CRAP/变异入口，编码规范维护 Ruff/complexipy/Lizard 入口。

合并到已有 pyproject.toml 的 Ruff 配置，不覆盖原有规则集合：

```toml
[tool.ruff.lint]
extend-select = ["C901"]

[tool.ruff.lint.mccabe]
max-complexity = 10
```

命令样例；尖括号须替换成项目真实参数：

```text
ruff check <源码范围>
complexipy <源码范围> --max-complexity-allowed 15
lizard -E NS --NS 4 <源码范围>
poly-crap --path <生产源码目录> --coverage <当前覆盖XML> --threshold 10 --min 0
mutmut run --max-children 1 "<模块匹配表达式>"
mutmut results --all true
```

## 结果核对与缺口

Lizard 只取 NS 字段按嵌套门槛判断；不采用默认 CC、函数长度等额外门槛。CSV 输出可能返回成功，即使 NS 超标，因此读取实际值。

UT 独立成功后核对覆盖输入有效性。poly-crap 的 `coverage:null`、错误源码映射或缺少相关函数覆盖不能因低分而通过。相关模块全量计算后 AI 对照 git diff，独立 verifier 核对变化函数；可靠支持自动筛选时可使用。

mutmut 复验入口显式指定相关模块。实测默认缓存可能沿用修改测试前的结果；必须确认修正后的测试实际执行。逐项区分已发现、存活、未覆盖、未执行及执行错误，关键输出填 Verify，不要求另建报告文档。

重复和架构依赖检查先复用项目现有入口。首版未预置统一工具；需要却缺入口时明确缺口，不标通过。
