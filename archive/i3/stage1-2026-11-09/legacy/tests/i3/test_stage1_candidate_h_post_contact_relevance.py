"""Candidate-H post-contact relevance-gated fallback checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_h_post_contact_relevance as P


class CandidateHPostContactRelevanceTests(unittest.TestCase):
    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_h_post_contact_relevance as p; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)

    def test_frozen_personal_history_and_decision_basis(self):
        self.assertEqual(
            P.DRINK_DELTA, (-0.5, -0.2, 35.0, 0.0, 0.0))
        self.assertEqual(P.EXPLORE, (("se_deplacer",),))
        self.assertEqual(
            tuple(sorted(P.H.ORDINARY_PLANS)),
            ("move", "move_wait", "sleep", "wait"))

    def test_characterization_reports_frozen_gate_without_live_authority(self):
        report = P.characterize()
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["runtime_life_access"])
        self.assertFalse(report["evidence_branch_access"])
        self.assertFalse(report["omega_read"])
        self.assertFalse(report["recurrence_read"])
        self.assertFalse(report["motor_command_authorized"])
        self.assertEqual(report["fixture"]["states"], 80)
        self.assertIn(
            report["verdict"],
            (
                "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS",
                "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_FAIL",
            ))
        self.assertFalse(report["runtime_candidate_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        self.assertEqual(
            report["unified_runtime_protocol_authorized"],
            report["verdict"]
            == "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS")
        print("CANDIDATE_H_POST_CONTACT_RELEVANCE_TEST " + json.dumps({
            "verdict": report["verdict"],
            "stage_a": report["stage_a"],
            "fallback": report["fallback"],
            "work": report["work"],
            "physical_accounting_diagnostic":
                report["physical_accounting_diagnostic"],
            "rules": report["rules"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
