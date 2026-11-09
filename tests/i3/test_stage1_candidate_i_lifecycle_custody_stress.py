"""Frozen Candidate-I lifecycle custody stress checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.archive.stage1.lab import stage1_candidate_i_lifecycle_custody_stress as L


class CandidateILifecycleCustodyStressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = L.characterize()

    def test_frozen_runtime_matrix_is_exact_and_non_scientific(self):
        row = self.report["runtime_matrix"]
        self.assertEqual(row["families"], ("stable", "depletion", "pulse"))
        self.assertEqual(
            row["policies"],
            (
                "personal_relevance_candidate_h_v1",
                "personal_shared_prior_candidate_i_v1",
                "personal_shared_prior_candidate_i_omega0_ablation_v1",
            ))
        self.assertEqual(row["development_index"], 0)
        self.assertEqual(row["world_seed"], 2000)
        self.assertEqual(row["genome_seed"], 901)
        self.assertEqual(row["life_seed"], 7_490_003)
        self.assertEqual(row["horizon"], 24)
        self.assertEqual(row["lives"], 9)
        self.assertEqual(row["max_physical_steps"], 216)
        self.assertEqual(self.report["scientific_gate"], "NOT_EVALUATED")
        self.assertFalse(self.report["fresh_development_condition_opened"])
        self.assertFalse(self.report["selection_validation_reserve_access"])
        self.assertFalse(self.report["60_61_evidence_acceptance_input"])
        self.assertFalse(self.report["62_63_evidence_acceptance_input"])

    def test_prerequisite_repairs_stay_green(self):
        row = self.report["prerequisites"]
        self.assertEqual(
            row["branch_settlement"],
            "BRANCH_DECISION_SETTLEMENT_REPAIR_PASS")
        self.assertEqual(
            row["probe_authority"],
            "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS")
        self.assertEqual(
            row["runtime_v2"], "GUARDED_BY_FULL_I3_TEST_SUITE")
        self.assertEqual(row["60_61_status"], "EXPOSED_CLOSED_NO_J1_J7")
        self.assertEqual(row["62_63_status"], "EXPOSED_CLOSED_NO_J1_J7")

    def test_fallback_lifecycle_owns_current_settlement_and_memory(self):
        row = self.report["synthetic"]["fallback"]
        self.assertEqual(row["route"], "P1.3_BASE_FINAL")
        self.assertTrue(row["addends_zero"])
        self.assertTrue(row["phase_sum_exact"])
        self.assertTrue(row["settlement_start_is_pre_stage_a"])
        self.assertTrue(row["branch_commit_exact"])
        self.assertTrue(row["opportunity_commit_exact"])
        self.assertTrue(row["authority_closed_after_learning"])
        self.assertTrue(row["next_decision"]["work_matches"])
        self.assertTrue(row["next_decision"]["settlement_current"])
        self.assertTrue(row["next_decision"]["persistent_reference"])

    def test_relevant_lifecycle_owns_current_settlement_and_memory(self):
        row = self.report["synthetic"]["relevant"]
        self.assertEqual(row["route"], "INFORMATION_FINAL")
        self.assertTrue(row["persistent_reference"])
        self.assertTrue(row["settlement_start_is_pre_stage_a"])
        self.assertTrue(row["branch_commit_exact"])
        self.assertTrue(row["opportunity_commit_exact"])
        self.assertTrue(row["authority_closed_after_learning"])
        self.assertTrue(row["next_decision"]["work_matches"])
        self.assertTrue(row["next_decision"]["settlement_current"])
        self.assertTrue(row["next_decision"]["persistent_reference"])

    def test_both_unfunded_paths_leave_no_learning_authority(self):
        common = self.report["synthetic"]["common_unfunded"]
        self.assertEqual(common["route"], "PROBE_UNFUNDED")
        self.assertEqual(common["reason"], "COMMON_MATRIX_UNFUNDED")
        self.assertTrue(common["no_motor"])
        self.assertTrue(common["authority_empty"])
        self.assertTrue(common["work_matches"])
        self.assertTrue(common["next_decision"]["work_matches"])
        self.assertTrue(common["next_decision"]["settlement_current"])

        recurrence = self.report["synthetic"]["recurrence_unfunded"]
        self.assertEqual(recurrence["route"], "PROBE_UNFUNDED")
        self.assertEqual(
            recurrence["reason"], "RECURRENCE_READ_UNFUNDED")
        self.assertTrue(recurrence["no_motor"])
        self.assertTrue(recurrence["authority_empty"])
        self.assertTrue(recurrence["work_matches"])
        self.assertTrue(recurrence["next_decision"]["work_matches"])
        self.assertTrue(recurrence["next_decision"]["settlement_current"])

    def test_post_contact_lifecycle_stays_candidate_h_and_omega_free(self):
        row = self.report["synthetic"]["post_contact"]
        self.assertEqual(row["route"], "POST_CONTACT_CANDIDATE_H")
        self.assertTrue(row["omega_unused"])
        self.assertTrue(row["decision_motor_work_parity"])
        self.assertTrue(row["observer_parity"])
        self.assertTrue(row["branch_commit_parity"])
        self.assertTrue(row["opportunity_commit_parity"])
        self.assertTrue(row["candidate_authority_closed"])
        self.assertTrue(row["control_authority_closed"])

    def test_same_genome_omega0_is_only_a_first_contact_ablation(self):
        row = self.report["synthetic"]["omega0"]
        self.assertTrue(row["genome_digest_equal"])
        self.assertTrue(row["native_omega_preserved"])
        self.assertTrue(row["zero_applied"])
        self.assertTrue(row["native_nonzero"])
        self.assertTrue(row["branch_memory_individual"])
        self.assertTrue(row["opportunity_memory_individual"])
        self.assertTrue(row["effects_individual"])
        self.assertTrue(row["values_individual"])

        self.assertEqual(len(self.report["omega0_pairs"]), 3)
        for pair in self.report["omega0_pairs"]:
            self.assertTrue(pair["same_genome"])
            self.assertEqual(pair["zero_omega"], 0.0)
            self.assertEqual(
                pair["zero_omega_source"],
                "SAME_GENOME_SOFTWARE_ABLATION")
            self.assertTrue(pair["persistent_equal"])

    def test_nine_exposed_condition_smokes_reduce_cleanly(self):
        rows = self.report["smokes"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(self.report["smoke_failures"], [])
        for row in rows:
            with self.subTest(
                    family=row["family"], policy=row["policy"]):
                self.assertEqual(row["development_index"], 0)
                self.assertEqual(row["world_seed"], 2000)
                self.assertEqual(
                    row["world_name"],
                    f"p2-{row['family']}-2000")
                self.assertIn(row["terminal"], ("dead", "censored"))
                self.assertLessEqual(row["steps_lived"], 24)
                self.assertEqual(row["shortfall_steps"], 0)
                self.assertEqual(
                    row["revision_scientific_verdict"],
                    "NOT_EVALUATED")
                self.assertEqual(row["policy_checks"]["failures"], [])
                self.assertEqual(row["memory_failures"], [])

    def test_l0_l11_pass_without_scientific_or_live_authority(self):
        report = self.report
        self.assertTrue(all(report["rules"].values()))
        self.assertEqual(
            report["verdict"],
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS")
        self.assertFalse(report["J1_J7_verdict_authorized"])
        self.assertTrue(report["new_live_protocol_proposal_authorized"])
        self.assertFalse(report["new_live_panel_execution_authorized"])
        self.assertFalse(report["stage2_authorized"])
        print("CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "smoke_failures": report["smoke_failures"],
            "runtime_matrix": report["runtime_matrix"],
        }, sort_keys=True))

    def test_import_is_inert_until_characterize(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.archive.stage1.lab.stage1_candidate_i_lifecycle_custody_stress; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
