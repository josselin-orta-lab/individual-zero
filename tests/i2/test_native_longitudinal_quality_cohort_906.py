"""Predeclared 32-tick native life cohort; report long-term traces honestly.

Source quality is world-locked at birth and never available to cognition
before a real, paid drink. This is a descriptive longitudinal engineering
study, NOT a positive-learning or survival claim.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body
from i2.runtime.native_paid_cycle import NativePaidI2, actual_old_water_gain


def _paid_scores_by_action(event):
    """Read the *paid* opinions without confusing per-life candidate refs."""
    if event["frame"] is None or event["advice"] is None:
        return {}
    semantics = {
        candidate["candidate_ref"]: candidate["semantic_ref"]
        for candidate in event["frame"]["candidates"]
    }
    return {
        semantics[entry["candidate_ref"]]: entry["value"]
        for entry in event["advice"]["values"]
    }


def _post_reversal_status(change_at, post_drinks):
    """World truth is a retrospective label, never an input to I2 cognition."""
    if change_at == 0:
        return "NO_REVERSAL"
    return "PHYSICALLY_OBSERVED" if post_drinks else "UNOBSERVED_CENSORED"



class NativeLongitudinalQualityCohort(unittest.TestCase):
    BODY = Body(85, 90, 35, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)
    STEPS = 32
    CHANGE_AT = 12
    # External worlds differ only by their physically realized water effect.
    WORLDS = (
        ("always_empty", 0.0, 0, 0.0),
        ("becomes_useful", 0.0, CHANGE_AT, 20.0),
        ("becomes_empty", 20.0, CHANGE_AT, 0.0),
        ("always_useful", 20.0, 0, 0.0),
    )

    def test_repeated_exposure_has_only_actually_experienced_quality(self):
        with tempfile.TemporaryDirectory() as directory:
            report = {}
            captures = {}
            runs = {}
            pair_readout = {}
            for name, initial_gain, change_at, later_gain in self.WORLDS:
                for learning in (False, True):
                    with self.subTest(world=name, learning=learning):
                        path = Path(directory) / (name + "-" + str(learning) + ".sqlite")
                        born_world = {
                            "drink_water_gain": initial_gain,
                            "water_quality_change_at": change_at,
                            "water_quality_after_gain": later_gain,
                        }
                        life = NativePaidI2.create(
                            path, body=self.BODY, temperament=self.TRAITS,
                            learning=learning, sleep_consolidation=False,
                            max_steps=self.STEPS, uc=1000, food_stock=0,
                            water_stock=1, water_restock_every=2,
                            discovered_water_gain=0,
                            **born_world)
                        birth = life.audit()
                        self.assertEqual(birth["max_steps"], self.STEPS)
                        for step in range(self.STEPS):
                            snapshot = life.step()
                            self.assertEqual(snapshot["revision"], step + 1)
                            self.assertFalse(snapshot["terminal"])
                        final = life.audit()
                        self.assertEqual(NativePaidI2.inspect(path).audit(), final)
                        with sqlite3.connect(path) as db:
                            events = [json.loads(r[0]) for r in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            physical = [tuple(r) for r in db.execute(
                                "SELECT admitted_action,before_json,after_json "
                                "FROM native_physical_events ORDER BY seq")]
                        self.assertEqual(len(events), self.STEPS)
                        self.assertEqual(len(physical), self.STEPS)
                        captures[(name, learning)] = tuple(
                            events[0]["claim"]["capture"]["accessible_semantics"])
                        self.assertIn("boire", captures[(name, learning)])
                        self.assertIn("collecter", captures[(name, learning)])
                        self.assertNotIn(
                            "boire_decouverte", captures[(name, learning)])
                        self.assertEqual(birth["body"], self.BODY.as_dict())
                        self.assertEqual(birth["temperament"],
                                         self.TRAITS.as_dict())
                        self.assertLess(final["remaining_uc"], 1000)
                        self.assertFalse(final["m11_authenticated"])
                        self.assertFalse(final["engine_registered"])
                        pre_drinks, post_drinks = [], []
                        for i, (event, record) in enumerate(
                                zip(events, physical)):
                            action, before_text, after_text = record
                            before = json.loads(before_text)
                            after = json.loads(after_text)
                            # The actual physical engine, not a subjective
                            # predicted reward, owns every outcome.
                            gain = (actual_old_water_gain(born_world, i)
                                    if action == "boire" else 0)
                            expected_water = min(
                                100.0, max(0.0, before["water"] - 0.4) + gain)
                            self.assertAlmostEqual(
                                after["water"], expected_water, places=6)
                            refs = event["claim"]["subjective_evidence_refs"]
                            self.assertFalse(any(
                                "water-quality" in ref for ref in refs))
                            self.assertFalse(any(
                                "water-found" in ref for ref in refs))
                            for epoch in range(2, self.STEPS + 1, 2):
                                marker = (
                                    "evidence:i2:native:water-offer-refilled:" +
                                    str(epoch))
                                self.assertEqual(marker in refs, i >= epoch)
                            if action == "boire":
                                (pre_drinks if i < self.CHANGE_AT
                                 else post_drinks).append({
                                    "step": i + 1,
                                    "actual_gain": gain,
                                    "net_water_delta": round(
                                        after["water"] - before["water"], 4),
                                })
                        self.assertEqual(final["revision"], self.STEPS)
                        report[name + (":learned" if learning else ":innate")] = {
                            "water": round(final["body"]["water"], 4),
                            "terminal": final["terminal"],
                            "uc_spent": birth["remaining_uc"] -
                                        final["remaining_uc"],
                            "pre_drinks": pre_drinks,
                            "post_drinks": post_drinks,
                            "actions": [r[0] for r in physical],
                            "cold_audit": "passed",
                            "no_motor_ticks": sum(
                                row[0] == "NO_ACTION" for row in physical),
                            "post_reversal_status": _post_reversal_status(
                                change_at, post_drinks),
                        }
                        runs[(name, learning)] = (physical, events)
                self.assertEqual(captures[(name, True)],
                                 captures[(name, False)])
                innate_physical, innate_events = runs[(name, False)]
                learned_physical, learned_events = runs[(name, True)]
                first_difference = next(
                    (i for i, (native, learned) in enumerate(
                        zip(innate_physical, learned_physical))
                     if native[0] != learned[0]), None)
                attribution = {
                    "first_action_divergence_step": (
                        first_difference + 1 if first_difference is not None
                        else None),
                    "matched_physical_prefix_ticks": (
                        first_difference if first_difference is not None
                        else self.STEPS),
                }
                if first_difference is not None:
                    # A decision divergence is meaningful only if both
                    # independently born individuals had identical physical
                    # outcomes and the same accessible facts beforehand.
                    self.assertEqual(
                        innate_physical[:first_difference],
                        learned_physical[:first_difference])
                    self.assertEqual(
                        innate_physical[first_difference][1],
                        learned_physical[first_difference][1])
                    native_claim = innate_events[first_difference]["claim"]
                    learned_claim = learned_events[first_difference]["claim"]
                    self.assertEqual(
                        native_claim["capture"]["accessible_semantics"],
                        learned_claim["capture"]["accessible_semantics"])
                    self.assertEqual(
                        native_claim["subjective_evidence_refs"],
                        learned_claim["subjective_evidence_refs"])
                    previous_drinks = [
                        record for record in innate_physical[:first_difference]
                        if record[0] == "boire"
                    ]
                    prior_restorations = sum(
                        json.loads(record[2])["water"] >
                        json.loads(record[1])["water"]
                        for record in previous_drinks)
                    attribution.update({
                        "previous_personal_drinks": len(previous_drinks),
                        "previous_restoring_drinks": prior_restorations,
                        "previous_nonrestoring_drinks": (
                            len(previous_drinks) - prior_restorations),
                        "innate_choice": innate_physical[first_difference][0],
                        "learned_choice": learned_physical[first_difference][0],
                        "innate_paid_scores": _paid_scores_by_action(
                            innate_events[first_difference]),
                        "learned_paid_scores": _paid_scores_by_action(
                            learned_events[first_difference]),
                        "same_observable_facts": True,
                    })
                pair_readout[name] = attribution
            # Changing a hidden outcome can NEVER change whether drinking
            # or exploring is physically offered at birth.
            self.assertEqual(len(set(captures.values())), 1)
            # This report is evidence to analyze, not a fixed motor tape
            # or a post hoc claim of learned success.
            print("I2_NATIVE_LONGITUDINAL_906=" +
                  json.dumps(report, sort_keys=True, separators=(",", ":")),
                  flush=True)
            print("I2_NATIVE_LONGITUDINAL_IDENTIFIABILITY_906=" +
                  json.dumps(pair_readout, sort_keys=True,
                             separators=(",", ":")), flush=True)

    def test_censored_reversal_is_not_labeled_as_learning(self):
        # An actual external change, without any subsequent chosen drink,
        # cannot appear as knowledge or as a demonstrated reappraisal.
        self.assertEqual(
            _post_reversal_status(12, []), "UNOBSERVED_CENSORED")
        self.assertEqual(
            _post_reversal_status(12, [{"step": 13, "actual_gain": 0.0}]),
            "PHYSICALLY_OBSERVED")
        self.assertEqual(
            _post_reversal_status(0, []), "NO_REVERSAL")


if __name__ == "__main__":
    unittest.main()
