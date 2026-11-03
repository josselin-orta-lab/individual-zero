"""P4 #952: born food-harm contrast and actual satiety credit, research only.

The experiment is a follow-up to source-locked #951. Four independent born
lives choose every motor through paid native Competition/Action Control.
No motor script, outcome adjustment, hidden harm oracle, or policy change.
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
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import NativePaidI2

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
DELTAS = (-8.0, 0.0)


class NativeHarmfulFoodSaturation952(unittest.TestCase):
    def test_born_harm_and_real_paid_satiety_outcomes(self):
        outcomes = {}
        physical_birth = {}
        with tempfile.TemporaryDirectory() as folder:
            for harm in DELTAS:
                for learning in (False, True):
                    key = ("harm" if harm < 0 else "harmless") + (
                        "-on" if learning else "-off")
                    path = Path(folder) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=learning, spatial_world=True,
                        ordinary_food_site="passage",
                        ordinary_water_site="camp",
                        food_stock=1, water_stock=2,
                        food_restock_every=8, water_restock_every=8,
                        uc=850, max_steps=64, berry_food_gain=35.,
                        berry_integrity_delta=harm, drink_water_gain=40.,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False,
                        place_return_tie=learning,
                        purpose_followthrough=learning,
                        contextual_movement_credit=learning)
                    beginning = life.audit()
                    for _ in range(64):
                        state = life.step()
                        if state["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        physical_birth[key] = db.execute(
                            "SELECT body_json,traits_json,food_stock,water_stock,"
                            "ordinary_food_site,ordinary_water_site,"
                            "food_restock_every,water_restock_every,"
                            "berry_food_gain,drink_water_gain,max_steps "
                            "FROM native_genesis WHERE id=1").fetchone()
                        rows = db.execute(
                            "SELECT admitted_action,before_json,after_json "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        events = [json.loads(line) for line, in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(rows), len(events))
                    current_site = BORN_SITE
                    visited = [current_site]
                    meals, food_offers, ambiguous = [], [], []
                    for tick, ((action, before, after), event) in enumerate(
                            zip(rows, events), 1):
                        available = event["claim"]["capture"][
                            "accessible_semantics"]
                        self.assertFalse(any(
                            "water-offer-refilled:" in evidence
                            for evidence in
                            event["claim"]["subjective_evidence_refs"]))
                        if "manger" in available:
                            self.assertEqual(current_site, "passage")
                            food_offers.append(tick)
                        if event.get("advice") and (
                                event["advice"]["status"] == "AMBIGUOUS"):
                            ambiguous.append(tick)
                        if action == "manger":
                            self.assertIn("manger", available)
                            before_body = json.loads(before)
                            after_body = json.loads(after)
                            food_gain = after_body["food"] - before_body["food"]
                            integrity_change = (
                                after_body["integrity"] -
                                before_body["integrity"])
                            meals.append({
                                "tick": tick,
                                "site": current_site,
                                "before_food": round(before_body["food"], 3),
                                "after_food": round(after_body["food"], 3),
                                "net_food_gain": round(food_gain, 3),
                                "net_integrity_change": round(
                                    integrity_change, 3),
                                "near_satiation": food_gain < 5,
                                "zero_or_negative_food_gain": food_gain <= 0})
                        if destination(action) is not None:
                            current_site = site_after(current_site, action)
                        visited.append(current_site)
                    self.assertEqual(final["site"], current_site)
                    outcomes[key] = dict(
                        actions=[row[0] for row in rows],
                        sites=visited,
                        meals=meals, food_offer_ticks=food_offers,
                        ambiguous_ticks=ambiguous,
                        exposure=("FOOD_CONSUMED" if meals else
                                  "FOOD_OFFERED_NOT_CHOSEN" if food_offers else
                                  "FOOD_SITE_REACHED_NO_OFFER" if "passage" in visited
                                  else "FOOD_SITE_NOT_VISITED"),
                        integrity_history=[
                            round(json.loads(row[2])["integrity"], 3)
                            for row in rows],
                        food_history=[
                            round(json.loads(row[2])["food"], 3)
                            for row in rows],
                        water_history=[
                            round(json.loads(row[2])["water"], 3)
                            for row in rows],
                        final_body=final["body"],
                        spent_uc=beginning["remaining_uc"] -
                                 final["remaining_uc"],
                        terminal=final["terminal"],
                        right_censored=(
                            final["revision"] == 64 and
                            not final["terminal"]),
                        cold_audit="PASS")
                    self.assertEqual(
                        final["scientific_verdict"], "NOT_ESTABLISHED")
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
            # Different born food integrity laws are intended; all OTHER
            # physical laws must match within each learning arm and site.
            for arm in ("off", "on"):
                self.assertEqual(
                    physical_birth["harm-" + arm],
                    physical_birth["harmless-" + arm])
            print("I2_HARMFUL_FOOD_SATIETY_952=" + json.dumps(
                outcomes, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
