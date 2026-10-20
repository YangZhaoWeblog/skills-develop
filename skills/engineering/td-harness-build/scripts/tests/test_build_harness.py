"""Exercise the real builder in disposable project directories."""

from pathlib import Path
import subprocess
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[2]
TEMPLATE = (SKILL / "assets/agents.md").read_bytes()


def chapters(content):
    start = content.index("## 二、".encode())
    end = content.index("## 三、".encode(), start)
    return content[:start], content[start:end], content[end:]


class BuildHarnessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="harness-builder-")
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name)
        self.entry = self.project / "AGENTS.md"

    def build(self):
        result = subprocess.run(
            ["bash", str(SKILL / "scripts/build_harness.sh"), str(self.project),
             "--has-api=false", "--has-db=false"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_missing_entry_copies_template(self):
        self.build()
        self.assertEqual(self.entry.read_bytes(), TEMPLATE)

    def test_refresh_restores_workflow_and_preserves_project_rules(self):
        prefix = "# 自有项目\n\n## 一、Index\n\n自有入口\n\n".encode()
        suffix = "## 三、项目规则\n\n禁止更改我的约束。".encode()
        self.entry.write_bytes(prefix + "## 二、Workflow\n\nPlan -> Code\n\n".encode() + suffix)
        self.entry.chmod(0o640)
        output = self.build()
        expected = prefix + chapters(TEMPLATE)[1] + suffix
        self.assertEqual(self.entry.read_bytes(), expected)
        self.assertEqual(self.entry.stat().st_mode & 0o777, 0o640)
        self.assertIn("[WORKFLOW]", output)
        self.build()
        self.assertEqual(self.entry.read_bytes(), expected)

    def test_final_rerun_repairs_summary_written_after_initial_build(self):
        self.build()
        prefix, _, suffix = chapters(self.entry.read_bytes())
        self.entry.write_bytes(prefix + "## 二、Workflow\n\nShort summary\n\n".encode() + suffix)
        task = self.project / ".harness/plans/current/development/task/02-plan.md"
        task.parent.mkdir(parents=True)
        task.write_text("Existing plan: leave unchanged.\n")
        copied_template = self.project / ".harness/templates/development/02-plan.md"
        copied_template.write_text("Obsolete template\n")
        self.build()
        self.assertEqual(self.entry.read_bytes(), TEMPLATE)
        self.assertEqual(task.read_text(), "Existing plan: leave unchanged.\n")
        self.assertEqual(copied_template.read_bytes(),
                         (SKILL / "assets/workflows/development/02-plan.md").read_bytes())

    def test_unrecognized_or_ambiguous_chapters_require_merge(self):
        for old in (b"# My project\nKeep all rules.\n",
                    "## 二、安全红线\n禁止生产写入\n## 三、Commands\n".encode(),
                    "## 三、Rules\n## 二、Workflow\n".encode(),
                    "## 二、Workflow\n## 三、Rules\n## 三、Duplicate\n".encode(),
                    "```md\n## 二、Example\n## 三、Example\n```\n".encode(),
                    "## 二、Workflow\n## 二、Duplicate\n## 三、Rules\n".encode()):
            with self.subTest(old=old):
                self.entry.write_bytes(old)
                self.assertIn("[MERGE] AGENTS.md", self.build())
                self.assertEqual(self.entry.read_bytes(), old)

    def test_symlink_is_not_followed(self):
        external = self.project / "shared-rules.md"
        original = "# Shared rules\n## 二、Workflow\nSummary\n## 三、Private rules\n".encode()
        external.write_bytes(original)
        self.entry.symlink_to(external)
        self.assertIn("[MERGE] AGENTS.md", self.build())
        self.assertTrue(self.entry.is_symlink())
        self.assertEqual(external.read_bytes(), original)

    def test_non_file_is_not_replaced(self):
        self.entry.mkdir()
        self.assertIn("[MERGE] AGENTS.md", self.build())
        self.assertTrue(self.entry.is_dir())


if __name__ == "__main__":
    unittest.main()
