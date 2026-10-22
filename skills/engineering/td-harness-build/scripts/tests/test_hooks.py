"""Run hook scripts against staged files in disposable Git repositories."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]


class HookTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="harness-hooks-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_") and key not in
                    {"SKIP_PRE_COMMIT", "SKIP_PRE_PUSH", "AI_TEST_GUARD", "SKIP_TEST_GUARD"}}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.run_command("git", "init", "-q", check=True)

    def run_command(self, *args, check=False):
        return subprocess.run(args, cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=check)

    def stage(self, content):
        path = self.root / "README.md"
        path.write_text(content)
        self.run_command("git", "add", "--", path.name, check=True)
        return path

    def run_hook(self, name="pre_commit_check.sh", body="  true"):
        source = (SCRIPTS / name).read_text()
        start = source.index("  # HARNESS_PROJECT_CHECKS_PENDING")
        end = source.index("\n}", start)
        hook = self.root / name
        hook.write_text(source[:start] + body + source[end:])
        return self.run_command("bash", str(hook))

    def test_markdown_headings_and_separators_pass(self):
        for separator in ("=======", "========", "=======  "):
            with self.subTest(separator=separator):
                self.stage("Valid title\n" + separator + "\n")
                result = self.run_hook()
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_conflicts_and_remaining_markers_block(self):
        cases = (
            "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> topic\n",
            "<<<<<<< HEAD\nours\n||||||| base\nbase\n=======\ntheirs\n>>>>>>> topic\n",
            "<<<<<<< HEAD\nremaining\n",
            "remaining\n>>>>>>> topic\n",
            "||||||| base\nremaining\n",
            "<<<<<<<<<< HEAD\nours\n==========\ntheirs\n>>>>>>>>>> topic\n",
        )
        for content in cases:
            with self.subTest(content=content):
                self.stage(content)
                result = self.run_hook()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unresolved merge markers", result.stderr)

    def test_checks_staged_content_not_unstaged_fix(self):
        path = self.stage("<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> topic\n")
        path.write_text("Resolved in working tree only\n")
        result = self.run_hook()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unresolved merge markers", result.stderr)

    def test_unstaged_conflict_does_not_change_staged_content_check(self):
        path = self.stage("Valid title\n=======\n")
        path.write_text("<<<<<<< HEAD\nnot staged\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_failure_is_not_hidden_by_later_success(self):
        self.stage("Valid content\n")
        for name in ("pre_commit_check.sh", "pre_push_check.sh"):
            with self.subTest(hook=name):
                result = self.run_hook(name, "  false\n  echo SHOULD_NOT_RUN")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("SHOULD_NOT_RUN", result.stdout)
                self.assertNotIn("[OK]", result.stdout)

    def test_successful_push_check_passes(self):
        result = self.run_hook("pre_push_check.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[OK]", result.stdout)


if __name__ == "__main__":
    unittest.main()
