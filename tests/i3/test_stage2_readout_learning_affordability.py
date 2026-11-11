"""Readout work can cost an individual's subsequent learning opportunity.

Strictly no new World or born organism. All cases are pure native-body
and native next-learning allowance calculations on synthetic bodies.
"""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_readout_learning_affordability as E
from i3.lab import stage2_action_phase_readout_budget as PHASE
from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost, transition)
from i3.modules.mind import Mind
from i3.modules.world import World


class ReadoutLearningAffordabilityTests(unittest.TestCase):
    def test_frozen_four_case_software_falsifier_never_creates_world(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World allowed")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("no life allowed")):
            result = E.audit()
        print("I3_READOUT_LEARNING_AFFORDABILITY_RESULT="+json.dumps(
            result, sort_keys=True))
        self.assertEqual(result["predeclared_cases"], 4)
        self.assertEqual(result["status"],
                         "SOFTWARE_PHASE_AFFORDABILITY_GATE_PASS")
        self.assertEqual(result["failed_declared_gates"], [])
        self.assertEqual(result["learning_lost_in_boundary_cases"], 2)
        self.assertEqual(result["worlds_opened"], 0)
        self.assertEqual(result["actually_lived_readout_debits"], 0)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        self.assertEqual(result["readout_predictions_executed"], 0)
        self.assertTrue(result["native_reference_next_learning_allocator_used"])

    def test_two_distinct_currencies_can_independently_block_learning(self):
        for name, body in E.CASES[:2]:
            with self.subTest(case=name):
                base = E.examine(body, extra_requested=False)
                readout = E.examine(body, extra_requested=True)
                self.assertEqual(base["optional_status"], "NOT_REQUESTED")
                self.assertEqual(readout["optional_status"], "MODEL_AUTHORIZED")
                self.assertTrue(base["next_base_learning_model_authorized"])
                self.assertFalse(readout["next_base_learning_model_authorized"])
                self.assertEqual(
                    readout["next_base_learning_work"],
                    {"cycles": 0, "simulated_steps": 0,
                     "memory_items": 0, "replays": 0})
                self.assertTrue(base["source_unchanged"])
                self.assertTrue(readout["source_unchanged"])
                self.assertEqual(base["chosen_action_unchanged"], "attendre")
                self.assertEqual(readout["chosen_action_unchanged"], "attendre")
                self.assertEqual(base["post_action_terminal"], [])
                self.assertEqual(readout["post_action_terminal"], [])
                self.assertGreater(readout["additional_modeled_energy"], 0)
                self.assertGreater(readout["additional_modeled_vigilance"], 0)
                self.assertIsNone(
                    readout["next_learning_pure_projected_body"])
                self.assertIsNotNone(
                    base["next_learning_pure_projected_body"])

    def test_fully_fundable_branch_pays_only_model_ticket(self):
        before = dict(E.CASES)["both_funded"]
        base = E.examine(before, extra_requested=False)
        more = E.examine(before, extra_requested=True)
        self.assertTrue(base["next_base_learning_model_authorized"])
        self.assertTrue(more["next_base_learning_model_authorized"])
        self.assertEqual(more["next_sleep_replays_reserved"], 0)
        ticket = PHASE.proposed_readout_work(0)
        self.assertEqual(ticket, CognitiveWork(cycles=6, memory_items=48))
        e, v = cognitive_cost(BodyLaws(), ticket)
        self.assertAlmostEqual(more["additional_modeled_energy"], e)
        self.assertAlmostEqual(more["additional_modeled_vigilance"], v)
        self.assertEqual(more["optional_ticket"], {
            "cycles": 6, "memory_items": 48, "replays": 0,
            "simulated_steps": 0})
        self.assertEqual(more["cumulative_decision_work"], {
            "cycles": 9, "memory_items": 60, "replays": 0,
            "simulated_steps": 0})
        self.assertGreater(base["post_action_body"][0],
                           more["post_action_body"][0])
        self.assertGreater(base["post_action_body"][4],
                           more["post_action_body"][4])
        self.assertEqual(base["post_action_body"][1:4],
                         more["post_action_body"][1:4])

    def test_unaffordable_readout_keeps_action_and_learning_without_phantom_bill(self):
        before = dict(E.CASES)["optional_denied"]
        base = E.examine(before, extra_requested=False)
        denied = E.examine(before, extra_requested=True)
        self.assertTrue(base["next_base_learning_model_authorized"])
        self.assertTrue(denied["next_base_learning_model_authorized"])
        self.assertEqual(denied["optional_status"], "NO_FUNDED_READOUT")
        self.assertEqual(base["post_action_body"], denied["post_action_body"])
        self.assertEqual(base["cumulative_decision_work"],
                         denied["cumulative_decision_work"])
        self.assertEqual(denied["additional_modeled_energy"], 0)
        self.assertEqual(denied["additional_modeled_vigilance"], 0)
        self.assertTrue(denied["source_unchanged"])
        self.assertFalse(denied["world_cognitive_debit_attested"])

    def test_phase_learning_uses_real_preparation_method_not_fake_price(self):
        before = dict(E.CASES)["both_funded"]
        original = Mind.prepare_learning
        observed = []
        def spy(mind, result, budget):
            observed.append((budget.body, result["body"], result["dead"]))
            return original(mind, result, budget)
        with patch.object(Mind, "prepare_learning", spy):
            E.examine(before, extra_requested=False)
            E.examine(before, extra_requested=True)
        self.assertEqual(len(observed), 2)
        for body, actual, dead in observed:
            self.assertEqual(body, tuple(actual))
            self.assertEqual(dead, ())

    def test_optional_work_denied_before_any_lookups_or_mind_training(self):
        body = dict(E.CASES)["optional_denied"]
        with patch.object(Mind, "learn_from_outcome",
                          side_effect=AssertionError("no learning allowed")), patch(
                              PHASE, "passive_readouts",
                              side_effect=AssertionError("no prediction allowed")):
            E.examine(body, extra_requested=True)
        with self.assertRaises(TypeError):
            E.examine(body, extra_requested=1)
        with self.assertRaises(ValueError):
            E.examine((float("nan"),60.,60.,90.,80.),
                      extra_requested=False)

    def test_stated_native_debit_and_body_transition_are_exact(self):
        original = dict(E.CASES)["energy_boundary"]
        base = E.examine(original, extra_requested=False)
        after, dead = transition(original, E.ACTION, BodyLaws(),
                                 E.DECISION)
        self.assertEqual(base["post_action_body"], list(after))
        self.assertEqual(base["post_action_terminal"], list(dead))
        second = E.examine(original, extra_requested=True)
        w = CognitiveWork(cycles=9, memory_items=60)
        after, dead = transition(original, E.ACTION, BodyLaws(), w)
        self.assertEqual(second["post_action_body"], list(after))
        self.assertEqual(second["post_action_terminal"], list(dead))


if __name__ == "__main__":
    unittest.main()
