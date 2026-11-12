"""Frozen short DEV engineering native World-paid error history test."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_actual_paid_error_ledger_engineering as E
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.mind import Mind
from i3.modules.world import World


class ActualPaidErrorLedgerEngineeringTests(unittest.TestCase):
    def test_frozen_dev_grid_paid_native_world_and_matched_retention(self):
        decide = Mind.decide
        step = World.step
        pay = World.pay_cognition
        predict = E.Mind.__dict__  # no edits: instrument the source effects via callback below
        counters = {"decide": 0, "step": 0, "pay": 0}

        def counted_decide(m, cap, budget):
            counters["decide"] += 1
            return decide(m, cap, budget)

        def counted_step(w, action, param, work):
            counters["step"] += 1
            return step(w, action, param, work)

        def counted_pay(w, work):
            counters["pay"] += 1
            return pay(w, work)

        with patch.object(Mind, "decide", counted_decide), patch.object(
                World, "step", counted_step), patch.object(
                World, "pay_cognition", counted_pay), patch(
                    "i3.runtime.life.run_life",
                    side_effect=AssertionError("no scientific or original life runner")):
            report = E.audit()
        print("I3_REAL_PAID_ERROR_LEDGER=" + json.dumps(
            {k:v for k,v in report.items() if k!="rows"},
            sort_keys=True, separators=(",", ":")))
        self.assertIn(report["status"],
                      ("ACTUAL_PAID_LEDGER_ENGINEERING_PASS",
                       "NO_ACTUAL_STORE_OBSERVED"))
        self.assertEqual(report["engineering_worlds"], 8)
        self.assertLessEqual(report["engineering_world_steps"], 96)
        self.assertEqual(report["engineering_world_steps"], counters["step"])
        self.assertEqual(report["engineering_world_steps"], counters["decide"])
        self.assertGreaterEqual(counters["pay"],
                                2*report["funded_stores_per_arm"])
        self.assertEqual(report["new_scientific_lives"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertTrue(report["external_lab_retention_never_read_by_Mind"])
        self.assertFalse(report["individually_chosen_additional_computation"])
        self.assertFalse(report["full_host_CPU_cost_equal"])
        self.assertEqual(len(report["deterministic_aggregate_sha256"]), 64)
        self.assertEqual(len(report["rows"]), 4)
        for row in report["rows"]:
            left, right = row["retain"], row["discard"]
            self.assertEqual(left["steps_lived"], right["steps_lived"])
            self.assertEqual(left["terminal"], right["terminal"])
            self.assertEqual(left["final_body"], right["final_body"])
            self.assertEqual(right["lab_ledger_count"], 0)
            self.assertEqual(left["lab_ledger_count"], sum(
                s["storage_funded"] for s in left["steps"]))
            for a,b in zip(left["steps"],right["steps"]):
                self.assertEqual(a["native_action"], b["native_action"])
                self.assertEqual(a["native_param"], b["native_param"])
                self.assertEqual(a["post_real_storage_body"],
                                 b["post_real_storage_body"])
                self.assertEqual(a["native_decision_work"],
                                 b["native_decision_work"])
                self.assertEqual(a["storage_receipt"],b["storage_receipt"])
                self.assertEqual(a["forecast_calls"],int(a["forecast_funded"]))
                self.assertEqual(a["storage_compute_calls"],
                                 int(a["storage_funded"]))
                self.assertEqual(a["storage_initial_appends"],
                                 int(a["storage_funded"]))
                if a["terminal"]:
                    self.assertFalse(a["storage_funded"])
                for key,receipt in (
                    ("decision",a["world_decision_receipt"]),
                    ("learning",a["native_learning_receipt"]),
                    ("storage",a["storage_receipt"])):
                    for currency in ("energy","vigilance"):
                        self.assertEqual(receipt[currency]["requested"],
                                         receipt[currency]["paid"])
                        self.assertEqual(receipt[currency]["unpaid"],0)

    def test_tiny_energy_and_vigilance_refuse_before_native_predict_or_store(self):
        for body in ((0.001,50.,50.,90.,80.),
                     (70.,50.,50.,90.,0.001)):
            with self.subTest(body=body):
                b=CognitiveBudget(body,BodyLaws())
                self.assertFalse(E._can_purchase(b,E.FORECAST_WORK,"attendre"))
                self.assertEqual(b.work,CognitiveWork())
                self.assertFalse(E._can_purchase(b,E.STORE_WORK))
                self.assertEqual(b.work,CognitiveWork())

    def test_retained_and_discarded_execute_same_record_calculation(self):
        args=dict(action="boire",predicted=(1.,0.,0.,0.,0.),
                  body_before=(40.,40.,40.,40.,40.),
                  body_after=(42.,40.,40.,40.,40.))
        x,y=[],[]
        self.assertEqual(E._record_error(x,mode="RETAIN",**args),.2)
        self.assertEqual(E._record_error(y,mode="PAID_DISCARD",**args),.2)
        self.assertEqual(x,[("boire",.2)])
        self.assertEqual(y,[])
        with self.assertRaises(ValueError):
            E._record_error(x,mode="UNPAID",**args)

    def test_invalid_frozen_worlds_and_modes_refused(self):
        with self.assertRaises(ValueError):
            E.run_arm(E.FACTORIES[0],840999,"RETAIN")
        with self.assertRaises(ValueError):
            E.run_arm(E.FACTORIES[0],840061,"ORACLE")
        with self.assertRaises(ValueError):
            E.run_arm(E.FACTORIES[0],True,"RETAIN")

    def test_replay_is_deterministic_and_no_policy_source_update(self):
        first,second=E.audit(),E.audit()
        self.assertEqual(first,second)
        self.assertEqual(first["rows"][0]["retain"]["final_body"],
                         first["rows"][0]["discard"]["final_body"])


if __name__=="__main__":
    unittest.main()
