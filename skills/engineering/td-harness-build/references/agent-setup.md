# 原生 Agent 接入

Build 接入或升级角色时读取。使用用户现有平台，不另建跨平台调度器。

## 1. 核对平台

检查当前平台、版本和已有角色；无法确认才询问。按当前官方文档核对配置格式、可用模型、权限及独立上下文能力。

| 平台 | 项目配置 | 官方说明 |
|---|---|---|
| **Codex** | **.codex/agents/**，TOML | [子 Agent](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| **Claude Code** | **.claude/agents/**，Markdown/frontmatter | [子 Agent](https://code.claude.com/docs/en/sub-agents) |

只接入实际使用的平台；同时使用两个平台时分别核验。现有配置保留，同名冲突先核对用途。

## 2. 配置角色

将 **[职责模板](../assets/project/agent-roles.md)** 复制或融合到 **.harness/agent-roles.md**。主 Agent 沿用当前用户会话，无需另建；仅接入 Coder、Verifier、Reviewer、Executor 四个独立角色。先核对职责和有效权限，再复用已有角色；名称相同不代表职责相同。

**只读探子不能代替 Coder**。Coder 须能实现与补测，Verifier 须能执行检查，Reviewer 独立审阅。上层规则禁止必要操作时，保留角色职责，记录冲突并报告未完成；不能把职责改成只读检索后宣称接入完成。

**AI 确认参数，脚本填配置**。核对用户指定模型；未指定则推荐实际可用型号。强模型用于 Verifier、Reviewer，经济模型用于 Coder、Executor；主 Agent 模型在当前会话设置，不由脚本修改。

新建角色使用 **[configure_agents.py](../scripts/configure_agents.py)**（Python 3.11+，仅标准库）：

```bash
python3 scripts/configure_agents.py /path/to/project --platform codex \
  --strong-model ACTUAL_STRONG_MODEL --economy-model ACTUAL_ECONOMY_MODEL \
  --strong-effort ACTUAL_STRONG_EFFORT --economy-effort ACTUAL_ECONOMY_EFFORT
```

在 Skill 目录运行，替换示例参数；Claude 使用 **--platform claude**。推理档位可省略，按平台默认／继承规则生效；模型与档位兼容性须先核实。用 **--dry-run** 预览。

脚本从 **assets/native-agents/** 生成四份配置，名称统一为 **harness-角色小写名**。相同文件保留；存在不同内容或软链时整批停止，不覆盖。已有配置的融合由 AI 按授权处理，不能先删文件绕过冲突。

配置只保存角色用途、模型、推理设置及职责入口。**Codex 权限继承主会话**，不写无效的角色级 sandbox／approval 设置；Claude 工具限制按实际需要和官方能力配置。脚本不安装供应商，不修改主会话权限，不证明模型可用。

## 3. 调用核验

先检查配置解析和角色发现，再在新会话给四角色各派一个隔离小任务，核对 **实际模型、独立上下文、工具权限及职责读取**。不改业务代码、不提交、不访问生产环境。

**Codex 项目信任**：项目未受信任时，本地角色可能不会加载。角色未发现时，先用平台配置诊断核对目标目录及禁用原因；按用户授权信任该项目，不扩大到父目录。重新启动后直接调用角色，不能用临时 **-c agents.…** 注册代替持久加载验收。保留已有配置；只有当前版本确需额外注册时才补登记。

按职责配置最小权限。Verifier 运行测试可能写临时产物，不能简单设为完全只读；平台无法强制的文件边界注明“指令约束”。

按 **[职责模板 §3](../assets/project/agent-roles.md#3-项目接入)** 更新项目 **.harness/agent-roles.md §3** 的接入摘要，覆盖对应角色的旧摘要，不累积调用流水；本轮未验证的项保留其原日期与适用范围，不统一刷新为通过。需重载或新会话时给出操作；**未调用核验，仍属未完成**，不能以文件存在或主 Agent 自检代替。完整完成条件见 **[SKILL.md](../SKILL.md#完成与反馈)**。

后续直接调用已配置角色；平台、模型或权限变化时复验相关项。
