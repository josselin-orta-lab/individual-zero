"""Frozen multi-phase Stage-0 processing reducer repair checks."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.archive.stage1.lab import stage1_multiphase_processing_reducer_repair as G


class MultiphaseProcessingReducerRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = G.characterize()

    def test_exact_legacy_shape_is_reproduced(self):
        self.assertTrue(
            self.report["rules"]["M1_exact_legacy_reproduction"])

    def test_declared_multiphase_shapes_reduce_with_frozen_processing_semantics(self):
        accepted = self.report["accepted"]
        self.assertTrue(accepted["candidate_h_stage_b_no_processing"])
        self.assertTrue(accepted["candidate_h_stage_b_funded"])
        self.assertTrue(accepted["candidate_i_fallback_no_processing"])
        self.assertTrue(accepted["candidate_i_information_final"])
        self.assertTrue(accepted["candidate_i_post_contact_no_processing"])

    def test_all_adversarial_receipts_fail_closed(self):
        self.assertTrue(all(
            self.report["invalid_rejections"].values()))

    def test_composite_prerequisite_stays_green(self):
        self.assertEqual(
            self.report["composite_prerequisite"],
            "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS")

    def test_frozen_m0_m9_gate_passes_without_live_authority(self):
        report = self.report
        self.assertEqual(
            report["verdict"],
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS")
        self.assertTrue(all(report["rules"].values()))
        self.assertFalse(report["world_access"])
        self.assertFalse(report["runtime_life_access"])
        self.assertFalse(report["p2_ecology_access"])
        self.assertFalse(report["evidence_branch_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["64_65_retry_authorized"])
        self.assertFalse(report["J1_J7_verdict_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        print("MULTIPHASE_PROCESSING_REDUCER_REPAIR_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "accepted": report["accepted"],
        }, sort_keys=True))

    def test_run_serializes_same_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertEqual(
            report["verdict"],
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS")

    def test_import_does_not_load_world_life_or_p2(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.archive.stage1.lab.stage1_multiphase_processing_reducer_repair; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
