"""New 48 matched full-life content experiment guards, NO actual birth in tests."""
from copy import deepcopy
from unittest.mock import patch
import os
import unittest

from i3.lab import stage2_content_48_development as CONTENT
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class Content48DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=CONTENT.cases()
        cls.source=CONTENT.SOURCE.source_fingerprint()

    def test_frozen_new_48_pair_allocation_and_scientific_scope(self):
        p=CONTENT.plan()
        self.assertEqual(p["matched_pairs"],48)
        self.assertFalse(p["scientific_registration"])
        self.assertFalse(p["entropy_independently_attested"])
        self.assertIsNone(p["biological_loss_margin"])
        self.assertFalse(p["scientific_go"])
        self.assertEqual(len(self.rows),96)
        self.assertEqual([r["index"] for r in self.rows[::2]],
                         list(range(480000,480048)))
        self.assertEqual({r["cohort"] for r in self.rows},{"development"})
        self.assertEqual(len({r["world_seed"] for r in self.rows}),48)
        self.assertEqual(CONTENT.cases(),self.rows)
        for i in range(48):
            a,b=self.rows[2*i:2*i+2]
            self.assertEqual((a["policy"],b["policy"]),CONTENT.POLICIES)
            for key in ("pair_id","index","family","world_seed",
                        "genome_seed","life_seed"):
                self.assertEqual(a[key],b[key])

    def test_mutations_rejected_before_constructing_World(self):
        run=CONTENT._run_case(self.rows,self.source)
        for change in (
            {"index":True},{"index":479999},{"index":480048},
            {"index":360000},{"index":240000},
            {"cohort":"selection"},{"cohort":"validation"},
            {"cohort":"reserve"},{"cohort":"engineering"},
            {"family":"unknown"},{"policy":"p13_replay_gate_random_equal_mean_v1"},
            {"life_seed":SAMPLE.LIFE_BASE+5},
            {"world_seed":SAMPLE.WORLD_BASE+5},
            {"genome_seed":SAMPLE.GENOME_BASE+5},
        ):
            with self.subTest(change=change):
                c=dict(self.rows[0],**change)
                with patch.object(SPECS,"_construct_f0_spec") as ctor:
                    with self.assertRaises(PermissionError):
                        run(c)
                    ctor.assert_not_called()
        with self.assertRaises(PermissionError):
            run(None)

    def test_new_ticket_exact_World_and_source(self):
        case=self.rows[1]
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_replay_content_newworld_development(
            case=case,spec=spec,transport_fingerprint=self.source)
        self.assertEqual(RA.verify(ticket,spec)["cohort"],"development")
        with self.assertRaises(PermissionError):
            GUARD.admit_replay_content_newworld_development(
                case=case,spec=spec,transport_fingerprint="f"*64)
        from dataclasses import replace
        changed=replace(spec,body=(1.,60.,60.,60.,60.))
        with self.assertRaises(PermissionError):
            GUARD.admit_replay_content_newworld_development(
                case=case,spec=changed,transport_fingerprint=self.source)

    def test_all_two_arms_bind_actual_life_without_true_World_in_tests(self):
        pair=self.rows[:2]
        seen=[]
        def fake_run(genome,spec,seed,horizon,*,decision_policy,admission,**kw):
            self.assertEqual(seed,pair[0]["life_seed"])
            self.assertEqual(horizon,400)
            self.assertEqual(kw["protocol"],CONTENT.PROTOCOL)
            self.assertEqual(RA.verify(admission,spec)["cohort"],"development")
            seen.append(decision_policy)
            return {"mock":True}
        with patch.object(CONTENT,"run_life",side_effect=fake_run):
            run=CONTENT._run_case(self.rows,self.source)
            self.assertTrue(run(pair[0])["mock"])
            self.assertTrue(run(pair[1])["mock"])
        self.assertEqual(seen,list(CONTENT.POLICIES))

    def test_one_shot_source_claim_blocks_unauthorized_life(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                CONTENT.execute("/tmp/i3-source-should-never-be-created")
        with patch.dict(os.environ,{
            "GITHUB_EVENT_NAME":"pull_request",
            "GITHUB_REF":"refs/heads/main",
            "GITHUB_RUN_ATTEMPT":"1",
            "I3_CONTENT_CLAIM_BRANCH":CONTENT.CLAIM_BRANCH,
            "GITHUB_SHA":"a"*40
        },clear=True):
            with self.assertRaises(PermissionError):
                CONTENT._claim_trusted_main()

    def test_complete_finite_analysis_and_adverse_pair(self):
        rows=[]
        for case in self.rows:
            r={**case,"terminal":"censored","steps_lived":400,
               "dead_at_horizon":False,
               "paid_energy":60.,"paid_vigilance":70.,
               "replays_paid":12,"sleep_steps":3,
               "random_content_receipt":(
                   None if case["policy"]==CONTENT.POLICIES[0] else
                   {"paid_replay_opportunities":2,
                    "selected_replays_paid":12,
                    "lived_sleep_ordinals":3,
                    "distinct_from_priority_subsets":1}),
               "world_sha256":str(case["world_seed"]),
               "genome_sha256":str(case["genome_seed"]),
               "source_sha256":"test",
            }
            rows.append(r)
        data=CONTENT.analyze(self.rows,rows)
        self.assertEqual(data["overall"]["assigned_pairs"],48)
        self.assertEqual(data["overall"]["paired_risk_difference_priority_minus_random"],0.)
        self.assertFalse(data["independent_iid_ecology_attested"])
        self.assertEqual(data["scientific_verdict"],"NOT_ISSUED")
        self.assertEqual(data["by_arm"][CONTENT.POLICIES[1]]
                         ["random_content_distinct_subsets"],48)
        with self.assertRaises(ValueError):
            CONTENT.analyze(self.rows,rows[:-1])
        switched=deepcopy(rows)
        switched[0],switched[2]=switched[2],switched[0]
        with self.assertRaises(ValueError):
            CONTENT.analyze(self.rows,switched)
        adverse=deepcopy(rows)
        adverse[0]["terminal"]="dead"
        adverse[0]["dead_at_horizon"]=True
        outcome=CONTENT.analyze(self.rows,adverse)["overall"]
        self.assertEqual(outcome["random_content_only_survives"],1)
        self.assertEqual(outcome["priority_only_survives"],0)
        self.assertEqual(outcome["paired_risk_difference_priority_minus_random"],-1/48)


if __name__=="__main__":
    unittest.main()
