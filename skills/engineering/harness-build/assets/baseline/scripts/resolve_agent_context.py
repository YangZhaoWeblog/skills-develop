#!/usr/bin/env python3
"""Resolve Harness-owned Agent context references before dispatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import tomllib
from pathlib import Path, PurePosixPath


def sha256(content: bytes) -> str:
    """Return the hexadecimal SHA-256 for bytes."""
    return hashlib.sha256(content).hexdigest()


def section(relative: str, content: bytes) -> bytes:
    """Frame exact referenced bytes in a deterministic Markdown section."""
    digest = sha256(content)
    encoded_path = json.dumps(relative, ensure_ascii=False)
    begin = (
        f"<!-- harness-context-v1 begin path={encoded_path} "
        f"byte_length={len(content)} sha256={digest} -->\n"
    ).encode("utf-8")
    end = (
        f"\n<!-- harness-context-v1 end path={encoded_path} -->\n"
    ).encode("utf-8")
    return begin + content + end


def ensure_within_repository(root: Path, path: Path, label: str) -> Path:
    """Resolve a path and reject real paths outside the repository."""
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as error:
        raise ValueError(f"missing {label}: {path}") from error
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes repository: {path}") from error
    return resolved


def resolve_reference(root: Path, reference: str) -> tuple[str, bytes]:
    """Validate one canonical repo-relative reference and read exact bytes."""
    if "\x00" in reference or "\\" in reference:
        raise ValueError(f"invalid repository-relative reference: {reference!r}")
    relative = PurePosixPath(reference)
    if relative.is_absolute():
        raise ValueError(f"absolute reference is forbidden: {reference}")
    if ".." in relative.parts:
        raise ValueError(f"parent traversal is forbidden: {reference}")
    canonical = relative.as_posix()
    if canonical in ("", ".") or canonical != reference:
        raise ValueError(f"reference must be canonical: {reference!r}")

    resolved = ensure_within_repository(
        root,
        root.joinpath(*relative.parts),
        "reference",
    )
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError(f"reference target is not a regular file: {reference}")
    content = resolved.read_bytes()
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"reference is not valid UTF-8: {reference}") from error
    return canonical, content


def parse_args() -> argparse.Namespace:
    """Parse the resolver command line."""
    parser = argparse.ArgumentParser(
        description="Resolve standalone @path references from a PGE Agent TOML."
    )
    parser.add_argument("--agent", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    """Write the deterministic context bundle and receipt."""
    args = parse_args()
    try:
        root = args.repo_root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"repository root is not a directory: {root}")
        agent = args.agent if args.agent.is_absolute() else root / args.agent
        agent = ensure_within_repository(root, agent, "Agent TOML")
        if not stat.S_ISREG(agent.stat().st_mode):
            raise ValueError(f"Agent TOML is not a regular file: {agent}")
        agent_relative = agent.relative_to(root).as_posix()
        agent_bytes = agent.read_bytes()
        agent_text = agent_bytes.decode("utf-8")
        parsed = tomllib.loads(agent_text)
        instructions = parsed.get("developer_instructions")
        if not isinstance(instructions, str):
            raise ValueError("Agent TOML must contain developer_instructions")
        references = [
            line[1:]
            for line in instructions.splitlines()
            if line.startswith("@") and line == line.strip()
        ]
        if not references:
            raise ValueError("Agent TOML has no standalone @path references")
        duplicates = sorted(
            reference
            for reference in set(references)
            if references.count(reference) > 1
        )
        if duplicates:
            raise ValueError(
                "duplicate @path reference: " + ", ".join(duplicates)
            )

        resolved = []
        sections = []
        for relative in references:
            relative, content = resolve_reference(root, relative)
            resolved.append(
                {
                    "path": relative,
                    "sha256": sha256(content),
                    "byte_length": len(content),
                }
            )
            sections.append(section(relative, content))

        bundle = b"".join(sections)
        receipt = {
            "schema_version": 1,
            "agent": {
                "path": agent_relative,
                "sha256": sha256(agent_bytes),
            },
            "references": resolved,
            "bundle": {
                "sha256": sha256(bundle),
                "byte_length": len(bundle),
            },
        }
        receipt_bytes = (
            json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(bundle)
        args.receipt.write_bytes(receipt_bytes)
    except (OSError, UnicodeDecodeError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"[BLOCK] {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "bundle_sha256": sha256(bundle),
                "receipt_sha256": sha256(receipt_bytes),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
