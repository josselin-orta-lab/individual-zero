"""Longitudinal G2 H2 writes: evicted evidence must fail before COMMIT."""
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_feedback_calibration import Source as H2Source, opportunity, forecast, heldout
from test_unified_control_cycle import A, B, C, Values, Current, Safety, Terminal
from i2.modules.delayed_credit_study import empty_feedback_memory, read_feedback, learn_from_feedback
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture


class LongitudinalH2Tests(unittest.TestCase):
    def test_seventeen_commits_cold_replay_and_evicted_issue_rejected(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "v5.sqlite"
        memory = empty_feedback_memory(opportunity(10))
        life = memory.life_ref
        class Subject:
            def verify(self, *, life_ref, claim, digest):
                return life_ref == life
        ports = dict(path=path, life_ref=life, observation_source=Subject(),
                     valuation_source=Values(), current_source=Current(),
                     safety_source=Safety(), genesis_ref="genesis:longitudinal",
                     terminal_source=Terminal())
        owner = CognitiveCycleFixture.create(synthetic_uc=100, **ports)
        source = H2Source()
        first_score = None
        for index in range(17):
            issue_step = 10 + index * 15
            readout = read_feedback(memory=memory, forecast=forecast(issue_step),
                                    source=source)
            prep, control = heldout(issue_step + 2, index % 3, 0)
            update = learn_from_feedback(memory=memory, readout=readout,
                                         prepared=prep, control=control, source=source)
            if index == 0:
                first_score = update.heldout_score
            commit_step = issue_step + 10
            observed = ObservationClaim(
                life, FirstPersonCapture(
                    commit_step, f"cycle:{commit_step}", memory.goal_ref,
                    tuple(sorted((A, B, C)))),
                f"source:cycle:{commit_step}", (f"evidence:{commit_step}",))
            if index == 0:
                owner.open(claim=observed, semantic_ref=A,
                           evidence_ref=f"evidence:{commit_step}", ttl_steps=12,
                           feedback_previous=memory, feedback_update=update)
            else:
                owner.observe(claim=observed, feedback_previous=memory,
                              feedback_update=update)
            owner = CognitiveCycleFixture.reopen(**ports)
            memory = owner.feedback_snapshot()
            self.assertEqual(memory, update.new_memory)
            self.assertEqual(owner.audit()["feedback_version"], index + 1)
        scorecard = owner.feedback_scorecard()
        self.assertEqual(scorecard["samples"], 17)
        self.assertEqual(scorecard["adaptive_mae"], scorecard["rows"][0]["adaptive_error"] * 0 +
                         sum(row["adaptive_error"] for row in scorecard["rows"]) / 17)
        self.assertEqual(scorecard["motor_authority"], "NONE")
        self.assertFalse(scorecard["m11_authenticated"])
        self.assertEqual(owner.audit()["committed"], 17)
        cold = CognitiveCycleFixture.reopen(**ports).feedback_scorecard()
        self.assertEqual(scorecard, cold)
        self.assertEqual(len(memory.used_issue_captures), 16)
        self.assertNotIn(first_score.issue_capture_ref, memory.used_issue_captures)

        at = 10 + 17 * 15
        readout = read_feedback(memory=memory, forecast=forecast(at), source=source)
        prep, control = heldout(at + 2, 2, 0)
        update = learn_from_feedback(memory=memory, readout=readout,
                                     prepared=prep, control=control, source=source)
        # Even when the bounded snapshot forgot the first issuance, the
        # single transaction journal must still reject that identifier.
        replay = replace(update, heldout_score=replace(
            update.heldout_score, issue_capture_ref=first_score.issue_capture_ref))
        capture = ObservationClaim(
            life, FirstPersonCapture(at + 10, f"cycle:{at + 10}",
                                     memory.goal_ref, tuple(sorted((A, B, C)))),
            f"source:cycle:{at + 10}", (f"evidence:{at + 10}",))
        before = owner.audit()
        with self.assertRaisesRegex(ValueError, "replayed H2 evidence outside"):
            owner.observe(claim=capture, feedback_previous=memory,
                          feedback_update=replay)
        after = CognitiveCycleFixture.reopen(**ports).audit()
        self.assertEqual(after["committed"], before["committed"])
        self.assertEqual(after["remaining_synthetic_uc"],
                         before["remaining_synthetic_uc"])
        self.assertEqual(after["feedback_version"], 17)


if __name__ == "__main__":
    unittest.main()
