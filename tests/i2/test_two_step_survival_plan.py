"""No hidden-food oracle or free action in the two-step survival sketch."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.two_step_survival_plan import (
    COLLECT, EAT, assess_collect_then_eat,
)


def claim(energy, offered=(COLLECT,)):
    return ObservationClaim(
        "life:i2:twostep", FirstPersonCapture(
            10, "capture:i2:twostep", "goal:survive", tuple(sorted(offered))),
        "source:i2:twostep", (f"evidence:i2:energy:{energy}",),
    )


class TwoStepTests(unittest.TestCase):
    def test_sequenceable_does_not_claim_food_safe(self):
        result = assess_collect_then_eat(
            claim=claim(10), energy=10, inventory=0, resources=2)
        self.assertEqual(result.status, "PHYSICALLY_SEQUENCEABLE_OUTCOME_UNKNOWN")
        self.assertEqual(result.actions, (COLLECT, EAT))
        self.assertEqual(result.guaranteed_pre_food_energy, 8)
        self.assertEqual(result.food_outcome, "UNKNOWN")
        self.assertEqual(result.motor_authority, "NONE")

    def test_cost_can_make_second_step_terminal(self):
        result = assess_collect_then_eat(
            claim=claim(4), energy=4, inventory=0, resources=1)
        self.assertEqual(result.status, "FOOD_ATTEMPT_MAY_BE_TERMINAL")
        self.assertEqual(result.guaranteed_pre_food_energy, 2)

    def test_dead_before_collect_rejected(self):
        result = assess_collect_then_eat(
            claim=claim(2), energy=2, inventory=0, resources=1)
        self.assertEqual(result.status, "INSUFFICIENT_ENERGY_TO_COLLECT")

    def test_missing_resource_and_unobserved_energy_refused(self):
        self.assertEqual(assess_collect_then_eat(
            claim=claim(8, offered=()), energy=8, inventory=0, resources=0
        ).status, "FIRST_STEP_UNAVAILABLE")
        with self.assertRaises(ValueError):
            assess_collect_then_eat(
                claim=claim(8), energy=7, inventory=0, resources=1)


if __name__ == "__main__":
    unittest.main()
