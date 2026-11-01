"""I2 plan viability: source-verified alternative precedes risky last resort."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.unstable_world_reappraisal_contract import SurvivalReflexSnapshot
from i2.modules.survival_plan_viability import (
    PlanAssessment, assess_last_resort,
)


class Authority:
    def __init__(self, claim):
        self.claim = claim

    def verify(self, *, life_ref, claim, digest):
        return claim == self.claim and life_ref == claim.life_ref and digest == claim.digest()

    def verify_survival_reflex(self, *, claim, snapshot):
        return claim == self.claim and snapshot.claim_digest == claim.digest()

    def verify_plan(self, *, claim, plan):
        return claim == self.claim and plan.evidence_ref in claim.subjective_evidence_refs


class PlanViabilityTests(unittest.TestCase):
    def setUp(self):
        self.food = "affordance:eat:berry_a"
        self.safe = "affordance:drink:water"
        self.unknown = "affordance:collect:berry_a"
        self.claim = ObservationClaim(
            "life:i2:plans",
            FirstPersonCapture(
                31, "capture:i2:plans:31", "goal:survive",
                tuple(sorted((self.food, self.safe, self.unknown))),
            ),
            "source:i2:plans:31",
            tuple(sorted(("evidence:i2:energy:3", "evidence:i2:water",
                          "evidence:i2:collect"))),
        )
        self.source = Authority(self.claim)
        self.reflex = SurvivalReflexSnapshot(
            self.claim.life_ref, self.claim.capture.ref,
            self.claim.digest(), "evidence:i2:energy:3", "CONSTRAIN",
        )

    def assess(self, safe="NOT_VIABLE", collect="NOT_VIABLE", **kwargs):
        plans = tuple(sorted((
            PlanAssessment(self.safe, safe, "evidence:i2:water"),
            PlanAssessment(self.unknown, collect, "evidence:i2:collect"),
        ), key=lambda p: p.semantic_ref))
        return assess_last_resort(
            claim=self.claim, reflex=self.reflex, reflex_source=self.source,
            observation_source=self.source, plan_source=self.source,
            food_semantic_ref=self.food, plans=kwargs.get("plans", plans),
        )

    def test_no_other_accessible_viable_plan_triggers_risk(self):
        result = self.assess()
        self.assertEqual(result.status, "LAST_RESORT_RISK_RECONSIDERATION")
        self.assertEqual(result.motor_authority, "NONE")
        self.assertTrue(result.paid_competition_required)
        self.assertFalse(result.hidden_food_payoff_known)

    def test_viable_alternative_precedes_last_resort(self):
        self.assertEqual(self.assess(safe="VIABLE").status, "ALTERNATIVE_VIABLE")

    def test_unknown_alternative_cannot_be_assumed_impossible(self):
        result = self.assess(collect="UNKNOWN")
        self.assertEqual(result.status, "ALTERNATIVE_UNRESOLVED")
        self.assertEqual(result.unresolved_semantics, (self.unknown,))

    def test_reject_incomplete_or_fabricated_assessments(self):
        with self.assertRaises(ValueError):
            self.assess(plans=(PlanAssessment(self.safe, "NOT_VIABLE",
                                              "evidence:i2:water"),))
        with self.assertRaises(ValueError):
            self.assess(plans=(
                PlanAssessment(self.safe, "NOT_VIABLE", "evidence:i2:oracle"),
                PlanAssessment(self.unknown, "NOT_VIABLE", "evidence:i2:collect"),
            ))

    def test_normal_energy_does_not_trigger_emergency_priority(self):
        relaxed = SurvivalReflexSnapshot(
            self.claim.life_ref, self.claim.capture.ref,
            self.claim.digest(), "evidence:i2:energy:3", "NO_PREEMPTION",
        )
        plans = (
            PlanAssessment(self.unknown, "NOT_VIABLE", "evidence:i2:collect"),
            PlanAssessment(self.safe, "NOT_VIABLE", "evidence:i2:water"),
        )
        result = assess_last_resort(
            claim=self.claim, reflex=relaxed, reflex_source=self.source,
            observation_source=self.source, plan_source=self.source,
            food_semantic_ref=self.food, plans=plans,
        )
        self.assertEqual(result.status, "NO_EMERGENCY_PRIORITY")


if __name__ == "__main__":
    unittest.main()
