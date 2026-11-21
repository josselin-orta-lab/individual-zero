"""Stage8-F1H: falsifiable paid T12 bodily consequence of one F1F motor fork.

Preexposed before any new trajectories; 8 full/sham/mean-masked ecologies,
no imposed actions, source original F1F tick2 and future autonomously learned
and PAID outcomes. Zero survival benefit is a valid scientific result.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import sys
import unittest

from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1f_ecological_mean_readout as F
from tools import stage8f1f_independent_ecology_audit as A
from tools import stage8f1h_prospective_native_body_value as H
from tools import stage8f1h_independent_prospective_body_audit as Cold


def reseal(report):
    for ctx in report["contexts"]:
        for arm in ctx["arms"].values():
            for s in arm["steps"]:
                if s["t"]!=2:
                    for key in ("mind_before_decision","decision_mind_after_choice"):
                        item=s[key]
                        item["sha256"]=I.h(item["data"])
                    post=s["postaction"]
                    for key in ("mind_before_outcome_observation","mind_after_any_learning"):
                        item=post[key]
                        item["sha256"]=I.h(item["data"])
                    post["learning_receipt_sha256"]=I.h({
                        k:v for k,v in post.items() if k!="learning_receipt_sha256"})
                s["receipt_sha256"]=I.h({
                    k:v for k,v in s.items() if k!="receipt_sha256"})
            arm["trajectory_sha256"]=I.h({
                k:v for k,v in arm.items() if k!="trajectory_sha256"})
        ctx["case_sha256"]=I.h({
            k:v for k,v in ctx.items() if k!="case_sha256"})
    report["provenance_chain_sha256"]=I.h({
        "source_main":H.SOURCE_MAIN,"f1c":H.F1C_SHA,
        "f1f":H.F1F_SHA,"f1f_cold":H.F1F_COLD_SHA,
        "preexposure":H.PREEXPOSURE_COMMIT,
        "contexts":[x["case_sha256"] for x in report["contexts"]]
    })


class F1HProspectiveBodyValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f1c=C.produce()
        cls.f1f=F.produce(cls.f1c)
        cls.f1f_cold=A.audit_f1f(cls.f1f,cls.f1c)
        cls.proof=H.produce(cls.f1c,cls.f1f,cls.f1f_cold)
        cls.orig_exact=(
            I.h(cls.f1c)==H.F1C_SHA and
            I.h(cls.f1f)==H.F1F_SHA and
            I.h(cls.f1f_cold)==H.F1F_COLD_SHA
        )

    def cold(self,proof=None):
        if not self.orig_exact:
            self.skipTest("cold original F1C/F1F receipts require pinned Python 3.11")
        return Cold.audit(self.proof if proof is None else proof,
                          self.f1c,self.f1f,self.f1f_cold)

    def test_t12_and_all_eight_ecologies_preregistered_not_selected(self):
        self.assertEqual(H.T12,12)
        self.assertEqual(self.proof["preexposed_horizon_inclusive"],12)
        self.assertEqual(self.proof["preregistered_preexposure_commit"],H.PREEXPOSURE_COMMIT)
        self.assertEqual(self.proof["preexposed_context_ids"],[c[0] for c in A.ECOLOGIES])
        self.assertEqual(len(self.proof["contexts"]),8)
        self.assertEqual(self.proof["arms_per_context"],list(H.MODES))
        self.assertEqual(self.proof["conditional_preknown_f1f_motor_divergent_context"],H.MIXED)

    def test_original_archival_sources_have_exact_sha_under_py311(self):
        if sys.version_info[:2]==(3,11):
            self.assertTrue(self.orig_exact)
        self.assertEqual(self.proof["f1f_source_original_sha256"],H.F1F_SHA)
        self.assertEqual(self.proof["frozen_f1g_td"],
                         "NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES")
        self.assertTrue(self.proof["frozen_stage8e2"].endswith("CLOSED_NO_RETRY"))

    def test_every_second_step_copies_exact_original_F1F_native_motor_receipt(self):
        for case,orig in zip(self.proof["contexts"],self.f1f["contexts"]):
            self.assertEqual(case["source_f1f_case_sha256"],orig["case_sha256"])
            for mode in H.MODES:
                row=case["arms"][mode]["steps"][0]
                self.assertEqual(row["f1f_tick2_receipt"],orig["arms"][mode])
                self.assertEqual(row["f1f_tick2_original_receipt_sha256"],
                                 orig["arms"][mode]["receipt_sha256"])
                self.assertEqual(row["t"],2)
                self.assertEqual(row["native_motor_raw_receipt"]["t"],2)

    def test_full_vs_masked_are_unforced_same_paid_action_cost_at_fork(self):
        changed=[]
        for row in self.proof["contexts"]:
            f,mask=(row["arms"][v]["steps"][0]["f1f_tick2_receipt"]
                    for v in ("full","mask_both"))
            self.assertEqual(f["cognitive_work"],mask["cognitive_work"])
            self.assertEqual(f["native_bill"],mask["native_bill"])
            self.assertEqual(f["before_world"],mask["before_world"])
            self.assertEqual(f["before_mind"],mask["before_mind"])
            changed.append((f["action"],f["param"])!=(mask["action"],mask["param"]))
        self.assertEqual(changed,[False]*7+[True])

    def test_paid_and_no_free_postaction_replays_at_all_future_ticks(self):
        for context in self.proof["contexts"]:
            for arm in context["arms"].values():
                for step in arm["steps"]:
                    learn=step["postaction"]
                    receipt=learn["actual_paid_learning_bill"]
                    if learn["status"]=="PAID_LEARNED":
                        self.assertIsNotNone(receipt)
                        self.assertGreater(receipt["energy"]["paid"],0.0)
                        self.assertGreater(receipt["vigilance"]["paid"],0.0)
                        self.assertEqual(receipt["energy"]["unpaid"],0.0)
                        self.assertEqual(receipt["vigilance"]["unpaid"],0.0)
                        self.assertEqual(learn["executed_replays"],learn["prepaid_replays"])
                    else:
                        self.assertIsNone(receipt)
                        self.assertEqual(learn["executed_replays"],0)
                        self.assertEqual(learn["learn_work"]["cycles"],0)

    def test_once_only_mask_no_later_experimenter_choice(self):
        self.assertTrue(self.proof["no_extra_content_mask_after_t2"])
        self.assertTrue(self.proof["no_policy_or_motor_override"])
        self.assertFalse(self.proof["run_life_executed"])
        self.assertEqual(self.proof["full_lives_created"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)
        source=inspect.getsource(H._native_followup_step)
        self.assertNotIn("mask_both",source)
        self.assertNotIn("world.step(\"se_deplacer\"",source)

    def test_sham_remains_exact_as_real_memory_all_twelve_ticks(self):
        for row in self.proof["contexts"]:
            self.assertTrue(row["sham_entire_trajectory_neutral"])
            self.assertTrue(H._sham_equivalence(row["arms"]["full"],row["arms"]["sham"]))

    def test_no_hidden_resurrection_or_post_horizon_native_step(self):
        for row in self.proof["contexts"]:
            for arm in row["arms"].values():
                ticks=[v["t"] for v in arm["steps"]]
                self.assertEqual(ticks,list(range(2,2+len(ticks))))
                self.assertLessEqual(max(ticks),H.T12)
                self.assertTrue(
                    ticks[-1]==H.T12 or arm["world_at_end"]["dead"] or
                    arm["metrics"]["native_engineering_error"] is not None)

    def test_survival_verdict_not_inferred_from_motor_or_score_alone(self):
        mixed=self.proof["contexts"][-1]
        self.assertTrue(mixed["initial_f1f_motor_difference"])
        self.assertIn(self.proof["mixed_primary_survival_verdict"],{
            "INCONCLUSIVE_NATIVE_CONTINUATION",
            "NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
            "LOCAL_T12_SURVIVAL_ADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
            "LOCAL_T12_SURVIVAL_DISADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
        })
        if all(v["metrics"]["alive_at_t12"] for v in (
                mixed["arms"]["full"],mixed["arms"]["mask_both"])):
            self.assertEqual(self.proof["mixed_primary_survival_verdict"],
                             "NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12")

    def test_independent_cold_every_native_cost_and_twelve_tick_physiology(self):
        report=self.cold()
        self.assertEqual(report["ecologies_checked"],8)
        self.assertEqual(report["native_followup_steps_reevaluated"],
                         self.proof["native_followup_world_step_count"])
        self.assertEqual(report["mixed_primary_survival_verdict"],
                         self.proof["mixed_primary_survival_verdict"])
        self.assertEqual(report["full_native_lives"],0)

    def test_falsified_survival_result_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        bad["mixed_primary_survival_verdict"]="LOCAL_T12_SURVIVAL_ADVANTAGE_OF_MEMORY_READOUT_OBSERVED"
        if bad["mixed_primary_survival_verdict"]==self.proof["mixed_primary_survival_verdict"]:
            bad["mixed_primary_survival_verdict"]="NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12"
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsified_native_future_energy_bill_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        row=bad["contexts"][0]["arms"]["full"]["steps"][1]
        row["native_motor_bill"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsified_postaction_debit_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        found=False
        for context in bad["contexts"]:
            for arm in context["arms"].values():
                for step in arm["steps"]:
                    bill=step["postaction"]["actual_paid_learning_bill"]
                    if bill is not None:
                        bill["vigilance"]["paid"]=0.
                        found=True
                        break
                if found: break
            if found: break
        self.assertTrue(found)
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsified_original_F1F_decision_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        bad["contexts"][-1]["arms"]["mask_both"]["steps"][0][
            "f1f_tick2_receipt"]["param"]="S"
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_extra_free_thirteenth_tick_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        target=bad["contexts"][0]["arms"]["full"]["steps"]
        target.append(deepcopy(target[-1]))
        target[-1]["t"]=13
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_original_source_f1c_f1f_cannot_be_reclassified(self):
        bad=deepcopy(self.f1f)
        bad["eight_contexts_with_motor_change"]=8
        with self.assertRaises(ValueError):
            Cold.audit(self.proof,self.f1c,bad,self.f1f_cold)

    def test_two_full_repeated_native_productions_are_bit_identical(self):
        a=H.produce(self.f1c,self.f1f,self.f1f_cold)
        self.assertEqual(C.canonical(self.proof),C.canonical(a))


if __name__=="__main__":
    unittest.main()
