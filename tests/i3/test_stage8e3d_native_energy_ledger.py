"""Synthetic only Stage8-E3D motor/cognition/sleep energy accounting falsifiers.

A fake aggregate never creates or simulates a native I3 life.
"""
import copy
import unittest
from unittest.mock import patch

from tools import stage8e3d_native_energy_ledger as M
from tools import stage8e3d_independent_energy_ledger as I

ACTIONS = tuple(M.ACTION_COSTS_ACTUALLY_APPLIED)
REASONS = ("FUNDED","NO_PROCESSING_BUDGET","NO_FUNDED_SCORE","NO_FUNDED_MOTOR")


def row(action="dormir", n=2880, *, gain=3.0):
    actions = {k:0 for k in ACTIONS}
    reasons = {k:0 for k in REASONS}
    actions[action] = n
    reasons["FUNDED" if action!="physical_inactivity" else "NO_PROCESSING_BUDGET"] = n
    paid = .2*n if action!="physical_inactivity" else 0.
    motor = M.ACTION_COSTS_ACTUALLY_APPLIED[action]*n
    restored = gain*n if action=="dormir" else 0.
    before=50*n
    after=before-paid-motor+restored
    return {
        "observed_steps":n,"actions":actions,"reasons":reasons,
        "decision_energy_paid":paid,"learning_energy_paid":0.,
        "predecision_energy_sum":before,"postdecision_energy_sum":after,
        "cognition_energy_paid_per_step":paid/n if n else None,
        "mean_predecision_energy":before/n if n else None,
        "mean_postdecision_energy":after/n if n else None,
        "first_failures":0,"lives_at_risk_at_start":144,
    }


def fixture():
    full = {"stage8e2_frozen_primary":M.CLOSED,
            "population_rows":[]}
    for p in range(64):
        arms={}
        for arm in M.ARMS:
            windows={w:row(n=2880) if w==M.WINDOWS[0] else row(n=0)
                     for w in M.WINDOWS}
            arms[arm]={"original_lives":144,"lived_steps":2880,
                       "first_failure_lives":0,"windows":windows}
        full["population_rows"].append({"population":p,"by_arm":arms})
    return full


class HistoricalWindowEnergyPhysics(unittest.TestCase):
    def test_native_executed_sleep_omits_nominal_quarter_energy_charge(self):
        v=M.read_window(row(n=2880))
        self.assertAlmostEqual(v["realized_sleep_energy_gain"],8640.)
        self.assertEqual(v["motor_energy_debit"],0.)
        self.assertAlmostEqual(v["sleep_energy_gain_per_sleep"],3.)

    def test_native_move_cost_and_paid_cognition_are_distinct(self):
        v=M.read_window(row(action="se_deplacer",n=2880))
        self.assertAlmostEqual(v["motor_energy_debit"],5760.)
        self.assertAlmostEqual(v["cognition_energy_paid"],576.)
        self.assertAlmostEqual(v["realized_sleep_energy_gain"],0.,places=4)
        self.assertAlmostEqual(v["net_energy_change"],-6336.,places=4)

    def test_fake_sleep_cost_breaks_physical_conservation(self):
        altered=row(n=2880,gain=3.25)
        with self.assertRaisesRegex(ValueError,"impossible physical energy"):
            M.read_window(altered)

    def test_sleep_recovery_cannot_be_invented_on_motor_step(self):
        altered=row(action="se_deplacer",n=2880)
        altered["postdecision_energy_sum"]+=2.
        with self.assertRaisesRegex(ValueError,"impossible physical energy"):
            M.read_window(altered)

    def test_lived_steps_no_action_cannot_pay_recovery(self):
        altered=row(action="physical_inactivity",n=2880)
        altered["postdecision_energy_sum"]+=1.
        with self.assertRaisesRegex(ValueError,"impossible physical energy"):
            M.read_window(altered)

    def test_zero_exposure_stays_null_not_imputed(self):
        v=M.read_window(row(n=0))
        self.assertIsNone(v["motor_debit_per_observed_step"])
        self.assertIsNone(v["sleep_energy_gain_per_sleep"])
        self.assertEqual(v["observed_steps"],0)

    def test_full_64_population_descriptive_and_independent_reducer(self):
        full=fixture()
        with patch.object(M,"read_original_reports",return_value=full):
            e3d=M.analyse("synthetic","synthetic")
        self.assertEqual(len(e3d["population_rows"]),64)
        self.assertEqual(len(e3d["descriptive_metrics"]),28)
        self.assertEqual(e3d["new_native_lives"],0)
        independent=I.check(e3d,"a"*64,full,{
            "source_exact_original_report_sha256":M.SOURCE_E3C_SHA,
            "original_stage8e2_negative_primary_unchanged":M.CLOSED})
        self.assertEqual(independent["population_arm_windows_checked"],1024)
        self.assertEqual(independent["descriptive_metric_windows_recomputed"],28)

    def test_independent_reducer_refuses_forged_sleep_motor_charge(self):
        full=fixture()
        with patch.object(M,"read_original_reports",return_value=full):
            e3d=M.analyse("synthetic","synthetic")
        e3d["population_rows"][0]["by_arm"]["S_sham"]["t001_020"]["motor_energy_debit"]=720.
        with self.assertRaisesRegex(ValueError,"energy balance"):
            I.check(e3d,"a"*64,full,{
                "source_exact_original_report_sha256":M.SOURCE_E3C_SHA,
                "original_stage8e2_negative_primary_unchanged":M.CLOSED})

    def test_old_original_sha_required_even_for_aggregate_reduction(self):
        with self.assertRaisesRegex(PermissionError,"source-exact historical"):
            M.read_original_reports("/nonexistent/E3C.json","/nonexistent/E3C_SECOND.json")


if __name__ == "__main__":
    unittest.main()
