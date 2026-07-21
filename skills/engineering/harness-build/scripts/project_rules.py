"""Rebuild project rule documents from canonical text and repository facts."""

from __future__ import annotations

import json
import os
import re
import tomllib
from pathlib import Path


FACT_GENERATED_PATHS = (
    "harness/api-standards.md",
    "harness/coding-style.md",
    "harness/database.md",
    "harness/dependency-map.md",
    "harness/deployment.md",
    "harness/development.md",
    "harness/testing.md",
)
EXCLUDED_DIRECTORIES = {
    ".agents",
    ".codex",
    ".git",
    ".idea",
    ".venv",
    ".worktrees",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
MAKE_TARGET = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?![=])", re.MULTILINE)
GO_MODULE = re.compile(r"^module\s+(\S+)", re.MULTILINE)
GO_VERSION = re.compile(r"^go\s+(\S+)", re.MULTILINE)
GO_REQUIRE = re.compile(
    r"^\s*(?:require\s+)?([^\s]+)\s+(v[^\s]+)"
    r"(?:\s+//\s*(indirect))?\s*$",
    re.MULTILINE,
)
JENKINS_COVERAGE_MIN = re.compile(
    r"\bCOVERAGE_MIN\s*=\s*['\"]([0-9]+(?:\.[0-9]+)?)['\"]"
)
TODO_SECTION = re.compile(r"\n## Project Growth TODO\n.*\Z", re.DOTALL)
CHAINMAKER_SDK = "chainmaker.org/chainmaker/contract-sdk-go/v2"


def repository_files(target: Path) -> list[Path]:
    """List ordinary repository files without following generated/vendor trees."""
    files = []
    for root, directories, names in os.walk(target, followlinks=False):
        directories[:] = sorted(
            name
            for name in directories
            if name not in EXCLUDED_DIRECTORIES
            and not (Path(root) / name).is_symlink()
        )
        for name in sorted(names):
            path = Path(root) / name
            if not path.is_symlink():
                files.append(path)
    return files


def relative(target: Path, paths: list[Path]) -> list[str]:
    """Return sorted target-relative paths."""
    return sorted(path.relative_to(target).as_posix() for path in paths)


def read_optional(path: Path) -> str:
    """Read one regular UTF-8 text file when present."""
    if not path.is_file() or path.is_symlink():
        return ""
    return path.read_text(encoding="utf-8")


def make_commands(target: Path) -> dict[str, list[str]]:
    """Collect reliable commands exposed by Makefiles."""
    commands = {
        "verify": [],
        "generate": [],
        "lint": [],
        "run": [],
    }
    content = read_optional(target / "Makefile")
    targets = set(MAKE_TARGET.findall(content))
    groups = {
        "verify": ("ut", "test", "check", "lint", "build"),
        "generate": ("protoc", "gen", "generate", "codegen", "gen-code"),
        "lint": ("lint", "fmt", "format"),
        "run": ("start-service", "start", "run", "serve"),
    }
    for group, candidates in groups.items():
        commands[group] = [
            f"make {name}" for name in candidates if name in targets
        ]
    return commands


def direct_go_dependencies(go_mod: str) -> set[str]:
    """Return Go modules not marked indirect in go.mod."""
    return {
        module
        for module, _, indirect in GO_REQUIRE.findall(go_mod)
        if not indirect
    }


def make_target_recipe(content: str, target: str) -> str:
    """Return the tab-indented recipe for one Make target."""
    match = re.search(
        rf"^{re.escape(target)}\s*:[^\n]*\n((?:\t[^\n]*(?:\n|$))*)",
        content,
        re.MULTILINE,
    )
    return match.group(1) if match else ""


def recipe_enforces_coverage(recipe: str, threshold: str) -> bool:
    """Detect a local recipe guard tied to the CI coverage threshold."""
    references_threshold = threshold in recipe or "COVERAGE_MIN" in recipe
    has_guard = re.search(
        r"(?:\bif\b|\btest\b|\[\[?|--fail-under|\bexit\b)",
        recipe,
    )
    return references_threshold and has_guard is not None


def package_commands(target: Path) -> dict[str, list[str]]:
    """Collect reliable commands declared by package.json scripts."""
    commands = {
        "verify": [],
        "generate": [],
        "lint": [],
        "run": [],
    }
    content = read_optional(target / "package.json")
    if not content:
        return commands
    package = json.loads(content)
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return commands
    groups = {
        "verify": ("test", "check", "lint", "build"),
        "generate": ("generate", "codegen"),
        "lint": ("lint", "format"),
        "run": ("start", "dev", "serve"),
    }
    for group, candidates in groups.items():
        commands[group] = [
            f"npm run {name}" for name in candidates if name in scripts
        ]
    return commands


def merge_commands(*sources: dict[str, list[str]]) -> dict[str, list[str]]:
    """Merge command groups without changing their discovery order."""
    merged = {"verify": [], "generate": [], "lint": [], "run": []}
    for source in sources:
        for group, commands in source.items():
            for command in commands:
                if command not in merged[group]:
                    merged[group].append(command)
    return merged


def collect_facts(target: Path) -> dict[str, object]:
    """Collect deterministic facts from standard repository files."""
    files = repository_files(target)
    relative_files = relative(target, files)
    file_set = set(relative_files)
    facts: dict[str, object] = {
        "languages": [],
        "tools": [],
        "frameworks": [],
        "module": "",
        "commands": merge_commands(
            make_commands(target),
            package_commands(target),
        ),
        "api_sources": [],
        "database_engines": [],
        "migration_roots": [],
        "structure": [],
        "ci": [],
        "deployment": [],
        "coverage_threshold": "",
        "local_coverage_gap": False,
        "test_count": 0,
        "test_files": [],
    }

    go_mod = read_optional(target / "go.mod")
    if go_mod:
        version = GO_VERSION.search(go_mod)
        module = GO_MODULE.search(go_mod)
        facts["languages"].append(
            f"Go {version.group(1)}" if version else "Go"
        )
        facts["tools"].append("Go")
        facts["module"] = module.group(1) if module else ""
        direct_dependencies = direct_go_dependencies(go_mod)
        dependencies = {
            "github.com/zeromicro/go-zero": "go-zero",
            "google.golang.org/grpc": "gRPC",
            "gorm.io/gorm": "GORM",
            CHAINMAKER_SDK: "ChainMaker smart contract",
        }
        for module_path, label in dependencies.items():
            if module_path in direct_dependencies:
                facts["frameworks"].append(label)
    else:
        direct_dependencies = set()

    package_json = read_optional(target / "package.json")
    if package_json:
        package = json.loads(package_json)
        version = package.get("engines", {}).get("node")
        facts["languages"].append(f"Node.js {version}" if version else "Node.js")
        facts["tools"].append("Node.js")

    pyproject = read_optional(target / "pyproject.toml")
    if pyproject:
        project = tomllib.loads(pyproject).get("project", {})
        version = project.get("requires-python")
        facts["languages"].append(f"Python {version}" if version else "Python")
        facts["tools"].append("Python")

    api_sources = [
        path
        for path in relative_files
        if (
            path.endswith((".graphql", ".gql"))
            or (
                path.endswith(".proto")
                and not path.startswith(
                    ("proto/google/", "proto/openapi/", "proto/validate/")
                )
            )
        )
        or Path(path).name.lower()
        in {"openapi.json", "openapi.yaml", "openapi.yml", "swagger.json"}
    ]
    register_path = "internal/contract/register.go"
    method_path = "const/method.go"
    if (
        CHAINMAKER_SDK in direct_dependencies
        and register_path in file_set
        and re.search(
            r"\.RegisterMethod\s*\(",
            read_optional(target / register_path),
        )
    ):
        api_sources.extend(
            path for path in (method_path, register_path) if path in file_set
        )
    facts["api_sources"] = api_sources[:40]

    migration_files = [
        path
        for path in relative_files
        if any("migration" in part.lower() for part in Path(path).parts)
        and Path(path).suffix.lower() in {".sql", ".go", ".py", ".rb"}
    ]
    migration_roots = {Path(path).parent.as_posix() for path in migration_files}
    facts["migration_roots"] = sorted(migration_roots)

    migration_configs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in files
        if any(
            "migration" in part.lower()
            for part in path.relative_to(target).parts
        )
        and path.suffix.lower() in {".hcl", ".json", ".toml", ".yaml", ".yml"}
    )
    migration_evidence = "\n".join(facts["migration_roots"])
    searchable = (
        migration_evidence if migration_evidence else go_mod.lower()
    ) + "\n" + migration_configs.lower()
    engines = []
    for needle, label in (
        ("mysql", "MySQL"),
        ("postgres", "PostgreSQL"),
        ("pgx", "PostgreSQL"),
        ("kingbase", "Kingbase"),
        ("sqlite", "SQLite"),
    ):
        if needle in searchable.lower() and label not in engines:
            engines.append(label)
    facts["database_engines"] = engines

    structure_candidates = (
        "app",
        "cmd",
        "internal",
        "internal/cron",
        "internal/dao",
        "internal/event",
        "internal/logic",
        "internal/svc",
        "pkg",
        "src",
    )
    facts["structure"] = [
        path for path in structure_candidates if (target / path).is_dir()
    ]

    ci_candidates = (
        "Jenkinsfile",
        ".gitlab-ci.yml",
    )
    ci = [path for path in ci_candidates if path in file_set]
    ci.extend(
        path
        for path in relative_files
        if path.startswith(".github/workflows/")
    )
    facts["ci"] = sorted(set(ci))[:40]

    deployment_candidates = (
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
    )
    deployment = [path for path in deployment_candidates if path in file_set]
    deployment.extend(
        path
        for path in relative_files
        if path.startswith(("charts/", "helm/", "k8s/"))
    )
    facts["deployment"] = sorted(set(deployment))[:40]

    coverage_match = JENKINS_COVERAGE_MIN.search(
        read_optional(target / "Jenkinsfile")
    )
    if coverage_match:
        threshold = coverage_match.group(1)
        facts["coverage_threshold"] = threshold
        makefile = read_optional(target / "Makefile")
        recipe = make_target_recipe(makefile, "ut")
        facts["local_coverage_gap"] = bool(recipe) and not recipe_enforces_coverage(
            recipe,
            threshold,
        )

    test_files = [
        path
        for path in relative_files
        if path.endswith("_test.go")
        or Path(path).name.startswith("test_")
        or ".test." in Path(path).name
        or ".spec." in Path(path).name
    ]
    facts["test_count"] = len(test_files)
    facts["test_files"] = test_files[:12]
    return facts


def bullets(items: list[str], empty: str) -> list[str]:
    """Render one fact group as Markdown bullets."""
    return [f"- {item}" for item in items] if items else [f"- {empty}"]


def joined_commands(commands: list[str]) -> str:
    """Render commands for one compact template field."""
    return " && ".join(commands) if commands else "Not detected; confirm before use"


def document_facts(path: str, facts: dict[str, object]) -> list[str]:
    """Select facts relevant to one generated rule document."""
    languages = list(facts["languages"])
    frameworks = list(facts["frameworks"])
    commands = dict(facts["commands"])
    if path.endswith("coding-style.md"):
        lines = bullets(languages, "No language marker detected.")
        if facts["module"]:
            lines.append(f"- Module: `{facts['module']}`")
        lines.extend(f"- Framework: {name}" for name in frameworks)
        lines.extend(
            f"- Existing code boundary: `{name}`"
            for name in facts["structure"]
        )
        lines.extend(f"- Formatting/lint command: `{cmd}`" for cmd in commands["lint"])
        return lines
    if path.endswith("testing.md"):
        lines = [
            f"- Verification command: `{command}`"
            for command in commands["verify"]
        ]
        lines.extend(
            f"- Existing test file: `{name}`" for name in facts["test_files"]
        )
        if facts["test_count"]:
            lines.append(f"- Detected test files: {facts['test_count']}")
        threshold = str(facts["coverage_threshold"])
        if threshold:
            lines.append(f"- CI coverage threshold: {threshold}%")
            if facts["local_coverage_gap"]:
                lines.append(
                    f"- Local `make ut` does not enforce the {threshold}% CI "
                    "coverage threshold; command success does not prove the CI "
                    "coverage gate."
                )
        return lines or ["- No reliable test command or test file detected."]
    if path.endswith("api-standards.md"):
        lines = [
            f"- API source: `{name}`" for name in facts["api_sources"]
        ]
        lines.extend(
            f"- Generation command: `{command}`"
            for command in commands["generate"]
        )
        return lines or ["- No public API source detected."]
    if path.endswith("database.md"):
        lines = [
            f"- Database engine: {name}"
            for name in facts["database_engines"]
        ]
        lines.extend(
            f"- Migration root: `{name}`"
            for name in facts["migration_roots"]
        )
        if "GORM" in frameworks:
            lines.append("- Data access library: GORM")
        return lines or ["- No database or migration fact detected."]
    if path.endswith("dependency-map.md"):
        lines = [
            f"- Framework/dependency: {name}" for name in frameworks
        ]
        lines.extend(
            f"- Existing module boundary: `{name}`"
            for name in facts["structure"]
        )
        return lines or ["- No standard dependency boundary detected."]
    if path.endswith("deployment.md"):
        lines = [f"- CI artifact: `{name}`" for name in facts["ci"]]
        lines.extend(
            f"- Deployment/runtime artifact: `{name}`"
            for name in facts["deployment"]
        )
        if not facts["deployment"]:
            lines.append("- No deployment/runtime artifact detected.")
        return lines
    raise ValueError(f"unsupported fact-generated document: {path}")


def rebuild_project_rules(target: Path, staging: Path, baseline: Path) -> None:
    """Replace stale project rule files with canonical, fact-backed documents."""
    facts = collect_facts(target)
    commands = dict(facts["commands"])
    for relative_path in FACT_GENERATED_PATHS:
        source = baseline / relative_path
        content = source.read_text(encoding="utf-8")
        content = TODO_SECTION.sub("", content).rstrip()
        if relative_path.endswith("development.md"):
            tools = ", ".join(facts["tools"]) or "Not detected"
            setup = []
            if "Go" in facts["tools"]:
                setup.append("go mod download")
            if "Node.js" in facts["tools"]:
                setup.append("npm install")
            content = content.replace("{{required_tools}}", tools)
            content = content.replace(
                "{{setup_commands}}",
                joined_commands(setup),
            )
            content = content.replace(
                "{{run_commands}}",
                "\n".join(commands["run"])
                if commands["run"]
                else "# No run command detected; confirm before use",
            )
            content = content.replace(
                "{{verification_commands}}",
                joined_commands(commands["verify"]),
            )
            content = content.replace(
                "{{generation_commands}}",
                joined_commands(commands["generate"]),
            )
            content = content.replace(
                "{{lint_commands}}",
                joined_commands(commands["lint"]),
            )
            selected_facts = []
            if facts["module"]:
                selected_facts.append(f"- Module: `{facts['module']}`")
            selected_facts.extend(
                f"- Language/toolchain: {name}" for name in facts["languages"]
            )
            selected_facts.extend(
                f"- Existing module boundary: `{name}`"
                for name in facts["structure"]
            )
            if not selected_facts:
                selected_facts.append(
                    "- No reliable local-development fact detected."
                )
        else:
            selected_facts = document_facts(relative_path, facts)

        activate = selected_facts and not selected_facts[0].startswith("- No ")
        if relative_path.endswith("deployment.md"):
            activate = bool(facts["deployment"])
        if activate:
            content = content.replace("> status: stub", "> status: active", 1)
        output = (
            content
            + "\n\n## Detected Repository Facts\n\n"
            + "\n".join(selected_facts)
            + "\n"
        )
        destination = staging / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
