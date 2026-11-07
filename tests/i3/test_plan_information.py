"""Plan-level Stage-1 information kernel: software arithmetic, no live policy."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (BodyLaws, CognitiveBudget, CognitiveWork,
                             CognitiveFundingError, debit_cognition)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.plan_information import (
    PlanSubjectiveOutcome, paid_plan_information_value)
from i3.runtime.life import run_life

BODY = (80., 80., 80., 80., 80.)
OUTCOMES = (
    PlanSubjectiveOutcome(.5, "body", (0., -70., 0., 0., 0.)),
    PlanSubjectiveOutcome(.5, "body", (0., 0., -70., 0., 0.)),
)
PLANS = (
    ("drink", (("boire",),)),
    ("eat", (("manger", "tok0"),)),
)


def model():
    m = Mind(midpoint(), 11)
    m.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    m.effects.observe(("boire",), (0., 0., 80., 0., 0.))
    m.effects.observe(("manger", "tok0"), (0., 80., 0., 0., 0.))
    m._drift = m.drift()
    return m


class PlanInformationTests(unittest.TestCase):
    def test_empirical_body_signal_can_change_best_existing_plan(self):
        m = model()
        b = CognitiveBudget(BODY, BodyLaws())
        result = paid_plan_information_value(m, OUTCOMES, PLANS, 4, b)
        self.assertGreater(result["information_value"], 0.)
        choices = {
            tuple(row["predicted_body"]): row["best_continuations"]
            for row in result["conditional_choices"]}
        self.assertEqual(len(choices), 2)
        low_food = min(choices, key=lambda body: body[1])
        low_water = min(choices, key=lambda body: body[2])
        self.assertEqual(choices[low_food], ("eat",))
        self.assertEqual(choices[low_water], ("drink",))
        self.assertEqual(result["outcome_generation"],
                         "CALLER_SUPPLIED_PERSONAL_BELIEFS_ONLY")
        self.assertEqual(result["status"],
                         "COMPLETE_SUBJECTIVE_ESTIMATE_NOT_POLICY")

    def test_indistinguishable_observations_have_zero_information(self):
        m = model()
        outcomes = (
            PlanSubjectiveOutcome(.5, "body", (0., -30., 0., 0., 0.)),
            PlanSubjectiveOutcome(.5, "body", (0., -30., 0., 0., 0.)),
        )
        result = paid_plan_information_value(
            m, outcomes, PLANS, 4, CognitiveBudget(BODY, BodyLaws()))
        self.assertAlmostEqual(result["information_value"], 0.)
        self.assertEqual(len(result["conditional_choices"]), 1)

    def test_complete_matrix_is_executed_not_branch_maximized_early(self):
        m = model()
        with patch.object(m, "simulate", wraps=m.simulate) as simulate:
            result = paid_plan_information_value(
                m, OUTCOMES, PLANS, 4, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(simulate.call_count, 4)
        self.assertEqual(len(result["branch_values"]), 2)
        self.assertTrue(all(len(row) == 2 for row in result["branch_values"]))

    def test_declared_complete_ceiling_matches_simple_one_action_matrix(self):
        result = paid_plan_information_value(
            model(), OUTCOMES, PLANS, 4, CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(result["minimum_complete_forecast_work"], {
            "cycles": 6,
            "simulated_steps": 36,
            "memory_items": 38,
            "replays": 0})
        self.assertEqual(result["work"], result["minimum_complete_forecast_work"])
        forecast, _ = debit_cognition(
            BODY, BodyLaws(), CognitiveWork(**result["forecast_work_ceiling"]))
        self.assertEqual(result["forecast_start_body"], forecast)

    def test_too_small_common_ceiling_fails_after_paid_preparation_only(self):
        b = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "cannot omit"):
            paid_plan_information_value(
                model(), OUTCOMES, PLANS, 4, b,
                forecast_work=CognitiveWork(
                    cycles=5, simulated_steps=36, memory_items=38))
        self.assertEqual(b.work, CognitiveWork(cycles=1, memory_items=38))

    def test_unaffordable_complete_quote_never_returns_partial_score(self):
        body = (.15, 80., 80., 80., .35)
        b = CognitiveBudget(body, BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            paid_plan_information_value(model(), OUTCOMES, PLANS, 4, b)
        self.assertEqual(b.work, CognitiveWork(cycles=1, memory_items=38))

    def test_dead_probe_branch_is_absorbing_and_still_in_matrix(self):
        outcomes = (
            PlanSubjectiveOutcome(.5, "body", (0., -100., 0., 0., 0.)),
            PlanSubjectiveOutcome(.5, "body", (0., 0., -70., 0., 0.)),
        )
        m = model()
        with patch.object(m, "simulate", wraps=m.simulate) as simulate:
            result = paid_plan_information_value(
                m, outcomes, PLANS, 4, CognitiveBudget(BODY, BodyLaws()))
        # Two continuations on the dead branch are absorbing and need no
        # projection; both live-branch continuations are still simulated.
        self.assertEqual(simulate.call_count, 2)
        self.assertEqual(result["branch_values"][0],
                         [-m.d_max, -m.d_max])
        actual = CognitiveWork(**result["work"])
        ceiling = CognitiveWork(**result["forecast_work_ceiling"])
        for name in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(getattr(actual, name), getattr(ceiling, name))

    def test_invalid_outcomes_and_plans_fail_before_simulation(self):
        cases = (
            (OUTCOMES[:1], PLANS),
            (OUTCOMES, ()),
            (OUTCOMES, (("bad", (("manger",),)),)),
            (OUTCOMES, (("bad", [("boire",)]),)),
        )
        for outcomes, plans in cases:
            b = CognitiveBudget(BODY, BodyLaws())
            with self.subTest(outcomes=outcomes, plans=plans), self.assertRaises(ValueError):
                paid_plan_information_value(model(), outcomes, plans, 4, b)
            self.assertEqual(b.work, CognitiveWork())

    def test_no_computation_after_physical_death(self):
        b = CognitiveBudget((80., 0., 80., 80., 80.), BodyLaws())
        with self.assertRaises(ValueError):
            paid_plan_information_value(model(), OUTCOMES, PLANS, 4, b)
        self.assertEqual(b.work, CognitiveWork())

    def test_module_does_not_create_runtime_policy(self):
        with patch("i3.runtime.life.World", side_effect=AssertionError("born too soon")):
            with self.assertRaisesRegex(ValueError, "unknown decision policy"):
                run_life(
                    midpoint(), None, 1, 1,
                    decision_policy="reference_information_v1")


if __name__ == "__main__":
    unittest.main()
