"""G2 transition guard: no second persistent owner and no motor rights."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_feedback_calibration import (
    Source, opportunity, forecast, heldout,
)
from i2.modules.delayed_credit_study import (
    empty_feedback_memory, read_feedback, learn_from_feedback,
    _feedback_memory_digest,
)
from i2.modules.feedback_transition_contract import verify_feedback_transition


class TransitionTests(unittest.TestCase):
    def transition(self):
        old = empty_feedback_memory(opportunity(10))
        readout = read_feedback(memory=old, forecast=forecast(10), source=Source())
        a, b = heldout(12, -8, 4)
        update = learn_from_feedback(memory=old, readout=readout,
                                     prepared=a, control=b, source=Source())
        return old, update

    def test_exact_successor_and_predecessor(self):
        old, update = self.transition()
        proof = verify_feedback_transition(
            stored=old, expected_previous_digest=_feedback_memory_digest(old),
            update=update)
        self.assertEqual((proof.previous_version, proof.next_version), (0, 1))
        self.assertEqual(proof.next_digest, _feedback_memory_digest(update.new_memory))
        self.assertEqual(proof.motor_authority, "NONE")
        self.assertFalse(proof.m11_authenticated)

    def test_stale_snapshot_or_replay_refused(self):
        old, update = self.transition()
        with self.assertRaisesRegex(ValueError, "stale"):
            verify_feedback_transition(stored=old,
                expected_previous_digest="sha256:" + "a"*64, update=update)
        with self.assertRaises(ValueError):
            verify_feedback_transition(stored=update.new_memory,
                expected_previous_digest=_feedback_memory_digest(update.new_memory),
                update=update)

    def test_forged_version_chain_context_and_score_refused(self):
        old, update = self.transition()
        successor = update.new_memory
        cases = (
            replace(successor, total_observations=2),
            replace(successor, life_ref="life:foreign"),
            replace(successor, goal_ref="goal:other"),
            replace(successor, history_head="a"*64),
            replace(successor, observed_differences=(99,)),
            replace(successor, used_issue_captures=("issue:alien",)),
        )
        for candidate in cases:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                verify_feedback_transition(
                    stored=old, expected_previous_digest=_feedback_memory_digest(old),
                    update=replace(update, new_memory=candidate))

    def test_score_forgery_and_duplicated_episodes_refused(self):
        old, update = self.transition()
        score = update.heldout_score
        invalid = (
            replace(score, absolute_error=score.absolute_error + 1),
            replace(score, direction_agreement=not score.direction_agreement),
            replace(score, observed_episode_refs=("episode:same", "episode:same")),
            replace(score, motor_authority="ADMITTED"),
            replace(score, m11_authenticated=True),
            replace(score, observed_outcome_difference=True),
        )
        for counterfeit in invalid:
            with self.subTest(score=counterfeit), self.assertRaises(ValueError):
                verify_feedback_transition(
                    stored=old,
                    expected_previous_digest=_feedback_memory_digest(old),
                    update=replace(update, heldout_score=counterfeit))

    def test_motor_flag_never_accepted(self):
        old, update = self.transition()
        with self.assertRaises(ValueError):
            verify_feedback_transition(
                stored=old, expected_previous_digest=_feedback_memory_digest(old),
                update=replace(update, motor_authority="ADMITTED"))


if __name__ == "__main__":
    unittest.main()
