import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from project_rules import rebuild_project_rules  # noqa: E402


class ProjectRulesTest(unittest.TestCase):
    def test_detects_chainmaker_contract_facts_without_ci_misclassification(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "target"
            target.mkdir()
            (target / "go.mod").write_text(
                "module example.org/contract\n\n"
                "go 1.24.12\n\n"
                "require (\n"
                "\tchainmaker.org/chainmaker/contract-sdk-go/v2 v2.3.9\n"
                "\tgoogle.golang.org/grpc v1.65.0 // indirect\n"
                ")\n",
                encoding="utf-8",
            )
            (target / "Makefile").write_text(
                "ut:\n\tgo test -coverprofile=cover.out ./...\n\n"
                "lint:\n\tgolangci-lint run ./...\n\n"
                "build:\n\tgo build ./...\n\n"
                "gen-code:\n\tgo generate ./code\n",
                encoding="utf-8",
            )
            (target / "Jenkinsfile").write_text(
                "environment { COVERAGE_MIN = '60' }\n",
                encoding="utf-8",
            )
            method = target / "const" / "method.go"
            method.parent.mkdir()
            method.write_text('const MethodPublish = "Publish"\n', encoding="utf-8")
            register = target / "internal" / "contract" / "register.go"
            register.parent.mkdir(parents=True)
            register.write_text(
                "func register(c Contract) { c.RegisterMethod(MethodPublish, handler) }\n",
                encoding="utf-8",
            )

            generated = self._render(target)

            api = generated["harness/api-standards.md"]
            self.assertIn("> status: active", api)
            self.assertIn("`const/method.go`", api)
            self.assertIn("`internal/contract/register.go`", api)
            coding = generated["harness/coding-style.md"]
            self.assertIn("Framework: ChainMaker smart contract", coding)
            self.assertNotIn("Framework: gRPC", coding)
            deployment = generated["harness/deployment.md"]
            self.assertIn("> status: stub", deployment)
            self.assertIn("CI artifact: `Jenkinsfile`", deployment)
            self.assertIn("No deployment/runtime artifact detected", deployment)
            self.assertIn("make gen-code", generated["harness/development.md"])
            testing = generated["harness/testing.md"]
            self.assertIn("CI coverage threshold: 60%", testing)
            self.assertIn("Local `make ut` does not enforce", testing)

    def test_keeps_direct_grpc_deployment_and_local_coverage_counterexamples(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "target"
            target.mkdir()
            (target / "go.mod").write_text(
                "module example.org/service\n\n"
                "go 1.24.12\n\n"
                "require google.golang.org/grpc v1.65.0\n",
                encoding="utf-8",
            )
            (target / "Makefile").write_text(
                "ut:\n\tgo test -coverprofile=cover.out ./...\n"
                "\ttest \"$$coverage\" -ge 60\n",
                encoding="utf-8",
            )
            (target / "Jenkinsfile").write_text(
                "environment { COVERAGE_MIN = '60' }\n",
                encoding="utf-8",
            )
            (target / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")

            generated = self._render(target)

            self.assertIn(
                "Framework: gRPC",
                generated["harness/coding-style.md"],
            )
            deployment = generated["harness/deployment.md"]
            self.assertIn("> status: active", deployment)
            self.assertIn("Deployment/runtime artifact: `Dockerfile`", deployment)
            testing = generated["harness/testing.md"]
            self.assertIn("CI coverage threshold: 60%", testing)
            self.assertNotIn("does not enforce", testing)

    def test_does_not_activate_chainmaker_api_without_registration(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "target"
            target.mkdir()
            (target / "go.mod").write_text(
                "module example.org/contract\n\n"
                "go 1.24.12\n\n"
                "require chainmaker.org/chainmaker/contract-sdk-go/v2 v2.3.9\n",
                encoding="utf-8",
            )

            generated = self._render(target)

            api = generated["harness/api-standards.md"]
            self.assertIn("> status: stub", api)
            self.assertIn("No public API source detected", api)

    def _render(self, target: Path) -> dict[str, str]:
        staging = target.parent / "staging"
        rebuild_project_rules(target, staging, SKILL_ROOT / "assets" / "baseline")
        return {
            relative: (staging / relative).read_text(encoding="utf-8")
            for relative in (
                "harness/api-standards.md",
                "harness/coding-style.md",
                "harness/deployment.md",
                "harness/development.md",
                "harness/testing.md",
            )
        }


if __name__ == "__main__":
    unittest.main()
