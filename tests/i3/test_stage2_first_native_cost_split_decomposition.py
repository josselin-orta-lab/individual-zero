"""No-World native Competition expense split reconciliation (POST-HOC)."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_first_native_cost_split_decomposition as E
from i3.modules.mind import Mind
from i3.modules.world import World


class FirstNativeCostSplitTests(unittest.TestCase):
    def test_all_four_original_units_no_world_exact_body_bill(self):
        with patch.object(World,"__init__",
                          side_effect=AssertionError("no World allowed")), patch.object(
                              Mind,"decide",
                              side_effect=AssertionError("no decision replay")):
            r=E.audit()
        print("I3_FIRST_NATIVE_COST_SPLIT="+json.dumps(
            r, sort_keys=True, separators=(",",":")))
        self.assertEqual(r["status"],"FIRST_NATIVE_COST_SPLIT_ACCOUNTING_PASS")
        self.assertEqual(r["technical_paired_units"],4)
        self.assertEqual(r["first_reconciled_cost_splits"],3)
        self.assertEqual(r["no_first_split_units"],1)
        self.assertEqual(r["clean_first_motor_mediations"],0)
        self.assertEqual(r["original_engineering_world_steps_rerun"],0)
        self.assertEqual(r["new_worlds"],0)
        self.assertEqual(r["new_scientific_lives"],0)
        self.assertEqual(r["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(r["physical_CPU_joules_calibrated"])
        self.assertFalse(r["adaptive_information_value_demonstrated"])
        self.assertEqual(r["original_aggregate_sha256"],E.SOURCE_RECEIPT_SHA256)
        self.assertEqual(r["source_derivative_git_blob_sha1"],E.SOURCE_BLOB_SHA1)
        self.assertEqual(len(r["structural_sha256"]),64)
        self.assertEqual([(z["world"],z["seed"]) for z in r["rows"]],
                         list(E.GRID))
        self.assertEqual([z["first_split_step"] for z in r["rows"]],
                         [None,11,3,3])
        self.assertEqual([z["additional_competition_cycles"] for z in r["rows"]],
                         [None,1,2,2])
        # The original full-life counts may DIFFER after cost mediation,
        # even while the optional operator matched at first cost split.
        self.assertEqual(
            [tuple(z["full_life_optional_read_totals"]) for z in r["rows"]],
            list(E.ORIGINAL_FULL_LIFE_READ_TOTALS))
        self.assertEqual(r["rows"][2]["full_life_optional_read_totals"],
                         [119,115])
        for x in r["rows"]:
            if x["first_split_step"] is None:
                self.assertTrue(x["original_end_bodies_equal"])
            else:
                self.assertLessEqual(x["max_body_bill_residual"],E.TOL)
                self.assertAlmostEqual(x["extra_native_energy_bill"],
                                       .02*x["additional_competition_cycles"])
                self.assertAlmostEqual(x["extra_native_vigilance_bill"],
                                       .05*x["additional_competition_cycles"])
                self.assertEqual(len(x["actual_five_channel_body_difference"]),5)
                for c in (1,2,3):
                    self.assertAlmostEqual(
                        x["actual_five_channel_body_difference"][c],0.)

    def test_forged_original_sources_fail_closed(self):
        src=json.loads(E.SOURCE.read_text(encoding="utf-8"))
        for key in ("source","denominator","reorder","motor","operator",
                    "cycles","body","simulated","summary"):
            bad=deepcopy(src)
            conf=bad["pairs"][1]["first_cost_confound"]
            if key=="source":
                bad["source"]["source_aggregate_sha256"]="0"*64
            elif key=="denominator":
                bad["pairs"].pop()
            elif key=="reorder":
                bad["pairs"][1]["seed"]=840061
            elif key=="motor":
                conf["native_motor"]=["oracle",None]
            elif key=="operator":
                conf["read_work_matched"]=False
            elif key=="cycles":
                conf["visible_decision_work"]["cycles"]=12
            elif key=="body":
                conf["visible_after_storage_body"][0]+=1.
            elif key=="simulated":
                conf["visible_decision_work"]["simulated_steps"]+=1
            elif key=="summary":
                bad["original_summary"]["early_native_cost_confounds"]=2
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    E.reduce_source(bad)

    def test_deterministic_read_only_and_no_new_lives(self):
        raw=E.SOURCE.read_bytes()
        a=E.audit()
        b=E.audit()
        self.assertEqual(a,b)
        self.assertEqual(raw,E.SOURCE.read_bytes())


if __name__=="__main__":
    unittest.main()
