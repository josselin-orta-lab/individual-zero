"""Stage-9 externally randomized food rewards, with recorded physical inputs."""
import unittest
from lab.stage9_random_reward_benchmark import (
    preregistered_food_rewards, run_random_reward_negative_control,
)

class RandomRewardNegativeControlTests(unittest.TestCase):
    def test_schedule_seeded_before_actions_and_counterbalanced(self):
        a = preregistered_food_rewards(campaign_seed=42, steps=14)
        self.assertEqual(a, preregistered_food_rewards(campaign_seed=42, steps=14))
        self.assertEqual(len(a), 13)
        self.assertEqual(tuple(e.t_monde for e in a), tuple(range(2, 15)))
        self.assertEqual(sum(e.payload["food"] == 70.0 for e in a), 6)
        self.assertEqual(len({(e.t_monde, e.sequence) for e in a}), 13)

    def test_invalid_protocol_is_rejected(self):
        for seed, steps in ((-1, 14), (True, 14), (1, 5), (1, True)):
            with self.subTest(seed=seed, steps=steps):
                with self.assertRaises(ValueError):
                    preregistered_food_rewards(campaign_seed=seed, steps=steps)

    def test_real_world_negative_control_is_replayed(self):
        first = run_random_reward_negative_control(
            campaign_seed=42, steps=14,
        )
        second = run_random_reward_negative_control(
            campaign_seed=42, steps=14,
        )
        self.assertEqual(first, second)
        self.assertEqual(first.logged_inputs, 13)
        self.assertGreaterEqual(first.drinking_commands, 1)
        self.assertTrue(first.bench_seeded_false_hypothesis)
        self.assertFalse(first.established_false_rule)
        self.assertIsNone(first.scientific_superstition_rate)
        self.assertIsNone(first.scientific_gate)

    def test_bench_does_not_claim_spontaneous_belief(self):
        result = run_random_reward_negative_control(
            campaign_seed=43, steps=14,
            bench_seed_false_hypothesis=False,
        )
        self.assertFalse(result.bench_seeded_false_hypothesis)
        self.assertFalse(result.established_false_rule)
        self.assertIsNone(result.scientific_gate)

if __name__ == "__main__":
    unittest.main()
