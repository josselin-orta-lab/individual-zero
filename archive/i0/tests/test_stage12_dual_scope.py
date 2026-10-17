"""B dual-scope policy: outcome observation never claims physical causation."""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.stage12_goal_agency import GoalAgencyService
from i0.modules.stage12_dual_scope import (
    OutcomeScopeJudgement, evaluate_outcome_scope, DUAL_SCOPE_VERSION,
)
from test_stage12_goal_agency_independence import perception


def trial(*, food_after, berries_after, paid=True):
    source = perception(1, food=60.0, berries=2)
    owner = GoalAgencyService()
    pending = owner.preregister(
        assessment_ref="assessment:1", intent_ref="intent:1",
        life_id="life:1", goal_ref="goal:food", option_ref="option:eat",
        command_hash="digest:1", world_step=1, measure="food",
        command=PrimitiveCommand("manger", {"target": "berry_a"}),
        capture=source,
    )
    after = perception(2, food=food_after, berries=berries_after)
    proximal = owner.evaluate(
        capture=after, world_step=2, cue_ref="cue:2" if paid else None,
        paid=paid,
    )
    distal = evaluate_outcome_scope(pending, proximal, original=source,
        observed=after, paid=paid, cue_ref="cue:2" if paid else None)
    return pending, proximal, distal, source, after


class DualScopeTests(unittest.TestCase):
    def test_ingestion_cue_but_no_food_gain(self):
        _, action, outcome, _, _ = trial(food_after=60.0, berries_after=1)
        self.assertEqual(action.subjective_agency, "self")
        self.assertEqual(outcome.proximal_agency, "self")
        self.assertEqual(outcome.observed_outcome, "not_improved")
        self.assertEqual(outcome.subjective_responsibility, "unknown")
        self.assertEqual(OutcomeScopeJudgement.from_dict(outcome.as_dict()), outcome)

    def test_exogenous_food_gain_does_not_prove_responsibility(self):
        _, action, outcome, _, _ = trial(food_after=80.0, berries_after=2)
        self.assertEqual(action.subjective_agency, "unknown")
        self.assertEqual(outcome.observed_outcome, "improved")
        self.assertEqual(outcome.subjective_responsibility, "unknown")

    def test_even_matching_ingestion_and_gain_cannot_prove_cause(self):
        _, action, outcome, _, _ = trial(food_after=80.0, berries_after=1)
        self.assertEqual(action.subjective_agency, "self")
        self.assertEqual(outcome.observed_outcome, "improved")
        self.assertEqual(outcome.subjective_responsibility, "unknown")

    def test_uc_refusal(self):
        _, action, outcome, _, _ = trial(food_after=90.0, berries_after=1, paid=False)
        self.assertEqual(action.subjective_agency, "unavailable")
        self.assertEqual(outcome.observed_outcome, "unavailable")
        self.assertEqual(outcome.subjective_responsibility, "unavailable")

    def test_wrong_intent_and_bad_serialization_rejected(self):
        pending, proximal, distal, before, after = trial(food_after=80, berries_after=1)
        with self.assertRaisesRegex(ValueError, "provenance"):
            evaluate_outcome_scope(pending, replace(proximal, intent_ref="forged"),
                                   original=before, observed=after,
                                   paid=True, cue_ref="cue:2")
        image = distal.as_dict()
        image["subjective_responsibility"] = "self"
        with self.assertRaisesRegex(ValueError, "invalid"):
            OutcomeScopeJudgement.from_dict(image)
        with self.assertRaisesRegex(ValueError, "invalid"):
            OutcomeScopeJudgement.from_dict({**distal.as_dict(), "extra": "truth"})
        self.assertEqual(distal.policy_version, DUAL_SCOPE_VERSION)

    def test_disabled_new_policy_is_not_a_legacy_mutation(self):
        # Pure module does not change existing GoalAgencyService images.
        src = perception(1, food=60, berries=2)
        legacy = GoalAgencyService()
        old = legacy.export_causal_state()
        self.assertEqual(old["schema"], legacy.schema)
        self.assertNotIn("outcome_responsibility", old)
        self.assertEqual(old, legacy.export_causal_state())


if __name__ == "__main__":
    unittest.main()
