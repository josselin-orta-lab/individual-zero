"""Stage-9 externally randomized food rewards, with recorded physical inputs."""
import unittest
from lab.stage9_random_reward_benchmark import (
    _audit_lived_hydration_provenance,
    preregistered_food_rewards, run_random_reward_negative_control,
)

def _technical_hydration_events() -> dict[str, dict[str, object]]:
    return {
        "command:1": {
            "kind": "command_experienced", "attempt_ref": "attempt:1",
            "t_monde": 1, "primitive": "boire", "parameters": {},
        },
        "world-transition:1": {
            "kind": "world_transition_experienced", "attempt_ref": "attempt:1",
            "t_monde": 1, "effects": {"drank": True},
        },
        "command:2": {
            "kind": "command_experienced", "attempt_ref": "attempt:2",
            "t_monde": 2, "primitive": "boire", "parameters": {},
        },
        "world-transition:2": {
            "kind": "world_transition_experienced", "attempt_ref": "attempt:2",
            "t_monde": 2, "effects": {"drank": True},
        },
    }


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
                "observed_step": 2,
                "cause_present": True,
            },
            {
                "identifier": "hydration:2",
                "episode_ref": "memory:one",
                "observation_ref": "world-transition:2",
                "observed_step": 3,
                "cause_present": True,
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
            _audit_lived_hydration_provenance(
                rows, witnesses, committed, _technical_hydration_events(),
            ), 1,
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
                _technical_hydration_events(),
            )
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                rows, witnesses, {
                    "memory:one": committed["memory:one"] - {"command:2"},
                },
                _technical_hydration_events(),
            )
        # Different world transitions cannot both claim one applied
        # command as an independent physical trial.
        reused_command = {
            **witnesses,
            "hydration:2": ("command:1", "world-transition:2"),
        }
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                rows, reused_command, committed, _technical_hydration_events(),
            )

    def test_rejects_witnesses_from_other_closed_memory_episodes(self):
        rows = [{
            "identifier": "hydration:1",
            "episode_ref": "memory:one",
            "observation_ref": "world-transition:1",
            "observed_step": 2,
            "cause_present": True,
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
            _audit_lived_hydration_provenance(
                rows, witnesses, split, _technical_hydration_events(),
            )

        # Re-labelling the row to the other episode also cannot launder it.
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                [{**rows[0], "episode_ref": "memory:two"}],
                witnesses, split, _technical_hydration_events(),
            )

        valid = {
            "memory:one": frozenset({"command:1", "world-transition:1"}),
            "memory:two": frozenset({"command:2", "world-transition:2"}),
        }
        extra = {
            "identifier": "hydration:2",
            "episode_ref": "memory:two",
            "observation_ref": "world-transition:2",
            "observed_step": 3,
            "cause_present": True,
        }
        both = {**witnesses, "hydration:2": ("command:2", "world-transition:2")}
        self.assertEqual(
            _audit_lived_hydration_provenance(
                [*rows, extra], both, valid, _technical_hydration_events(),
            ), 2,
        )

    def test_rejects_mismatched_physical_timing_and_action_types(self):
        rows = [{
            "identifier": "hydration:1",
            "episode_ref": "memory:one",
            "observation_ref": "world-transition:1",
            "observed_step": 2,
            "cause_present": True,
        }]
        refs = {"hydration:1": ("command:1", "world-transition:1")}
        closed = {
            "memory:one": frozenset({
                "command:1", "world-transition:1",
                "command:2", "world-transition:2",
            }),
        }
        source = _technical_hydration_events()
        self.assertEqual(
            _audit_lived_hydration_provenance(rows, refs, closed, source), 1,
        )
        for change in (
            ("command:1", "t_monde", 2),
            ("world-transition:1", "t_monde", 2),
            ("command:1", "primitive", "attendre"),
            ("command:1", "kind", "world_transition_experienced"),
            ("world-transition:1", "attempt_ref", "attempt:other"),
            ("command:1", "attempt_ref", "attempt:other"),
            ("command:1", "parameters", {"target": "water"}),
            ("world-transition:1", "effects", {"drank": False}),
        ):
            with self.subTest(change=change):
                event_ref, field, value = change
                damaged = {
                    key: dict(event) for key, event in source.items()
                }
                damaged[event_ref][field] = value
                with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
                    _audit_lived_hydration_provenance(
                        rows, refs, closed, damaged,
                    )
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                [{**rows[0], "observed_step": 3}],
                refs, closed, source,
            )

    def test_physically_executed_wait_is_an_independent_control_arm(self):
        row = {
            "identifier": "hydration:wait",
            "episode_ref": "memory:one",
            "observation_ref": "world-transition:2",
            "observed_step": 3,
            "cause_present": False,
        }
        witness = {"hydration:wait": ("command:2", "world-transition:2")}
        closed = {
            "memory:one": frozenset({
                "command:2", "world-transition:2",
            }),
        }
        source = _technical_hydration_events()
        source["command:2"]["primitive"] = "attendre"
        source["world-transition:2"]["effects"] = {"rest": "attendre"}
        self.assertEqual(
            _audit_lived_hydration_provenance([row], witness, closed, source),
            1,
        )
        # Labelling a drink as a passive wait, or a wait as an active
        # exposure, must not manufacture a controlled baseline.
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                [{**row, "cause_present": True}], witness, closed, source,
            )
        source["world-transition:2"]["effects"] = {"rest": "dormir"}
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                [row], witness, closed, source,
            )

    def test_one_execution_attempt_cannot_supply_two_independent_trials(self):
        observations = [
            {
                "identifier": "hydration:1", "episode_ref": "memory:one",
                "observation_ref": "world-transition:1",
                "observed_step": 2, "cause_present": True,
            },
            {
                "identifier": "hydration:2", "episode_ref": "memory:one",
                "observation_ref": "world-transition:2",
                "observed_step": 3, "cause_present": True,
            },
        ]
        witnesses = {
            "hydration:1": ("command:1", "world-transition:1"),
            "hydration:2": ("command:2", "world-transition:2"),
        }
        committed = {
            "memory:one": frozenset({
                "command:1", "world-transition:1",
                "command:2", "world-transition:2",
            }),
        }
        events = _technical_hydration_events()
        self.assertEqual(
            _audit_lived_hydration_provenance(
                observations, witnesses, committed, events,
            ), 1,
        )
        # Re-labelled events from the same scheduler attempt cannot
        # provide two independent physical trials, even with distinct
        # source-event IDs and distinct apparent world steps.
        events["command:2"]["attempt_ref"] = "attempt:1"
        events["world-transition:2"]["attempt_ref"] = "attempt:1"
        with self.assertRaisesRegex(AssertionError, "unique closed Memory"):
            _audit_lived_hydration_provenance(
                observations, witnesses, committed, events,
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
