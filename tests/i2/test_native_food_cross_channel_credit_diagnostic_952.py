"""P4 #952: isolate target-need success from observed secondary harm.

Read-only *structural* witness for current target-specific credit accounting.
No new choice policy, no second memory owner, no scripted motor, no learned
outcome oracle. This DOES NOT assert the separate generic G2 relief is blind
to integrity; it tests only the downstream native target-specific override.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body
from i2.modules.native_owner_support import _json, current_evidence
from i2.runtime.native_paid_cycle import (
    PRIORS, innate_adjustment, personally_nonrestoring_scores,
    personally_observed_resource_outcomes,
)


TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def observed_food(seq, before, after):
    # A pure read-only projection of an already physical before/after pair,
    # not an action issued or a future outcome predicted to the individual.
    return (seq, "capture:i2:p4:food:" + str(seq), "manger", 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


def food_claim(body):
    return ObservationClaim(
        "life:i2:p4:food-audit",
        FirstPersonCapture(2, "capture:i2:p4:food-audit",
                           "goal:physical-needs", ("manger", "boire")),
        "source:i2:p4:food-audit",
        tuple(sorted(current_evidence(body, TRAITS))))


class NativeCrossChannelFoodEvidence952(unittest.TestCase):
    def test_target_success_same_when_realized_integrity_differs(self):
        hungry = Body(85, 40, 75, 100)
        beneficial = Body(84.5, 74.8, 74.6, 100)
        harmful = Body(84.5, 74.8, 74.6, 92)
        examples = {
            "harmless": (observed_food(1, hungry, beneficial),),
            "harmful": (observed_food(1, hungry, harmful),)
        }
        # Both restore exactly the same *food* reserve. Existing native
        # target-specific outcome accounting marks both as successful.
        for history in examples.values():
            self.assertEqual(
                personally_observed_resource_outcomes(
                    previous=history, traits=TRAITS)["manger"], (1, 0))

        born = innate_adjustment(PRIORS, hungry, TRAITS)
        before_scores = {"manger": born["manger"], "boire": born["boire"]}
        values = []
        for history in examples.values():
            adjusted, _, associated = personally_nonrestoring_scores(
                before_scores, claim=food_claim(hungry),
                body=hungry, traits=TRAITS, previous=history, learning=True)
            self.assertIn("manger", associated)
            self.assertEqual(adjusted["manger"], born["manger"] + 1)
            values.append(adjusted["manger"])
        self.assertEqual(values[0], values[1])
        self.assertNotEqual(harmful.integrity, beneficial.integrity)

    def test_saturated_harm_is_not_counted_as_food_success_or_failure(self):
        satiated = Body(85, 100, 75, 100)
        eaten_without_gain = Body(84.5, 100, 74.6, 92)
        previous = (observed_food(1, satiated, eaten_without_gain),)
        counts = personally_observed_resource_outcomes(
            previous=previous, traits=TRAITS)
        self.assertEqual(counts["manger"], (0, 0))
        baseline = innate_adjustment(PRIORS, satiated, TRAITS)
        scores, _, associated = personally_nonrestoring_scores(
            {"manger": baseline["manger"]}, claim=food_claim(satiated),
            body=satiated, traits=TRAITS, previous=previous, learning=True)
        self.assertNotIn("manger", associated)
        self.assertEqual(scores["manger"], baseline["manger"])
        self.assertEqual(eaten_without_gain.food, satiated.food)
        self.assertLess(eaten_without_gain.integrity, satiated.integrity)

    def test_learning_off_does_not_add_target_specific_credit(self):
        hungry = Body(85, 40, 75, 100)
        harmful = Body(84.5, 74.8, 74.6, 92)
        before_scores = {"manger": 17}
        adjusted, discouraged, associated = personally_nonrestoring_scores(
            before_scores, claim=food_claim(hungry),
            body=hungry, traits=TRAITS,
            previous=(observed_food(1, hungry, harmful),),
            learning=False)
        self.assertEqual(adjusted, before_scores)
        self.assertFalse(discouraged)
        self.assertFalse(associated)


if __name__ == "__main__":
    unittest.main()
