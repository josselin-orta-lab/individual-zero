"""Pure sleep food-transfer mechanism, not an experiment on born I3."""
import json
import unittest
from math import isclose
from unittest.mock import patch

from i3.lab import stage2_sleep_cognition_metabolic_transfer as E
from i3.lab import stage2_action_phase_readout_budget as PHASE
from i3.modules.body import BodyLaws, CognitiveWork, transition
from i3.modules.mind import Mind
from i3.modules.world import World


class SleepCognitionMetabolicTransferTests(unittest.TestCase):
    def test_frozen_six_cells_original_physics_no_world(self):
        with patch.object(World,"__init__",
                          side_effect=AssertionError("no World permitted")), patch(
                          "i3.runtime.life.run_life",
                          side_effect=AssertionError("no life permitted")), patch.object(
                          Mind,"decide",
                          side_effect=AssertionError("no policy permitted")):
            result=E.audit()
        print("I3_SLEEP_COGNITION_FOOD_TRANSFER_RESULT="+json.dumps(
            result,sort_keys=True))
        self.assertEqual(result["status"],"SOFTWARE_METABOLIC_TRANSFER_GATE_PASS")
        self.assertEqual(result["fixed_synthetic_cases"],6)
        self.assertEqual(result["failed_predeclared_cells"],[])
        self.assertTrue(result["saturated_sleep_hides_energy_vigilance_bill_not_food"])
        self.assertTrue(result["native_model_terminal_only_after_optional_cognition"])
        self.assertEqual(result["worlds_opened"],0)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["actually_lived_extra_readout_debits"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        self.assertFalse(result["cpu_to_body_calibrated"])

    def test_saturated_sleep_hides_energy_vigilance_but_food_costs_differ(self):
        before=dict((x,(b,a)) for x,b,a in E.CASES)["sleep_saturated"]
        plain=E.examine(before,action="dormir",request_readout=False)
        extra=E.examine(before,action="dormir",request_readout=True)
        self.assertEqual(plain["post_action_body"][0],100.)
        self.assertEqual(extra["post_action_body"][0],100.)
        self.assertEqual(plain["post_action_body"][4],100.)
        self.assertEqual(extra["post_action_body"][4],100.)
        self.assertLess(extra["post_action_body"][1],plain["post_action_body"][1])
        self.assertGreater(extra["modeled_food_converted_to_energy"],
                           plain["modeled_food_converted_to_energy"])
        self.assertAlmostEqual(extra["additional_native_model_energy"],.1296)
        self.assertAlmostEqual(extra["additional_native_model_vigilance"],.30)
        self.assertEqual(extra["native_terminal_reasons"],[])
        self.assertFalse(extra["actual_world_debit_attested"])

    def test_native_vital_food_terminal_never_imputed(self):
        by={name:(body,action) for name,body,action in E.CASES}
        before,act=by["sleep_food_critical"]
        plain=E.examine(before,action=act,request_readout=False)
        extra=E.examine(before,action=act,request_readout=True)
        self.assertEqual(plain["native_terminal_reasons"],[])
        self.assertGreater(plain["post_action_body"][1],0)
        self.assertEqual(extra["native_terminal_reasons"],["zero_food"])
        self.assertEqual(extra["post_action_body"][1],0.)
        # The same need and motor existed in both arms; these are native laws.
        self.assertEqual(extra["selected_action"],plain["selected_action"])
        self.assertEqual(extra["original_decision_work"],
                         plain["original_decision_work"])
        self.assertGreater(extra["modeled_food_spent_on_repair"],0)
        self.assertLess(extra["modeled_food_spent_on_repair"],
                        plain["modeled_food_spent_on_repair"])

    def test_critical_near_miss_and_unsaturated_controls(self):
        by={name:(body,action) for name,body,action in E.CASES}
        before,act=by["sleep_food_control"]
        plain=E.examine(before,action=act,request_readout=False)
        extra=E.examine(before,action=act,request_readout=True)
        self.assertEqual(plain["native_terminal_reasons"],[])
        self.assertEqual(extra["native_terminal_reasons"],[])
        self.assertLess(extra["post_action_body"][1],plain["post_action_body"][1])
        before,act=by["sleep_unsaturated"]
        plain=E.examine(before,action=act,request_readout=False)
        extra=E.examine(before,action=act,request_readout=True)
        self.assertLess(extra["post_action_body"][0],plain["post_action_body"][0])
        self.assertLess(extra["post_action_body"][4],plain["post_action_body"][4])
        self.assertTrue(isclose(extra["post_action_body"][1],
                                plain["post_action_body"][1],abs_tol=1e-12))
        self.assertEqual(extra["native_terminal_reasons"],[])

    def test_non_sleep_motor_does_not_convert_food_and_rejection_is_atomic(self):
        by={name:(body,action) for name,body,action in E.CASES}
        before,act=by["wait_no_conversion"]
        plain=E.examine(before,action=act,request_readout=False)
        extra=E.examine(before,action=act,request_readout=True)
        self.assertEqual(plain["modeled_food_converted_to_energy"],0.)
        self.assertEqual(extra["modeled_food_converted_to_energy"],0.)
        self.assertTrue(isclose(plain["post_action_body"][1],
                                extra["post_action_body"][1],abs_tol=1e-12))
        before,act=by["sleep_readout_denied"]
        plain=E.examine(before,action=act,request_readout=False)
        denied=E.examine(before,action=act,request_readout=True)
        self.assertEqual(denied["status"],"NO_FUNDED_READOUT")
        self.assertEqual(plain["post_action_body"],denied["post_action_body"])
        self.assertEqual(denied["actual_model_work"],plain["actual_model_work"])
        self.assertEqual(denied["additional_native_model_energy"],0.)
        self.assertEqual(denied["additional_native_model_vigilance"],0.)

    def test_exact_reference_body_law_not_a_custom_transfer_formula(self):
        for _, body, action in E.CASES:
            for requested in (False,True):
                with self.subTest(action=action,body=body,requested=requested):
                    receipt=E.examine(body,action=action,
                                      request_readout=requested)
                    model=CognitiveWork(**receipt["actual_model_work"])
                    post,terminal=transition(body,action,BodyLaws(),model)
                    self.assertEqual(receipt["post_action_body"],list(post))
                    self.assertEqual(receipt["native_terminal_reasons"],list(terminal))
                    self.assertEqual(receipt["original_decision_work"],
                                     {"cycles":3,"memory_items":12,
                                      "replays":0,"simulated_steps":0})
        self.assertEqual(PHASE.proposed_readout_work(0),
                         CognitiveWork(cycles=6,memory_items=48))

    def test_invalid_source_or_forged_choice_fails_before_any_transition(self):
        body=E.CASES[0][1]
        for invalid in (None,0,"true"):
            with self.assertRaises(TypeError):
                E.examine(body,action="dormir",request_readout=invalid)
        with self.assertRaises(ValueError):
            E.examine(body,action="se_deplacer",request_readout=False)
        with self.assertRaises(ValueError):
            E.examine((float("nan"),60.,60.,90.,99.),
                      action="dormir",request_readout=False)
        with patch.object(E,"transition",
                          side_effect=AssertionError("no physical advance")):
            with self.assertRaises(ValueError):
                E.examine(body,action="invented_action",
                          request_readout=True)


if __name__=="__main__":
    unittest.main()
