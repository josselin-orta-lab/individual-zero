"""Adversarial comparisons for the A2.30-K immutable archive reviewer."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_stage12_issue110_b_a230k_impact import (
    compare_by_step, passive_projections,
)


class ArchiveImpactControls(unittest.TestCase):
    def test_detects_first_true_world_step_not_sequence_index(self):
        a = {3: ["eat"], 7: ["move"]}
        b = {3: ["eat"], 7: ["sleep"]}
        self.assertEqual(compare_by_step(a, b), 7)

    def test_detects_extra_attempt(self):
        self.assertEqual(compare_by_step({4: ["collect"]}, {}), 4)

    def test_identical_traces_do_not_claim_a_difference(self):
        original = {1: ["eat"], 5: ["move"]}
        self.assertIsNone(compare_by_step(original, dict(original)))

    def test_ignores_identity_refs_but_preserves_prediction_mismatch(self):
        old = [{
            "kind": "stage6_planning_result",
            "t_monde": 2,
            "data": {
                "goal_ref": "birthA:goal",
                "proposal_ref": None,
                "progressive_search_diagnostic": {
                    "status": "incomplete_model",
                    "expanded_states": 1,
                    "unavailable_edges": 5,
                    "root_candidate_edges": 5,
                    "root_available_edges": 0,
                    "root_unavailable_edges": 5,
                    "root_model_diagnostic": "no_predictable_first_step",
                },
            },
        }]
        other = [{
            **old[0], "data": {
                **old[0]["data"], "goal_ref": "birthB:goal",
            },
        }]
        self.assertEqual(
            passive_projections(old)["planning"],
            passive_projections(other)["planning"],
        )
        other[0]["data"]["progressive_search_diagnostic"] = {
            **other[0]["data"]["progressive_search_diagnostic"],
            "root_available_edges": 1,
        }
        self.assertEqual(compare_by_step(
            passive_projections(old)["planning"],
            passive_projections(other)["planning"],
        ), 2)


if __name__ == "__main__":
    unittest.main()
