"""I2 native observation provenance, birth constraints and innate behavior."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import (
    _json, saved_body, saved_traits, genesis_binding, current_evidence,
    native_scores, NativeCaptureReflex,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim

class NativeOwnerSupportTests(unittest.TestCase):
    def setUp(self):
        self.body = Body(50, 5, 70, 100)
        self.traits = BirthTemperament(0, 0.7, 0.5, 0, 0)
        self.claim = ObservationClaim(
            "i2:local:test",
            FirstPersonCapture(10, "capture:i2:native:1", "goal:food",
                               ("affordance:drink:water",)),
            "source:i2:previous-commit:0",
            tuple(sorted(current_evidence(self.body, self.traits))))
    def test_canonical_four_reserves_and_immutable_genesis_binding(self):
        b, t = _json(self.body.as_dict()), _json(self.traits.as_dict())
        self.assertEqual(saved_body(b), self.body)
        self.assertEqual(saved_traits(t), self.traits)
        self.assertNotEqual(
            genesis_binding(b, t),
            genesis_binding(_json(Body(49, 5, 70, 100).as_dict()), t))
        with self.assertRaises(ValueError):
            saved_body('{"energy":50}')
        with self.assertRaises(ValueError):
            saved_body(b.replace('"energy":50', '"energy":NaN'))
    def test_claim_bound_innate_reflex_without_motor(self):
        bound = NativeCaptureReflex(self.claim, self.body, self.traits)
        self.assertEqual(bound.state, "CONSTRAIN")
        self.assertTrue(bound.verify_survival_reflex(
            claim=self.claim, snapshot=bound.snapshot()))
        stale = ObservationClaim(
            self.claim.life_ref, self.claim.capture,
            self.claim.source_event_ref, ("evidence:i2:forged",))
        with self.assertRaises(ValueError):
            NativeCaptureReflex(stale, self.body, self.traits)
    def test_native_innate_need_weights_affect_subjective_value(self):
        priors = {"affordance:drink:water": 1,
                  "affordance:eat:berry_a": 4,
                  "affordance:collect:berry_a": 3}
        result = native_scores(
            priors, self.body, self.traits,
            collect="affordance:collect:berry_a",
            eat="affordance:eat:berry_a", drink="affordance:drink:water")
        self.assertGreater(result["affordance:eat:berry_a"],
                           priors["affordance:eat:berry_a"])
        self.assertEqual(priors["affordance:eat:berry_a"], 4)
        self.assertEqual(len(result), 3)
    def test_terminal_body_does_not_assert_survival(self):
        dying = Body(20, 1, 1, 1)
        claim = ObservationClaim(
            self.claim.life_ref, self.claim.capture,
            self.claim.source_event_ref,
            tuple(sorted(current_evidence(dying, self.traits))))
        self.assertEqual(NativeCaptureReflex(claim, dying, self.traits).state,
                         "PREEMPT")

if __name__ == "__main__":
    unittest.main()
