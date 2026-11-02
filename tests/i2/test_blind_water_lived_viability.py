"""Blind water effect: viability must follow lived paid body changes, not genesis.

Fresh research identities use the current SQLite owner, with no motor
instruction and no independent M11 witness claim.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.runtime.isolated_prototype import (
    BLIND_WATER_EVIDENCE, RESTORATIVE_WATER_EVIDENCE,
    IsolatedI2, SCENARIOS, DRINK, _ToyPlanSource, PrototypeRefusal,
)


class LearnedWaterViabilityTests(unittest.TestCase):
    def test_blind_same_initial_claim_opposite_later_lived_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            arms = {}
            for restorative in (True, False):
                life = IsolatedI2.create(
                    Path(folder) / f"{restorative}.sqlite",
                    learning=True, impulses=SCENARIOS["adverse"],
                    initial_energy=4, initial_uc=60, resources=8,
                    last_resort_exploration=True, deadline_aware=True,
                    restorative_water_study=restorative,
                    finite_water_capacity=2, water_effect_blind=True,
                )
                meta, state, records = life._read()
                first = life._claim(
                    0, state["energy"], state["inventory"], state["resources"],
                    records, physical_ticks=0, restorative_water_study=restorative,
                    finite_water_capacity=2, water_effect_blind=True)
                self.assertIn(BLIND_WATER_EVIDENCE, first.subjective_evidence_refs)
                self.assertNotIn(RESTORATIVE_WATER_EVIDENCE,
                                 first.subjective_evidence_refs)
                reflex = LocalEnergySurvivalReflex(first, state["energy"])
                unknown = _ToyPlanSource(first, reflex)
                self.assertEqual(unknown._alternative_state(DRINK), "UNKNOWN")
                first_step = life.step()
                self.assertEqual(first_step.chosen, DRINK)
                self.assertGreater(first_step.actual_uc_spent, 0)
                meta, state, records = life._read()
                second = life._claim(
                    state["revision"], state["energy"], state["inventory"],
                    state["resources"], records,
                    physical_ticks=state["tick_count"],
                    restorative_water_study=restorative,
                    finite_water_capacity=2, water_effect_blind=True)
                reflex2 = LocalEnergySurvivalReflex(second, state["energy"])
                history = life._history(records)
                source = _ToyPlanSource(second, reflex2, history)
                self.assertEqual(
                    source._alternative_state(DRINK),
                    "VIABLE" if restorative else "UNKNOWN")
                self.assertEqual(
                    source._alternative_plan(DRINK).evidence_ref,
                    "evidence:i2:outcome:1")
                self.assertEqual(history[0].observed_net, 4 if restorative else -2)
                self.assertFalse(life.audit()["m11_authenticated"])
                arms[restorative] = (first.capture.accessible_semantics,
                                     first.subjective_evidence_refs)
            # Same subjective first-person evidence despite opposite hidden physics.
            self.assertEqual(arms[True], arms[False])

    def test_no_learning_ablation_does_not_inherit_a_plan_payoff(self):
        with tempfile.TemporaryDirectory() as folder:
            life = IsolatedI2.create(
                Path(folder) / "control.sqlite", learning=False,
                impulses=SCENARIOS["adverse"], initial_energy=4,
                restorative_water_study=True, finite_water_capacity=2,
                water_effect_blind=True, deadline_aware=True,
                last_resort_exploration=True)
            self.assertEqual(life.step().chosen, DRINK)
            meta, state, records = life._read()
            claim = life._claim(
                state["revision"], state["energy"], state["inventory"],
                state["resources"], records, physical_ticks=state["tick_count"],
                restorative_water_study=True, finite_water_capacity=2,
                water_effect_blind=True)
            reflex = LocalEnergySurvivalReflex(claim, state["energy"])
            self.assertEqual(
                _ToyPlanSource(claim, reflex, ())._alternative_state(DRINK),
                "UNKNOWN")
            self.assertEqual(life.audit()["revision"], 1)

    def test_blind_requires_finite_water_genesis(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(PrototypeRefusal):
                IsolatedI2.create(Path(folder) / "bad.sqlite",
                    learning=True, impulses=SCENARIOS["adverse"],
                    water_effect_blind=True)


if __name__ == "__main__":
    unittest.main()
