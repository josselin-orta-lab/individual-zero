"""F1F original-F1C anchored eight-native-WorldSpec masked-content falsifiers."""
from __future__ import annotations

from copy import deepcopy
import inspect
import sys
import unittest

from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1f_ecological_mean_readout as F
from tools import stage8f1f_native_ecological_contexts as X
from tools import stage8f1f_independent_ecology_audit as A


def reseal(report):
    for row in report["contexts"]:
        src=row["source"]
        src["source_proof_sha256"]=I.h({
            k:v for k,v in src.items() if k!="source_proof_sha256"})
        for receipt in row["arms"].values():
            for k in ("before_mind","effective_readout_mind",
                      "post_decision_exposed_mind","post_decision_restored_mind"):
                receipt[k]["sha256"]=I.h(receipt[k]["data"])
            receipt["receipt_sha256"]=I.h({
                k:v for k,v in receipt.items() if k!="receipt_sha256"})
        row["case_sha256"]=I.h({
            k:v for k,v in row.items() if k!="case_sha256"})
    report["provenance_chain_sha256"]=I.h({
        "source_main":F.SOURCE_MAIN,
        "source_f1c":F.SOURCE_F1C_SHA,
        "original_chain":report["f1c_original_provenance_chain_sha256"],
        "eight_cases":[x["case_sha256"] for x in report["contexts"]]})


class F1FEightNativeEcologies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=C.produce()
        cls.report=F.produce(cls.original)
        cls.original_exact=I.h(cls.original)==F.SOURCE_F1C_SHA

    def cold(self,proof=None):
        if not self.original_exact:
            self.skipTest("cold original SHA exact only on Python 3.11 native producer")
        return A.audit_f1f(self.report if proof is None else proof,self.original)

    def test_all_ecologies_names_and_geometry_were_preexposed(self):
        self.assertEqual([x[0] for x in X.ECOLOGIES],[
            "bare","water_here","water_north","water_east","water_west",
            "food_here","food_east","mixed_here_water_east_food"])
        self.assertEqual(self.report["preregistered_eco_names"],
                         [x[0] for x in X.ECOLOGIES])
        self.assertEqual(len(self.report["contexts"]),8)
        self.assertEqual(self.report["arms_per_context"],list(F.MODES_F1F))

    def test_native_F1C_paid_same_original_learning_every_ecology(self):
        first=self.original["arms"]["retain"]
        for row in self.report["contexts"]:
            src=row["source"]
            self.assertEqual(src["native_first_motor"],first["native_motor_step"])
            self.assertEqual(src["native_postaction_paid_learning"],
                             first["paid_postaction_learning"])
            self.assertEqual(src["full_retained_mind_source_sha256"],
                             first["private_persisted_postaction"]["sha256"])
            for actual in row["arms"].values():
                self.assertEqual(actual["before_mind"],
                                 first["private_persisted_postaction"])
                self.assertEqual(actual["before_world"],
                                 src["world_at_start_of_next_decision"])

    def test_world_resources_are_native_tick1_only_and_never_from_model(self):
        for case,row in zip(X.ECOLOGIES,self.report["contexts"]):
            spec=row["context"]
            self.assertEqual(spec,X.describe(case))
            self.assertEqual(row["source"]["context"],spec)
            self.assertEqual(row["source"]["first_tick_world_steps"],1)
            self.assertTrue(all(k[0]==1 for k in spec["scheduled_native_changes"]))
            self.assertEqual(row["source"]["pre_exposure_perception_sha256"],
                             self.original["arms"]["retain"]["capture_sha256"])
            self.assertEqual(row["source"]["world_at_start_of_next_decision"]["t"],1)

    def test_every_second_step_truly_chosen_and_funded(self):
        self.assertEqual(self.report["native_step_calls"],32)
        self.assertEqual(self.report["native_full_lives_created"],0)
        self.assertEqual(self.report["new_scientific_cohorts"],0)
        self.assertFalse(self.report["run_life_executed"])
        self.assertNotIn("run_life(",inspect.getsource(F.produce))
        for row in self.report["contexts"]:
            for name,arm in row["arms"].items():
                self.assertEqual(arm["native_second_step"]["t"],2)
                self.assertEqual(arm["post_decision_restored_mind"]["data"]["class"],
                                 "PaidMicrodecisionMind")
                self.assertEqual(arm["actual_param"] if "actual_param" in arm else arm["param"],
                                 arm["param"])
                self.assertEqual(arm["native_bill"]["energy"]["unpaid"],0.0)
                self.assertEqual(arm["native_bill"]["vigilance"]["unpaid"],0.0)

    def test_exact_readout_mean_shape_only(self):
        old,learned,_,_=F.authentic_reference(self.original)
        for row in self.report["contexts"]:
            a,b,c=(row["arms"][m] for m in F.MODES_F1F)
            self.assertEqual(a["effective_readout_mind"],b["effective_readout_mind"])
            self.assertNotEqual(a["effective_readout_mind"],c["effective_readout_mind"])
            active=I.observed_stats(c["effective_readout_mind"])
            for key in F.TARGET_KEYS:
                self.assertEqual(active[key][1],old[key][1])
                self.assertEqual(active[key][0],learned[key][0])
                self.assertEqual(active[key][2],learned[key][2])
                self.assertEqual(I.observed_stats(
                    c["post_decision_restored_mind"])[key],learned[key])

    def test_no_fake_cost_parity_and_negative_results_remain_valid(self):
        for row in self.report["contexts"]:
            x,y=F.case_gate(row["arms"])
            self.assertEqual(row["native_work_and_bills_exact_equal"],x)
            self.assertEqual(row["sham_neutral"],y)
            self.assertIs(row["valid_equal_cost_pair"],bool(x and y))
            if x and y:
                full,masked=row["arms"]["full"],row["arms"]["mask_both"]
                observed=(full["action"],full["param"])!=(masked["action"],masked["param"])
                self.assertIs(row["mean_content_motor_difference"],observed)
        self.assertIn(self.report["primary_verdict"],{
            "INCONCLUSIVE_ECOLOGY_COST_GATE",
            "NO_MEAN_CONTENT_MOTOR_EFFECT_IN_EIGHT_PREREGISTERED_ECOLOGIES",
            "MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"})

    def test_exact_source_json_on_311(self):
        if sys.version_info[:2]==(3,11):
            self.assertTrue(self.original_exact)

    def test_independent_cold_auditor_rechecks_all_24_native_second_steps(self):
        r=self.cold()
        self.assertEqual(r["actual_native_second_steps_checked"],24)
        self.assertEqual(r["preexposed_ecologies"],8)
        self.assertEqual(r["primary_verdict"],self.report["primary_verdict"])
        self.assertEqual(r["scientific_lives"],0)

    def test_falsify_ecological_world_resource_and_reseal(self):
        bad=deepcopy(self.report)
        bad["contexts"][1]["arms"]["full"]["before_world"]["water_cells"][0][2]=0
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_native_paid_bill_and_reseal(self):
        bad=deepcopy(self.report)
        bad["contexts"][0]["arms"]["full"]["native_bill"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_private_learned_value_and_reseal(self):
        bad=deepcopy(self.report)
        private=bad["contexts"][0]["arms"]["mask_both"]["effective_readout_mind"]
        for pair in private["data"]["private"]["__dict__"]:
            if pair[0]=="values":
                pair[1][0][0]+=10.0
                break
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_sham_neutrality_and_reseal(self):
        bad=deepcopy(self.report)
        bad["contexts"][4]["arms"]["sham"]["action"]="dormir"
        bad["contexts"][4]["arms"]["sham"]["param"]=None
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_positive_claim_without_changed_motor(self):
        bad=deepcopy(self.report)
        bad["eight_contexts_with_motor_change"]=999
        bad["primary_verdict"]="MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_original_first_native_step(self):
        bad=deepcopy(self.report)
        bad["contexts"][3]["source"]["native_first_motor"]["t"]=9
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_invented_original_F1C(self):
        bad=deepcopy(self.original)
        bad["arms"]["retain"]["decision_funding"]="FREE_SLEEP"
        with self.assertRaises(ValueError):
            A.audit_f1f(self.report,bad)

    def test_all_eight_worlds_are_byte_reproducible(self):
        duplicate=F.produce(self.original)
        self.assertEqual(C.canonical(self.report),C.canonical(duplicate))


if __name__=="__main__":
    unittest.main()
