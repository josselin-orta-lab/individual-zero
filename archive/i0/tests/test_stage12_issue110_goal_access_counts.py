"""Software-only validation of passive goal-access accounting.

Synthetic receipts validate the reporter, never I0 autonomous behavior.
"""
from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_goal_access_ablation import summarize_canonical_receipts


def sample(events):
    return b"\n".join(json.dumps({"causal_event": event},
                                  sort_keys=True).encode("utf-8")
                      for event in events)


class GoalAccessCounterTests(unittest.TestCase):
    def test_valid_history_separates_goal_motive_from_exploration(self):
        raw = sample([
            {"kind": "active_goal_changed"},
            {"kind": "stage6_planning_result", "data": {"proposal_ref": None}},
            {"kind": "stage6_planning_result", "data": {"proposal_ref": "option:goal"}},
            {"kind": "stage12_action_motive_attested", "data": {
                "motive_type": "cible_exploration",
                "goal_ref": None, "active_goal_ref": "goal:water",
            }},
            {"kind": "stage12_action_motive_attested", "data": {
                "motive_type": "active_goal",
                "goal_ref": "goal:water", "active_goal_ref": "goal:water",
            }},
            {"kind": "command_experienced", "primitive": "boire"},
            {"kind": "step_closed"},
        ])
        row = summarize_canonical_receipts(raw)
        self.assertEqual(row["planning_attempts"], 2)
        self.assertEqual(row["planning_proposals"], 1)
        self.assertEqual(row["goal_motive_commands"], 1)
        self.assertEqual(row["physical_steps"], 1)
        self.assertEqual(row["motive_types"]["cible_exploration"], 1)

    def test_missing_planning_provenance_refused(self):
        with self.assertRaisesRegex(ValueError, "missing Stage6"):
            summarize_canonical_receipts(sample([
                {"kind": "stage6_planning_result", "data": {}},
            ]))

    def test_closed_step_without_command_refused(self):
        with self.assertRaisesRegex(ValueError, "physical actions"):
            summarize_canonical_receipts(sample([
                {"kind": "step_closed"},
            ]))


if __name__ == "__main__":
    unittest.main()
