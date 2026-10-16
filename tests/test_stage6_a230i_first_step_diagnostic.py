"""A2.30-I first-edge diagnostics must not change Stage6 decisions.

These are software fixtures, not independent lived food transitions.
"""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_stage6_a230e_discriminants import (
    COLLECT, EAT, WAIT, SLEEP, planner, state,
)


def observably_diagnosed(model):
    model._config = replace(model._config, progressive_subgoals=True)
    return model


class FirstStepModelDiagnosticTests(unittest.TestCase):
    @staticmethod
    def target(s):
        return float(s.body["food"]) >= 50

    def test_all_root_candidates_unknown_diagnoses_only_a_model_gap(self):
        first = state(berries=1)
        # Unused table edge ensures no executable first action in the actual
        # initial state while still providing a well-formed Equipment corpus.
        training = state(food=35.0, berries=1)
        model = observably_diagnosed(planner(
            [(training, WAIT, training)], depth=2
        ))
        result = model.search(initial_state=first, target=self.target)
        self.assertEqual(result.status, "incomplete_model")
        self.assertEqual(result.commands, ())
        self.assertEqual(result.root_available_edges, 0)
        self.assertEqual(result.root_candidate_edges,
                         result.root_unavailable_edges)
        self.assertGreater(result.root_unavailable_edges, 0)
        self.assertEqual(model.last_search_diagnostic["root_model_diagnostic"],
                         "no_predictable_first_step")

    def test_known_root_but_unknown_later_is_not_first_step_gap(self):
        first = state(resource=True)
        after = state(berries=1)
        model = observably_diagnosed(planner(
            [(first, COLLECT, after)], depth=2
        ))
        result = model.search(initial_state=first, target=self.target)
        self.assertEqual(result.status, "incomplete_model")
        self.assertEqual(result.root_available_edges, 1)
        self.assertGreater(result.root_unavailable_edges, 0)
        self.assertEqual(model.last_search_diagnostic["root_model_diagnostic"],
                         "at_least_one_predictable_first_step")

    def test_complete_food_plan_never_becomes_root_failure(self):
        first = state(berries=1)
        after = state(food=55.0)
        model = observably_diagnosed(planner(
            [(first, EAT, after)], depth=1
        ))
        result = model.search(initial_state=first, target=self.target)
        self.assertEqual(result.status, "plan_found")
        self.assertEqual(result.commands, (EAT,))
        self.assertEqual(result.root_available_edges, 1)
        self.assertEqual(result.root_unavailable_edges, 0)
        # Other candidates were not simulated after early success. Do not
        # advertise a root-exhaustion certificate.
        self.assertGreater(result.root_candidate_edges,
                           result.root_available_edges)
        self.assertNotEqual(model.last_search_diagnostic["root_model_diagnostic"],
                            "no_predictable_first_step")

    def test_initially_satisfied_goal_has_no_attempted_first_step(self):
        first = state(food=80.0)
        model = observably_diagnosed(planner(
            [(first, WAIT, first)], depth=1
        ))
        result = model.search(initial_state=first, target=self.target)
        self.assertEqual(result.status, "plan_found")
        self.assertEqual(result.commands, ())
        self.assertEqual(result.root_candidate_edges, 0)
        self.assertEqual(result.root_available_edges, 0)
        self.assertEqual(result.root_unavailable_edges, 0)
        self.assertEqual(model.last_search_diagnostic["root_model_diagnostic"],
                         "not_classified")

    def test_partial_progress_does_not_confuse_inventory_with_goal_success(self):
        first = state(resource=True)
        after = state(berries=1)
        model = observably_diagnosed(planner(
            [(first, COLLECT, after)], depth=1
        ))
        result = model.search(
            initial_state=first, target=self.target, progress_measure="food"
        )
        self.assertEqual(result.status, "partial_progress")
        self.assertEqual(result.commands, (COLLECT,))
        self.assertEqual(result.root_available_edges, 1)
        self.assertFalse(
            model.last_search_diagnostic["root_model_diagnostic"]
            == "no_predictable_first_step"
        )

    def test_result_without_progressive_feature_preserves_public_status(self):
        first = state()
        training = state(food=80.0)
        model = planner([(training, WAIT, training)], depth=1)
        result = model.search(initial_state=first, target=self.target)
        self.assertEqual(result.status, "incomplete_model")
        self.assertIsNone(model.last_search_diagnostic)
        self.assertEqual(result.unavailable_edges,
                         result.root_unavailable_edges)


if __name__ == "__main__":
    unittest.main()
