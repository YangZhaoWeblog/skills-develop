#!/usr/bin/env bash
# install_hooks.sh — 安装 hook 到目标项目
# 优先 lefthook（如已有 lefthook.yml）；否则装到 .git/hooks/
# 幂等

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${REPO_ROOT}/scripts"

# 1. 复制脚本到 scripts/
for script in check_razor_block.sh check_wip.sh check_test_guard.sh \
              check_commit_msg.sh pre_commit_check.sh pre_push_check.sh; do
    cp "${SKILL_DIR}/${script}" "${REPO_ROOT}/scripts/${script}"
    chmod +x "${REPO_ROOT}/scripts/${script}"
done

# 2. 装 hook
if command -v lefthook >/dev/null 2>&1; then
    if [[ ! -f "${REPO_ROOT}/lefthook.yml" ]]; then
        # 从 templates 渲染
        sed "s|{{REPO_ROOT}}|${REPO_ROOT}|g" \
            "${SKILL_DIR}/../templates/lefthook.yml.tmpl" \
            > "${REPO_ROOT}/lefthook.yml"
    fi
    cd "${REPO_ROOT}" && lefthook install
    echo "✓ lefthook installed"
else
    # fallback：直接装到 .git/hooks/
    HOOKS_DIR="${REPO_ROOT}/.git/hooks"
    cat > "${HOOKS_DIR}/pre-commit" <<EOF
#!/usr/bin/env bash
exec bash "${REPO_ROOT}/scripts/pre_commit_check.sh" "\$@"
EOF
    cat > "${HOOKS_DIR}/commit-msg" <<EOF
#!/usr/bin/env bash
exec bash "${REPO_ROOT}/scripts/check_commit_msg.sh" "\$@"
EOF
    cat > "${HOOKS_DIR}/pre-push" <<EOF
#!/usr/bin/env bash
exec bash "${REPO_ROOT}/scripts/pre_push_check.sh" "\$@"
EOF
    chmod +x "${HOOKS_DIR}"/{pre-commit,commit-msg,pre-push}
    echo "✓ git hooks installed (no lefthook)"
fi

# 3. 创建 .harness/
mkdir -p "${REPO_ROOT}/.harness"
[[ ! -f "${REPO_ROOT}/.harness/metrics.tsv" ]] && \
    echo -e "timestamp\tmetric\tvalue" > "${REPO_ROOT}/.harness/metrics.tsv"

echo "✓ td-harness hooks ready"
