"""Branch-specific P1.3 replanning arithmetic; software only."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.plan_information import (
    RevealedPlanOutcome, paid_revealed_plan_information_value)
from i3.runtime.life import run_life

BODY = (80., 80., 20., 80., 80.)
COMMON = (
    ("wait", (("attendre",),)),
)
WATER_PLAN = (
    ("use-water", (("se_deplacer",), ("boire",))),
)


def model():
    m = Mind(midpoint(), 31)
    m.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    m.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    m.effects.observe(("boire",), (-.5, -.2, 50., 0., 0.))
    m.effects.observe(("manger", "tok0"), (-.5, 30., -.4, 0., 0.))
    m._drift = m.drift()
    return m


def two_branch():
    return (
        RevealedPlanOutcome(
            .5, "NO_ACTIONABLE_PERSONAL_MODEL", (0., 0., 0., 0., 0.), ()),
        RevealedPlanOutcome(
            .5, "ACTIONABLE_WATER", (0., 0., 0., 0., 0.), WATER_PLAN),
    )


class RevealedPlanInformationTests(unittest.TestCase):
    def test_revealed_water_plan_can_create_positive_information_value(self):
        result = paid_revealed_plan_information_value(
            model(), two_branch(), COMMON, 4,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertGreater(result["information_value"], 0.)
        self.assertEqual(result["common_continuation_order"], ("wait",))
        self.assertEqual(result["common_best_continuations"], ("wait",))
        by_signal = {
            row["signal"]: row
            for row in result["conditional_choices"]}
        self.assertEqual(
            by_signal["NO_ACTIONABLE_PERSONAL_MODEL"]["available_continuations"],
            ("wait",))
        self.assertEqual(
            by_signal["ACTIONABLE_WATER"]["available_continuations"],
            ("use-water", "wait"))
        self.assertEqual(
            by_signal["ACTIONABLE_WATER"]["best_continuations"],
            ("use-water",))
        self.assertEqual(
            result["revealed_plan_semantics"], "OBSERVABLE_GROUP_ONLY")

    def test_uninformed_comparator_never_receives_revealed_plan(self):
        result = paid_revealed_plan_information_value(
            model(), two_branch(), COMMON, 4,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertNotIn("use-water", result["common_continuation_order"])
        self.assertNotIn("use-water", result["common_best_continuations"])
        rows = [dict(row) for row in result["branch_values"]]
        self.assertEqual(tuple(rows[0]), ("wait",))
        self.assertEqual(tuple(sorted(rows[1])), ("use-water", "wait"))

    def test_complete_branch_specific_matrix_is_executed(self):
        m = model()
        with patch.object(m, "simulate", wraps=m.simulate) as simulate:
            result = paid_revealed_plan_information_value(
                m, two_branch(), COMMON, 4,
                CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(simulate.call_count, 3)
        self.assertEqual(result["minimum_complete_forecast_work"], {
            "cycles": 5,
            "simulated_steps": 28,
            "memory_items": 37,
            "replays": 0})
        self.assertEqual(
            result["work"], result["minimum_complete_forecast_work"])
        forecast, _ = debit_cognition(
            BODY, BodyLaws(),
            CognitiveWork(**result["forecast_work_ceiling"]))
        self.assertEqual(result["forecast_start_body"], forecast)

    def test_indistinguishable_outcomes_cannot_reveal_different_plans(self):
        outcomes = (
            RevealedPlanOutcome(
                .5, "same", (0., 0., 0., 0., 0.), ()),
            RevealedPlanOutcome(
                .5, "same", (0., 0., 0., 0., 0.), WATER_PLAN),
        )
        m = model()
        budget = CognitiveBudget(BODY, BodyLaws())
        with patch.object(m, "simulate", wraps=m.simulate) as simulate:
            with self.assertRaisesRegex(ValueError, "indistinguishable"):
                paid_revealed_plan_information_value(
                    m, outcomes, COMMON, 4, budget)
        self.assertEqual(simulate.call_count, 0)
        # The complete input/preparation scan remains paid before the
        # forecast-body observable equivalence can be checked.
        self.assertEqual(budget.work, CognitiveWork(
            cycles=1, memory_items=37))

    def test_same_observable_and_same_revealed_plan_is_one_group(self):
        outcomes = (
            RevealedPlanOutcome(
                .4, "water", (0., 0., 0., 0., 0.), WATER_PLAN),
            RevealedPlanOutcome(
                .6, "water", (0., 0., 0., 0., 0.), WATER_PLAN),
        )
        result = paid_revealed_plan_information_value(
            model(), outcomes, COMMON, 4,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(len(result["conditional_choices"]), 1)
        self.assertAlmostEqual(
            result["conditional_choices"][0]["probability"], 1.0)
        self.assertEqual(
            result["conditional_choices"][0]["available_continuations"],
            ("use-water", "wait"))

    def test_observable_food_branch_may_use_only_its_observed_token_placeholder(self):
        food = (
            ("use-observed-food",
             (("se_deplacer",), ("collecter", "observed-token"),
              ("manger", "observed-token"))),
        )
        outcomes = (
            RevealedPlanOutcome(.5, "none", (0., 0., 0., 0., 0.), ()),
            RevealedPlanOutcome(.5, "food", (0., 0., 0., 0., 0.), food),
        )
        result = paid_revealed_plan_information_value(
            model(), outcomes, COMMON, 5,
            CognitiveBudget(BODY, BodyLaws()))
        by_signal = {
            row["signal"]: row["available_continuations"]
            for row in result["conditional_choices"]}
        self.assertEqual(by_signal["none"], ("wait",))
        self.assertEqual(
            by_signal["food"], ("use-observed-food", "wait"))

    def test_revealed_plan_cannot_shadow_common_plan(self):
        outcomes = (
            RevealedPlanOutcome(
                .5, "none", (0., 0., 0., 0., 0.), ()),
            RevealedPlanOutcome(
                .5, "water", (0., 0., 0., 0., 0.),
                (("wait", (("boire",),)),)),
        )
        budget = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "shadow"):
            paid_revealed_plan_information_value(
                model(), outcomes, COMMON, 4, budget)
        self.assertEqual(budget.work, CognitiveWork())

    def test_invalid_probability_or_plan_fails_before_work(self):
        cases = (
            (
                RevealedPlanOutcome(
                    .4, "none", (0., 0., 0., 0., 0.), ()),
                RevealedPlanOutcome(
                    .4, "water", (0., 0., 0., 0., 0.), WATER_PLAN),
            ),
            (
                RevealedPlanOutcome(
                    .5, "none", (0., 0., 0., 0., 0.), ()),
                RevealedPlanOutcome(
                    .5, "water", (0., 0., 0., 0., 0.),
                    (("bad", (("manger",),)),)),
            ),
        )
        for outcomes in cases:
            budget = CognitiveBudget(BODY, BodyLaws())
            with self.subTest(outcomes=outcomes), self.assertRaises(ValueError):
                paid_revealed_plan_information_value(
                    model(), outcomes, COMMON, 4, budget)
            self.assertEqual(budget.work, CognitiveWork())

    def test_no_live_policy_is_created(self):
        with patch(
            "i3.runtime.life.World",
            side_effect=AssertionError("born too soon")):
            with self.assertRaisesRegex(ValueError, "unknown decision policy"):
                run_life(
                    midpoint(), None, 1, 1,
                    decision_policy="reference_information_v1")


if __name__ == "__main__":
    unittest.main()
