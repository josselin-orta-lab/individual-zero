"""Predeclared native I2 water-boundary sensitivity, not a survival study.

Probe the brittleness of an 8-tick terminal result to three birth water
levels.  The hidden world condition must never leak into decision-making.
"""
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import NativePaidI2, NativeRefusal, HORIZON


class NativeWaterBoundarySensitivity(unittest.TestCase):
    WATERS = (2.4, 3.0, 4.0)
    WORLD_GAINS = (0.0, 30.0)
    TEMPERAMENT = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def test_water_boundary_without_future_evidence_leakage(self):
        with TemporaryDirectory() as temp:
            outcomes = {}
            for initial_water in self.WATERS:
                for learning in (False, True):
                    for gain in self.WORLD_GAINS:
                        with self.subTest(
                            water=initial_water, learning=learning, source_gain=gain
                        ):
                            path = Path(temp) / (
                                f"water-{initial_water}-learning-{learning}-source-{gain}.db")
                            actor = NativePaidI2.create(
                                path, body=Body(80, 60, initial_water, 100),
                                temperament=self.TEMPERAMENT,
                                learning=learning, sleep_consolidation=False,
                                food_stock=0, water_stock=4, drink_water_gain=0.0,
                                discovered_water_gain=gain, uc=1000)
                            birth = actor.audit()
                            self.assertEqual(
                                birth["body"]["water"], initial_water)
                            for tick in range(HORIZON):
                                if actor.audit()["terminal"]:
                                    break
                                actor.step()
                            final = actor.audit()
                            self.assertTrue(
                                final["terminal"] or final["revision"] == HORIZON)
                            self.assertLess(final["remaining_uc"], 1000)
                            self.assertEqual(final["m11_authenticated"], False)
                            self.assertEqual(final["engine_registered"], False)
                            self.assertEqual(final["temperament"],
                                             self.TEMPERAMENT.as_dict())
                            with sqlite3.connect(path) as db:
                                events = [json.loads(row[0]) for row in db.execute(
                                    "SELECT event_json FROM events ORDER BY seq")]
                                bodies = [tuple(row) for row in db.execute(
                                    "SELECT admitted_action,before_json,after_json "
                                    "FROM native_physical_events ORDER BY seq")]
                                discoveries = [tuple(row) for row in db.execute(
                                    "SELECT seq,found FROM native_discoveries ORDER BY seq")]
                            self.assertEqual(len(bodies), final["revision"])
                            self.assertEqual(len(events), final["revision"])
                            self.assertEqual(
                                NativePaidI2.inspect(path).audit(), final)
                            if final["terminal"]:
                                with self.assertRaises(NativeRefusal):
                                    actor.step()
                            self.assertIn(
                                "collecter",
                                events[0]["claim"]["capture"]["accessible_semantics"])
                            self.assertNotIn(
                                "boire_decouverte",
                                events[0]["claim"]["capture"]["accessible_semantics"])
                            self.assertLessEqual(
                                sum(action == "collecter" for action, *_ in bodies), 1)
                            discovered = tuple(seq for seq, found in discoveries
                                               if found == 1)
                            consumed = [
                                (seq, before, after)
                                for seq, (action, before, after) in enumerate(bodies, 1)
                                if action == "boire_decouverte"]
                            self.assertLessEqual(len(consumed), 1)
                            for seq, before, after in consumed:
                                self.assertTrue(any(d < seq for d in discovered))
                                self.assertGreater(json.loads(after)["water"],
                                                   json.loads(before)["water"])
                            for seq, event in enumerate(events, 1):
                                claim = event["claim"]
                                available = claim["capture"]["accessible_semantics"]
                                if "boire_decouverte" in available:
                                    self.assertTrue(any(d < seq for d in discovered))
                                for d in discovered:
                                    if d >= seq:
                                        self.assertNotIn(
                                            "evidence:i2:native:water-found:" + str(d),
                                            claim["subjective_evidence_refs"])
                                if not learning:
                                    self.assertEqual(
                                        claim["capture"]["goal_ref"],
                                        "goal:physical-needs")
                            if gain == 0.0:
                                self.assertFalse(discovered)
                                self.assertFalse(consumed)
                            # No food or integrity sink can independently
                            # kill these fixed mild worlds by tick 8.
                            self.assertEqual(
                                final["terminal"],
                                final["body"]["water"] == 0)
                            expected_water = max(
                                0.0,
                                initial_water - 0.4 * final["revision"] +
                                gain * len(consumed))
                            self.assertAlmostEqual(
                                final["body"]["water"], expected_water,
                                delta=0.000001)
                            outcomes[(initial_water, learning, gain)] = {
                                "first": events[0]["claim"]["capture"],
                                "actions": tuple(action for action, *_ in bodies),
                                "final": final,
                                "discovered": discovered,
                                "drunk": len(consumed),
                            }
                    empty = outcomes[(initial_water, learning, 0.0)]
                    positive = outcomes[(initial_water, learning, 30.0)]
                    # The same individual type cannot know which hidden
                    # world it inhabits at its very first observation.
                    self.assertEqual(
                        empty["first"]["accessible_semantics"],
                        positive["first"]["accessible_semantics"])
                    self.assertEqual(
                        empty["first"]["goal_ref"], positive["first"]["goal_ref"])
                    if not positive["drunk"]:
                        self.assertEqual(
                            positive["final"]["body"]["water"],
                            empty["final"]["body"]["water"])
                    if initial_water == 4.0:
                        self.assertFalse(empty["final"]["terminal"])
                    if initial_water == 2.4:
                        self.assertTrue(empty["final"]["terminal"])
                        self.assertLessEqual(empty["final"]["revision"], 7)

    # A water-dependent terminal contrast must not be elevated to
    # general learning or survival claims: it may disappear if the
    # initial water reserve is high enough to cross all eight ticks.


if __name__ == "__main__":
    unittest.main()
