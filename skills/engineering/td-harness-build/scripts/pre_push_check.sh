#!/usr/bin/env bash
# pre_push_check.sh — Run the project's fixed pre-push checks.
# 初始化时只配置 run_project_checks；复用项目脚本，不在执行时选择工具。
# 豁免须获授权并记录未验证项：SKIP_PRE_PUSH=1 git push。

set -euo pipefail

if [[ "${SKIP_PRE_PUSH:-}" == "1" ]]; then
  printf '%s\n' '[SKIP] SKIP_PRE_PUSH=1; checks not executed.'
  exit 0
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel)" || {
  printf '%s\n' '[BLOCK] Run this hook inside its Git worktree.' >&2
  exit 2
}
cd "$PROJECT_ROOT"

run_project_checks() {
  # HARNESS_PROJECT_CHECKS_PENDING
  # 初始化时替换本函数体，删除上方标记。写入完整命令及必要的工作目录。
  # 例如项目已有统一入口：make check；否则依次调用已确认的 build/lint/test 入口。
  # 这里只调用已有执行源；没有入口时先按语言参考接入，不在 Hook 内重写检查逻辑。
  # 纯文档或尚未定技术栈的空项目，可写明暂无语言检查及后续接入条件并 return 0。
  printf '%s\n' '[BLOCK] Project checks are not configured. Configure run_project_checks in scripts/pre_push_check.sh, verify it, then retry.' >&2
  return 2
}

# 不在 if/|| 条件中调用，确保任一失败立即终止，不被后续成功命令掩盖。
# 项目检查不读取 Git 的 pre-push 协议输入；检查范围由固定项目入口负责。
set +e
( set -e; run_project_checks "$@" </dev/null )
status=$?
set -e
if [[ "$status" -ne 0 ]]; then
  printf '[BLOCK] Project checks failed (exit %s). Fix the reported error and rerun.\n' "$status" >&2
  exit "$status"
fi
printf '%s\n' '[OK] Configured project checks passed; task Verify remains required.'
