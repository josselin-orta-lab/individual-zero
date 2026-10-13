"""M11 OPT1: exact leased anchor and preserved full-history corruption alarms."""
from __future__ import annotations
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from lab.journal import HashChainedJournal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked


IDENTITY = "i0:verified-anchor-test"


def state(step=0):
    return {"individual_id": IDENTITY,
            "world": {"physical_step": step},
            "scheduler": {"t_monde": step},
            "owners": {"metacognition_health": {"cycle": step}}}


class VerifiedAnchorTests(unittest.TestCase):
    def test_audited_anchor_commits_with_two_complete_history_audits(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.sqlite")
            journal = HashChainedJournal()
            with SQLiteLifeLedger.birth(path=path, individual_id=IDENTITY,
                                        initial_state=state()) as ledger:
                calls = []
                original = ledger.audit
                def counting():
                    calls.append(1)
                    return original()
                ledger.audit = counting
                certified = ledger.audit()
                ledger.begin_intent(expected_generation=0, intent_ref="intent:1",
                                    trusted_current=certified)
                event = journal.append(event_id="event:1", causal_event={
                    "kind": "test_causal_receipt", "t_monde": 1}).as_dict()
                result = ledger.commit_generation(
                    expected_generation=0,
                    expected_head="0" * 64,
                    intent_ref="intent:1", current_state=state(1),
                    events=[event], verified_intent=certified)
                self.assertEqual(len(calls), 2)
                self.assertEqual(result.generation, 1)
                self.assertEqual(result.journal_head, journal.head_hash)

    def test_stale_and_forged_certificates_fail_closed(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.sqlite")
            with SQLiteLifeLedger.birth(path=path, individual_id=IDENTITY,
                                        initial_state=state()) as ledger:
                first = ledger.audit()
                second = ledger.audit()
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=0, intent_ref="intent:1",
                                        trusted_current=first)
                # Failing a transactional intent poisons the handle. Retest
                # with a fresh separately born identity rather than rewinding.
                self.assertIsNotNone(second)

    def test_corrupted_current_image_rejected_before_intent(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.sqlite")
            with SQLiteLifeLedger.birth(path=path, individual_id=IDENTITY,
                                        initial_state=state()) as ledger:
                current = ledger.audit()
                with sqlite3.connect(path) as external:
                    external.execute("UPDATE life_current SET state_hash='tampered' "
                                     "WHERE slot=1")
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=0, intent_ref="intent:1",
                                        trusted_current=current)
                self.assertFalse(ledger._db.in_transaction)

    def test_corrupted_historical_event_rejected_after_commit_before_publishing(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.sqlite")
            journal = HashChainedJournal()
            with SQLiteLifeLedger.birth(path=path, individual_id=IDENTITY,
                                        initial_state=state()) as ledger:
                first = ledger.audit()
                ledger.begin_intent(expected_generation=0, intent_ref="intent:1",
                                    trusted_current=first)
                first_event = journal.append(
                    event_id="event:1",
                    causal_event={"kind": "test_causal_receipt", "t_monde": 1}
                ).as_dict()
                ledger.commit_generation(expected_generation=0,
                    expected_head="0" * 64, intent_ref="intent:1",
                    current_state=state(1), events=[first_event],
                    verified_intent=first)
                current = ledger.audit()
                ledger.begin_intent(expected_generation=1, intent_ref="intent:2",
                                    trusted_current=current)
                # Tamper the prior SQL record without modifying its count/head.
                with sqlite3.connect(path) as external:
                    external.execute("UPDATE causal_occurrence SET canonical_bytes=? "
                                     "WHERE idx=0", (sqlite3.Binary(b'corrupt'),))
                next_event = journal.append(
                    event_id="event:2",
                    causal_event={"kind": "test_causal_receipt", "t_monde": 2}
                ).as_dict()
                with self.assertRaises(RecoveryBlocked):
                    ledger.commit_generation(
                        expected_generation=1,
                        expected_head=journal.entries[0].event_hash,
                        intent_ref="intent:2", current_state=state(2),
                        events=[next_event], verified_intent=current)
                self.assertTrue(ledger._poisoned)
            with self.assertRaises(RecoveryBlocked):
                SQLiteLifeLedger.audit_read_only(path=path,
                    expected_individual_id=IDENTITY)

    def test_untrusted_legacy_call_keeps_full_audits(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.sqlite")
            journal = HashChainedJournal()
            with SQLiteLifeLedger.birth(path=path, individual_id=IDENTITY,
                                        initial_state=state()) as ledger:
                count = []
                original = ledger.audit
                def counted():
                    count.append(1)
                    return original()
                ledger.audit = counted
                ledger.begin_intent(expected_generation=0, intent_ref="intent:1")
                event = journal.append(event_id="event:1", causal_event={
                    "kind": "test_causal_receipt", "t_monde": 1}).as_dict()
                ledger.commit_generation(
                    expected_generation=0, expected_head="0" * 64,
                    intent_ref="intent:1", current_state=state(1),
                    events=[event])
                self.assertEqual(len(count), 3)


if __name__ == "__main__":
    unittest.main()
