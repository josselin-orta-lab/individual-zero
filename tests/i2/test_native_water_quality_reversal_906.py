"""Born-locked changes of physical water quality, never prospective rewards.

A physically accessible offer and its actual physiological value are
separate. I2 can learn quality only by really drinking and experiencing
the body's subsequent change. No forced motor tapes in cognitive tests.
"""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, actual_old_water_gain,
)


class NativeWaterQualityReversalTests(unittest.TestCase):
    BODY = Body(80, 80, 8, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def test_hidden_quality_changes_with_physical_time_not_learning_flag(self):
        world = {
            "drink_water_gain": 0.0, "water_quality_change_at": 3,
            "water_quality_after_gain": 20.0,
        }
        self.assertEqual(actual_old_water_gain(world, 0), 0.0)
        self.assertEqual(actual_old_water_gain(world, 1), 0.0)
        self.assertEqual(actual_old_water_gain(world, 2), 0.0)
        self.assertEqual(actual_old_water_gain(world, 3), 20.0)
        self.assertEqual(actual_old_water_gain(world, 64), 20.0)
        world["water_quality_change_at"] = 0
        self.assertEqual(actual_old_water_gain(world, 64), 0.0)

    def test_reversal_after_vetoed_ticks_never_grants_water_or_future_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            observations = []
            for learning in (False, True):
                path = Path(folder) / ("reversal-" + str(learning) + ".db")
                life = NativePaidI2.create(
                    path, body=self.BODY, temperament=self.TRAITS,
                    learning=learning, sleep_consolidation=False,
                    max_steps=8, uc=1000, food_stock=0, water_stock=1,
                    water_restock_every=2, drink_water_gain=0,
                    water_quality_change_at=3, water_quality_after_gain=20,
                    discovered_water_gain=0,
                )
                initial = life.audit()
                for tick in range(1, 4):
                    snap = life.step(veto=True)
                    self.assertEqual(snap["revision"], tick)
                    self.assertAlmostEqual(
                        snap["body"]["water"], self.BODY.water - 0.4 * tick)
                prior = life.audit()
                self.assertLess(prior["body"]["water"], self.BODY.water)
                after_choice = life.step()
                self.assertEqual(after_choice["revision"], 4)
                with sqlite3.connect(path) as db:
                    events = [json.loads(r[0]) for r in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                    actions = [tuple(r) for r in db.execute(
                        "SELECT admitted_action,before_json,after_json "
                        "FROM native_physical_events ORDER BY seq")]
                self.assertEqual(len(events), 4)
                self.assertEqual(len(actions), 4)
                self.assertEqual([r[0] for r in actions[:3]],
                                 ["NO_ACTION", "NO_ACTION", "NO_ACTION"])
                for ev in events:
                    self.assertFalse(any(
                        "water-quality" in ref
                        for ref in ev["claim"]["subjective_evidence_refs"]))
                self.assertAlmostEqual(
                    self.BODY.water - 0.4 * 3,
                    json.loads(actions[2][2])["water"])
                self.assertEqual(NativePaidI2.inspect(path).audit(), after_choice)
                self.assertEqual(initial["body"], self.BODY.as_dict())
                self.assertEqual(initial["temperament"], self.TRAITS.as_dict())
                if actions[3][0] == "boire":
                    self.assertAlmostEqual(
                        json.loads(actions[3][2])["water"] -
                        json.loads(actions[3][1])["water"], 19.6)
                else:
                    self.assertLessEqual(
                        json.loads(actions[3][2])["water"],
                        json.loads(actions[3][1])["water"])
                observations.append((
                    events[0]["claim"]["capture"]["accessible_semantics"],
                    events[3]["claim"]["capture"]["accessible_semantics"],
                    actions[3][0],
                ))
            self.assertEqual(observations[0][0], observations[1][0])
            self.assertEqual(observations[0][1], observations[1][1])

    def test_reversal_values_are_immutable_born_physics(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tamper.db"
            life = NativePaidI2.create(
                path, body=self.BODY, temperament=self.TRAITS,
                water_restock_every=2, water_quality_change_at=3,
                water_quality_after_gain=20)
            life.audit()
            with sqlite3.connect(path) as db:
                db.execute("UPDATE native_genesis SET water_quality_after_gain=50 "
                           "WHERE id=1")
            with self.assertRaises(NativeRefusal):
                life.audit()
            for invalid in (True, 1.1, -1, 129, "3"):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(folder) / ("bad-" + str(invalid) + ".db"),
                            body=self.BODY, temperament=self.TRAITS,
                            water_restock_every=2,
                            water_quality_change_at=invalid)
            for invalid in (True, -1, 101, "10"):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(folder) / ("bad-gain-" + str(invalid) + ".db"),
                            body=self.BODY, temperament=self.TRAITS,
                            water_restock_every=2,
                            water_quality_change_at=3,
                            water_quality_after_gain=invalid)
            with self.assertRaises(NativeRefusal):
                NativePaidI2.create(
                    Path(folder) / "no-renewal.db",
                    body=self.BODY, temperament=self.TRAITS,
                    water_quality_change_at=3,
                    water_quality_after_gain=20)


if __name__ == "__main__":
    unittest.main()
