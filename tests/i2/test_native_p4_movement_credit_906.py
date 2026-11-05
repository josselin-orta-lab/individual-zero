"""P4 #906 preregistered after #972: source-locked movement-credit ablation.

No motor scripts, reward modifications or extra owner. Existing native v20
factor only; independently born paid lives, terminal/censor and cold replay.
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
WORLDS = (("harmless", 0.), ("harmful", -12.))


def paid(event):
    frame, advice = event.get("frame"), event.get("advice")
    if frame is None or advice is None:
        return {"status": None, "values": {}}
    names = {c["candidate_ref"]: c["semantic_ref"]
             for c in frame["candidates"]}
    return {"status": advice["status"], "values": {
        names[v["candidate_ref"]]: {
            "value": v["value"], "evidence": v["evidence_ref"]}
        for v in advice["values"]}}


class NativeP4MovementCredit906(unittest.TestCase):
    def test_four_source_locked_paid_born_lives(self):
        reports, lines, births = {}, {}, {}
        with tempfile.TemporaryDirectory() as root:
            for world, injury in WORLDS:
                for context in (False, True):
                    label = world + ("-isolated" if context else "-global")
                    path = Path(root) / (label + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=True, origin_novelty_tie=True,
                        target_food_credit_enabled=True,
                        contextual_movement_credit=context,
                        spatial_world=True, ordinary_food_site="source",
                        ordinary_water_site="camp",
                        food_stock=1, water_stock=2,
                        food_restock_every=8, water_restock_every=8,
                        berry_food_gain=35., berry_integrity_delta=injury,
                        drink_water_gain=40., uc=950, max_steps=96,
                        place_return_tie=False, purpose_followthrough=False,
                        sleep_consolidation=False,
                        evidence_tie_exploration=False)
                    begin = life.audit()
                    for _ in range(96):
                        if life.step()["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                    with sqlite3.connect(path) as db:
                        births[label] = db.execute(
                            "SELECT body_json,traits_json,food_stock,water_stock,"
                            "ordinary_food_site,ordinary_water_site,"
                            "food_restock_every,water_restock_every,"
                            "berry_food_gain,berry_integrity_delta,"
                            "drink_water_gain,max_steps,origin_novelty_tie,learning,"
                            "target_food_credit_enabled FROM native_genesis "
                            "WHERE id=1").fetchone()
                        rows = db.execute(
                            "SELECT admitted_action,before_json,after_json,terminal "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        events = [json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(rows), len(events))
                    actions, sites, site = [], [BORN_SITE], BORN_SITE
                    meals, drinks, offered_food, novelty, isolated_ticks = [], [], [], [], []
                    minima = dict(begin["body"])
                    timeline, death = [], None
                    for tick, ((action, before, after, terminal), event) in enumerate(
                            zip(rows, events), 1):
                        pre, post = json.loads(before), json.loads(after)
                        offered = event["claim"]["capture"]["accessible_semantics"]
                        values = paid(event)
                        if "manger" in offered:
                            self.assertEqual(site, "source")
                            offered_food.append(tick)
                        if action == "manger":
                            self.assertEqual(site, "source")
                            self.assertIn("manger", offered)
                            meals.append({
                                "tick": tick, "food_gain": round(
                                    post["food"] - pre["food"], 4),
                                "integrity_delta": round(
                                    post["integrity"] - pre["integrity"], 4)})
                        if action == "boire":
                            self.assertEqual(site, "camp")
                            self.assertIn("boire", offered)
                            drinks.append(tick)
                        if destination(action) is not None:
                            self.assertIn(action, offered)
                        if any(":visited-versus-unvisited-adjacent-tie" in
                               v["evidence"] for v in values["values"].values()):
                            novelty.append(tick)
                        if any(":movement-result-not-generalized-across-sites" in
                               v["evidence"] for v in values["values"].values()):
                            isolated_ticks.append(tick)
                        timeline.append({
                            "tick": tick, "site": site, "action": action,
                            "before": pre, "paid": values,
                            "prior_moves": sum(destination(a) is not None
                                               for a in actions),
                            "prior_meals": len(meals) - int(action == "manger")})
                        if terminal:
                            self.assertIsNone(death)
                            self.assertEqual(tick, len(rows))
                            death = tick
                        for name in minima:
                            minima[name] = min(minima[name], post[name])
                        actions.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    self.assertEqual(final["terminal"], death is not None)
                    if not context:
                        self.assertFalse(isolated_ticks)
                    lines[label] = timeline
                    reports[label] = {
                        "steps": final["revision"],
                        "terminal": final["terminal"], "terminal_tick": death,
                        "right_censored": final["revision"] == 96
                                          and not final["terminal"],
                        "actions": actions, "sites": sites,
                        "source_first_visit": next(
                            (t for t, s in enumerate(sites) if s == "source"), None),
                        "food_offer_ticks": offered_food,
                        "meals": meals, "drinks": drinks,
                        "novelty_paid_ticks": novelty,
                        "isolated_movement_paid_ticks": isolated_ticks,
                        "min_body": minima, "final_body": final["body"],
                        "uc_spent": begin["remaining_uc"] - final["remaining_uc"],
                        "cold_audit": "PASS"}
            comparisons = {}
            for world, _ in WORLDS:
                off, on = world + "-global", world + "-isolated"
                self.assertEqual(births[off], births[on])
                a, b = lines[off], lines[on]
                divergence = next((i for i in range(min(len(a), len(b)))
                                   if a[i]["action"] != b[i]["action"]), None)
                if divergence is not None:
                    self.assertEqual([x["action"] for x in a[:divergence]],
                                     [x["action"] for x in b[:divergence]])
                    self.assertEqual(a[divergence]["before"],
                                     b[divergence]["before"])
                comparisons[world] = {
                    "first_controlled_motor_difference":
                        divergence + 1 if divergence is not None else None,
                    "first_global": a[divergence] if divergence is not None else None,
                    "first_isolated": b[divergence] if divergence is not None else None,
                    "personal_food_before_first_difference":
                        a[divergence]["prior_meals"] if divergence is not None else None,
                    "personal_moves_before_first_difference":
                        a[divergence]["prior_moves"] if divergence is not None else None}
            for state in ("global", "isolated"):
                a, b = (lines["harmless-" + state],
                        lines["harmful-" + state])
                first = next((i for i in range(min(len(a), len(b)))
                              if a[i]["action"] == "manger" or
                                 b[i]["action"] == "manger"), None)
                if first is not None:
                    self.assertEqual([x["action"] for x in a[:first+1]],
                                     [x["action"] for x in b[:first+1]])
                    self.assertEqual(a[first]["before"], b[first]["before"])
                comparisons[state + "_first_physical_harm_contact"] = (
                    first+1 if first is not None else None)
            print("I2_P4_MOVEMENT_CREDIT_906=" + json.dumps(
                {"lives": reports, "comparisons": comparisons},
                sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
