# 编码规范（coding-style）

> 本文件是 AGENTS.md 的展开。AI 修改代码前必读对应章节。

## 命名

- 包名：小写单数，避免缩写（`user` 而非 `usr`）
- 接口：`-er` 后缀（`Reader`, `Writer`），单方法用动词名词
- 错误：`Err{Domain}{Reason}`（`ErrUserNotFound`）
- 常量：`PascalCase`，作用域局部用 `camelCase`

## 错误处理

```go
// ✅ 包装并保留链路
if err != nil {
    return fmt.Errorf("query user %s: %w", id, err)
}

// ❌ 裸 return
if err != nil {
    return err
}
```

## 日志

- 使用结构化日志（slog / zap），禁用 `fmt.Println` / `log.Println` 调试输出
- 关键路径必须有 trace_id

## Import 顺序

1. 标准库
2. 第三方
3. 项目内（按字典序）

每组之间一空行。

## 注释

- 所有 exported 函数必须有 GoDoc（首词为函数名）
- 复杂逻辑加 `// why:` 注释解释为什么这样写

---

> 项目特定规则在此文件追加；通用规则参考 Effective Go / TS Handbook。
