"""Nested unsupported-action trial value: software only, no live policy."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.plan_information import PlanSubjectiveOutcome
from i3.modules.unknown_action_trial import paid_unknown_action_trial_value
from i3.modules.unknown_effect_prior import PRIOR_WORK

BODY = (20., 80., 80., 80., 80.)
COMMON = (
    ("sleep-now", (("dormir",),)),
    ("wait-now", (("attendre",),)),
)
POST = (
    ("post-sleep", (("dormir",),)),
    ("post-wait", (("attendre",),)),
)


def make_mind():
    mind = Mind(midpoint(), 31)
    mind.effects.observe(("attendre",), (0., -1., -1., .2, 0.))
    mind.effects.observe(("dormir",), (70., -8., -1., 0., 20.))
    mind._drift = mind.drift()
    return mind


class UnknownActionTrialTests(unittest.TestCase):
    def test_zero_mean_trial_can_have_positive_information_without_positive_prior(self):
        result = paid_unknown_action_trial_value(
            make_mind(), ("boire",), COMMON, POST, 4,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(
            result["status"],
            "COMPLETE_UNKNOWN_ACTION_TRIAL_ESTIMATE_NOT_POLICY")
        self.assertEqual(
            tuple(round(x, 12) for x in result["prior_expected_external_delta"]),
            (0., 0., 0., 0., 0.))
        self.assertGreater(result["information_value"], 0.)
        self.assertGreaterEqual(
            result["trial_informed_value"],
            result["trial_frozen_value"])
        self.assertEqual(len(result["conditional_choices"]), 2)
        chosen = {
            tuple(round(x, 6) for x in row["post_trial_body"]):
                row["best_post_trial_continuations"]
            for row in result["conditional_choices"]}
        self.assertEqual(len(set(chosen.values())), 2)

    def test_information_value_and_trial_advantage_are_separate_quantities(self):
        result = paid_unknown_action_trial_value(
            make_mind(), ("boire",), COMMON, POST, 4,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertAlmostEqual(
            result["information_value"],
            result["trial_informed_value"] - result["trial_frozen_value"])
        self.assertAlmostEqual(
            result["trial_advantage"],
            result["trial_informed_value"] - result["no_trial_value"])
        # The kernel never equates epistemic value with whether the trial
        # itself should be selected.
        self.assertIn("no_trial_best_continuations", result)
        self.assertIn("trial_frozen_best_continuations", result)

    def test_common_no_trial_plan_cannot_smuggle_unsupported_action(self):
        allowance = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "no-trial"):
            paid_unknown_action_trial_value(
                make_mind(), ("boire",),
                (("bad", (("boire",),)),), POST, 4, allowance)
        self.assertEqual(allowance.work, CognitiveWork())

    def test_locally_flat_stake_returns_no_trial_score_after_paid_prior_only(self):
        body = (80., 80., 80., 80., 80.)
        allowance = CognitiveBudget(body, BodyLaws())
        result = paid_unknown_action_trial_value(
            make_mind(), ("boire",), COMMON, POST, 4, allowance)
        self.assertEqual(result["status"], "NO_STAKE_RELEVANT_UNCERTAINTY")
        self.assertIsNone(result["no_trial_value"])
        self.assertIsNone(result["trial_informed_value"])
        self.assertEqual(result["information_value"], 0.)
        self.assertEqual(allowance.work, PRIOR_WORK)

    def test_real_mind_state_is_unchanged_by_nested_counterfactuals(self):
        mind = make_mind()
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        paid_unknown_action_trial_value(
            mind, ("boire",), COMMON, POST, 4,
            CognitiveBudget(BODY, BodyLaws()))
        after = {
            "effects": mind.effects.stats,
            "values": mind.values,
            "buffer": tuple(mind.buffer),
            "map": mind.map,
            "hist": mind.hist,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        self.assertEqual(after, before)

    def test_complete_forecast_ceiling_covers_all_actual_work(self):
        result = paid_unknown_action_trial_value(
            make_mind(), ("boire",), COMMON, POST, 4,
            CognitiveBudget(BODY, BodyLaws()))
        actual = result["work"]
        ceiling = result["forecast_work_ceiling"]
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(actual[key], ceiling[key])
        self.assertEqual(
            result["work_breakdown"]["total"], result["work"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["motor_command_authorized"])
        self.assertFalse(result["world_access"])

    def test_unaffordable_complete_matrix_returns_no_score(self):
        body = (.1, 80., 80., 80., 1.)
        allowance = CognitiveBudget(body, BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            paid_unknown_action_trial_value(
                make_mind(), ("boire",), COMMON, POST, 4, allowance)
        self.assertGreater(allowance.work.cycles, 0)

    def test_indistinguishable_clipped_trials_cannot_teach_hidden_different_effects(self):
        body = (20., 80., 80., 80., 80.)

        def forged(body_arg, theta, powers, weights, allowance):
            allowance.spend(PRIOR_WORK)
            return {
                "status": "FORGED_TEST_ONLY",
                "outcomes": (
                    PlanSubjectiveOutcome(
                        .5, "same", (-50., 0., 0., 0., 0.)),
                    PlanSubjectiveOutcome(
                        .5, "same", (-100., 0., 0., 0., 0.)),
                ),
                "expected_external_delta": (-75., 0., 0., 0., 0.),
            }

        allowance = CognitiveBudget(body, BodyLaws())
        with patch(
            "i3.modules.unknown_action_trial.paid_zero_mean_stake_prior",
            side_effect=forged):
            with self.assertRaisesRegex(ValueError, "indistinguishable"):
                paid_unknown_action_trial_value(
                    make_mind(), ("boire",), COMMON, POST, 4, allowance)
        self.assertGreater(allowance.work.cycles, 0)

    def test_exact_token_action_is_allowed_without_cross_token_common_use(self):
        common = (("wait", (("attendre",),)),)
        post = (
            ("repeat", (("manger", "tok0"),)),
            ("wait-after", (("attendre",),)),
        )
        result = paid_unknown_action_trial_value(
            make_mind(), ("manger", "tok0"), common, post, 3,
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(result["action_key"], ("manger", "tok0"))
        self.assertEqual(result["prior_expected_external_delta"], (0.,) * 5)

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.unknown_action_trial; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
