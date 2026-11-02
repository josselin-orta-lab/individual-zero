"""Owner-authorized four-life short paid-world adaptation pilot (#886).

A descriptive adaptive behavior check with unchanged innate reflex in both
arms, not statistical or independent live-M11 evidence and not I1 comparison.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, DRINK, COLLECT, world_endpoint,
)


class ShortAdaptationPilot(unittest.TestCase):
    def test_locked_four_life_study(self):
        records = {}
        with tempfile.TemporaryDirectory(prefix="i2-adaptation-pilot-") as root:
            for restorative in (False, True):
                for learning in (False, True):
                    label = f"water-{int(restorative)}-learning-{int(learning)}"
                    life = IsolatedI2.create(
                        Path(root) / (label + ".sqlite"),
                        learning=learning,
                        impulses=SCENARIOS["adverse"],
                        initial_energy=6, initial_uc=60, resources=8,
                        restorative_water_study=restorative,
                        water_effect_blind=True, finite_water_capacity=2,
                        deadline_aware=True, last_resort_exploration=True)
                    run = life.run_world(ticks=4)
                    decisions = life.decision_evidence()
                    audit = life.audit()
                    endpoint = world_endpoint(run)
                    self.assertFalse(audit["m11_authenticated"])
                    self.assertEqual(audit["science"], "NOT_ESTABLISHED")
                    self.assertEqual(audit["physical_ticks"], len(run["trace"]))
                    self.assertLessEqual(sum(d["chosen"] == DRINK for d in decisions), 2)
                    self.assertTrue(all(d["uc_spent"] > 0 and
                                        d["internal_admission"]
                                        for d in decisions))
                    records[restorative, learning] = dict(
                        decisions=decisions, audit=audit, endpoint=endpoint,
                        trace=run["trace"])

            positive_fixed = records[True, False]
            positive_learned = records[True, True]
            first_fixed = positive_fixed["decisions"][0]
            first_learned = positive_learned["decisions"][0]
            self.assertEqual(first_fixed["chosen"], first_learned["chosen"])
            self.assertEqual(first_fixed["chosen"], DRINK)
            self.assertEqual(first_fixed["uc_spent"], first_learned["uc_spent"])

            matched_first_divergence = False
            if len(positive_fixed["decisions"]) >= 2 and len(positive_learned["decisions"]) >= 2:
                a, b = positive_fixed["decisions"][1], positive_learned["decisions"][1]
                matched_fields = (
                    "before_energy", "before_inventory", "before_resources",
                    "visible", "physical_ticks_before", "uc_before",
                    "subjective_outcomes_available", "uc_spent")
                matched_first_divergence = (all(a[k] == b[k] for k in matched_fields)
                    and a["chosen"] != b["chosen"]
                    and a["internal_admission"] and b["internal_admission"])
            self.assertTrue(all(x["survival_reflex"]["authority"] ==
                                "LOCAL_NON_MOTOR_ONLY"
                                for x in positive_fixed["decisions"] +
                                         positive_learned["decisions"]))
            self.assertEqual(positive_fixed["audit"]["actual_uc_spent"],
                             positive_learned["audit"]["actual_uc_spent"])
            self.assertEqual(records[False, False]["decisions"][0]["visible"],
                             records[True, False]["decisions"][0]["visible"])
            self.assertEqual(records[False, True]["decisions"][0]["visible"],
                             records[True, True]["decisions"][0]["visible"])
            delta = (positive_learned["audit"]["energy"] -
                     positive_fixed["audit"]["energy"])
            verdict = ("LOCAL_MODEL_ADAPTATION_OBSERVED"
                       if matched_first_divergence and delta > 0
                       else "NOT_OBSERVED")
            summary = {
                "protocol": "i2-short-adaptation-pilot-2026-11-02-v1",
                "fixed": {
                    "ticks": 4, "energy": 6, "uc": 60, "resources": 8,
                    "finite_water": 2, "water_effect_blind": True,
                    "deadline_aware": True, "innate_reflex": True,
                    "berry_world": "adverse"},
                "cases": [{
                    "water_restorative": w, "learning_enabled": l,
                    "first_person_choices": [d["chosen"] for d in records[w, l]["decisions"]],
                    "paid_uc": records[w, l]["audit"]["actual_uc_spent"],
                    "energy": records[w, l]["audit"]["energy"],
                    "death_tick": records[w, l]["endpoint"]["modeled_death_tick"],
                    "right_censored": records[w, l]["endpoint"]["right_censored"],
                    "water_remaining": records[w, l]["audit"]["water_remaining"],
                    "reflex_states": [d["survival_reflex"]["state"]
                                      for d in records[w, l]["decisions"]],
                    "world_reasons": [t["reason"] for t in records[w, l]["trace"]],
                } for w in (False, True) for l in (False, True)],
                "first_divergence_prechoice_matched": matched_first_divergence,
                "positive_water_energy_delta_learned_minus_fixed": delta,
                "verdict": verdict,
                "i2_greater_than_i1": "NOT_TESTED",
                "general_adaptation": "NOT_ESTABLISHED",
                "m11_authenticated": False,
            }
            print("I2_SHORT_ADAPTATION_PILOT_V1=" +
                  json.dumps(summary, sort_keys=True, separators=(",", ":")),
                  flush=True)
            # No claim that the pilot must be positive: a null result is data.
            self.assertEqual(len(records), 4)


if __name__ == "__main__":
    unittest.main()
