"""Adversarial safeguards for A2.30-G offline model-graph witnessing."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_stage12_issue110_b_a230g_graph_witness import (
    independent_known_graph_witness,
)

ROOT = "a" * 64
CHILD = "b" * 64
WAIT = {"primitive": "attendre", "parameters": {}}
SLEEP = {"primitive": "dormir", "parameters": {}}


def node(sha, depth, commands):
    return {
        "state_sha256": sha, "depth": depth,
        "candidate_commands": commands,
    }


def edge(parent, depth, command, successor=None):
    return {
        "state_sha256": parent,
        "parent_depth": depth,
        "command": command,
        "complete": successor is not None,
        "next_state_sha256": successor,
        "reason": None if successor is not None else "equipment_input_unseen",
    }


def search(status, candidates, edges, depth=3, commands=()):
    return {
        "status": status,
        "depth_limit": depth,
        "initial_state_sha256": ROOT,
        "candidate_states": candidates,
        "expanded_states": len(candidates),
        "edges": edges,
        "unavailable_edges": sum(not e["complete"] for e in edges),
        "commands": list(commands),
    }


class OfflineGraphWitnessTests(unittest.TestCase):
    def test_zero_known_first_step_certifies_a_model_frontier_not_world_impossibility(self):
        row = independent_known_graph_witness(search(
            "incomplete_model",
            [node(ROOT, 0, [WAIT, SLEEP])],
            [edge(ROOT, 0, WAIT), edge(ROOT, 0, SLEEP)],
        ))
        self.assertTrue(row["zero_known_first_step"])
        self.assertEqual(row["root_unknown_edges"], 2)
        self.assertFalse(row["fully_closed_finite_known_graph"])
        self.assertFalse(row["real_world_impossibility_proven"])

    def test_known_first_step_then_unknown_deeper_is_not_root_block(self):
        row = independent_known_graph_witness(search(
            "incomplete_model",
            [node(ROOT, 0, [WAIT]), node(CHILD, 1, [SLEEP])],
            [edge(ROOT, 0, WAIT, CHILD), edge(CHILD, 1, SLEEP)],
        ))
        self.assertFalse(row["zero_known_first_step"])
        self.assertTrue(row["some_known_first_step"])
        self.assertEqual(row["first_unknown_parent_depth"], 1)

    def test_closed_finite_known_graph_is_only_a_model_level_certificate(self):
        row = independent_known_graph_witness(search(
            "not_found_within_horizon",
            [node(ROOT, 0, [WAIT])],
            [edge(ROOT, 0, WAIT, ROOT)],
        ))
        self.assertTrue(row["fully_closed_finite_known_graph"])
        self.assertFalse(row["goal_predicate_independently_checked"])
        self.assertFalse(row["real_world_impossibility_proven"])

    def test_independent_bfs_rejects_silent_pruning(self):
        example = search(
            "incomplete_model",
            [node(ROOT, 0, [WAIT, SLEEP])],
            [edge(ROOT, 0, WAIT, CHILD), edge(ROOT, 0, SLEEP)],
        )
        with self.assertRaisesRegex(ValueError, "independent BFS"):
            independent_known_graph_witness(example)

    def test_known_goal_path_may_censor_later_candidate_actions(self):
        row = independent_known_graph_witness(search(
            "plan_found",
            [node(ROOT, 0, [WAIT, SLEEP])],
            [edge(ROOT, 0, WAIT, CHILD)],
            commands=(WAIT,),
        ))
        self.assertEqual(row["model_known_edges"], 1)
        self.assertFalse(row["fully_closed_finite_known_graph"])

    def test_unknown_edge_must_not_claim_a_successor(self):
        unknown = edge(ROOT, 0, WAIT)
        unknown["next_state_sha256"] = CHILD
        with self.assertRaisesRegex(ValueError, "invented"):
            independent_known_graph_witness(search(
                "incomplete_model", [node(ROOT, 0, [WAIT])], [unknown]
            ))

    def test_returned_path_must_be_supported_by_actual_known_edge(self):
        with self.assertRaisesRegex(ValueError, "unknown edge"):
            independent_known_graph_witness(search(
                "plan_found",
                [node(ROOT, 0, [WAIT])],
                [edge(ROOT, 0, WAIT)],
                commands=(WAIT,),
            ))


if __name__ == "__main__":
    unittest.main()
