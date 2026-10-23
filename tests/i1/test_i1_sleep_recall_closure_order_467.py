"""#467: exact journal-order proof for mid-step Memory episode closure."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_i1_world_preset import _closed_custody_at_sleep_recall


class SleepRecallClosureOrderTests(unittest.TestCase):
    def setUp(self):
        self.episode = {
            "id": "episode:4", "event_refs": ["lived:step3"],
            "start_t_monde": 3, "end_t_monde": 9,
        }
        self.closure = {
            "kind": "episode_closed", "t_monde": 9,
            "data": dict(self.episode),
        }
        self.recall = {"kind": "i1_sleep_site_recall_consulted",
                       "t_monde": 9}

    def verify(self, events, newly_closed=None):
        return _closed_custody_at_sleep_recall(
            preclosed_occurrences={"lived:old": 1},
            step_events=events, recall=self.recall,
            newly_closed=([self.episode] if newly_closed is None
                          else newly_closed),
            world_step=9,
        )

    def test_same_step_closure_before_read_is_authorized(self):
        counts, closures = self.verify([self.closure, self.recall])
        self.assertEqual(closures, 1)
        self.assertEqual(counts["lived:step3"], 1)
        self.assertEqual(counts["lived:old"], 1)

    def test_future_closure_does_not_authorize_recall(self):
        counts, closures = self.verify([self.recall, self.closure])
        self.assertEqual(closures, 0)
        self.assertNotIn("lived:step3", counts)

    def test_unauthenticated_or_duplicate_closures_fail(self):
        invalid = [
            [{"kind": "episode_closed", "t_monde": 8,
              "data": dict(self.episode)}, self.recall],
            [{"kind": "episode_closed", "t_monde": 9,
              "data": {**self.episode, "event_refs": ["invented"]}},
             self.recall],
            [self.closure, self.closure, self.recall],
        ]
        for events in invalid:
            with self.subTest(events=events), self.assertRaises(RuntimeError):
                self.verify(events)

    def test_open_episode_is_not_an_authorized_closure(self):
        with self.assertRaises(RuntimeError):
            self.verify([self.closure, self.recall], newly_closed=[])


if __name__ == "__main__":
    unittest.main()
