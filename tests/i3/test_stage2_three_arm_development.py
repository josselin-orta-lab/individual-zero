"""Three-arm EXPLORATORY original-custody tests; never run a real life."""
from copy import deepcopy
import os
from unittest.mock import patch
import unittest

from i3.lab import stage2_three_arm_development as THREE
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.runtime import admission as RA


class ThreeArmDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=THREE.cases()
        cls.fingerprint=THREE.SOURCE.source_fingerprint()

    def test_frozen_allocation_and_external_authority_not_claimed(self):
        rows=self.cases
        plan=THREE.load_plan()
        self.assertEqual(len(rows),192)
        self.assertEqual(plan["units"],64)
        self.assertFalse(plan["witness_independent_external_attestation"])
        self.assertFalse(plan["scientific_registration"])
        self.assertEqual(plan["scientific_noninferiority_margin"],None)
        self.assertEqual([rows[i]["index"] for i in range(0,192,3)],
                         list(range(360000,360064)))
        self.assertEqual({r["cohort"] for r in rows},{"development"})
        self.assertEqual({r["policy"] for r in rows},set(THREE.ARMS))
        self.assertEqual(len({r["world_seed"] for r in rows}),64)
        self.assertEqual(rows,THREE.cases())
        for i in range(64):
            triple=rows[3*i:3*i+3]
            self.assertEqual(tuple(r["policy"] for r in triple),THREE.ARMS)
            for k in ("pair_id","index","family","world_seed",
                      "genome_seed","life_seed"):
                self.assertEqual(len({r[k] for r in triple}),1)

    def test_foreign_cases_rejected_before_world_construction(self):
        runner=THREE._run_case(self.cases,self.fingerprint)
        for change in (
            {"cohort":"selection"},{"cohort":"validation"},{"cohort":"reserve"},
            {"index":80},{"index":96},{"index":240000},{"index":359999},
            {"index":360064},{"index":True},
            {"policy":"p13_replay_gate_zero_perceived_cost_v1"},
            {"family":"unknown"},{"life_seed":SAMPLE.LIFE_BASE+7},
            {"world_seed":SAMPLE.WORLD_BASE+7},
            {"genome_seed":SAMPLE.GENOME_BASE+7},
        ):
            with self.subTest(change=change):
                case=dict(self.cases[0],**change)
                with patch.object(SPECS,"_construct_f0_spec") as ctor:
                    with self.assertRaises(PermissionError):
                        runner(case)
                    ctor.assert_not_called()
        with self.assertRaises(PermissionError):
            runner(None)

    def test_guards_bind_all_three_policy_worlds_and_funding(self):
        triple=self.cases[:3]
        def fake(genome,spec,seed,horizon,*,decision_policy,admission,**kwargs):
            self.assertEqual(seed,triple[0]["life_seed"])
            self.assertEqual(horizon,400)
            self.assertEqual(kwargs["protocol"],THREE.PROTOCOL)
            if decision_policy=="reference":
                self.assertIsNone(admission)
            else:
                self.assertEqual(RA.verify(admission,spec)["cohort"],"development")
            return {"mocked":True}
        runner=THREE._run_case(self.cases,self.fingerprint)
        with patch.object(THREE,"run_life",side_effect=fake):
            for case in triple:
                out=runner(case)
                self.assertTrue(out["mocked"])
                self.assertEqual(out["admission_receipt"]["index"],360000)
        spec=SPECS._construct_f0_spec(triple[2]["family"],triple[2]["world_seed"])
        with self.assertRaises(PermissionError):
            GUARD.admit_three_arm_newworld_development(
                case=triple[2],spec=spec,transport_fingerprint="f"*64)
        from dataclasses import replace
        changed=replace(spec,body=(1.,60.,60.,60.,60.))
        with self.assertRaises(PermissionError):
            GUARD.admit_three_arm_newworld_development(
                case=triple[2],spec=changed,transport_fingerprint=self.fingerprint)

    def test_only_trusted_main_claim_can_open_a_cohort(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                THREE.execute("/tmp/no-new-world-opening")
        with patch.dict(os.environ,{
                "GITHUB_EVENT_NAME":"pull_request","GITHUB_REF":"refs/heads/main",
                "GITHUB_RUN_ATTEMPT":"1",
                "I3_THREE_ARM_CLAIM_BRANCH":THREE.CLAIM_BRANCH,
                "GITHUB_SHA":"a"*40},clear=True):
            with self.assertRaises(PermissionError):
                THREE._trusted_source_claim()

    def test_three_policy_analysis_requires_complete_originals(self):
        fake=[]
        for case in self.cases:
            r={**case,
               "terminal":"censored","steps_lived":400,
               "paid_energy":100.,"paid_vigilance":110.,
               "replays_paid":8,"sleep_steps":2,"inactive_steps":3,
               "dead_at_400":False,
               "random_schedule":None,
               "world_sha256":str(case["world_seed"]),
               "genome_sha256":str(case["genome_seed"]),
               "source_sha256":"source"}
            fake.append(r)
        result=THREE.analyze(self.cases,fake)
        self.assertEqual(result["primary"],"GATE_MINUS_RANDOM")
        self.assertEqual(result["overall_contrasts"]["GATE_MINUS_RANDOM"]["target_only_survives"],0)
        self.assertFalse(result["external_iid_or_ecological_sampling_attestation"])
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        with self.assertRaises(ValueError):
            THREE.analyze(self.cases,fake[:-1])
        broken=deepcopy(fake)
        broken[0],broken[3]=broken[3],broken[0]
        with self.assertRaises(ValueError):
            THREE.analyze(self.cases,broken)
        adverse=deepcopy(fake)
        adverse[2]["terminal"]="dead"
        adverse[2]["dead_at_400"]=True
        summary=THREE.analyze(self.cases,adverse)
        self.assertEqual(summary["overall_contrasts"]["GATE_MINUS_RANDOM"]["target_only_survives"],1)
        self.assertEqual(summary["by_arm"][THREE.ARMS[2]]["deaths_at_horizon"],1)

    def test_three_arm_actual_random_receipt_cannot_be_fake_paid(self):
        identity=self.cases[2]
        receipt={"cohort":"development","index":identity["index"],
                 "family":identity["family"],"world_seed":identity["world_seed"],
                 "world_name":"test","world_sha256":"test-world",
                 "transport_fingerprint":self.fingerprint}
        schedule={"draws_funded":2,"nominal_replays_scheduled":12,
                  "eligible_replays_scheduled":9,"actual_replays_paid":8,
                  "lived_sleep_ordinals":2,
                  "mean_numerator":5532,"mean_denominator":867}
        life={"manifest":{"world_sha256":"test-world",
                          "life_seed":identity["life_seed"],
                          "source":{"sha256":"s"},
                          "genome":{"genes":{"foo":1}},
                          "experimental_policy":{"name":identity["policy"]}},
              "admission_receipt":receipt,"world":"test",
              "steps_lived":400,"terminal":"dead","death_causes":[],
              "actions":{"dormir":2},
              "cognitive_accounting":{
                 "totals":{"energy":{"unpaid":0.,"paid":15.},
                           "vigilance":{"unpaid":0.,"paid":11.}},
                 "shortfall_steps":0,"status":"SETTLED_FOR_DECLARED_WORK",
                 "replays_executed":8,"inactive_steps":0},
              "replay_gate":{"random_schedule":schedule}}
        ok=THREE._reduce_row(identity,life,self.fingerprint)
        self.assertEqual(ok["replays_paid"],8)
        self.assertTrue(ok["dead_at_400"])
        for key,value in (("actual_replays_paid",10),
                          ("eligible_replays_scheduled",7),
                          ("nominal_replays_scheduled",15),
                          ("draws_funded",3),
                          ("mean_denominator",866)):
            with self.subTest(key=key):
                bad=deepcopy(life)
                bad["replay_gate"]["random_schedule"][key]=value
                with self.assertRaises(ValueError):
                    THREE._reduce_row(identity,bad,self.fingerprint)


if __name__=="__main__":
    unittest.main()
