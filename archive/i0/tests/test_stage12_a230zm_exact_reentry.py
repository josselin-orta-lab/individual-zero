"""Negative controls for preregistered A2.30-ZM physical reentry experiment.

The original 64 worlds and 260 physics steps are executed ONCE in the CI
experiment step. These tests ONLY read its outputs, never create worlds or I0.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zm_exact_reentry import (
    PATH,EAST,audit_read_only_output,digest,
    EXPECTED_TEST_WORLDS,EXPECTED_PHYSICAL_STEPS,
)


class FirstPersonExactStateReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=Path(os.environ["A230ZM_OUTPUT_DIR"])
        cls.original=json.loads((folder/"a230zm-physical-loop-worlds.json").read_text())
        cls.summary=json.loads((folder/"a230zm-summary.json").read_text())

    def score(self,worlds=None):
        return audit_read_only_output(
            deepcopy(self.original if worlds is None else worlds)
        )

    def test_preregistered_every_physical_world_and_stage6_search(self):
        x=self.score()
        self.assertEqual(x["independent_detached_WorldBody_worlds"],64)
        self.assertEqual(x["real_physically_applied_closed_loop_steps"],256)
        self.assertEqual(x["real_fifth_control_physical_steps"],4)
        self.assertEqual(x["real_physical_steps_total"],260)
        self.assertEqual(x["actual_stage6_shadow_searches"],64)
        self.assertEqual(x["spatially_returned_to_initial_cell"],64)
        self.assertEqual(x["exact_firstperson_state_reentered"],4)
        self.assertEqual(x["same_location_but_changed_full_state"],60)
        self.assertEqual(x["first_move_exact_key_known_at_return"],4)
        self.assertEqual(x["stage6_one_step_spatial_plans_found"],4)
        self.assertEqual(x["stage6_incomplete_model"],60)
        self.assertEqual(x["physically_revalidated_predictions"],4)
        self.assertFalse(x["real_I0_UC_measured"])
        self.assertFalse(x["firstperson_safe_motor_generalization_proven"])
        self.assertEqual(x["new_I0_births"],0)
        self.assertEqual(x["new_I0_autonomous_steps"],0)

    def test_all_sixty_four_factorial_cells_and_expected_mechanisms(self):
        self.assertEqual(len(self.original),EXPECTED_TEST_WORLDS)
        seen=set()
        counts=Counter()
        for w in self.original:
            key=(tuple(w["factor_position"]),
                 w["factor_berry_B_local_visible"],
                 w["factor_movement_energy_cost"],
                 w["factor_food_decay"],
                 w["factor_water_decay"],
                 w["factor_night_start"])
            self.assertNotIn(key,seen)
            seen.add(key)
            counts["full_identical"]+=w["full_firstperson_state_reentered"]
            counts["night_shift"]+=w["factor_night_start"]==3
            counts["energy_costly"]+=w["factor_movement_energy_cost"]>0
            counts["food_decay"]+=w["factor_food_decay"]>0
            counts["water_decay"]+=w["factor_water_decay"]>0
        self.assertEqual(len(seen),64)
        self.assertEqual(counts["full_identical"],4)
        for k in ("night_shift","energy_costly","food_decay","water_decay"):
            self.assertEqual(counts[k],32)

    def test_positive_real_fifth_move_matches_exact_model_prediction(self):
        positives=[
            x for x in self.original if x["full_firstperson_state_reentered"]
        ]
        self.assertEqual(len(positives),4)
        for p in positives:
            receipt=p["precommitted_fifth_positive_physical_control"]
            self.assertIsNotNone(receipt)
            self.assertEqual(receipt["physical_example"]["command"],EAST.as_dict())
            self.assertEqual(receipt["physical_example"]["state"],p["returned_firstperson"])
            self.assertEqual(
                receipt["physical_example"]["observed_next_state"],
                p["planner_stage6_shadow"]["predictions"][0]["next_state"]
            )
            self.assertTrue(receipt["exact_prediction_equals_fifth_physical_outcome"])
            self.assertTrue(receipt["not_trained_on_fifth_action_before_prediction"])

    def test_spatial_revisit_is_not_a_full_state_revisit_when_body_or_night_changes(self):
        for p in self.original:
            self.assertEqual(
                (p["initial_firstperson"]["x"],p["initial_firstperson"]["y"]),
                (p["returned_firstperson"]["x"],p["returned_firstperson"]["y"])
            )
            self.assertEqual(
                p["first_move_exact_known_at_return"],
                p["initial_firstperson"]==p["returned_firstperson"],
            )
            if p["factor_movement_energy_cost"]>0:
                self.assertLess(
                    p["returned_firstperson"]["body"]["energy"],
                    p["initial_firstperson"]["body"]["energy"],
                )
            if p["factor_food_decay"]>0:
                self.assertLess(
                    p["returned_firstperson"]["body"]["food"],
                    p["initial_firstperson"]["body"]["food"],
                )
            if p["factor_water_decay"]>0:
                self.assertLess(
                    p["returned_firstperson"]["body"]["water"],
                    p["initial_firstperson"]["body"]["water"],
                )
            if p["factor_night_start"]==3:
                self.assertFalse(p["initial_firstperson"]["is_night"])
                self.assertTrue(p["returned_firstperson"]["is_night"])

    def test_no_berry_ingestion_even_in_layout_with_visible_B(self):
        for p in self.original:
            self.assertTrue(p["no_berry_B_ingestion"])
            self.assertFalse(p["model_certifies_safety"])
            self.assertEqual(p["actual_i0_births"],0)
            self.assertEqual(p["actual_i0_autonomous_steps"],0)
            self.assertFalse(p["real_i0_UC_cost_measured"])
            for rec in p["all_four_physical_movements"]:
                self.assertEqual(rec["physical_example"]["command"]["primitive"],
                                 "se_deplacer")
                self.assertFalse(rec["terminal"])
            self.assertTrue(p["planner_stage6_shadow"]["not_a_food_goal"])
            self.assertTrue(p["planner_stage6_shadow"]["no_shadow_action_dispatched"])

    def test_fake_spatial_only_equivalence_refused(self):
        x=deepcopy(self.original)
        target=next(p for p in x if p["factor_movement_energy_cost"]>0)
        target["full_firstperson_state_reentered"]=True
        with self.assertRaisesRegex(ValueError,"fabricated known state|reentry"):
            self.score(x)

    def test_forged_day_night_ignorance_refused(self):
        x=deepcopy(self.original)
        target=next(p for p in x if p["factor_night_start"]==3)
        target["returned_firstperson"]["is_night"]=False
        with self.assertRaisesRegex(ValueError,"perceptual/physical reentry"):
            self.score(x)

    def test_unlicensed_external_hidden_food_effect_refused(self):
        x=deepcopy(self.original)
        x[0]["initial_firstperson"]["berry_b_toxin_external_only"]=-100
        with self.assertRaisesRegex(ValueError,"perceptual/physical reentry"):
            self.score(x)

    def test_tampered_provenance_receipt_sha_rejected(self):
        x=deepcopy(self.original)
        x[0]["all_four_physical_movements"][0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"motor causal/terminal receipt"):
            self.score(x)

    def test_example_from_another_world_rejected(self):
        x=deepcopy(self.original)
        x[0]["all_four_physical_movements"][0]["source_world"]=x[1]["world_id"]
        with self.assertRaisesRegex(ValueError,"motor causal/terminal receipt"):
            self.score(x)

    def test_accidentally_consumed_berry_b_cannot_pass(self):
        x=deepcopy(self.original)
        x[0]["no_berry_B_ingestion"]=False
        with self.assertRaisesRegex(ValueError,"fabricated known state"):
            self.score(x)

    def test_false_motor_death_or_postmortem_event_rejected(self):
        x=deepcopy(self.original)
        x[0]["all_four_physical_movements"][1]["terminal"]=True
        with self.assertRaisesRegex(ValueError,"motor causal/terminal receipt"):
            self.score(x)

    def test_tampered_world_number_or_duplicate_cell_rejected(self):
        x=deepcopy(self.original)
        x[1]["world_id"]=x[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"scientific source world identity"):
            self.score(x)

    def test_future_prediction_fabricated_from_missing_edge_rejected(self):
        x=deepcopy(self.original)
        target=next(p for p in x if not p["full_firstperson_state_reentered"])
        target["planner_stage6_shadow"]["status"]="plan_found"
        target["planner_stage6_shadow"]["root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"unseen firstperson full root"):
            self.score(x)

    def test_plan_dispatched_by_shadow_rejected(self):
        x=deepcopy(self.original)
        x[0]["planner_stage6_shadow"]["no_shadow_action_dispatched"]=False
        with self.assertRaisesRegex(ValueError,"shadow used future"):
            self.score(x)

    def test_i0_real_uc_forged_rejected(self):
        x=deepcopy(self.original)
        x[0]["real_i0_UC_cost_measured"]=True
        with self.assertRaisesRegex(ValueError,"fabricated known state"):
            self.score(x)

    def test_fake_fifth_move_not_in_precommitted_positive_cells_rejected(self):
        x=deepcopy(self.original)
        yes=next(p["precommitted_fifth_positive_physical_control"]
                 for p in x if p["full_firstperson_state_reentered"])
        target=next(p for p in x if not p["full_firstperson_state_reentered"])
        target["precommitted_fifth_positive_physical_control"]=deepcopy(yes)
        with self.assertRaisesRegex(ValueError,"fifth physical act selected"):
            self.score(x)

    def test_fifth_physical_prediction_difference_rejected(self):
        x=deepcopy(self.original)
        target=next(p for p in x if p["full_firstperson_state_reentered"])
        target["precommitted_fifth_positive_physical_control"][
            "predicted_next_state"]["body"]["food"]+=1.0
        with self.assertRaisesRegex(ValueError,"fifth physical move"):
            self.score(x)

    def test_invented_safe_motion_generalization_refused(self):
        x=deepcopy(self.original)
        x[0]["model_certifies_safety"]=True
        with self.assertRaisesRegex(ValueError,"fabricated known state"):
            self.score(x)

    def test_no_cognitive_life_or_oracle_is_imported_by_runner(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/run_stage12_issue110_b_a230zm_exact_reentry.py"
               ).read_text()
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("Oracle(",source)
        self.assertNotIn("from lab.oracle import",source)
        self.assertNotIn("model.install(",source)


if __name__=="__main__":
    unittest.main()
