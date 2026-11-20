"""Falsifiers for matched Stage8-F1 native one-tick, NO native lives.

A single original Mind snapshot is forked into paid action, equal-paid discard,
and historical (unequal-budget) reference; real World.step debits are inspected.
Independent checker does not import the generator's native objects.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.mind import Mind
from i3.modules.genome import midpoint
from tools import stage8f1_matched_native_funding as A
from tools import stage8f1_independent_native_funding_audit as I


class MatchedNativeOneTickFundingEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=A.produce()
        cls.independent=I.audit(cls.native,A.digest(cls.native))

    def test_eight_frozen_exact_same_minds_and_three_native_world_steps(self):
        self.assertEqual(len(self.native["scenarios"]),8)
        self.assertEqual(self.native["synthetic_native_world_step_calls"],24)
        self.assertEqual(self.native["full_lives_generated"],0)
        self.assertEqual(self.native["new_scientific_cohorts"],0)
        self.assertEqual(self.independent["native_world_step_receipts_checked"],24)
        self.assertEqual(self.independent["pairs_checked"],8)
        self.assertEqual(self.independent["positive_micros"],5)
        self.assertEqual(self.independent["unaffordable_micros"],2)
        self.assertEqual(self.independent["fully_funded_reference_cases"],1)

    def test_real_world_cognition_is_identical_in_candidate_and_discard(self):
        for row in self.native["scenarios"]:
            with self.subTest(row=row["case"]):
                a,b=(row["runs"][k] for k in ("candidate","equal_paid_discard"))
                self.assertEqual(a["mind_predecision_sha256"],b["mind_predecision_sha256"])
                self.assertEqual(a["capture_sha256"],b["capture_sha256"])
                self.assertEqual(a["before_body"],b["before_body"])
                self.assertEqual(a["budget_work"],b["budget_work"])
                self.assertEqual(a["paid_allowance_remaining"],b["paid_allowance_remaining"])
                self.assertEqual(a["native_step_result"]["cognitive_accounting"],
                                 b["native_step_result"]["cognitive_accounting"])
                self.assertEqual(a["native_step_result"]["t"],1)
                self.assertEqual(b["native_step_result"]["t"],1)
                self.assertEqual(a["receipt_sha256"],A.digest({
                    k:v for k,v in a.items() if k!="receipt_sha256"}))

    def test_favorable_personal_sleep_only_paid_then_native_energy_restores(self):
        row=self.native["scenarios"][0]
        a,b=(row["runs"][k] for k in ("candidate","equal_paid_discard"))
        self.assertEqual(a["action"],"dormir")
        self.assertIsNone(b["action"])
        self.assertEqual(b["computed_discarded_option"],"dormir")
        self.assertAlmostEqual(a["paid_native_bills"]["energy"],.0328)
        self.assertAlmostEqual(a["paid_native_bills"]["vigilance"],.05)
        self.assertGreater(a["native_step_result"]["body"][0],
                           b["native_step_result"]["body"][0])
        self.assertEqual(row["runs"]["p13_reference"]["budget_work"],
                         {"cycles":0,"simulated_steps":0,"memory_items":0,"replays":0})

    def test_adverse_personal_sleep_is_paid_abstention_not_forced(self):
        for name in ("learned_adverse_sleep","no_learned_effect",
                     "water_visible_motor_unaffordable"):
            row=next(x for x in self.native["scenarios"] if x["case"]==name)
            a,b=(row["runs"][k] for k in ("candidate","equal_paid_discard"))
            self.assertIsNone(a["action"])
            self.assertEqual(a["funding"],"F1_PAID_VOLUNTARY_ABSTENTION")
            self.assertEqual(a["native_step_result"]["body"],
                             b["native_step_result"]["body"])

    def test_no_credit_if_even_micro_is_unaffordable(self):
        for row in self.native["scenarios"]:
            if row["branch"]!="UNFUNDED":
                continue
            for arm in ("candidate","equal_paid_discard","p13_reference"):
                r=row["runs"][arm]
                self.assertIsNone(r["action"])
                self.assertEqual(r["funding"],"NO_PROCESSING_BUDGET")
                self.assertEqual(r["paid_native_bills"],{"energy":0.,"vigilance":0.})
                self.assertEqual(r["paid_allowance_remaining"],r["before_body"])

    def test_native_physics_cannot_undo_food_death(self):
        row=next(x for x in self.native["scenarios"]
                 if x["case"]=="terminal_food_not_rescued")
        for r in row["runs"].values():
            self.assertIn("zero_food",r["native_step_result"]["dead"])
        w,_=A.make_state(A.STATES[6])
        w.step(None,None,CognitiveWork())
        with self.assertRaisesRegex(RuntimeError,"death"):
            w.step("dormir",None,CognitiveWork())

    def test_same_personal_model_is_not_just_monkeypatched_lambda(self):
        w,base=A.make_state(A.STATES[0])
        a=A.cloned_mind(A.PaidMicrodecisionMind,base)
        b=A.cloned_mind(A.PaidMicrodecisionEqualPaidDiscardMind,base)
        self.assertEqual(A.state_witness(a),A.state_witness(b))
        self.assertGreater(len(a.effects.stats),0)
        self.assertEqual(a.effects.predict(("dormir",))[0][0],3.)
        a.effects.observe(("dormir",),(-1.,-.3,-1.,0.,0.))
        self.assertNotEqual(A.digest(A.state_witness(a)),
                            A.digest(A.state_witness(b)))
        self.assertEqual(b.effects.predict(("dormir",))[0][0],3.)

    def test_independent_checker_rejects_forged_native_payment(self):
        bad=deepcopy(self.native)
        v=bad["scenarios"][0]["runs"]["equal_paid_discard"]
        v["native_step_result"]["cognitive_accounting"]["energy"]["paid"]=0.
        v["receipt_sha256"]=I.h({k:w for k,w in v.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(ValueError,"native|physical|charge|World"):
            I.audit(bad,A.digest(bad))

    def test_checker_rejects_forged_start_memory_or_perception(self):
        bad=deepcopy(self.native)
        bad["scenarios"][0]["runs"]["candidate"]["mind_predecision_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"seal|matched|original"):
            I.audit(bad,A.digest(bad))
        bad2=deepcopy(self.native)
        bad2["scenarios"][0]["synthetic_predecision_state"]["capture"]["body"][0]=.99
        with self.assertRaisesRegex(ValueError,"shared|perception|matched"):
            I.audit(bad2,A.digest(bad2))

    def test_checker_rejects_fake_free_motor_or_new_life(self):
        bad=deepcopy(self.native)
        bad["scenarios"][0]["runs"]["equal_paid_discard"]["action"]="dormir"
        with self.assertRaises(ValueError):
            I.audit(bad,A.digest(bad))
        bad2=deepcopy(self.native)
        bad2["full_lives_generated"]=1
        with self.assertRaisesRegex(ValueError,"not fixed"):
            I.audit(bad2,A.digest(bad2))

    def test_independent_checksum_does_not_trust_modified_receipts(self):
        bad=deepcopy(self.native)
        row=bad["scenarios"][0]
        row["runs"]["candidate"]["native_step_result"]["body"][0]+=1.
        with self.assertRaisesRegex(ValueError,"seal"):
            I.audit(bad,A.digest(bad))

    def test_historical_reference_not_cost_matched_in_micro_decision(self):
        for row in self.native["scenarios"]:
            if row["branch"]=="F1":
                a=row["runs"]["candidate"];p=row["runs"]["p13_reference"]
                self.assertNotEqual(a["budget_work"],p["budget_work"])
                self.assertEqual(p["funding"],"NO_PROCESSING_BUDGET")
                self.assertTrue(row["p13_is_NOT_cost_matched_to_micro_branch"])

    def test_non_native_comparator_has_no_life_admission_entrypoint(self):
        import inspect
        from i3.modules.stage8f1_paid_microdecision_mind import (
            PaidMicrodecisionMind, PaidMicrodecisionEqualPaidDiscardMind)
        self.assertNotIn("run_life",inspect.getsource(PaidMicrodecisionMind))
        self.assertNotIn("run_life",inspect.getsource(PaidMicrodecisionEqualPaidDiscardMind))
        self.assertEqual(self.native["native_life_manifest_or_evidence_chain"],
                         "NOT_CLAIMED")


if __name__=="__main__":
    unittest.main()
