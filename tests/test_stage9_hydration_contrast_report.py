"""Deterministic diagnostic of matched water-physics worlds."""
import unittest
from lab.stage9_hydration_contrast_report import run_hydration_contrast_report, _positive_gap

class Stage9HydrationContrastTests(unittest.TestCase):
    def test_matched_worlds_report_real_opportunities_without_acceptance(self):
        first=run_hydration_contrast_report(seeds=(42,),steps=14)
        second=run_hydration_contrast_report(seeds=(42,),steps=14)
        self.assertEqual(first,second)
        self.assertEqual(first.to_json(),second.to_json())
        self.assertEqual(first.matched_pairs_checked,1)
        self.assertEqual(len(first.cases),4)
        self.assertEqual(first.acceptance_status,"open")
        self.assertFalse(first.golden_stage9_frozen)
        null,positive,exploratory,aligned=first.cases
        self.assertEqual(null.schedule_sha256,positive.schedule_sha256)
        self.assertEqual(null.schedule_sha256,exploratory.schedule_sha256)
        self.assertEqual(null.positive_drinks,0)
        self.assertGreaterEqual(positive.positive_drinks,1)
        self.assertEqual(positive.comparison_role,"matched_positive_water_gain")
        self.assertEqual(exploratory.comparison_role,"exploratory_changed_water_decay")
        self.assertEqual(aligned.comparison_role,"exploratory_model_aligned_prediction")
        self.assertEqual(aligned.schedule_sha256,null.schedule_sha256)
        # The aligned physics is a controlled *opportunity*, not a forced
        # learning result. It may saturate water before n1 and independent
        # controls exist; report missing evidence rather than assuming success.
        if aligned.first_hypothesis_step is None:
            self.assertNotIn(aligned.causal_status, (
                "hypothese_causale", "testee_par_intervention", "etablie",
            ))
            self.assertEqual(aligned.drinks_after_hypothesis, 0)
        else:
            self.assertGreaterEqual(aligned.first_hypothesis_step, 1)
            self.assertIn(aligned.causal_status, (
                "hypothese_causale", "testee_par_intervention", "etablie",
            ))
        self.assertGreaterEqual(aligned.drinks_after_hypothesis, 0)
        self.assertGreaterEqual(aligned.unscored_test_evaluations, 0)
        self.assertGreaterEqual(aligned.published_interventions, 0)
        self.assertTrue(aligned.missing_evidence)
        self.assertGreaterEqual(aligned.post_hypothesis_decision_steps, 0)
        self.assertGreaterEqual(aligned.designated_test_target_steps, 0)
        self.assertLessEqual(
            aligned.designated_test_target_steps,
            aligned.post_hypothesis_decision_steps,
        )
        self.assertLessEqual(
            aligned.accessible_test_context_steps,
            aligned.designated_test_target_steps,
        )
        self.assertGreaterEqual(aligned.causal_test_proposals, 0)
        self.assertGreaterEqual(aligned.causal_test_registration_events, 0)
        self.assertLessEqual(
            aligned.accepted_causal_test_registrations,
            aligned.causal_test_registration_events,
        )
        self.assertLessEqual(
            aligned.unscored_test_evaluations,
            aligned.causal_test_evaluation_events,
        )
        self.assertTrue(all(row.scientific_gate is None for row in first.cases))
        self.assertEqual(len(first.as_dict()["evidence_sha256"]),64)

    def test_first_observed_blocker_is_explained(self):
        common=dict(
            applied_drinks=2,closed_drinks=2,positive_drinks=2,
            wait_controls=0,matched_positive_drinks=0,n1=2,status="aucun",
            pending_hydration_exposures=0,pending_causal_observations=0,
        )
        self.assertEqual(_positive_gap(**common),"no_naturally_selected_wait_controls")
        common["wait_controls"]=1
        self.assertEqual(_positive_gap(**common),"insufficient_context_matched_control_exposures")
        common["matched_positive_drinks"]=2
        self.assertEqual(_positive_gap(**common),"base_rate_or_evidence_admission")
        common["pending_causal_observations"]=1
        self.assertEqual(_positive_gap(**common),"pending_causal_publication")
        common["status"]="correlation_observee"
        self.assertEqual(_positive_gap(**common),"observed_alternatives_or_next_publication_required")

    def test_invalid_campaign_design_rejected(self):
        for seeds,steps in (((),14),((42,42),14),((True,),14),((42,),True),((42,),5)):
            with self.subTest(seeds=seeds,steps=steps):
                with self.assertRaises(ValueError):
                    run_hydration_contrast_report(seeds=seeds,steps=steps)

if __name__=="__main__":
    unittest.main()
