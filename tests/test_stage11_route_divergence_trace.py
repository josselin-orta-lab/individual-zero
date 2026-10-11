"""Public retrospective Stage-11 decision trace, NOT a scientific explanation.

Previous behavioral outcome was observed BEFORE this trace was specified.
This checks exact independent replay and only already journaled causal data.
"""
from unittest import TestCase

from lab.stage11_route_divergence_trace_probe import (
    PREVIOUS_JOURNAL_SHA256, PROTOCOL, VARIANTS,
    run_public_route_divergence_trace,
)


class Stage11RoutedDecisionDivergenceTraceTests(TestCase):
    def test_fixed_negative_step5_trace_is_reproducible_and_observational(self):
        traces = {}
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                observed = run_public_route_divergence_trace(variant=variant)
                independent = run_public_route_divergence_trace(variant=variant)
                self.assertEqual(observed, independent)
                self.assertEqual(observed.to_json(), independent.to_json())
                self.assertEqual(observed.protocol_version, PROTOCOL)
                self.assertFalse(observed.heldout)
                self.assertIsNone(observed.scientific_verdict)
                self.assertEqual(observed.planning_uc, 4)
                self.assertEqual(observed.exploration_uc, 4)
                self.assertEqual(
                    observed.reproduced_journal_sha256,
                    PREVIOUS_JOURNAL_SHA256[variant],
                )
                self.assertEqual(
                    observed.prior_result_journal_sha256,
                    observed.reproduced_journal_sha256,
                )
                self.assertEqual(
                    tuple(s[0] for s in observed.snapshot_ids_and_hashes),
                    (4, 5),
                )
                self.assertEqual(len(observed.first_four_actions), 4)
                self.assertEqual(len(observed.integrity_after_steps_3_to_5), 3)
                self.assertEqual(
                    tuple(row[0] for row in observed.integrity_after_steps_3_to_5),
                    (3, 4, 5),
                )
                self.assertEqual(
                    tuple(row[0] for row in observed.modulation_profiles_after_steps_3_to_5),
                    (3, 4, 5),
                )
                # Technical observations, not invented free cognitive work:
                # real published S_t and Competition trace entries for step 5.
                self.assertTrue(any(
                    row["kind"] == "s_t_published"
                    for row in observed.step5_causal_events
                ))
                self.assertTrue(any(
                    row["kind"] == "competition_cycle"
                    for row in observed.step5_causal_events
                ))
                for event in observed.step5_causal_events:
                    if event["kind"] != "competition_cycle":
                        continue
                    for candidate in event["data"]["traces"]:
                        self.assertIs(type(candidate["crossed"]), bool)
                        self.assertIn("accumulator_after", candidate)
                        self.assertIn("threshold", candidate)
                traces[variant] = observed
                print("stage11_public_route_divergence_trace=" + observed.to_json())

        control, hazard = traces["control"], traces["hidden_transient"]
        # The first four applied actions (including return hops) were already
        # documented as identical. The first different actual command is t=5.
        self.assertEqual(
            control.initial_perception_prefix_sha256,
            hazard.initial_perception_prefix_sha256,
        )
        self.assertEqual(control.first_four_actions, hazard.first_four_actions)
        self.assertEqual(control.step5_action[1], "se_deplacer")
        self.assertIn("frontier:2:3:", control.step5_action[2])
        self.assertEqual(hazard.step5_action[1], "attendre")
        self.assertEqual(hazard.step5_action[3], "fallback")
        self.assertEqual(
            control.integrity_after_steps_3_to_5[0][1], 100.0,
        )
        self.assertEqual(
            hazard.integrity_after_steps_3_to_5[0][1], 90.0,
        )
        # These physical/decision differences must not be labeled as
        # knowledge of the unseen danger, recovery, or a causal experiment.

    def test_unregistered_diagnostic_inputs_rejected(self):
        for variant in ("", "junction_open", "unknown", None, True):
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                run_public_route_divergence_trace(variant=variant)
