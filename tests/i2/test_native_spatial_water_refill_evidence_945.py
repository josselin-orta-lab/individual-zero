"""P3 #945: a spatial research owner must not infer distant refill events.

All route projections are physical-only probes, not scripted native motors.
Native action evidence below is chosen by existing paid Competition.
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
from i2.modules.native_owner_support import current_evidence
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, bounded_native_evidence,
    old_water_accessible, old_water_available,
)

BODY = Body(85, 40, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
MARKER = "evidence:i2:native:water-offer-refilled:"


def physical(seq, action="NO_ACTION"):
    return (seq, "capture:" + str(seq), action, 0.0, "{}", "{}", 0)


class SpatialWaterRefillEvidence945(unittest.TestCase):
    def test_spatial_cannot_observe_hidden_history_by_global_clock(self):
        rows = tuple(physical(tick) for tick in range(1, 10))
        local = current_evidence(BODY, TRAITS)
        spatial = bounded_native_evidence(
            local, rows, water_restock_every=3, spatial_world=True)
        self.assertFalse(any(MARKER in item for item in spatial))
        global_access = bounded_native_evidence(
            local, rows, water_restock_every=3, spatial_world=False)
        self.assertTrue(any(MARKER + "3" == item for item in global_access))
        self.assertTrue(any(MARKER + "6" == item for item in global_access))
        self.assertTrue(any(MARKER + "9" == item for item in global_access))
        self.assertEqual(
            bounded_native_evidence(local, rows, water_restock_every=0,
                                    spatial_world=True),
            bounded_native_evidence(local, rows, water_restock_every=0,
                                    spatial_world=False))

    def test_spatial_first_person_claim_keeps_local_offer_not_refill_clock(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "projection.sqlite"
            life = NativePaidI2.create(
                path, body=BODY, temperament=TRAITS, uc=100,
                spatial_world=True, ordinary_water_site="camp",
                ordinary_food_site="source", water_stock=0, food_stock=0,
                water_restock_every=3, food_restock_every=3, max_steps=8)
            with life._connect() as db:
                meta = life._meta(db)

            def capture(rows):
                claim = life._claim(
                    {"revision": len(rows), "body": BODY, "traits": TRAITS,
                     "current_evidence": current_evidence(BODY, TRAITS)},
                    meta, rows)
                self.assertFalse(any(MARKER in item for item
                                     in claim.subjective_evidence_refs))
                self.assertFalse(any("food-restock" in item for item
                                     in claim.subjective_evidence_refs))
                return claim
            camp_at_birth = capture(())
            self.assertNotIn("boire", camp_at_birth.capture.accessible_semantics)
            at_passage = (physical(1, "se_deplacer_vers_passage"),)
            at_source = (*at_passage, physical(2, "se_deplacer_vers_source"))
            remote_at_refill = (*at_source, physical(3))
            self.assertEqual(old_water_available(meta, remote_at_refill), 1)
            self.assertFalse(old_water_accessible(meta, remote_at_refill))
            remote_claim = capture(remote_at_refill)
            self.assertNotIn("boire", remote_claim.capture.accessible_semantics)
            self.assertIn("manger", remote_claim.capture.accessible_semantics)
            arrived_camp = (*remote_at_refill,
                            physical(4, "se_deplacer_vers_passage"),
                            physical(5, "se_deplacer_vers_camp"))
            camp_claim = capture(arrived_camp)
            self.assertIn("boire", camp_claim.capture.accessible_semantics)
            self.assertNotIn("manger", camp_claim.capture.accessible_semantics)
            self.assertEqual(life.audit(), NativePaidI2.inspect(path).audit())

    def test_forged_remote_water_refill_in_cognitive_journal_refused(self):
        # Negative integrity control, not a legitimate observation: an
        # adversary cannot manufacture a first-person refill by rewriting
        # one sealed event without a matching owned provenance chain.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "forged_refill.sqlite"
            life = NativePaidI2.create(
                path, body=BODY, temperament=TRAITS, uc=200,
                spatial_world=True, ordinary_water_site="source",
                ordinary_food_site="camp", water_stock=0, food_stock=0,
                water_restock_every=2, food_restock_every=0,
                max_steps=5)
            for _ in range(4):
                life.step()
            self.assertEqual(life.audit(), NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                original = db.execute(
                    "SELECT event_json FROM events WHERE seq=4").fetchone()[0]
                event = json.loads(original)
                evidence = event["claim"]["subjective_evidence_refs"]
                self.assertFalse(any(MARKER in item for item in evidence))
                evidence.append(MARKER + "2")
                db.execute("UPDATE events SET event_json=? WHERE seq=4",
                           (json.dumps(event, sort_keys=True,
                                       separators=(",", ":")),))
            with self.assertRaises((NativeRefusal, ValueError)):
                life.audit()

    def test_same_physical_laws_paid_learning_off_on_cold_audit(self):
        out = {}
        with tempfile.TemporaryDirectory() as folder:
            for learning in (False, True):
                life = NativePaidI2.create(
                    Path(folder) / ("on.sqlite" if learning else "off.sqlite"),
                    body=BODY, temperament=TRAITS, uc=250, max_steps=16,
                    learning=learning, spatial_world=True,
                    ordinary_water_site="camp", ordinary_food_site="source",
                    food_stock=0, water_stock=0,
                    water_restock_every=3, food_restock_every=3,
                    place_return_tie=learning,
                    purpose_followthrough=learning,
                    contextual_movement_credit=learning)
                initial = life.audit()
                for _ in range(16):
                    final = life.step()
                    if final["terminal"]:
                        break
                self.assertEqual(final, NativePaidI2.inspect(life.path).audit())
                with sqlite3.connect(life.path) as db:
                    records = [json.loads(row[0]) for row in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                    physical = list(db.execute(
                        "SELECT admitted_action,before_json,after_json "
                        "FROM native_physical_events ORDER BY seq"))
                self.assertEqual(len(records), len(physical))
                actions = []
                local_offers = []
                for tick, (event, sample) in enumerate(
                        zip(records, physical), 1):
                    action, before_json, after_json = sample
                    actions.append(action)
                    self.assertFalse(any(
                        MARKER in evidence for evidence in
                        event["claim"]["subjective_evidence_refs"]))
                    offered = event["claim"]["capture"][
                        "accessible_semantics"]
                    if "boire" in offered:
                        local_offers.append(tick)
                    if action == "boire":
                        self.assertIn("boire", offered)
                    if action == "NO_ACTION":
                        # Even when physical refill happens after a tick,
                        # an abstention never produces free bodily hydration.
                        before_body = json.loads(before_json)
                        after_body = json.loads(after_json)
                        self.assertLessEqual(
                            after_body["water"], before_body["water"])
                out["on" if learning else "off"] = dict(
                    actions=actions,
                    locally_observed_water_offer_ticks=local_offers,
                    final_body=final["body"],
                    spent_uc=initial["remaining_uc"]-final["remaining_uc"],
                    death=final["terminal"],
                    right_censored=final["revision"] == 16
                        and not final["terminal"],
                    cold_audit="PASS")
            print("I2_LOCAL_WATER_EVIDENCE_945=" + json.dumps(
                out, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
