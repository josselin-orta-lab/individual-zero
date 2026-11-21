"""F1G separate preregistered TD and buffer content falsifiers, no new life."""
from __future__ import annotations

from copy import deepcopy
import inspect
import sys
import unittest

from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1f_independent_ecology_audit as A
from tools import stage8f1f_ecological_mean_readout as F
from tools import stage8f1f_native_ecological_contexts as X
from tools import stage8f1g_separate_td_buffer_readouts as G


def reseal(report):
    for context in report["contexts"]:
        source=context["source"]
        source["source_proof_sha256"]=I.h({
            k:v for k,v in source.items() if k!="source_proof_sha256"})
        for row in context["arms"].values():
            for key in ("before_mind","effective_readout_mind",
                        "post_decision_exposed_mind","post_decision_restored_mind"):
                row[key]["sha256"]=I.h(row[key]["data"])
            row["receipt_sha256"]=I.h({
                k:v for k,v in row.items() if k!="receipt_sha256"})
        context["case_sha256"]=I.h({
            k:v for k,v in context.items() if k!="case_sha256"})
    report["provenance_chain_sha256"]=I.h({
        "study":G.SCHEMA,
        "source_main":G.SOURCE_MAIN,
        "implementation_base":G.IMPLEMENTATION_BASE,
        "source_f1c":G.SOURCE_F1C_SHA,
        "source_f1f":G.F1F_FIXED_ORIGINAL_SHA256,
        "original_chain":report["f1c_original_provenance_chain_sha256"],
        "eight_cases":[c["case_sha256"] for c in report["contexts"]],
    })


class Stage8F1GTDAndBufferIndependent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=C.produce()
        cls.proof=G.produce(cls.original)
        cls.source_exact=I.h(cls.original)==G.SOURCE_F1C_SHA

    def cold(self,proof=None):
        if not self.source_exact:
            self.skipTest("SHA of original source F1C only guaranteed on Python 3.11")
        return A.audit_f1g(self.proof if proof is None else proof,self.original)

    def test_source_F1C_SHA_exact_under_reference_python(self):
        if sys.version_info[:2]==(3,11):
            self.assertTrue(self.source_exact)

    def test_preexposed_ecologies_all_eight_even_F1F_negative_cases(self):
        self.assertEqual(tuple(self.proof["preregistered_eco_names"]),
                         tuple(x[0] for x in X.ECOLOGIES))
        self.assertEqual(len(self.proof["contexts"]),8)
        self.assertEqual(self.proof["f1g_preexposure_document_commit"],
                         "82d3dc015b5d89ce52b1abc632e7a6a1a52d01b7")
        self.assertEqual(self.proof["f1f_previous_observed_motor_change_count"],1)
        self.assertEqual(self.proof["arms_per_context"],list(G.MODES))

    def test_true_paid_lived_F1C_Mind_all_32_next_decisions(self):
        src=self.original["arms"]["retain"]
        for ctx in self.proof["contexts"]:
            self.assertEqual(ctx["source"]["native_first_motor"],src["native_motor_step"])
            self.assertEqual(ctx["source"]["native_postaction_paid_learning"],
                             src["paid_postaction_learning"])
            for arm in ctx["arms"].values():
                self.assertEqual(arm["before_mind"],src["private_persisted_postaction"])
                self.assertEqual(arm["before_world"],
                                 ctx["source"]["world_at_start_of_next_decision"])
                self.assertEqual(arm["native_second_step"]["t"],2)
        self.assertEqual(self.proof["native_step_calls"],40)
        self.assertFalse(self.proof["run_life_executed"])
        self.assertEqual(self.proof["native_full_lives_created"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)

    def test_TD_masks_only_original_personal_values(self):
        orig=I.private_fields(
            self.original["arms"]["retain"]["private_before_postaction_learning"])
        later=I.private_fields(
            self.original["arms"]["retain"]["private_persisted_postaction"])
        self.assertNotEqual(orig["values"],later["values"])
        for ctx in self.proof["contexts"]:
            source=I.private_fields(ctx["arms"]["full"]["before_mind"])
            effective=I.private_fields(ctx["arms"]["mask_td"]["effective_readout_mind"])
            self.assertEqual(effective["values"],orig["values"])
            self.assertEqual(source["values"],later["values"])
            self.assertEqual({k for k in source if source[k]!=effective[k]},{"values"})
            restored=I.private_fields(ctx["arms"]["mask_td"]["post_decision_restored_mind"])
            self.assertEqual(restored["values"],later["values"])

    def test_buffer_mask_one_null_not_a_fabricated_episode(self):
        reference=I.private_fields(self.original["arms"]["retain"]["private_persisted_postaction"])
        self.assertEqual(len(reference["buffer"]["__deque__"]),1)
        for ctx in self.proof["contexts"]:
            row=ctx["arms"]["mask_buffer"]
            source=I.private_fields(row["before_mind"])
            masked=I.private_fields(row["effective_readout_mind"])
            self.assertEqual({k for k in source if source[k]!=masked[k]},{"buffer"})
            self.assertEqual(masked["buffer"],{"__deque__":[None],"maxlen":None})
            self.assertEqual(row["allowed_temporary_masks"],
                             ["buffer.content.one_null"])
            self.assertEqual(I.private_fields(row["post_decision_restored_mind"])["buffer"],
                             source["buffer"])

    def test_all_four_arms_actual_cost_parity_is_not_assumed(self):
        for ctx in self.proof["contexts"]:
            eq,sham=G.gate(ctx["arms"])
            self.assertIs(ctx["same_work_and_two_currencies_across_all_four_arms"],eq)
            self.assertIs(ctx["identity_sham_neutral"],sham)
            self.assertIs(ctx["all_four_arms_matched_valid"],bool(eq and sham))
            self.assertIs(ctx["td_content_motor_changed"],
                          ((ctx["arms"]["full"]["action"],ctx["arms"]["full"]["param"])
                           !=(ctx["arms"]["mask_td"]["action"],ctx["arms"]["mask_td"]["param"]))
                          if eq and sham else None)
            self.assertIs(ctx["buffer_content_motor_changed"],
                          ((ctx["arms"]["full"]["action"],ctx["arms"]["full"]["param"])
                           !=(ctx["arms"]["mask_buffer"]["action"],ctx["arms"]["mask_buffer"]["param"]))
                          if eq and sham else None)
        self.assertIn(self.proof["primary_gate_status"],{
            "TWO_SEPARATE_TD_BUFFER_CONTENT_COST_GATES_EVALUATED",
            "INCONCLUSIVE_TD_OR_BUFFER_COST_GATE"})

    def test_sentinel_does_not_get_a_free_replay_or_postaction_learning(self):
        for ctx in self.proof["contexts"]:
            for arm in ctx["arms"].values():
                self.assertFalse(arm["new_learning_performed"])
                self.assertTrue(arm["real_personal_memory_restored"])
                self.assertEqual(arm["native_bill"]["energy"]["unpaid"],0.)
                self.assertEqual(arm["native_bill"]["vigilance"]["unpaid"],0.)
        self.assertNotIn("run_life(",inspect.getsource(G.produce))

    def test_independent_auditor_all_eight_TD_and_buffer_comparisons(self):
        report=self.cold()
        self.assertEqual(report["native_second_steps_checked"],32)
        self.assertEqual(report["preexposed_ecologies"],8)
        self.assertEqual(report["td_primary_verdict"],self.proof["td_primary_verdict"])
        self.assertEqual(report["buffer_primary_verdict"],self.proof["buffer_primary_verdict"])
        self.assertEqual(report["scientific_lives"],0)

    def test_falsify_paid_native_energy_rejected_when_resigned(self):
        bad=deepcopy(self.proof)
        bad["contexts"][0]["arms"]["mask_td"]["native_bill"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_buffer_second_synthetic_episode_rejected(self):
        bad=deepcopy(self.proof)
        snap=bad["contexts"][1]["arms"]["mask_buffer"]["effective_readout_mind"]
        pairs=dict(snap["data"]["private"]["__dict__"])
        pairs["buffer"]["__deque__"].append(None)
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_TD_from_any_invented_value_rejected(self):
        bad=deepcopy(self.proof)
        snap=bad["contexts"][2]["arms"]["mask_td"]["effective_readout_mind"]
        pairs=dict(snap["data"]["private"]["__dict__"])
        pairs["values"][0][0]+=10.
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_private_genetics_or_rng_override_rejected(self):
        bad=deepcopy(self.proof)
        snap=bad["contexts"][0]["arms"]["mask_td"]["effective_readout_mind"]
        pairs=dict(snap["data"]["private"]["__dict__"])
        pairs["w"]["__tuple__"][0]+=1.
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_unregistered_world_resource_rejected(self):
        bad=deepcopy(self.proof)
        bad["contexts"][4]["arms"]["full"]["before_world"]["water_cells"][0][2]=0
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_sham_motor_injection_rejected(self):
        bad=deepcopy(self.proof)
        bad["contexts"][0]["arms"]["sham_state"]["action"]="dormir"
        bad["contexts"][0]["arms"]["sham_state"]["param"]=None
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_retrospective_TD_positive_verdict_rejected(self):
        bad=deepcopy(self.proof)
        bad["td_content_motor_changed_ecologies"]=99
        bad["td_primary_verdict"]="TD_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_ECOLOGIES"
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_original_F1F_results_not_used_to_select_cases(self):
        bad=deepcopy(self.proof)
        bad["f1f_previous_observed_motor_change_count"]=8
        reseal(bad)
        with self.assertRaises(ValueError):
            self.cold(bad)

    def test_falsify_source_F1C_initial_paid_learning(self):
        bad=deepcopy(self.original)
        bad["arms"]["retain"]["decision_work"]["cycles"]=0
        with self.assertRaises(ValueError):
            A.audit_f1g(self.proof,bad)

    def test_two_producers_are_byte_identical_same_eight_ecologies(self):
        reproduction=G.produce(self.original)
        self.assertEqual(C.canonical(self.proof),C.canonical(reproduction))


if __name__=="__main__":
    unittest.main()
