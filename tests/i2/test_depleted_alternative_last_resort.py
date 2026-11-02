"""Regression: a depleted lived rescue option precedes paid risky fallback.

Readout is researcher-only; no hidden payoff, injected motor act, new
survival threshold, or independent M11 claim. Uses the existing owner.
"""
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, EAT


class DepletedAlternativeLastResortTests(unittest.TestCase):
    def test_matching_prechoice_then_paid_fallback_with_both_hidden_outcomes(self):
        with tempfile.TemporaryDirectory(prefix="i2-rescue-transition-") as root:
            for world in ("adverse", "restoration"):
                arms = {}
                for label, last_resort in (("deadline", False), ("combined", True)):
                    life = IsolatedI2.create(
                        Path(root) / f"{world}-{label}.sqlite",
                        learning=True,
                        impulses=SCENARIOS[world] + (SCENARIOS[world][-1],) * 2,
                        extended_postcontact_study=True,
                        initial_energy=40, initial_uc=60, resources=8,
                        restorative_water_study=True, finite_water_capacity=1,
                        deadline_aware=True,
                        last_resort_exploration=last_resort,
                    )
                    execution = life.run_world(ticks=20)
                    arms[label] = (life.decision_evidence(), life.audit(), execution)
                baseline, baseline_audit, _ = arms["deadline"]
                chosen, chosen_audit, _ = arms["combined"]
                self.assertGreaterEqual(len(chosen), 9)
                self.assertGreaterEqual(len(baseline), 9)
                # Actual same lived history, not a researcher-matched fantasy.
                for earlier, comparison in zip(chosen[:8], baseline[:8]):
                    for field in (
                        "chosen", "before_energy", "energy_after",
                        "before_inventory", "before_resources",
                        "subjective_outcomes_available", "uc_spent",
                    ):
                        self.assertEqual(earlier[field], comparison[field],
                                         (world, field))
                self.assertEqual(chosen[7]["chosen"], DRINK)
                self.assertEqual(chosen[8]["physical_ticks_before"], 16)
                self.assertEqual(chosen[8]["before_energy"], 4)
                self.assertNotIn(DRINK, chosen[8]["visible"])
                self.assertEqual(chosen[8]["visible"], baseline[8]["visible"])
                self.assertEqual(chosen[8]["subjective_outcomes_available"],
                                 baseline[8]["subjective_outcomes_available"])
                self.assertEqual(chosen[8]["uc_before"], baseline[8]["uc_before"])
                self.assertGreater(chosen[8]["candidate_scores"][EAT], 0)
                # Last resort overrides a negative past food result only after
                # finite water was physically consumed and no longer offered.
                self.assertEqual([e["observed_net"] for e in chosen[8][
                    "outcomes_used_by_valuation"] if e["action"] == EAT], [-10])
                self.assertTrue(chosen[8]["last_resort_priority_applied"])
                self.assertTrue(chosen[8]["internal_admission"])
                self.assertEqual(chosen[8]["chosen"], EAT)
                self.assertNotEqual(baseline[8]["chosen"], EAT)
                self.assertGreater(chosen[8]["uc_spent"], 0)
                self.assertEqual(chosen_audit["water_remaining"], 0)
                self.assertEqual(baseline_audit["water_remaining"], 0)
                self.assertFalse(chosen_audit["m11_authenticated"])
                if world == "adverse":
                    self.assertTrue(chosen_audit["terminal"])
                    self.assertEqual(chosen[8]["energy_after"], 0)
                else:
                    self.assertFalse(chosen_audit["terminal"])
                    self.assertGreater(chosen[8]["energy_after"], 0)
                    # Newly favorable payoff belongs to the NEXT capture.
                    self.assertTrue(any(
                        event["action"] == EAT and event["observed_net"] > 0
                        for event in chosen[9]["subjective_outcomes_available"]
                    ))


if __name__ == "__main__":
    unittest.main()
