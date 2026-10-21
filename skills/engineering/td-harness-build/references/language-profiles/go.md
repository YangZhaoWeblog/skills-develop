# Go 检查参考

> 建立或补充 Go 项目检查入口时读取。先复用项目配置，再使用本参考；通过条件统一见 [verification.md](../../assets/project/docs/verification.md)。以下版本是评估基线，不代表已安装。

## 工具选择

| 检查 | 选择 | 采用理由 / 限制 |
|---|---|---|
| UT / 覆盖 | 项目现有 `go test` 入口 | 标准工具；复用同次成功 UT 的覆盖数据 |
| 圈 / 认知复杂度、嵌套 | golangci-lint 的 gocyclo / gocognit / revive | 共用已有 lint；配置样例见 [资产](../../assets/.golangci.yml)，合并而不覆盖项目配置 |
| CRAP | [padiazg/go-crap](https://github.com/padiazg/go-crap) v0.5.1 | 支持已有覆盖 profile；已测边界。构建工具需要 Go 1.26.2，不能因此修改项目 go.mod |
| 变异 | [gremlins](https://github.com/go-gremlins/gremlins) v0.6.0 | 支持范围及逐项状态；默认退出成功不等于所有变异已被发现 |
| 重复 | [mibk/dupl](https://github.com/mibk/dupl) v1.1.0 | 实测可跨包比较；不只依赖当前 golangci-lint 的同包 dupl 检查 |
| 架构依赖 | 项目 depguard 规则 + Go 编译 | 只检查项目明确的禁止依赖与循环；函数语义归属仍需独立 Review |

## Go 单元测试默认方案

**go test** 负责运行；**testify/assert、require** 负责断言；需要隔离的 Go 接口统一使用 **mockgen + gomock**。按需采用 **httptest** 或 **go-sqlmock** 验证 HTTP / SQL 交互；不整批安装所有工具。已有工具或项目规则冲突时，先按升级规则确认迁移范围。

### 安装与版本

先核对 **go.mod、工具锁定方式、项目安装脚本和当前平台**，只补缺失项，不为检查工具改变项目语言版本。

在实际 Go 模块目录核对已有 lint 配置；缺少时以 [配置样例](../../assets/.golangci.yml) 为起点，按项目版本和源码范围适配，再验证固定命令。骨架脚本不自动复制语言配置。

```bash
# 已有 Go 环境的检查示例；读取实际结果，不用后续 echo 掩盖失败
go version
go env GOTOOLCHAIN

# macOS 且项目已选择 Homebrew 管理 Go 时的安装示例
brew install go
```

Windows / Linux 按项目包管理方式或官方对应平台安装方式填写，不执行 brew 示例。只在必要且已获授权时修改 PATH 等环境配置；完成后报告实际操作与未完成项，不用新安装覆盖已可用的环境。

### 接口替身生成

**mockgen** 从接口生成替身，**gomock** 配置返回值和调用核验。固定兼容项目的生成器及运行库版本，维护唯一生成入口、源接口和输出位置，不手写替身或修改生成文件。

```text
# 示例：接入时替换固定版本与项目路径，不能原样执行
go run go.uber.org/mock/mockgen@<固定版本> -source=<接口文件> -destination=<生成文件> -package=<生成包名>
```

接口变化后重新生成，核对差异并运行受影响测试。仅需固定返回值时也配置生成替身；参数、次数和顺序只约束需要验证的行为。纯函数直接测试，不为采用工具强制增加无用接口。禁止用 gomonkey / monkey 运行时 patch 生产函数绕过隔离设计。

### 文件组织与执行示例

沿用项目测试布局。Go 默认使用 **_test.go**，内部测试可同包，公开 API 黑盒测试可用外部测试包。相似场景可用表驱动，不要求所有用例共用一个文件或写法。

```text
# 示例包名和用例名须替换为项目实际值
go test ./...
go test ./internal/service/... -run '^TestCreateUser$' -count=1 -v
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out
```

先确认 UT 成功，再分析同次生成的覆盖文件；不要因报告命令成功而忽略测试失败。项目使用嵌套 module 时按实际模块运行。

Go 并发代码须执行适用范围的 **go test -race**；平台或工具不支持时按验证规则报告缺口，不擅自省略。Fuzz 与 Benchmark 仅在 Plan 需要时使用，不作为每次任务必跑项。

## 命令落点

以下尖括号是待填写参数，不是可直接执行的命令。落到项目文档时换成真实目录、文件和配置，验证一次后作为固定入口；每次任务只改变范围。

测试规范维护：

```text
<项目 UT 命令，生成本次 coverage.out>
go-crap scan --coverage-profile <coverage.out> --format json <源码范围>
gremlins --config <项目配置> unleash --workers 1 --output <临时结果文件> <包范围>
```

编码规范维护：

```text
<项目 golangci-lint 固定入口>
dupl -t 150 -plumbing -files < <显式源码文件清单>
```

`150` 是重复候选的检测起点，不是函数行数或零重复门槛。重复扫描的输入先排除生成代码；读取两端位置和语义，不自动抽象。

## 结果核对

可靠支持时用工具筛选变化函数；否则在相关模块全量计算，AI 对照 git diff，独立 verifier 核对新增和修改函数。不要默认使用 gremlins 的 Git 增量筛选：实测存在新文件及子模块漏检。

UT 必须独立成功，覆盖文件必须与当前源码和范围匹配。go-crap 的成功退出或低分不能证明 UT 已成功，也不能证明覆盖输入有效。计算范围排除生成代码和测试代码，测试质量另行审查。

gremlins 读取逐项存活、未覆盖、超时和执行错误，不只看退出码或百分比。工具原生临时结果只供核验；关键位置、状态及复验写回 Verify，不新建报告文档。

若复验因工具的自动时间预算过短而超时，先核对测试本身和启动耗时，再调整固定入口的 `--timeout-coefficient`。本次小函数试跑用 `20` 后复验成功；这只是已验证的起点，不是全项目统一值。超时不能算测试发现了错误。

depguard 的文件范围要同时覆盖目录直接文件和子目录。禁止包规则区分包本身、子包及相似名字；按本项目分层制定，不把某个项目的 helper/logic 名称强加到所有项目。
