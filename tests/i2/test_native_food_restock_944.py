"""P3 #944: physically renewed food, without clock-driven learned value.

Pure route/stock projections are NOT autonomous proof. Actual born lives below
let existing paid Competition and Action Control choose every action.
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
    NativePaidI2, NativeRefusal, old_food_available, old_food_accessible,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
BODY = Body(85, 35, 35, 100)


def physical(seq, action="NO_ACTION"):
    # Read-only physical record shape, never an admitted test motor.
    return (seq, "capture:" + str(seq), action, 0.0, "{}", "{}", 0)


class ExogenousNativeFoodRestock944(unittest.TestCase):
    def test_exogenous_stock_and_locality_are_physical_only(self):
        meta = {"food_stock": 0, "food_restock_every": 3,
                "ordinary_food_site": "source", "spatial_world": 1}
        self.assertEqual(old_food_available(meta, ()), 0)
        self.assertEqual(old_food_available(meta, (physical(1), physical(2))), 0)
        at_passage = (physical(1, "se_deplacer_vers_passage"),)
        at_source = (*at_passage, physical(2, "se_deplacer_vers_source"))
        self.assertFalse(old_food_accessible(meta, at_source))
        third = (*at_source, physical(3))
        self.assertEqual(old_food_available(meta, third), 1)
        self.assertTrue(old_food_accessible(meta, third))
        eaten = (*third, physical(4, "manger"))
        self.assertFalse(old_food_accessible(meta, eaten))
        self.assertEqual(old_food_available(meta, (*eaten, physical(5))), 0)
        refilled = (*eaten, physical(5), physical(6))
        self.assertEqual(old_food_available(meta, refilled), 1)
        self.assertTrue(old_food_accessible(meta, refilled))
        remote = (*refilled, physical(7, "se_deplacer_vers_passage"))
        self.assertEqual(old_food_available(meta, remote), 1)
        self.assertFalse(old_food_accessible(meta, remote))
        no_refill = {**meta, "food_restock_every": 0}
        self.assertEqual(old_food_available(no_refill, refilled), -1)
        self.assertFalse(old_food_accessible(no_refill, refilled))
        one_born = {**meta, "food_stock": 1}
        self.assertTrue(old_food_accessible(one_born, at_source))
        self.assertEqual(old_food_available(one_born, refilled), 2)

    def test_current_capture_never_offers_remote_or_future_food(self):
        # Pure prospective route probe, not a real paid/dispatched action.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "local_capture.sqlite"
            life = NativePaidI2.create(
                path, body=BODY, temperament=TRAITS,
                spatial_world=True, ordinary_food_site="source",
                ordinary_water_site="camp", food_stock=0, water_stock=0,
                food_restock_every=3, uc=100, max_steps=7)
            with life._connect() as db:
                meta = life._meta(db)
            def offer(rows):
                claim = life._claim(
                    {"revision": len(rows), "body": BODY, "traits": TRAITS,
                     "current_evidence": current_evidence(BODY, TRAITS)},
                    meta, rows)
                self.assertFalse(any("food-restock" in ref or
                                     "future" in ref for ref in
                                     claim.subjective_evidence_refs))
                return claim.capture.accessible_semantics
            beginning = ()
            at_passage = (physical(1, "se_deplacer_vers_passage"),)
            at_source = (*at_passage, physical(2, "se_deplacer_vers_source"))
            self.assertNotIn("manger", offer(beginning))
            self.assertNotIn("manger", offer(at_passage))
            self.assertNotIn("manger", offer(at_source))
            refill_at_source = (*at_source, physical(3))
            self.assertIn("manger", offer(refill_at_source))
            eaten = (*refill_at_source, physical(4, "manger"))
            self.assertNotIn("manger", offer(eaten))
            self.assertIn("manger", offer((*eaten, physical(5), physical(6))))
            remote_again = (*eaten, physical(5, "se_deplacer_vers_passage"),
                            physical(6))
            self.assertNotIn("manger", offer(remote_again))

    def test_born_interval_is_exact_and_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            base = dict(body=BODY, temperament=TRAITS,
                        spatial_world=True, ordinary_food_site="source",
                        ordinary_water_site="camp", food_stock=0, water_stock=2,
                        uc=100, max_steps=4)
            for index, invalid in enumerate((-1, True, 33, 1.5, "4")):
                with self.subTest(invalid=invalid), self.assertRaises(NativeRefusal):
                    NativePaidI2.create(root / ("illegal" + str(index) + ".sqlite"),
                                        **base, food_restock_every=invalid)
            path = root / "life.sqlite"
            life = NativePaidI2.create(path, **base, food_restock_every=3)
            self.assertEqual(life.audit(), NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                db.execute("UPDATE native_genesis SET food_restock_every=4")
            with self.assertRaises(NativeRefusal):
                life.audit()

    def test_two_independent_96_tick_paid_lives(self):
        outcomes = {}
        with tempfile.TemporaryDirectory() as folder:
            for learning in (False, True):
                key = "on" if learning else "off"
                path = Path(folder) / (key + ".sqlite")
                life = NativePaidI2.create(
                    path, body=BODY, temperament=TRAITS, learning=learning,
                    spatial_world=True, ordinary_food_site="source",
                    ordinary_water_site="camp", food_stock=1, water_stock=2,
                    food_restock_every=8, water_restock_every=8,
                    uc=850, max_steps=96, drink_water_gain=40.,
                    berry_food_gain=35., evidence_tie_exploration=False,
                    sleep_consolidation=False, place_return_tie=learning,
                    purpose_followthrough=learning,
                    contextual_movement_credit=learning)
                first = life.audit()
                for _ in range(96):
                    state = life.step()
                    if state["terminal"]:
                        break
                final = life.audit()
                self.assertEqual(final, NativePaidI2.inspect(path).audit())
                with sqlite3.connect(path) as db:
                    records = db.execute(
                        "SELECT admitted_action, before_json, after_json "
                        "FROM native_physical_events ORDER BY seq").fetchall()
                    cognitive = [json.loads(record[0]) for record in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                self.assertEqual(len(cognitive), len(records))
                site = BORN_SITE
                visited_sites = [site]
                food_sites = []
                for action, _, _ in records:
                    if action == "manger":
                        self.assertEqual(site, "source")
                        food_sites.append(site)
                    if destination(action) is not None:
                        site = site_after(site, action)
                    visited_sites.append(site)
                self.assertEqual(final["site"], site)
                actions = [item[0] for item in records]
                # Read-only diagnosis of a possible persistent positive tie.
                # These are real previously paid frames, never new evaluations.
                statuses = []
                ambiguous = []
                for tick, event in enumerate(cognitive, 1):
                    advice = event.get("advice")
                    statuses.append(advice.get("status") if advice else None)
                    if not advice or not event.get("frame"):
                        continue
                    values = advice.get("values") or []
                    if not values:
                        continue
                    top = max(value["value"] for value in values)
                    if top <= 0:
                        continue
                    names = {candidate["candidate_ref"]: candidate["semantic_ref"]
                             for candidate in event["frame"]["candidates"]}
                    tied = sorted(names[value["candidate_ref"]]
                                  for value in values if value["value"] == top)
                    if len(tied) > 1:
                        ambiguous.append({
                            "tick": tick, "site": visited_sites[tick - 1],
                            "top": top, "candidates": tied,
                            "advice_status": advice.get("status")})
                outcomes[key] = dict(
                    actions=actions, visited_sites=visited_sites,
                    paid_advice_statuses=statuses,
                    positive_top_ties=ambiguous,
                    food_use_sites=food_sites,
                    water_history=[round(json.loads(a)["water"], 3)
                                   for _, _, a in records],
                    food_history=[round(json.loads(a)["food"], 3)
                                  for _, _, a in records],
                    final_body=final["body"],
                    spent_uc=first["remaining_uc"] - final["remaining_uc"],
                    terminal=final["terminal"],
                    right_censored=(
                        final["revision"] == 96 and not final["terminal"]),
                    food_exposure=("FOOD_USED" if food_sites
                                   else "NO_FOOD_EXPOSURE"),
                    cold_audit="PASS")
                self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                self.assertFalse(final["m11_authenticated"])
                self.assertFalse(final["engine_registered"])
            print("I2_EXOGENOUS_FOOD_RESTOCK_P3_944=" + json.dumps(
                outcomes, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
