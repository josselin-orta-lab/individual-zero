"""Native individual distress-cost ledger ≠ causal value of information.

Only fixed synthetic software sources: NEVER a living forecast or a new World.
"""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_personal_computation_value_identifiability as E
from i3.lab import stage2_action_conditional_existing_effects as EFFECTS
from i3.modules.body import (
    BodyLaws, CognitiveWork, debit_cognition, transition)
from i3.modules.mind import Mind
from i3.modules.world import World


class PersonalComputationIdentifiabilityTests(unittest.TestCase):
    def test_full_frozen_256_grid_three_branches_never_opens_world(self):
        with patch.object(
            World, "__init__", side_effect=AssertionError("NO WORLD")), patch(
                "i3.runtime.life.run_life",
                side_effect=AssertionError("NO LIVING SOURCE")), patch.object(
                    Mind, "decide",
                    side_effect=AssertionError("NO MOTOR POLICY")), patch.object(
                        Mind, "learn_from_outcome",
                        side_effect=AssertionError("NO PAID LEARNING")):
            result = E.audit()
        print("I3_VOI_IDENTIFIABILITY_SOFTWARE_RESULT="+json.dumps(
            {k: v for k, v in result.items() if k != "rows"},
            sort_keys=True))
        self.assertEqual(
            result["status"],
            "FIXED_ACTION_PERSONAL_COST_ONLY_INFORMATION_UNIDENTIFIED")
        self.assertEqual(result["factorial_grid_size"], 256)
        self.assertEqual(len(result["rows"]), 256)
        self.assertEqual(len(result["exact_full_grid_sha256"]), 64)
        self.assertEqual(
            result["optional_funded_cells"]+result["optional_denied_cells"],256)
        self.assertEqual(
            sum(result["cost_only_intrinsic_signs_on_funded"].values()),
            result["optional_funded_cells"])
        self.assertTrue(result["all_paid_visible_discard_equivalent"])
        self.assertEqual(len(result["sampled_predeclared_receipts"]),8)
        self.assertIsNone(result["expected_information_benefit"])
        self.assertIsNone(result["realized_future_action_effect"])
        self.assertIsNone(result["net_value_of_computation"])
        self.assertEqual(result["worlds_opened"],0)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["actual_personal_outcomes_scored"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(result["cpu_to_body_calibrated"])
        self.assertFalse(result["stage2_2_go"])
        for row in result["rows"]:
            self.assertTrue(row["equal_cost_visible_discard_physical"])
            self.assertEqual(row["readouts_executed_in_each_paid_arm"],
                             3 if row["extra_admitted"] else 0)
            self.assertIn(row["chosen_action"],E.ACTIONS)

    def test_paid_visible_and_paid_discard_both_compute_but_do_not_control(self):
        for action in E.ACTIONS:
            before=(5.,60.,60.,90.,5.)
            with self.subTest(action=action):
                visible=E.project_model_arm(
                    before,action=action,food_weight=2.0,mode="paid_visible")
                discard=E.project_model_arm(
                    before,action=action,food_weight=2.0,mode="paid_discard")
                self.assertTrue(visible["optional_admitted"])
                self.assertTrue(E._same_paid_physical_receipt(visible,discard))
                self.assertEqual(visible["synthetic_readouts_actually_executed"],3)
                self.assertEqual(discard["synthetic_readouts_actually_executed"],3)
                self.assertTrue(visible["synthetic_readout_sha256"])
                self.assertEqual(visible["synthetic_readout_sha256"],
                                 discard["synthetic_readout_sha256"])
                self.assertEqual(
                    tuple(visible["laboratory_readouts_visible"]),
                    ("action","global","persistence"))
                self.assertIsNone(discard["laboratory_readouts_visible"])
                self.assertTrue(visible["external_forecast_never_controls_action"])
                self.assertIsNone(visible["realized_future_action_effect"])
                self.assertIsNone(visible["net_value_of_computation"])

    def test_synthetic_action_information_can_differ_without_motor_effect(self):
        before=(5.,60.,60.,90.,5.)
        forecasts={}
        for action in E.ACTIONS:
            v=E.project_model_arm(
                before,action=action,food_weight=2.0,mode="paid_visible")
            forecasts[action]=v["laboratory_readouts_visible"]
        self.assertNotEqual(
            forecasts["attendre"]["action"],forecasts["dormir"]["action"])
        self.assertEqual(
            forecasts["attendre"]["persistence"],
            forecasts["dormir"]["persistence"])
        self.assertEqual(
            forecasts["attendre"]["global"],
            forecasts["dormir"]["global"])
        # The two selected actions are separate fixed software cells, NOT
        # a causal choice or a preference chosen by any born individual.

    def test_phases_use_real_native_transition_and_original_learning_allocator(self):
        before=(5.,80.,60.,90.,5.)
        for action in E.ACTIONS:
            with self.subTest(action=action):
                receipt=E.project_model_arm(
                    before,action=action,food_weight=.2,mode="paid_visible")
                work=CognitiveWork(**receipt["total_declared_decision_work"])
                immediate,dead=transition(before,action,BodyLaws(),work)
                self.assertEqual(receipt["immediate_post_action_body"],immediate)
                self.assertEqual(receipt["native_terminal_reasons"],dead)
                self.assertEqual(receipt["next_learning_status"],
                                 "MODEL_FUNDED_LEARNING")
                learning=CognitiveWork(**receipt["next_learning_work"])
                post,acct=debit_cognition(immediate,BodyLaws(),learning)
                self.assertEqual(receipt["post_paid_learning_model_body"],post)
                self.assertTrue(all(a["unpaid"] == 0 for a in acct.values()))
                self.assertEqual(receipt["primary_target_phase"],
                                 "POST_PAID_LEARNING")
                self.assertEqual(receipt["secondary_target_phase"],
                                 "IMMEDIATE_POST_WORLD")
                self.assertTrue(receipt["source_mind_unchanged"])

    def test_denied_calculation_cannot_peek_or_change_action_body(self):
        before=(.45,60.,60.,90.,99.95)
        baseline=E.project_model_arm(
            before,action="attendre",food_weight=.2,mode="reference")
        with patch.object(
            E,"passive_readouts",
            side_effect=AssertionError("unfunded forecast must not run")):
            rejected=E.project_model_arm(
                before,action="attendre",food_weight=.2,mode="paid_visible")
        self.assertEqual(rejected["optional_status"],"NO_FUNDED_READOUT")
        self.assertFalse(rejected["optional_admitted"])
        self.assertEqual(rejected["synthetic_readouts_actually_executed"],0)
        self.assertIsNone(rejected["synthetic_readout_sha256"])
        self.assertEqual(rejected["total_declared_decision_work"],
                         baseline["total_declared_decision_work"])
        self.assertEqual(rejected["immediate_post_action_body"],
                         baseline["immediate_post_action_body"])
        self.assertEqual(rejected["post_paid_learning_model_body"],
                         baseline["post_paid_learning_model_body"])
        self.assertEqual(rejected["post_learning_intrinsic_target"],
                         baseline["post_learning_intrinsic_target"])

    def test_legal_personal_genetic_weights_change_value_not_physics(self):
        before=(99.95,.23,60.,90.,99.95)
        results={}
        for food_weight in E.PERSONAL_FOOD_WEIGHTS:
            results[food_weight]={
                mode:E.project_model_arm(
                    before,action="dormir",food_weight=food_weight,mode=mode)
                for mode in ("reference","paid_visible")
            }
        for mode in ("reference","paid_visible"):
            self.assertEqual(
                results[.2][mode]["immediate_post_action_body"],
                results[2.][mode]["immediate_post_action_body"])
            self.assertEqual(
                results[.2][mode]["post_paid_learning_model_body"],
                results[2.][mode]["post_paid_learning_model_body"])
            self.assertNotEqual(
                results[.2][mode]["post_learning_intrinsic_target"],
                results[2.][mode]["post_learning_intrinsic_target"])
        for food_weight in E.PERSONAL_FOOD_WEIGHTS:
            baseline=results[food_weight]["reference"]
            paid=results[food_weight]["paid_visible"]
            self.assertEqual(baseline["native_terminal_reasons"],())
            self.assertEqual(paid["native_terminal_reasons"],("zero_food",))
            source=E._source(before,"dormir",food_weight)
            self.assertEqual(
                paid["post_learning_intrinsic_target"],-source.d_max)
            self.assertEqual(paid["next_learning_status"],
                             "TERMINAL_NO_LEARNING")
            self.assertEqual(paid["next_learning_work"],{
                "cycles":0,"simulated_steps":0,"memory_items":0,"replays":0})

    def test_bad_source_and_unfunded_action_fail_without_forging_observation(self):
        before=(5.,60.,60.,90.,5.)
        for bad_mode in ("science","fund_for_free",None):
            with self.subTest(mode=bad_mode),self.assertRaises(ValueError):
                E.project_model_arm(
                    before,action="dormir",food_weight=.2,mode=bad_mode)
        for weight in (False,0.5,2,"2"):
            with self.subTest(weight=weight),self.assertRaises(ValueError):
                E.project_model_arm(
                    before,action="dormir",food_weight=weight,mode="reference")
        for action in ("boire",None,False):
            with self.subTest(action=action),self.assertRaises(ValueError):
                E.project_model_arm(
                    before,action=action,food_weight=.2,mode="reference")
        for body in (
            (float("nan"),60.,60.,90.,5.),
            (5.,60.,59.99,90.,5.),
            (5.,60.,60.,89.99,5.),
            (10.,60.,60.,90.,5.),
        ):
            with self.subTest(body=body),self.assertRaises(ValueError):
                E.project_model_arm(
                    body,action="attendre",food_weight=.2,mode="reference")


if __name__=="__main__":
    unittest.main()
