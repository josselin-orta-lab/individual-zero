"""Negative controls for sealed ZB real-I0 autonomously lived attrition audit."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zd_autonomous_funnel import (
    audit_export_bytes, by_step, candidate_root, classify_step,
    compare_original_python_versions, original_source, run,
    validate_core_results, _compare_except_f64,
)

EXPECTED_EXCLUSIVE = {
    "insufficient_same_step_planner_evidence":12,
    "goal_selected_with_precommit":20,
    "evaluated_not_crossed":32,
    "reduced_sleep":46,
    "no_planner_proposal":174,
    "no_attested_active_goal":96,
    "crossed_but_not_selected":4,
}


class OriginalAutonomousFoodFunnelAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left=Path(os.environ["A230ZD_ORIGINAL_311"])
        cls.right=Path(os.environ["A230ZD_ORIGINAL_312"])
        cls.temporary=tempfile.TemporaryDirectory(prefix="a230zd-test-")
        cls.result=run(cls.left,cls.right,Path(cls.temporary.name)/"audit")
        cls.a=original_source(cls.left,"3.11")
        cls.b=original_source(cls.right,"3.12")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_original_sha_wal_and_prereg_outputs(self):
        source=self.result["source_py311_metrics"]
        self.assertEqual(source["original_born_I0_lives"],12)
        self.assertEqual(source["original_autonomous_world_steps"],384)
        self.assertEqual(source["actual_stage6_searches"],196)
        self.assertEqual(source["actual_searches_no_predictable_root"],174)
        self.assertEqual(source["actual_root_available_edge_total"],18)
        self.assertEqual(source["verified_berry_b_motors"],0)
        self.assertEqual(source["verified_berry_b_eats"],0)
        self.assertEqual(self.result["new_I0_lives"],0)
        self.assertEqual(self.result["new_physical_world_steps"],0)
        self.assertEqual(self.result["Stage12"],"PARTIAL")
        self.assertEqual(source["exclusive_original_step_categories"],EXPECTED_EXCLUSIVE)

    def test_accessible_b_candidate_only_locally_and_eastern_physics(self):
        a=self.a["life_reports"]
        self.assertEqual(sum(x["first_person_root"][
            "candidate_collect_B_initial"] for x in a),4)
        self.assertEqual(sum(x["first_person_root"][
            "adjacent_east_B_accessible"] for x in a),4)
        for x in a:
            if x["layout"]=="B_LOCAL":
                self.assertTrue(x["first_person_root"]["candidate_collect_B_initial"])
            else:
                self.assertFalse(x["first_person_root"]["candidate_collect_B_initial"])
            self.assertFalse(x["first_person_root"]["candidate_eat_B_initial"])

    def test_proposed_food_is_not_attested_B_species(self):
        q=self.a["core"]
        self.assertGreater(sum(q["planner_proposal_refs_not_B_species_grounded"].values()),0)
        self.assertFalse(q["B_specific_planner_option_count_identifiable_from_receipts"])
        self.assertFalse(q["unique_cause_of_B_absence_established"])
        self.assertFalse(q["UC_refusal_causally_responsible_for_B_absence_established"])

    def test_real_uc_refusal_cannot_be_a_fabricated_explanation(self):
        self.assertEqual(self.a["core"]["real_UC_refused_operations"],{})
        self.assertTrue(all(not s["uc_refusal_operations"]
            for x in self.a["life_reports"] for s in x["steps"]))

    def test_cross_python_physical_motor_parity_but_float_drift(self):
        r=self.result["cross_python_integrity"]
        self.assertFalse(r["full_cross_python_cognitive_reproducibility"])
        self.assertTrue(r["physical_and_perceptual_events_bit_identical"])
        self.assertEqual(r["whole_journals_byte_identical_lives"],6)
        self.assertEqual(r["whole_journals_not_byte_identical_lives"],6)
        self.assertLessEqual(r["cognitive_float_max_absolute_difference"],1e-12)
        self.assertGreater(r["cognitive_float_max_absolute_difference"],0)
        self.assertTrue(all(
            "sustained" in x["birth_id"]
            for x in r["divergences"]
        ))
        self.assertEqual(
            compare_original_python_versions(self.a,self.b),r
        )

    def test_fake_berry_b_local_presence_rejected(self):
        baseline=next(row for row in self.a["summary"]["lives"]
                      if row["layout"]=="B_NONE")
        f=deepcopy(baseline["initial_accessible_projection"])
        f["current_resources"].append("berry_b")
        with self.assertRaisesRegex(ValueError,"placement"):
            candidate_root(f,"B_NONE")

    def test_hidden_toxicity_cannot_be_added_as_a_perception(self):
        f=deepcopy(self.a["summary"]["lives"][0][
            "initial_accessible_projection"])
        f["berry_b_safe"]=True
        with self.assertRaisesRegex(ValueError,"hidden"):
            candidate_root(f,"B_LOCAL")

    def test_forged_option_cross_without_evaluation_not_selected(self):
        life=next(x for x in self.a["life_reports"]
                  if x["exclusive_step_categories"].get(
                      "crossed_but_not_selected",0))
        step=next(row for row in life["steps"]
                  if row["category"]=="crossed_but_not_selected")
        label=(life["profile"]+"-"+life["layout"]+"-"+
               life["hidden_effect_for_external_pairing_only"])
        path=self.a["root"]/label/"canonical.jsonl"
        events=[json.loads(s)["causal_event"] for s in path.read_bytes().splitlines()]
        time=step["t_monde"]
        selected=[e for e in events if e.get("t_monde")==time]
        amended=deepcopy(selected)
        amended=[e for e in amended if e["kind"]!="competition_cycle"]
        audited=classify_step(amended,time)
        self.assertEqual(audited["category"],"insufficient_competition_evidence")

    def test_forged_canonical_motor_fails_hash_chain(self):
        row=self.a["summary"]["lives"][0]
        name=(row["profile"]+"-"+row["layout"]+"-"+
              row["hidden_B_external_only"])
        filename=self.a["root"]/name/"canonical.jsonl"
        canonical=filename.read_bytes()
        altered=canonical.replace(b'"primitive":"se_deplacer"',
                                   b'"primitive":"collecter"',1)
        self.assertNotEqual(altered,canonical)
        with self.assertRaises(ValueError):
            audit_export_bytes(
                altered,expected_head=row["journal_head"],
                expected_count=row["journal_count"],
            )

    def test_strange_extra_postterminal_or_world_steps_refused(self):
        synthetic=[
            {"kind":"perceptual_capture","t_monde":33,"data":{}}
        ]
        with self.assertRaisesRegex(ValueError,"out-of-horizon"):
            by_step(synthetic,32)

    def test_duplicate_hidden_pair_life_detected(self):
        fake=deepcopy(self.a["life_reports"])
        fake[1]["birth_id"]=fake[0]["birth_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            validate_core_results(fake)

    def test_only_canonical_floating_microdrift_may_differ(self):
        with self.assertRaisesRegex(ValueError,"not a canonical floating"):
            _compare_except_f64(
                {"primitive":"attendre"},{"primitive":"manger"}
            )
        with self.assertRaisesRegex(ValueError,"bound"):
            _compare_except_f64(
                {"value":{"$f64":"0x1.0p+0"}},
                {"value":{"$f64":"0x1.8p+0"}}
            )

    def test_no_original_birth_or_stage6_search_performed_by_auditor(self):
        script=(Path(__file__).resolve().parents[1]/
                "scripts/audit_stage12_issue110_b_a230zd_autonomous_funnel.py"
               ).read_text()
        self.assertNotIn("WorldBody(",script)
        self.assertNotIn("build_life(",script)
        self.assertNotIn("Stage12Runtime(",script)
        self.assertNotIn(".run_step(",script)
        self.assertNotIn("SimulatorPlanner.search(",script)
        self.assertNotIn("run_stage12_issue110_b_a230zb_autonomous_food import",script)
        self.assertNotIn("import Oracle",script)


if __name__=="__main__":
    unittest.main()
