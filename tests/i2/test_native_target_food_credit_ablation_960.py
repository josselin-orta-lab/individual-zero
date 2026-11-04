"""#960 born-locked food-target-only ablation, paid four-life P4 study.

No new reward formula or motor script. Negative outcomes and right-censoring
are meaningful evidence. All native decisions still pass paid Competition,
fresh Action Control, immutable genesis and independent cold replay.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import _json, current_evidence
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, PRIORS, innate_adjustment,
    personally_nonrestoring_action, personally_nonrestoring_scores,
)

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def claim(body):
    return ObservationClaim(
        "life:i2:p4:credit:probe",
        FirstPersonCapture(
            2, "capture:i2:p4:credit:probe", "goal:physical-needs",
            ("boire", "manger")),
        "source:i2:p4:credit:probe",
        tuple(sorted(current_evidence(body, TRAITS))))


def physical_row(seq, action, before, after):
    return (
        seq, "capture:i2:p4:credit:" + str(seq), action, 0.0,
        _json(before.as_dict()), _json(after.as_dict()), 0
    )


class NativeTargetFoodCreditAblation960(unittest.TestCase):
    def test_target_credit_only_and_other_need_are_unchanged(self):
        before = Body(85, 40, 40, 100)
        after = Body(84.5, 74.8, 39.6, 92)
        history = (physical_row(1, "manger", before, after),)
        original = {"manger": -12, "boire": 16}
        on, _, on_assoc = personally_nonrestoring_scores(
            original, claim=claim(before), body=before, traits=TRAITS,
            previous=history, learning=True,
            target_food_credit_enabled=True)
        off, _, off_assoc = personally_nonrestoring_scores(
            original, claim=claim(before), body=before, traits=TRAITS,
            previous=history, learning=True,
            target_food_credit_enabled=False)
        baseline = innate_adjustment(PRIORS, before, TRAITS)
        self.assertEqual(on["manger"], baseline["manger"] + 1)
        self.assertEqual(off["manger"], original["manger"])
        self.assertEqual(on["boire"], off["boire"])
        self.assertEqual(on["boire"], original["boire"])
        self.assertEqual(on_assoc, frozenset(("manger",)))
        self.assertEqual(off_assoc, frozenset())
        default, _, _ = personally_nonrestoring_scores(
            original, claim=claim(before), body=before, traits=TRAITS,
            previous=history, learning=True)
        self.assertEqual(default, on)
        for invalid in (0, 1, None, "false", []):
            with self.subTest(invalid=repr(invalid)):
                with self.assertRaises(NativeRefusal):
                    personally_nonrestoring_scores(
                        original, claim=claim(before), body=before,
                        traits=TRAITS, previous=history, learning=True,
                        target_food_credit_enabled=invalid)

    def test_critical_last_resort_independent_of_food_credit(self):
        critical = Body(85, 5, 75, 100)
        failed = (physical_row(1, "manger", Body(85, 5, 75, 100),
                               Body(84.5, 4.8, 74.6, 100)),
                  physical_row(2, "manger", Body(84.5, 4.8, 74.6, 100),
                               Body(84, 4.6, 74.2, 100)))
        self.assertTrue(personally_nonrestoring_action(
            body=critical, previous=failed, action="manger"))
        # The last-resort protection must operate even when the proposed
        # target-food memory overlay is disabled. No motor is generated here.
        for enabled in (False, True):
            values, discouraged, _ = personally_nonrestoring_scores(
                {"manger": 25, "boire": 4}, claim=claim(critical),
                body=critical, traits=TRAITS, previous=failed,
                learning=True, target_food_credit_enabled=enabled)
            self.assertIn("manger", discouraged)
            self.assertLessEqual(values["manger"], 0)

    def test_born_bool_digest_and_default_parity(self):
        with tempfile.TemporaryDirectory() as folder:
            for i, invalid in enumerate((0, 1, None, "false", 1.5)):
                with self.subTest(invalid=repr(invalid)):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(folder) / ("bad" + str(i) + ".sqlite"),
                            body=BODY, temperament=TRAITS,
                            target_food_credit_enabled=invalid)
            for label, flag in (("default", None), ("on", True), ("off", False)):
                path = Path(folder) / (label + ".sqlite")
                opts = {} if flag is None else {
                    "target_food_credit_enabled": flag}
                life = NativePaidI2.create(
                    path, body=BODY, temperament=TRAITS, max_steps=2,
                    uc=100, **opts)
                self.assertEqual(life.audit(), NativePaidI2.inspect(path).audit())
                with sqlite3.connect(path) as db:
                    saved = db.execute(
                        "SELECT target_food_credit_enabled FROM native_genesis "
                        "WHERE id=1").fetchone()[0]
                self.assertEqual(saved, int(flag is not False))
                if label == "off":
                    with sqlite3.connect(path) as db:
                        db.execute("UPDATE native_genesis "
                                   "SET target_food_credit_enabled=1")
                    with self.assertRaises(NativeRefusal):
                        life.audit()

    def test_paid_harmful_and_harmless_four_birth_ablation(self):
        results = {}
        born_laws = {}
        with tempfile.TemporaryDirectory() as folder:
            for harm in (-8., 0.):
                for credit in (False, True):
                    label = ("harm" if harm < 0 else "harmless") + (
                        "-credit-on" if credit else "-credit-off")
                    path = Path(folder) / (label + ".sqlite")
                    life = NativePaidI2.create(
                        path, body=BODY, temperament=TRAITS,
                        learning=True, target_food_credit_enabled=credit,
                        spatial_world=True, ordinary_food_site="passage",
                        ordinary_water_site="camp", food_stock=1,
                        water_stock=2, food_restock_every=8,
                        water_restock_every=8, uc=850, max_steps=64,
                        berry_food_gain=35., berry_integrity_delta=harm,
                        drink_water_gain=40., evidence_tie_exploration=False,
                        sleep_consolidation=False, place_return_tie=True,
                        purpose_followthrough=True,
                        contextual_movement_credit=True)
                    beginning = life.audit()
                    for _ in range(64):
                        result = life.step()
                        if result["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(final, NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        born_laws[label] = db.execute(
                            "SELECT body_json, traits_json, food_stock, water_stock,"
                            " ordinary_food_site, ordinary_water_site,"
                            " food_restock_every, water_restock_every,"
                            " berry_food_gain, drink_water_gain, max_steps"
                            " FROM native_genesis WHERE id=1").fetchone()
                        physical = db.execute(
                            "SELECT admitted_action, before_json, after_json,"
                            " net_physiological_relief FROM native_physical_events"
                            " ORDER BY seq").fetchall()
                        events = [json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    self.assertEqual(len(physical), len(events))
                    site = BORN_SITE
                    sites = [site]
                    offers, meals, all_actions, selected_paid = [], [], [], []
                    for tick, ((action, before, after, relief), event) in enumerate(
                            zip(physical, events), 1):
                        offered = event["claim"]["capture"][
                            "accessible_semantics"]
                        self.assertFalse(any(
                            "water-offer-refilled:" in evidence
                            for evidence in event["claim"][
                                "subjective_evidence_refs"]))
                        if "manger" in offered:
                            self.assertEqual(site, "passage")
                            offers.append(tick)
                        if action == "manger":
                            self.assertEqual(site, "passage")
                            self.assertIn("manger", offered)
                            old, new = json.loads(before), json.loads(after)
                            delta = new["food"] - old["food"]
                            meals.append({
                                "tick": tick, "food_before": old["food"],
                                "food_after": new["food"],
                                "integrity_before": old["integrity"],
                                "integrity_after": new["integrity"],
                                "realized_food_gain": round(delta, 3),
                                "low_gain": delta < 5,
                                "zero_gain": delta <= 0,
                                "net_relief": relief})
                        frame, advice = event.get("frame"), event.get("advice")
                        if frame and advice:
                            names = {c["candidate_ref"]: c["semantic_ref"]
                                     for c in frame["candidates"]}
                            paid = {names[v["candidate_ref"]]: {
                                "value": v["value"], "evidence": v["evidence_ref"]}
                                for v in advice["values"]}
                        else:
                            paid = {}
                        selected_paid.append({
                            "tick": tick, "action": action,
                            "body_before": json.loads(before),
                            "food_offer": "manger" in offered,
                            "paid_status": advice["status"] if advice else None,
                            "food_paid": paid.get("manger"),
                            "sleep_paid": paid.get("dormir")})
                        all_actions.append(action)
                        if destination(action) is not None:
                            site = site_after(site, action)
                        sites.append(site)
                    self.assertEqual(final["site"], site)
                    results[label] = {
                        "actions": all_actions, "sites": sites,
                        "food_offer_ticks": offers, "meals": meals,
                        "first_decisions": selected_paid[:4],
                        "food_decisions": [r for r in selected_paid
                                           if r["food_offer"]],
                        "final_body": final["body"],
                        "spent_uc": beginning["remaining_uc"] -
                                    final["remaining_uc"],
                        "terminal": final["terminal"],
                        "right_censored": final["revision"] == 64
                                          and not final["terminal"],
                        "cold_audit": "PASS"}
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    self.assertEqual(final["scientific_verdict"],
                                     "NOT_ESTABLISHED")
            for harm in ("harm", "harmless"):
                self.assertEqual(
                    born_laws[harm + "-credit-off"],
                    born_laws[harm + "-credit-on"])
            for credit in ("-credit-off", "-credit-on"):
                self.assertEqual(
                    born_laws["harm" + credit],
                    born_laws["harmless" + credit])
            for harm in ("harm", "harmless"):
                left, right = (results[harm + suffix]["actions"]
                               for suffix in ("-credit-off", "-credit-on"))
                first_difference = next(
                    (index + 1 for index, (x, y) in enumerate(zip(left, right))
                     if x != y), None)
                results[harm + "-credit-first-difference"] = first_difference
            print("I2_TARGET_FOOD_CREDIT_ABLATION_960=" +
                  json.dumps(results, sort_keys=True,
                             separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
