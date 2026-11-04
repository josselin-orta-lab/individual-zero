"""P4 #967: six genuine uninterrupted native 128-tick lives, no motor script."""
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
from i2.runtime.native_paid_cycle import NativePaidI2, actual_old_water_gain

BODY = Body(85, 12, 16, 55)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
WORLDS = (("fragile_harmless", 0., 0),
          ("fragile_harmful", -12., 0),
          ("fragile_harmful_water_collapse", -12., 48))


def scored(event):
    frame, advice = event.get("frame"), event.get("advice")
    if frame is None or advice is None:
        return {}
    names = {x["candidate_ref"]: x["semantic_ref"]
             for x in frame["candidates"]}
    return {names[x["candidate_ref"]]: {
        "value": x["value"], "evidence": x["evidence_ref"]}
        for x in advice["values"]}


class CompetingSurvival967(unittest.TestCase):
    def test_six_paid_born_lives_and_hidden_quality(self):
        report, pairs, histories, births = {}, {}, {}, {}
        with tempfile.TemporaryDirectory() as folder:
            for name, harm, reversal in WORLDS:
                for credit in (False, True):
                    key = name + ("-on" if credit else "-off")
                    path = Path(folder) / (key + ".sqlite")
                    law = dict(
                        body=BODY, temperament=TRAITS, learning=True,
                        target_food_credit_enabled=credit,
                        spatial_world=True, ordinary_food_site="passage",
                        ordinary_water_site="camp", food_stock=1,
                        water_stock=1, food_restock_every=24,
                        water_restock_every=16, uc=1000, max_steps=128,
                        berry_food_gain=35., berry_integrity_delta=harm,
                        drink_water_gain=12., water_quality_change_at=reversal,
                        water_quality_after_gain=0.,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False, place_return_tie=True,
                        purpose_followthrough=True,
                        contextual_movement_credit=True)
                    life = NativePaidI2.create(path, **law)
                    born = life.audit()
                    for _ in range(128):
                        if life.step()["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        births[key] = db.execute(
                            "SELECT body_json,traits_json,food_stock,water_stock,"
                            "ordinary_food_site,ordinary_water_site,"
                            "food_restock_every,water_restock_every,"
                            "berry_food_gain,berry_integrity_delta,"
                            "drink_water_gain,water_quality_change_at,"
                            "water_quality_after_gain,max_steps "
                            "FROM native_genesis WHERE id=1").fetchone()
                        physical = db.execute(
                            "SELECT admitted_action,before_json,after_json,"
                            "net_physiological_relief,terminal "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        events = [json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(physical), len(events))
                    self.assertEqual(len(physical), final["revision"])
                    site, sites, actions = BORN_SITE, [BORN_SITE], []
                    meals, drinks, fo, wo, last_resort = [], [], [], [], []
                    minima, timeline, death = dict(born["body"]), [], None
                    for tick, ((action, before, after, relief, terminal),
                               event) in enumerate(zip(physical, events), 1):
                        pre, post = json.loads(before), json.loads(after)
                        offered = event["claim"]["capture"]["accessible_semantics"]
                        refs = event["claim"]["subjective_evidence_refs"]
                        self.assertFalse(any("water-quality" in r for r in refs))
                        self.assertFalse(any("water-offer-refilled:" in r for r in refs))
                        if "manger" in offered:
                            self.assertEqual(site, "passage")
                            fo.append(tick)
                        if "boire" in offered:
                            self.assertEqual(site, "camp")
                            wo.append(tick)
                        if event["claim"]["capture"]["goal_ref"] == (
                                "goal:physical-last-resort"):
                            last_resort.append(tick)
                        if action == "manger":
                            self.assertEqual(site, "passage")
                            self.assertIn(action, offered)
                            gain = post["food"] - pre["food"]
                            meals.append({"tick": tick,
                                "food_gain": round(gain, 3),
                                "integrity_delta": round(
                                    post["integrity"]-pre["integrity"], 3),
                                "low_gain": gain < 5, "zero_gain": gain <= 0})
                        if action == "boire":
                            self.assertEqual(site, "camp")
                            self.assertIn(action, offered)
                            actual = actual_old_water_gain(law, tick-1)
                            self.assertAlmostEqual(
                                post["water"], min(100.,
                                    max(0., pre["water"]-.4)+actual), places=6)
                            drinks.append({"tick": tick, "actual_gain": actual,
                                           "post_change": tick > reversal
                                           if reversal else False})
                        if action == "NO_ACTION":
                            self.assertLessEqual(post["food"], pre["food"])
                            self.assertLessEqual(post["water"], pre["water"])
                        if terminal:
                            self.assertIsNone(death)
                            death = tick
                            self.assertEqual(tick, len(physical))
                        for channel in minima:
                            minima[channel] = min(minima[channel], post[channel])
                        timeline.append({"tick": tick, "action": action,
                                         "body_before": pre,
                                         "paid": scored(event)})
                        actions.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(site, final["site"])
                    self.assertEqual(final["terminal"], death is not None)
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                    histories[key] = {"physics": physical, "timeline": timeline}
                    contacts = [d for d in drinks if d["post_change"]]
                    report[key] = {
                        "actions": actions, "sites": sites,
                        "food_offer_ticks": fo, "water_offer_ticks": wo,
                        "meals": meals, "drinks": drinks,
                        "post_change_exposure": (
                            "NO_REVERSAL" if not reversal else
                            "PHYSICALLY_OBSERVED" if contacts else
                            "UNOBSERVED_CENSORED"),
                        "post_change_empty_drinks": sum(
                            x["actual_gain"] == 0 for x in contacts),
                        "first_post_change_drink": (
                            contacts[0]["tick"] if contacts else None),
                        "last_resort_goal_ticks": last_resort,
                        "minimum_body": minima, "final_body": final["body"],
                        "terminal": final["terminal"], "terminal_tick": death,
                        "steps": final["revision"],
                        "right_censored": not final["terminal"]
                            and final["revision"] == 128,
                        "uc_spent": born["remaining_uc"]-final["remaining_uc"],
                        "cold_audit": "PASS"}
            for name, _, _ in WORLDS:
                left, right = name+"-off", name+"-on"
                self.assertEqual(births[left], births[right])
                a, b = histories[left]["timeline"], histories[right]["timeline"]
                first = next((i for i in range(min(len(a), len(b)))
                              if a[i]["action"] != b[i]["action"]), None)
                if first is not None:
                    self.assertEqual(a[first]["body_before"],
                                     b[first]["body_before"])
                    self.assertEqual([x["action"] for x in a[:first]],
                                     [x["action"] for x in b[:first]])
                pairs[name] = {
                    "first_motor_divergence": first+1 if first is not None else None,
                    "first_off": a[first] if first is not None else None,
                    "first_on": b[first] if first is not None else None}
            for credit in ("off", "on"):
                a = histories["fragile_harmful-"+credit]["physics"]
                b = histories["fragile_harmful_water_collapse-"+credit]["physics"]
                ix = next((i for i, (x, y) in enumerate(zip(a, b))
                           if x != y), None)
                if ix is not None:
                    self.assertGreater(ix+1, 48)
                    self.assertEqual(a[ix][0], "boire")
                    self.assertEqual(b[ix][0], "boire")
                pairs["hidden_quality-"+credit] = {
                    "first_physical_divergence": ix+1 if ix is not None else None}
            print("I2_COMPETING_SURVIVAL_967=" + json.dumps(
                {"lives": report, "comparisons": pairs},
                sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
