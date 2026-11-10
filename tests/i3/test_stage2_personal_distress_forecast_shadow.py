"""Future first-person direct distress prediction via replayed memories, LAB ONLY."""
from copy import deepcopy
from math import isfinite
from unittest.mock import patch
import unittest

from i3.lab import stage2_personal_distress_forecast_shadow as LAB
from i3.lab import stage2_replay_predictive_negative_control as NEG


class ShadowPersonalDistressTests(unittest.TestCase):
    def setUp(self):
        self.source=NEG.synthetic_personal_mind(7)
        self.p=LAB.PersonalDistressHead(self.source)
        self.r=LAB.PersonalDistressHead(self.source)
        self.buffer=tuple(self.source.buffer)
        self.initial=NEG._mind_seal(self.source)

    def train_pair(self):
        self.p.apply(self.buffer,(0,1,2))
        self.r.apply(self.buffer,(3,4,5))
        self.assertEqual(self.p.training_updates,self.r.training_updates)
        self.assertNotEqual(self.p.weights,self.r.weights)

    def test_all_48_synthetic_heldout_forecast_trials_do_not_create_world(self):
        with patch("i3.modules.world.World.__init__",side_effect=AssertionError("NO WORLD")):
            result=LAB.rehearse()
        self.assertEqual(result["synthetic_cases"],48)
        self.assertEqual(result["replays_per_detached_head"],3)
        self.assertEqual(result["scored_heldout_future_observations"],48)
        self.assertGreater(result["different_memory_subsets"],0)
        self.assertGreater(result["different_frozen_predictions"],0)
        self.assertLessEqual(result["different_frozen_predictions"],48)
        self.assertEqual(sum(result[k] for k in (
            "priority_lower_synthetic_sq_loss",
            "random_lower_synthetic_sq_loss",
            "tied_synthetic_sq_loss")),48)
        self.assertTrue(result["all_future_forecasts_sealed_before_outcomes"])
        self.assertTrue(result["no_world_or_live_policy_modification"])
        self.assertTrue(result["no_physical_cognitive_debit"])
        self.assertEqual(result["scientific_lives"],0)
        self.assertTrue(result["no_survival_or_predictive_utility_generalization"])

    def test_same_count_different_personal_memories_change_frozen_prediction(self):
        self.train_pair()
        body=LAB._heldout_before(7)
        a,b=self.p.predict(body),self.r.predict(body)
        self.assertTrue(isfinite(a) and isfinite(b))
        self.assertNotEqual(a,b)
        self.assertEqual(NEG._mind_seal(self.source),self.initial)
        self.assertEqual(self.p.source_identity,self.r.source_identity)

    def test_no_replay_and_same_replay_memory_indices_are_exact_controls(self):
        body=LAB._heldout_before(7)
        self.assertEqual(self.p.predict(body),self.r.predict(body))
        self.p.apply(self.buffer,())
        self.r.apply(self.buffer,())
        self.assertEqual(self.p.predict(body),self.r.predict(body))
        self.p.apply(self.buffer,(0,1,2))
        self.r.apply(self.buffer,(0,1,2))
        self.assertEqual(self.p.weights,self.r.weights)
        self.assertEqual(self.p.predict(body),self.r.predict(body))

    def test_targets_are_from_observed_body_not_TD_value_bootstrap(self):
        after=(75.,63.,68.,85.,74.)
        original=self.p.target_from_actual_outcome(after,False)
        other=deepcopy(self.source)
        other.values=[[999999.]*6 for _ in other.gammas]
        head=LAB.PersonalDistressHead(other)
        self.assertEqual(original,head.target_from_actual_outcome(after,False))
        self.assertEqual(self.p.target_from_actual_outcome(after,True),
                         -self.source.d_max)
        with self.assertRaises(TypeError):
            self.p.target_from_actual_outcome(after,1)

    def test_preoutcome_sha_then_realized_target_then_closed(self):
        self.train_pair()
        monitor=LAB.PrequentialDistressAudit(self.source)
        before=LAB._heldout_before(7)
        frozen=monitor.freeze(identity="real-step-7",
                              priority_head=self.p,random_head=self.r,
                              before_body=before)
        self.assertTrue(frozen["different_forecast"])
        self.assertFalse(frozen["future_outcome_observed"])
        with self.assertRaises(PermissionError):
            monitor.report()
        observed=monitor.score(
            identity="real-step-7",
            preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
            actual_after_body=LAB._heldout_after(7),actual_dead=False)
        self.assertTrue(observed["target_is_actual_next_body_not_TD_bootstrap"])
        self.assertTrue(isfinite(observed["priority_squared_error"]))
        self.assertTrue(isfinite(observed["random_squared_error"]))
        self.assertEqual(observed["priority_minus_random_squared_error"],
                         observed["priority_squared_error"]-
                         observed["random_squared_error"])
        report=monitor.report()
        self.assertEqual(report["frozen_predictions"],1)
        self.assertEqual(report["scored_observed_outcomes"],1)
        self.assertEqual(report["explicitly_censored_outcomes"],0)
        self.assertTrue(report["all_windows_accounted"])
        self.assertFalse(report["actual_organism_cognitive_funding"])
        self.assertFalse(report["scientific_predictive_utility_claim"])
        self.assertEqual(NEG._mind_seal(self.source),self.initial)

    def test_terminal_outcome_is_adverse_observation_not_favorable_censor(self):
        self.train_pair()
        monitor=LAB.PrequentialDistressAudit(self.source)
        frozen=monitor.freeze(identity="dead-7",priority_head=self.p,
                              random_head=self.r,before_body=LAB._heldout_before(7))
        row=monitor.score(
            identity="dead-7",preoutcome_prediction_sha256=
                frozen["preoutcome_prediction_sha256"],
            actual_after_body=(10.,0.,0.,0.,0.),actual_dead=True)
        self.assertEqual(row["observed_next_intrinsic_reward"],-self.source.d_max)
        self.assertTrue(row["terminal_observed"])
        self.assertEqual(monitor.report()["scored_observed_outcomes"],1)

    def test_right_censor_no_target_no_zero_score_and_no_rerun(self):
        self.train_pair()
        monitor=LAB.PrequentialDistressAudit(self.source)
        frozen=monitor.freeze(identity="horizon",priority_head=self.p,
                              random_head=self.r,before_body=LAB._heldout_before(7))
        row=monitor.censor(identity="horizon",
             preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
             reason="HORIZON_BEFORE_NEXT_TRANSITION")
        self.assertEqual(row["status"],"CENSORED_NO_TARGET")
        self.assertIsNone(row["priority_squared_error"])
        self.assertFalse(row["zero_error_imputation"])
        report=monitor.report()
        self.assertEqual(report["scored_observed_outcomes"],0)
        self.assertEqual(report["explicitly_censored_outcomes"],1)
        with self.assertRaises(PermissionError):
            monitor.score(identity="horizon",
                preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
                actual_after_body=LAB._heldout_after(7),actual_dead=False)
        with self.assertRaises(PermissionError):
            monitor.freeze(identity="horizon",priority_head=self.p,
                           random_head=self.r,before_body=LAB._heldout_before(7))

    def test_source_cannot_be_swapped_between_shadow_training_arms(self):
        self.train_pair()
        other=NEG.synthetic_personal_mind(8)
        monitor=LAB.PrequentialDistressAudit(self.source)
        with self.assertRaises(PermissionError):
            monitor.freeze(identity="mix",priority_head=self.p,
                           random_head=LAB.PersonalDistressHead(other),
                           before_body=LAB._heldout_before(7))
        self.assertEqual(monitor.report()["frozen_predictions"],0)
        self.r.fit_replayed_personal_memory(self.buffer[6])
        with self.assertRaises(PermissionError):
            monitor.freeze(identity="unequal-count",priority_head=self.p,
                           random_head=self.r,before_body=LAB._heldout_before(7))

    def test_wrong_indices_malformed_bodies_and_tampered_seal_fail(self):
        for indices in ((-1,), (99,), (True,), (0,0),
                        tuple(range(17))):
            with self.subTest(indices=indices),self.assertRaises(ValueError):
                self.p.apply(self.buffer,indices)
        for body in ((1.,2.,3.),(70.,65.,float("nan"),90.,70.),
                     (70.,65.,1000.,90.,70.)):
            with self.subTest(body=body),self.assertRaises(ValueError):
                self.p.predict(body)
        self.train_pair()
        monitor=LAB.PrequentialDistressAudit(self.source)
        frozen=monitor.freeze(identity="sealed",priority_head=self.p,
                              random_head=self.r,before_body=LAB._heldout_before(7))
        with self.assertRaises(PermissionError):
            monitor.score(identity="sealed",preoutcome_prediction_sha256="0"*64,
                          actual_after_body=LAB._heldout_after(7),actual_dead=False)
        with self.assertRaises(TypeError):
            monitor.score(identity="sealed",
                preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
                actual_after_body=LAB._heldout_after(7),actual_dead=1)
        with self.assertRaises(ValueError):
            monitor.censor(identity="sealed",
                preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
                reason="IGNORE_BAD_RESULT")
        monitor.score(identity="sealed",
            preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
            actual_after_body=LAB._heldout_after(7),actual_dead=False)
        with self.assertRaises(PermissionError):
            monitor.score(identity="sealed",
                preoutcome_prediction_sha256=frozen["preoutcome_prediction_sha256"],
                actual_after_body=LAB._heldout_after(7),actual_dead=False)


if __name__=="__main__":
    unittest.main()
