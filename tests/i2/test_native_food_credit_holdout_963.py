"""#963 preregistered v19 out-of-sample study: eight PAID native lives.

No policy changes, scripts or handpicked motor trajectories. These are
selected physical scenarios, not random statistical replication.
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
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import (
    NativePaidI2, personally_observed_resource_outcomes)

WORLDS = {
    "hungry_harmless": ((85, 18, 35, 100), (0, .5, .3, 0, 0), 0., 8, 8, 2),
    "mild_harm_threat": ((85, 35, 35, 100), (0, .8, .15, 0, 0), -4., 8, 8, 2),
    "severe_harm": ((85, 35, 35, 100), (0, .5, .3, 0, 0), -12., 8, 8, 2),
    "scarce_competing_needs": ((85, 18, 28, 100), (0, .5, .3, 0, 0), -8., 32, 16, 1),
}


def paid(event):
    frame, advice = event.get("frame"), event.get("advice")
    if frame is None or advice is None:
        return {"status": None, "values": {}}
    names = {c["candidate_ref"]: c["semantic_ref"] for c in frame["candidates"]}
    return {"status": advice["status"],
            "values": {names[v["candidate_ref"]]:
                       {"value": v["value"], "evidence": v["evidence_ref"]}
                       for v in advice["values"]}}


class NativeFoodCreditHoldout963(unittest.TestCase):
    def test_eight_independent_paid_lives(self):
        results, genesis, timelines = {}, {}, {}
        with tempfile.TemporaryDirectory() as folder:
            for world, (body, traits, harm, food_period, water_period,
                        water_stock) in WORLDS.items():
                temperament = BirthTemperament(*traits)
                for credit in (False, True):
                    key = world + ("-on" if credit else "-off")
                    path = Path(folder) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=Body(*body), temperament=temperament,
                        learning=True, target_food_credit_enabled=credit,
                        spatial_world=True, ordinary_food_site="passage",
                        ordinary_water_site="camp", food_stock=1,
                        water_stock=water_stock,
                        food_restock_every=food_period,
                        water_restock_every=water_period, uc=950, max_steps=96,
                        berry_food_gain=35., berry_integrity_delta=harm,
                        drink_water_gain=40., evidence_tie_exploration=False,
                        sleep_consolidation=False, place_return_tie=True,
                        purpose_followthrough=True,
                        contextual_movement_credit=True)
                    initial = life.audit()
                    for _ in range(96):
                        if life.step()["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        genesis[key] = db.execute(
                            "SELECT body_json,traits_json,food_stock,water_stock,"
                            "ordinary_food_site,ordinary_water_site,"
                            "food_restock_every,water_restock_every,"
                            "berry_food_gain,berry_integrity_delta,"
                            "drink_water_gain,max_steps "
                            "FROM native_genesis WHERE id=1").fetchone()
                        physics = db.execute(
                            "SELECT admitted_action,before_json,after_json,"
                            "net_physiological_relief,terminal "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        events = [json.loads(x[0]) for x in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                        history = life._rows(db)
                    self.assertEqual(len(physics), len(events))
                    self.assertEqual(len(physics), len(history))
                    self.assertEqual(len(physics), final["revision"])
                    site, sites, moves, timeline = BORN_SITE, [BORN_SITE], [], []
                    meals, food_offers, water_offers, drinks = [], [], [], []
                    minima = dict(initial["body"])
                    first_death = None
                    for tick, ((action, before, after, relief, terminal),
                               event) in enumerate(zip(physics, events), 1):
                        pre, post = json.loads(before), json.loads(after)
                        offered = event["claim"]["capture"]["accessible_semantics"]
                        self.assertFalse(any(
                            "water-offer-refilled:" in x
                            for x in event["claim"]["subjective_evidence_refs"]))
                        if "manger" in offered:
                            self.assertEqual(site, "passage")
                            food_offers.append(tick)
                        if "boire" in offered:
                            self.assertEqual(site, "camp")
                            water_offers.append(tick)
                        if action == "manger":
                            self.assertEqual(site, "passage")
                            self.assertIn("manger", offered)
                            gain = post["food"] - pre["food"]
                            meals.append({
                                "tick": tick, "food_gain": round(gain, 3),
                                "integrity_change": round(
                                    post["integrity"] - pre["integrity"], 3),
                                "low_gain": gain < 5, "zero_gain": gain <= 0,
                                "net_relief": relief})
                        if action == "boire":
                            self.assertIn("boire", offered)
                            self.assertEqual(site, "camp")
                            drinks.append(tick)
                        if action == "NO_ACTION":
                            self.assertLessEqual(post["food"], pre["food"])
                            self.assertLessEqual(post["water"], pre["water"])
                        if terminal:
                            self.assertIsNone(first_death)
                            first_death = tick
                            self.assertEqual(tick, len(physics))
                        for channel in minima:
                            minima[channel] = min(minima[channel], post[channel])
                        counts = personally_observed_resource_outcomes(
                            previous=history[:tick - 1], traits=temperament)
                        timeline.append({
                            "tick": tick, "action": action,
                            "body_before": pre,
                            "needs_before": assess_needs(
                                Body(**pre), temperament).pressures,
                            "food_history": counts["manger"],
                            "paid": paid(event)})
                        moves.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    self.assertEqual(final["terminal"], first_death is not None)
                    self.assertFalse(final["m11_authenticated"])
                    self.assertFalse(final["engine_registered"])
                    self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                    timelines[key] = timeline
                    results[key] = {
                        "actions": moves, "sites": sites,
                        "food_offer_ticks": food_offers,
                        "water_offer_ticks": water_offers, "drink_ticks": drinks,
                        "meals": meals, "min_body": minima,
                        "final_body": final["body"],
                        "spent_uc": initial["remaining_uc"] -
                                    final["remaining_uc"],
                        "steps": len(physics), "terminal": final["terminal"],
                        "terminal_tick": first_death,
                        "right_censored": (
                            not final["terminal"] and len(physics) == 96),
                        "food_exposure": (
                            "FOOD_CONSUMED" if meals else
                            "FOOD_OFFERED_NOT_CHOSEN" if food_offers else
                            "FOOD_SITE_VISITED_NO_OFFER" if "passage" in sites
                            else "NO_FOOD_EXPOSURE"),
                        "cold_audit": "PASS"}
            comparisons = {}
            for world in WORLDS:
                off, on = world + "-off", world + "-on"
                self.assertEqual(genesis[off], genesis[on])
                a, b = timelines[off], timelines[on]
                first = next((i for i in range(min(len(a), len(b)))
                              if a[i]["action"] != b[i]["action"]), None)
                xa, xb = (a[first], b[first]) if first is not None else (None, None)
                if first is not None:
                    self.assertEqual(xa["body_before"], xb["body_before"])
                    self.assertEqual([v["action"] for v in a[:first]],
                                     [v["action"] for v in b[:first]])
                comparable = (first is not None and
                              xa["food_history"] == xb["food_history"] and
                              sum(xa["food_history"]) > 0)
                comparisons[world] = {
                    "first_motor_divergence": first + 1 if first is not None else None,
                    "food_credit_attributable_first_divergence": comparable,
                    "first_paid_off": xa, "first_paid_on": xb,
                    "different_lengths": len(a) != len(b)}
            print("I2_FOOD_CREDIT_HOLDOUT_963=" + json.dumps(
                {"lives": results, "comparisons": comparisons},
                sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
