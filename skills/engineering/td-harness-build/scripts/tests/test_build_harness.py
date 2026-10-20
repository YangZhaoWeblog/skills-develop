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

    def build(self, *options):
        result = subprocess.run(
            ["bash", str(SKILL / "scripts/build_harness.sh"), str(self.project),
             "--has-api=false", "--has-db=false", *options],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_missing_entry_copies_template(self):
        self.build()
        self.assertEqual(self.entry.read_bytes(), TEMPLATE)
        self.assertTrue((self.project / ".harness/agent-roles.md").is_file())
        self.assertFalse((self.project / ".harness/agents.md").exists())

    def test_legacy_role_document_requires_review_and_is_not_shadowed(self):
        old = self.project / ".harness/agents.md"
        old.parent.mkdir()
        content = "Custom role boundaries and previous verification evidence.\n"
        old.write_text(content)
        result = subprocess.run(
            ["bash", str(SKILL / "scripts/build_harness.sh"), str(self.project)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(set(self.project.rglob("*")), {old.parent, old})
        self.assertEqual(old.read_text(), content)
        self.assertIn(".harness/agents.md", result.stdout)
        output = self.build("--accept-migrations")
        self.assertIn("[MERGE] Populate .harness/agent-roles.md", output)
        self.assertEqual(old.read_text(), content)
        new = self.project / ".harness/agent-roles.md"
        self.assertFalse(new.exists())
        self.assertFalse(new.is_symlink())

        # The approved semantic merge belongs to the caller; reruns retain it.
        old.rename(new)
        self.build()
        self.assertEqual(new.read_text(), content)

    def test_role_document_migration_preserves_both_existing_versions(self):
        folder = self.project / ".harness"
        folder.mkdir()
        old = folder / "agents.md"
        new = folder / "agent-roles.md"
        old.write_text("Legacy evidence\n")
        new.write_text("Current project role boundaries\n")
        self.build("--accept-migrations")
        self.assertEqual(old.read_text(), "Legacy evidence\n")
        self.assertEqual(new.read_text(), "Current project role boundaries\n")

    def test_linked_legacy_role_document_is_retained(self):
        external = self.project / "shared-role-rules.md"
        external.write_text("Shared role constraints\n")
        folder = self.project / ".harness"
        folder.mkdir()
        old = folder / "agents.md"
        old.symlink_to(external)
        self.build("--accept-migrations")
        self.assertTrue(old.is_symlink())
        self.assertEqual(external.read_text(), "Shared role constraints\n")
        self.assertFalse((folder / "agent-roles.md").exists())
        self.assertFalse((folder / "agent-roles.md").is_symlink())

    def test_dangling_legacy_role_link_is_not_shadowed(self):
        folder = self.project / ".harness"
        folder.mkdir()
        old = folder / "agents.md"
        target = self.project / "unavailable-role-rules.md"
        old.symlink_to(target)
        self.build("--accept-migrations")
        self.assertEqual(old.readlink(), target)
        self.assertFalse(target.exists())
        new = folder / "agent-roles.md"
        self.assertFalse(new.exists())
        self.assertFalse(new.is_symlink())

    def test_current_role_links_are_not_replaced_or_followed(self):
        folder = self.project / ".harness"
        folder.mkdir()
        new = folder / "agent-roles.md"
        target = self.project / "shared-role-rules.md"
        for target_exists in (False, True):
            with self.subTest(target_exists=target_exists):
                if target_exists:
                    target.write_text("External role constraints\n")
                new.symlink_to(target)
                self.build()
                self.assertEqual(new.readlink(), target)
                self.assertEqual(target.exists(), target_exists)
                if target_exists:
                    self.assertEqual(target.read_text(), "External role constraints\n")
                new.unlink()

    def test_devops_layout_is_current_and_project_content_is_preserved(self):
        self.build()
        folder = self.project / ".harness/docs/devops"
        self.assertTrue((folder / "release.md").is_file())
        local = folder / "local-dev.md"
        local.write_text("Actual project startup command\n")
        self.build()
        self.assertEqual(local.read_text(), "Actual project startup command\n")
        self.assertFalse((self.project / ".harness/docs/runtime").exists())

    def test_legacy_runtime_requires_approval_and_keeps_original_documents(self):
        folder = self.project / ".harness/docs/runtime"
        folder.mkdir(parents=True)
        for name in ("local-dev.md", "release.md"):
            (folder / name).write_text("Existing project instructions: " + name)
        result = subprocess.run(
            ["bash", str(SKILL / "scripts/build_harness.sh"), str(self.project)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertFalse(self.entry.exists())
        output = self.build("--accept-migrations")
        for name in ("local-dev.md", "release.md"):
            self.assertEqual((folder / name).read_text(), "Existing project instructions: " + name)
            self.assertFalse((self.project / ".harness/docs/devops" / name).exists())
            self.assertIn("[MERGE] Populate .harness/docs/devops/" + name, output)

    def test_legacy_devops_filenames_do_not_get_shadowed_by_empty_templates(self):
        folder = self.project / ".harness/docs/devops"
        folder.mkdir(parents=True)
        for name in ("env.md", "development.md", "deployment.md"):
            (folder / name).write_text("Existing " + name)
        self.build("--accept-migrations")
        for name in ("env.md", "development.md", "deployment.md"):
            self.assertEqual((folder / name).read_text(), "Existing " + name)
        self.assertFalse((folder / "local-dev.md").exists())
        self.assertFalse((folder / "release.md").exists())

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
