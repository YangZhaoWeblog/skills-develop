#!/usr/bin/env python3
"""Build and safely apply the canonical code-repository Harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

from project_rules import FACT_GENERATED_PATHS, rebuild_project_rules
from validate_capabilities import SOURCE_MANIFEST, validate


SKILL_ROOT = Path(__file__).resolve().parents[1]
BASELINE = SKILL_ROOT / "assets" / "baseline"
OWNERSHIP_MANIFEST = SKILL_ROOT / "assets" / "ownership-manifest.json"
GRILL_SKILLS = ("grilling", "domain-modeling", "grill-me", "grill-with-docs")
DIRECT_WRITE_PATHS = ("skills-lock.json",)
KNOWN_AGENT_ENTRIES = {"pge-generator.toml", "pge-evaluator.toml"}
GOVERNANCE_FILENAME = re.compile(
    r"(^|[-_])(workflow|gates?|pge|agents?|instructions?|governance)([-_.]|$)"
)
REASONING_EFFORT = re.compile(
    r'^model_reasoning_effort\s*=\s*"([^"]+)"$',
    re.MULTILINE,
)


def potential_managed_paths() -> list[str]:
    """List every target-relative path the Builder may write."""
    ownership = json.loads(OWNERSHIP_MANIFEST.read_text(encoding="utf-8"))
    paths = set(ownership["builder_owned"])
    paths.update(ownership["project_overlay_paths"])
    paths.update(ownership["fact_generated"])
    paths.add("skills-lock.json")
    paths.update(f".agents/skills/{name}" for name in GRILL_SKILLS)
    paths.update(
        source.relative_to(BASELINE).as_posix()
        for source in BASELINE.rglob("*")
        if not source.is_dir()
    )
    return sorted(paths)


def assert_safe_managed_paths(root: Path) -> None:
    """Reject managed writes that could follow symlinks."""
    for relative in potential_managed_paths():
        relative_path = Path(relative)
        for parent in relative_path.parents:
            if parent == Path("."):
                continue
            if (root / parent).is_symlink():
                raise ValueError(
                    "managed path ancestor is a symlink: "
                    + parent.as_posix()
                )
    for relative in DIRECT_WRITE_PATHS:
        if (root / relative).is_symlink():
            raise ValueError(
                "direct-write managed path is a symlink: " + relative
            )


def copy_tree(source: Path, destination: Path) -> None:
    """Copy a tree while preserving symlinks and file metadata."""
    shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)


def copy_skill(source: Path, destination: Path) -> None:
    """Copy an installed Skill without fixture-only provenance markers."""
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".snapshot-*"),
    )


def copy_node(source: Path, destination: Path) -> None:
    """Copy one file or symlink with its mode and target intact."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    if source.is_symlink():
        destination.symlink_to(source.readlink())
    elif source.is_dir():
        copy_tree(source, destination)
    else:
        shutil.copy2(source, destination, follow_symlinks=False)


def overlay_baseline(staging: Path) -> None:
    """Strongly replace owned files and fill only missing profile files."""
    manifest = json.loads(OWNERSHIP_MANIFEST.read_text(encoding="utf-8"))
    builder_owned = set(manifest["builder_owned"])
    builder_owned.update(manifest["fact_generated"])
    for source in sorted(path for path in BASELINE.rglob("*") if not path.is_dir()):
        relative = source.relative_to(BASELINE).as_posix()
        destination = staging / relative
        if relative in builder_owned or not (
            destination.exists() or destination.is_symlink()
        ):
            copy_node(source, destination)


def load_project_overlay(
    target: Path,
    overlay: Path | None,
) -> tuple[Path | None, list[str]]:
    """Require and validate a reviewed overlay for every existing Harness."""
    existing_harness = (target / "AGENTS.md").exists() or (
        target / "harness"
    ).is_dir()
    if overlay is None:
        if existing_harness:
            raise ValueError(
                "reviewed project overlay is required for an existing Harness"
            )
        return None, []

    manifest_path = overlay / "project-overlay.json"
    if not manifest_path.is_file():
        raise ValueError("project overlay is missing project-overlay.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("reviewed") is not True:
        raise ValueError("project overlay must be explicitly reviewed")

    ownership = json.loads(OWNERSHIP_MANIFEST.read_text(encoding="utf-8"))
    allowed = set(ownership["project_overlay_paths"])
    paths = manifest.get("project_owned_paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("project overlay must list project_owned_paths")
    unknown = sorted(set(paths) - allowed)
    if unknown:
        raise ValueError(
            "project overlay contains unclassified paths: "
            + ", ".join(unknown)
        )
    required = {
        relative
        for relative in allowed
        if (target / relative).exists() or (target / relative).is_symlink()
    }
    unreviewed = sorted(required - set(paths))
    if unreviewed:
        raise ValueError(
            "project overlay must cover existing project-owned paths: "
            + ", ".join(unreviewed)
        )
    missing = sorted(
        relative
        for relative in paths
        if not (
            (overlay / relative).exists()
            or (overlay / relative).is_symlink()
        )
    )
    if missing:
        raise ValueError(
            "project overlay is missing reviewed paths: "
            + ", ".join(missing)
        )
    return overlay, sorted(set(paths))


def apply_project_overlay(
    staging: Path,
    overlay: Path | None,
    paths: list[str],
) -> None:
    """Strongly copy every reviewed project-owned path into staging."""
    if overlay is None:
        return
    for relative in paths:
        copy_node(overlay / relative, staging / relative)


def preserve_reasoning_effort(target: Path, staging: Path) -> None:
    """Carry forward target Agent reasoning levels without carrying model."""
    for name in KNOWN_AGENT_ENTRIES:
        source = target / ".codex" / "agents" / name
        destination = staging / ".codex" / "agents" / name
        if not source.is_file() or not destination.is_file():
            continue
        match = REASONING_EFFORT.search(source.read_text(encoding="utf-8"))
        if match is None:
            continue
        content = destination.read_text(encoding="utf-8")
        content, replacements = REASONING_EFFORT.subn(
            f'model_reasoning_effort = "{match.group(1)}"',
            content,
            count=1,
        )
        if replacements != 1:
            raise ValueError(
                f"canonical Agent is missing model_reasoning_effort: {name}"
            )
        destination.write_text(content, encoding="utf-8")


def find_skill(snapshot: Path, name: str) -> Path:
    """Find one named Skill in a resolved upstream snapshot."""
    matches = sorted(
        path.parent
        for path in snapshot.rglob("SKILL.md")
        if path.parent.name == name
    )
    if len(matches) != 1:
        raise ValueError(
            f"upstream snapshot must contain exactly one {name} Skill; "
            f"found {len(matches)}"
        )
    return matches[0]


def file_digest(path: Path) -> str:
    """Return a stable SHA-256 digest for one Skill directory."""
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        relative_path = child.relative_to(path)
        if any(part.startswith(".snapshot-") for part in relative_path.parts):
            continue
        relative = relative_path.as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if child.is_symlink():
            digest.update(b"L")
            digest.update(child.readlink().as_posix().encode("utf-8"))
        elif child.is_dir():
            digest.update(b"D")
        elif child.is_file():
            digest.update(b"F")
            digest.update(child.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def skill_path_in_repository(path: Path) -> str:
    """Return the upstream-relative Skill manifest path."""
    parts = path.parts
    try:
        index = parts.index("skills")
    except ValueError as error:
        raise ValueError(f"upstream Skill is outside skills/: {path}") from error
    return Path(*parts[index:]).joinpath("SKILL.md").as_posix()


def merge_skills_lock(
    staging: Path,
    upstream_skills: dict[str, Path],
) -> None:
    """Preserve existing lock entries and add this run's Grill Skills."""
    lock_path = staging / "skills-lock.json"
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    else:
        lock = {"version": 1, "skills": {}}
    if not isinstance(lock.get("skills"), dict):
        raise ValueError("skills-lock.json must contain a skills object")
    for name, source in sorted(upstream_skills.items()):
        lock["skills"][name] = {
            "source": "mattpocock/skills",
            "sourceType": "github",
            "skillPath": skill_path_in_repository(source),
            "computedHash": file_digest(source),
        }
    lock_path.write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_fixture_evidence(snapshot: Path) -> tuple[str, str]:
    """Read deterministic snapshot evidence supplied by a test fixture."""
    commit_file = snapshot / ".snapshot-commit"
    tree_file = snapshot / ".snapshot-tree"
    if not commit_file.is_file() or not tree_file.is_file():
        raise ValueError("upstream fixture is missing snapshot evidence")
    return (
        commit_file.read_text(encoding="utf-8").strip(),
        tree_file.read_text(encoding="utf-8").strip(),
    )


def resolve_upstream_fixture(snapshot: Path) -> tuple[dict[str, Path], dict]:
    """Resolve all Grill Skills from one already-frozen fixture snapshot."""
    commit, tree = read_fixture_evidence(snapshot)
    skills = {name: find_skill(snapshot, name) for name in GRILL_SKILLS}
    for name, skill_path in skills.items():
        marker = skill_path / ".snapshot-tree"
        if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != tree:
            raise ValueError(
                f"mixed upstream snapshots: {name} does not belong to {tree}"
            )
    evidence = {
        "resolved_upstream_commit": commit,
        "resolved_upstream_tree": tree,
        "skills_cli_version": "fixture",
        "skill_sha256": {
            name: file_digest(skill_path)
            for name, skill_path in sorted(skills.items())
        },
    }
    return skills, evidence


def resolve_skills_cli_version() -> str:
    """Read the installed or cached Skills CLI version without network."""
    installed = shutil.which("skills")
    if installed is not None:
        command = [installed, "--version"]
    else:
        npx = shutil.which("npx")
        if npx is None:
            raise ValueError("skills CLI is unavailable offline")
        command = [npx, "--offline", "skills", "--version"]
    version = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if version.returncode != 0:
        detail = version.stderr.strip() or version.stdout.strip()
        raise ValueError(f"skills CLI is unavailable offline: {detail}")
    value = version.stdout.strip() or version.stderr.strip()
    if not value:
        raise ValueError("skills CLI returned an empty offline version")
    return value


def resolve_live_upstream(
    repository: str, snapshot: Path
) -> tuple[dict[str, Path], dict]:
    """Clone one current upstream snapshot and record reproducible evidence."""
    clone = subprocess.run(
        ["git", "clone", "-q", "--depth", "1", repository, str(snapshot)],
        check=False,
        capture_output=True,
        text=True,
    )
    if clone.returncode != 0:
        detail = clone.stderr.strip() or clone.stdout.strip()
        raise ValueError(f"failed to resolve upstream snapshot: {detail}")

    commit = subprocess.run(
        ["git", "-C", str(snapshot), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "-C", str(snapshot), "rev-parse", "HEAD^{tree}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    skills = {name: find_skill(snapshot, name) for name in GRILL_SKILLS}
    cli_version = resolve_skills_cli_version()
    evidence = {
        "resolved_upstream_commit": commit,
        "resolved_upstream_tree": tree,
        "skills_cli_version": cli_version,
        "skill_sha256": {
            name: file_digest(skill_path)
            for name, skill_path in sorted(skills.items())
        },
    }
    return skills, evidence


def assert_git_repository(target: Path) -> None:
    """Reject targets that are not existing Git code repositories."""
    if not target.is_dir():
        raise ValueError(f"target is not a directory: {target}")
    result = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise ValueError(f"target is not a Git repository: {target}")


def classify_target(target: Path) -> None:
    """Block unclassified executable Agent entries before staging."""
    agent_directory = target / ".codex" / "agents"
    unknown = (
        sorted(
            path.relative_to(target).as_posix()
            for path in agent_directory.glob("*.toml")
            if path.name not in KNOWN_AGENT_ENTRIES
        )
        if agent_directory.is_dir()
        else []
    )
    if unknown:
        raise ValueError(
            "unknown execution entry: " + ", ".join(unknown)
        )

    ownership = json.loads(OWNERSHIP_MANIFEST.read_text(encoding="utf-8"))
    known_harness = {
        Path(relative).as_posix()
        for relative in (
            ownership["builder_owned"] + ownership["project_overlay_paths"]
            + ownership["fact_generated"]
        )
        if relative.startswith("harness/")
    }
    governance_extensions = sorted(
        path.relative_to(target).as_posix()
        for path in (target / "harness").rglob("*")
        if path.is_file()
        and path.relative_to(target).as_posix() not in known_harness
        and GOVERNANCE_FILENAME.search(path.name.lower())
    ) if (target / "harness").is_dir() else []
    if governance_extensions:
        raise ValueError(
            "unknown governance extension: "
            + ", ".join(governance_extensions)
        )


def build_staging(
    target: Path,
    staging: Path,
    upstream_skills: dict[str, Path],
    project_overlay: Path | None,
    project_overlay_paths: list[str],
) -> None:
    """Build a complete candidate without writing the target repository."""
    if staging.exists():
        raise ValueError(f"staging path already exists: {staging}")
    assert_safe_managed_paths(target)
    shutil.copytree(
        target,
        staging,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git"),
    )
    assert_safe_managed_paths(staging)
    overlay_baseline(staging)
    apply_project_overlay(staging, project_overlay, project_overlay_paths)
    rebuild_project_rules(target, staging, BASELINE)
    preserve_reasoning_effort(target, staging)
    for name, source in upstream_skills.items():
        destination = staging / ".agents" / "skills" / name
        if destination.exists() or destination.is_symlink():
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        copy_skill(source, destination)
    merge_skills_lock(staging, upstream_skills)

    failures = validate(SOURCE_MANIFEST, staging)
    if failures:
        raise ValueError("source validation failed:\n" + "\n".join(failures))


def managed_paths(
    target: Path,
    staging: Path,
    project_overlay_paths: list[str],
) -> list[str]:
    """List the only paths that a successful apply may replace."""
    manifest = json.loads(OWNERSHIP_MANIFEST.read_text(encoding="utf-8"))
    paths = set(manifest["builder_owned"])
    paths.update(project_overlay_paths)
    paths.update(FACT_GENERATED_PATHS)
    paths.add("skills-lock.json")
    paths.update(f".agents/skills/{name}" for name in GRILL_SKILLS)
    for source in sorted(path for path in BASELINE.rglob("*") if not path.is_dir()):
        relative = source.relative_to(BASELINE).as_posix()
        destination = target / relative
        if not (destination.exists() or destination.is_symlink()):
            paths.add(relative)
    return sorted(
        relative
        for relative in paths
        if (staging / relative).exists() or (staging / relative).is_symlink()
    )


def remove_node(path: Path) -> None:
    """Remove one existing node without following symlinks."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def tree_digest(root: Path) -> tuple[str, int]:
    """Digest path, type, mode, file bytes, and symlink targets."""
    digest = hashlib.sha256()
    count = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        count += 1
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(stat.S_IMODE(path.lstat().st_mode)).encode("ascii"))
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"L\0")
            digest.update(path.readlink().as_posix().encode("utf-8"))
        elif path.is_dir():
            digest.update(b"D")
        elif path.is_file():
            digest.update(b"F\0")
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest(), count


def backup_target(target: Path, backup: Path) -> None:
    """Back up every target node except Git internals."""
    shutil.copytree(
        target,
        backup,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git"),
    )


def restore_target(target: Path, backup: Path) -> None:
    """Restore all non-Git target nodes to their pre-apply bytes and modes."""
    for child in target.iterdir():
        if child.name != ".git":
            remove_node(child)
    copy_tree(backup, target)


def apply_staging(
    target: Path,
    staging: Path,
    project_overlay_paths: list[str],
    failpoint: str | None,
) -> dict:
    """Apply a validated staging tree under a complete rollback backup."""
    assert_safe_managed_paths(target)
    before_digest, before_nodes = tree_digest(target)
    with tempfile.TemporaryDirectory() as tmp_dir:
        backup = Path(tmp_dir) / "backup"
        backup_target(target, backup)
        if failpoint == "backup":
            raise ValueError("injected failpoint: backup")

        try:
            for index, relative in enumerate(
                managed_paths(target, staging, project_overlay_paths)
            ):
                assert_safe_managed_paths(target)
                copy_node(staging / relative, target / relative)
                if failpoint == "apply" and index == 0:
                    raise ValueError("injected failpoint: apply")

            failures = validate(SOURCE_MANIFEST, target)
            if failures:
                raise ValueError(
                    "post-check source validation failed:\n"
                    + "\n".join(failures)
                )
            if failpoint == "post-check":
                raise ValueError("injected failpoint: post-check")
        except BaseException:
            restore_target(target, backup)
            restored_digest, _ = tree_digest(target)
            if restored_digest != before_digest:
                raise RuntimeError(
                    "rollback failed to restore the complete target digest"
                )
            raise
    after_digest, after_nodes = tree_digest(target)
    return {
        "before_sha256": before_digest,
        "after_sha256": after_digest,
        "before_nodes": before_nodes,
        "after_nodes": after_nodes,
        "digest_fields": [
            "path",
            "type",
            "mode",
            "content_or_symlink_target",
        ],
    }


def parse_args() -> argparse.Namespace:
    """Parse the Harness Builder command line."""
    parser = argparse.ArgumentParser(
        description="Build and safely apply the canonical repository Harness."
    )
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--staging-only", type=Path)
    parser.add_argument("--upstream-fixture", type=Path)
    parser.add_argument("--project-overlay", type=Path)
    parser.add_argument(
        "--upstream-repository",
        default="https://github.com/mattpocock/skills.git",
    )
    parser.add_argument(
        "--failpoint",
        choices=("classify", "source-validation", "backup", "apply", "post-check"),
    )
    return parser.parse_args()


def main() -> int:
    """Run the Harness Builder command."""
    args = parse_args()
    try:
        target = args.target.resolve()
        assert_git_repository(target)
        assert_safe_managed_paths(target)
        classify_target(target)
        project_overlay = (
            args.project_overlay.resolve()
            if args.project_overlay is not None
            else None
        )
        if project_overlay is not None:
            assert_safe_managed_paths(project_overlay)
        project_overlay, project_overlay_paths = load_project_overlay(
            target,
            project_overlay,
        )
        if args.failpoint == "classify":
            raise ValueError("injected failpoint: classify")
        if args.upstream_fixture is not None:
            upstream_skills, evidence = resolve_upstream_fixture(
                args.upstream_fixture.resolve()
            )
            if args.staging_only is not None:
                staging = args.staging_only.resolve()
                build_staging(
                    target,
                    staging,
                    upstream_skills,
                    project_overlay,
                    project_overlay_paths,
                )
                digest, nodes = tree_digest(target)
                transaction_summary = {
                    "before_sha256": digest,
                    "after_sha256": digest,
                    "before_nodes": nodes,
                    "after_nodes": nodes,
                    "digest_fields": [
                        "path",
                        "type",
                        "mode",
                        "content_or_symlink_target",
                    ],
                }
            else:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    staging = Path(tmp_dir) / "staging"
                    build_staging(
                        target,
                        staging,
                        upstream_skills,
                        project_overlay,
                        project_overlay_paths,
                    )
                    if args.failpoint == "source-validation":
                        raise ValueError("injected failpoint: source-validation")
                    transaction_summary = apply_staging(
                        target,
                        staging,
                        project_overlay_paths,
                        args.failpoint,
                    )
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                upstream_skills, evidence = resolve_live_upstream(
                    args.upstream_repository,
                    Path(tmp_dir) / "upstream",
                )
                staging = (
                    args.staging_only.resolve()
                    if args.staging_only is not None
                    else Path(tmp_dir) / "staging"
                )
                build_staging(
                    target,
                    staging,
                    upstream_skills,
                    project_overlay,
                    project_overlay_paths,
                )
                if args.staging_only is not None:
                    digest, nodes = tree_digest(target)
                    transaction_summary = {
                        "before_sha256": digest,
                        "after_sha256": digest,
                        "before_nodes": nodes,
                        "after_nodes": nodes,
                        "digest_fields": [
                            "path",
                            "type",
                            "mode",
                            "content_or_symlink_target",
                        ],
                    }
                else:
                    if args.failpoint == "source-validation":
                        raise ValueError(
                            "injected failpoint: source-validation"
                        )
                    transaction_summary = apply_staging(
                        target,
                        staging,
                        project_overlay_paths,
                        args.failpoint,
                    )
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"[BLOCK] {error}", file=sys.stderr)
        return 1

    evidence["transaction_summary"] = transaction_summary
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
