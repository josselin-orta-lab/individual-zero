"""Frozen exposed DEV world engineering gate for privately funded risk reads."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_paid_residual_native_uncertainty_engineering as E
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.world import World


class PaidResidualNativeUncertaintyEngineeringTests(unittest.TestCase):
    def test_frozen_eight_dev_worlds_and_native_control(self):
        with patch("i3.runtime.life.run_life",
                   side_effect=AssertionError("no scientific life runner")):
            r = E.audit()
        print("I3_PAID_RESIDUAL_NATIVE_UNCERTAINTY=" +
              json.dumps(r,sort_keys=True,separators=(",",":")))
        self.assertIn(r["status"],(
            "PAID_RESIDUAL_READOUT_ENGINEERING_PASS_MOTOR_MEDIATION",
            "PAID_RESIDUAL_READOUT_ENGINEERING_PASS_NO_MOTOR_MEDIATION",
            "PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND"))
        self.assertEqual(r["early_native_cost_confounds"],sum(
            p["first_cost_confound"] is not None for p in r["pair_results"]))
        self.assertEqual(
            r["general_action_mediation_inference_admissible"],
            r["early_native_cost_confounds"] == 0)
        if r["early_native_cost_confounds"]:
            self.assertEqual(
                r["status"], "PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND")
            self.assertFalse(r["general_action_mediation_inference_admissible"])
        self.assertEqual(r["engineering_worlds"],8)
        self.assertLessEqual(r["engineering_world_steps"],96)
        self.assertEqual(len(r["pair_results"]),4)
        self.assertEqual(r["scientific_worlds"],0)
        self.assertEqual(r["scientific_lives"],0)
        self.assertEqual(r["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(r["additional_computation_is_laboratory_requested"] is False)
        self.assertFalse(r["CPU_joules_calibrated"])
        self.assertFalse(r["stage2_2_go"])
        self.assertEqual(len(r["deterministic_aggregate_sha256"]),64)
        self.assertEqual(r["first_differences"],sum(
            p["first_motor_difference"] is not None for p in r["pair_results"]))
        for p in r["pair_results"]:
            self.assertLessEqual(p["visible_steps"],12)
            self.assertLessEqual(p["discard_steps"],12)
            self.assertEqual(len(p["visible_end_body"]),5)
            self.assertEqual(len(p["discard_end_body"]),5)

    def test_genuine_paid_same_operator_read_visibility_and_discard(self):
        left=E.PaidResidualResearchMind(midpoint(),840061,mode="VISIBLE")
        right=E.PaidResidualResearchMind(midpoint(),840061,mode="PAID_DISCARD")
        for mind in (left,right):
            mind.error_history[:]=[("boire",2.),("dormir",4.),("boire",8.)]
        body=(70.,60.,60.,90.,80.)
        for mind in (left,right):
            mind._risk_budget=CognitiveBudget(body,BodyLaws())
        try:
            mean_a,u_a=left._read_plan_prediction(("boire",))
            mean_b,u_b=right._read_plan_prediction(("boire",))
        finally:
            left._risk_budget=right._risk_budget=None
        self.assertEqual(mean_a,mean_b)
        self.assertEqual(u_b,1.)
        self.assertNotEqual(u_a,u_b)
        self.assertEqual(left.risk_events[0]["computed_uncertainty"],
                         right.risk_events[0]["computed_uncertainty"])
        self.assertEqual(left.risk_events[0]["operator_visits"],3)
        self.assertEqual(right.risk_events[0]["operator_visits"],3)
        self.assertEqual(left.risk_events[0]["modeled_work"],
                         right.risk_events[0]["modeled_work"])

    def test_no_personal_action_support_preserves_original_uncertainty(self):
        m=E.PaidResidualResearchMind(midpoint(),840061,mode="VISIBLE")
        m.error_history[:]=[("dormir",4.)]
        m._risk_budget=CognitiveBudget((70.,60.,60.,90.,80.),BodyLaws())
        try:
            original=m.effects.predict(("boire",))[1]
            mean,u=m._read_plan_prediction(("boire",))
        finally:
            m._risk_budget=None
        self.assertEqual(u,original)
        self.assertEqual(m.risk_events[-1]["status"],
                         "PAID_NO_SAME_ACTION_SUPPORT")
        self.assertEqual(m.risk_events[-1]["operator_visits"],1)

    def test_low_energy_and_vigilance_deny_before_private_history_scan(self):
        for body in ((0.001,60.,60.,90.,80.),
                     (70.,60.,60.,90.,0.001)):
            m=E.PaidResidualResearchMind(midpoint(),840061,mode="VISIBLE")
            m.error_history[:]=[("boire",2.)]
            m._risk_budget=CognitiveBudget(body,BodyLaws())
            try:
                mean,u=m._read_plan_prediction(("boire",))
            finally:
                m._risk_budget=None
            self.assertEqual(m.risk_events[-1]["status"],
                             "DENIED_BEFORE_LEDGER_READ")
            self.assertEqual(m.risk_events[-1]["operator_visits"],0)
            self.assertIsNone(m.risk_events[-1]["computed_uncertainty"])
            self.assertEqual(m.risk_events[-1]["modeled_work"],
                             {"cycles":0,"simulated_steps":0,
                              "memory_items":0,"replays":0})

    def test_invalid_frozen_configuration_and_determinism(self):
        with self.assertRaises(ValueError):
            E.run_arm(E.FACTORIES[0],840062,"UNFUNDED_ORACLE")
        with self.assertRaises(ValueError):
            E.run_arm(E.FACTORIES[0],845001,"VISIBLE")
        with self.assertRaises(ValueError):
            E.PaidResidualResearchMind(midpoint(),840061,mode=None)
        a,b=E.audit(),E.audit()
        self.assertEqual(a,b)


if __name__=="__main__":
    unittest.main()
