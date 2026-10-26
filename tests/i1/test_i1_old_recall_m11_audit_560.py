"""Synthetic operator traces for #560; NOT natural L2 positive evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from i1_old_recall_m11_audit import audit_old_recall_step


class OldRecallM11Audit560(unittest.TestCase):
    def setUp(self):
        self.episodes = [{"id": f"episode:{i}", "event_refs": (
            ["cmd:1", "transition:1"] if i == 0 else [f"cmd:{i+1}"]
        )} for i in range(34)]
        self.commits = {"cmd:1": 1, "transition:1": 1}
        self.proposal = {"kind": "memory_recall_proposed", "t_monde": 35,
                         "cycle": 1, "data": {"episode_ref": "episode:0"}}
        self.charge = {"kind": "compute_charge", "t_monde": 35,
                       "cycle": 1, "data": {
                           "module": "planning", "operation": "i1_bounded_old_episode_recall",
                           "requested_uc": 8, "accepted": True}}
        self.observed = {"kind": "i1_old_episode_paid_observation", "t_monde": 35,
                         "cycle": 1, "data": {
                             "episode_ref": "episode:0",
                             "source_event_refs": ["cmd:1", "transition:1"],
                             "charged_operation": "i1_bounded_old_episode_recall",
                             "charged_uc": 8, "witnesses": [],
                             "decision_evidence": False, "causal_attribution": False,
                             "q_or_p40_augmented": False, "motor_permission": False}}

    def audit(self, events, **override):
        return audit_old_recall_step(
            events=events, world_step=35, preclosed=self.episodes,
            newly_closed=[], previous_commits=override.get("commits", self.commits),
        )

    def test_positive_synthetic_only(self):
        out = self.audit([self.proposal, self.charge, self.observed])
        self.assertEqual(out["authentic_old_consultations"], 1)
        self.assertEqual(out["l2_positive"], "OBSERVED")
        self.assertEqual(out["l3_decision_influence"], "NOT_ESTABLISHED")

    def test_negative_natural_absence_is_not_failure(self):
        out = self.audit([])
        self.assertEqual(out["l2_positive"], "NOT_OBSERVED")
        self.assertEqual(out["accepted_old_read_charges"], 0)
        out = self.audit([self.proposal, self.charge])
        self.assertEqual(out["accepted_old_read_charges"], 1)
        self.assertEqual(out["authentic_old_consultations"], 0)

    def test_unpaid_stale_invalid_source_and_cross_cycle(self):
        from copy import deepcopy
        cases = [
            [self.proposal, self.observed],
            [self.charge, self.proposal, self.observed],
            [self.proposal, self.observed, self.charge],
        ]
        for events in cases:
            with self.subTest(events=events), self.assertRaises(ValueError):
                self.audit(events)
        bad = deepcopy(self.observed)
        bad["cycle"] = 2
        with self.assertRaises(ValueError):
            self.audit([self.proposal, self.charge, bad])
        bad = deepcopy(self.observed)
        bad["data"]["source_event_refs"] = ["cmd:1", "uncommitted"]
        with self.assertRaises(ValueError):
            self.audit([self.proposal, self.charge, bad])
        bad = deepcopy(self.observed)
        bad["data"]["motor_permission"] = True
        with self.assertRaises(ValueError):
            self.audit([self.proposal, self.charge, bad])
        with self.assertRaises(ValueError):
            self.audit([self.proposal, self.charge, self.observed],
                       commits={"cmd:1": 35, "transition:1": 35})

    def test_recent_episode_cannot_count_as_old(self):
        from copy import deepcopy
        p = deepcopy(self.proposal)
        o = deepcopy(self.observed)
        p["data"]["episode_ref"] = "episode:4"
        o["data"]["episode_ref"] = "episode:4"
        o["data"]["source_event_refs"] = ["cmd:5"]
        with self.assertRaises(ValueError):
            self.audit([p, self.charge, o])


if __name__ == "__main__":
    unittest.main()
