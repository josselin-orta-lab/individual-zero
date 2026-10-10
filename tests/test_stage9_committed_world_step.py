"""Synthetic INV-53 journal regressions, not held-out physical evidence."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.journal import HashChainedJournal
from lab.stage9_canonical_journal_audit import audit_raw_causal_journal


def synthetic_journal(*, second_step: int = 1, second_committed: bool = True) -> bytes:
    journal = HashChainedJournal()
    for label, step, committed in (
        ("first", 1, True), ("second", second_step, second_committed),
    ):
        attempt = f"synthetic-attempt:{label}"
        command = f"synthetic-command:{label}"
        transition = f"synthetic-transition:{label}"
        journal.append(
            event_id=command,
            causal_event={
                "kind": "command_experienced",
                "attempt_ref": attempt, "t_monde": step,
            },
        )
        journal.append(
            event_id=transition,
            causal_event={
                "kind": "world_transition_experienced",
                "attempt_ref": attempt, "t_monde": step,
            },
        )
        if committed:
            journal.append(
                event_id=f"synthetic-commit:{label}",
                causal_event={
                    "kind": "auto_segment_commit",
                    "attempt_ref": attempt,
                    "t_monde": step,
                    "event_refs": [command, transition],
                },
            )
    assert journal.verify()
    return journal.canonical_bytes()


class Stage9CommittedWorldStepTests(unittest.TestCase):
    def inspect(self, *, second_step: int, second_committed: bool):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic-causal-journal.jsonl"
            path.write_bytes(synthetic_journal(
                second_step=second_step,
                second_committed=second_committed,
            ))
            return audit_raw_causal_journal(
                path, physical_observation_refs={"synthetic-transition:first"},
            )

    def test_two_accepted_attempts_cannot_advance_one_world_step(self):
        # Both attempts have a separate matching command, transition and
        # Memory commit. The old per-attempt uniqueness checks accepted the
        # first while ignoring the second, unreported accepted advancement.
        with self.assertRaisesRegex(
            ValueError, "multiple committed physical advancements at one world step",
        ):
            self.inspect(second_step=1, second_committed=True)

    def test_cancelled_rollback_attempt_at_same_world_step_remains_valid(self):
        # INV-49 keeps the second attempt in technical history, but INV-44
        # does not expose it autobiographically without a valid commit.
        result = self.inspect(second_step=1, second_committed=False)
        self.assertEqual(result["claimed_physical_transitions_checked"], 1)
        self.assertFalse(result["physical_truth_attested"])

    def test_distinct_completed_world_steps_are_still_accepted(self):
        result = self.inspect(second_step=2, second_committed=True)
        self.assertEqual(result["claimed_physical_transitions_checked"], 1)
        self.assertEqual(result["journal_events_checked"], 6)
        self.assertFalse(result["physical_truth_attested"])


if __name__ == "__main__":
    unittest.main()
