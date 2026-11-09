"""Frozen Candidate-I shared-prior integration checks."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_i_shared_prior_integration as I


class CandidateISharedPriorIntegrationTests(unittest.TestCase):
    def test_base_fallback_discards_both_addends_and_matches_control(self):
        row = I._base_fallback(
            "P80", (80.0, 80.0, 40.0, 80.0, 80.0), 0.25)
        self.assertTrue(row["addends_zero"])
        self.assertTrue(row["score_identity"])
        self.assertTrue(row["top_identity"])
        self.assertTrue(row["action_identity"])
        self.assertTrue(row["funding_identity"])
        self.assertTrue(row["work_identity"])
        self.assertTrue(row["body_identity"])
        self.assertEqual(row["before_mode"], ("reference", "chunk_end"))
        self.assertEqual(row["after_mode"], ("reference", "chunk_end"))
        self.assertEqual(row["candidate_score_addend_mode_after"], "normal")

    def test_food_fallback_is_external_token_renaming_invariant(self):
        left = I._base_fallback(
            "F108", (60.0, 20.0, 80.0, 50.0, 80.0), 0.5,
            token="alpha")
        right = I._base_fallback(
            "F108", (60.0, 20.0, 80.0, 50.0, 80.0), 0.5,
            token="beta")
        for key in (
                "action", "param", "option", "funding", "work",
                "body_after_computation", "scores", "top", "addends_zero"):
            self.assertEqual(left[key], right[key])

    def test_full_frozen_gate_reports_without_prejudging_result(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = I.run(fh.name)
        expected = (
            "CANDIDATE_I_SHARED_PRIOR_INTEGRATION_PASS"
            if all(report["rules"].values()) else
            "CANDIDATE_I_SHARED_PRIOR_INTEGRATION_DEFECT")
        self.assertEqual(report["verdict"], expected)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["runtime_registered"])
        self.assertFalse(report["candidate_i_policy_registered"])
        self.assertFalse(report["new_live_panel_authorized"])
        self.assertEqual(
            report["score_addend_mode_first_contact_fallback"],
            "discard_both_bonus_terms")
        print("CANDIDATE_I_SHARED_PRIOR_INTEGRATION_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "summaries": report["summaries"],
            "fallback_identity_failures":
                report["fallback_identity_failures"][:5],
            "fallback_addend_failures":
                report["fallback_addend_failures"][:5],
            "physical_accounting_failures":
                report["physical_accounting_failures"][:5],
            "renaming_mismatches":
                report["renaming_mismatches"][:5],
            "state_restoration": report["state_restoration"],
        }, sort_keys=True))

    def test_import_does_not_load_life_or_world_generators(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_i_shared_prior_integration; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.worldgen' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
