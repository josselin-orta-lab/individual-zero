"""Real-world-state detached counterfactual: strict observer software tests."""
from collections import deque
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_realstate_content_fork_engineering as ENG
from i3.lab import stage2_replay_content_local as LOCAL
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.modules.genome import generation_zero
from i3.modules.p13_replay_gate_mind import P13ReplayGateMind
from i3.runtime import admission as RA
from i3.runtime.realstate_content_fork_observer import (
    RealStateContentForkObserver, SCHEMA)


class RealStateContentForkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=ENG.cases()
        cls.source=ENG.SOURCE.source_fingerprint()

    def test_immutable_unused_public_engineering_and_world_admission(self):
        self.assertEqual(len(self.cases),2)
        self.assertEqual([r["index"] for r in self.cases],[182,183])
        self.assertEqual({r["policy"] for r in self.cases},{ENG.POLICY})
        self.assertEqual({r["cohort"] for r in self.cases},{"engineering"})
        case=self.cases[0]
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_realstate_content_fork_engineering(
            case=case,spec=spec,transport_fingerprint=self.source)
        self.assertEqual(RA.verify(ticket,spec)["cohort"],"engineering")
        for alteration in ({"index":181},{"index":184},{"index":True},
                           {"cohort":"development"},{"cohort":"selection"},
                           {"cohort":"validation"},{"cohort":"reserve"},
                           {"world_seed":-1},{"policy":"p13_replay_gate_v1"}):
            with self.subTest(alteration=alteration):
                with self.assertRaises(PermissionError):
                    GUARD.admit_realstate_content_fork_engineering(
                        case=dict(case,**alteration),spec=spec,
                        transport_fingerprint=self.source)
        with self.assertRaises(PermissionError):
            GUARD.admit_realstate_content_fork_engineering(
                case=case,spec=spec,transport_fingerprint="f"*64)

    def test_real_pre_replay_snapshot_fork_is_detached_and_nonmutating(self):
        genome=generation_zero(LOCAL.GENOME_SEED_START)
        mind=P13ReplayGateMind(genome,99101,mode="gate_random_content")
        mind.buffer=deque(deepcopy(list(LOCAL.synthetic_mind(0).buffer)))
        mind.last=(LOCAL.BODY,("dormir",),"dormir",None)
        mind.content_sleep_ordinal=3
        prior=deepcopy(mind)
        observer=RealStateContentForkObserver(mind)
        result={"dead":False,"body":LOCAL.BODY,"moved":False}
        actual=mind.learn_from_outcome(
            result,replay_limit=3,replay_observer=observer.replay)
        self.assertEqual(actual,3)
        receipt=observer.report()
        self.assertEqual(receipt["schema"],SCHEMA)
        self.assertEqual(receipt["status"],"FIRST_DIFFERING_REPLAY_CAPTURED")
        fork=receipt["first_fork"]
        self.assertEqual(fork["prepaid_replays_in_each_detached_arm"],3)
        self.assertEqual(len(fork["random_memory_indices"]),3)
        self.assertEqual(len(fork["priority_memory_indices"]),3)
        self.assertNotEqual(set(fork["random_memory_indices"]),
                            set(fork["priority_memory_indices"]))
        self.assertGreaterEqual(
            fork["l1_value_difference_between_detached_updates"],0)
        self.assertFalse(fork["observer_physical_debit"])
        self.assertFalse(fork["world_or_life_clone_created"])
        self.assertEqual(mind.rng.getstate(),prior.rng.getstate())
        self.assertEqual(mind._budget_rng.getstate(),
                         prior._budget_rng.getstate())
        control=deepcopy(prior)
        self.assertEqual(control.learn_from_outcome(result,replay_limit=3),3)
        self.assertEqual(mind.values,control.values)
        self.assertEqual(list(mind.buffer),list(control.buffer))
        self.assertEqual(mind.content_replays_executed,
                         control.content_replays_executed)
        self.assertEqual(mind.content_subsets_distinct_from_priority,
                         control.content_subsets_distinct_from_priority)

    def test_replay_fork_no_success_fabrication_when_no_paid_work(self):
        genome=generation_zero(LOCAL.GENOME_SEED_START+1)
        mind=P13ReplayGateMind(genome,99102,mode="gate_random_content")
        obs=RealStateContentForkObserver(mind)
        self.assertEqual(obs.report()["status"],
                         "NO_DIFFERING_FUNDED_REPLAY_OBSERVED")
        self.assertEqual(obs.report()["prepaid_replay_opportunities_seen"],0)
        self.assertIsNone(obs.report()["first_fork"])
        with self.assertRaises(PermissionError):
            RealStateContentForkObserver(
                P13ReplayGateMind(genome,99102,mode="gate"))

    def test_wrong_public_case_fails_before_world_birth(self):
        case=self.cases[0]
        for alter in ({"index":181},{"index":184},
                      {"cohort":"development"},{"policy":"reference"},
                      {"life_seed":-1}):
            with patch.object(SPECS,"_construct_f0_spec") as create:
                with self.assertRaises(PermissionError):
                    ENG._run(dict(case,**alter),self.source,True)
                create.assert_not_called()


if __name__=="__main__":
    unittest.main()
