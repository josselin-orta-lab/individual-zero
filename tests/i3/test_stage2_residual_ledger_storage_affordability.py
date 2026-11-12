"""No-World original-source modeled funding for error-ledger maintenance."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_residual_ledger_storage_affordability as E
from i3.modules.world import World


class Stage2ResidualLedgerStorageAffordabilityTests(unittest.TestCase):
    def test_original_all_assigned_320_events_and_two_mode_parity(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("new World forbidden")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("new life forbidden")):
            result = E.audit()
        receipt = {k:v for k,v in result.items() if k != "rows"}
        print("I3_STAGE2_RESIDUAL_STORAGE="+json.dumps(
            receipt, sort_keys=True, separators=(",", ":")))
        self.assertEqual(
            result["status"],"RESIDUAL_LEDGER_STORAGE_MODEL_AFFORDABILITY_PASS")
        self.assertEqual(result["events"],320)
        self.assertEqual(result["arm_attempts"],640)
        self.assertEqual(result["funded"]+result["denied"],320)
        self.assertEqual(result["computed_each_arm"],result["funded"])
        self.assertEqual(result["initial_append_each_arm"],result["funded"])
        self.assertEqual(result["four_empty_initial_ledgers"],4)
        self.assertEqual(len(result["rows"]),320)
        self.assertEqual(result["worlds_opened"],0)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertTrue(result["model_tariff_provisional"])
        self.assertFalse(result["native_World_step_executed_here"])
        self.assertFalse(result["new_actual_World_debit_executed_here"])
        self.assertTrue(result["model_storage_not_originally_paid_by_individual"])
        self.assertFalse(result["host_CPU_joules_calibrated"])
        self.assertEqual(len(result["structural_digest"]),64)
        self.assertEqual(result["retained_final"],result["funded"])
        for row in result["rows"]:
            self.assertEqual(len(row["historical_post_paid_learning_body"]),5)
            self.assertEqual(row["modelled_work"] if "modelled_work" in row
                             else row["modeled_work"],
                             {"cycles":2,"simulated_steps":0,
                              "memory_items":12,"replays":0}
                             if row["status"]=="MODEL_AUTHORIZED_RECORD"
                             else {"cycles":0,"simulated_steps":0,
                                   "memory_items":0,"replays":0})
            self.assertEqual(row["residual_computations_per_arm"],
                             row["record_append_calls_per_arm"])

    def test_admission_refuses_before_observing_prediction_or_appending(self):
        prior=[("boire",1.)]
        for body in ((0.01,60.,60.,90.,80.),
                     (70.,60.,60.,90.,0.01)):
            with self.subTest(body=body), patch.object(
                    E,"paired_score",
                    side_effect=AssertionError("unfunded prediction accessed")):
                for mode in E.MODES:
                    ledger=deepcopy(prior)
                    before=deepcopy(ledger)
                    x=E._attempt(body=body,action="boire",
                                 prediction=[1,0,0,0,0],
                                 actual=[2,0,0,0,0],
                                 mode=mode,records=ledger)
                    self.assertEqual(x["status"],
                                     "DENIED_BEFORE_RESIDUAL_READ")
                    self.assertEqual(ledger,before)
                    self.assertEqual(x["computed"],0)
                    self.assertEqual(x["appended"],0)
                    self.assertEqual(x["modeled_work"],
                                     {"cycles":0,"simulated_steps":0,
                                      "memory_items":0,"replays":0})

    def test_real_error_computation_and_append_in_both_modes(self):
        left,right=[],[]
        body=(70.,60.,60.,90.,80.)
        spy=E.paired_score
        with patch.object(E,"paired_score", wraps=spy) as scoring:
            a=E._attempt(body=body,action="boire",
                         prediction=[1,0,0,0,0],
                         actual=[2,0,0,0,0],mode="RETAIN",records=left)
            b=E._attempt(body=body,action="boire",
                         prediction=[1,0,0,0,0],
                         actual=[2,0,0,0,0],mode="PAID_DISCARD",records=right)
        self.assertEqual(scoring.call_count,2)
        self.assertEqual(a["computed_error"],.2)
        self.assertEqual(a["computed_error"],b["computed_error"])
        self.assertEqual(a["modeled_work"],b["modeled_work"])
        self.assertEqual(a["appended"],b["appended"])
        self.assertEqual(left,[("boire",.2)])
        self.assertEqual(right,[])
        self.assertEqual(a["retained"],1)
        self.assertEqual(b["retained"],0)

    def test_source_corruptions_fail_closed_without_world(self):
        source=json.loads(E.DATASET.read_text(encoding="utf-8"))
        bills=json.loads(E.DECISION_BILLS.read_text(encoding="utf-8"))
        post=json.loads(E.POST_BODY.read_text(encoding="utf-8"))
        for kind in ("source","missing","identity","seal","body","bill"):
            s,b,p=deepcopy(source),deepcopy(bills),deepcopy(post)
            if kind=="source":
                s["source_ref"]["original_aggregate_sha256"]="0"*64
            elif kind=="missing":
                p["worlds"][0]["events"].pop()
            elif kind=="identity":
                p["worlds"][0]["seed"] += 1
            elif kind=="seal":
                p["worlds"][0]["events"][0]["preoutcome_forecast_sha256"]="0"*64
            elif kind=="body":
                p["worlds"][0]["events"][0]["post_paid_learning_body"][0] += 1.
            elif kind=="bill":
                b["worlds"][0]["events"][0]["world_decision_bill"]["energy"]["paid"] = -1.
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    E.reduce_sources_with_storage(s,b,p)

    def test_bytes_remain_unchanged_and_audit_is_deterministic(self):
        paths=(E.DATASET,E.DECISION_BILLS,E.POST_BODY)
        old=[x.read_bytes() for x in paths]
        first,second=E.audit(),E.audit()
        self.assertEqual(first,second)
        self.assertEqual(old,[x.read_bytes() for x in paths])


if __name__=="__main__":
    unittest.main()
