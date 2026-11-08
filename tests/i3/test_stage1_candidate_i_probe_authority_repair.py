"""Frozen Candidate-I probe-restore authority repair checks."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_i_probe_authority_repair as G


class CandidateIProbeAuthorityRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = G.characterize()

    def test_legacy_stale_authority_resurrection_is_reproduced(self):
        row = self.report["legacy"]
        self.assertTrue(row["stale_last_restored"])
        self.assertTrue(row["settlement_absent"])
        self.assertTrue(row["learning_boundary_rejected"])

    def test_snapshot_has_no_learning_authority_and_is_taken_after_clear(self):
        self.assertEqual(self.report["forbidden_snapshot_keys"], ())
        row = self.report["common_matrix_unfunded"]
        self.assertTrue(row["authority_at_snapshot_empty"])

    def test_both_probe_unfunded_exits_restore_perception_only(self):
        common = self.report["common_matrix_unfunded"]
        self.assertEqual(common["route"], "PROBE_UNFUNDED")
        self.assertEqual(common["reason"], "COMMON_MATRIX_UNFUNDED")
        self.assertTrue(common["authority_after_empty"])
        self.assertTrue(common["reversible_restored"])
        self.assertTrue(common["work_matches"])

        recurrence = self.report["recurrence_read_unfunded"]
        self.assertEqual(recurrence["route"], "PROBE_UNFUNDED")
        self.assertEqual(
            recurrence["reason"], "RECURRENCE_READ_UNFUNDED")
        self.assertTrue(recurrence["authority_after_empty"])
        self.assertTrue(recurrence["reversible_restored"])
        self.assertTrue(recurrence["work_matches"])

    def test_fallback_creates_only_current_decision_authority(self):
        row = self.report["fallback"]
        self.assertEqual(row["route"], "P1.3_BASE_FINAL")
        self.assertTrue(row["single_current_cell_observation"])
        self.assertTrue(row["last_is_fresh"])
        self.assertTrue(row["settlement_aligned"])
        self.assertTrue(row["phase_work_exact"])
        self.assertTrue(row["addends_zero"])

    def test_relevant_path_creates_only_current_decision_authority(self):
        row = self.report["relevant"]
        self.assertTrue(row["found"])
        self.assertIsNotNone(row["body"])
        self.assertTrue(row["last_is_fresh"])
        self.assertTrue(row["settlement_aligned"])
        self.assertTrue(row["persistent_reference"])

    def test_post_contact_remains_candidate_h_and_omega_free(self):
        row = self.report["post_contact"]
        self.assertTrue(row["motor_work_equal"])
        self.assertTrue(row["observer_equal"])
        self.assertEqual(row["route"], "POST_CONTACT_CANDIDATE_H")
        self.assertTrue(row["omega_unused"])

    def test_frozen_gate_passes_without_live_or_retry_authority(self):
        report = self.report
        self.assertEqual(
            report["verdict"],
            "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS")
        self.assertTrue(all(report["rules"].values()))
        self.assertFalse(report["world_access"])
        self.assertFalse(report["runtime_life_access"])
        self.assertFalse(report["p2_ecology_access"])
        self.assertFalse(report["evidence_branch_acceptance_input"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["60_61_retry_authorized"])
        self.assertFalse(report["62_63_retry_authorized"])
        self.assertFalse(report["J1_J7_verdict_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        print("CANDIDATE_I_PROBE_AUTHORITY_REPAIR_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "relevant_body": report["relevant"]["body"],
        }, sort_keys=True))

    def test_run_serializes_same_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertEqual(
            report["verdict"],
            "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS")

    def test_import_does_not_load_runtime_life_or_p2_ecology(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_i_probe_authority_repair; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
