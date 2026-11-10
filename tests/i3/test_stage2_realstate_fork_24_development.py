"""Prospectively frozen new realstate fork pilot tests; no World births."""
from copy import deepcopy
from unittest.mock import patch
import os
import unittest

from i3.lab import stage2_realstate_fork_24_development as D
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class RealStateFork24DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=D.cases()
        cls.source=D.SOURCE.source_fingerprint()

    def test_frozen_allocation_and_source_scope(self):
        p=D.plan()
        self.assertEqual(p["matched_units"],24)
        self.assertEqual(p["planned_original_lives"],48)
        self.assertEqual(p["unit_index_start"],540000)
        self.assertFalse(p["independent_iid_ecology_attested"])
        self.assertFalse(p["scientific_go"])
        self.assertFalse(p["scientific_registration"])
        self.assertEqual(len(self.rows),48)
        self.assertEqual([x["index"] for x in self.rows[::2]],
                         list(range(540000,540024)))
        self.assertEqual(len({x["world_seed"] for x in self.rows}),24)
        for i in range(24):
            a,b=self.rows[2*i:2*i+2]
            self.assertEqual((a["policy"],b["policy"]),D.POLICIES)
            for k in ("family","index","pair_id","life_seed",
                      "genome_seed","world_seed"):
                self.assertEqual(a[k],b[k])
        self.assertEqual(D.cases(),self.rows)

    def test_stale_or_modified_source_never_enters_world(self):
        runner=D._run_case(self.rows,self.source)
        for mut in ({"index":539999},{"index":540024},{"index":True},
                    {"index":510000},{"cohort":"engineering"},
                    {"cohort":"selection"},{"cohort":"reserve"},
                    {"cohort":"validation"},{"policy":"reference"},
                    {"family":"broken"},{"life_seed":-1},
                    {"genome_seed":-1},{"world_seed":-1}):
            with self.subTest(mut=mut):
                with patch.object(SPECS,"_construct_f0_spec") as constructor:
                    with self.assertRaises(PermissionError):
                        runner(dict(self.rows[0],**mut))
                    constructor.assert_not_called()

    def test_exact_admission_and_observer_only_random_content(self):
        pair=self.rows[:2]
        def fake_life(genome,spec,life_seed,horizon,*,
                      decision_policy,admission,
                      observer_realstate_content_fork,**kw):
            self.assertEqual(RA.verify(admission,spec)["cohort"],"development")
            self.assertEqual(life_seed,pair[0]["life_seed"])
            self.assertEqual(horizon,400)
            self.assertEqual(observer_realstate_content_fork,
                             decision_policy==D.POLICIES[1])
            return {"mock":True}
        with patch.object(D,"run_life",side_effect=fake_life):
            run=D._run_case(self.rows,self.source)
            self.assertTrue(run(pair[0])["mock"])
            self.assertTrue(run(pair[1])["mock"])

    def test_before_first_source_claim_blocks_world(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                D.execute("/tmp/i3-realstate-fork-never-should-create")
        with patch.dict(os.environ,{
            "GITHUB_EVENT_NAME":"pull_request","GITHUB_REF":"refs/heads/main",
            "GITHUB_RUN_ATTEMPT":"1",
            "I3_REALSTATE_FORK_CLAIM_BRANCH":D.CLAIM_BRANCH,
            "GITHUB_SHA":"a"*40},clear=True):
            with self.assertRaises(PermissionError):
                D._claim_trusted_main()

    def test_all_assigned_primary_includes_no_first_fork(self):
        original=[]
        for case in self.rows:
            random=case["policy"]==D.POLICIES[1]
            original.append({
                **case,"terminal":"censored","steps_lived":400,
                "dead_at_horizon":False,"paid_energy":3.,
                "paid_vigilance":4.,"replays_paid":20,"sleep_steps":5,
                "world_sha256":str(case["world_seed"]),
                "genome_sha256":str(case["genome_seed"]),
                "source_sha256":"source",
                "random_content_receipt":(
                    {"distinct_from_priority_subsets":1,
                     "paid_replay_opportunities":2,
                     "selected_replays_paid":20,"lived_sleep_ordinals":5}
                    if random else None),
                "realstate_fork_receipt":({
                    "status":"NO_DIFFERING_FUNDED_REPLAY_OBSERVED",
                    "prepaid_replay_opportunities_seen":0,
                    "differing_replay_opportunities_seen":0,
                    "first_fork":None} if random else None)
            })
        report=D.analyze(self.rows,original)
        self.assertEqual(report["mechanism"]["assigned_pairs"],24)
        self.assertEqual(report["mechanism"]["first_fork_absent"],24)
        self.assertEqual(report["mechanism"]["positive_learned_value_difference"],0)
        self.assertFalse(report["mechanism"]["biological_mediation_claim"])
        positive=deepcopy(original)
        positive[1]["realstate_fork_receipt"]["first_fork"]={
            "l1_value_difference_between_detached_updates":.05}
        outcome=D.analyze(self.rows,positive)
        self.assertEqual(outcome["mechanism"]["first_fork_captured"],1)
        self.assertEqual(outcome["mechanism"]["positive_learned_value_difference"],1)
        self.assertEqual(outcome["mechanism"]["primary_fraction_per_assigned_pair"],1/24)
        with self.assertRaises(ValueError):
            D.analyze(self.rows,positive[:-1])
        altered=deepcopy(original)
        altered[1]["world_sha256"]="wrong"
        with self.assertRaises(ValueError):
            D.analyze(self.rows,altered)


if __name__=="__main__":
    unittest.main()
