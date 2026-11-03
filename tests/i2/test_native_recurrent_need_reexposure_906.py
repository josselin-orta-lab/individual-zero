"""Predeclared recurrent-need native I2 pilot, no scripted motor actions.

A long continuous life can become thirsty again after the external source
changes quality. A reversal which is never sampled remains unobserved; do
not silently label a source as learned-bad. Research issue #906.
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
from i2.runtime.native_paid_cycle import NativePaidI2, actual_old_water_gain


class RecurrentNeedReexposure906(unittest.TestCase):
    MAX_STEPS = 96
    CHANGE_AT = 12
    BIRTH_BODY = Body(85, 90, 9, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)
    WORLD_CASES = (
        ("stable_useful", 0, 10.0),
        ("becomes_empty", CHANGE_AT, 0.0),
    )

    def test_natural_need_return_without_motor_script(self):
        # One lasting SQLite individual per cell, no copying/restarting
        # identities and no selection imposed by the experimental harness.
        with tempfile.TemporaryDirectory() as directory:
            reports = {}
            histories = {}
            for name, change_at, after_gain in self.WORLD_CASES:
                for learning in (False, True):
                    key = name + (":learned" if learning else ":innate")
                    with self.subTest(key=key):
                        path = Path(directory) / (key.replace(":", "-") + ".sqlite")
                        born_world = {
                            "drink_water_gain": 10.0,
                            "water_quality_change_at": change_at,
                            "water_quality_after_gain": after_gain,
                        }
                        life = NativePaidI2.create(
                            path,
                            body=self.BIRTH_BODY, temperament=self.TRAITS,
                            learning=learning, sleep_consolidation=False,
                            max_steps=self.MAX_STEPS, uc=1200,
                            food_stock=0, water_stock=1,
                            water_restock_every=2,
                            discovered_water_gain=0, **born_world,
                        )
                        first = life.audit()
                        for _ in range(self.MAX_STEPS):
                            status = life.step()
                            if status["terminal"]:
                                break
                        last = life.audit()
                        self.assertEqual(NativePaidI2.inspect(path).audit(), last)
                        with sqlite3.connect(path) as db:
                            decisions = [json.loads(row[0]) for row in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            physical = [tuple(row) for row in db.execute(
                                "SELECT admitted_action,before_json,after_json "
                                "FROM native_physical_events ORDER BY seq")]
                        self.assertEqual(len(decisions), len(physical))
                        self.assertEqual(len(physical), last["revision"])
                        self.assertLessEqual(last["revision"], self.MAX_STEPS)
                        self.assertLess(last["remaining_uc"], first["remaining_uc"])
                        self.assertFalse(last["m11_authenticated"])
                        self.assertFalse(last["engine_registered"])
                        self.assertEqual(last["scientific_verdict"], "NOT_ESTABLISHED")
                        postchange_drinks = []
                        critical_ticks = []
                        for tick, (event, (action, before_json, after_json)) in enumerate(
                                zip(decisions, physical), start=1):
                            before, after = json.loads(before_json), json.loads(after_json)
                            if before["water"] <= 10:
                                critical_ticks.append(tick)
                            actual = (actual_old_water_gain(born_world, tick - 1)
                                      if action == "boire" else 0.0)
                            self.assertAlmostEqual(
                                after["water"],
                                min(100.0, max(0.0, before["water"] - 0.4) + actual),
                                places=6)
                            # Source quality is never seen before drinking;
                            # motor decisions must remain endogenous and paid.
                            refs = event["claim"]["subjective_evidence_refs"]
                            self.assertFalse(any(
                                "water-quality" in ref for ref in refs))
                            if tick > self.CHANGE_AT and action == "boire":
                                postchange_drinks.append({
                                    "step": tick,
                                    "actual_gain": actual,
                                    "water_before": round(before["water"], 4),
                                    "water_after": round(after["water"], 4),
                                })
                        status = ("NO_REVERSAL" if change_at == 0 else
                                  ("PHYSICALLY_OBSERVED" if postchange_drinks
                                   else "UNOBSERVED_CENSORED"))
                        reports[key] = {
                            "executed_ticks": last["revision"],
                            "technical_limit": self.MAX_STEPS,
                            "terminal": last["terminal"],
                            "terminal_or_horizon_censored": (
                                "TERMINAL" if last["terminal"] else "HORIZON_CENSORED"),
                            "first_critical_water_tick": (
                                critical_ticks[0] if critical_ticks else None),
                            "first_postchange_drink_tick": (
                                postchange_drinks[0]["step"]
                                if postchange_drinks else None),
                            "postchange_drinks": postchange_drinks,
                            "postchange_exposure": status,
                            "final_water": round(last["body"]["water"], 4),
                            "uc_spent": first["remaining_uc"] - last["remaining_uc"],
                            "motor_actions": [r[0] for r in physical],
                            "cold_audit": "passed",
                        }
                        histories[(name, learning)] = (physical, decisions)
            for learning in (False, True):
                stable, stable_events = histories[("stable_useful", learning)]
                reversed_world, reversed_events = histories[("becomes_empty", learning)]
                # Two worlds are physically and informationally identical
                # until a chosen drink *after* the external quality reversal.
                same_prefix = 0
                for idx, (a, b) in enumerate(zip(stable, reversed_world)):
                    if a != b:
                        break
                    same_prefix = idx + 1
                for idx in range(same_prefix):
                    self.assertEqual(
                        stable_events[idx]["claim"]["capture"]["accessible_semantics"],
                        reversed_events[idx]["claim"]["capture"]["accessible_semantics"])
                    self.assertEqual(
                        stable_events[idx]["claim"]["subjective_evidence_refs"],
                        reversed_events[idx]["claim"]["subjective_evidence_refs"])
                first_difference = same_prefix + 1 if (
                    same_prefix < min(len(stable), len(reversed_world))) else None
                if first_difference is not None:
                    # World differences must first arise at an actual motor
                    # contact after the reversal, never from foresight.
                    self.assertGreater(first_difference, self.CHANGE_AT)
                    self.assertEqual(stable[first_difference - 1][0], "boire")
                    self.assertEqual(reversed_world[first_difference - 1][0], "boire")
                reports[":control_check:" + str(learning)] = {
                    "identical_committed_prefix": same_prefix,
                    "first_physical_world_difference": first_difference,
                }
            print("I2_NATIVE_RECURRENT_NEED_906=" + json.dumps(
                reports, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
