"""Stage8-F1E equal-cost authentic paid memory CONTENT readout falsifiers.

All original F1C history is retained; ONLY temporary numerical readout can
differ. A null motor effect is the valid and expected-to-be-reportable result.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import sys
import unittest

from tools import stage8f1c_paid_postaction_learning as F1C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1e_equal_cost_content_readout as E
from tools import stage8f1e_independent_equal_cost_content_audit as A


def resign(report):
    for row in report["arms"].values():
        for field in ("before_mind","effective_readout_mind",
                      "post_decision_before_restore","post_decision_restored_mind"):
            row[field]["sha256"]=I.h(row[field]["data"])
        row["receipt_sha256"]=I.h({
            k:v for k,v in row.items() if k!="receipt_sha256"})
    report["provenance_chain_sha256"]=I.h({
        "source":E.SOURCE,
        "f1c_source":E.F1C_ORIGINAL_SHA256,
        "f1c_proof_chain":report["f1c_original_provenance_chain_sha256"],
        "receipts":[report["arms"][m]["receipt_sha256"] for m in E.MODES]})


def forged_stat(snapshot,key,channel=0,bump=1):
    fields=dict(snapshot["data"]["private"]["__dict__"])
    raw=dict(fields["effects"]["__effects_model__"]["__dict__"])
    for actual,stat in raw["stats"]["__dict__"]:
        if actual=={"__tuple__":list(key)}:
            stat[1][channel]+=bump
            return
    raise AssertionError("unknown already-trained F1C key in test fixture")


class PaidContentNextChoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f1c=F1C.produce()
        cls.proof=E.produce(cls.f1c)
        cls.orig_exact=I.h(cls.f1c)==E.F1C_ORIGINAL_SHA256

    def cold(self,proof=None):
        if not self.orig_exact:
            self.skipTest("source original canonical bytes require original Python 3.11")
        return A.audit(self.proof if proof is None else proof,self.f1c)

    def test_predeclared_modes_only_no_world_search(self):
        self.assertEqual(tuple(self.proof["preexposed_conditions"]),E.MODES)
        self.assertEqual(self.proof["source_case"],"learned_beneficial_sleep")
        self.assertEqual(len(self.proof["arms"]),5)
        self.assertEqual(self.proof["new_native_world_step_calls"],5)
        self.assertEqual(self.proof["original_f1c_native_world_step_reconstructions"],1)
        self.assertEqual(self.proof["new_native_full_lives"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)
        self.assertFalse(self.proof["run_life_executed"])
        self.assertNotIn("run_life(",inspect.getsource(E.produce))
        self.assertNotIn("world.step(\"dormir\"",inspect.getsource(E._readout))

    def test_original_F1C_earned_memory_identical_across_all_conditions(self):
        src=self.f1c["arms"]["retain"]["private_persisted_postaction"]
        for mode,row in self.proof["arms"].items():
            self.assertEqual(src,row["before_mind"],mode)
            self.assertEqual(row["before_world"]["t"],1)
            self.assertEqual(row["native_second_step"]["t"],2)
            self.assertEqual(row["before_world"]["body"],
                             self.f1c["arms"]["retain"]["body_after_paid_learning"])
            self.assertEqual(row["next_capture"]["body"],row["before_world"]["body"])

    def test_only_personal_mean_readout_changes_not_learnt_counts(self):
        old,now=E.old_and_new(self.f1c)
        main=self.proof["arms"]["full"]["before_mind"]
        for mode,row in self.proof["arms"].items():
            source=I.private_fields(main)
            exposed=I.private_fields(row["effective_readout_mind"])
            self.assertEqual(set(source),set(exposed))
            for name in source:
                if name!="effects":
                    self.assertEqual(source[name],exposed[name],(mode,name))
            stats=I.observed_stats(row["effective_readout_mind"])
            self.assertEqual(set(stats),set(old))
            for key in E.TARGET_KEYS:
                self.assertEqual(stats[key][0],now[key][0])
                self.assertEqual(stats[key][2],now[key][2])
                self.assertEqual(stats[key][1],
                    old[key][1] if key in E.KEYS_BY_MODE[mode] else now[key][1],
                    (mode,key))
            self.assertEqual(I.observed_stats(row["post_decision_restored_mind"]),now)

    def test_control_has_genuinely_equal_work_and_two_native_currencies(self):
        full=self.proof["arms"]["full"]
        for mode,row in self.proof["arms"].items():
            for field in ("before_world","next_capture","actual_decision_work",
                          "actual_native_bill","expected_cost",
                          "remaining_after_paid_budget"):
                self.assertEqual(row[field],full[field],(mode,field))
            self.assertGreater(row["actual_native_bill"]["energy"]["paid"],0.)
            self.assertGreater(row["actual_native_bill"]["vigilance"]["paid"],0.)
            self.assertEqual(row["actual_native_bill"]["energy"]["unpaid"],0.)
            self.assertEqual(row["actual_native_bill"]["vigilance"]["unpaid"],0.)

    def test_sham_intervention_is_truly_behaviorally_neutral(self):
        a,b=self.proof["arms"]["full"],self.proof["arms"]["sham"]
        for field in ("effective_readout_mind","actual_action","actual_param",
                      "actual_decision_work","actual_native_bill",
                      "native_second_step","post_decision_restored_mind"):
            self.assertEqual(a[field],b[field],field)

    def test_only_the_readout_is_mutated_not_the_real_F1C_memory(self):
        source=I.observed_stats(self.f1c["arms"]["retain"]["private_persisted_postaction"])
        for r in self.proof["arms"].values():
            self.assertEqual(I.observed_stats(r["post_decision_restored_mind"]),source)
            self.assertTrue(r["original_trained_effect_model_restored"])
            self.assertFalse(r["second_learning_executed"])

    def test_predeclared_primary_may_be_negative(self):
        a,b=(self.proof["arms"][m] for m in ("full","mask_both"))
        self.assertEqual(self.proof["native_motor_effect_primary"],A.classification(a,b))
        self.assertIn(self.proof["native_motor_effect_primary"],{
            "NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE",
            "EQUAL_COST_CONTENT_CAUSES_DIFFERENT_NEXT_MOTOR_COMMAND_IN_THIS_CASE"})

    def test_repeat_two_native_processes_bit_identical(self):
        second=E.produce(self.f1c)
        self.assertEqual(F1C.canonical(self.proof),F1C.canonical(second))
        self.assertEqual(self.proof["provenance_chain_sha256"],
                         second["provenance_chain_sha256"])

    def test_cold_independent_receipts_five_steps(self):
        result=self.cold()
        self.assertEqual(result["native_second_step_receipts_verified"],5)
        self.assertTrue(result["next_work_all_exactly_equal"])
        self.assertEqual(result["primary_verdict"],self.proof["native_motor_effect_primary"])
        self.assertEqual(result["scientific_lives"],0)

    def test_forged_new_effect_mean_rejected_even_when_resigned(self):
        bad=deepcopy(self.proof)
        forged_stat(bad["arms"]["mask_both"]["effective_readout_mind"],("dormir",))
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_forged_memory_count_rejected_even_when_resigned(self):
        bad=deepcopy(self.proof)
        stats=I.private_fields(bad["arms"]["mask_global_only"]["effective_readout_mind"])
        raw=dict(stats["effects"]["__effects_model__"]["__dict__"])["stats"]["__dict__"]
        raw[0][1][0]+=1
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_forged_equality_of_physically_unpaid_bill_rejected(self):
        bad=deepcopy(self.proof)
        for row in bad["arms"].values():
            row["actual_native_bill"]["energy"]["paid"]=0.
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_forged_external_genome_or_rng_rejected(self):
        bad=deepcopy(self.proof)
        snapshot=bad["arms"]["mask_sleep_only"]["effective_readout_mind"]
        for pair in snapshot["data"]["private"]["__dict__"]:
            if pair[0]=="intention":
                pair[1]="MOTOR_FORCED_BY_LAB"
                break
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_forged_sham_or_free_readout_rejected(self):
        bad=deepcopy(self.proof)
        bad["arms"]["sham"]["actual_param"]="S"
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_primary_negative_cannot_be_rewritten_positive(self):
        bad=deepcopy(self.proof)
        value="EQUAL_COST_CONTENT_CAUSES_DIFFERENT_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
        if bad["native_motor_effect_primary"]==value:
            value="NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
        bad["native_motor_effect_primary"]=value
        resign(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_original_F1C_and_stage8e2_custody_not_rewritten(self):
        bad=deepcopy(self.f1c)
        bad["arms"]["retain"]["action"]="attendre"
        with self.assertRaises(ValueError):
            A.audit(self.proof,bad)
        wrong=deepcopy(self.proof)
        wrong["stage8e2_frozen_causal_status"]="STAGE8E2_CAUSAL_BLOCK_DEMONSTRATED"
        resign(wrong)
        with self.assertRaises(ValueError):
            self.cold(wrong)


if __name__=="__main__":
    unittest.main()
