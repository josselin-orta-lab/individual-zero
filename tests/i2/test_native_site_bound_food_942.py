"""#942 P3 physically localized ordinary food; research-only and source-audited.

Physical-only routing demonstrations below are not autonomous choices.
In the longer births all motors come from native paid Competition/Action Control.
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
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, old_food_accessible,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
BORN = Body(85, 35, 35, 100)


def row(seq, action):
    # Read-only physical route model, NEVER used as an autonomous action tape.
    return (seq, "capture:" + str(seq), action, 0.0, "{}", "{}", 0)


class SiteBoundOrdinaryFood942(unittest.TestCase):
    def test_source_only_and_depletion_in_physical_route_projection(self):
        meta = {"food_stock": 2, "ordinary_food_site": "source",
                "spatial_world": 1}
        self.assertFalse(old_food_accessible(meta, ()))
        at_passage = (row(1, "se_deplacer_vers_passage"),)
        self.assertFalse(old_food_accessible(meta, at_passage))
        at_source = (*at_passage, row(2, "se_deplacer_vers_source"))
        self.assertTrue(old_food_accessible(meta, at_source))
        once = (*at_source, row(3, "manger"))
        self.assertTrue(old_food_accessible(meta, once))
        twice = (*once, row(4, "manger"))
        self.assertFalse(old_food_accessible(meta, twice))
        left = (*at_source, row(3, "se_deplacer_vers_passage"))
        self.assertFalse(old_food_accessible(meta, left))
        # Legacy non-site-born food is spatially independent, not a new oracle.
        self.assertTrue(old_food_accessible({
            **meta, "ordinary_food_site": None}, ()))
        self.assertFalse(old_food_accessible({
            **meta, "food_stock": 0}, ()))

    def test_pure_routed_claim_offers_only_reached_food_without_oracle(self):
        # This explicitly models routing; no cognitive decision or paid motor
        # occurred. It tests subjective capture contents, NOT autonomous life.
        with tempfile.TemporaryDirectory() as directory:
            life = NativePaidI2.create(
                Path(directory) / "claim.sqlite", body=BORN, temperament=TRAITS,
                spatial_world=True, ordinary_food_site="source",
                ordinary_water_site="camp", food_stock=2, water_stock=2,
                max_steps=4, uc=100)
            with life._connect() as db:
                meta = life._meta(db)
            def physical_claim(rows):
                return life._claim(
                    {"revision": len(rows), "body": BORN, "traits": TRAITS,
                     "current_evidence": current_evidence(BORN, TRAITS)},
                    meta, rows)
            at_passage = (row(1, "se_deplacer_vers_passage"),)
            at_source = (*at_passage, row(2, "se_deplacer_vers_source"))
            for rows in ((), at_passage):
                self.assertNotIn(
                    "manger", physical_claim(rows).capture.accessible_semantics)
            arrived = physical_claim(at_source)
            self.assertIn("manger", arrived.capture.accessible_semantics)
            self.assertNotIn("boire", arrived.capture.accessible_semantics)
            self.assertIn("evidence:i2:spatial:current:source",
                          arrived.subjective_evidence_refs)
            self.assertFalse(any(
                "future" in item or "food_stock" in item
                for item in arrived.subjective_evidence_refs))
            consumed = (*at_source, row(3, "manger"), row(4, "manger"))
            self.assertNotIn(
                "manger", physical_claim(consumed).capture.accessible_semantics)
            departed = (*at_source, row(3, "se_deplacer_vers_passage"))
            self.assertNotIn(
                "manger", physical_claim(departed).capture.accessible_semantics)

    def test_genesis_gate_and_first_person_offer_at_born_camp(self):
        with tempfile.TemporaryDirectory() as directory:
            base = dict(body=BORN, temperament=TRAITS, spatial_world=True,
                        ordinary_water_site="camp",
                        ordinary_food_site="source", food_stock=2,
                        water_stock=2, max_steps=4, uc=100)
            for invalid in (
                {"ordinary_food_site": "nonexistent"},
                {"ordinary_food_site": True},
                {"ordinary_food_site": "source", "spatial_world": False,
                 "ordinary_water_site": None},
            ):
                with self.subTest(invalid=invalid), self.assertRaises(NativeRefusal):
                    NativePaidI2.create(
                        Path(directory) / ("invalid_" + str(len(invalid)) + ".sqlite"),
                        **{**base, **invalid})
            path = Path(directory) / "born.sqlite"
            life = NativePaidI2.create(path, **base)
            with life._connect() as db:
                meta = life._meta(db)
                from i2.runtime.native_physiology_journal import native_snapshot
                snap = native_snapshot(db)
                rows = life._rows(db)
                claim = life._claim(snap, meta, rows)
            self.assertNotIn("manger", claim.capture.accessible_semantics)
            self.assertIn("boire", claim.capture.accessible_semantics)
            self.assertNotIn("evidence:i2:spatial:current:source",
                             claim.subjective_evidence_refs)
            self.assertEqual(NativePaidI2.inspect(path).audit(), life.audit())
            # Birth locality is immutable. Pure physical routing above proves
            # offer mathematics; no paid individual has been driven to source.
            with sqlite3.connect(path) as db:
                db.execute("UPDATE native_genesis SET ordinary_food_site='camp'")
            with self.assertRaises(NativeRefusal):
                life.audit()

    def test_new_same_world_paid_longer_lives_no_motor_script(self):
        outcomes = {}
        with tempfile.TemporaryDirectory() as directory:
            for learning in (False, True):
                key = "learning-on" if learning else "learning-off"
                path = Path(directory) / (key + ".sqlite")
                life = NativePaidI2.create(
                    path, body=BORN, temperament=TRAITS,
                    learning=learning, spatial_world=True,
                    ordinary_food_site="source",
                    ordinary_water_site="camp", place_return_tie=learning,
                    purpose_followthrough=learning,
                    contextual_movement_credit=learning,
                    evidence_tie_exploration=False,
                    sleep_consolidation=False, food_stock=2, water_stock=2,
                    water_restock_every=0, drink_water_gain=40.0,
                    berry_food_gain=35.0, uc=500, max_steps=64)
                first = life.audit()
                for _ in range(64):
                    state = life.step()
                    if state["terminal"]:
                        break
                final = life.audit()
                self.assertEqual(NativePaidI2.inspect(path).audit(), final)
                with sqlite3.connect(path) as db:
                    physical = list(db.execute(
                        "SELECT admitted_action, after_json FROM "
                        "native_physical_events ORDER BY seq"))
                actions = [action for action, _ in physical]
                samples = [json.loads(body) for _, body in physical]
                site = BORN_SITE
                visited = [site]
                food_sites = []
                for action in actions:
                    if action == "manger":
                        food_sites.append(site)
                        self.assertEqual(site, "source")
                    if destination(action) is not None:
                        site = site_after(site, action)
                    visited.append(site)
                self.assertLessEqual(len(food_sites), 2)
                self.assertEqual(final["site"], site)
                outcomes[key] = {
                    "visited_sites": visited,
                    "food_use_sites": food_sites,
                    "actions": actions,
                    "food_uses": sum(a == "manger" for a in actions),
                    "drinks": sum(a == "boire" for a in actions),
                    "final_body": final["body"],
                    "food_history": [round(b["food"], 3) for b in samples],
                    "water_history": [round(b["water"], 3) for b in samples],
                    "spent_uc": first["remaining_uc"] - final["remaining_uc"],
                    "terminal": final["terminal"],
                    "horizon_censored": (
                        final["revision"] == 64 and not final["terminal"]),
                    "exposure": "FOOD_USED" if "manger" in actions
                                else "NO_FOOD_EXPOSURE",
                    "cold_audit": "PASS"}
                self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                self.assertFalse(final["m11_authenticated"])
                self.assertFalse(final["engine_registered"])
            print("I2_LOCAL_FOOD_TWO_NEEDS_P3_942=" + json.dumps(
                outcomes, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
