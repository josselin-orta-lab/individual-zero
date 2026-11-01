"""ADR-0006: an observable bodily scalar is not yet a motivation mechanism.

Frozen pre-implementation issue #662 comment 6560453473; no new policy.
Neutral model, initial energy 17 or 60, 60 synthetic UC, both fixed and
chosen-only observational modes, same hypothetical identity for direct
counterfactual comparisons only (not two independent births).
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.lab.integrated_loop import IntegratedLab, REGIMES, EAT  # noqa: E402


def one_energy_history(*, initial_energy: int, learning: bool) -> tuple:
    with tempfile.TemporaryDirectory(prefix="g1lab-energy-null-") as d:
        path = Path(d) / "disposable.sqlite"
        lab = IntegratedLab.create(
            path, life_ref="lab:energy:counterfactual",
            genesis_ref="lab:energy:mock-genesis", learning=learning,
            deltas=REGIMES["neutral"], initial_uc=60,
            initial_energy=initial_energy, revisit=False,
        )
        steps = []
        for _ in REGIMES["neutral"]:
            result = lab.step()
            steps.append(result)
            if result.terminal:
                break
        audit = lab.audit()
        with sqlite3.connect(path) as db:
            events = [
                json.loads(row[0]) for row in db.execute(
                    "SELECT event_json FROM events ORDER BY seq"
                )
            ]
        return steps, events, audit


class EnergyObservationDoesNotImplyDrive(unittest.TestCase):
    def test_energy_evidence_varies_but_actions_do_not(self):
        for learning in (False, True):
            with self.subTest(learning=learning):
                low, low_events, low_audit = one_energy_history(
                    initial_energy=17, learning=learning,
                )
                high, high_events, high_audit = one_energy_history(
                    initial_energy=60, learning=learning,
                )
                self.assertEqual(len(low), 8)
                self.assertEqual(len(high), 8)
                self.assertFalse(low[-1].terminal)
                self.assertFalse(high[-1].terminal)
                self.assertEqual([s.chosen for s in low],
                                 [s.chosen for s in high])
                self.assertEqual([s.visible for s in low],
                                 [s.visible for s in high])
                self.assertEqual([s.result_net for s in low],
                                 [s.result_net for s in high])
                self.assertEqual([s.uc_spent for s in low],
                                 [s.uc_spent for s in high])
                self.assertEqual(low_audit["actual_synthetic_uc_spent"],
                                 high_audit["actual_synthetic_uc_spent"])
                self.assertEqual(low_audit["motor_authority"], "NONE")
                self.assertFalse(low_audit["m11_authenticated"])
                self.assertNotEqual(low_events, high_events)
                for i, (left, right) in enumerate(zip(low_events, high_events)):
                    before_low = 17 if i == 0 else low[i-1].energy
                    before_high = 60 if i == 0 else high[i-1].energy
                    self.assertIn(
                        f"evidence:lab:body-energy:{before_low}",
                        left["claim"]["subjective_evidence_refs"],
                    )
                    self.assertIn(
                        f"evidence:lab:body-energy:{before_high}",
                        right["claim"]["subjective_evidence_refs"],
                    )
                    self.assertNotEqual(before_low, before_high)
                self.assertEqual(low[-1].energy, 1)
                self.assertEqual(high[-1].energy, 44)

    def test_aversive_cost_and_nutrition_are_not_distinct_observables(self):
        # A scientific construct limitation, not evidence about animal
        # physiology: observed chosen-result has one net scalar.
        from dataclasses import fields
        from i2.modules.chosen_outcome_study import ObservedChosenResult
        names = {field.name for field in fields(ObservedChosenResult)}
        self.assertIn("observed_net", names)
        self.assertNotIn("aversive_cost", names)
        self.assertNotIn("nutrient_gain", names)
        self.assertNotIn("social_observation", names)


if __name__ == "__main__":
    unittest.main()
