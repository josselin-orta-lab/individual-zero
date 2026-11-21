"""F1D fixed original-learning-to-next-choice first-person falsifiers.

No scientific lives, forced behavior, sleep override or refitting the
historical Stage8-E2 negative verdict. Null motor effects MUST remain valid.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import inspect
import sys
import unittest

from tools import stage8f1c_paid_postaction_learning as F1C
from tools import stage8f1d_next_decision_retention as F1D
from tools import stage8f1d_independent_next_decision_audit as A
from tools import stage8f1c_independent_postaction_audit as I


def reseal(report):
    for row in report["arms"].values():
        row["receipt_sha256"] = I.h({
            k:v for k,v in row.items() if k!="receipt_sha256"})
    report["provenance_chain_sha256"]=I.h({
        "source":F1D.SOURCE_HEAD,
        "f1c_json":F1D.F1C_ORIGINAL_SHA,
        "f1c_chain":report["f1c_provenance_chain_sha256"],
        "next_receipts":[report["arms"][k]["receipt_sha256"]
                         for k in F1D.MODES]})


class Stage8F1DNextNativeChoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A fully deterministic reconstruction of F1C native source. The
        # actual CI producer separately downloads the ARCHIVED ORIGINAL.
        cls.f1c=F1C.produce()
        cls.proof=F1D.produce(cls.f1c)
        cls.sha=I.h(cls.f1c)
        cls.exact_source=(cls.sha==F1D.F1C_ORIGINAL_SHA)

    def test_source_reproduces_original_on_native_311_runner(self):
        # Canonical original F1C was produced under Python 3.11.
        if sys.version_info[:2]==(3,11):
            self.assertEqual(self.sha,F1D.F1C_ORIGINAL_SHA)

    def test_original_historical_negative_no_lives(self):
        self.assertFalse(self.proof["run_life_executed"])
        self.assertEqual(self.proof["new_native_lives"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)
        self.assertEqual(self.proof["executed_native_world_step_calls"],4)
        self.assertEqual(self.proof["frozen_stage8e2"],F1D.FROZEN_NEGATIVE)
        self.assertEqual(self.proof["historical_g2_memory_equivalence"],"NOT_DEMONSTRATED")
        self.assertNotIn("run_life(",inspect.getsource(F1D._run_second_decision))

    def test_source_reconstructed_from_original_private_memories(self):
        for mode in F1D.MODES:
            self.assertEqual(
                self.proof["arms"][mode]["before_mind"],
                self.f1c["arms"][mode]["private_persisted_postaction"])
            self.assertEqual(
                self.proof["arms"][mode]["f1c_original_receipt_sha256"],
                self.f1c["arms"][mode]["receipt_sha256"])
        self.assertEqual(
            self.proof["predecision_different_mind_fields"],
            ["buffer","effects","values"])

    def test_next_first_person_worlds_exactly_matched(self):
        rows=self.proof["arms"]
        active=rows["retain"]
        ctrl=rows["discard_after_compute"]
        self.assertEqual(active["before_world"],ctrl["before_world"])
        self.assertEqual(active["next_capture"],ctrl["next_capture"])
        self.assertEqual(active["next_capture_sha256"],
                         ctrl["next_capture_sha256"])
        self.assertEqual(active["before_world"]["t"],1)
        self.assertEqual(active["actual_native_step"]["t"],2)
        self.assertEqual(ctrl["actual_native_step"]["t"],2)
        self.assertEqual(active["before_world"]["body"],
                         self.f1c["arms"]["retain"]["body_after_paid_learning"])

    def test_lived_native_memory_reaches_both_future_decisions(self):
        ar=self.proof["arms"]
        expected={
            "retain":self.f1c["arms"]["retain"]["private_persisted_postaction"],
            "discard_after_compute":self.f1c["arms"]["discard_after_compute"]["private_persisted_postaction"],
        }
        for mode in F1D.MODES:
            self.assertEqual(ar[mode]["before_mind"],expected[mode])
            self.assertEqual(ar[mode]["next_capture"]["body"],
                             ar[mode]["before_world"]["body"])
            I.cost(ar[mode]["decision_work"])
            self.assertIn("funding",ar[mode]["decision_info"])
        self.assertNotEqual(ar["retain"]["observer_only_sleep_forecast"],
                            ar["discard_after_compute"]["observer_only_sleep_forecast"])

    def test_null_choice_is_a_legitimate_scientific_outcome(self):
        ar=self.proof["arms"]
        expected=A.classify(ar["retain"],ar["discard_after_compute"])
        self.assertEqual(self.proof["observed_motor_effect_classification"],expected)
        self.assertIn(expected, (
            "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE",
            "NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED",
            "NEXT_MOTOR_DECISION_DIFFERENCE_WITH_UNEQUAL_COGNITION"))
        self.assertEqual(self.proof["next_work_exactly_equal"],
                         ar["retain"]["decision_work"]==ar["discard_after_compute"]["decision_work"])

    def test_next_work_and_physics_are_reduced_independently(self):
        if not self.exact_source:
            # Tests under non-origin Python versions still exercise the
            # engine, but cannot claim exact historical byte equivalence.
            self.skipTest("cross-Python original byte provenance is not an inference")
        audit=A.audit(self.proof,self.f1c)
        self.assertEqual(audit["native_second_world_step_receipts_verified"],2)
        self.assertEqual(audit["origin_first_world_step_receipts_reproduced"],2)
        self.assertEqual(audit["paired_first_person_world_states"],1)
        self.assertFalse(audit["historical_G2_decision_effect_proved"])
        self.assertFalse(audit["survival_heritability_or_gamma_causality_proved"])

    def test_resigned_forged_native_second_motor_physics_rejected(self):
        bad=deepcopy(self.proof)
        a=bad["arms"]["retain"]
        a["action"]="dormir" if a["action"]!="dormir" else None
        a["param"]=None
        reseal(bad)
        if self.exact_source:
            with self.assertRaises(ValueError):
                A.audit(bad,self.f1c)

    def test_resigned_forged_native_cognitive_bill_rejected(self):
        bad=deepcopy(self.proof)
        bad["arms"]["retain"]["actual_native_step"]["cognitive_accounting"]["energy"]["paid"] = 0.
        reseal(bad)
        if self.exact_source:
            with self.assertRaises(ValueError):
                A.audit(bad,self.f1c)

    def test_resigned_modified_prior_mind_state_rejected(self):
        bad=deepcopy(self.proof)
        altered=bad["arms"]["retain"]["before_mind"]
        altered["data"]["private"]["__dict__"][0][1]="replacement-memory"
        altered["sha256"]=I.h(altered["data"])
        reseal(bad)
        if self.exact_source:
            with self.assertRaises(ValueError):
                A.audit(bad,self.f1c)

    def test_relabel_motor_verdict_from_negative_to_positive_rejected(self):
        bad=deepcopy(self.proof)
        alt="NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED"
        if self.proof["observed_motor_effect_classification"]==alt:
            alt="NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
        bad["observed_motor_effect_classification"]=alt
        reseal(bad)
        if self.exact_source:
            with self.assertRaises(ValueError):
                A.audit(bad,self.f1c)

    def test_changed_historical_anchor_cannot_be_posthoc_relabelled(self):
        bad=deepcopy(self.proof)
        bad["frozen_stage8e2"]="STAGE8E2_CAUSAL_SUCCESS"
        reseal(bad)
        if self.exact_source:
            with self.assertRaises(ValueError):
                A.audit(bad,self.f1c)

    def test_f1c_json_modified_or_reseeded_is_rejected(self):
        modified=deepcopy(self.f1c)
        modified["arms"]["retain"]["action"]="attendre"
        with self.assertRaises(ValueError):
            A.audit(self.proof,modified)

    def test_exact_two_tick_receipts_reproducible(self):
        other=F1D.produce(self.f1c)
        self.assertEqual(F1C.canonical(other),F1C.canonical(self.proof))
        self.assertEqual(other["provenance_chain_sha256"],
                         self.proof["provenance_chain_sha256"])


if __name__=="__main__":
    unittest.main()
