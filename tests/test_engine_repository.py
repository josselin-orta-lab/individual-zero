"""Registry invariants independent of the cognitive actor's behavior."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineToolingTests(unittest.TestCase):
    def test_registry_and_original_archive_are_consistent(self):
        proc = subprocess.run([sys.executable, "scripts/check_engine_repository.py", "--json"],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["active_generation"], "I1")
        self.assertEqual(report["archived"], {"workflows": 127, "tests": 297})

    def test_proposal_ci_not_misclassified_as_archived_i0(self):
        from scripts.check_engine_repository import unexpected_workflows

        active = "i1-current-ci.yml"
        workflows = [Path(".github/workflows/" + name) for name in
                     ("i1-current-ci.yml", "i2-proposal-safety.yml",
                      "engine-structural.yml", "agent-context-static.yml",
                      "stage9-historical.yml")]
        self.assertEqual(unexpected_workflows(workflows, active_ci=active),
                         ["stage9-historical.yml"])

    def test_static_agent_navigation_is_not_historical_runtime_ci(self):
        from scripts.check_engine_repository import unexpected_workflows
        paths = [Path(".github/workflows/agent-context-static.yml"),
                 Path(".github/workflows/i2-proposal-safety.yml"),
                 Path(".github/workflows/stage9-historical.yml")]
        self.assertEqual(unexpected_workflows(paths, active_ci="i1-current-ci.yml"),
                         ["stage9-historical.yml"])

    def test_documentation_does_not_trigger_heavy_i1_ci(self):
        workflow = (ROOT / ".github/workflows/i1-current-ci.yml").read_text()
        triggers = workflow.split("  workflow_dispatch:", 1)[0]
        for required in (
            "      - 'src/i1/**'",
            "      - 'tests/test_engine_repository.py'",
            "      - '!src/i1/**/*.md'",
            "      - '!src/i1/docs/**'",
            "      - '!src/i1/AGENTS.md'",
        ):
            self.assertIn(required, triggers)
        self.assertNotIn("      - 'AGENTS.md'", triggers)
        self.assertNotIn("      - 'docs/engineering/SCRIPT_INVENTORY.md'", triggers)
        self.assertNotIn("      - 'docs/engines/i1/**'", triggers)
        positive_end = triggers.index("      - '.github/workflows/engine-structural.yml'")
        for negative in ("!src/i1/**/*.md", "!src/i1/docs/**", "!src/i1/AGENTS.md"):
            self.assertGreater(triggers.index(negative), positive_end)

    def test_original_engine_sources_are_present(self):
        self.assertFalse((ROOT / "src/lab").exists())
        self.assertTrue((ROOT / "archive/i0/lab/__init__.py").is_file())
        for name in ("i0", "i1", "i1/lab", "i1/runtime"):
            self.assertTrue((ROOT / "src" / name).is_dir(), name)


if __name__ == "__main__":
    unittest.main()
