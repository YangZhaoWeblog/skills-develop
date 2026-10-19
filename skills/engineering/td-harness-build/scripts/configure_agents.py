#!/usr/bin/env python3
"""Render project-scoped native agents. Requires Python 3.11+; no packages."""
import argparse
import json
import os
from pathlib import Path
import string
import sys
import tomllib

ROLES = {
    "coder": ("Coder", "Implement approved plans and tests; report changes and evidence."),
    "verifier": ("Verifier", "Verify the current implementation against selected checks; report failures and evidence."),
    "reviewer": ("Reviewer", "Independently review requirements, changes, and verification evidence."),
    "executor": ("Executor", "Update assigned documents and execute explicitly authorized mechanical operations."),
}


def value(text):
    if not text.strip() or any(ord(c) < 32 or ord(c) == 127 for c in text):
        raise argparse.ArgumentTypeError("Use a non-empty value without control characters.")
    return text


def safe_directory(path):
    """Reject linked ancestors before reading or creating project files."""
    for part in (*reversed(path.parents), path):
        if part.is_symlink() or (part.exists() and not part.is_dir()):
            raise ValueError(f"Directory needs review: {part}")


def render(platform, role, model, effort):
    label, description = ROLES[role]
    name = f"harness-{role}"
    instructions = (
        f"You are the {label}. Before acting, read project AGENTS.md and "
        f".harness/agents.md, then follow the {label} responsibilities and shared handoff rules. "
        "Read the current task sources identified by the parent. If required guidance is missing, "
        "report the gap before acting. Work only within the assigned scope and authorization."
    )
    quote = lambda text: json.dumps(text, ensure_ascii=False)
    suffix = "toml" if platform == "codex" else "md"
    template = Path(__file__).resolve().parent.parent / "assets/native-agents" / f"{platform}.{suffix}.tmpl"
    field = "model_reasoning_effort" if platform == "codex" else "effort"
    assignment = " = " if platform == "codex" else ": "
    settings = f"{field}{assignment}{quote(effort)}\n" if effort else ""
    output = string.Template(template.read_text()).substitute(
        name=quote(name), description=quote(description), model=quote(model),
        effort_setting=settings, instructions=quote(instructions) if platform == "codex" else instructions,
    )
    if platform == "codex":
        parsed = tomllib.loads(output)
    else:
        # This template uses only flat JSON-quoted string values, a YAML subset.
        frontmatter = output.split("---\n", 2)[1]
        parsed = {key: json.loads(raw.strip()) for key, raw in
                  (line.split(":", 1) for line in frontmatter.splitlines())}
    for key, expected in (("name", name), ("model", model), ("description", description)):
        if parsed[key] != expected:
            raise ValueError(f"Template did not preserve {key}")
    return f"{name}.{suffix}", output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--platform", choices=("codex", "claude"), required=True)
    parser.add_argument("--strong-model", type=value, required=True)
    parser.add_argument("--economy-model", type=value, required=True)
    parser.add_argument("--strong-effort", type=value)
    parser.add_argument("--economy-effort", type=value)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(os.path.abspath(args.project))
    safe_directory(root)
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    safe_directory(root / ".harness")
    for required in (root / "AGENTS.md", root / ".harness/agents.md"):
        if not required.is_file():
            raise ValueError(f"Required guidance is missing: {required}")
    destination = root / f".{args.platform}" / "agents"
    safe_directory(destination)
    pending = []
    conflicts = []
    for role in ROLES:
        strong = role in ("verifier", "reviewer")
        model = args.strong_model if strong else args.economy_model
        effort = args.strong_effort if strong else args.economy_effort
        name, content = render(args.platform, role, model, effort)
        path = destination / name
        if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_text() != content)):
            conflicts.append(path)
        elif path.exists():
            print(f"[KEEP] {path}")
        else:
            pending.append((path, content))
    if conflicts:
        for path in conflicts:
            print(f"[CONFLICT] Existing entry retained: {path}", file=sys.stderr)
        print("[BLOCK] No files written. Review existing definitions before merging.", file=sys.stderr)
        return 3
    for path, content in pending:
        if not args.dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        print(f"[{'WOULD ADD' if args.dry_run else 'ADD'}] {path}")
    print("[PREVIEW] No files written." if args.dry_run else
          "[PREPARED] Configurations rendered; agent discovery and actual invocation remain unverified.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        sys.exit(2)
