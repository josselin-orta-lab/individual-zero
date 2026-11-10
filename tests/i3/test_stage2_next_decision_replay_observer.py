"""Next-perception real replay counterfactual: no World in unit tests."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i3.lab import stage2_next_decision_replay_engineering as ENG
from i3.lab import stage2_survival_b1_worldspec_audit as SPECS
from i3.lab import stage2_admission as GUARD
from i3.lab import stage2_replay_content_local as LOCAL
from i3.modules.genome import generation_zero
from i3.modules.p13_replay_gate_mind import P13ReplayGateMind
from i3.modules.body import BodyLaws
from i3.runtime import admission as RA
from i3.runtime.next_decision_replay_observer import (
    NextDecisionReplayObserver,SCHEMA)


class NextDecisionReplayObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=ENG.cases()
        cls.fingerprint=ENG.SOURCE.source_fingerprint()

    def test_strict_new_public_unit_admission(self):
        self.assertEqual([x["index"] for x in self.cases],[184,185])
        self.assertEqual(len(self.cases),2)
        c=self.cases[0]
        spec=SPECS._construct_f0_spec(c["family"],c["world_seed"])
        ticket=GUARD.admit_next_decision_replay_engineering(
            case=c,spec=spec,transport_fingerprint=self.fingerprint)
        self.assertEqual(RA.verify(ticket,spec)["cohort"],"engineering")
        for alteration in ({"index":183},{"index":186},{"index":True},
                           {"cohort":"development"},{"cohort":"selection"},
                           {"cohort":"validation"},{"cohort":"reserve"},
                           {"policy":"p13_replay_gate_v1"},
                           {"world_seed":-1},{"life_seed":-1}):
            with self.subTest(change=alteration),self.assertRaises(PermissionError):
                GUARD.admit_next_decision_replay_engineering(
                    case=dict(c,**alteration),spec=spec,
                    transport_fingerprint=self.fingerprint)
        with self.assertRaises(PermissionError):
            GUARD.admit_next_decision_replay_engineering(
                case=c,spec=spec,transport_fingerprint="0"*64)

    def test_unborn_wrong_case_cannot_construct_world(self):
        c=self.cases[0]
        for alteration in ({"index":183},{"index":186},
                           {"cohort":"development"},{"life_seed":-1}):
            with patch.object(SPECS,"_construct_f0_spec") as ctor:
                with self.assertRaises(PermissionError):
                    ENG._run(dict(c,**alteration),self.fingerprint,True)
                ctor.assert_not_called()

    def test_first_fork_has_no_effect_on_live_td_and_no_oracle(self):
        genome=generation_zero(LOCAL.GENOME_SEED_START)
        mind=P13ReplayGateMind(genome,99101,mode="gate_random_content")
        sample=LOCAL.synthetic_mind(0)
        mind.buffer=deepcopy(sample.buffer)
        mind.last=(LOCAL.BODY,("dormir",),"dormir",None)
        mind.content_sleep_ordinal=3
        control=deepcopy(mind)
        witness=NextDecisionReplayObserver(mind)
        effect={"dead":False,"body":LOCAL.BODY,"moved":False}
        self.assertEqual(mind.learn_from_outcome(
            effect,replay_limit=3,replay_observer=witness.replay),3)
        self.assertEqual(control.learn_from_outcome(effect,replay_limit=3),3)
        self.assertEqual(mind.values,control.values)
        self.assertEqual(list(mind.buffer),list(control.buffer))
        witness.after_learning()
        report=witness.report()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["status"],
                         "FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION")
        self.assertTrue(report["first_fork"]["different_learned_values"])
        self.assertIsNone(report["first_fork"]["next_decision"])
        self.assertTrue(report["external_detached_work_only"])
        self.assertTrue(report["no_second_world"])
        self.assertTrue(report["no_calibrated_predictive_accuracy_claim"])

    def test_null_without_actual_replay_is_not_dropped(self):
        mind=P13ReplayGateMind(
            generation_zero(LOCAL.GENOME_SEED_START),222,
            mode="gate_random_content")
        obs=NextDecisionReplayObserver(mind)
        self.assertEqual(obs.report()["status"],"NO_DIFFERENT_FUNDED_REPLAY")
        self.assertIsNone(obs.report()["first_fork"])
        self.assertEqual(obs.report()["funded_opportunities"],0)
        with self.assertRaises(PermissionError):
            NextDecisionReplayObserver(
                P13ReplayGateMind(
                    generation_zero(LOCAL.GENOME_SEED_START),222,
                    mode="gate"))

    def test_on_off_four_physical_engineering_executions(self):
        # Slow technical lives are checked in a separate branch-gated job,
        # not repeated inside the 987+ tests on every pull request.
        self.assertEqual(ENG.UNITS,2)
        self.assertEqual(ENG.HORIZON,260)
        self.assertEqual(ENG.POLICY,"p13_replay_gate_random_content_v1")


if __name__=="__main__":
    unittest.main()
