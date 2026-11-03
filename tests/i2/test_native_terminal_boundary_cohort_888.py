"""Eight-tick terminal-boundary extension of the predeclared native 2x2 cohort.

The result is a bounded software comparison, not a survival-rate study.
All four individuals share the exact physical environment *within each
source world*, born temperament and reserves, with the innate reflex retained.
"""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body
from i2.runtime.native_paid_cycle import NativePaidI2, NativeRefusal, HORIZON


class NativeTerminalBoundaryCohort(unittest.TestCase):
    BODY = Body(80, 60, 3, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)
    SOURCE_WORLDS = (("empty", 0.0), ("restorative", 30.0))

    def test_8_tick_mortality_requires_actually_discovered_drunk_water(self):
        self.assertEqual(HORIZON, 8)
        with tempfile.TemporaryDirectory() as temp:
            observations = {}
            for name, water_gain in self.SOURCE_WORLDS:
                for learning in (False, True):
                    with self.subTest(source_world=name, learning=learning):
                        path = Path(temp) / (name + "-" + str(learning) + ".sqlite")
                        life = NativePaidI2.create(
                            path, body=self.BODY, temperament=self.TRAITS,
                            learning=learning, sleep_consolidation=False,
                            food_stock=0, water_stock=4, drink_water_gain=0.0,
                            discovered_water_gain=water_gain, uc=1000)
                        born = life.audit()
                        observations[(name, learning)] = {
                            "born": born,
                            "initial_capture": None,
                            "end": None,
                            "actions": (),
                            "discoveries": (),
                        }
                        for _ in range(HORIZON):
                            life.step()
                        final = life.audit()
                        with sqlite3.connect(path) as db:
                            events = [json.loads(row[0]) for row in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            actions = tuple(row[0] for row in db.execute(
                                "SELECT admitted_action FROM native_physical_events "
                                "ORDER BY seq"))
                            discoveries = tuple(tuple(row) for row in db.execute(
                                "SELECT seq,found FROM native_discoveries ORDER BY seq"))
                        observations[(name, learning)].update(
                            initial_capture=events[0]["claim"]["capture"],
                            end=final, actions=actions, discoveries=discoveries)
                        self.assertEqual(final["revision"], HORIZON)
                        self.assertLess(final["remaining_uc"], born["remaining_uc"])
                        self.assertGreaterEqual(final["remaining_uc"], 0)
                        self.assertEqual(final["m11_authenticated"], False)
                        self.assertEqual(final["engine_registered"], False)
                        self.assertEqual(born["body"], self.BODY.as_dict())
                        self.assertEqual(born["temperament"], self.TRAITS.as_dict())
                        self.assertLessEqual(actions.count("collecter"), 1)
                        self.assertLessEqual(actions.count("boire_decouverte"), 1)
                        for seq, event in enumerate(events, 1):
                            offered = event["claim"]["capture"]["accessible_semantics"]
                            if "boire_decouverte" in offered:
                                self.assertTrue(any(
                                    dseq < seq and found == 1
                                    for dseq, found in discoveries))
                        if final["terminal"]:
                            with self.assertRaises(NativeRefusal):
                                life.step()

            for world, _ in self.SOURCE_WORLDS:
                learned = observations[(world, True)]
                control = observations[(world, False)]
                self.assertEqual(
                    learned["initial_capture"]["accessible_semantics"],
                    control["initial_capture"]["accessible_semantics"])
                self.assertEqual(learned["born"]["body"], control["born"]["body"])
                self.assertEqual(
                    learned["born"]["temperament"], control["born"]["temperament"])
                self.assertIn("collecter", control["initial_capture"]["accessible_semantics"])
                self.assertNotIn(
                    "boire_decouverte", control["initial_capture"]["accessible_semantics"])
                self.assertEqual(control["discoveries"], ())
                self.assertNotIn("collecter", control["actions"])

            empty_learned = observations[("empty", True)]
            positive_learned = observations[("restorative", True)]
            empty_control = observations[("empty", False)]
            positive_control = observations[("restorative", False)]
            self.assertEqual(empty_learned["discoveries"], ((3, 0),))
            self.assertEqual(positive_learned["discoveries"], ((3, 1),))
            self.assertEqual(empty_learned["actions"][:3],
                             positive_learned["actions"][:3])
            self.assertNotIn("boire_decouverte", empty_learned["actions"])
            self.assertIn("boire_decouverte", positive_learned["actions"])
            self.assertEqual(empty_control["actions"], positive_control["actions"])
            self.assertEqual(
                empty_control["end"]["body"], positive_control["end"]["body"])

            # All lives have eight physical ticks. Only actually drunk,
            # admitted newly discovered water changes hydration at the
            # terminal boundary. Neither learning nor exploration creates
            # water if the physically hidden site is empty.
            for arm in (empty_learned, empty_control, positive_control):
                self.assertTrue(arm["end"]["terminal"])
                self.assertEqual(arm["end"]["body"]["water"], 0)
            self.assertFalse(positive_learned["end"]["terminal"])
            self.assertGreater(positive_learned["end"]["body"]["water"], 0)
            self.assertGreater(
                positive_learned["end"]["body"]["water"],
                positive_control["end"]["body"]["water"])
            self.assertEqual(empty_learned["end"]["body"]["water"],
                             empty_control["end"]["body"]["water"])


if __name__ == "__main__":
    unittest.main()
