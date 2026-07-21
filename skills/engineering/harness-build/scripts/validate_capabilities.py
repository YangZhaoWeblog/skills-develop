#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path


JSON_FENCE = re.compile(r"```json[^\n]*\n(.*?)```", re.DOTALL)
MERMAID_FENCE = re.compile(r"```mermaid[^\n]*\n(.*?)```", re.DOTALL)
SKILL_REFERENCE = re.compile(r"\$([a-z0-9][a-z0-9-]*)")
SOURCE_MANIFEST = (
    Path(__file__).resolve().parents[1] / "assets" / "capability-manifest.json"
)


def staged_regular_file(
    staging: Path,
    relative_path: str,
    capability_id: str,
    failures: list[str],
) -> Path | None:
    """Resolve one staged file without accepting an external symlink."""
    try:
        root = staging.resolve(strict=True)
        resolved = (staging / relative_path).resolve(strict=True)
    except FileNotFoundError:
        failures.append(f"{capability_id}: missing {relative_path}")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        failures.append(
            f"{capability_id}: {relative_path} escapes the staged repository"
        )
        return None
    if not resolved.is_file():
        failures.append(
            f"{capability_id}: {relative_path} is not a regular file"
        )
        return None
    return resolved


def validate_human_start_revision_bound(
    staging: Path, capability: dict
) -> list[str]:
    capability_id = capability["id"]
    failures = []

    spec_relative_path = capability["spec_template"]
    spec_path = staging / spec_relative_path
    contracts = []
    if not spec_path.is_file():
        failures.append(f"{capability_id}: missing {spec_relative_path}")
    else:
        content = spec_path.read_text(encoding="utf-8")
        for block in JSON_FENCE.findall(content):
            try:
                candidate = json.loads(block)
            except json.JSONDecodeError:
                continue
            if (
                isinstance(candidate, dict)
                and "contract_revision" in candidate
                and "human_start_gate" in candidate
            ):
                contracts.append(candidate)

    if len(contracts) != 1:
        failures.append(
            f"{capability_id}: {spec_relative_path} must contain exactly one "
            "Human Start JSON block"
        )
    else:
        gate = contracts[0]["human_start_gate"]
        if not isinstance(gate, dict):
            failures.append(
                f"{capability_id}: human_start_gate must be a JSON object"
            )
        else:
            for field in (
                "status",
                "approved_contract_revision",
                "channel",
                "evidence",
            ):
                if field not in gate:
                    failures.append(
                        f"{capability_id}: human_start_gate missing {field}"
                    )

    protocol = capability["protocol"]
    protocol_path = staging / protocol["path"]
    if not protocol_path.is_file():
        failures.append(f"{capability_id}: missing {protocol['path']}")
    else:
        protocol_lines = set(
            protocol_path.read_text(encoding="utf-8").splitlines()
        )
        for required_line in protocol["required_lines"]:
            if required_line not in protocol_lines:
                failures.append(
                    f"{capability_id}: {protocol['path']} missing "
                    f"{required_line!r}"
                )

    checker = capability["checker"]
    checker_path = staging / checker["path"]
    if not checker_path.is_file():
        failures.append(f"{capability_id}: missing {checker['path']}")
    else:
        digest = hashlib.sha256(checker_path.read_bytes()).hexdigest()
        if digest not in checker["sha256_allowlist"]:
            failures.append(
                f"{capability_id}: {checker['path']} has unapproved SHA-256 "
                f"{digest}"
            )
    return failures


def validate_mermaid_control_flow(staging: Path, capability: dict) -> list[str]:
    capability_id = capability["id"]
    expected_path = capability["path"]
    failures = []
    protocol_path = staging / expected_path
    blocks = (
        MERMAID_FENCE.findall(protocol_path.read_text(encoding="utf-8"))
        if protocol_path.is_file()
        else []
    )
    if len(blocks) != 1:
        failures.append(
            f"{capability_id}: {expected_path} must contain exactly one "
            "normative Mermaid fence"
        )

    diagram = blocks[0] if len(blocks) == 1 else ""
    required_edges = set(capability["required_edges"])
    for relative_path in capability.get("exclusive_paths", []):
        candidate_path = staging / relative_path
        if not candidate_path.is_file():
            continue
        for candidate in MERMAID_FENCE.findall(
            candidate_path.read_text(encoding="utf-8")
        ):
            candidate_lines = {
                " ".join(line.split()) for line in candidate.splitlines()
            }
            if required_edges.issubset(candidate_lines):
                failures.append(
                    f"{capability_id}: normative diagram duplicated in "
                    f"{relative_path}"
                )

    for node in capability["required_nodes"]:
        if re.search(rf"\b{re.escape(node)}\b", diagram) is None:
            failures.append(f"{capability_id}: missing node {node}")

    diagram_lines = {" ".join(line.split()) for line in diagram.splitlines()}
    for edge in required_edges:
        if edge not in diagram_lines:
            failures.append(f"{capability_id}: missing edge {edge}")
    return failures


def validate_toml_absent_top_level_key(
    staging: Path, capability: dict
) -> list[str]:
    capability_id = capability["id"]
    key = capability["key"]
    failures = []
    for relative_path in capability["paths"]:
        source_path = staging / relative_path
        if not source_path.is_file():
            failures.append(f"{capability_id}: missing {relative_path}")
            continue
        try:
            content = tomllib.loads(source_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            failures.append(f"{capability_id}: invalid TOML {relative_path}: {error}")
            continue
        if key in content:
            failures.append(
                f"{capability_id}: {relative_path} has forbidden top-level key {key}"
            )
    return failures


def validate_agent_context_contract(
    staging: Path, capability: dict
) -> list[str]:
    """Validate static context references without executing staged code."""
    capability_id = capability["id"]
    failures = []

    required_context_paths = {
        reference.removeprefix("@")
        for agent in capability["agents"]
        for reference in agent["references"]
    }
    for relative_path in sorted(required_context_paths):
        staged_regular_file(
            staging,
            relative_path,
            capability_id,
            failures,
        )

    resolver = capability["resolver"]
    resolver_path = staged_regular_file(
        staging,
        resolver["path"],
        capability_id,
        failures,
    )
    if resolver_path is not None:
        digest = hashlib.sha256(resolver_path.read_bytes()).hexdigest()
        if digest not in resolver["sha256_allowlist"]:
            failures.append(
                f"{capability_id}: {resolver['path']} has unapproved SHA-256 "
                f"{digest}"
            )

    forbidden = capability.get("forbidden_agent_phrases", [])
    for agent in capability["agents"]:
        relative_path = agent["path"]
        source_path = staged_regular_file(
            staging,
            relative_path,
            capability_id,
            failures,
        )
        if source_path is None:
            continue
        try:
            document = tomllib.loads(source_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
            failures.append(
                f"{capability_id}: invalid Agent TOML {relative_path}: {error}"
            )
            continue
        instructions = document.get("developer_instructions")
        if not isinstance(instructions, str):
            failures.append(
                f"{capability_id}: {relative_path} lacks developer_instructions"
            )
            continue
        references = [
            line for line in instructions.splitlines() if line.startswith("@")
        ]
        if references != agent["references"]:
            failures.append(
                f"{capability_id}: {relative_path} must contain standalone "
                f"references in order {agent['references']!r}"
            )
        for phrase in agent["required_phrases"]:
            if phrase not in instructions:
                failures.append(
                    f"{capability_id}: {relative_path} missing {phrase!r}"
                )
        for phrase in forbidden:
            if phrase in instructions:
                failures.append(
                    f"{capability_id}: {relative_path} copies schema marker "
                    f"{phrase!r}"
                )

    for document in capability["dispatch_documents"]:
        relative_path = document["path"]
        source_path = staged_regular_file(
            staging,
            relative_path,
            capability_id,
            failures,
        )
        if source_path is None:
            continue
        content = source_path.read_text(encoding="utf-8")
        for phrase in document["required_phrases"]:
            if phrase not in content:
                failures.append(
                    f"{capability_id}: {relative_path} missing {phrase!r}"
                )
    return failures


def validate_skill_toolchain(staging: Path, capability: dict) -> list[str]:
    capability_id = capability["id"]
    failures = []
    for relative_path in capability["paths"]:
        if not (staging / relative_path).is_file():
            failures.append(f"{capability_id}: missing {relative_path}")

    return failures


def validate_skill_references(staging: Path, capability: dict) -> list[str]:
    capability_id = capability["id"]
    references = set()
    for relative_path in capability["paths"]:
        path = staging / relative_path
        candidates = sorted(path.rglob("*.md")) if path.is_dir() else [path]
        for candidate in candidates:
            if candidate.is_file():
                references.update(
                    SKILL_REFERENCE.findall(
                        candidate.read_text(encoding="utf-8")
                    )
                )

    failures = []
    skill_root = staging / capability["skill_root"]
    for name in sorted(references):
        if not (skill_root / name / "SKILL.md").is_file():
            failures.append(
                f"{capability_id}: ${name} has no installed Skill"
            )
    return failures


def validate_fact_generated_documents(
    staging: Path, capability: dict
) -> list[str]:
    """Require every repository-fact document to come from the current build."""
    failures = []
    for relative_path in capability["paths"]:
        path = staging / relative_path
        if not path.is_file():
            failures.append(f"{capability['id']}: missing {relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        if capability["marker"] not in content:
            failures.append(
                f"{capability['id']}: {relative_path} was not regenerated"
            )
        if "{{" in content or "}}" in content:
            failures.append(
                f"{capability['id']}: {relative_path} contains an unresolved template"
            )
    return failures


def validate(manifest_path: Path, staging: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for capability in manifest["capabilities"]:
        if capability["kind"] == "human_start_revision_bound":
            failures.extend(
                validate_human_start_revision_bound(staging, capability)
            )
        elif capability["kind"] == "mermaid_control_flow":
            failures.extend(validate_mermaid_control_flow(staging, capability))
        elif capability["kind"] == "toml_absent_top_level_key":
            failures.extend(validate_toml_absent_top_level_key(staging, capability))
        elif capability["kind"] == "agent_context_contract":
            failures.extend(validate_agent_context_contract(staging, capability))
        elif capability["kind"] == "skill_toolchain":
            failures.extend(validate_skill_toolchain(staging, capability))
        elif capability["kind"] == "skill_references":
            failures.extend(validate_skill_references(staging, capability))
        elif capability["kind"] == "fact_generated_documents":
            failures.extend(
                validate_fact_generated_documents(staging, capability)
            )
        else:
            failures.append(
                f"{capability['id']}: unsupported capability kind "
                f"{capability['kind']!r}"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a staged Harness against source-owned capabilities."
    )
    parser.add_argument("--staging", required=True, type=Path)
    args = parser.parse_args()

    failures = validate(SOURCE_MANIFEST, args.staging)
    if failures:
        for failure in failures:
            print(f"[BLOCK] {failure}", file=sys.stderr)
        return 1

    print("[OK] source capabilities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
