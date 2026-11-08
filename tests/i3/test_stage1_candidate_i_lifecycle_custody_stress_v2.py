"""Candidate-I lifecycle custody stress v2 checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_i_lifecycle_custody_stress_v2 as V


class CandidateILifecycleCustodyStressV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = V.characterize()

    def test_historical_l0_l11_is_preserved_exactly(self):
        row = self.report["historical_lifecycle"]
        self.assertEqual(
            row["verdict"],
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS")
        self.assertTrue(all(row["rules"].values()))
        self.assertEqual(row["smoke_failures"], [])
        matrix = row["runtime_matrix"]
        self.assertEqual(matrix["lives"], 9)
        self.assertEqual(matrix["development_index"], 0)
        self.assertEqual(matrix["world_seed"], 2000)
        self.assertEqual(matrix["genome_seed"], 901)
        self.assertEqual(matrix["life_seed"], 7_490_003)
        self.assertEqual(matrix["horizon"], 24)

    def test_multiphase_reducer_m0_m9_stays_green(self):
        row = self.report["multiphase_reducer"]
        self.assertEqual(
            row["verdict"],
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS")
        self.assertTrue(all(row["rules"].values()))
        self.assertEqual(
            row["composite_prerequisite"],
            "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS")

    def test_generic_geometry_forces_stage_b_processing_failure(self):
        row = self.report["geometry"]
        self.assertEqual(row["body"], (0.15, 80.0, 80.0, 80.0, 80.0))
        self.assertEqual(
            row["stage_a_work"],
            {"cycles": 5, "simulated_steps": 0,
             "memory_items": 0, "replays": 0})
        self.assertAlmostEqual(row["energy_after_stage_a"], 0.05)
        self.assertTrue(row["three_cycle_base_unfunded"])

    def test_candidate_h_production_receipt_is_sequential_no_processing(self):
        row = self.report["forced"]["h"]
        self.assertEqual(row["route"], "P1.3_FINAL")
        self.assertEqual(row["public_funding"], "NO_PROCESSING_BUDGET")
        self.assertEqual(row["observer_outcome"], "no_processing_budget")
        self.assertTrue(row["action_none"])
        self.assertTrue(row["stage_a_exact"])
        self.assertTrue(row["stage_b_zero"])
        self.assertTrue(row["total_exact"])
        self.assertTrue(row["body_exact"])
        self.assertTrue(row["persistent_reference"])

    def test_candidate_i_native_and_omega0_production_receipts_are_post_contact(self):
        for name in ("native", "omega0"):
            row = self.report["forced"][name]
            with self.subTest(name=name):
                self.assertEqual(row["route"], "POST_CONTACT_CANDIDATE_H")
                self.assertEqual(row["nested_route"], "P1.3_FINAL")
                self.assertEqual(
                    row["public_funding"], "NO_PROCESSING_BUDGET")
                self.assertEqual(
                    row["observer_outcome"], "no_processing_budget")
                self.assertTrue(row["omega_unused"])
                self.assertEqual(
                    row["post_contact_source"],
                    "CANDIDATE_H_1163_UNCHANGED")
                self.assertTrue(row["action_none"])
                self.assertTrue(row["stage_a_exact"])
                self.assertTrue(row["stage_b_zero"])
                self.assertTrue(row["total_exact"])
                self.assertTrue(row["body_exact"])
                self.assertTrue(row["persistent_reference"])

        omega = self.report["forced"]["omega0_custody"]
        self.assertNotEqual(omega["native_genome_omega"], 0.0)
        self.assertEqual(omega["native_omega"], omega["native_genome_omega"])
        self.assertEqual(omega["omega0_applied"], 0.0)
        self.assertTrue(omega["branch_memory_individual"])
        self.assertTrue(omega["opportunity_memory_individual"])
        self.assertTrue(omega["effects_individual"])
        self.assertTrue(omega["values_individual"])

    def test_actual_receipts_reduce_as_unprocessed_without_hiding_total_work(self):
        for name, row in self.report["forced"]["joins"].items():
            with self.subTest(name=name):
                self.assertEqual(
                    row["processing_owner_work"],
                    {"cycles": 0, "simulated_steps": 0,
                     "memory_items": 0, "replays": 0})
                self.assertFalse(row["processing_paid"])
                self.assertFalse(row["positive_drink"])
                self.assertEqual(
                    row["total_work"],
                    {"cycles": 5, "simulated_steps": 0,
                     "memory_items": 0, "replays": 0})

    def test_following_decision_replaces_forced_settlement_authority(self):
        for name, row in self.report["forced"]["cleanup"].items():
            with self.subTest(name=name):
                self.assertTrue(row["before_last_none"])
                self.assertTrue(row["before_pending_branch_none"])
                self.assertTrue(row["before_pending_opportunity_none"])
                self.assertTrue(row["previous_settlement_bound_to_forced_body"])
                self.assertTrue(row["work_matches"])
                self.assertTrue(row["new_settlement_current"])
                self.assertTrue(row["stale_last_not_resurrected"])
                self.assertTrue(row["persistent_reference"])

    def test_v0_v8_pass_without_scientific_or_live_execution_authority(self):
        report = self.report
        self.assertEqual(
            report["verdict"],
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS")
        self.assertTrue(all(report["rules"].values()))
        self.assertEqual(report["scientific_gate"], "NOT_EVALUATED")
        self.assertFalse(report["fresh_development_condition_opened"])
        self.assertFalse(report["selection_validation_reserve_access"])
        self.assertFalse(report["60_61_evidence_acceptance_input"])
        self.assertFalse(report["62_63_evidence_acceptance_input"])
        self.assertFalse(report["64_65_evidence_acceptance_input"])
        self.assertFalse(report["J1_J7_verdict_authorized"])
        self.assertTrue(report["new_live_protocol_proposal_authorized"])
        self.assertFalse(report["new_live_panel_execution_authorized"])
        self.assertFalse(report["stage2_authorized"])
        print("CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "geometry": report["geometry"],
        }, sort_keys=True))

    def test_import_is_inert_until_characterize(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_i_lifecycle_custody_stress_v2; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
