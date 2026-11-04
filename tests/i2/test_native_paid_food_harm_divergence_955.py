"""#955: paid native choice divergence under personally experienced food harm.

Research-only diagnostic: no change to scores, motor, body or safety.
Prepared after #953 observations; NOT held-out scientific confirmation.
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
    NativePaidI2, personally_observed_resource_outcomes,
)

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)
OBSERVATION_TICKS = (15, 16, 17, 25, 33, 34, 41, 49, 57)


class PaidFoodHarmDivergence955(unittest.TestCase):
    def test_independent_cold_paid_harm_divergence(self):
        data = {}
        with tempfile.TemporaryDirectory() as folder:
            for learning in (False, True):
                for harm in (-8.0, 0.0):
                    key = ("on" if learning else "off") + (
                        "-harm" if harm else "-harmless")
                    path = Path(folder) / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=learning, spatial_world=True,
                        ordinary_food_site="passage",
                        ordinary_water_site="camp", food_stock=1,
                        water_stock=2, food_restock_every=8,
                        water_restock_every=8, uc=850, max_steps=64,
                        berry_food_gain=35., berry_integrity_delta=harm,
                        drink_water_gain=40., evidence_tie_exploration=False,
                        sleep_consolidation=False,
                        place_return_tie=learning,
                        purpose_followthrough=learning,
                        contextual_movement_credit=learning)
                    first = life.audit()
                    for _ in range(64):
                        state = life.step()
                        if state["terminal"]:
                            break
                    last = life.audit()
                    self.assertEqual(last, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        physical = db.execute(
                            "SELECT admitted_action,before_json,after_json "
                            "FROM native_physical_events ORDER BY seq"
                        ).fetchall()
                        cognitive = [json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                        # Independent observational projection FROM the
                        # committed physical + cognitive journal, not a
                        # hypothetical food action or second life owner.
                        personal_history = life._rows(db)
                    self.assertEqual(len(physical), len(cognitive))
                    self.assertEqual(len(physical), len(personal_history))
                    site = BORN_SITE
                    summary = []
                    for tick, ((action, before, after), event) in enumerate(
                            zip(physical, cognitive), 1):
                        body_before = Body(**json.loads(before))
                        pressures = assess_needs(body_before, TRAITS).pressures
                        target_counts = personally_observed_resource_outcomes(
                            previous=personal_history[:tick - 1],
                            traits=TRAITS)["manger"]
                        offered = event["claim"]["capture"][
                            "accessible_semantics"]
                        if action == "manger":
                            self.assertEqual(site, "passage")
                            self.assertIn("manger", offered)
                        frame = event.get("frame")
                        advice = event.get("advice")
                        scored = {}
                        if frame and advice:
                            names = {
                                c["candidate_ref"]: c["semantic_ref"]
                                for c in frame["candidates"]}
                            scored = {
                                names[v["candidate_ref"]]: {
                                    "value": v["value"],
                                    "evidence_ref": v["evidence_ref"]}
                                for v in advice["values"]}
                        summary.append({
                            "tick": tick, "site": site, "action": action,
                            "food_before": body_before.food,
                            "integrity_before": body_before.integrity,
                            "need_food": round(pressures["food"], 4),
                            "need_integrity": round(
                                pressures["integrity"], 4),
                            "observed_food_successes": target_counts[0],
                            "observed_food_failures": target_counts[1],
                            "food_offered": "manger" in offered,
                            "paid_status": (
                                advice["status"] if advice else None),
                            "food_paid": scored.get("manger"),
                            "sleep_paid": scored.get("dormir"),
                            "water_paid": scored.get("boire"),
                        })
                        if destination(action) is not None:
                            site = site_after(site, action)
                    self.assertEqual(last["site"], site)
                    data[key] = {
                        "trace": summary,
                        "final_body": last["body"],
                        "spent_uc": first["remaining_uc"] -
                                    last["remaining_uc"],
                        "terminal": last["terminal"],
                        "right_censored": last["revision"] == 64
                            and not last["terminal"],
                        "cold_audit": "PASS"}
                    self.assertFalse(last["m11_authenticated"])
                    self.assertFalse(last["engine_registered"])
                    self.assertEqual(last["scientific_verdict"],
                                     "NOT_ESTABLISHED")
            report = {}
            for learning in (False, True):
                prefix = "on" if learning else "off"
                harmful = data[prefix + "-harm"]["trace"]
                harmless = data[prefix + "-harmless"]["trace"]
                count = min(len(harmful), len(harmless))
                motor_diff = next(
                    (tick for tick in range(count)
                     if harmful[tick]["action"] != harmless[tick]["action"]),
                    None)
                integrity_diff = next(
                    (tick for tick in range(count)
                     if harmful[tick]["integrity_before"] !=
                        harmless[tick]["integrity_before"]), None)
                index = sorted(set(
                    tick - 1 for tick in OBSERVATION_TICKS
                    if tick <= count
                ) | ({motor_diff} if motor_diff is not None else set()))
                report[prefix] = {
                    "first_motor_divergence_tick":
                        motor_diff + 1 if motor_diff is not None else None,
                    "first_body_integrity_divergence_before_tick":
                        integrity_diff + 1 if integrity_diff is not None
                        else None,
                    "paid_comparisons": [
                        {"harmful": harmful[t], "harmless": harmless[t]}
                        for t in index],
                    "harmful_terminal": data[prefix + "-harm"]["terminal"],
                    "harmless_terminal": data[prefix + "-harmless"]["terminal"],
                    "harmful_uc": data[prefix + "-harm"]["spent_uc"],
                    "harmless_uc": data[prefix + "-harmless"]["spent_uc"],
                    "cold_audits": ["PASS", "PASS"]
                }
            print("I2_PAID_FOOD_HARM_DIVERGENCE_955=" + json.dumps(
                report, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
