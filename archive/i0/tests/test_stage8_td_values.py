from __future__ import annotations

import unittest

from i0.modules.td_values import (
    EvaluationState,
    LinearTDValues,
    TDLearningConfig,
    ValueFeatureConfig,
)


def config(*, eta: float = 0.5, lambda_e: float = 0.5, beta: float = 0.9):
    return TDLearningConfig(
        version="stage8-td-test-v1",
        eta=eta,
        lambda_e=lambda_e,
        beta=beta,
        evidence_scale=1.0,
        features=ValueFeatureConfig(
            version="phi-test-v1",
            feature_names=("bias", "water", "goal_drink"),
            position_scale_x=31.0,
            position_scale_y=31.0,
        ),
    )


def state(water: float, goal: str | None = "drink") -> EvaluationState:
    return EvaluationState(
        body={
            "energy": 50.0,
            "food": 60.0,
            "water": water,
            "integrity": 100.0,
        },
        x=2,
        y=2,
        active_goal_type=goal,
        temporal_context="day",
    )


class LinearTDValueTests(unittest.TestCase):
    def test_birth_value_is_unlearned_not_zero_evidence(self) -> None:
        model = LinearTDValues(config())

        value = model.learned_value(state(20.0), "drink:water:boire")

        self.assertEqual(value.status, "unlearned")
        self.assertIsNone(value.value)
        self.assertIsNone(value.evidence)
        self.assertEqual(model.q(state(20.0), "drink:water:boire"), 0.0)

    def test_l1_update_matches_normative_td_equation(self) -> None:
        model = LinearTDValues(config(eta=0.5, lambda_e=0.0, beta=0.9))
        previous = state(20.0)
        next_state = state(60.0)

        update = model.update_segment(
            previous_state=previous,
            previous_signature="drink",
            rewards=(4.0,),
            next_state=next_state,
            next_signature="wait",
        )

        self.assertEqual(update.segment_length, 1)
        self.assertEqual(update.return_g, 4.0)
        self.assertEqual(update.q_previous, 0.0)
        self.assertEqual(update.q_next, 0.0)
        self.assertEqual(update.delta, 4.0)

        learned = model.learned_value(previous, "drink")
        self.assertEqual(learned.status, "learned")
        self.assertIsNotNone(learned.value)
        self.assertGreater(learned.value, 0.0)

    def test_multistep_segment_discounts_reflex_intermediate_rewards(self) -> None:
        model = LinearTDValues(config(eta=0.2, lambda_e=0.5, beta=0.5))

        update = model.update_segment(
            previous_state=state(20.0),
            previous_signature="drink",
            rewards=(2.0, 4.0, 8.0),
            next_state=state(30.0),
            next_signature="eat",
        )

        self.assertEqual(update.segment_length, 3)
        self.assertEqual(update.return_g, 2.0 + 0.5 * 4.0 + 0.25 * 8.0)
        self.assertEqual(update.delta, update.return_g)

    def test_terminal_update_uses_zero_bootstrap(self) -> None:
        model = LinearTDValues(config(beta=0.8))

        update = model.update_terminal(
            previous_state=state(20.0),
            previous_signature="drink",
            rewards=(1.0, 2.0),
        )

        self.assertEqual(update.q_next, 0.0)
        self.assertEqual(update.return_g, 1.0 + 0.8 * 2.0)

    def test_eligibility_trace_can_update_previous_signature(self) -> None:
        model = LinearTDValues(config(eta=0.1, lambda_e=1.0, beta=0.9))
        model.update_segment(
            previous_state=state(20.0),
            previous_signature="drink",
            rewards=(1.0,),
            next_state=state(30.0),
            next_signature="eat",
        )
        before = model.q(state(20.0), "drink")

        second = model.update_segment(
            previous_state=state(30.0),
            previous_signature="eat",
            rewards=(2.0,),
            next_state=state(40.0),
            next_signature="wait",
        )
        after = model.q(state(20.0), "drink")

        self.assertIn("drink", second.updated_signatures)
        self.assertNotEqual(after, before)

    def test_snapshot_round_trip_is_exact(self) -> None:
        first = LinearTDValues(config())
        first.update_segment(
            previous_state=state(20.0),
            previous_signature="drink",
            rewards=(3.0,),
            next_state=state(60.0),
            next_signature="wait",
        )
        snapshot = first.export_causal_state()

        second = LinearTDValues(config())
        second.restore_causal_state(snapshot)

        self.assertEqual(
            second.export_causal_state(),
            snapshot,
        )

    def test_feature_schema_rejects_unknown_or_hidden_feature(self) -> None:
        hidden = LinearTDValues(
            TDLearningConfig(
                version="bad-v1",
                eta=0.1,
                lambda_e=0.5,
                beta=0.9,
                evidence_scale=1.0,
                features=ValueFeatureConfig(
                    version="phi-bad-v1",
                    feature_names=("bias", "accumulator"),
                    position_scale_x=31.0,
                    position_scale_y=31.0,
                ),
            )
        )
        with self.assertRaisesRegex(ValueError, "unknown P-32"):
            hidden.features(state(20.0))


if __name__ == "__main__":
    unittest.main()
