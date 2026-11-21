"""Stage8-F1I strict before-exposure 16 fresh paid Minds, real native food tests."""
from __future__ import annotations

from copy import deepcopy
import inspect
import unittest

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1i_independent_lived_resources as F
from tools import stage8f1i_independent_cold_resource_audit as Cold


def reseal(obj):
    for row in obj["rows"]:
        source=row["source"]
        for step in source["source_steps"]:
            step["postaction"]["learning_receipt_sha256"]=I.h({
                k:v for k,v in step["postaction"].items()
                if k!="learning_receipt_sha256"})
            step["receipt_sha256"]=I.h({
                k:v for k,v in step.items() if k!="receipt_sha256"})
        source["source_receipt_sha256"]=I.h({
            k:v for k,v in source.items() if k!="source_receipt_sha256"})
        for arm in row["arms"].values():
            for step in arm["steps"]:
                step["postaction"]["learning_receipt_sha256"]=I.h({
                    k:v for k,v in step["postaction"].items()
                    if k!="learning_receipt_sha256"})
                step["receipt_sha256"]=I.h({
                    k:v for k,v in step.items() if k!="receipt_sha256"})
            arm["trajectory_sha256"]=I.h({
                k:v for k,v in arm.items() if k!="trajectory_sha256"})
        row["case_sha256"]=I.h({
            k:v for k,v in row.items() if k!="case_sha256"})
    obj["provenance_chain_sha256"]=I.h({
       "source_main":F.SOURCE_MAIN,"grid_commit":F.PRE_GRID_COMMIT,
       "protocol_commit":F.PRE_PROTOCOL_COMMIT,
       "case_hashes":[r["case_sha256"] for r in obj["rows"]]
    })


class F1IIndependentlyPaidMinds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=F.exact_grid()
        cls.proof=F.produce(cls.grid)
        cls.cold=Cold.audit(cls.proof,cls.grid)

    def test_sixteen_exact_preregistered_seeds_worlds_initial_bodies(self):
        self.assertEqual(len(self.proof["rows"]),16)
        self.assertEqual([x["origin"]["id"] for x in self.proof["rows"]],
                         ["R"+str(i).zfill(2) for i in range(1,17)])
        self.assertEqual(len({x["origin"]["seed"] for x in self.proof["rows"]}),16)
        self.assertEqual(self.proof["preexposure_grid_commit"],F.PRE_GRID_COMMIT)
        self.assertEqual(self.proof["preexposure_protocol_commit"],F.PRE_PROTOCOL_COMMIT)
        self.assertEqual(self.grid["terminal_tick"],30)

    def test_every_birth_is_fresh_no_artificial_personal_knowledge(self):
        hashes=set()
        for root in self.proof["rows"]:
            genesis=root["source"]["genesis"]
            self.assertEqual(genesis["mind"]["data"]["class"],"Mind")
            self.assertEqual(I.observed_stats(genesis["mind"]),{})
            private=I.private_fields(genesis["mind"])
            self.assertEqual(private["buffer"],{"__deque__":[],"maxlen":None})
            self.assertTrue(all(all(v==0. for v in row) for row in private["values"]))
            hashes.add(genesis["mind"]["sha256"])
        self.assertEqual(len(hashes),16)

    def test_true_food_effects_before_learning_never_lab_injected(self):
        for root in self.proof["rows"]:
            before=root["source"]["genesis"]["world"]
            self.assertEqual(len(before["hidden_effects"]),1)
            token,phys=before["hidden_effects"][0]
            eco=F.MATRIX[root["origin"]["ecology"]]
            self.assertEqual(token,eco[3])
            self.assertEqual(phys,[eco[4],eco[5]])
            self.assertEqual(before["water_cells"][0][2],2)
            self.assertEqual(before["food_cells"][0][2],2)

    def test_all_personal_learning_is_prepaid_per_world_step(self):
        for root in self.proof["rows"]:
            source=root["source"]
            for step in source["source_steps"]:
                self.assertEqual(step["readout_mode"],"full")
                self.assertEqual(step["native_motor"]["cognitive_accounting"]["energy"]["unpaid"],0.)
                self.assertEqual(step["native_motor"]["cognitive_accounting"]["vigilance"]["unpaid"],0.)
                post=step["postaction"]
                if post["status"]=="PAID_LEARNED":
                    self.assertIsNotNone(post["actual_paid_learning_bill"])
                    self.assertEqual(post["executed_replays"],post["prepaid_replays"])
                    self.assertEqual(post["actual_paid_learning_bill"]["energy"]["unpaid"],0.)
                    self.assertEqual(post["actual_paid_learning_bill"]["vigilance"]["unpaid"],0.)
            for arm in root["arms"].values():
                for step in arm["steps"]:
                    self.assertEqual(step["native_motor"]["cognitive_accounting"]["energy"]["unpaid"],0.)
                    self.assertEqual(step["native_motor"]["cognitive_accounting"]["vigilance"]["unpaid"],0.)
                    post=step["postaction"]
                    if post["status"]=="PAID_LEARNED":
                        self.assertIsNotNone(post["actual_paid_learning_bill"])
                        self.assertEqual(post["executed_replays"],post["prepaid_replays"])

    def test_at_fork_only_OWN_earlier_paid_means_temporarily_read(self):
        for root in self.proof["rows"]:
            if not root["source"]["source_valid_for_fork"]:
                continue
            source=root["source"]
            from_t1={
                tuple(row["key"]):row["stat"]
                for row in source["paid_t1_mean_anchor"]}
            t4={
                tuple(row["key"]):row["stat"]
                for row in source["paid_t4_full_effects"]}
            step=root["arms"]["mask_owned_prior_means"]["steps"][0]
            current=I.observed_stats(step["effective_readout_mind"]) if "effective_readout_mind" in step else I.observed_stats(step["exposed_mind_during_decision"])
            self.assertEqual(step["temporary_prior_mean_keys"],
                             [list(k) for k in sorted(set(from_t1)&set(t4),key=repr)])
            for key in t4:
                target=from_t1[key][1] if key in from_t1 else t4[key][1]
                self.assertEqual(current[key][1],target)
                self.assertEqual(current[key][0],t4[key][0])
                self.assertEqual(current[key][2],t4[key][2])
            self.assertEqual(I.observed_stats(step["after_restoration_before_motor"]),
                             I.observed_stats(step["before_mind"]))

    def test_exact_cognitive_fork_parity_is_a_gate_not_assumption(self):
        for root in self.proof["rows"]:
            if not root["source"]["source_valid_for_fork"]:
                self.assertFalse(root["origin_valid"])
                continue
            f,sham,mask=(root["arms"][m] for m in F.MODES)
            measured=all(Cold.gate_same_fork(f,root["arms"][m]) for m in F.MODES)
            self.assertIs(root["fork_work_and_bills_equal"],measured)
            self.assertIs(root["sham_whole_trajectory_equal"],Cold.sham_equal(f,sham))
            if measured and root["sham_whole_trajectory_equal"]:
                x,y=(z["steps"][0] for z in (f,mask))
                self.assertEqual(x["cognitive_work"],y["cognitive_work"])
                self.assertEqual(x["native_motor"]["cognitive_accounting"],
                                 y["native_motor"]["cognitive_accounting"])

    def test_no_mind_rewrites_after_tick5_and_irreversible_death(self):
        self.assertTrue(self.proof["all_future_reads_unmodified_after_t5"])
        self.assertTrue(self.proof["no_forced_actions"])
        self.assertEqual(self.proof["full_lives_or_run_life"],0)
        self.assertEqual(self.proof["new_scientific_cohorts"],0)
        for root in self.proof["rows"]:
            for a in root["arms"].values():
                ticks=[v["t"] for v in a["steps"]]
                self.assertEqual(ticks,list(range(5,5+len(ticks))))
                self.assertLessEqual(a["last_world"]["t"],30)
                for step in a["steps"][1:]:
                    self.assertEqual(step["readout_mode"],"full")
                    self.assertEqual(step["temporary_prior_mean_keys"],[])
        self.assertNotIn("run_life(",inspect.getsource(F.trajectory))

    def test_real_food_consumption_count_does_not_invent_meals(self):
        count=sum(int(step["action"]=="manger")
                  for root in self.proof["rows"]
                  for arm in root["arms"].values()
                  for step in arm["steps"])
        self.assertEqual(count,self.proof["actual_native_food_ingestions_all_arms"])
        self.assertEqual(count,self.cold["native_food_ingestions_verified"])

    def test_independent_engine_free_cold_auditor_reduces_every_native_tick(self):
        self.assertEqual(self.cold["native_personal_origin_step_count"],
                         self.proof["native_first_four_source_step_count"])
        self.assertEqual(self.cold["native_after_fork_steps_reduced"],
                         self.proof["native_followup_step_count"])
        self.assertEqual(self.cold["primary_verdict"],
                         self.proof["strict_preexposed_primary_verdict"])
        self.assertEqual(self.cold["no_original_F1F_F1G_F1H_verdict_rewritten"],True)

    def test_no_retrospective_survival_success_allowed(self):
        bad=deepcopy(self.proof)
        bad["strict_preexposed_primary_verdict"]="REPRODUCIBLE_LOCAL_T30_SURVIVAL_ADVANTAGE_OF_OWN_LEARNED_CONTENT"
        if bad==self.proof:
            bad["strict_preexposed_primary_verdict"]="NO_REPRODUCIBLE_SURVIVAL_ADVANTAGE_T30"
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_fake_native_food_gain_even_resigned_is_rejected(self):
        bad=deepcopy(self.proof)
        target=bad["rows"][0]["source"]["source_steps"][0]
        target["native_motor"]["body"][1]+=12.
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_fake_unpaid_native_decision_is_rejected(self):
        bad=deepcopy(self.proof)
        target=bad["rows"][0]["source"]["source_steps"][0]
        target["native_motor"]["cognitive_accounting"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_fake_postaction_cognitive_payment_is_rejected(self):
        bad=deepcopy(self.proof)
        found=False
        for root in bad["rows"]:
            for step in root["source"]["source_steps"]:
                paid=step["postaction"]["actual_paid_learning_bill"]
                if paid is not None:
                    paid["vigilance"]["paid"]=0.
                    found=True
                    break
            if found:break
        self.assertTrue(found)
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_fabricated_old_personal_effect_rejected_even_if_rehashed(self):
        bad=deepcopy(self.proof)
        for root in bad["rows"]:
            if root["source"]["source_valid_for_fork"]:
                record=root["arms"]["mask_owned_prior_means"]["steps"][0]
                exposed=record["exposed_mind_during_decision"]
                typed=dict(exposed["data"]["private"]["__dict__"])
                typed["effects"]["__dict__"][0][1]["__dict__"][0][1][0][1][1][0]+=50.
                exposed["sha256"]=I.h(exposed["data"])
                reseal(bad)
                with self.assertRaises(ValueError):
                    Cold.audit(bad,self.grid)
                break

    def test_new_world_redefinition_cannot_hide_favorable_case(self):
        bad=deepcopy(self.grid)
        bad["origins"][0]["seed"]+=100
        with self.assertRaises(ValueError):
            Cold.audit(self.proof,bad)

    def test_two_original_native_processes_are_byte_identical(self):
        duplicate=F.produce(self.grid)
        from tools import stage8f1c_paid_postaction_learning as C
        self.assertEqual(C.canonical(self.proof),C.canonical(duplicate))


if __name__=="__main__":
    unittest.main()
