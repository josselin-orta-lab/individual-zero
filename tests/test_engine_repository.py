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
        self.assertEqual(report["reference_generation"], "I3")
        self.assertEqual(report["archived"], {"workflows": 127, "tests": 297})

    def test_owner_selected_i3_reference_is_not_automatic_active_release(self):
        from scripts.check_engine_repository import reference_selection_errors
        from tools.run_engine_checks import plan

        registry = json.loads((ROOT / "config/engine-registry.json").read_text())
        contract = json.loads((ROOT / "src/i3/engine.json").read_text())
        surface = json.loads((ROOT / "src/i3/ACTIVE_SURFACE.json").read_text())
        self.assertEqual(registry["reference_generation"], "I3")
        self.assertEqual(registry["active_generation"], "I1")
        self.assertNotIn("I3", registry["generations"])
        self.assertEqual(reference_selection_errors(registry, contract, surface), [])
        self.assertFalse(surface["governance"]["fresh_lived_worlds_allowed"])
        with self.assertRaisesRegex(ValueError, "only the registered active engine"):
            plan("I3", "smoke")

        def snapshot():
            return (json.loads(json.dumps(registry)),
                    json.loads(json.dumps(contract)),
                    json.loads(json.dumps(surface)))

        for problem in (
            "wrong_reference", "active_i3", "registered_i3",
            "contract_active", "contract_entrypoint", "scientific_world",
            "wrong_stage",
        ):
            r, c, s = snapshot()
            if problem == "wrong_reference":
                r["reference_generation"] = "I1"
            elif problem == "active_i3":
                r["active_generation"] = "I3"
            elif problem == "registered_i3":
                r["generations"]["I3"] = {"source": "src/i3"}
            elif problem == "contract_active":
                c["status"] = "active"
            elif problem == "contract_entrypoint":
                c["entrypoints"] = {"runtime": "unreleased.runtime"}
            elif problem == "scientific_world":
                s["governance"]["next_scientific_cohort_authorized"] = True
            else:
                s["current_stage"] = "2.2 controller"
            with self.subTest(problem=problem):
                self.assertTrue(reference_selection_errors(r, c, s))

    def test_proposal_ci_not_misclassified_as_archived_i0(self):
        from scripts.check_engine_repository import unexpected_workflows

        active = "i1-current-ci.yml"
        workflows = [Path(".github/workflows/" + name) for name in
                     ("i1-current-ci.yml", "i2-proposal-safety.yml", "i3-proposal-checks.yml",
                      "engine-structural.yml", "agent-context-static.yml",
                      "stage9-historical.yml")]
        self.assertEqual(unexpected_workflows(workflows, active_ci=active),
                         ["stage9-historical.yml"])

    def test_i3_proposal_allowance_does_not_admit_arbitrary_studies(self):
        from scripts.check_engine_repository import unexpected_workflows

        rejected = ["i3-activation.yml", "i3-proposal-checks-extra.yml",
                    "i3-scientific-study.yml", "stage9-historical.yml"]
        paths = [Path(".github/workflows/" + name)
                 for name in ["i3-proposal-checks.yml", *rejected]]
        self.assertEqual(unexpected_workflows(paths, active_ci="i1-current-ci.yml"),
                         sorted(rejected))

    def test_one_shot_stage6_allowance_is_exact_not_a_prefix(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage6-one-shot-20261115.yml"
        blocked = ("i3-stage6-one-shot-20261115-retry.yml",
                   "i3-stage6-one-shot-20261116.yml",
                   "i3-scientific-study.yml")
        paths = [Path(".github/workflows/" + name)
                 for name in (allowed, *blocked)]
        self.assertEqual(unexpected_workflows(paths,
                         active_ci="i1-current-ci.yml"), sorted(blocked))

    def test_stage7_inherited_persistence_allowance_is_exact_once(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage7-persistence-one-shot-20261116.yml"
        blocked = ("i3-stage7-persistence-one-shot-20261116-retry.yml",
                   "i3-stage7-persistence-one-shot-20261117.yml",
                   "i3-stage7-persistence-extra-worlds.yml")
        paths = [Path(".github/workflows/" + name)
                 for name in (allowed, *blocked)]
        self.assertEqual(unexpected_workflows(
            paths, active_ci="i1-current-ci.yml"), sorted(blocked))

    def test_static_agent_navigation_is_not_historical_runtime_ci(self):
        from scripts.check_engine_repository import unexpected_workflows
        paths = [Path(".github/workflows/agent-context-static.yml"),
                 Path(".github/workflows/i2-proposal-safety.yml"),
                 Path(".github/workflows/stage9-historical.yml")]
        self.assertEqual(unexpected_workflows(paths, active_ci="i1-current-ci.yml"),
                         ["stage9-historical.yml"])

    def test_archived_i2_is_static_on_pr_and_full_matrix_is_manual(self):
        # I2's original 3.11/3.12 tests remain reproducible but never run
        # automatically when someone edits a frozen tree or shared policy.
        living = (ROOT / ".github/workflows/i1-current-ci.yml").read_text()
        archived = (ROOT / ".github/workflows/i2-proposal-safety.yml").read_text()
        light = (ROOT / ".github/workflows/agent-context-static.yml").read_text()
        living_paths = living.split("  workflow_dispatch:", 1)[0]
        archived_dispatch = archived.split("\npermissions:", 1)[0]
        light_paths = light.split("\npermissions:", 1)[0]

        self.assertIn("  workflow_dispatch:", archived_dispatch)
        self.assertNotIn("  pull_request:", archived_dispatch)
        self.assertIn("ref: ${{ github.sha }}", archived)
        self.assertIn("python tools/i2_ci_shards.py", archived)
        self.assertIn("python-version: ['3.11', '3.12']", archived)
        self.assertIn("python scripts/check_engine_repository.py --json", archived)
        i3 = (ROOT / ".github/workflows/i3-proposal-checks.yml").read_text()
        i3_paths = i3.split("  push:", 1)[0]
        for shared in ("scripts/check_engine_repository.py",
                       "tests/test_engine_repository.py"):
            self.assertNotIn("      - '" + shared + "'", i3_paths)
        for i3_owned in ("src/i3/**/*.py", "src/i3/engine.json",
                         "src/i3/ACTIVE_SURFACE.json", "tests/i3/**",
                         ".github/workflows/i3-proposal-checks.yml"):
            self.assertIn("      - '" + i3_owned + "'", i3_paths)
        self.assertIn("python-version: ['3.11', '3.12']", i3)

        for owned in ("src/i2/**", "tests/i2/**",
                      "config/archives/i2-20261116.json",
                      "tools/check_i2_archive.py",
                      "tools/i2_ci_shards.py",
                      "tools/assess_engine_proposal.py",
                      "scripts/check_engine_repository.py",
                      "tests/test_engine_repository.py",
                      ".github/workflows/i2-proposal-safety.yml"):
            self.assertIn("      - '" + owned + "'", light_paths)
        self.assertIn("python tools/check_i2_archive.py --json", light)
        self.assertIn("python scripts/check_engine_repository.py --json", light)
        self.assertIn(
            "python -m unittest discover -s tests -p test_engine_repository.py -v",
            light,
        )

        # I1 must still get full native CI for actual live code, but a
        # static I2/registry guard must not require I1 births.
        for owned in ("tools/assess_engine_proposal.py",
                      "tests/test_engine_repository.py"):
            self.assertNotIn("      - '" + owned + "'", living_paths)
        self.assertIn("      - 'scripts/**'", living_paths)
        self.assertIn("      - '!scripts/check_engine_repository.py'", living_paths)
        self.assertGreater(
            living_paths.index("      - '!scripts/check_engine_repository.py'"),
            living_paths.index("      - 'scripts/**'"),
        )
        for required in (
            "      - 'src/i1/**'",
            "      - 'tests/i1/**'",
            "      - 'tools/run_engine_checks.py'",
            "      - 'config/engine-registry.json'",
            "      - '.github/workflows/i1-current-ci.yml'",
            "      - '.github/workflows/engine-structural.yml'",
        ):
            self.assertIn(required, living_paths)
        for negative in (
            "!src/i1/**/*.md", "!src/i1/docs/**", "!src/i1/AGENTS.md"
        ):
            self.assertGreater(
                living_paths.index(negative),
                living_paths.index("      - '.github/workflows/engine-structural.yml'"),
            )

    def test_original_engine_sources_are_present(self):
        self.assertFalse((ROOT / "src/lab").exists())
        self.assertTrue((ROOT / "archive/i0/lab/__init__.py").is_file())
        for name in ("i0", "i1", "i1/lab", "i1/runtime"):
            self.assertTrue((ROOT / "src" / name).is_dir(), name)


if __name__ == "__main__":
    unittest.main()
