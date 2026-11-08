"""Frozen branch-decision settlement repair checks."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_branch_decision_settlement_repair as G
from i3.modules.body import CognitiveWork


class BranchDecisionSettlementRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = G.characterize()

    def test_frozen_synthetic_fixture_reproduces_legacy_failure(self):
        report = self.report
        self.assertEqual(report["fixture"]["B0"], G.B0)
        self.assertEqual(report["fixture"]["WA"], {
            "cycles": 10, "simulated_steps": 0,
            "memory_items": 0, "replays": 0})
        self.assertEqual(report["fixture"]["WB"], {
            "cycles": 5, "simulated_steps": 0,
            "memory_items": 0, "replays": 0})
        self.assertEqual(report["fixture"]["WT"], {
            "cycles": 15, "simulated_steps": 0,
            "memory_items": 0, "replays": 0})
        self.assertTrue(report["legacy_mismatch_reproduced"])

    def test_repaired_pair_keeps_total_work_and_exact_delta(self):
        report = self.report
        self.assertEqual(
            report["direct_repaired"]["work"],
            {
                "cycles": 1, "simulated_steps": 0,
                "memory_items": 16, "replays": 0})
        self.assertTrue(
            report["direct_repaired"]["matches_expected"])
        self.assertTrue(
            report["direct_repaired"]["store_work_exact"])
        self.assertTrue(
            report["candidate_h"]["matches_expected"])
        self.assertTrue(
            report["candidate_i"]["matches_expected"])

    def test_candidate_producers_bind_total_work_to_pre_stage_a_body(self):
        for name in ("candidate_h_producer", "candidate_i_producer"):
            row = self.report[name]
            with self.subTest(name=name):
                self.assertTrue(row["start_matches"])
                self.assertTrue(row["work_matches"])
                self.assertIsNotNone(row["stage_a_paid"])

    def test_receipt_is_consumed_and_missing_receipt_fails_closed(self):
        for name in ("reference", "candidate_h", "candidate_i"):
            self.assertTrue(
                self.report[name]["settlement_consumed"])
        self.assertTrue(
            self.report["rules"][
                "B7_missing_or_stale_receipt_fails_closed"])
        self.assertTrue(self.report["stale_receipt_replaced"])

    def test_upper_cost_shadow_keeps_its_local_reference_interval(self):
        shadow = self.report["upper_cost_shadow"]
        self.assertTrue(all(shadow.values()))

    def test_gate_passes_all_frozen_rules_without_live_authority(self):
        report = self.report
        self.assertEqual(
            report["verdict"],
            "BRANCH_DECISION_SETTLEMENT_REPAIR_PASS")
        self.assertTrue(all(report["rules"].values()))
        self.assertFalse(report["world_access"])
        self.assertFalse(report["runtime_life_access"])
        self.assertFalse(report["p2_ecology_access"])
        self.assertFalse(report["evidence_branch_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["60_61_retry_authorized"])
        self.assertFalse(report["J1_J7_verdict_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        print("BRANCH_DECISION_SETTLEMENT_REPAIR_TEST " + json.dumps({
            "verdict": report["verdict"],
            "legacy_mismatch_reproduced":
                report["legacy_mismatch_reproduced"],
            "rules": report["rules"],
        }, sort_keys=True))

    def test_run_serializes_same_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertEqual(
            report["verdict"],
            "BRANCH_DECISION_SETTLEMENT_REPAIR_PASS")

    def test_import_does_not_load_runtime_life_or_p2_ecology(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_branch_decision_settlement_repair; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
