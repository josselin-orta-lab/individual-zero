"""Prospectively frozen (#906) born-locked tie arbitration: four 12-tick lives.

The new-source actual quality is neither inferred nor communicated before
a motor act. Report negative choices, wasted UC, and absent discoveries.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    NativePaidI2, TIE_EXPLORATION_EVIDENCE, NO_ACTION,
)


def scores(event):
    if event["frame"] is None or event["advice"] is None:
        return {}
    by_ref = {c["candidate_ref"]: c["semantic_ref"]
              for c in event["frame"]["candidates"]}
    return {
        by_ref[v["candidate_ref"]]: {
            "value": v["value"], "provenance": v["evidence_ref"]
        } for v in event["advice"]["values"]
    }


class StableNovelSourceFalsifier906(unittest.TestCase):
    BODY = Body(85, 90, 35, 100)
    TRAITS = BirthTemperament(0, .5, .3, 0, 0)
    STEPS = 12

    def test_novelty_can_be_useless_and_never_predicts_quality(self):
        captures = {}
        reports = {}
        with tempfile.TemporaryDirectory() as directory:
            for gain in (0.0, 10.0):
                for enabled in (False, True):
                    label = ("useful" if gain else "useless") + (
                        ":tie-on" if enabled else ":tie-off")
                    with self.subTest(label=label):
                        path = Path(directory) / (label.replace(":", "-") + ".db")
                        life = NativePaidI2.create(
                            path, body=self.BODY, temperament=self.TRAITS,
                            learning=True, evidence_tie_exploration=enabled,
                            sleep_consolidation=False, max_steps=self.STEPS,
                            uc=300, food_stock=0, water_stock=8,
                            water_restock_every=0, drink_water_gain=0.0,
                            discovered_water_gain=gain,
                        )
                        born = life.audit()
                        for _ in range(self.STEPS):
                            result = life.step()
                            if result["terminal"]:
                                break
                        final = life.audit()
                        self.assertEqual(NativePaidI2.inspect(path).audit(), final)
                        self.assertLessEqual(final["revision"], self.STEPS)
                        self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                        self.assertFalse(final["engine_registered"])
                        self.assertFalse(final["m11_authenticated"])
                        with sqlite3.connect(path) as db:
                            decisions = [json.loads(row[0]) for row in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            physical = [tuple(row) for row in db.execute(
                                "SELECT admitted_action,before_json,after_json "
                                "FROM native_physical_events ORDER BY seq")]
                            found = [tuple(row) for row in db.execute(
                                "SELECT seq,found FROM native_discoveries ORDER BY seq")]
                        self.assertEqual(len(decisions), final["revision"])
                        self.assertEqual(len(physical), final["revision"])
                        self.assertEqual(
                            len(found),
                            sum(action == "collecter" for action, _, _ in physical))
                        for tick, (event, (action, before, after)) in enumerate(
                                zip(decisions, physical), start=1):
                            before, after = json.loads(before), json.loads(after)
                            self.assertFalse(any("water-quality" in e
                                for e in event["claim"]["subjective_evidence_refs"]))
                            if action == "boire":
                                self.assertAlmostEqual(
                                    after["water"], max(0, before["water"] - 0.4))
                            if action == "boire_decouverte":
                                self.assertTrue(any(
                                    step < tick and value for step, value in found))
                                self.assertAlmostEqual(after["water"],
                                    min(100, max(0, before["water"] - 0.4) + gain))
                        actions = [a for a, _, _ in physical]
                        sc = [scores(event) for event in decisions]
                        captures[(gain, enabled)] = (actions, physical, decisions, sc)
                        reports[label] = {
                            "ticks": final["revision"],
                            "censor": "TERMINAL" if final["terminal"] else
                                      "HORIZON_CENSORED",
                            "actions": actions,
                            "action_counts": dict(Counter(actions)),
                            "water_final": round(final["body"]["water"], 4),
                            "uc_spent": born["remaining_uc"] - final["remaining_uc"],
                            "first_collect": next(
                                (i for i, action in enumerate(actions, 1)
                                 if action == "collecter"), None),
                            "first_discovered_drink": next(
                                (i for i, action in enumerate(actions, 1)
                                 if action == "boire_decouverte"), None),
                            "found": found,
                            "third_paid": sc[2] if len(sc) > 2 else None,
                            "third_advice_status": (
                                decisions[2]["advice"]["status"]
                                if len(decisions) > 2 else None),
                            "cold_audit": "PASS",
                        }
            # Invisible site quality can never affect the initial choices
            # nor their competitive beliefs. Differences can arise only
            # after real exploration and subsequent physical exposure.
            for enabled in (False, True):
                bad = captures[(0.0, enabled)]
                good = captures[(10.0, enabled)]
                self.assertEqual(bad[0][:3], good[0][:3])
                for i in range(3):
                    self.assertEqual(
                        bad[2][i]["claim"]["subjective_evidence_refs"],
                        good[2][i]["claim"]["subjective_evidence_refs"])
                    self.assertEqual(
                        bad[2][i]["claim"]["capture"]["accessible_semantics"],
                        good[2][i]["claim"]["capture"]["accessible_semantics"])
                    self.assertEqual(
                        {k: v["value"] for k, v in bad[3][i].items()},
                        {k: v["value"] for k, v in good[3][i].items()})
            self.assertEqual(captures[(0.0, False)][0][2], NO_ACTION)
            self.assertEqual(captures[(10.0, False)][0][2], NO_ACTION)
            self.assertEqual(captures[(0.0, True)][0][2], "collecter")
            self.assertEqual(captures[(10.0, True)][0][2], "collecter")
            for gain in (0.0,10.0):
                third = captures[(gain,True)][3][2]
                self.assertIn(TIE_EXPLORATION_EVIDENCE,
                              third["collecter"]["provenance"])
                self.assertEqual(third["collecter"]["value"], 4)
            print("I2_NATIVE_STABLE_NOVELTY_FALSIFIER_906=" + json.dumps(
                reports, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
