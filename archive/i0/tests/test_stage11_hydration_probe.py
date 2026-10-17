"""Stage-11 public developmental hydration funnel, NEVER held-out acceptance."""
import unittest
import json

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_hydration_probe import run_public_hydration_funnel


class Stage11HydrationProbeTests(unittest.TestCase):
    def test_public_run_is_reproducible_and_does_not_forge_science(self):
        first = run_public_hydration_funnel(seed=41, world="small_water_gain", steps=18)
        second = run_public_hydration_funnel(seed=41, world="small_water_gain", steps=18)
        self.assertEqual(first, second)
        self.assertEqual(first.classification, "development_only_not_heldout")
        self.assertIsNone(first.scientific_verdict)
        self.assertFalse(first.golden_stage9_frozen)
        self.assertFalse(first.prospective_prediction_enabled)
        self.assertEqual(first.exploration_visit_ceiling, 2)
        self.assertEqual(first.exploration_policy_version, "p48-development-v2")
        self.assertEqual(first.stage11_prospective_prediction_count, 0)
        self.assertEqual(first.stage11_prospective_source_count, 0)
        self.assertEqual(first.stage11_physical_comparator_join_candidates, 0)
        self.assertEqual(first.stage11_comparison_water_values, ())
        self.assertEqual(first.schedule_sha256, second.schedule_sha256)
        self.assertGreaterEqual(first.stage11_test_proposals, 0)
        self.assertGreaterEqual(first.stage11_unscored_evaluations, 0)
        self.assertGreaterEqual(first.stage11_scored_intrinsic_evaluations, 0)
        self.assertLessEqual(first.stage11_scored_distinct_options,
                             first.stage11_scored_intrinsic_evaluations)
        self.assertLessEqual(first.stage11_unpredicted_proposals,
                             first.stage11_test_proposals)
        self.assertEqual(
            first.stage11_unpredicted_proposals,
            sum(value for _, value in first.stage11_prediction_unavailability),
        )
        self.assertLessEqual(first.stage11_lived_actions_physically_closed,
                             first.stage11_lived_causal_actions_pending)
        self.assertLessEqual(first.stage11_published_agency_reports_for_tests,
                             first.stage11_executed_test_commands)
        self.assertLessEqual(first.stage11_verified_interventions,
                             first.stage11_executed_test_commands)
        self.assertEqual(len(first.stage11_applied_test_steps),
                         first.stage11_executed_test_commands)
        self.assertEqual(len(first.stage11_action_custody_at_send),
                         first.stage11_executed_test_commands)
        for t, option, water_before, version, registered in (
            first.stage11_action_custody_at_send
        ):
            self.assertIn(t, first.stage11_applied_test_steps)
            self.assertTrue(option.startswith("option:causal-test:"))
            self.assertTrue(0 <= water_before <= 100)
            self.assertTrue(version is None or version >= 1)
            self.assertIs(type(registered), bool)
        self.assertEqual(len(first.stage11_physical_action_custody),
                         first.stage11_pending_test_actions)
        self.assertEqual(len(first.stage11_test_comparator_sent_steps),
                         first.stage11_test_comparison_events)
        self.assertEqual(len(first.stage11_prospective_lineage),
                         first.stage11_prospective_prediction_count)
        self.assertEqual(
            sum(row[3] for row in first.stage11_test_comparison_classes),
            first.stage11_test_comparison_events,
        )
        self.assertLessEqual(
            first.stage11_test_comparison_events,
            first.stage11_executed_test_commands,
        )
        self.assertLessEqual(
            first.stage11_published_test_agency_reports,
            first.stage11_test_comparison_events,
        )
        self.assertLessEqual(
            first.stage11_causal_action_memory_closed,
            first.stage11_executed_test_commands,
        )
        self.assertLessEqual(
            first.stage11_verified_interventions,
            first.stage11_causal_intervention_stagings,
        )
        self.assertLessEqual(
            first.stage11_causal_intervention_stagings,
            first.stage11_causal_action_memory_closed,
        )
        self.assertGreaterEqual(first.stage11_pending_test_actions, 0)
        # Actual executed information-seeking acts now create visit
        # counters, even when P-47 cannot later confirm an intervention.
        self.assertGreaterEqual(
            first.stage11_exploration_visits,
            first.stage11_executed_test_commands,
        )
        self.assertGreaterEqual(first.stage11_exploration_stagnant_visits, 0)
        self.assertLessEqual(
            first.stage11_exploration_stagnant_visits,
            first.stage11_exploration_visits,
        )
        self.assertTrue(all(
            count > 0 and isinstance(status, str)
            and isinstance(attribution, str) and isinstance(water, str)
            for status, attribution, water, count
            in first.stage11_test_comparison_classes
        ))
        data = first.as_dict()
        digest = data.pop("evidence_sha256")
        self.assertEqual(digest, sha256_hex(canonical_causal_bytes(data)))
        # Preserve the diagnostic readout in the small software CI log.
        # This is NOT an independent protocol registration or scientific GO.
        print("stage11_public_hydration_diagnostic=" + json.dumps(
            first.as_dict(), sort_keys=True, separators=(",", ":")
        ))

    def test_prior_lived_forecast_is_separately_opt_in_and_never_scientific(self):
        # Public world and seed, isolated run. Prediction means prospective
        # descriptive expectation, not proof that the individual caused it.
        diagnostic = run_public_hydration_funnel(
            seed=41, world="small_water_gain", steps=18,
            enable_lived_prediction=True,
        )
        self.assertTrue(diagnostic.prospective_prediction_enabled)
        self.assertEqual(diagnostic.classification,
                         "development_only_not_heldout")
        self.assertIsNone(diagnostic.scientific_verdict)
        self.assertFalse(diagnostic.golden_stage9_frozen)
        self.assertLessEqual(
            diagnostic.stage11_prospective_prediction_count,
            diagnostic.stage11_executed_test_commands,
        )
        self.assertGreaterEqual(
            diagnostic.stage11_prospective_source_count,
            diagnostic.stage11_prospective_prediction_count,
        )
        self.assertLessEqual(
            diagnostic.stage11_verified_interventions,
            diagnostic.stage11_causal_intervention_stagings,
        )
        print("stage11_prospective_hydration_diagnostic=" + json.dumps(
            diagnostic.as_dict(), sort_keys=True, separators=(",", ":")
        ))

    def test_declared_public_three_visit_prediction_opportunity(self):
        # Predeclared public seed, world, time window, and *alternative*
        # development-only P-48 ceiling. Zero forecasts is a valid result.
        row = run_public_hydration_funnel(
            seed=41, world="small_water_gain", steps=24,
            enable_lived_prediction=True,
            exploration_policy="three_visit_window",
        )
        self.assertEqual(row.classification, "development_only_not_heldout")
        self.assertEqual(row.protocol_version, "stage11-public-hydration-funnel-dev-v7")
        self.assertEqual(row.exploration_policy_version, "p48-three-visit-window-dev-v1")
        self.assertEqual(row.exploration_visit_ceiling, 3)
        self.assertLessEqual(row.stage11_exploration_visits, 3)
        self.assertLessEqual(row.stage11_prospective_prediction_count,
                             row.stage11_executed_test_commands)
        self.assertGreaterEqual(row.stage11_prospective_source_count,
                                row.stage11_prospective_prediction_count)
        self.assertIsNone(row.scientific_verdict)
        self.assertFalse(row.golden_stage9_frozen)
        self.assertLessEqual(row.stage11_verified_interventions,
                             row.stage11_causal_intervention_stagings)
        for entry in row.stage11_test_comparison_classes:
            self.assertNotEqual(entry[2], "unreported")
        for sent, observed_step, predicted, observed, precision, status in (
            row.stage11_comparison_water_values
        ):
            self.assertGreater(observed_step, sent)
            self.assertTrue(0 <= predicted <= 100 and 0 <= observed <= 100)
            self.assertGreaterEqual(precision, 0)
            if status == "conforming":
                self.assertLessEqual(abs(observed-predicted), precision)
        self.assertLessEqual(row.stage11_physical_comparator_join_candidates,
                             row.stage11_published_test_agency_reports)
        self.assertEqual(row.stage11_physical_comparator_join_candidates,
                         sum(closed and joined for _, _, _, closed, joined
                             in row.stage11_physical_action_custody))
        for sent, source_steps in row.stage11_prospective_lineage:
            self.assertIn(sent, row.stage11_applied_test_steps)
            self.assertTrue(all(old < sent for old in source_steps))
        self.assertTrue(set(row.stage11_test_comparator_sent_steps).issubset(
            set(row.stage11_applied_test_steps)
        ))
        print("stage11_three_visit_opportunity_diagnostic=" + json.dumps(
            row.as_dict(), sort_keys=True, separators=(",", ":")
        ))

    def test_predeclared_public_32step_memory_comparator_join_window(self):
        # A fixed public extension of the 24-step result, not scientific
        # confirmation, tuning, or manipulation of physical memory records.
        result = run_public_hydration_funnel(
            seed=41, world="small_water_gain", steps=32,
            enable_lived_prediction=True,
            exploration_policy="three_visit_window",
        )
        self.assertIsNone(result.scientific_verdict)
        self.assertEqual(result.classification, "development_only_not_heldout")
        self.assertFalse(result.golden_stage9_frozen)
        self.assertEqual(result.exploration_visit_ceiling, 3)
        self.assertLessEqual(result.stage11_verified_interventions,
                             result.stage11_causal_intervention_stagings)
        self.assertLessEqual(
            result.stage11_physical_comparator_join_candidates,
            result.stage11_published_test_agency_reports,
        )
        self.assertEqual(
            len(result.stage11_physical_action_custody),
            result.stage11_pending_test_actions,
        )
        self.assertEqual(
            len(result.stage11_applied_test_steps),
            result.stage11_executed_test_commands,
        )
        self.assertEqual(
            len(result.stage11_action_custody_at_send),
            result.stage11_executed_test_commands,
        )
        self.assertEqual(
            tuple(row[0] for row in result.stage11_action_custody_at_send),
            result.stage11_applied_test_steps,
        )
        self.assertEqual(
            result.stage11_physical_comparator_join_candidates,
            sum(closed and matched for _, _, _, closed, matched
                in result.stage11_physical_action_custody),
        )
        for status, attribution, water_effect, count in result.stage11_test_comparison_classes:
            self.assertGreater(count, 0)
            self.assertNotEqual(water_effect, "unreported")
        print("stage11_32step_physical_comparator_followup=" + json.dumps(
            result.as_dict(), sort_keys=True, separators=(",", ":")
        ))

    def test_rejects_nonpublic_variants_and_invalid_seeds(self):
        for args in (
            {"seed": -1}, {"seed": True}, {"steps": 0},
            {"world": "sealed_hidden"}, {"world": "null_water_reference"},
            {"enable_lived_prediction": "yes"},
            {"exploration_policy": "sealed_hindsight"},
        ):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    run_public_hydration_funnel(**args)


if __name__ == "__main__":
    unittest.main()
