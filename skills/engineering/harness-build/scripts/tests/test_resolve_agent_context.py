import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
RESOLVER = SKILL_ROOT / "assets" / "baseline" / "scripts" / "resolve_agent_context.py"


class ResolveAgentContextTest(unittest.TestCase):
    def test_preserves_reference_order_and_exact_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "repo"
            root.mkdir()
            agent = root / ".codex" / "agents" / "fixture.toml"
            agent.parent.mkdir(parents=True)
            agent.write_text(
                'name = "fixture"\n'
                'developer_instructions = """\n'
                '@harness/second.md\n'
                '@harness/first.md\n'
                '"""\n',
                encoding="utf-8",
            )
            files = {
                "harness/second.md": "# Second\n\ncafé".encode(),
                "harness/first.md": b"# First\n",
            }
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)

            first = self._run(root, agent, root / "bundle.md", root / "receipt.json")
            second = self._run(
                root,
                agent,
                root / "bundle-again.md",
                root / "receipt-again.json",
            )

            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(0, second.returncode, second.stderr)
            expected = b"".join(
                self._section(relative, files[relative])
                for relative in ("harness/second.md", "harness/first.md")
            )
            bundle = (root / "bundle.md").read_bytes()
            self.assertEqual(expected, bundle)
            self.assertEqual(bundle, (root / "bundle-again.md").read_bytes())

            receipt = json.loads((root / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(1, receipt["schema_version"])
            self.assertEqual(
                {
                    "path": ".codex/agents/fixture.toml",
                    "sha256": hashlib.sha256(agent.read_bytes()).hexdigest(),
                },
                receipt["agent"],
            )
            self.assertEqual(
                [
                    {
                        "path": relative,
                        "sha256": hashlib.sha256(files[relative]).hexdigest(),
                        "byte_length": len(files[relative]),
                    }
                    for relative in ("harness/second.md", "harness/first.md")
                ],
                receipt["references"],
            )
            self.assertEqual(
                {
                    "sha256": hashlib.sha256(bundle).hexdigest(),
                    "byte_length": len(bundle),
                },
                receipt["bundle"],
            )
            self.assertEqual(
                (root / "receipt.json").read_bytes(),
                (root / "receipt-again.json").read_bytes(),
            )
            self.assertEqual(first.stdout, second.stdout)
            summary = json.loads(first.stdout)
            self.assertEqual(receipt["bundle"]["sha256"], summary["bundle_sha256"])
            self.assertEqual(
                hashlib.sha256((root / "receipt.json").read_bytes()).hexdigest(),
                summary["receipt_sha256"],
            )

    def test_rejects_missing_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root, agent = self._fixture(Path(tmp_dir), ["harness/missing.md"])

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "missing.md")

    def test_rejects_absolute_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            external = base / "outside.md"
            external.write_text("outside\n", encoding="utf-8")
            root, agent = self._fixture(base, [external.as_posix()])

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "absolute")

    def test_rejects_parent_traversal_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            external = base / "outside.md"
            external.write_text("outside\n", encoding="utf-8")
            root, agent = self._fixture(base, ["../outside.md"])

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "parent traversal")

    def test_rejects_duplicate_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            root, agent = self._fixture(
                base,
                ["harness/style.md", "harness/style.md"],
            )
            style = root / "harness" / "style.md"
            style.parent.mkdir()
            style.write_text("style\n", encoding="utf-8")

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "duplicate")

    def test_rejects_non_regular_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            root, agent = self._fixture(base, ["harness/directory"])
            (root / "harness" / "directory").mkdir(parents=True)

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "regular file")

    def test_rejects_symlink_escape_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            external = base / "outside.md"
            external.write_text("outside\n", encoding="utf-8")
            root, agent = self._fixture(base, ["harness/escape.md"])
            link = root / "harness" / "escape.md"
            link.parent.mkdir()
            link.symlink_to(external)

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "escapes repository")

    def test_rejects_non_utf8_reference(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            root, agent = self._fixture(base, ["harness/binary.md"])
            binary = root / "harness" / "binary.md"
            binary.parent.mkdir()
            binary.write_bytes(b"\xff\xfe")

            result = self._run(root, agent, root / "bundle.md", root / "receipt.json")

            self._assert_blocked(result, root, "UTF-8")

    def test_resolves_both_baseline_agents_with_the_same_context_order(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "repo"
            agent_root = SKILL_ROOT / "assets" / "baseline" / ".codex" / "agents"
            for name in ("pge-generator.toml", "pge-evaluator.toml"):
                target = root / ".codex" / "agents" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((agent_root / name).read_bytes())
            for relative in (
                "harness/coding-style.md",
                "harness/code-shape.md",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(
                    (SKILL_ROOT / "assets" / "baseline" / relative).read_bytes()
                )

            receipts = []
            bundles = []
            for role in ("generator", "evaluator"):
                result = self._run(
                    root,
                    root / ".codex" / "agents" / f"pge-{role}.toml",
                    root / f"{role}-bundle.md",
                    root / f"{role}-receipt.json",
                )
                self.assertEqual(0, result.returncode, result.stderr)
                receipts.append(
                    json.loads(
                        (root / f"{role}-receipt.json").read_text(encoding="utf-8")
                    )
                )
                bundles.append((root / f"{role}-bundle.md").read_bytes())

            self.assertEqual(bundles[0], bundles[1])
            self.assertEqual(
                ["harness/coding-style.md", "harness/code-shape.md"],
                [item["path"] for item in receipts[0]["references"]],
            )
            self.assertEqual(
                receipts[0]["references"],
                receipts[1]["references"],
            )
            self.assertNotEqual(receipts[0]["agent"], receipts[1]["agent"])

    def _run(
        self,
        root: Path,
        agent: Path,
        bundle: Path,
        receipt: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(RESOLVER),
                "--agent",
                str(agent),
                "--repo-root",
                str(root),
                "--out",
                str(bundle),
                "--receipt",
                str(receipt),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _fixture(
        self,
        base: Path,
        references: list[str],
    ) -> tuple[Path, Path]:
        root = base / "repo"
        root.mkdir()
        agent = root / ".codex" / "agents" / "fixture.toml"
        agent.parent.mkdir(parents=True)
        reference_lines = "".join(f"@{reference}\n" for reference in references)
        agent.write_text(
            'name = "fixture"\n'
            'developer_instructions = """\n'
            f"{reference_lines}"
            '"""\n',
            encoding="utf-8",
        )
        return root, agent

    def _assert_blocked(
        self,
        result: subprocess.CompletedProcess[str],
        root: Path,
        message: str,
    ) -> None:
        self.assertNotEqual(0, result.returncode)
        self.assertIn(message, result.stderr)
        self.assertFalse((root / "bundle.md").exists())
        self.assertFalse((root / "receipt.json").exists())

    def _section(self, relative: str, content: bytes) -> bytes:
        digest = hashlib.sha256(content).hexdigest()
        encoded_path = json.dumps(relative, ensure_ascii=False)
        return (
            f"<!-- harness-context-v1 begin path={encoded_path} "
            f"byte_length={len(content)} sha256={digest} -->\n"
        ).encode("utf-8") + content + (
            f"\n<!-- harness-context-v1 end path={encoded_path} -->\n"
        ).encode("utf-8")


if __name__ == "__main__":
    unittest.main()
