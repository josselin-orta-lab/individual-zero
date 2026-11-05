"""Owner-bound alternative-plan evidence, without an invented world oracle."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, EAT, DRINK, _ToyPlanSource,
)
from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.survival_plan_viability import PlanAssessment


class OwnerBoundPlans(unittest.TestCase):
    def test_existing_physical_world_has_only_food_as_immediate_energy_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            i2 = IsolatedI2.create(
                Path(folder) / "subject.sqlite", learning=True,
                impulses=SCENARIOS["adverse"], initial_energy=8,
                last_resort_exploration=True)
            self.assertEqual(i2.step().chosen, COLLECT)
            i2.advance_physics()
            i2.advance_physics()
            _, body, rows = i2._read()
            claim = i2._claim(body["revision"], body["energy"],
                              body["inventory"], body["resources"], rows,
                              physical_ticks=body["tick_count"])
            reflex = LocalEnergySurvivalReflex(claim, body["energy"])
            source = _ToyPlanSource(claim, reflex)
            self.assertEqual(source.priority(), EAT)
            self.assertTrue(source.verify_plan(
                claim=claim, plan=PlanAssessment(
                    DRINK, "NOT_VIABLE", reflex.evidence_ref)))
            self.assertFalse(source.verify_plan(
                claim=claim, plan=PlanAssessment(
                    DRINK, "VIABLE", reflex.evidence_ref)))
            self.assertEqual(i2.step().chosen, EAT)

    def test_unknown_action_blocks_claim_of_only_remaining_plan(self):
        semantics = tuple(sorted((EAT, "affordance:unknown:rescue")))
        claim = ObservationClaim(
            "life:i2:unknown", FirstPersonCapture(
                10, "capture:i2:unknown:10", "goal:survive", semantics),
            "source:i2:unknown:10", ("evidence:i2:energy:3",))
        reflex = LocalEnergySurvivalReflex(claim, 3)
        source = _ToyPlanSource(claim, reflex)
        self.assertIsNone(source.priority())
        self.assertFalse(source.verify_plan(
            claim=claim, plan=PlanAssessment(
                "affordance:unknown:rescue", "NOT_VIABLE",
                reflex.evidence_ref)))


if __name__ == "__main__":
    unittest.main()
