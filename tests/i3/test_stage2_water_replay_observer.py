"""Read-only replay/water observer and newborn engineering admission guards."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_water_replay_observer_engineering as ENG
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.lab import stage2_replay_content_local as LOCAL
from i3.modules.genome import generation_zero
from i3.modules.p13_replay_gate_mind import P13ReplayGateMind
from i3.runtime import admission as RA
from i3.runtime.replay_water_observer import (
    ReplayWaterObserver, first_divergences, SCHEMA)


class WaterReplayObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=ENG.cases()
        cls.source=ENG.SOURCE.source_fingerprint()

    def test_new_source_and_ticket_rejects_old_and_scientific(self):
        self.assertEqual(len(self.rows),4)
        self.assertEqual({x["index"] for x in self.rows},{180,181})
        for i in range(2):
            a,b=self.rows[2*i:2*i+2]
            self.assertEqual((a["policy"],b["policy"]),ENG.POLICIES)
            for key in ("index","world_seed","genome_seed","life_seed"):
                self.assertEqual(a[key],b[key])
        c=self.rows[0]
        spec=SPECS._construct_f0_spec(c["family"],c["world_seed"])
        t=GUARD.admit_water_replay_observer_engineering(
            case=c,spec=spec,transport_fingerprint=self.source)
        self.assertEqual(RA.verify(t,spec)["cohort"],"engineering")
        for change in (
            {"index":144},{"index":179},{"index":182},
            {"cohort":"development"},{"cohort":"reserve"},
            {"cohort":"selection"},{"cohort":"validation"},
            {"policy":"reference"},{"life_seed":-1},{"world_seed":-1},
        ):
            with self.subTest(change=change),self.assertRaises(PermissionError):
                GUARD.admit_water_replay_observer_engineering(
                    case=dict(c,**change),spec=spec,
                    transport_fingerprint=self.source)
        with self.assertRaises(PermissionError):
            GUARD.admit_water_replay_observer_engineering(
                case=c,spec=spec,transport_fingerprint="bad")

    def test_callback_cannot_change_original_td_or_add_work(self):
        g=generation_zero(LOCAL.GENOME_SEED_START)
        result={"dead":False,"body":LOCAL.BODY,"moved":False}
        for mode in ("gate","gate_random_content"):
            original=P13ReplayGateMind(g,10101,mode=mode)
            original.buffer=deepcopy(LOCAL.synthetic_mind(0).buffer)
            original.last=(LOCAL.BODY,("dormir",),"dormir",None)
            observed=deepcopy(original)
            if mode=="gate_random_content":
                original.content_sleep_ordinal=observed.content_sleep_ordinal=1
            witnessed=[]
            def callback(chosen,ranked,priorities):
                witnessed.append((tuple(chosen),tuple(ranked),tuple(priorities)))
                return ["this mutation must be ignored"]
            self.assertEqual(original.learn_from_outcome(result,replay_limit=3),3)
            self.assertEqual(observed.learn_from_outcome(
                result,replay_limit=3,replay_observer=callback),3)
            self.assertEqual(len(witnessed),1)
            self.assertEqual(len(witnessed[0][0]),3)
            self.assertEqual(original.values,observed.values)
            self.assertEqual(list(original.buffer),list(observed.buffer))
            self.assertEqual(original.rng.getstate(),observed.rng.getstate())
            self.assertEqual(original._budget_rng.getstate(),
                             observed._budget_rng.getstate())
            self.assertEqual(original.content_replays_executed,
                             observed.content_replays_executed)
        with self.assertRaises(TypeError):
            observed.learn_from_outcome(result,replay_limit=3,replay_observer=True)

    def test_first_divergence_distinguishes_channels_and_shorter_life(self):
        row={"step":1,"replay_memory_indices":[1,2],
             "pre_replay_state_sha256":"same_pre_td_state",
             "predecision_learned_values_sha256":"same_values",
             "predecision_personal_buffer_sha256":"same_buffer",
             "postlearning_values_sha256":"same_post_values",
             "personally_learned_drink_effect":None,
             "personal_water_belief_sha256":"a",
             "decision_option":"boire","action":"boire","param":None,
             "capture_water_before_decision":48}
        a={"schema":SCHEMA,"steps":[row,dict(row,step=2)]}
        b={"schema":SCHEMA,"steps":[dict(row),dict(
            row,step=2,replay_memory_indices=[3,4],
            personal_water_belief_sha256="b",action="dormir",
            decision_option="dormir",capture_water_before_decision=47)]}
        x=first_divergences(a,b)
        self.assertEqual(x["first_differences"],{
            "replay_memory_indices":2,"personal_water_belief":2,
            "decision":2,"body_water":2,
            "pre_replay_learned_state":None,
            "predecision_learned_values":None,
            "predecision_memory_buffer":None,
            "postlearning_values":None,
            "learned_drink_effect":None})
        self.assertFalse(x["fixed_count_causal_mediation_claim"])
        short={"schema":SCHEMA,"steps":[row]}
        self.assertEqual(first_divergences(short,b)["common_observed_steps"],1)

    def test_unfunded_or_forged_replay_rejected(self):
        obs=ReplayWaterObserver()
        with self.assertRaises(RuntimeError):
            obs.replay((0,), (0,), (1.,))
        for bad in ([(0,0)], [True], [3], [-1]):
            obs._pending={"replay_priority_indices":[],
                          "replay_memory_indices":[],
                          "replay_count_prepaid":0}
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                obs.replay(tuple(bad),(0,1),(2.,1.))
        obs._pending=None
        with self.assertRaises(RuntimeError):
            obs.report() if obs._pending is not None else obs.commit(
                mind=None,world=None,result={},replay_limit=None,post_audit={})


if __name__=="__main__":
    unittest.main()
