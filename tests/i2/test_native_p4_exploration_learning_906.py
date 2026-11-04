"""P4 #906: prospective lived food harm vs learning, innate exploration fixed ON.

No motor tape, no new cognitive rules, no hidden injury oracle. Both genuine
independent native births decide using paid Competition and fresh Action Control.
A terminal life ends naturally; 96 steps alive means right-censored, not GO.
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
from i2.runtime.native_paid_cycle import NativePaidI2

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
WORLDS = (("harmless", 0.), ("harmful", -12.))


def paid(event):
    frame, advice = event.get("frame"), event.get("advice")
    if frame is None or advice is None:
        return {"status": None, "values": {}}
    names = {c["candidate_ref"]: c["semantic_ref"]
             for c in frame["candidates"]}
    return {"status": advice["status"],
            "values": {names[v["candidate_ref"]]: {
                "score": v["value"], "evidence": v["evidence_ref"]}
                for v in advice["values"]}}


class NativeP4InnateExplorationLearning906(unittest.TestCase):
    def test_four_unforced_lives_under_harmless_or_harmful_food(self):
        report, timelines, births = {}, {}, {}
        with tempfile.TemporaryDirectory() as folder:
            for name, harm in WORLDS:
                for learning in (False, True):
                    key = name + ("-learning-on" if learning else "-learning-off")
                    path = Path(folder) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=learning, origin_novelty_tie=True,
                        spatial_world=True, ordinary_food_site="source",
                        ordinary_water_site="camp", food_stock=1,
                        water_stock=2, food_restock_every=8,
                        water_restock_every=8, uc=950, max_steps=96,
                        berry_food_gain=35., berry_integrity_delta=harm,
                        drink_water_gain=40., target_food_credit_enabled=True,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False, place_return_tie=False,
                        purpose_followthrough=False,
                        contextual_movement_credit=False)
                    birth = life.audit()
                    for _ in range(96):
                        if life.step()["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    self.assertEqual(final["scientific_verdict"],
                                     "NOT_ESTABLISHED")
                    with sqlite3.connect(path) as db:
                        births[key] = db.execute(
                            "SELECT body_json,traits_json,food_stock,water_stock,"
                            "ordinary_food_site,ordinary_water_site,"
                            "food_restock_every,water_restock_every,"
                            "berry_food_gain,berry_integrity_delta,"
                            "drink_water_gain,max_steps,origin_novelty_tie "
                            "FROM native_genesis WHERE id=1").fetchone()
                        physical = db.execute(
                            "SELECT admitted_action,before_json,after_json,"
                            "net_physiological_relief,terminal "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        cognitive = [json.loads(x[0]) for x in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(physical), len(cognitive))
                    self.assertEqual(len(physical), final["revision"])
                    site, sites = BORN_SITE, [BORN_SITE]
                    actions, meals, drinks, fo, wo, novelty = [], [], [], [], [], []
                    timeline, food_success, food_failure, food_injury = [], 0, 0, 0
                    minima = dict(birth["body"])
                    death = None
                    for tick, (p, event) in enumerate(zip(physical, cognitive), 1):
                        action, before, after, relief, terminal = p
                        pre, post = json.loads(before), json.loads(after)
                        offered = event["claim"]["capture"]["accessible_semantics"]
                        refs = event["claim"]["subjective_evidence_refs"]
                        self.assertFalse(any("future" in r or
                                             "food-hidden" in r or
                                             "water-quality" in r for r in refs))
                        if "manger" in offered:
                            self.assertEqual(site, "source")
                            fo.append(tick)
                        if "boire" in offered:
                            self.assertEqual(site, "camp")
                            wo.append(tick)
                        if destination(action) is not None:
                            self.assertIn(action, offered)
                        if action == "manger":
                            self.assertEqual(site, "source")
                            self.assertIn("manger", offered)
                            gain = post["food"]-pre["food"]
                            injury = post["integrity"]-pre["integrity"]
                            meals.append({"tick": tick, "gain": round(gain, 4),
                                          "injury": round(injury, 4),
                                          "relief": round(relief, 5)})
                            if assess_needs(Body(**pre), TRAITS).pressures["food"] > 0:
                                if gain > 0:
                                    food_success += 1
                                else:
                                    food_failure += 1
                            if injury < 0:
                                food_injury += 1
                        if action == "boire":
                            self.assertEqual(site, "camp")
                            self.assertIn(action, offered)
                            drinks.append(tick)
                        if action == "NO_ACTION":
                            self.assertLessEqual(post["food"], pre["food"])
                            self.assertLessEqual(post["water"], pre["water"])
                        score = paid(event)
                        if any(":visited-versus-unvisited-adjacent-tie" in v["evidence"]
                               for v in score["values"].values()):
                            novelty.append(tick)
                        # Before-tick learned-food counts are independent of the
                        # current motor and thus available only from past effects.
                        previous_meals = [m for m in meals if m["tick"] < tick]
                        timeline.append({
                            "tick": tick, "action": action, "site": site,
                            "before": pre, "after": post,
                            "prior_food_contacts": len(previous_meals),
                            "prior_food_injuries": food_injury -
                                int(action == "manger" and
                                    post["integrity"] < pre["integrity"]),
                            "paid": score,
                        })
                        if terminal:
                            self.assertIsNone(death)
                            death = tick
                            self.assertEqual(tick, len(physical))
                        for channel in minima:
                            minima[channel] = min(minima[channel], post[channel])
                        actions.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    self.assertEqual(final["terminal"], death is not None)
                    timelines[key] = timeline
                    report[key] = {
                        "actions": actions, "sites": sites,
                        "food_offer_ticks": fo, "water_offer_ticks": wo,
                        "food_exposure": ("FOOD_CONSUMED" if meals else
                            "FOOD_OFFERED_NO_CONTACT" if fo else
                            "SOURCE_REACHED_NO_OFFER" if "source" in sites else
                            "NO_FOOD_EXPOSURE"),
                        "meals": meals, "drinks": drinks,
                        "first_source_visit": next(
                            (i for i, v in enumerate(sites) if v == "source"), None),
                        "origin_novelty_paid_ticks": novelty,
                        "prior_food_successes": food_success,
                        "prior_food_failures": food_failure,
                        "observed_food_injuries": food_injury,
                        "min_body": minima, "final_body": final["body"],
                        "terminal": final["terminal"], "terminal_tick": death,
                        "steps": final["revision"],
                        "right_censored": not final["terminal"]
                            and final["revision"] == 96,
                        "uc_spent": birth["remaining_uc"] -
                                    final["remaining_uc"],
                        "cold_audit": "PASS"}
            comparisons = {}
            for name, _ in WORLDS:
                off, on = name + "-learning-off", name + "-learning-on"
                self.assertEqual(births[off], births[on])
                a, b = timelines[off], timelines[on]
                first = next((i for i in range(min(len(a), len(b)))
                              if a[i]["action"] != b[i]["action"]), None)
                if first is not None:
                    self.assertEqual([x["action"] for x in a[:first]],
                                     [x["action"] for x in b[:first]])
                    self.assertEqual(a[first]["before"], b[first]["before"])
                comparisons[name] = {
                    "first_learning_motor_divergence": first+1
                        if first is not None else None,
                    "prior_food_contacts_at_first_divergence":
                        a[first]["prior_food_contacts"] if first is not None
                        else None,
                    "prior_food_injuries_at_first_divergence":
                        a[first]["prior_food_injuries"] if first is not None
                        else None,
                    "first_off": a[first] if first is not None else None,
                    "first_on": b[first] if first is not None else None,
                    "food_experience_identifiable_at_first_divergence":
                        (first is not None and
                         a[first]["prior_food_contacts"] > 0),
                }
            # Hidden adverse food physics cannot influence decisions before
            # the first actual admitted meal, for each learning flag.
            for learning in (False, True):
                suffix = "-learning-on" if learning else "-learning-off"
                a, b = (timelines["harmless"+suffix],
                        timelines["harmful"+suffix])
                first = next((i for i in range(min(len(a), len(b)))
                              if a[i]["after"] != b[i]["after"]), None)
                if first is not None:
                    self.assertEqual(a[first]["action"], "manger")
                    self.assertEqual(b[first]["action"], "manger")
                    self.assertEqual(a[first]["before"], b[first]["before"])
                    self.assertEqual([x["action"] for x in a[:first]],
                                     [x["action"] for x in b[:first]])
                comparisons["hidden_harm"+suffix] = {
                    "first_actual_physical_difference":
                        first+1 if first is not None else None,
                    "source_before_first_contact_unobserved":
                        first is not None or
                        not any(x["action"] == "manger" for x in a),
                }
            print("I2_P4_EXPLORATION_LEARNING_906=" + json.dumps(
                {"lives": report, "comparisons": comparisons},
                sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
