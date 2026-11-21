"""Strict F1J cost matching and independent cold body/round falsification tests.

All 16 roots and gates were preregistered before this test can execute.
The test suite NEVER imposes physical actions or retroactively relabels F1I.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import unittest

from i3.modules.body import BodyLaws,CognitiveBudget
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1j_native_equal_cost_prospective as J
from tools import stage8f1j_independent_fixed_round_cold_audit as Cold
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind


def reseal(outcome):
    for row in outcome["rows"]:
        for step in row["source"]["source_steps"]:
            step["receipt_sha256"]=I.h({
                k:v for k,v in step.items() if k!="receipt_sha256"})
        src=row["source"]
        src["source_receipt_sha256"]=I.h({
            k:v for k,v in src.items() if k!="source_receipt_sha256"})
        for arm in row["arms"].values():
            for step in arm["steps"]:
                step["receipt_sha256"]=I.h({
                    k:v for k,v in step.items() if k!="receipt_sha256"})
            arm["trajectory_sha256"]=I.h({
                k:v for k,v in arm.items() if k!="trajectory_sha256"})
        row["case_sha256"]=I.h({
            k:v for k,v in row.items() if k!="case_sha256"})
    outcome["provenance_sha256"]=I.h({
        "main":J.BASE,"grid_commit":J.GRID_PREEXPOSURE_COMMIT,
        "protocol_commit":J.PREEXPOSURE_COMMIT,
        "case_receipts":[r["case_sha256"] for r in outcome["rows"]],
    })


class F1JFixedRoundRealNativeCost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=J.exact_grid()
        cls.proof=J.produce(cls.grid)
        cls.cold=Cold.audit(cls.proof,cls.grid)

    def test_preexposure_locks_new_16_unselected_seeds_and_all_ecologies(self):
        self.assertEqual(J.GRID_PREEXPOSURE_COMMIT,
                         "8f82eea7a8b08e086010dfe497099212fb35508f")
        self.assertEqual(J.PREEXPOSURE_COMMIT,
                         "b90d6eb13459ddfda4f63c0828f4e39f135a376e")
        self.assertEqual(len(self.proof["rows"]),16)
        self.assertEqual([r["origin"]["seed"] for r in self.proof["rows"]],
                         list(range(202611219001,202611219017)))
        self.assertEqual(self.proof["preregistered_ecologies"],
                         list(Cold.ECOLOGIES))
        self.assertEqual(self.proof["frozen_prior_results"]["f1i"],
                         "INCONCLUSIVE_COST_GATE")
        self.assertEqual(self.proof["frozen_prior_results"]["f1i_unmatched_origins"],
                         ["R07","R08","R10","R11"])

    def test_all_16_personal_histories_are_fresh_and_paid_or_fail_closed(self):
        for row in self.proof["rows"]:
            origin=row["source"]
            before=Cold.private_fields(origin["genesis"]["mind"])
            self.assertEqual(Cold.observed_stats(origin["genesis"]["mind"]),{})
            self.assertEqual(before["buffer"],{"__deque__":[],"maxlen":None})
            self.assertTrue(all(all(v==0 for v in w) for w in before["values"]))
            self.assertEqual(origin["genesis"]["mind"]["data"]["class"],
                             "F1JFixedRoundMind")
            if origin["source_valid_for_fork"]:
                self.assertEqual(len(origin["source_steps"]),4)
                self.assertEqual(origin["source_steps"][0]["postaction"]["status"],
                                 "PAID_LEARNED")
                self.assertNotEqual(Cold.observed_stats(origin["source_tick4_mind"]),{})

    def test_only_substantive_rounds_authorized_before_calculation(self):
        base=Mind(midpoint(),20261121)
        candidate=F1JFixedRoundMind(midpoint(),20261121)
        # Unit-only synthetic scored alternatives, no motor or World.step.
        base.acc={"a":3.,"b":0.}
        candidate.acc={"a":3.,"b":0.}
        scored=[("a",2.),("b",1.)]
        body=(100.,80.,80.,90.,100.)
        old=CognitiveBudget(body,BodyLaws())
        new=CognitiveBudget(body,BodyLaws())
        o,old_used=base._compete(scored,2,old)
        n,new_used=candidate._compete(scored,2,new)
        self.assertEqual(old_used,1)
        self.assertEqual(new_used,2)
        self.assertEqual(new.work.cycles,2)
        self.assertEqual(len(candidate._observer_competition[
            "actual_substantive_round_snapshots"]),2)
        self.assertEqual(candidate._observer_competition[
            "paid_competition_cycles"],2)
        self.assertEqual(candidate._observer_competition[
            "winner_before_control"],n)
        self.assertIn(o,("a","b"))
        self.assertIn(n,("a","b"))

    def test_cost_gate_checks_all_four_real_work_fields_and_both_coins(self):
        for row in self.proof["rows"]:
            if not row["source"]["source_valid_for_fork"]:
                self.assertFalse(row["origin_valid"])
                continue
            full,sham,mask=(row["arms"][m] for m in J.ARMS)
            equal=all(Cold.gate_same_fork(full,row["arms"][m]) for m in J.ARMS)
            self.assertIs(row["equal_full_native_work_and_paid_both_coins"],equal)
            self.assertIs(row["whole_trajectory_sham_neutral"],
                          Cold.sham_equal(full,sham))
            if equal:
                f=full["steps"][0]
                m=mask["steps"][0]
                self.assertEqual(f["cognitive_work"],m["cognitive_work"])
                self.assertEqual(f["requested_native_cost"],m["requested_native_cost"])
                self.assertEqual(f["native_motor"]["cognitive_accounting"],
                                 m["native_motor"]["cognitive_accounting"])

    def test_full_sham_complete_trajectory_neutral_if_eligible(self):
        for row in self.proof["rows"]:
            if not row["source"]["source_valid_for_fork"]:
                continue
            self.assertTrue(row["whole_trajectory_sham_neutral"])
            self.assertTrue(Cold.sham_equal(row["arms"]["full"],row["arms"]["sham"]))

    def test_every_paid_competition_round_reduced_from_actual_options_and_scores(self):
        self.assertEqual(self.cold["all_original_personal_sources"],
                         self.proof["source_valid_roots"])
        self.assertGreater(self.cold["actual_substantive_competition_rounds_reduced"],0)
        self.assertEqual(self.cold["strict_t5_full_work_and_two_coins_matched"],
                         self.proof["matched_all_native_work_four_fields_and_paid_energy_vigilance_roots"])
        self.assertEqual(self.cold["strict_primary_parity_verdict"],
                         self.proof["strict_preexposed_primary_verdict"])

    def test_world_food_water_and_death_audited_without_action_override(self):
        self.assertEqual(self.cold["native_personal_source_steps"],
                         self.proof["real_source_native_steps"])
        self.assertEqual(self.cold["native_prospective_followup_steps"],
                         self.proof["real_followup_native_steps"])
        self.assertEqual(self.cold["native_food_ingestions_verified"],
                         self.proof["real_meals_per_all_branches"])
        self.assertEqual(self.cold["native_water_drinks_verified"],
                         self.proof["real_drinks_per_all_branches"])
        self.assertTrue(self.proof["self_chosen_native_actions_no_motor_override"])
        self.assertFalse("run_life(" in inspect.getsource(J.produce))
        self.assertEqual(self.proof["full_native_lives_run_life"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)

    def test_no_postfork_masks_except_one_registered_readout_t5(self):
        for row in self.proof["rows"]:
            for arm in row["arms"].values():
                for step in arm["steps"][1:]:
                    self.assertEqual(step["temporary_prior_mean_keys"],[])
                    self.assertEqual(step["readout_mode"],"full")
        self.assertTrue(self.proof["no_postfork_memory_interventions"])

    def test_expected_negative_or_positive_outcome_depends_on_all_16_not_selection(self):
        actual=self.proof["strict_preexposed_primary_verdict"]
        self.assertIn(actual,(
           "FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL",
           "NO_FIXED_ROUND_COST_PARITY_DEMONSTRATED",
           "INCONCLUSIVE_UNFUNDED_OR_SOURCE_GATE",
           "INVALID_SHAM","INVALID_NATIVE_AUDIT"))
        if actual=="FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL":
            self.assertEqual(self.proof[
                "matched_all_native_work_four_fields_and_paid_energy_vigilance_roots"],16)
            self.assertEqual(self.proof["source_valid_roots"],16)
            self.assertEqual(self.proof["sham_neutral_roots"],16)

    def test_fake_competition_round_resigned_must_fail_engine_free(self):
        bad=deepcopy(self.proof)
        found=False
        for row in bad["rows"]:
            for step in row["source"]["source_steps"]:
                w=step["decision_info"].get("observer",{}).get("competition_witness")
                if w and w["actual_substantive_round_snapshots"]:
                    first=w["actual_substantive_round_snapshots"][0]
                    key=next(iter(first))
                    first[key]+=0.17
                    found=True
                    break
            if found:
                break
        self.assertTrue(found)
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_fake_cognitive_bill_resigned_must_fail_cold_audit(self):
        bad=deepcopy(self.proof)
        step=bad["rows"][0]["source"]["source_steps"][0]
        step["native_motor"]["cognitive_accounting"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_retrospective_reclassification_of_f1i_invalidates_original(self):
        bad=deepcopy(self.proof)
        bad["frozen_prior_results"]["f1i"]="FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL"
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_two_new_native_generations_are_byte_identical(self):
        second=J.produce(self.grid)
        self.assertEqual(C.canonical(self.proof),C.canonical(second))


if __name__=="__main__":
    unittest.main()
