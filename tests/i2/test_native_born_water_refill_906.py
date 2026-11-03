"""Exogenous recurring old-water offers across one native I2 life.

An offer is an environmental affordance available at the current physical
tick, not an observed prediction about its quality or a free water grant.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, old_water_available,
)


class NativeBornWaterRenewalTests(unittest.TestCase):
    BODY = Body(85, 90, 90, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def test_refill_is_caused_by_elapsed_ticks_not_learning(self):
        metadata = {"water_stock": 1, "water_restock_every": 3}
        def history(actions):
            return tuple((i, "", action) for i, action in enumerate(actions, 1))
        self.assertEqual(old_water_available(metadata, history([])), 1)
        self.assertEqual(old_water_available(metadata, history(["boire"])), 0)
        self.assertEqual(old_water_available(
            metadata, history(["boire", "dormir", "attendre"])), 1)
        self.assertEqual(old_water_available(
            metadata, history(["boire", "dormir", "attendre", "boire"])), 0)
        self.assertEqual(old_water_available(
            metadata, history(["boire", "dormir", "attendre", "boire",
                               "dormir", "attendre"])), 1)
        metadata["water_restock_every"] = 0
        self.assertEqual(old_water_available(metadata, history([
            "boire", "dormir", "attendre", "attendre"])), 0)

    def test_one_long_life_observes_refills_only_after_committed_time(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "long-refill.sqlite"
            actor = NativePaidI2.create(
                path, body=self.BODY, temperament=self.TRAITS,
                learning=False, sleep_consolidation=False,
                food_stock=0, water_stock=0, water_restock_every=3,
                drink_water_gain=0, discovered_water_gain=0,
                max_steps=12, uc=1000)
            self.assertEqual(actor.audit()["max_steps"], 12)
            for _ in range(12):
                actor.step()
            final = actor.audit()
            self.assertEqual(final["revision"], 12)
            self.assertEqual(NativePaidI2.inspect(path).audit(), final)
            with sqlite3.connect(path) as db:
                records = [json.loads(row[0]) for row in db.execute(
                    "SELECT event_json FROM events ORDER BY seq")]
                actions = [row[0] for row in db.execute(
                    "SELECT admitted_action FROM native_physical_events "
                    "ORDER BY seq")]
            for index, record in enumerate(records):
                capture = record["claim"]["capture"]
                observed = record["claim"]["subjective_evidence_refs"]
                # Refill is an exogenous fact of elapsed physical time,
                # not a promise about future resource success.
                for epoch in range(3, 13, 3):
                    marker = "evidence:i2:native:water-offer-refilled:" + str(epoch)
                    self.assertEqual(marker in observed, index >= epoch)
                self.assertEqual(
                    "boire" in capture["accessible_semantics"],
                    index // 3 > sum(a == "boire" for a in actions[:index]))
            self.assertNotIn(
                "boire", records[0]["claim"]["capture"]["accessible_semantics"])
            self.assertNotIn(
                "evidence:i2:native:water-offer-refilled:3",
                records[2]["claim"]["subjective_evidence_refs"])
            self.assertIn(
                "evidence:i2:native:water-offer-refilled:3",
                records[3]["claim"]["subjective_evidence_refs"])
            self.assertEqual(final["temperament"], self.TRAITS.as_dict())

    def test_refill_after_vetoed_physical_time_is_an_offer_not_free_water(self):
        # Safety rejection prevents motor actions, not physical time.
        # A born external refill may appear after three genuine time ticks,
        # but cannot grant hydration until a later admitted actual drink.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "veto-physical-time.sqlite"
            actor = NativePaidI2.create(
                path, body=self.BODY, temperament=self.TRAITS,
                learning=False, sleep_consolidation=False,
                food_stock=0, water_stock=0, water_restock_every=3,
                drink_water_gain=20.0, max_steps=5, uc=1000)
            for expected in range(1, 4):
                snap = actor.step(veto=True)
                self.assertEqual(snap["revision"], expected)
                self.assertAlmostEqual(
                    snap["body"]["water"], self.BODY.water - 0.4 * expected)
                self.assertEqual(snap, NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                actions = [row[0] for row in db.execute(
                    "SELECT admitted_action FROM native_physical_events")]
                events = [json.loads(row[0]) for row in db.execute(
                    "SELECT event_json FROM events ORDER BY seq")]
            self.assertEqual(len(actions), 3)
            self.assertTrue(all(action == "NO_ACTION" for action in actions))
            for event in events:
                self.assertNotIn(
                    "boire", event["claim"]["capture"]["accessible_semantics"])
            actor.step()
            with sqlite3.connect(path) as db:
                fourth = json.loads(db.execute(
                    "SELECT event_json FROM events WHERE seq=4").fetchone()[0])
            self.assertIn(
                "boire", fourth["claim"]["capture"]["accessible_semantics"])
            self.assertIn(
                "evidence:i2:native:water-offer-refilled:3",
                fourth["claim"]["subjective_evidence_refs"])
            self.assertEqual(actor.audit()["revision"], 4)

    def test_independent_born_controls_share_refill_and_genesis_is_signed(self):
        with tempfile.TemporaryDirectory() as folder:
            starts = []
            for learning in (True, False):
                path = Path(folder) / (str(learning) + ".sqlite")
                actor = NativePaidI2.create(
                    path, body=self.BODY, temperament=self.TRAITS,
                    learning=learning, sleep_consolidation=False,
                    water_stock=0, water_restock_every=3,
                    max_steps=6, food_stock=0, uc=1000)
                starts.append(actor.audit()["body"])
                for _ in range(3):
                    actor.step()
                with sqlite3.connect(path) as db:
                    records = [json.loads(row[0]) for row in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                for record in records:
                    self.assertNotIn(
                        "evidence:i2:native:water-offer-refilled:3",
                        record["claim"]["subjective_evidence_refs"])
                with sqlite3.connect(path) as db:
                    db.execute(
                        "UPDATE native_genesis SET water_restock_every=4 WHERE id=1")
                with self.assertRaises(NativeRefusal):
                    actor.audit()
            self.assertEqual(starts[0], starts[1])
            for invalid in (True, -1, 33, 3.0, "3"):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(folder) / ("bad-" + str(invalid) + ".sqlite"),
                            body=self.BODY, temperament=self.TRAITS,
                            water_restock_every=invalid)


if __name__ == "__main__":
    unittest.main()
