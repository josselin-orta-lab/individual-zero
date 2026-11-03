"""#951 graded food access: real paid, unscripted research births only.

No new cognitive score, motor script or simulated learned food outcome.
Predeclared experimental boundaries: NATIVE_ECOLOGICAL_EXPOSURE_GRADIENT_951.
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
FOOD_SITES = ("camp", "passage", "source")


class NativeEcologicalExposureGradient951(unittest.TestCase):
    def test_paid_graded_food_access_without_motor_scripts(self):
        outcomes = {}
        with tempfile.TemporaryDirectory() as folder:
            for food_site in FOOD_SITES:
                for learning in (False, True):
                    arm = "on" if learning else "off"
                    key = food_site + "-" + arm
                    path = Path(folder) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=learning, spatial_world=True,
                        ordinary_food_site=food_site,
                        ordinary_water_site="camp",
                        food_stock=1, water_stock=2,
                        food_restock_every=8, water_restock_every=8,
                        uc=850, max_steps=64, berry_food_gain=35.,
                        drink_water_gain=40.,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False,
                        place_return_tie=learning,
                        purpose_followthrough=learning,
                        contextual_movement_credit=learning)
                    initial = life.audit()
                    for _ in range(64):
                        result = life.step()
                        if result["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        physical = db.execute(
                            "SELECT admitted_action,before_json,after_json "
                            "FROM native_physical_events ORDER BY seq"
                        ).fetchall()
                        cognitive = [json.loads(event) for event, in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(physical), len(cognitive))
                    site = BORN_SITE
                    sites = [site]
                    food_offers, meals, water_offers, ties = [], [], [], []
                    source_tied_ticks, paid_statuses = [], []
                    for tick, ((action, before, after), event) in enumerate(
                            zip(physical, cognitive), 1):
                        before_body, after_body = (
                            json.loads(before), json.loads(after))
                        offered = event["claim"]["capture"][
                            "accessible_semantics"]
                        # In a spatial birth no unseen remote refill belongs
                        # to an individual's subjective history (#945/#950).
                        self.assertFalse(any(
                            "water-offer-refilled:" in ref
                            for ref in event["claim"]["subjective_evidence_refs"]))
                        if "manger" in offered:
                            self.assertEqual(site, food_site)
                            food_offers.append(tick)
                        if "boire" in offered:
                            self.assertEqual(site, "camp")
                            water_offers.append(tick)
                        if action == "manger":
                            self.assertEqual(site, food_site)
                            self.assertIn(action, offered)
                            meals.append({
                                "tick": tick, "site": site,
                                "before_food": before_body["food"],
                                "after_food": after_body["food"]})
                        if action == "boire":
                            self.assertIn(action, offered)
                        if action == "NO_ACTION":
                            self.assertLessEqual(
                                after_body["water"], before_body["water"])
                        advice = event.get("advice") or {}
                        paid_statuses.append(advice.get("status"))
                        if advice.get("status") == "AMBIGUOUS":
                            ties.append(tick)
                            frame = event.get("frame")
                            if frame is not None:
                                names = {
                                    candidate["candidate_ref"]: candidate["semantic_ref"]
                                    for candidate in frame["candidates"]}
                                values = advice.get("values") or []
                                if values:
                                    top = max(value["value"] for value in values)
                                    leaders = {
                                        names[value["candidate_ref"]]
                                        for value in values if value["value"] == top}
                                    if (site == "passage" and top > 0 and
                                            {"se_deplacer_vers_camp",
                                             "se_deplacer_vers_source"} <= leaders):
                                        source_tied_ticks.append(tick)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    if meals:
                        exposure = "FOOD_CONSUMED"
                    elif food_offers:
                        exposure = "FOOD_OFFERED_NOT_CHOSEN"
                    elif food_site in sites:
                        exposure = "FOOD_SITE_VISITED_NO_OFFER"
                    else:
                        exposure = "FOOD_SITE_NOT_VISITED"
                    outcomes[key] = {
                        "actions": [row[0] for row in physical],
                        "visited_sites": sites,
                        "food_offer_ticks": food_offers,
                        "water_offer_ticks": water_offers,
                        "meals": meals,
                        "food_exposure": exposure,
                        "ambiguous_ticks": ties,
                        "passage_source_route_tied_ticks": source_tied_ticks,
                        "paid_statuses": paid_statuses,
                        "food_history": [
                            round(json.loads(row[2])["food"], 3)
                            for row in physical],
                        "water_history": [
                            round(json.loads(row[2])["water"], 3)
                            for row in physical],
                        "energy_history": [
                            round(json.loads(row[2])["energy"], 3)
                            for row in physical],
                        "final_body": final["body"],
                        "spent_uc": (
                            initial["remaining_uc"] - final["remaining_uc"]),
                        "terminal": final["terminal"],
                        "right_censored": (
                            final["revision"] == 64 and not final["terminal"]),
                        "cold_audit": "PASS"}
                    self.assertEqual(
                        final["scientific_verdict"], "NOT_ESTABLISHED")
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
            print("I2_ECOLOGICAL_EXPOSURE_GRADIENT_951=" + json.dumps(
                outcomes, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
