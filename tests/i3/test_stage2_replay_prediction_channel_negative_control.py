"""Falsify naive prediction-accuracy claims from replay-induced TD changes."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_replay_prediction_channel_negative_control as N
from i3.lab import stage2_replay_content_local as LOCAL


class ReplayPredictionChannelNegativeControlTests(unittest.TestCase):
    def test_same_personal_effect_forecast_despite_different_replay_memories(self):
        source=N.source_mind(0)
        original=deepcopy(source)
        p,pi,pc=N._replay(source,0,"priority")
        r,ri,rc=N._replay(source,0,"random_content")
        self.assertNotEqual(set(pi),set(ri))
        self.assertEqual(pc,rc)
        self.assertEqual(pc["unpaid"],(0.0,0.0))
        self.assertEqual(pc["work"][-1],LOCAL.COUNT)
        self.assertEqual(N._effect_channel(p),N._effect_channel(r))
        self.assertEqual(N._effect_channel(p),N._effect_channel(original))
        self.assertEqual(p.effects.stats,r.effects.stats)
        self.assertEqual(source.effects.stats,original.effects.stats)
        self.assertEqual(list(source.buffer),list(original.buffer))
        self.assertEqual(source.values,original.values)
        self.assertNotEqual(p.values,r.values)

    def test_finite_panel_no_world_and_future_oracle(self):
        result=N.probe()
        self.assertEqual(result["schema"],N.SCHEMA)
        self.assertEqual(result["status"],
                         "COMPLETE_SOFTWARE_NEGATIVE_CONTROL_ONLY")
        self.assertEqual(result["fixed_synthetic_units"],48)
        self.assertEqual(result["replay_count_each_detached_copy"],3)
        self.assertEqual(result["different_memory_subsets"],48)
        self.assertEqual(
            result["same_effects_model_and_action_effect_forecasts"],48)
        self.assertGreater(result["different_TD_value_vectors"],0)
        self.assertGreater(result["different_evaluated_value_predictions"],0)
        self.assertTrue(result["equal_estimated_energy_vigilance_tariff_per_arm"])
        self.assertTrue(result["projected_tariff_not_physically_debited"])
        self.assertTrue(result["no_hidden_World_or_future_actual_outcome_read"])
        self.assertTrue(result["no_World_or_life_executed"])
        self.assertEqual(result["scientific_survival_verdict"],"NOT_ISSUED")
        self.assertEqual(result["proper_future_predictive_score"],"NOT_DEFINED")
        self.assertEqual(len(result["observations"]),48)

    def test_invalid_trial_fails_before_any_world(self):
        for t in (-1,48,True):
            with self.subTest(trial=t),self.assertRaises(ValueError):
                N.source_mind(t)


if __name__=="__main__":
    unittest.main()
