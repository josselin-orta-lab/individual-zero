"""#906: preregistered held-out-physics v22 six-life P4 cohort.

The independent six-life 2x3 cohort was frozen in GitHub issue #906 BEFORE
this source existed. No motor tape, no future stock/quality oracle, no new
cognition, no bootstrapped physiological memory and no favorable assertions.
Every life is independently born and cold replayed.
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
from i2.modules.native_spatial_world import BORN_SITE, GRAPH, destination, site_after
from i2.runtime.native_paid_cycle import NativePaidI2

BODY = Body(78, 46, 44, 94)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
WORLDS = (
    ("harm-passage", 0.0, -9.0),
    ("harm-source", -9.0, 0.0),
)


def paid_values(event):
    frame, advice = event.get("frame"), event.get("advice")
    if frame is None or advice is None:
        return {"status": None, "values": {}}
    names = {x["candidate_ref"]: x["semantic_ref"]
             for x in frame["candidates"]}
    return {"status": advice["status"],
            "values": {names[v["candidate_ref"]]: {
                "value": v["value"], "evidence": v["evidence_ref"]}
                for v in advice["values"]}}


class P4HeldoutWholeBodyPlace906(unittest.TestCase):
    def test_six_independently_born_paid_lives_no_script(self):
        reports, timelines, physical_births = {}, {}, {}
        with tempfile.TemporaryDirectory() as root:
            arms = (
                ("innate-only", False, False),
                ("target-only", True, False),
                ("whole-body", True, True),
            )
            for world, source_injury, passage_injury in WORLDS:
                for arm, learning, holistic in arms:
                    key = world + "-" + arm
                    path = Path(root) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=learning, whole_body_place_tie=holistic,
                        origin_novelty_tie=True,
                        target_food_credit_enabled=False,
                        contextual_movement_credit=False,
                        place_return_tie=True,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False,
                        purpose_followthrough=False,
                        spatial_world=True, ordinary_water_site="camp",
                        water_stock=2, water_restock_every=10,
                        drink_water_gain=35.0,
                        ordinary_food_site="source", food_stock=1,
                        food_restock_every=12, berry_food_gain=10.,
                        berry_integrity_delta=source_injury,
                        second_food_site="passage", second_food_stock=1,
                        second_food_restock_every=12,
                        second_berry_food_gain=10.,
                        second_berry_integrity_delta=passage_injury,
                        uc=1000, max_steps=128)
                    born = life.audit()
                    for _ in range(128):
                        if life.step()["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                    with sqlite3.connect(path) as db:
                        physical_births[key] = db.execute(
                            "SELECT body_json,traits_json,ordinary_water_site,"
                            "water_stock,water_restock_every,drink_water_gain,"
                            "ordinary_food_site,food_stock,food_restock_every,"
                            "berry_food_gain,berry_integrity_delta,"
                            "second_food_site,second_food_stock,"
                            "second_food_restock_every,second_berry_food_gain,"
                            "second_berry_integrity_delta,max_steps,"
                            "origin_novelty_tie,target_food_credit_enabled,"
                            "contextual_movement_credit FROM native_genesis"
                        ).fetchone()
                        rows = db.execute(
                            "SELECT admitted_action,before_json,after_json,terminal "
                            "FROM native_physical_events ORDER BY seq").fetchall()
                        events = [json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(rows), len(events))
                    self.assertEqual(len(rows), final["revision"])
                    site = BORN_SITE
                    sites = [site]
                    actions = []
                    meals, food_offers, water_offers = [], [], []
                    evidence_ticks, action_frames = [], []
                    known_sites = {site}
                    first_harm = None
                    hunger_at_safe_offers = []
                    min_body = dict(born["body"])
                    death = None
                    trace = []
                    for tick, ((action, before, after, terminal), event) in enumerate(
                            zip(rows, events), 1):
                        pre, post = json.loads(before), json.loads(after)
                        offers = event["claim"]["capture"]["accessible_semantics"]
                        paid = paid_values(event)
                        if any(":lived-whole-body-site-need-relevance" in
                               value["evidence"]
                               for value in paid["values"].values()):
                            evidence_ticks.append(tick)
                        if not holistic:
                            self.assertFalse(any(
                                ":lived-whole-body-site-need-relevance" in
                                value["evidence"]
                                for value in paid["values"].values()))
                        self.assertTrue(set(offers).issubset(
                            {"manger", "boire", "boire_decouverte",
                             "collecter", "dormir", "attendre",
                             "se_deplacer_vers_camp",
                             "se_deplacer_vers_passage",
                             "se_deplacer_vers_source"}))
                        if "manger" in offers:
                            self.assertIn(site, ("passage", "source"))
                            food_offers.append({"tick": tick, "site": site})
                            if site == ("source" if source_injury == 0 else "passage"):
                                hunger_at_safe_offers.append({
                                    "tick": tick, "food_before": pre["food"],
                                    "food_below_setpoint": pre["food"] < 70,
                                    "after_personal_injury": first_harm is not None,
                                    "action": action})
                        if "boire" in offers:
                            self.assertEqual(site, "camp")
                            water_offers.append(tick)
                        if action == "manger":
                            self.assertIn(site, ("source", "passage"))
                            self.assertIn("manger", offers)
                            injury = post["integrity"] - pre["integrity"]
                            gain = post["food"] - pre["food"]
                            expected_injury = (
                                source_injury if site == "source"
                                else passage_injury)
                            # Full integrity starts <=100 and can only
                            # saturate an injury at 0; no future site effect
                            # may leak into a prior meal.
                            self.assertLessEqual(injury, 0)
                            self.assertGreaterEqual(gain, 0)
                            if expected_injury == 0:
                                self.assertEqual(injury, 0)
                            meals.append({
                                "tick": tick, "site": site,
                                "gain": round(gain, 5),
                                "injury": round(injury, 5),
                                "true_harmful_site": expected_injury < 0})
                            if injury < 0 and first_harm is None:
                                first_harm = tick
                        if action == "boire":
                            self.assertEqual(site, "camp")
                            self.assertIn("boire", offers)
                        if destination(action) is not None:
                            self.assertIn(action, offers)
                            self.assertIn(destination(action), GRAPH[site])
                        if action == "NO_ACTION":
                            self.assertLessEqual(post["food"], pre["food"])
                            self.assertLessEqual(post["water"], pre["water"])
                        preceding_meals = len(meals) - int(action == "manger")
                        preceding_harm = sum(m["injury"] < 0 for m in meals[:-1]
                                             if action == "manger") if (
                                                 action == "manger") else sum(
                                                 m["injury"] < 0 for m in meals)
                        trace.append({
                            "tick": tick, "site": site, "action": action,
                            "before": pre, "after": post,
                            "offered_food": "manger" in offers,
                            "prior_meals": preceding_meals,
                            "prior_harmful_meals": preceding_harm,
                            "known_sites_before": sorted(known_sites),
                            "paid": paid,
                        })
                        for channel in min_body:
                            min_body[channel] = min(min_body[channel], post[channel])
                        if terminal:
                            self.assertIsNone(death)
                            self.assertEqual(tick, len(rows))
                            death = tick
                        actions.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                            known_sites.add(site)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    self.assertEqual(final["terminal"], death is not None)
                    safe_site = ("source" if source_injury == 0 else "passage")
                    harmful_site = ("source" if source_injury < 0 else "passage")
                    first_safe_after_harm = next(
                        (m["tick"] for m in meals
                         if m["site"] == safe_site and
                         first_harm is not None and m["tick"] > first_harm),
                        None)
                    # Researcher's physical alternative feasibility at a
                    # given time is distinct from subjective discovery.
                    # Both food sites are reachable in this fixed world;
                    # food offers are measured only where the life goes.
                    known_safe_before_harm = (
                        safe_site in trace[first_harm - 1]["known_sites_before"]
                        if first_harm is not None else None)
                    reports[key] = {
                        "steps": final["revision"], "terminal": final["terminal"],
                        "death_tick": death,
                        "right_censored": not final["terminal"]
                            and final["revision"] == 128,
                        "actions": actions, "sites": sites,
                        "visited_sites": sorted(known_sites),
                        "food_offers": food_offers,
                        "safe_food_offers_with_hunger": [
                            v for v in hunger_at_safe_offers
                            if v["food_below_setpoint"]],
                        "safe_food_offers_after_harm_with_hunger": [
                            v for v in hunger_at_safe_offers
                            if v["food_below_setpoint"] and
                            v["after_personal_injury"]],
                        "water_offer_ticks": water_offers,
                        "whole_body_paid_evidence_ticks": evidence_ticks,
                        "meals": meals, "first_harmful_meal": first_harm,
                        "harmful_site": harmful_site, "safe_site": safe_site,
                        "safe_site_personally_visited_before_first_harm":
                            known_safe_before_harm,
                        "first_safe_meal_after_personal_harm":
                            first_safe_after_harm,
                        "no_alternative_exposure": not any(
                            m["site"] == safe_site for m in meals),
                        "final_body": final["body"], "min_body": min_body,
                        "uc_spent": born["remaining_uc"] - final["remaining_uc"],
                        "cold_audit": "PASS"}
                    timelines[key] = trace
            comparisons = {}
            for world, _, _ in WORLDS:
                keys = {
                    arm: world + "-" + arm for arm, _, _ in arms
                }
                for a_name, b_name in (
                    ("innate-only", "target-only"),
                    ("target-only", "whole-body"),
                    ("innate-only", "whole-body"),
                ):
                    key_a, key_b = keys[a_name], keys[b_name]
                    self.assertEqual(physical_births[key_a],
                                     physical_births[key_b])
                    a, b = timelines[key_a], timelines[key_b]
                    first = next(
                        (i for i in range(min(len(a), len(b)))
                         if a[i]["action"] != b[i]["action"]), None)
                    if first is not None:
                        self.assertEqual(
                            [x["action"] for x in a[:first]],
                            [x["action"] for x in b[:first]])
                        self.assertEqual(a[first]["before"],
                                         b[first]["before"])
                        self.assertEqual(a[first]["site"], b[first]["site"])
                    comparisons[world + ":" + a_name + ":vs:" + b_name] = {
                        "first_motor_divergence":
                            first + 1 if first is not None else None,
                        "first_a": a[first] if first is not None else None,
                        "first_b": b[first] if first is not None else None,
                        "prior_meals":
                            a[first]["prior_meals"] if first is not None else None,
                        "prior_harm":
                            a[first]["prior_harmful_meals"]
                            if first is not None else None,
                        "food_before":
                            a[first]["before"]["food"]
                            if first is not None else None,
                        "integrity_before":
                            a[first]["before"]["integrity"]
                            if first is not None else None,
                    }
            for arm, _, _ in arms:
                a = timelines["harm-passage-"+arm]
                b = timelines["harm-source-"+arm]
                first = next(
                    (i for i in range(min(len(a), len(b)))
                     if a[i]["after"] != b[i]["after"]), None)
                if first is not None:
                    self.assertEqual(a[first]["action"], "manger")
                    self.assertEqual(b[first]["action"], "manger")
                    self.assertEqual(a[first]["before"], b[first]["before"])
                    self.assertEqual([x["action"] for x in a[:first]],
                                     [x["action"] for x in b[:first]])
                comparisons["first_counterbalanced_harm-"+arm] = (
                    first + 1 if first is not None else None)
            print("I2_P4_HELDOUT_WHOLE_BODY_V22_906=" + json.dumps(
                {"lives": reports, "comparisons": comparisons},
                sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
