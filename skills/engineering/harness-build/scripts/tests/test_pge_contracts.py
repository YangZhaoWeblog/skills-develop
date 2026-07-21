import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
CHECKER = SKILL_ROOT / "assets" / "baseline" / "scripts" / "check_pge_contracts.sh"
SPEC_TEMPLATE = SKILL_ROOT / "assets" / "baseline" / "docs" / "pge" / "spec.template.md"


class PGEContractCheckerTests(unittest.TestCase):
    def _check_spec(self, content: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            spec = root / "docs" / "pge" / "governance-spec.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(content, encoding="utf-8")
            return subprocess.run(
                ["bash", str(CHECKER), "docs/pge/governance-spec.md"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_accepts_targeted_regression_plan_for_non_behavior_contract(self):
        content = SPEC_TEMPLATE.read_text(encoding="utf-8").replace(
            "## RED / Tracer Bullet Or Targeted Verification Plan",
            "## Targeted Regression Plan",
        )

        result = self._check_spec(content)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[OK] pge_contracts", result.stdout)

    def test_rejects_contract_without_any_verification_plan(self):
        content = SPEC_TEMPLATE.read_text(encoding="utf-8").replace(
            "## RED / Tracer Bullet Or Targeted Verification Plan",
            "## Notes",
        )

        result = self._check_spec(content)

        self.assertEqual(1, result.returncode)
        self.assertIn("RED/tracer or targeted verification plan", result.stderr)

    def test_staged_mode_accepts_complete_contract(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            spec = root / "docs" / "pge" / "governance-spec.md"
            spec.parent.mkdir(parents=True)
            content = SPEC_TEMPLATE.read_text(encoding="utf-8") + ("\npadding" * 20_000)
            spec.write_text(content, encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", str(spec.relative_to(root))], cwd=root, check=True)

            result = subprocess.run(
                [
                    "bash",
                    str(CHECKER),
                    "--staged",
                    "docs/pge/governance-spec.md",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[OK] pge_contracts", result.stdout)


if __name__ == "__main__":
    unittest.main()
