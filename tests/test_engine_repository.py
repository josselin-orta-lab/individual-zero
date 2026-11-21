"""Registry invariants independent of the cognitive actor's behavior."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineToolingTests(unittest.TestCase):

    def test_stage8f1h_only_preregistered_T12_native_prospective_proof(self):
        from scripts.check_engine_repository import unexpected_workflows
        permitted="i3-stage8f1h-prospective-body-value-native-proof.yml"
        blocked=(
            "i3-stage8f1h-prospective-body-value-science.yml",
            "i3-stage8f1h-prospective-body-value-native-proof-retry.yml",
            "i3-stage8f1h-new-historical-G2-births.yml",
        )
        entries=[Path(".github/workflows/"+v) for v in (permitted,*blocked)]
        self.assertEqual(unexpected_workflows(entries,active_ci="i1-current-ci.yml"),
                         sorted(blocked))


    def test_stage8f1g_exact_preexposed_separate_td_buffer_workflow(self):
        from scripts.check_engine_repository import unexpected_workflows
        name="i3-stage8f1g-separated-td-buffer-eight-ecologies-proof.yml"
        blocked=(
            "i3-stage8f1g-separated-td-buffer-new-science.yml",
            "i3-stage8f1g-separated-td-buffer-eight-ecologies-proof-retry.yml",
            "i3-stage8f1g-reopen-g2-lives.yml",
        )
        entries=[Path(".github/workflows/"+v) for v in (name,*blocked)]
        self.assertEqual(unexpected_workflows(entries,active_ci="i1-current-ci.yml"),
                         sorted(blocked))


    def test_stage8f1f_only_preregistered_eight_ecological_native_proof(self):
        from scripts.check_engine_repository import unexpected_workflows
        permitted="i3-stage8f1f-eight-ecology-mean-readout-proof.yml"
        rejected=(
            "i3-stage8f1f-eight-ecology-mean-readout-science.yml",
            "i3-stage8f1f-eight-ecology-mean-readout-proof-retry.yml",
            "i3-stage8f1f-new-g2-births.yml",
        )
        entries=[Path(".github/workflows/"+v) for v in (permitted,*rejected)]
        self.assertEqual(unexpected_workflows(entries,active_ci="i1-current-ci.yml"),
                         sorted(rejected))


    def test_stage8f1e_only_preexposed_equal_content_readout_workflow(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8f1e-equal-cost-content-readout-proof.yml"
        rejected=(
            "i3-stage8f1e-equal-cost-content-readout-science.yml",
            "i3-stage8f1e-equal-cost-content-readout-proof-retry.yml",
            "i3-stage8f1e-new-g2-cohort.yml",
        )
        entries=[Path(".github/workflows/"+v) for v in (allowed,*rejected)]
        self.assertEqual(unexpected_workflows(entries,active_ci="i1-current-ci.yml"),
                         sorted(rejected))


    def test_stage8f1d_only_registered_synthetic_next_choice_workflow(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8f1d-next-decision-retention-proof.yml"
        forbidden=(
            "i3-stage8f1d-next-decision-retention-cohort.yml",
            "i3-stage8f1d-next-decision-retention-proof-retry.yml",
            "i3-stage8f1d-new-g2-life-generation.yml",
        )
        paths=[Path(".github/workflows/"+p) for p in (allowed,*forbidden)]
        self.assertEqual(
            unexpected_workflows(paths,active_ci="i1-current-ci.yml"),
            sorted(forbidden))


    def test_stage8f1c_pr_only_synthetic_learning_workflow_is_exact(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed = "i3-stage8f1c-paid-postaction-learning-proof.yml"
        rejected = (
            "i3-stage8f1c-paid-postaction-learning-cohort.yml",
            "i3-stage8f1c-paid-postaction-learning-proof-retry.yml",
            "i3-stage8f1c-g2-native-life-generator.yml",
        )
        workflows = [Path(".github/workflows/" + name)
                     for name in (allowed, *rejected)]
        self.assertEqual(
            unexpected_workflows(workflows, active_ci="i1-current-ci.yml"),
            sorted(rejected))


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

    def test_stage8a_mean_persistence_once_whitelist_is_not_wildcard(self):
        from scripts.check_engine_repository import unexpected_workflows

        accepted = "i3-stage8a-mean-persistence-once-20261116.yml"
        denied = ("i3-stage8a-mean-persistence-once-20261116-retry.yml",
                  "i3-stage8a-mean-persistence-once-20261117.yml",
                  "i3-stage8a-fishing-seeds.yml")
        entries = [Path(".github/workflows/" + x)
                   for x in (accepted, *denied)]
        self.assertEqual(unexpected_workflows(
            entries, active_ci="i1-current-ci.yml"), sorted(denied))

    def test_stage8a_posthoc_readonly_audit_allowance_is_exact(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage8a-readonly-original-audit-20261117.yml"
        rejected = ("i3-stage8a-readonly-original-audit-retry.yml",
                    "i3-stage8a-readonly-original-audit-20261118.yml",
                    "i3-stage8a-new-lives-masquerading-as-audit.yml")
        paths = [Path(".github/workflows/" + file)
                 for file in (allowed, *rejected)]
        self.assertEqual(
            unexpected_workflows(paths,active_ci="i1-current-ci.yml"),
            sorted(rejected))

    def test_stage8b_heldout_ecology_once_is_only_allowed_exact_workflow(self):
        from scripts.check_engine_repository import unexpected_workflows

        name = "i3-stage8b-ecology-heldout-once-20261117.yml"
        blocked = (
            "i3-stage8b-ecology-heldout-once-20261117-retry.yml",
            "i3-stage8b-ecology-heldout-once-20261118.yml",
            "i3-stage8b-select-favorable-ecologies.yml",
        )
        candidates = [Path(".github/workflows/" + x)
                      for x in (name, *blocked)]
        self.assertEqual(unexpected_workflows(
            candidates, active_ci="i1-current-ci.yml"), sorted(blocked))

    def test_stage8b_readonly_original_audit_is_exact_only(self):
        from scripts.check_engine_repository import unexpected_workflows

        approved = "i3-stage8b-readonly-original-audit-20261117.yml"
        forbidden = (
            "i3-stage8b-readonly-original-audit-20261118.yml",
            "i3-stage8b-readonly-original-audit-20261117-retry.yml",
            "i3-stage8b-original-sample-relaunch.yml",
        )
        candidates=[Path(".github/workflows/" + name)
                    for name in (approved,*forbidden)]
        self.assertEqual(unexpected_workflows(
            candidates,active_ci="i1-current-ci.yml"),sorted(forbidden))

    def test_stage8e2_consumed_technical_and_single_science_allowance(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage8e2-prospective-science-once-20261120.yml"
        blocked = (
            "i3-stage8e2-two-native-technical-once-20261119.yml",
            "i3-stage8e2-two-native-technical-once-20261119-retry.yml",
            "i3-stage8e2-prospective-science-once-20261120-retry.yml",
            "i3-stage8e2-prospective-science-once-20261121.yml",
            "i3-stage8e2-gamma-causal-science.yml",
        )
        entries = [Path(".github/workflows/" + name)
                   for name in (allowed, *blocked)]
        self.assertEqual(
            unexpected_workflows(entries, active_ci="i1-current-ci.yml"),
            sorted(blocked),
        )

    def test_stage8f1b_independent_existing_receipts_only_once(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8f1b-cold-existing-native-receipts-once-20261121.yml"
        forbidden=(
            "i3-stage8f1b-cold-existing-native-receipts-once-20261121-retry.yml",
            "i3-stage8f1b-cold-existing-native-receipts-once-20261122.yml",
            "i3-stage8f1b-new-world-cold-originals-once-20261121.yml",
        )
        paths=[Path(".github/workflows/"+n) for n in (allowed,*forbidden)]
        self.assertEqual(unexpected_workflows(paths,active_ci="i1-current-ci.yml"),
                         sorted(forbidden))

    def test_stage8f1b_corrected_pythonpath_proof_only_once(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8f1b-matched-native-funding-proof-once-20261121.yml"
        forbidden=(
            "i3-stage8f1b-matched-native-funding-proof-once-20261121-retry.yml",
            "i3-stage8f1b-matched-native-funding-proof-once-20261122.yml",
            "i3-stage8f1b-new-native-births-once-20261121.yml",
        )
        names=[Path(".github/workflows/"+n) for n in (allowed,*forbidden)]
        self.assertEqual(unexpected_workflows(names,active_ci="i1-current-ci.yml"),
                         sorted(forbidden))

    def test_stage8f1b_matched_native_funding_one_shot_only(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8f1b-matched-native-funding-once-20261120.yml"
        forbidden=(
            "i3-stage8f1b-matched-native-funding-once-20261120-retry.yml",
            "i3-stage8f1b-matched-native-funding-once-20261121.yml",
            "i3-stage8f1b-new-native-scientific-cohort.yml",
        )
        paths=[Path(".github/workflows/"+n) for n in (allowed,*forbidden)]
        self.assertEqual(unexpected_workflows(paths,active_ci="i1-current-ci.yml"),
                         sorted(forbidden))

    def test_stage8e3d_original_energy_aggregate_one_shot_only(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8e3d-readonly-energy-ledger-once-20261120.yml"
        foreign=(
            "i3-stage8e3d-readonly-energy-ledger-once-20261120-retry.yml",
            "i3-stage8e3d-readonly-energy-ledger-once-20261121.yml",
            "i3-stage8e3d-new-native-gamma-simulation.yml",
        )
        workflows=[Path(".github/workflows/"+name) for name in (allowed,*foreign)]
        self.assertEqual(
            unexpected_workflows(workflows, active_ci="i1-current-ci.yml"),
            sorted(foreign))

    def test_stage8e3c_original_timecourse_one_shot_only(self):
        from scripts.check_engine_repository import unexpected_workflows
        allowed="i3-stage8e3c-readonly-first-energy-gate-once-20261120.yml"
        forbidden=(
            "i3-stage8e3c-readonly-first-energy-gate-once-20261121.yml",
            "i3-stage8e3c-readonly-first-energy-gate-once-20261120-retry.yml",
            "i3-stage8e3c-new-gamma-science-once-20261120.yml",
        )
        workflows=[Path(".github/workflows/"+name) for name in (allowed,*forbidden)]
        self.assertEqual(
            unexpected_workflows(workflows,active_ci="i1-current-ci.yml"),
            sorted(forbidden))

    def test_stage8e3b_funding_original_readonly_allowance_is_exact_only(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage8e3b-readonly-native-funding-gates-once-20261120.yml"
        forbidden = (
            "i3-stage8e3b-readonly-native-funding-gates-once-20261121.yml",
            "i3-stage8e3b-readonly-native-funding-gates-once-20261120-retry.yml",
            "i3-stage8e3b-new-genomic-science-once-20261120.yml",
        )
        workflows = [Path(".github/workflows/" + name)
                     for name in (allowed, *forbidden)]
        self.assertEqual(
            unexpected_workflows(workflows, active_ci="i1-current-ci.yml"),
            sorted(forbidden),
        )

    def test_stage8e3a_original_readonly_allowance_is_exact_only(self):
        from scripts.check_engine_repository import unexpected_workflows

        allowed = "i3-stage8e3a-readonly-native-g2-originals-once-20261120.yml"
        forbidden = (
            "i3-stage8e3a-readonly-native-g2-originals-once-20261120-retry.yml",
            "i3-stage8e3a-scientific-new-gamma-cohort.yml",
            "i3-stage8e3a-readonly-native-g2-originals-once-20261121.yml",
        )
        workflows = [Path(".github/workflows/" + name)
                     for name in (allowed, *forbidden)]
        self.assertEqual(
            unexpected_workflows(workflows, active_ci="i1-current-ci.yml"),
            sorted(forbidden),
        )

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
            # Same changes must still activate I2's lightweight archival PR gate.
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
        # I2 is now a pinned historical generation: no routine pull request
        # can launch the complete I2 paid synthetic test/replay matrix.
        self.assertIn("  workflow_dispatch:", light)
        self.assertIn("python tools/check_i2_archive.py --json", light)
        self.assertIn("python -m unittest discover -s tests -p test_historical_generation_archive.py -v", light)
        self.assertEqual(light.count("python tools/i2_ci_shards.py"), 1)
        full_step = light.split("      - name: Full archived I2 test suite (explicit manual audit ONLY)", 1)[1]
        self.assertIn("if: github.event_name == 'workflow_dispatch'", full_step)
        self.assertIn("I2_EXPLICIT_HISTORICAL_TECHNICAL_AUDIT", full_step)
        self.assertLess(light.index("python tools/check_i2_archive.py --json"),
                        light.index("python tools/i2_ci_shards.py"))
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
