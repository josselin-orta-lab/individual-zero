"""Positive-water Stage-9 control: actions selected by the real individual."""
from __future__ import annotations

import unittest

from lab.stage9_positive_hydration_benchmark import (
    POSITIVE_HYDRATION_VARIANTS,
    run_positive_hydration_diagnostic,
)
from lab.stage9_random_reward_benchmark import (
    run_random_reward_negative_control,
)


class PositiveHydrationBenchmarkTests(unittest.TestCase):
    def test_same_food_schedule_distinguishes_positive_water_from_null_control(self):
        # Reuse the negative control's seeded food schedule. The bench only
        # changes world physics; it cannot inject commands or causal claims.
        positive = run_positive_hydration_diagnostic(
            campaign_seed=42, world_variant="small_water_gain", steps=14,
        )
        negative = run_random_reward_negative_control(
            campaign_seed=42, world_variant="null_water_reference",
            bench_seed_false_hypothesis=False, steps=14,
        )
        self.assertEqual(positive.schedule_sha256, negative.schedule_sha256)
        self.assertEqual(positive.scientific_gate, None)
        self.assertIsNone(negative.scientific_gate)
        self.assertGreaterEqual(positive.applied_drink_commands, 1)
        self.assertGreaterEqual(positive.closed_drink_observations, 1)
        self.assertGreaterEqual(positive.positive_drink_observations, 1)
        self.assertEqual(negative.lived_positive_drink_observations, 0)
        self.assertGreaterEqual(
            positive.closed_hydration_observations,
            positive.positive_drink_observations,
        )
        self.assertEqual(
            positive.independent_closed_episodes,
            positive.closed_hydration_observations,
        )
        self.assertGreaterEqual(
            positive.closed_memory_episodes,
            positive.independent_closed_episodes,
        )
        self.assertGreaterEqual(positive.pending_hydration_exposures, 0)
        self.assertGreaterEqual(positive.pending_causal_observations, 0)
        self.assertEqual(
            positive.observed_hydration_refs,
            tuple(sorted(set(positive.observed_hydration_refs))),
        )

    def test_multiple_seeded_physical_variants_are_deterministic_diagnostics(self):
        valid_reasons = {
            "no_closed_drinking_observations",
            "no_observed_positive_drinking_effect",
            "fewer_than_n1_positive_drinking_episodes",
            "no_independent_matched_wait_control",
            "fewer_than_n1_matched_positive_episodes",
            "eligible_for_contextual_base_rate_check",
        }
        for variant in POSITIVE_HYDRATION_VARIANTS:
            for seed in (41, 43):
                with self.subTest(variant=variant, seed=seed):
                    args = dict(
                        campaign_seed=seed,
                        world_variant=variant,
                        steps=18,
                    )
                    first = run_positive_hydration_diagnostic(**args)
                    second = run_positive_hydration_diagnostic(**args)
                    self.assertEqual(first, second)
                    self.assertEqual(first.scientific_gate, None)
                    self.assertIn(first.missing_evidence, valid_reasons)
                    self.assertEqual(len(first.journal_sha256), 64)
                    self.assertEqual(
                        first.qualifying_n1,
                        first.positive_drinks_with_matched_controls >= 2,
                    )
                    self.assertLessEqual(
                        first.positive_drinks_with_matched_controls,
                        first.positive_drink_observations,
                    )
                    self.assertGreaterEqual(
                        first.independent_closed_episodes,
                        first.closed_drink_observations,
                    )
                    self.assertLessEqual(
                        sum(n for _, n in first.causal_test_unpredicted_proposal_reasons),
                        first.causal_test_proposal_events,
                    )
                    self.assertEqual(
                        first.applied_causal_test_drinks, 0,
                        "without intrinsic evidence, test proposals cannot execute",
                    )

    def test_invalid_protocol_parameters_are_not_accepted(self):
        for seed, steps, variant in (
            (True, 14, "small_water_gain"),
            (-1, 14, "small_water_gain"),
            (41, 5, "small_water_gain"),
            (41, True, "small_water_gain"),
            (41, 14, "imaginary_world"),
        ):
            with self.subTest(seed=seed, steps=steps, variant=variant):
                with self.assertRaises(ValueError):
                    run_positive_hydration_diagnostic(
                        campaign_seed=seed,
                        steps=steps,
                        world_variant=variant,
                    )


if __name__ == "__main__":
    unittest.main()
