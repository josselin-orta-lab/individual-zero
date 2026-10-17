"""Reject cryptographically valid, semantically false stopped-step archives.

An admitted command or autobiographical commitment cannot be counted as
"blocked"/"external_stop" with zero world advances under MVP v1.3.1 M-01/M-19.
These are deliberately forged self-consistent hashes, not untrusted plaintext.
"""
from __future__ import annotations

import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal


def stopped_fixture(*, outcome, with_command=False, with_memory=False):
    journal = HashChainedJournal()

    def add(identifier, kind, **extra):
        journal.append(
            event_id=identifier,
            causal_event={
                "kind": kind, "emitter": "test", "t_monde": 1,
                "attempt_ref": "attempt:1", **extra,
            },
        )

    add("opened", "step_opened", data={"attempt_index": 0})
    if with_command:
        add("command", "command_experienced", command_hash="fake-command",
            primitive="attendre", parameters={})
    if with_memory:
        add("committed", "auto_segment_commit", event_refs=["command"],
            filter_version="stage2-autobio-v1")
    add("closed", "step_closed", data={
        "outcome": outcome,
        "applied_command_count": 0,
        "world_advance_count": 0,
    })
    assert journal.verify()
    return journal


class StoppedStepAuditTests(unittest.TestCase):
    def test_valid_stops_without_accepted_command_remain_auditable(self):
        for outcome in ("blocked", "external_stop"):
            with self.subTest(outcome=outcome):
                journal = stopped_fixture(outcome=outcome)
                result = audit_export_bytes(
                    journal.canonical_bytes(),
                    expected_head=journal.head_hash,
                    expected_count=len(journal.entries),
                )
                self.assertEqual(result.world_steps_closed, 1)
                self.assertEqual(result.autobiographical_commits, 0)

    def test_rehashed_stopped_step_cannot_claim_that_command_disappeared(self):
        for outcome in ("blocked", "external_stop"):
            for memory in (False, True):
                with self.subTest(outcome=outcome, false_memory=memory):
                    forged = stopped_fixture(
                        outcome=outcome, with_command=True, with_memory=memory,
                    )
                    self.assertTrue(forged.verify())
                    with self.assertRaisesRegex(ValueError, "stopped step contains"):
                        audit_export_bytes(
                            forged.canonical_bytes(),
                            expected_head=forged.head_hash,
                            expected_count=len(forged.entries),
                        )


if __name__ == "__main__":
    unittest.main()
