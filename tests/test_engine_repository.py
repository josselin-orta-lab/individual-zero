"""Registry invariants independent of the cognitive actor's behavior."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineToolingTests(unittest.TestCase):

    def test_i0_archive_manifest_is_closed_over_tracked_paths(self):
        from scripts.check_engine_repository import archive_inventory_errors

        entries = [
            {"archived": "archive/i0/tests/test_old.py"},
            {"archived": "archive/i0/workflows/old.yml"},
        ]
        tracked = [entry["archived"] for entry in entries]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "archive/i0/tests").mkdir(parents=True)
            (root / "archive/i0/workflows").mkdir()
            self.assertEqual(archive_inventory_errors(root, entries, tracked), [])
            extra = archive_inventory_errors(
                root, entries, tracked + ["archive/i0/tests/stray.py"])
            self.assertIn("unmanifested tracked I0 archive file: archive/i0/tests/stray.py", extra)
            missing = archive_inventory_errors(root, entries, tracked[:1])
            self.assertIn("manifested I0 archive file not tracked: archive/i0/workflows/old.yml", missing)
            link = root / "archive/i0/tests/test_old.py"
            link.symlink_to("elsewhere.py")
            linked = archive_inventory_errors(root, entries, tracked)
            self.assertIn("frozen I0 archive file is symlink: archive/i0/tests/test_old.py", linked)
            unsafe = archive_inventory_errors(
                root, entries + [{"archived": "archive/i0/tests/../../escape.py"}], tracked)
            self.assertTrue(any("unsafe I0 archive manifest destination" in x for x in unsafe))

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

    def test_static_engine_policy_routes_to_light_ci_not_living_i1(self):
        heavy = (ROOT / ".github/workflows/i1-current-ci.yml").read_text()
        light = (ROOT / ".github/workflows/i2-proposal-safety.yml").read_text()
        heavy_paths = heavy.split("  workflow_dispatch:", 1)[0]
        light_paths = light.split("\npermissions:", 1)[0]
        for owned in ("tools/assess_engine_proposal.py",
                      "tests/test_engine_repository.py"):
            # No positive path in I1's expensive PR trigger.
            self.assertNotIn("      - '" + owned + "'", heavy_paths)
            # Same static source changes must activate I2 proposal tests.
            self.assertIn("      - '" + owned + "'", light_paths)
        self.assertIn("      - 'scripts/**'", heavy_paths)
        self.assertIn("      - '!scripts/check_engine_repository.py'", heavy_paths)
        self.assertGreater(
            heavy_paths.index("      - '!scripts/check_engine_repository.py'"),
            heavy_paths.index("      - 'scripts/**'"),
        )
        self.assertIn("      - 'scripts/check_engine_repository.py'", light_paths)
        self.assertIn("python scripts/check_engine_repository.py --json", light)
        self.assertIn(
            "python -m unittest discover -s tests -p test_engine_repository.py -v",
            light,
        )
        # Changes to real I1 source/engine contracts must still run full I1.
        for required in (
            "      - 'src/i1/**'",
            "      - 'tests/i1/**'",
            "      - 'tools/run_engine_checks.py'",
            "      - 'config/engine-registry.json'",
            "      - '.github/workflows/i1-current-ci.yml'",
            "      - '.github/workflows/engine-structural.yml'",
        ):
            self.assertIn(required, heavy_paths)
        for negative in (
            "!src/i1/**/*.md", "!src/i1/docs/**", "!src/i1/AGENTS.md"
        ):
            self.assertGreater(
                heavy_paths.index(negative),
                heavy_paths.index("      - '.github/workflows/engine-structural.yml'"),
            )


    def test_original_engine_sources_are_present(self):
        self.assertFalse((ROOT / "src/lab").exists())
        self.assertTrue((ROOT / "archive/i0/lab/__init__.py").is_file())
        for name in ("i0", "i1", "i1/lab", "i1/runtime"):
            self.assertTrue((ROOT / "src" / name).is_dir(), name)


if __name__ == "__main__":
    unittest.main()
