"""Prospective 24-unit replay/water full-life allocation and temporal reducer.

No new scientific World may be instantiated in these PR software tests.
"""
from copy import deepcopy
from unittest.mock import patch
import os
import unittest

from i3.lab import stage2_water_divergence_24_development as D
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class WaterDivergence24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=D.cases()
        cls.source=D.SOURCE.source_fingerprint()

    def test_pre_birth_frozen_source_48_lives(self):
        p=D.plan()
        self.assertEqual(p["matched_units"],24)
        self.assertEqual(p["life_horizon"],400)
        self.assertFalse(p["scientific_go"])
        self.assertFalse(p["independent_iid_ecology_attested"])
        self.assertFalse(p["selection_validation_reserve"])
        self.assertEqual(len(self.rows),48)
        self.assertEqual([r["index"] for r in self.rows[::2]],
                         list(range(510000,510024)))
        self.assertEqual(len({r["world_seed"] for r in self.rows}),24)
        self.assertEqual(len({r["life_seed"] for r in self.rows}),24)
        self.assertEqual(len({r["genome_seed"] for r in self.rows}),24)
        for i in range(24):
            a,b=self.rows[2*i:2*i+2]
            self.assertEqual((a["policy"],b["policy"]),D.POLICIES)
            self.assertEqual(a["cohort"],"development")
            for key in ("pair_id","family","world_seed","genome_seed",
                        "life_seed","index"):
                self.assertEqual(a[key],b[key])

    def test_unsupported_cohorts_and_seed_mutations_rejected_before_world(self):
        runner=D._run_case(self.rows,self.source)
        original=self.rows[0]
        for change in ({"index":True},{"index":509999},{"index":510024},
                       {"index":480000},{"index":360000},
                       {"cohort":"selection"},{"cohort":"validation"},
                       {"cohort":"reserve"},{"cohort":"engineering"},
                       {"life_seed":0},{"genome_seed":0},{"world_seed":0},
                       {"family":"invalid"},{"policy":"reference"}):
            with self.subTest(change=change):
                invalid=dict(original,**change)
                with patch.object(SPECS,"_construct_f0_spec") as ctor:
                    with self.assertRaises(PermissionError):
                        runner(invalid)
                    ctor.assert_not_called()
        with self.assertRaises(PermissionError):
            runner(None)

    def test_central_guard_and_true_passive_observer_argument(self):
        case=self.rows[1]
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_water_divergence_newworld_development(
            case=case,spec=spec,transport_fingerprint=self.source)
        self.assertEqual(RA.verify(ticket,spec)["cohort"],"development")
        with self.assertRaises(PermissionError):
            GUARD.admit_water_divergence_newworld_development(
                case=case,spec=spec,transport_fingerprint="wrong")
        called=[]
        def mocked_life(genome,world,seed,horizon,*,admission,
                        decision_policy,observer_replay_water,**kw):
            self.assertTrue(observer_replay_water)
            self.assertEqual(horizon,400)
            self.assertEqual(seed,case["life_seed"])
            self.assertEqual(RA.verify(admission,world)["cohort"],"development")
            called.append(decision_policy)
            return {"simulated":False}
        with patch.object(D,"run_life",side_effect=mocked_life):
            result=D._run_case(self.rows,self.source)(case)
        self.assertEqual(called,[D.POLICIES[1]])
        self.assertFalse(result["simulated"])

    def test_no_source_claim_blocks_all_births(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                D.execute("/tmp/i3-water-24-no-birth-permitted")
        with patch.dict(os.environ,{"GITHUB_EVENT_NAME":"pull_request",
                                    "GITHUB_REF":"refs/heads/main",
                                    "GITHUB_RUN_ATTEMPT":"1",
                                    "GITHUB_SHA":"a"*40,
                                    "I3_WATER_DIVERGENCE_CLAIM_BRANCH":D.CLAIM_BRANCH},
                        clear=True):
            with self.assertRaises(PermissionError):
                D._claim_trusted_main()

    @staticmethod
    def step(step=1, chosen=(0,1), pre="state", belief="belief", action="dormir"):
        return {
            "step":step,"action":action,"param":None,
            "decision_option":action,
            "pre_replay_state_sha256":pre,
            "replay_count_prepaid":len(chosen),
            "replay_memory_indices":list(chosen),
            "replay_priority_indices":[0,1],
            "personal_water_belief_sha256":belief,
            "personally_learned_drink_effect":None,
            "predecision_learned_values_sha256":"pre_value",
            "predecision_personal_buffer_sha256":"buffer",
            "postlearning_values_sha256":"post_value",
            "capture_water_before_decision":30,
            "positive_water_uptake":False,
            "paid_replays_actual":len(chosen),
        }

    def test_primary_mechanism_and_null_adverse_life_reported(self):
        rows=[]
        for case in self.rows:
            is_random=case["policy"]==D.POLICIES[1]
            s=self.step(chosen=(2,3) if is_random else (0,1))
            r={**case,"terminal":"censored","steps_lived":400,
               "dead_at_horizon":False,
               "paid_energy":100.,"paid_vigilance":110.,
               "replays_paid":2,"sleep_steps":1,
               "random_content_receipt":None,
               "world_sha256":str(case["world_seed"]),
               "genome_sha256":str(case["genome_seed"]),
               "source_sha256":"synthetic-test",
               "chronology":{"schema":D.OBSERVER_SCHEMA,"steps":[s]}}
            rows.append(r)
        report=D.analyze(self.rows,rows)
        self.assertEqual(report["mechanism"]["assigned_pairs"],24)
        self.assertEqual(report["mechanism"]["pairs_with_different_replay_content"],24)
        self.assertEqual(report["mechanism"]["pairs_with_same_state_first_replay_difference"],24)
        self.assertEqual(report["mechanism"]["belief_differences_after_first_replay_choice"],0)
        self.assertEqual(report["overall"]["paired_risk_difference_priority_minus_random"],0)
        self.assertFalse(report["mechanism"]["causal_mediation_claim"])
        wrong=deepcopy(rows)
        wrong[0]["chronology"]["steps"][0]["pre_replay_state_sha256"]="different"
        adjusted=D.analyze(self.rows,wrong)
        self.assertEqual(adjusted["mechanism"]["pairs_with_same_state_first_replay_difference"],23)
        adverse=deepcopy(rows)
        adverse[0]["terminal"]="dead"
        adverse[0]["dead_at_horizon"]=True
        score=D.analyze(self.rows,adverse)["overall"]
        self.assertEqual(score["random_content_only_survives"],1)
        self.assertEqual(score["paired_risk_difference_priority_minus_random"],-1/24)
        with self.assertRaises(ValueError):
            D.analyze(self.rows,rows[:-1])


if __name__=="__main__":
    unittest.main()
