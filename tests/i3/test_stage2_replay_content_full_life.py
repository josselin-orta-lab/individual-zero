"""Replay-content full-life transport tests, World lives never run in tests."""
from collections import deque
from copy import deepcopy
import random
import unittest
from unittest.mock import patch

from i3.lab import stage2_replay_content_engineering as ENG
from i3.lab import stage2_survival_b1_sampling as SAMPLE
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.lab import stage2_replay_content_local as LOCAL
from i3.modules.genome import generation_zero
from i3.modules.mind import Mind
from i3.modules.p13_replay_gate_mind import P13ReplayGateMind
from i3.modules.stage2_replay_content_selection import random_content_indices
from i3.runtime import admission as RA


class ContentFullLifeEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=ENG.cases()
        cls.source=ENG.SOURCE.source_fingerprint()

    def test_unused_fixed_two_arm_pairs(self):
        self.assertEqual(len(self.rows),24)
        preview=SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"]
        for i in range(12):
            original=preview[ENG.FIRST+i]
            first,second=self.rows[2*i:2*i+2]
            self.assertEqual(first["index"],144+i)
            self.assertEqual(first["policy"],ENG.POLICIES[0])
            self.assertEqual(second["policy"],ENG.POLICIES[1])
            for key in ("index","world_seed","genome_seed",
                        "life_seed","pair_id","family"):
                self.assertEqual(first[key],second[key])
            for key in ("world_seed","genome_seed","life_seed"):
                self.assertEqual(first[key],original[key])
            self.assertEqual(first["cohort"],"engineering")
        self.assertEqual(len({r["world_seed"] for r in self.rows}),12)
        old=preview[:144]
        self.assertTrue({r["world_seed"] for r in self.rows}.isdisjoint(
            {r["world_seed"] for r in old}))

    def test_case_mutation_rejected_before_spec_and_birth(self):
        runner=ENG._run_case(self.rows,self.source)
        for change in (
            {"index":143},{"index":156},{"index":360000},{"index":True},
            {"cohort":"development"},{"cohort":"validation"},
            {"cohort":"selection"},{"cohort":"reserve"},
            {"family":"unknown"},{"policy":"reference"},
            {"life_seed":SAMPLE.LIFE_BASE+99},
            {"world_seed":SAMPLE.WORLD_BASE+99},
            {"genome_seed":SAMPLE.GENOME_BASE+99},
        ):
            with self.subTest(change=change):
                case=dict(self.rows[0],**change)
                with patch.object(SPECS,"_construct_f0_spec") as mk:
                    with self.assertRaises(PermissionError):
                        runner(case)
                    mk.assert_not_called()
        with self.assertRaises(PermissionError):
            runner(None)
        with self.assertRaises(PermissionError):
            ENG.execute()

    def test_central_engineering_admission_and_source_binding(self):
        case=self.rows[1]
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_replay_content_newworld_engineering(
            case=case,spec=spec,transport_fingerprint=self.source)
        self.assertEqual(RA.verify(ticket,spec)["cohort"],"engineering")
        with self.assertRaises(PermissionError):
            GUARD.admit_replay_content_newworld_engineering(
                case=case,spec=spec,transport_fingerprint="f"*64)
        from dataclasses import replace
        changed=replace(spec,body=(1.,60.,60.,60.,60.))
        with self.assertRaises(PermissionError):
            GUARD.admit_replay_content_newworld_engineering(
                case=case,spec=changed,transport_fingerprint=self.source)

    def test_memory_identity_random_is_reproducible_and_independent(self):
        random.seed(53)
        before=random.getstate()
        x=random_content_indices(eligible=12,count=3,life_seed=77,
                                 sleep_ordinal=1)
        self.assertEqual(len(x),len(set(x)))
        self.assertEqual(x,random_content_indices(
            eligible=12,count=3,life_seed=77,sleep_ordinal=1))
        self.assertEqual(random.getstate(),before)
        self.assertTrue(all(0<=i<12 for i in x))
        for bad in ({"count":13},{"eligible":-1},{"count":True},
                    {"sleep_ordinal":-1},{"life_seed":1.2}):
            params={"eligible":12,"count":3,"life_seed":77,
                    "sleep_ordinal":1}
            params.update(bad)
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                random_content_indices(**params)

    def test_real_td_update_same_count_but_different_memory_choices(self):
        genome=generation_zero(LOCAL.GENOME_SEED_START)
        priority=P13ReplayGateMind(genome,1101,mode="gate")
        randomized=P13ReplayGateMind(genome,1101,mode="gate_random_content")
        source=LOCAL.synthetic_mind(0)
        for mind in (priority,randomized):
            mind.buffer=deque(deepcopy(list(source.buffer)))
            mind.last=(LOCAL.BODY,("dormir",),"dormir",None)
        randomized.content_sleep_ordinal=1
        random_before=randomized.rng.getstate()
        budget_before=randomized._budget_rng.getstate()
        result={"dead":False,"body":LOCAL.BODY,"moved":False}
        self.assertEqual(priority.learn_from_outcome(result,replay_limit=3),3)
        self.assertEqual(randomized.learn_from_outcome(result,replay_limit=3),3)
        self.assertEqual(randomized.content_replays_executed,3)
        self.assertEqual(randomized.content_replay_opportunities,1)
        self.assertEqual(randomized.rng.getstate(),random_before)
        self.assertEqual(randomized._budget_rng.getstate(),budget_before)
        self.assertNotEqual(priority.values,randomized.values)
        self.assertEqual(priority.content_replays_executed,0)

    def test_full_life_transport_mock_keeps_motor_and_source(self):
        pair=self.rows[:2]
        seen=[]
        def fake_life(genome,spec,life_seed,horizon,*,decision_policy,admission,**kw):
            self.assertEqual(RA.verify(admission,spec)["cohort"],"engineering")
            self.assertEqual(horizon,400)
            self.assertEqual(life_seed,pair[0]["life_seed"])
            seen.append(decision_policy)
            return {"mock":True}
        with patch.object(ENG,"run_life",side_effect=fake_life):
            runner=ENG._run_case(self.rows,self.source)
            for case in pair:
                self.assertTrue(runner(case)["mock"])
        self.assertEqual(seen,list(ENG.POLICIES))


if __name__=="__main__":
    unittest.main()
