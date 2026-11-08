"""Unified Candidate-H software-integration checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_h_unified_integration as U
from i3.modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind,
    first_contact_relevant_fields,
    post_contact_relevant_scores)


class CandidateHUnifiedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = U.characterize()

    def test_import_has_no_world_generation_or_runtime_life_authority(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.personal_relevance_candidate_h_mind; "
            "import i3.lab.stage1_candidate_h_unified_integration; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.worldgen' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)

    def test_frozen_relevance_predicates_are_exact(self):
        self.assertTrue(first_contact_relevant_fields(
            ("TRIAL",), 0.01, 0.02))
        self.assertFalse(first_contact_relevant_fields(
            ("DECLINE_TRIAL",), 0.01, 0.02))
        self.assertFalse(first_contact_relevant_fields(
            ("TRIAL",), 0.0, 0.02))

        with_scores = {"frontier": 2.0, "wait": 1.5}
        without_scores = {"frontier": 1.0, "wait": 1.5}
        self.assertTrue(post_contact_relevant_scores(
            with_scores, without_scores, ("frontier",)))
        self.assertFalse(post_contact_relevant_scores(
            with_scores, with_scores, ("frontier",)))

    def test_report_preserves_frozen_classifier_identities(self):
        first = self.report["first_contact_parity"]
        post = self.report["post_contact_parity"]
        self.assertEqual(
            (first["states"], first["relevant"], first["fallback"]),
            (80, 24, 56))
        self.assertEqual(first["mismatches"], [])
        self.assertEqual(
            (post["states"], post["relevant"], post["fallback"]),
            (80, 68, 12))
        self.assertEqual(post["mismatches"], [])

    def test_routing_panel_is_exact_frozen_envelope(self):
        panel = self.report["routing_panel"]
        self.assertEqual(panel["decisions_per_omega"], 60)
        self.assertEqual(
            tuple(panel["history_modes"]), U.HISTORY_MODES)
        self.assertEqual(tuple(panel["omega_arms"]), U.OMEGA_ARMS)
        self.assertEqual(
            len(panel["rows_omega_minus1"]), 60)
        self.assertEqual(
            len(panel["rows_omega_plus1"]), 60)

    def test_gate_reports_result_without_granting_runtime(self):
        report = self.report
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["evidence_branch_access"])
        self.assertFalse(report["runtime_registered"])
        self.assertFalse(report["runtime_registration_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        self.assertFalse(
            report["selection_validation_reserve_authorized"])
        self.assertIn(
            report["verdict"],
            (
                "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS",
                "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_FAIL",
            ))
        self.assertEqual(
            report["future_development_protocol_authorized"],
            report["verdict"]
            == "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS")
        print("CANDIDATE_H_UNIFIED_INTEGRATION_TEST " + json.dumps({
            "verdict": report["verdict"],
            "first_contact_parity": report["first_contact_parity"],
            "post_contact_parity": report["post_contact_parity"],
            "routing_panel": {
                "decisions_per_omega":
                    report["routing_panel"]["decisions_per_omega"],
                "errors": report["routing_panel"]["errors"],
                "route_counts_omega_minus1":
                    report["routing_panel"]["route_counts_omega_minus1"],
                "probe_unfunded_omega_minus1":
                    report["routing_panel"]["probe_unfunded_omega_minus1"],
                "fallback_identity_failures":
                    report["routing_panel"]["fallback_identity_failures"],
                "routes_observed":
                    report["routing_panel"]["routes_observed"],
                "omega_mismatches":
                    report["routing_panel"]["omega_mismatches"],
            },
            "forced_failure": report["forced_failure"],
            "rules": report["rules"],
        }, sort_keys=True))

    def test_candidate_class_stays_unregistered_and_omega_free(self):
        mind = U._make_mind(0.0, "NO_SUPPORT")
        self.assertIsInstance(mind, PersonalRelevanceCandidateHMind)
        self.assertFalse(hasattr(mind, "first_contact_omega"))
        self.assertEqual(
            (mind.simulation_mode, mind.projection_accounting),
            ("reference", "chunk_end"))


if __name__ == "__main__":
    unittest.main()
