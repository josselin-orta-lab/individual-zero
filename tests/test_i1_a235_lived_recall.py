"""A2.35 provenance-only matcher, no cognitive activation."""
from dataclasses import dataclass
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "i1_overlays"))
from i1_lived_recall import matched_collection_recall


@dataclass(frozen=True)
class Episode:
    id: str
    end_t_monde: int
    event_refs: tuple[str, ...]


class LivedRecallUnitTests(unittest.TestCase):
    def setUp(self):
        self.command = {"event_id": "c1", "kind":"command_experienced",
                        "t_monde": 2, "primitive":"collecter",
                        "parameters":{"target":"berry_b"}}
        self.effect = {"event_id":"o1", "kind":"world_transition_experienced",
                       "t_monde":2,"effects":{"collected":{"kind":"berry_b","quantity":1}}}
        self.episode = Episode("episode:0", 2, ("c1","o1"))

    def check(self, events=None, episodes=None, refs=("episode:0",), step=3):
        return matched_collection_recall(
            episodes=[self.episode] if episodes is None else episodes,
            autobiography=[self.command,self.effect] if events is None else events,
            admitted_recall_refs=refs,t_monde=step)

    def test_real_success_with_matching_recall(self):
        self.assertEqual(self.check(), ("c1","o1"))

    def test_no_unrecalled_or_future_or_partial_sources(self):
        self.assertEqual(self.check(refs=()), ())
        self.assertEqual(self.check(step=2), ())
        self.assertEqual(self.check(episodes=[Episode("episode:0",2,("c1",))]), ())
        self.assertEqual(self.check(episodes=[Episode("episode:0",2,("o1",))]), ())
        self.assertEqual(self.check(events=[self.command]), ())
        self.assertEqual(self.check(events=[self.effect]), ())

    def test_failed_and_other_primitive_cannot_be_success(self):
        for effects in ({},{"collected":{"kind":"berry_b","quantity":0}},
                        {"scenario_forced_failure":"collecter"},
                        {"collected":{"kind":"berry_a","quantity":1}},
                        {"collected":{"kind":"berry_b","quantity":True}}):
            with self.subTest(effects=effects):
                self.assertEqual(self.check(events=[
                    self.command,{**self.effect,"effects":effects}]),())
        self.assertEqual(self.check(events=[
            {**self.command,"primitive":"manger"},self.effect]),())
        self.assertEqual(self.check(events=[
            {**self.command,"parameters":{"target":"berry_a"}},self.effect]),())

    def test_no_cross_time_matching(self):
        self.assertEqual(self.check(events=[
            self.command,{**self.effect,"t_monde":3}]),())

    def test_duplicate_sources_not_double_counted(self):
        self.assertEqual(self.check(episodes=[self.episode,self.episode]),("c1","o1"))


if __name__=="__main__":
    unittest.main()
