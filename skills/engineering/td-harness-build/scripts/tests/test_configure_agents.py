"""Behavior checks for native-agent rendering; no model calls or installation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "configure_agents.py"


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / ".harness").mkdir()
        (self.root / "AGENTS.md").write_text("Project entry")
        (self.root / ".harness/agent-roles.md").write_text("Role rules")

    def run_renderer(self, platform="codex", *extra, expected=0):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root), "--platform", platform,
             "--strong-model", 'strong:"quoted"\\model', "--economy-model", "cheap/model", *extra],
            text=True, capture_output=True,
        )
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        return proc

    def test_both_platforms_roundtrip_and_repeat(self):
        for platform, extension in (("codex", "toml"), ("claude", "md")):
            with self.subTest(platform=platform):
                self.run_renderer(platform, "--strong-effort", "high", "--economy-effort", "low")
                files = sorted((self.root / f".{platform}/agents").glob(f"*.{extension}"))
                self.assertEqual(len(files), 4)
                before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
                for path in files:
                    text = path.read_text()
                    if platform == "codex":
                        data = tomllib.loads(text)
                        self.assertNotIn("sandbox_mode", data)
                        self.assertNotIn("approval_policy", data)
                        instructions = data["developer_instructions"]
                        effort = data["model_reasoning_effort"]
                    else:
                        header, instructions = text.split("---\n")[1:]
                        data = {k: json.loads(v) for k, v in
                                (line.split(":", 1) for line in header.splitlines())}
                        effort = data["effort"]
                    strong = "verifier" in path.name or "reviewer" in path.name
                    self.assertEqual(data["model"], 'strong:"quoted"\\model' if strong else "cheap/model")
                    self.assertEqual(effort, "high" if strong else "low")
                    self.assertIn(".harness/agent-roles.md", instructions)
                    self.assertNotIn(".harness/agents.md", instructions)
                self.run_renderer(platform, "--strong-effort", "high", "--economy-effort", "low")
                self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files})

    def test_preview_writes_nothing(self):
        self.run_renderer("codex", "--dry-run")
        self.assertFalse((self.root / ".codex").exists())

    def test_conflict_blocks_whole_batch(self):
        target = self.root / ".codex/agents"
        target.mkdir(parents=True)
        path = target / "harness-verifier.toml"
        path.write_text("USER CONTENT")
        self.run_renderer(expected=3)
        self.assertEqual(list(target.iterdir()), [path])
        self.assertEqual(path.read_text(), "USER CONTENT")

    def test_directory_and_file_symlinks_preserved(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".codex").symlink_to(outside, target_is_directory=True)
        self.run_renderer(expected=2)
        self.assertEqual(list(outside.iterdir()), [])
        (self.root / ".codex").unlink()
        target = self.root / ".codex/agents"
        target.mkdir(parents=True)
        link = target / "harness-coder.toml"
        link.symlink_to(outside / "missing")
        self.run_renderer(expected=3)
        self.assertTrue(link.is_symlink())
        self.assertEqual(list(target.iterdir()), [link])

    def test_missing_guidance_and_invalid_parameters(self):
        (self.root / ".harness/agent-roles.md").unlink()
        self.run_renderer(expected=2)
        self.assertFalse((self.root / ".codex").exists())
        (self.root / ".harness/agent-roles.md").write_text("Role rules")
        for value in ("", "   ", "bad\nmodel"):
            self.run_renderer("codex", "--strong-model", value, expected=2)
        self.assertFalse((self.root / ".codex").exists())

    def test_parameters_are_data_not_shell(self):
        model = '$(touch SHOULD_NOT_EXIST); `echo hello` 😀'
        self.run_renderer("codex", "--strong-model", model)
        data = tomllib.loads((self.root / ".codex/agents/harness-reviewer.toml").read_text())
        self.assertEqual(data["model"], model)
        self.assertFalse((self.root / "SHOULD_NOT_EXIST").exists())
        self.assertNotIn("model_reasoning_effort", data)

    def test_legacy_guidance_alone_does_not_satisfy_new_role_entry(self):
        (self.root / ".harness/agent-roles.md").rename(self.root / ".harness/agents.md")
        for platform in ("codex", "claude"):
            with self.subTest(platform=platform):
                self.run_renderer(platform, expected=2)
                self.assertFalse((self.root / f".{platform}").exists())


if __name__ == "__main__":
    unittest.main()
