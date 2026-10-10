"""Synthetic INV-53 journal regressions, not held-out physical evidence."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.journal import HashChainedJournal
from lab.stage9_canonical_journal_audit import audit_raw_causal_journal


def synthetic_journal(
    *, second_step: int = 1, second_committed: bool = True,
    second_fault: str | None = None,
) -> bytes:
    journal = HashChainedJournal()
    for label, step, committed in (
        ("first", 1, True), ("second", second_step, second_committed),
    ):
        attempt = f"synthetic-attempt:{label}"
        command = f"synthetic-command:{label}"
        transition = f"synthetic-transition:{label}"
        if label != "second" or second_fault != "no_command":
            journal.append(
                event_id=command,
                causal_event={
                    "kind": "command_experienced",
                    "attempt_ref": attempt, "t_monde": step,
                },
            )
        if label == "second" and second_fault == "extra_command":
            journal.append(
                event_id=f"synthetic-extra-command:{label}",
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
        if label == "first" and second_fault == "foreign_cognitive_ref":
            journal.append(
                event_id="synthetic-cognitive:first",
                causal_event={
                    "kind": "s_t_published",
                    "attempt_ref": attempt, "t_monde": step,
                    "data": {"synthetic": True},
                },
            )
        if label == "second" and second_fault == "extra_transition":
            journal.append(
                event_id=f"synthetic-extra-transition:{label}",
                causal_event={
                    "kind": "world_transition_experienced",
                    "attempt_ref": attempt, "t_monde": step,
                },
            )
        if label == "second" and second_fault in (
            "technical_leak", "wrong_step_cognitive", "valid_cognitive",
        ):
            event_kind = (
                "oracle_annotation" if second_fault == "technical_leak"
                else "s_t_published"
            )
            journal.append(
                event_id="synthetic-secondary-event",
                causal_event={
                    "kind": event_kind,
                    "attempt_ref": attempt,
                    "t_monde": 999 if second_fault == "wrong_step_cognitive" else step,
                    "data": {"synthetic": True},
                },
            )
        if committed:
            refs = (
                [command]
                if label == "second" and second_fault == "omit_transition_ref"
                else (
                    [transition]
                    if label == "second" and second_fault == "no_command"
                    else [command, transition]
                )
            )
            if label == "second" and second_fault in (
                "technical_leak", "wrong_step_cognitive", "valid_cognitive",
            ):
                refs.append("synthetic-secondary-event")
            if label == "second" and second_fault == "foreign_cognitive_ref":
                refs.append("synthetic-cognitive:first")
            event = {
                "kind": "auto_segment_commit",
                "attempt_ref": attempt,
                "t_monde": step,
                "event_refs": refs,
            }
            journal.append(
                event_id=f"synthetic-commit:{label}", causal_event=event,
            )
            if label == "second" and second_fault == "extra_commit":
                journal.append(
                    event_id=f"synthetic-extra-commit:{label}",
                    causal_event=event,
                )
    assert journal.verify()
    return journal.canonical_bytes()


class Stage9CommittedWorldStepTests(unittest.TestCase):
    def inspect(
        self, *, second_step: int, second_committed: bool,
        second_fault: str | None = None,
    ):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic-causal-journal.jsonl"
            path.write_bytes(synthetic_journal(
                second_step=second_step,
                second_committed=second_committed,
                second_fault=second_fault,
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


    def test_unreported_committed_attempt_cannot_hide_extra_applied_events(self):
        # The second attempt is not in physical_observation_refs, and has
        # its own completed *different* world step. It still cannot claim
        # two commands, two advancements, or an advancement without command.
        for fault in ("extra_command", "extra_transition", "no_command"):
            with self.subTest(fault=fault):
                with self.assertRaisesRegex(
                    ValueError, "committed physical attempt has nonunique",
                ):
                    self.inspect(
                        second_step=2, second_committed=True,
                        second_fault=fault,
                    )

    def test_unreported_attempt_cannot_hide_extra_memory_commit(self):
        # A duplicate autobiographical close with a new event ID must not
        # confer a second valid physical sample outside scoring rows.
        with self.assertRaisesRegex(
            ValueError, "physical attempt has multiple Memory commits",
        ):
            self.inspect(
                second_step=2, second_committed=True,
                second_fault="extra_commit",
            )

    def test_unreported_commit_must_include_its_applied_transition(self):
        with self.assertRaisesRegex(
            ValueError, "committed physical attempt lacks ordered applied events",
        ):
            self.inspect(
                second_step=2, second_committed=True,
                second_fault="omit_transition_ref",
            )

    def test_rollback_with_extra_uncommitted_events_is_not_accepted(self):
        # The append-only technical trace may include an abnormal cancelled
        # attempt. Without AutoSegmentCommit it provides no accepted sample.
        for fault in ("extra_command", "extra_transition"):
            with self.subTest(fault=fault):
                result = self.inspect(
                    second_step=1, second_committed=False,
                    second_fault=fault,
                )
                self.assertEqual(result["claimed_physical_transitions_checked"], 1)
                self.assertFalse(result["physical_truth_attested"])


    def test_unreported_commit_rejects_foreign_or_wrong_step_cognitive_ref(self):
        # Both sources pass the hash chain and refer to an existing, earlier
        # event of an autobiographically allowed kind. A source from another
        # attempt or world step must still fail.
        for fault in ("foreign_cognitive_ref", "wrong_step_cognitive"):
            with self.subTest(fault=fault):
                with self.assertRaisesRegex(
                    ValueError, "committed Memory reference crosses attempts",
                ):
                    self.inspect(
                        second_step=2, second_committed=True, second_fault=fault,
                    )

    def test_unreported_commit_rejects_technical_oracle_event(self):
        # Unknown technical kinds are *not* added to DC-09 by mentioning them
        # in a syntactically valid autobio commit.
        with self.assertRaisesRegex(
            ValueError, "exposes technical event",
        ):
            self.inspect(
                second_step=2, second_committed=True,
                second_fault="technical_leak",
            )

    def test_unreported_commit_allows_same_attempt_perceptible_event(self):
        # Match the versioned Stage-7 allowlist actually used by Stage 9.
        result = self.inspect(
            second_step=2, second_committed=True,
            second_fault="valid_cognitive",
        )
        self.assertEqual(result["claimed_physical_transitions_checked"], 1)
        self.assertFalse(result["physical_truth_attested"])

    def test_distinct_completed_world_steps_are_still_accepted(self):
        result = self.inspect(second_step=2, second_committed=True)
        self.assertEqual(result["claimed_physical_transitions_checked"], 1)
        self.assertEqual(result["journal_events_checked"], 6)
        self.assertFalse(result["physical_truth_attested"])


if __name__ == "__main__":
    unittest.main()
