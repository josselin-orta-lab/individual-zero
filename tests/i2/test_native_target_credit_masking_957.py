"""#957: read-only stage masking of generic chosen-outcome food value.

Structural negative/positive probes only. These do not replay a life, give
new actions or change native policy; actual G2 motor evidence remains #956.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body, transition
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_owner_support import _json, current_evidence
from i2.modules.chosen_outcome_study import FIXED_SCORE_OFFSET
from i2.runtime.native_paid_cycle import (
    PRIORS, innate_adjustment, personally_nonrestoring_scores,
    personally_observed_resource_outcomes,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
BODY = Body(85, 40, 75, 100)


def claim(body):
    return ObservationClaim(
        "life:i2:p4:mask-audit",
        FirstPersonCapture(
            2, "capture:i2:p4:mask-audit",
            "goal:physical-needs", ("boire", "manger")),
        "source:i2:p4:mask-audit",
        tuple(sorted(current_evidence(body, TRAITS))))


def food_row(*, gain=34.8, injury=-8.):
    before = BODY
    after = Body(84.5, min(100., BODY.food + gain), 74.6,
                 max(0., BODY.integrity + injury))
    return (1, "capture:i2:p4:prior:1", "manger", 0.,
            _json(before.as_dict()), _json(after.as_dict()), 0)


class TargetCreditMasking957(unittest.TestCase):
    def test_positive_food_history_replaces_distinct_generic_values(self):
        # Exact same current body and target experience; intentionally
        # distinct already computed generic scores are pure inputs here.
        prior = (food_row(injury=-8.),)
        target = personally_observed_resource_outcomes(
            previous=prior, traits=TRAITS)
        self.assertEqual(target["manger"], (1, 0))
        baseline = innate_adjustment(PRIORS, BODY, TRAITS)["manger"]
        observed = []
        for generic in (-35, 15, 70):
            result, discouraged, associated = personally_nonrestoring_scores(
                {"manger": generic}, claim=claim(BODY), body=BODY,
                traits=TRAITS, previous=prior, learning=True)
            self.assertIn("manger", associated)
            self.assertEqual(result["manger"], baseline + 1)
            self.assertFalse(discouraged)
            observed.append(result["manger"])
        self.assertEqual(len(set(observed)), 1)

    def test_physical_net_relief_diverges_even_though_target_value_does_not(self):
        # Actual born-law pure transitions from an identical physical body.
        # These are prospective physics projections, NOT admitted motors or
        # hidden future outcomes presented to an individual.
        next_harm = transition(
            BODY, "manger", berry_food_gain=35.,
            berry_integrity_delta=-8.).body
        next_safe = transition(
            BODY, "manger", berry_food_gain=35.,
            berry_integrity_delta=0.).body
        self.assertEqual(next_harm.food, next_safe.food)
        self.assertLess(next_harm.integrity, next_safe.integrity)
        current = assess_needs(BODY, TRAITS)
        relief = []
        target_adjusted = []
        for after in (next_harm, next_safe):
            later = assess_needs(after, TRAITS)
            actual_relief = (
                sum(current.pressures.values()) -
                sum(later.pressures.values()))
            relief.append(actual_relief)
            # This is the existing G2 projection from a committed net
            # consequence, not a new reward formula applied in native.
            generic = int(round(20 * actual_relief)) + FIXED_SCORE_OFFSET
            history = ((1, "capture:i2:p4:prior:1", "manger",
                        actual_relief, _json(BODY.as_dict()),
                        _json(after.as_dict()), 0),)
            adjusted, _, associated = personally_nonrestoring_scores(
                {"manger": generic},
                claim=claim(BODY), body=BODY, traits=TRAITS,
                previous=history, learning=True)
            self.assertIn("manger", associated)
            target_adjusted.append(adjusted["manger"])
        self.assertLess(relief[0], relief[1])
        self.assertEqual(target_adjusted[0], target_adjusted[1])

    def test_without_target_history_generic_value_survives(self):
        for generic in (-35, 15, 70):
            result, _, associated = personally_nonrestoring_scores(
                {"manger": generic}, claim=claim(BODY), body=BODY,
                traits=TRAITS, previous=(), learning=True)
            self.assertEqual(result["manger"], generic)
            self.assertFalse(associated)

    def test_learning_off_retains_distinct_scores_despite_food_history(self):
        history = (food_row(injury=-8.),)
        for generic in (-35, 15, 70):
            result, discouraged, associated = personally_nonrestoring_scores(
                {"manger": generic}, claim=claim(BODY), body=BODY,
                traits=TRAITS, previous=history, learning=False)
            self.assertEqual(result["manger"], generic)
            self.assertFalse(discouraged)
            self.assertFalse(associated)

    def test_target_success_does_not_distinguish_actual_integrity_harm(self):
        harmful = (food_row(injury=-8.),)
        harmless = (food_row(injury=0.),)
        for history in (harmful, harmless):
            self.assertEqual(
                personally_observed_resource_outcomes(
                    previous=history, traits=TRAITS)["manger"], (1, 0))
        for generic in (-25, 20):
            values = []
            for history in (harmful, harmless):
                result, _, _ = personally_nonrestoring_scores(
                    {"manger": generic}, claim=claim(BODY), body=BODY,
                    traits=TRAITS, previous=history, learning=True)
                values.append(result["manger"])
            self.assertEqual(values[0], values[1])


if __name__ == "__main__":
    unittest.main()
