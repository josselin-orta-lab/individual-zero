"""New real-perception decision fork source and complete assigned denominator."""
from copy import deepcopy
from unittest.mock import patch
import os
import unittest

from i3.lab import stage2_next_decision_24_development as D
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.runtime import admission as RA


class NextDecision24DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=D.cases()
        cls.fingerprint=D.SOURCE.source_fingerprint()

    def test_new_source_all_24_frozen_units_not_old_worlds(self):
        plan=D.plan()
        self.assertEqual(plan["matched_units"],24)
        self.assertEqual(plan["planned_original_lives"],48)
        self.assertEqual(plan["unit_index_start"],560000)
        self.assertFalse(plan["independent_iid_ecology_attested"])
        self.assertFalse(plan["stage2_2"])
        self.assertFalse(plan["scientific_go"])
        self.assertEqual(len(self.cases),48)
        self.assertEqual([x["index"] for x in self.cases[::2]],
                         list(range(560000,560024)))
        self.assertEqual(len({x["world_seed"] for x in self.cases}),24)
        for a,b in zip(self.cases[::2],self.cases[1::2]):
            self.assertEqual((a["policy"],b["policy"]),D.POLICIES)
            for k in ("index","pair_id","family","world_seed",
                      "life_seed","genome_seed"):
                self.assertEqual(a[k],b[k])
        self.assertEqual(D.cases(),self.cases)

    def test_bad_allocation_fails_before_any_world(self):
        fn=D._run_case(self.cases,self.fingerprint)
        for changed in ({"index":559999},{"index":560024},
                        {"index":True},{"index":540000},
                        {"policy":"reference"},{"cohort":"engineering"},
                        {"cohort":"selection"},{"cohort":"validation"},
                        {"cohort":"reserve"},{"life_seed":-1},
                        {"world_seed":-1},{"family":"wrong"}):
            with self.subTest(changed=changed):
                with patch.object(SPECS,"_construct_f0_spec") as ctor:
                    with self.assertRaises(PermissionError):
                        fn(dict(self.cases[0],**changed))
                    ctor.assert_not_called()

    def test_exact_development_ticket_and_random_only_observer(self):
        originals=self.cases[:2]
        def fake_life(genome,spec,seed,horizon,*,admission,
                      decision_policy,observer_next_decision_replay,**kw):
            self.assertEqual(RA.verify(admission,spec)["cohort"],"development")
            self.assertEqual(seed,originals[0]["life_seed"])
            self.assertEqual(horizon,400)
            self.assertEqual(observer_next_decision_replay,
                             decision_policy==D.POLICIES[1])
            return {"mock":True}
        with patch.object(D,"run_life",side_effect=fake_life):
            runner=D._run_case(self.cases,self.fingerprint)
            self.assertTrue(runner(originals[0])["mock"])
            self.assertTrue(runner(originals[1])["mock"])

    def test_no_trusted_main_claim_means_no_world(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                D.execute("/tmp/i3-next-decision-should-never-create")
        with patch.dict(os.environ,{"GITHUB_EVENT_NAME":"pull_request",
                                   "GITHUB_REF":"refs/heads/main",
                                   "GITHUB_RUN_ATTEMPT":"1",
                                   "I3_NEXT_DECISION_CLAIM_BRANCH":D.CLAIM_BRANCH,
                                   "GITHUB_SHA":"a"*40},clear=True):
            with self.assertRaises(PermissionError):
                D._claim_trusted_main()

    def test_finite_24_primary_preserves_null_censored_and_adverse(self):
        rows=[]
        for case in self.cases:
            random=case["policy"]==D.POLICIES[1]
            rows.append({**case,"terminal":"censored","steps_lived":400,
                         "dead_at_horizon":False,
                         "paid_energy":9.,"paid_vigilance":10.,
                         "replays_paid":2,"sleep_steps":4,
                         "world_sha256":str(case["world_seed"]),
                         "genome_sha256":str(case["genome_seed"]),
                         "source_sha256":"source",
                         "random_content_receipt":({
                             "paid_replay_opportunities":1,
                             "selected_replays_paid":2,
                             "lived_sleep_ordinals":4,
                             "distinct_from_priority_subsets":1}
                             if random else None),
                         "next_decision_receipt":({
                             "status":"NO_DIFFERENT_FUNDED_REPLAY",
                             "funded_opportunities":0,
                             "different_opportunities":0,
                             "first_fork":None} if random else None)})
        x=D.analyze(self.cases,rows)
        self.assertEqual(x["mechanism"]["assigned_pairs"],24)
        self.assertEqual(x["mechanism"]["no_different_funded_memory_fork"],24)
        self.assertEqual(x["mechanism"]["different_next_admitted_action_or_param"],0)
        self.assertEqual(x["mechanism"]["primary_fraction_of_all_assigned"],0)
        changed=deepcopy(rows)
        changed[1]["next_decision_receipt"]["first_fork"]={
            "next_decision":{"same_admitted_action_and_param":False,
                             "same_decision_option":False},
            "shared_actual_transition_td_residual":None}
        y=D.analyze(self.cases,changed)
        self.assertEqual(y["mechanism"]["different_next_admitted_action_or_param"],1)
        self.assertEqual(y["mechanism"]["primary_fraction_of_all_assigned"],1/24)
        self.assertEqual(y["mechanism"]["no_different_funded_memory_fork"],23)
        no_next=deepcopy(rows)
        no_next[1]["next_decision_receipt"]["first_fork"]={
            "next_decision":None,"shared_actual_transition_td_residual":None}
        z=D.analyze(self.cases,no_next)
        self.assertEqual(z["mechanism"]["first_fork_without_following_real_decision"],1)
        with self.assertRaises(ValueError):
            D.analyze(self.cases,changed[:-1])
        broken=deepcopy(rows)
        broken[1]["world_sha256"]="tampered"
        with self.assertRaises(ValueError):
            D.analyze(self.cases,broken)


if __name__=="__main__":
    unittest.main()
