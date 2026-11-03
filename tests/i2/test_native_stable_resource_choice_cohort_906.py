"""Prospectively locked four-cell stable native I2 cohort (#906, ADR-0010).

Only actual paid autonomous action decisions are observed. Stable source
quality is never passed to cognition except through chosen consequences.
A negative result, censoring or no personally tried water is valid.
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
from i2.runtime.native_paid_cycle import NativePaidI2, NO_ACTION


def paid_values_by_action(event):
    frame, advice = event["frame"], event["advice"]
    if frame is None or advice is None:
        return {}
    meanings = {candidate["candidate_ref"]: candidate["semantic_ref"]
                for candidate in frame["candidates"]}
    return {
        meanings[value["candidate_ref"]]: {
            "value": value["value"], "evidence_ref": value["evidence_ref"]
        }
        for value in advice["values"]
    }


class StableResourceChoiceCohort906(unittest.TestCase):
    BODY = Body(85, 90, 35, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)
    TICKS = 24
    UC = 300
    WATER_STOCK = 8  # Explicit pre-execution feasibility amendment #906
    WORLDS = (("stable_useful", 10.0), ("stable_ineffective", 0.0))

    def test_stable_personal_efficacy_affects_actual_paid_choices_or_reports_null(self):
        paths = {}
        with tempfile.TemporaryDirectory() as directory:
            report = {}
            trials = {}
            for name, quality in self.WORLDS:
                for learning in (False, True):
                    key = name + (":learned" if learning else ":innate")
                    with self.subTest(cell=key):
                        path = Path(directory) / (key.replace(":", "_") + ".sqlite")
                        life = NativePaidI2.create(
                            path, body=self.BODY, temperament=self.TRAITS,
                            learning=learning, sleep_consolidation=False,
                            max_steps=self.TICKS, uc=self.UC,
                            food_stock=0, water_stock=self.WATER_STOCK,
                            water_restock_every=0, drink_water_gain=quality,
                            discovered_water_gain=10,
                        )
                        initial = life.audit()
                        self.assertEqual(initial["revision"], 0)
                        for tick in range(self.TICKS):
                            state = life.step()
                            if state["terminal"]:
                                break
                        final = life.audit()
                        self.assertEqual(NativePaidI2.inspect(path).audit(), final)
                        self.assertLessEqual(final["revision"], self.TICKS)
                        self.assertFalse(final["engine_registered"])
                        self.assertFalse(final["m11_authenticated"])
                        self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                        with sqlite3.connect(path) as db:
                            events = [json.loads(row[0]) for row in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            effects = [tuple(row) for row in db.execute(
                                "SELECT admitted_action,before_json,after_json "
                                "FROM native_physical_events ORDER BY seq")]
                            discoveries = [tuple(row) for row in db.execute(
                                "SELECT seq,found FROM native_discoveries ORDER BY seq")]
                        self.assertEqual(len(events), final["revision"])
                        self.assertEqual(len(effects), final["revision"])
                        self.assertEqual(
                            len(discoveries), sum(row[0] == "collecter" for row in effects))
                        personally_failed_drinks = 0
                        personally_restored_drinks = 0
                        encountered = []
                        after_failure_choices = []
                        for tick, (event, (action, before_json, after_json)) in enumerate(
                                zip(events, effects), start=1):
                            before, after = json.loads(before_json), json.loads(after_json)
                            self.assertFalse(any(
                                "water-quality" in ref
                                for ref in event["claim"]["subjective_evidence_refs"]))
                            if action == "boire":
                                expected = min(100.0, before["water"] - 0.4 + quality)
                                self.assertAlmostEqual(after["water"], expected, places=6)
                                if before["water"] < 70:
                                    if after["water"] > before["water"]:
                                        personally_restored_drinks += 1
                                    else:
                                        personally_failed_drinks += 1
                            if (action == "boire_decouverte" and
                                    not any(seq < tick and found
                                            for seq, found in discoveries)):
                                self.fail("a discovered source was used without discovery")
                            if personally_failed_drinks:
                                after_failure_choices.append(action)
                            encountered.append({
                                "tick": tick, "action": action,
                                "water_before": round(before["water"], 4),
                                "water_after": round(after["water"], 4),
                                "available": event["claim"]["capture"]["accessible_semantics"],
                                "paid_values": paid_values_by_action(event),
                            })
                        self.assertEqual(initial["body"], self.BODY.as_dict())
                        self.assertEqual(
                            initial["remaining_uc"] - final["remaining_uc"],
                            sum(
                                event["intake_uc"] + event["competition_uc"] +
                                event["control_uc"] for event in events))
                        outcome = {
                            "ticks": final["revision"],
                            "censor": "TERMINAL" if final["terminal"] else "HORIZON_CENSORED",
                            "water_final": round(final["body"]["water"], 4),
                            "uc_spent": initial["remaining_uc"] - final["remaining_uc"],
                            "nonrestoring_drinks": personally_failed_drinks,
                            "restoring_drinks": personally_restored_drinks,
                            "first_drink": next(
                                (r["tick"] for r in encountered
                                 if r["action"] == "boire"), None),
                            "actions": dict(Counter(row[0] for row in effects)),
                            "first_collect": next(
                                (r["tick"] for r in encountered
                                 if r["action"] == "collecter"), None),
                            "first_discovered_drink": next(
                                (r["tick"] for r in encountered
                                 if r["action"] == "boire_decouverte"), None),
                            "after_personal_failure_actions": dict(
                                Counter(after_failure_choices)),
                            "advice_after_first_failure": next(
                                (r["paid_values"] for idx, r in enumerate(encountered)
                                 if idx and effects[idx - 1][0] == "boire"
                                 and json.loads(effects[idx - 1][2])["water"] <=
                                     json.loads(effects[idx - 1][1])["water"]),
                                None),
                            "cold_audit": "PASS",
                        }
                        trials[(name, learning)] = (effects, events, encountered)
                        report[key] = outcome
            for name, _ in self.WORLDS:
                innate, innate_events, innate_history = trials[(name, False)]
                learned, learned_events, learned_history = trials[(name, True)]
                identical_prefix = 0
                for a, b in zip(innate, learned):
                    if a != b:
                        break
                    identical_prefix += 1
                first_div = (identical_prefix + 1
                             if identical_prefix < min(len(innate), len(learned))
                             else None)
                if first_div is not None:
                    i = first_div - 1
                    self.assertEqual(
                        innate_events[i]["claim"]["subjective_evidence_refs"],
                        learned_events[i]["claim"]["subjective_evidence_refs"])
                    self.assertEqual(
                        innate_events[i]["claim"]["capture"]["accessible_semantics"],
                        learned_events[i]["claim"]["capture"]["accessible_semantics"])
                    # Contrast must share actual predecision physical state.
                    self.assertEqual(innate[i][1], learned[i][1])
                report[":comparison:" + name] = {
                    "identical_physical_prefix": identical_prefix,
                    "first_motor_or_physical_divergence": first_div,
                    "first_divergence_paid_scores_innate": (
                        innate_history[first_div - 1]["paid_values"] if first_div else None),
                    "first_divergence_paid_scores_learned": (
                        learned_history[first_div - 1]["paid_values"] if first_div else None),
                    "verdict": (
                        "NO_BEHAVIORAL_DIFFERENCE" if first_div is None
                        else "DIVERGENT_ACTIONS_REQUIRE_CAUSAL_REVIEW"),
                }
            for learning in (False, True):
                good, _, _ = trials[("stable_useful", learning)]
                bad, _, _ = trials[("stable_ineffective", learning)]
                prefix = 0
                for a, b in zip(good, bad):
                    if a != b:
                        break
                    prefix += 1
                # An actually consumed resource is the first point where
                # two otherwise identical stable worlds can differ physically.
                if prefix < min(len(good), len(bad)):
                    self.assertEqual(good[prefix][0], "boire")
                    self.assertEqual(bad[prefix][0], "boire")
                report[":world_identifiability:" + str(learning)] = {
                    "identical_physical_prefix": prefix,
                    "first_quality_difference": (
                        prefix + 1 if prefix < min(len(good), len(bad)) else None),
                }
            print("I2_NATIVE_STABLE_RESOURCE_CHOICE_906=" + json.dumps(
                report, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
