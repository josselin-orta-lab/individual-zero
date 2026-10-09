"""Stage-9 externally randomized food rewards, with recorded physical inputs."""
import unittest
from lab.stage9_random_reward_benchmark import (
    _audit_lived_hydration_provenance,
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

    def test_physical_hydration_witnesses_may_share_one_memory_episode(self):
        rows = [
            {
                "identifier": "hydration:1",
                "episode_ref": "memory:one",
                "observation_ref": "world-transition:1",
            },
            {
                "identifier": "hydration:2",
                "episode_ref": "memory:one",
                "observation_ref": "world-transition:2",
            },
        ]
        witnesses = {
            "hydration:1": ("command:1", "world-transition:1"),
            "hydration:2": ("command:2", "world-transition:2"),
        }
        committed = {
            "memory:one": frozenset({
                "command:1", "command:2",
                "world-transition:1", "world-transition:2",
            }),
        }
        self.assertEqual(
            _audit_lived_hydration_provenance(rows, witnesses, committed), 1,
        )
        # Reusing a physical transition with another observation ID or
        # episode alias is not an additional source of causal evidence.
        duplicated = [
            rows[0],
            {**rows[1], "episode_ref": "memory:alias",
             "observation_ref": "world-transition:1"},
        ]
        alias_witnesses = {
            **witnesses,
            "hydration:2": ("command:2", "world-transition:1"),
        }
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                duplicated, alias_witnesses, committed,
            )
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                rows, witnesses, {
                    "memory:one": committed["memory:one"] - {"command:2"},
                },
            )

    def test_rejects_witnesses_from_other_closed_memory_episodes(self):
        rows = [{
            "identifier": "hydration:1",
            "episode_ref": "memory:one",
            "observation_ref": "world-transition:1",
        }]
        witnesses = {
            "hydration:1": ("command:1", "world-transition:1"),
        }
        # Both source IDs are in committed Memory, but not together in the
        # episode claimed by this causal row. A global ref union falsely
        # accepts these mismatched physical witnesses.
        split = {
            "memory:one": frozenset({"command:1"}),
            "memory:two": frozenset({"world-transition:1"}),
        }
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(rows, witnesses, split)

        # Re-labelling the row to the other episode also cannot launder it.
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                [{**rows[0], "episode_ref": "memory:two"}],
                witnesses, split,
            )

        valid = {
            "memory:one": frozenset({"command:1", "world-transition:1"}),
            "memory:two": frozenset({"command:2", "world-transition:2"}),
        }
        extra = {
            "identifier": "hydration:2",
            "episode_ref": "memory:two",
            "observation_ref": "world-transition:2",
        }
        both = {**witnesses, "hydration:2": ("command:2", "world-transition:2")}
        self.assertEqual(
            _audit_lived_hydration_provenance([*rows, extra], both, valid), 2,
        )

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
        self.assertGreaterEqual(len(first.verified_null_drink_transitions), 1)
        self.assertEqual(first.observed_false_rule_rate, 0.0)
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
