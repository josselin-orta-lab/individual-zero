"""Actual TD replay selection vs unchanged effects: complete software falsifier."""
from copy import deepcopy
from math import isfinite
from unittest.mock import patch
import unittest

from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab import stage2_prequential_effect_audit as PRE


class ReplayPredictiveNegativeControlTests(unittest.TestCase):
    def test_finite_48_synthetic_no_world_and_zero_effect_prediction_difference(self):
        with patch("i3.modules.world.World.__init__",side_effect=AssertionError("NO WORLD")):
            report=NEG.rehearse()
        self.assertEqual(report["schema"],NEG.SCHEMA)
        self.assertEqual(report["synthetic_cases"],48)
        self.assertEqual(report["detached_td_replays_per_arm"],3)
        self.assertGreater(report["different_memory_subset_cases"],0)
        self.assertGreater(report["different_learned_value_cases"],0)
        self.assertGreater(report["different_value_residual_readout_cases"],0)
        self.assertEqual(report["different_one_step_effect_forecast_cases"],0)
        self.assertTrue(report["effects_model_unchanged_in_every_case"])
        self.assertTrue(report["original_mind_unchanged_in_every_case"])
        self.assertTrue(report["no_world_or_life_executed"])
        self.assertTrue(report["observer_cpu_is_external"])
        self.assertEqual(report["scientific_lives"],0)
        self.assertFalse(report["prospective_calibrated_predictive_utility"])

    def test_real_td_on_personal_nonempty_effect_model_is_only_value_sensitive(self):
        src=NEG.synthetic_personal_mind(7)
        original=NEG._mind_seal(src)
        self.assertGreater(len(src.effects.stats),0)
        self.assertNotEqual(src.effects.predict(("boire",))[0],(0.,)*5)
        receipt=NEG.contrast(src,count=3,life_seed=9900007,
                             sleep_ordinal=8)
        self.assertEqual(receipt["replays_in_each_detached_copy"],3)
        self.assertTrue(receipt["same_effects_model_after_replay"])
        self.assertTrue(receipt["same_action_effect_predictions"])
        self.assertEqual(NEG._mind_seal(src),original)
        self.assertFalse(receipt["observer_physical_debit"])
        self.assertFalse(receipt["predictive_utility_claim"])

    def test_zero_replay_is_a_real_negative_control_not_positive_claim(self):
        src=NEG.synthetic_personal_mind(0)
        r=NEG.contrast(src,count=0,life_seed=42,sleep_ordinal=0)
        self.assertEqual(r["replays_in_each_detached_copy"],0)
        self.assertFalse(r["different_memory_subset"])
        self.assertFalse(r["different_values"])
        self.assertEqual(r["value_vector_L1"],0)
        self.assertEqual(r["value_residual_readout_L1"],0)
        self.assertTrue(r["same_action_effect_predictions"])

    def test_wrong_replay_count_seed_or_body_fails_before_td(self):
        src=NEG.synthetic_personal_mind(0)
        for k in (-1,17,True,3.5):
            with self.subTest(count=k),self.assertRaises(ValueError):
                NEG.contrast(src,count=k,life_seed=1,sleep_ordinal=1)
        for fields in ({"life_seed":-1},{"life_seed":True},
                       {"sleep_ordinal":-1},{"sleep_ordinal":1.2}):
            with self.subTest(fields=fields),self.assertRaises(ValueError):
                NEG.contrast(src,**({ "count":2,"life_seed":1,"sleep_ordinal":1 } | fields))
        for body in ((80.,65.,70.),(80.,65.,float("nan"),90.,70.),
                     (80.,65.,110.,90.,70.),(True,65.,60.,90.,70.)):
            with self.subTest(body=body),self.assertRaises(ValueError):
                NEG.contrast(src,count=2,life_seed=1,sleep_ordinal=1,body=body)


class PrequentialEffectAuditTests(unittest.TestCase):
    def setUp(self):
        self.source=NEG.synthetic_personal_mind(1)
        self.p=deepcopy(self.source)
        self.r=deepcopy(self.source)
        # Make different learned VALUES without touching the effects model.
        self.p._td(self.p.buffer[0][1],self.p.buffer[0][2],False)
        self.r._td(self.r.buffer[-1][1],self.r.buffer[-1][2],False)
        self.assertNotEqual(self.p.values,self.r.values)
        self.assertEqual(self.p.effects.stats,self.r.effects.stats)
        self.audit=PRE.PrequentialEffectAudit()
        self.body=NEG.BODY
        self.action=("boire",)

    def freeze(self,identity="same-later-real-step"):
        return self.audit.freeze(identity=identity,priority_mind=self.p,
                                 random_mind=self.r,before_body=self.body,
                                 actual_action_key=self.action)

    def test_precommit_real_outcome_proper_mean_score_not_replay_value(self):
        source_before=NEG._mind_seal(self.source)
        f=self.freeze()
        self.assertFalse(f["future_outcome_seen"])
        self.assertTrue(f["same_effects_prediction"])
        result=self.audit.score(
            identity="same-later-real-step",
            preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
            actual_action_key=self.action,
            actual_after_body=(78.,64.,72.,88.,79.))
        self.assertEqual(result["status"],"OBSERVED_SAME_ACTION")
        self.assertGreater(result["priority_mean_squared_error"],0)
        self.assertEqual(result["priority_mean_squared_error"],
                         result["random_mean_squared_error"])
        self.assertEqual(result["difference_priority_minus_random"],0.0)
        self.assertTrue(result["proper_point_mean_score_only"])
        summary=self.audit.report()
        self.assertEqual(summary["forecast_commits"],1)
        self.assertEqual(summary["realized_scored"],1)
        self.assertEqual(summary["right_censored_no_imputation"],0)
        self.assertEqual(summary["sum_paired_loss_difference"],0)
        self.assertTrue(summary["no_evidence_of_replay_predictive_utility"])
        self.assertEqual(NEG._mind_seal(self.source),source_before)

    def test_censor_missing_next_actual_outcome_and_prohibit_score_imputation(self):
        f=self.freeze("censored")
        with self.assertRaises(PermissionError):
            self.audit.report()
        r=self.audit.censor(
            identity="censored",
            preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
            reason="TERMINAL_BEFORE_NEXT_ACTION")
        self.assertIsNone(r["priority_mean_squared_error"])
        self.assertTrue(r["not_imputed_as_zero"])
        report=self.audit.report()
        self.assertEqual(report["forecast_commits"],1)
        self.assertEqual(report["right_censored_no_imputation"],1)
        self.assertEqual(report["realized_scored"],0)
        with self.assertRaises(PermissionError):
            self.audit.score(identity="censored",
                             preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                             actual_action_key=self.action,actual_after_body=self.body)
        with self.assertRaises(PermissionError):
            self.freeze("censored")

    def test_wrong_action_hash_outcome_or_duplicate_cannot_retroactively_rewrite(self):
        with self.assertRaises(PermissionError):
            self.audit.score(
                identity="missing",preoutcome_forecast_sha256="f"*64,
                actual_action_key=self.action,actual_after_body=self.body)
        f=self.freeze()
        with self.assertRaises(PermissionError):
            self.freeze("second-outstanding")
        with self.assertRaises(PermissionError):
            self.audit.score(
                identity="same-later-real-step",
                preoutcome_forecast_sha256="0"*64,
                actual_action_key=self.action,actual_after_body=self.body)
        with self.assertRaises(PermissionError):
            self.audit.score(
                identity="same-later-real-step",
                preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                actual_action_key=("manger",),actual_after_body=self.body)
        with self.assertRaises(ValueError):
            self.audit.score(
                identity="same-later-real-step",
                preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                actual_action_key=self.action,
                actual_after_body=(80.,65.,float("nan"),90.,70.))
        good=self.audit.score(
            identity="same-later-real-step",
            preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
            actual_action_key=self.action,actual_after_body=self.body)
        self.assertTrue(isfinite(good["priority_mean_squared_error"]))
        with self.assertRaises(PermissionError):
            self.audit.score(identity="same-later-real-step",
                             preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                             actual_action_key=self.action,actual_after_body=self.body)

    def test_forecast_disagreement_invalidates_replay_only_negative_control(self):
        self.r.effects.observe(("boire",),(-4.,2.,11.,0.,-3.))
        with self.assertRaises(PermissionError):
            self.freeze()
        self.assertEqual(self.audit.report()["forecast_commits"],0)

    def test_unknown_censor_cannot_hide_bad_outcome_or_complete_window(self):
        f=self.freeze()
        with self.assertRaises(ValueError):
            self.audit.censor(identity="same-later-real-step",
                              preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                              reason="BETTER_IF_REPLACED")
        self.audit.censor(identity="same-later-real-step",
                          preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                          reason="ORIGINAL_OUTCOME_NOT_OBSERVABLE")
        self.assertEqual(self.audit.report()["right_censored_no_imputation"],1)

    def test_valid_readout_cannot_be_generated_after_result_is_seen(self):
        # API accepts no outcome in freeze; sequential enforcement rejects
        # any attempted retrospective second outcome or alternate action.
        f=self.freeze()
        receipt=self.audit.score(identity="same-later-real-step",
                    preoutcome_forecast_sha256=f["preoutcome_forecast_sha256"],
                    actual_action_key=self.action,actual_after_body=self.body)
        self.assertTrue(receipt["outcome_seen_only_after_forecast_commit"])
        with self.assertRaises(PermissionError):
            self.freeze()


if __name__=="__main__":
    unittest.main()
