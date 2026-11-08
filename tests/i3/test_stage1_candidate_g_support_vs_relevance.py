"""Candidate-G support-vs-relevance diagnostic software checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_support_vs_relevance as D


class CandidateGSupportVsRelevanceTests(unittest.TestCase):
    def test_import_does_not_load_runtime_or_world(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_g_support_vs_relevance as d; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules"
        ], check=True)

    def test_frozen_plan_basis(self):
        self.assertEqual(
            D.ORDINARY_PLANS,
            {
                "wait": (("attendre",),),
                "sleep": (("dormir",),),
                "move": (("se_deplacer",),),
                "move_wait": (("se_deplacer",), ("attendre",)),
            })

    def test_characterization_preserves_canonical_kernel_and_reports_drift(self):
        report = D.characterize()
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["evidence_branch_access"])
        self.assertFalse(report["omega_read"])
        self.assertTrue(report["support_present_in_all_states"])
        self.assertEqual(report["kernel"]["evaluated"], 80)
        self.assertEqual(report["kernel"]["strict_epistemic_selected"], 24)
        self.assertEqual(report["kernel"]["support_only_nonselected"], 56)
        self.assertEqual(report["kernel"]["declined"], 40)
        self.assertAlmostEqual(
            report["kernel"]["mean_simulated_steps"], 470.05, places=9)
        self.assertEqual(
            report["kernel"]["actual_work_ceiling_violations"], 0)
        self.assertEqual(
            report["classification"] in (
                "SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT",
                "NO_SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_ON_GRID"),
            True)
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["candidate_h_implementation_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        print("CANDIDATE_G_SUPPORT_VS_RELEVANCE_TEST " + json.dumps({
            "classification": report["classification"],
            "kernel": report["kernel"],
            "support_only_nonselected_states":
                report["support_only_nonselected_states"],
            "strict_selected_states": report["strict_selected_states"],
            "all_states": report["all_states"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
