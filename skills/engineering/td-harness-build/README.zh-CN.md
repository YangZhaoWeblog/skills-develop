<p align="right">中文 | <a href="README.md">English</a></p>

# TD Harness Build

为项目构建或升级 **Harness**，提供从需求澄清到实现、验证与交付的 **多 Agent 协作工作流**。

## 一、开始使用

在项目目录安装：

```bash
npx skills@latest add YangZhaoWeblog/skills-develop --skill td-harness-build -y
```

在项目目录调用：

**新项目**

```text
$td-harness-build 我想做一个 Obsidian 插件。
```

**已有项目**

```text
$td-harness-build
```

## 二、工作流

[![产品与开发工作流](assets/workflow-overview.svg)](assets/workflow-overview.svg)

[查看详细返工图](assets/workflow-feedback.svg)

### 产品任务与开发任务

<p align="center">
  <a href="assets/task-relationships.svg"><img src="assets/task-relationships.svg" alt="一个产品任务对应一个或多个开发任务" width="900"></a>
</p>
