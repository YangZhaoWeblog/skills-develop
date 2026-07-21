import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_capabilities.py"
VALID_CHECKER = (
    SKILL_ROOT / "assets" / "baseline" / "scripts" / "check_pge_contracts.py"
).read_text(encoding="utf-8")
DIAGRAM_NODES = [
    "Planner",
    "Grill",
    "ContractDraft",
    "GeneratorProbe",
    "EvaluatorChallenge",
    "ContractLock",
    "Generator",
    "Implementation",
    "Evaluator",
    "FinalEvaluation",
    "HumanStart",
    "ParallelJoin",
    "Fallback",
    "CircuitBreaker",
]
DIAGRAM_EDGES = [
    "Planner --> Grill",
    "Grill --> ContractDraft",
    "ContractDraft --> GeneratorProbe",
    "ContractDraft --> EvaluatorChallenge",
    "GeneratorProbe --> ContractLock",
    "EvaluatorChallenge --> ContractLock",
    "ContractLock --> HumanStart",
    "HumanStart --> Generator",
    "Generator --> Implementation",
    "Generator --> ParallelJoin",
    "Implementation --> ParallelJoin",
    "ParallelJoin --> Evaluator",
    "Evaluator --> FinalEvaluation",
    "Evaluator -->|FAIL| Generator",
    "Evaluator -->|FAIL| Planner",
    "ThirdFailure --> CircuitBreaker",
    "AgentUnavailable --> Fallback",
]
FACT_GENERATED_PATHS = [
    "harness/api-standards.md",
    "harness/coding-style.md",
    "harness/database.md",
    "harness/dependency-map.md",
    "harness/deployment.md",
    "harness/development.md",
    "harness/testing.md",
]


class CapabilityValidatorTest(unittest.TestCase):
    def test_baseline_normative_diagram_shows_complete_pge_lifecycle(self):
        protocol = (
            SKILL_ROOT / "assets" / "baseline" / "harness" / "pge-protocol.md"
        ).read_text(encoding="utf-8")

        for node in DIAGRAM_NODES:
            self.assertIn(f"{node}[", protocol)
        for edge in DIAGRAM_EDGES:
            self.assertIn(edge, protocol)

    def test_baseline_documents_trusted_checker_at_coding_start(self):
        protocol = (
            SKILL_ROOT / "assets" / "baseline" / "harness" / "pge-protocol.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "Pre-Challenge structure checks do not require Human Start approval.",
            protocol,
        )
        self.assertIn(
            "python3 scripts/check_pge_contracts.py docs/pge/<sprint>-spec.md",
            protocol,
        )
        self.assertIn(
            "Run this trusted checker at Coding Start before production code",
            protocol,
        )

    def test_accepts_complete_staging_fixture(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)

            validation = self._run_validator(staging)

            self.assertEqual(0, validation.returncode, validation.stderr)
            self.assertEqual("[OK] source capabilities\n", validation.stdout)

    def test_validation_is_read_only_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            staging = root / "staging"
            target = root / "target"
            self._write_complete_harness(staging)
            target.mkdir()
            (target / "sentinel").write_bytes(b"target-data")
            staging_before = self._tree_digest(staging)
            target_before = self._tree_digest(target)

            first = self._run_validator(staging)
            second = self._run_validator(staging)

            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(
                (first.returncode, first.stdout, first.stderr),
                (second.returncode, second.stdout, second.stderr),
            )
            self.assertEqual(staging_before, self._tree_digest(staging))
            self.assertEqual(target_before, self._tree_digest(target))

    def test_rejects_target_that_self_validates_without_human_start(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            staging = root / "staging"
            target = root / "target"
            marker = root / "checker-ran"
            self._write_weak_harness(staging, marker)
            target.mkdir()
            sentinel = target / "sentinel"
            sentinel.write_bytes(b"unchanged")

            target_check = subprocess.run(
                [sys.executable, str(staging / "scripts" / "check_pge_contracts.py")],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, target_check.returncode)
            marker.unlink()

            validation = self._run_validator(staging)

            self.assertEqual(1, validation.returncode, validation.stderr)
            self.assertIn("pge.human_start.revision_bound", validation.stderr)
            self.assertNotIn("pge.diagram.control_flow", validation.stderr)
            self.assertNotIn("agent.model.inherit", validation.stderr)
            self.assertNotIn("grill.toolchain.complete", validation.stderr)
            self.assertFalse(marker.exists(), "validator executed the staging checker")
            self.assertEqual(b"unchanged", sentinel.read_bytes())

    def test_rejects_invalid_pge_control_flow_diagram(self):
        mutations = [
            (
                f"missing node {node}",
                lambda content, node=node: content.replace(node, "OmittedNode"),
            )
            for node in DIAGRAM_NODES
        ]
        mutations.extend(
            (
                f"missing edge {edge}",
                lambda content, edge=edge: content.replace(f"    {edge}\n", ""),
            )
            for edge in DIAGRAM_EDGES
        )
        mutations.append(
            (
                "diagram moved",
                lambda content: content.replace(self._control_flow_diagram(), ""),
            )
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp_dir:
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                protocol = staging / "harness" / "pge-protocol.md"
                original = protocol.read_text(encoding="utf-8")
                protocol.write_text(mutate(original), encoding="utf-8")
                if name == "diagram moved":
                    moved = staging / "docs" / "control-flow.md"
                    moved.parent.mkdir(exist_ok=True)
                    moved.write_text(self._control_flow_diagram(), encoding="utf-8")

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("pge.diagram.control_flow", validation.stderr)

    def test_accepts_project_mermaid_outside_builder_owned_pge_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            (staging / "ARCHITECTURE.md").write_text(
                "```mermaid\nflowchart LR\n    service --> database\n```\n",
                encoding="utf-8",
            )
            dependency_map = staging / "harness" / "dependency-map.md"
            dependency_map.write_text(
                dependency_map.read_text(encoding="utf-8")
                + "\n```mermaid\nflowchart LR\n    logic --> dao\n```\n",
                encoding="utf-8",
            )

            validation = self._run_validator(staging)

            self.assertEqual(0, validation.returncode, validation.stderr)

    def test_rejects_normative_diagram_copied_to_builder_owned_pge_doc(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            workflow = (
                staging
                / ".agents"
                / "skills"
                / "pge-workflow"
                / "SKILL.md"
            )
            workflow.parent.mkdir(parents=True, exist_ok=True)
            workflow.write_text(
                f"# PGE Workflow\n\n{self._control_flow_diagram()}\n",
                encoding="utf-8",
            )

            validation = self._run_validator(staging)

            self.assertEqual(1, validation.returncode, validation.stderr)
            self.assertIn("pge.diagram.control_flow", validation.stderr)

    def test_rejects_explicit_model_in_pge_agent(self):
        agent_paths = [
            ".codex/agents/pge-generator.toml",
            ".codex/agents/pge-evaluator.toml",
        ]
        for agent_path in agent_paths:
            with (
                self.subTest(agent_path=agent_path),
                tempfile.TemporaryDirectory() as tmp_dir,
            ):
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                path = staging / agent_path
                path.write_text(
                    f'model = "fixed-model"\n{path.read_text(encoding="utf-8")}',
                    encoding="utf-8",
                )

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("agent.model.inherit", validation.stderr)

    def test_rejects_checker_with_mutated_human_start_relation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            checker = staging / "scripts" / "check_pge_contracts.py"

            target_check = subprocess.run(
                [
                    sys.executable,
                    str(checker),
                    str(staging / "docs" / "pge" / "spec.template.md"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, target_check.returncode, target_check.stderr)
            checker.write_text(
                checker.read_text(encoding="utf-8").replace(
                    'gate.get("approved_contract_revision") '
                    '== contract["contract_revision"]',
                    'gate.get("approved_contract_revision") '
                    '!= contract["contract_revision"]',
                ),
                encoding="utf-8",
            )

            validation = self._run_validator(staging)

            self.assertEqual(1, validation.returncode, validation.stderr)
            self.assertIn("pge.human_start.revision_bound", validation.stderr)

    def test_allowlisted_checker_reads_human_start_after_unrelated_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec = Path(tmp_dir) / "spec.md"
            content = (
                SKILL_ROOT
                / "assets"
                / "baseline"
                / "docs"
                / "pge"
                / "spec.template.md"
            ).read_text(encoding="utf-8")
            content = content.replace('"status": "pending"', '"status": "approved"')
            content = content.replace(
                '"approved_contract_revision": null',
                '"approved_contract_revision": 1',
            )
            content = content.replace('"channel": ""', '"channel": "direct_reply"')
            content = content.replace('"evidence": ""', '"evidence": "approved"')
            spec.write_text(content, encoding="utf-8")

            target_check = self._run_baseline_checker(spec)

            self.assertEqual(0, target_check.returncode, target_check.stderr)
            self.assertNotIn("Traceback", target_check.stderr)

    def test_allowlisted_checker_rejects_ambiguous_or_malformed_gate(self):
        valid_contract = {
            "contract_revision": 1,
            "human_start_gate": {
                "status": "approved",
                "approved_contract_revision": 1,
                "channel": "direct_reply",
                "evidence": "approved",
            },
        }
        unrelated = '```json\n{"pge_fallback": {}}\n```\n'
        valid_fence = f"```json\n{json.dumps(valid_contract)}\n```\n"
        cases = {
            "duplicate": unrelated + valid_fence + valid_fence,
            "invalid json": unrelated + '```json\n{"contract_revision":\n```\n',
            "non-object gate": unrelated
            + "```json\n"
            + json.dumps({"contract_revision": 1, "human_start_gate": []})
            + "\n```\n",
            "missing field": unrelated
            + "```json\n"
            + json.dumps(
                {
                    "contract_revision": 1,
                    "human_start_gate": {
                        "status": "approved",
                        "approved_contract_revision": 1,
                        "channel": "direct_reply",
                    },
                }
            )
            + "\n```\n",
        }
        for name, content in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp_dir:
                spec = Path(tmp_dir) / "spec.md"
                spec.write_text(content, encoding="utf-8")

                target_check = self._run_baseline_checker(spec)

                self.assertEqual(1, target_check.returncode, target_check.stderr)
                self.assertNotIn("Traceback", target_check.stderr)

    def test_allowlisted_checker_enforces_human_start_gate(self):
        mutations = {
            "stale revision": (
                '"approved_contract_revision": 1',
                '"approved_contract_revision": 2',
            ),
            "empty channel": ('"channel": "direct_reply"', '"channel": ""'),
            "empty evidence": ('"evidence": "approved"', '"evidence": ""'),
            "pending status": ('"status": "approved"', '"status": "pending"'),
        }
        for name, (old, new) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp_dir:
                staging = Path(tmp_dir) / "staging"
                self._write_human_start_harness(staging)
                spec = staging / "docs" / "pge" / "spec.template.md"
                spec.write_text(
                    spec.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8",
                )

                target_check = subprocess.run(
                    [
                        sys.executable,
                        str(staging / "scripts" / "check_pge_contracts.py"),
                        str(spec),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(1, target_check.returncode, target_check.stderr)

    def test_rejects_missing_human_start_template_field(self):
        fields = [
            "contract_revision",
            "status",
            "approved_contract_revision",
            "channel",
            "evidence",
        ]
        for field in fields:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp_dir:
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                self._delete_contract_field(staging, field)

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("pge.human_start.revision_bound", validation.stderr)

    def test_rejects_missing_human_start_protocol_relation(self):
        relations = [
            "approved_contract_revision == contract_revision",
            'channel != ""',
            'evidence != ""',
        ]
        for relation in relations:
            with (
                self.subTest(relation=relation),
                tempfile.TemporaryDirectory() as tmp_dir,
            ):
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                protocol = staging / "harness" / "pge-protocol.md"
                protocol.write_text(
                    protocol.read_text(encoding="utf-8").replace(
                        f"{relation}\n", ""
                    ),
                    encoding="utf-8",
                )

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("pge.human_start.revision_bound", validation.stderr)

    def test_rejects_incomplete_or_expanded_grill_toolchain(self):
        mutations = {
            "missing grilling": lambda staging: (
                staging / ".agents" / "skills" / "grilling" / "SKILL.md"
            ).unlink(),
            "missing domain modeling": lambda staging: (
                staging / ".agents" / "skills" / "domain-modeling" / "SKILL.md"
            ).unlink(),
            "missing grill me": lambda staging: (
                staging / ".agents" / "skills" / "grill-me" / "SKILL.md"
            ).unlink(),
            "missing grill with docs": lambda staging: (
                staging / ".agents" / "skills" / "grill-with-docs" / "SKILL.md"
            ).unlink(),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp_dir:
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                mutate(staging)

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("grill.toolchain.complete", validation.stderr)

    def test_accepts_current_upstream_wrapper_bodies(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            self._replace_skill_body(
                staging,
                "grill-me",
                "Run a `/grilling` session.",
            )
            self._replace_skill_body(
                staging,
                "grill-with-docs",
                "Run a `/grilling` session, using the `/domain-modeling` skill.",
            )

            validation = self._run_validator(staging)

            self.assertEqual(0, validation.returncode, validation.stderr)

    def test_accepts_floating_upstream_wrapper_bodies(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            self._replace_skill_body(
                staging,
                "grill-me",
                "Upstream changed this wrapper without changing its Skill name.",
            )
            self._replace_skill_body(
                staging,
                "grill-with-docs",
                "Upstream now documents a different one-hop invocation.",
            )

            validation = self._run_validator(staging)

            self.assertEqual(0, validation.returncode, validation.stderr)

    def test_rejects_missing_skill_referenced_by_generated_harness(self):
        skill_names = [
            "pge-workflow",
            "grilling",
            "domain-modeling",
            "grill-me",
            "grill-with-docs",
        ]
        for skill_name in skill_names:
            with self.subTest(skill_name=skill_name), tempfile.TemporaryDirectory() as tmp_dir:
                staging = Path(tmp_dir) / "staging"
                self._write_complete_harness(staging)
                shutil.rmtree(staging / ".agents" / "skills" / skill_name)

                validation = self._run_validator(staging)

                self.assertEqual(1, validation.returncode, validation.stderr)
                self.assertIn("harness.skill_references.resolve", validation.stderr)

    def test_rejects_project_rule_that_was_not_fact_generated(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            staging = Path(tmp_dir) / "staging"
            self._write_complete_harness(staging)
            stale = staging / "harness" / "testing.md"
            stale.write_text("# Stale project testing rules\n", encoding="utf-8")

            validation = self._run_validator(staging)

            self.assertEqual(1, validation.returncode, validation.stderr)
            self.assertIn("project.rules.fact_generated", validation.stderr)
            self.assertIn("harness/testing.md was not regenerated", validation.stderr)

    def _run_validator(self, staging: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--staging",
                str(staging),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_baseline_checker(
        self,
        spec: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(
                    SKILL_ROOT
                    / "assets"
                    / "baseline"
                    / "scripts"
                    / "check_pge_contracts.py"
                ),
                str(spec),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _tree_digest(self, root: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def _write_complete_harness(self, staging: Path) -> None:
        self._write_human_start_harness(staging)
        self._write_agent_files(staging)
        self._write_grill_skills(staging)
        workflow = (
            staging / ".agents" / "skills" / "pge-workflow" / "SKILL.md"
        )
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "---\nname: pge-workflow\ndescription: fixture\n---\n\n"
            "Use $grill-me or $grill-with-docs, then $grilling and "
            "$domain-modeling when selected.\n",
            encoding="utf-8",
        )
        (staging / "AGENTS.md").write_text(
            "Use $pge-workflow for medium work.\n",
            encoding="utf-8",
        )
        for relative_path in FACT_GENERATED_PATHS:
            path = staging / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Generated project rule\n\n## Detected Repository Facts\n\n"
                "- Fixture fact.\n",
                encoding="utf-8",
            )

    def _delete_contract_field(self, staging: Path, field: str) -> None:
        spec = staging / "docs" / "pge" / "spec.template.md"
        content = spec.read_text(encoding="utf-8")
        prefix, remainder = content.split("```json\n", 1)
        json_text, suffix = remainder.split("\n```", 1)
        contract = json.loads(json_text)
        if field == "contract_revision":
            del contract[field]
        else:
            del contract["human_start_gate"][field]
        spec.write_text(
            f"{prefix}```json\n{json.dumps(contract, indent=2)}\n```{suffix}",
            encoding="utf-8",
        )

    def _write_weak_harness(self, staging: Path, marker: Path) -> None:
        self._write_complete_harness(staging)
        (staging / "harness" / "pge-protocol.md").write_text(
            "# PGE Protocol\n\n## Human Start\n\nA locked contract may start.\n\n"
            f"{self._control_flow_diagram()}",
            encoding="utf-8",
        )
        (staging / "scripts" / "check_pge_contracts.py").write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    f"Path({str(marker)!r}).write_text('ran', encoding='utf-8')",
                    "raise SystemExit(0)",
                ]
            ),
            encoding="utf-8",
        )

    def _write_human_start_harness(self, staging: Path) -> None:
        (staging / "docs" / "pge").mkdir(parents=True)
        (staging / "harness").mkdir()
        (staging / "scripts").mkdir()
        (staging / "docs" / "pge" / "spec.template.md").write_text(
            """
```json
{
  "contract_revision": 1,
  "human_start_gate": {
    "status": "approved",
    "approved_contract_revision": 1,
    "channel": "direct_reply",
    "evidence": "approved"
  }
}
```
""".strip(),
            encoding="utf-8",
        )
        human_start_checks = "\n".join(
            [
                "approved_contract_revision == contract_revision",
                'channel != ""',
                'evidence != ""',
                "Pre-Challenge structure checks do not require Human Start approval.",
                "python3 scripts/check_pge_contracts.py docs/pge/<sprint>-spec.md",
            ]
        )
        (staging / "harness" / "pge-protocol.md").write_text(
            f"# PGE Protocol\n\n{human_start_checks}\n\n"
            f"{self._control_flow_diagram()}",
            encoding="utf-8",
        )
        (staging / "scripts" / "check_pge_contracts.py").write_text(
            VALID_CHECKER,
            encoding="utf-8",
        )

    def _control_flow_diagram(self) -> str:
        return """```mermaid
flowchart LR
    Planner[Planner]
    Grill[Grill]
    ContractDraft[Contract draft]
    GeneratorProbe[Generator read-only probe]
    EvaluatorChallenge[Evaluator read-only challenge]
    ContractLock[Contract lock]
    HumanStart[Human Start]
    Generator[Generator]
    Implementation[Implementation]
    ParallelJoin[Parallel join]
    Evaluator[Evaluator]
    FinalEvaluation[Final evaluation]
    Fallback[Fallback]
    CircuitBreaker[Circuit breaker]
    ThirdFailure[third failure]
    AgentUnavailable[agent unavailable]
    Planner --> Grill
    Grill --> ContractDraft
    ContractDraft --> GeneratorProbe
    ContractDraft --> EvaluatorChallenge
    GeneratorProbe --> ContractLock
    EvaluatorChallenge --> ContractLock
    ContractLock --> HumanStart
    HumanStart --> Generator
    Generator --> Implementation
    Generator --> ParallelJoin
    Implementation --> ParallelJoin
    ParallelJoin --> Evaluator
    Evaluator --> FinalEvaluation
    Evaluator -->|FAIL| Generator
    Evaluator -->|FAIL| Planner
    ThirdFailure --> CircuitBreaker
    AgentUnavailable --> Fallback
```"""

    def _write_agent_files(self, staging: Path) -> None:
        agent_dir = staging / ".codex" / "agents"
        agent_dir.mkdir(parents=True)
        for agent_name in ("pge-generator.toml", "pge-evaluator.toml"):
            (agent_dir / agent_name).write_text(
                f'name = "{agent_name.removesuffix(".toml")}"\n',
                encoding="utf-8",
            )

    def _write_grill_skills(self, staging: Path) -> None:
        bodies = {
            "grilling": "Upstream grilling instructions.",
            "domain-modeling": "Upstream domain-modeling instructions.",
            "grill-me": "Run a `/grilling` session.",
            "grill-with-docs": (
                "Run a `/grilling` session, using the `/domain-modeling` skill."
            ),
        }
        for name, body in bodies.items():
            skill_dir = staging / ".agents" / "skills" / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: fixture\n---\n\n{body}\n",
                encoding="utf-8",
            )

    def _replace_skill_body(self, staging: Path, name: str, body: str) -> None:
        skill = staging / ".agents" / "skills" / name / "SKILL.md"
        frontmatter = skill.read_text(encoding="utf-8").split("---", 2)[1]
        skill.write_text(
            f"---{frontmatter}---\n\n{body}\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
