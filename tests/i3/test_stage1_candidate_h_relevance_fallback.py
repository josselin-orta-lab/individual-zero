"""Candidate-H relevance-gated fallback software checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_h_relevance_fallback as H


class CandidateHRelevanceFallbackTests(unittest.TestCase):
    def test_import_has_no_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_h_relevance_fallback; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)

    def test_frozen_ordinary_basis(self):
        self.assertEqual(
            H.ORDINARY_PLANS,
            {
                "wait": (("attendre",),),
                "sleep": (("dormir",),),
                "move": (("se_deplacer",),),
                "move_wait": (("se_deplacer",), ("attendre",)),
            })

    def test_characterization_is_bounded_and_reports_frozen_gate(self):
        report = H.characterize()
        self.assertFalse(report["world_access"])
        self.assertFalse(report["runtime_life_access"])
        self.assertFalse(report["evidence_branch_access"])
        self.assertFalse(report["omega_read"])
        self.assertFalse(report["motor_command_authorized"])
        self.assertEqual(report["fixture"]["states"], 80)
        self.assertEqual(report["canonical_probe"]["relevant"], 24)
        self.assertEqual(report["canonical_probe"]["fallback"], 56)
        self.assertEqual(report["canonical_probe"]["declined"], 40)
        self.assertAlmostEqual(
            report["canonical_probe"]["mean_simulated_steps"],
            470.05, places=9)
        self.assertIn(
            report["verdict"],
            (
                "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS",
                "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_FAIL",
            ))
        self.assertFalse(report["runtime_candidate_authorized"])
        self.assertFalse(report["post_contact_generalization_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        print("CANDIDATE_H_RELEVANCE_FALLBACK_TEST " + json.dumps({
            "verdict": report["verdict"],
            "canonical_probe": report["canonical_probe"],
            "fallback": report["fallback"],
            "work": report["work"],
            "rules": report["rules"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
