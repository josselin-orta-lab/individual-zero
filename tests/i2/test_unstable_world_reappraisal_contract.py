"""Contract-only I2 unstable-world reappraisal boundary tests."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.chosen_outcome_study import ObservedChosenResult
from i2.modules.unstable_world_reappraisal_contract import (
    CONTRACT, SurvivalReflexSnapshot, NeedSnapshot, review_reappraisal,
)


class Obs:
    def verify(self, *, life_ref, claim, digest):
        return life_ref == claim.life_ref and digest == claim.digest()


class Results:
    def verify_chosen_result(self, *, result):
        return True


class Reflex:
    def verify_survival_reflex(self, *, claim, snapshot):
        return snapshot.capture_ref == claim.capture.ref


class Need:
    def verify_need(self, *, claim, snapshot):
        return snapshot.capture_ref == claim.capture.ref


class TestReappraisal(unittest.TestCase):
    def setUp(self):
        self.claim = ObservationClaim(
            "life:i2:test", FirstPersonCapture(
                40, "capture:i2:test:40", "goal:food",
                ("affordance:drink:water", "affordance:eat:berry_a")),
            "source:i2:local:40",
            tuple(sorted(("evidence:i2:bad", "evidence:i2:good",
                          "evidence:i2:context", "evidence:i2:reflex",
                          "evidence:i2:need"))),
        )
        self.eat = "affordance:eat:berry_a"
        self.bad = ObservedChosenResult(
            self.claim.life_ref, "capture:i2:old:1", self.eat,
            11, "evidence:i2:bad", -10)
        self.good = ObservedChosenResult(
            self.claim.life_ref, "capture:i2:old:2", self.eat,
            19, "evidence:i2:good", 4)
        self.reflex = self.snap("NO_PREEMPTION")

    def snap(self, state):
        return SurvivalReflexSnapshot(
            self.claim.life_ref, self.claim.capture.ref,
            self.claim.digest(), "evidence:i2:reflex", state)

    def need(self, state):
        return NeedSnapshot(
            self.claim.life_ref, self.claim.capture.ref,
            self.claim.digest(), "evidence:i2:need", state)

    def call(self, **kw):
        return review_reappraisal(
            claim=kw.pop("claim", self.claim),
            target_semantic_ref=kw.pop("target_semantic_ref", self.eat),
            chosen_results=kw.pop("chosen_results", (self.bad,)),
            observation_source=kw.pop("observation_source", Obs()),
            chosen_source=kw.pop("chosen_source", Results()), **kw)

    def test_no_reflex_fails_closed_even_when_context_changes(self):
        decision = self.call(new_context_refs=("evidence:i2:context",))
        self.assertEqual(decision.review_status, "REFLEX_UNAVAILABLE")
        self.assertEqual(decision.contract, CONTRACT)
        self.assertFalse(decision.hidden_regime_identified)
        self.assertEqual(decision.motor_authority, "NONE")
        self.assertTrue(decision.requires_paid_competition)
        self.assertTrue(decision.requires_fresh_action_control)

    def test_hidden_change_unidentifiable_and_no_bonus(self):
        d = self.call(reflex=self.reflex, reflex_source=Reflex())
        self.assertEqual(d.evidence_state, "LATENT_CHANGE_NOT_IDENTIFIABLE")
        self.assertEqual(d.review_status, "LATENT_CHANGE_UNIDENTIFIABLE_DEFER")
        self.assertFalse(d.m11_authenticated)

    def test_context_cue_is_hypothesis_not_safe_food(self):
        d = self.call(reflex=self.reflex, reflex_source=Reflex(),
                      new_context_refs=("evidence:i2:context",))
        self.assertEqual(d.evidence_state, "NEW_CONTEXT_CUE_NOT_PAYOFF_PROOF")
        self.assertEqual(d.review_status, "EVIDENCE_BASED_RECONSIDERATION_HYPOTHESIS")
        self.assertFalse(d.hidden_regime_identified)
        self.assertEqual(d.motor_authority, "NONE")

    def test_personally_observed_contradiction_is_a_hypothesis(self):
        d = self.call(chosen_results=(self.bad, self.good),
                      reflex=self.reflex, reflex_source=Reflex())
        self.assertEqual(d.evidence_state, "PERSONAL_OUTCOME_CONTRADICTION")
        self.assertEqual(d.review_status, "EVIDENCE_BASED_RECONSIDERATION_HYPOTHESIS")

    def test_survival_preemption_and_constrain_win(self):
        for state, expected in (("PREEMPT", "REFLEX_PREEMPTED"),
                                ("CONSTRAIN", "REFLEX_CONSTRAINED"),
                                ("UNKNOWN", "REFLEX_UNKNOWN_DEFER")):
            with self.subTest(state=state):
                d = self.call(reflex=self.snap(state), reflex_source=Reflex(),
                              need=self.need("CRITICAL"), need_source=Need(),
                              new_context_refs=("evidence:i2:context",))
                self.assertEqual(d.review_status, expected)

    def test_critical_need_can_motivate_but_cannot_override_reflex(self):
        d = self.call(reflex=self.reflex, reflex_source=Reflex(),
                      need=self.need("CRITICAL"), need_source=Need())
        self.assertEqual(d.review_status, "NEED_BASED_RISK_RECONSIDERATION_HYPOTHESIS")
        self.assertFalse(d.hidden_regime_identified)

    def test_unavailable_target_and_no_aversion(self):
        d = self.call(target_semantic_ref="affordance:collect:berry_a",
                      reflex=self.reflex, reflex_source=Reflex())
        self.assertEqual(d.review_status, "TARGET_NOT_AVAILABLE")
        d = self.call(chosen_results=(self.good,), reflex=self.reflex,
                      reflex_source=Reflex())
        self.assertEqual(d.review_status, "NO_PERSONALLY_LEARNED_AVERSION")

    def test_spoofed_ports_future_evidence_or_missing_cue_rejected(self):
        with self.assertRaises(ValueError):
            self.call(chosen_results=(self.bad, self.bad))
        with self.assertRaises(ValueError):
            self.call(new_context_refs=("evidence:i2:oracle",))
        with self.assertRaises(ValueError):
            self.call(chosen_results=(ObservedChosenResult(
                self.claim.life_ref, "capture:i2:future", self.eat,
                41, "evidence:i2:bad", -10),))
        with self.assertRaises(ValueError):
            self.call(reflex=SurvivalReflexSnapshot(
                "life:i2:foreign", self.claim.capture.ref,
                self.claim.digest(), "evidence:i2:reflex", "NO_PREEMPTION"),
                reflex_source=Reflex())
        with self.assertRaises(ValueError):
            self.call(reflex=self.reflex, reflex_source=Reflex(),
                      need=self.need("CRITICAL"))
        with self.assertRaises(ValueError):
            self.call(reflex=self.reflex, reflex_source=Reflex(),
                      need=self.need("CRITICAL"), need_source=object())


if __name__ == "__main__":
    unittest.main()
