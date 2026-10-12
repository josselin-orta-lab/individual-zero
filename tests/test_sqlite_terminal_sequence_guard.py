"""M-19: a hash-valid SQLite sequence must still respect irreversible death.

These are storage/auditor software tests, not physical or scientific M-11 proof.
"""
from __future__ import annotations

from copy import deepcopy
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.journal import GENESIS_HASH
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


IDENTITY = "i0:terminal-sequence-regression"


def state(step=0):
    return {
        "individual_id": IDENTITY,
        "world": {"physical_step": step},
        "scheduler": {"t_monde": step},
        "owners": {"metacognition_health": {"cycle": step}},
    }


def death():
    return {
        "kind": "individual_death_confirmed",
        "t_monde": 1,
        "attempt_ref": "attempt:1",
    }


def closure():
    return {
        "kind": "step_closed",
        "t_monde": 1,
        "attempt_ref": "attempt:1",
        "data": {
            "outcome": "dead",
            "applied_command_count": 1,
            "world_advance_count": 1,
        },
    }


def records(events):
    """Construct a completely canonical, hash-consistent arbitrary event list.

    Deliberately do not append using HashChainedJournal: the test must reach
    the SQLite validator even with a forged but cryptographically valid suffix.
    """
    previous = GENESIS_HASH
    rows = []
    for index, causal in enumerate(events):
        event_id = "event:" + str(index)
        digest = sha256_hex(bytes.fromhex(previous) + canonical_causal_bytes({
            "event_id": event_id, "causal_event": causal,
        }))
        rows.append({
            "index": index, "event_id": event_id,
            "previous_hash": previous, "event_hash": digest,
            "causal_event": causal,
        })
        previous = digest
    return rows


class SQLiteTerminalSequenceGuardTests(unittest.TestCase):
    def test_valid_terminal_suffix_is_committed_and_auditable(self):
        with TemporaryDirectory() as temp:
            path = str(Path(temp) / "life.db")
            rows = records([
                {"kind": "world_transition_experienced", "t_monde": 1},
                death(), closure(),
            ])
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=state(),
            ) as store:
                store.begin_intent(expected_generation=0, intent_ref="step:1")
                receipt = store.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="step:1", current_state=state(1),
                    events=rows, status="dead",
                )
                self.assertEqual(receipt.journal_count, 3)
                self.assertEqual(receipt.status, "dead")
            self.assertEqual(SQLiteLifeLedger.audit_read_only(
                path=path, expected_individual_id=IDENTITY,
            ).status, "dead")

    def test_invalid_terminal_suffixes_are_rejected_atomically(self):
        mismatched_attempt = closure()
        mismatched_attempt["attempt_ref"] = "attempt:other"
        mismatched_time = closure()
        mismatched_time["t_monde"] = 2
        bad_count = closure()
        bad_count["data"]["applied_command_count"] = 0
        boolean_count = closure()
        boolean_count["data"]["world_advance_count"] = True
        invalid_death_time = death()
        invalid_death_time["t_monde"] = 0
        invalid_death_attempt = death()
        invalid_death_attempt["attempt_ref"] = ""
        bad_outcome = closure()
        bad_outcome["data"]["outcome"] = "normal"
        intervening = {"kind": "memory_updated", "t_monde": 1}
        cases = {
            "postdeath_cognition": ([death(), closure(), intervening], "dead"),
            "postdeath_technical": ([death(), closure(), {"kind": "operator_receipt"}], "dead"),
            "second_terminal_closure": ([death(), closure(), closure()], "dead"),
            "reversed_death_closure": ([closure(), death()], "dead"),
            "mismatched_attempt": ([death(), mismatched_attempt], "dead"),
            "mismatched_world_time": ([death(), mismatched_time], "dead"),
            "invalid_physical_count": ([death(), bad_count], "dead"),
            "boolean_physical_count": ([death(), boolean_count], "dead"),
            "intervening_cognitive_event": ([death(), intervening, closure()], "dead"),
            "death_without_closure": ([death()], "dead"),
            "death_wrong_time": ([invalid_death_time, closure()], "dead"),
            "death_missing_attempt": ([invalid_death_attempt, closure()], "dead"),
            "nonfatal_closure": ([death(), bad_outcome], "dead"),
            "unpaired_fatal_closure": ([closure()], "active"),
            "unpaired_fatal_with_dead_status": ([closure()], "dead"),
            "dead_status_without_death": ([{"kind": "step_closed", "data": {"outcome": "normal"}}], "dead"),
            "active_status_with_death": ([death(), closure()], "active"),
            "halt_status_with_death": ([death(), closure()], "technical_halt"),
        }
        for name, (events, status) in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as temp:
                path = str(Path(temp) / "life.db")
                with SQLiteLifeLedger.birth(
                    path=path, individual_id=IDENTITY, initial_state=state(),
                ) as store:
                    store.begin_intent(expected_generation=0, intent_ref="step:1")
                    with self.assertRaises((ValueError, RecoveryBlocked)):
                        store.commit_generation(
                            expected_generation=0, expected_head=GENESIS_HASH,
                            intent_ref="step:1", current_state=state(1),
                            events=records(deepcopy(events)), status=status,
                        )
                # A rejected generation must neither append events nor
                # resurrect the previously active generation after an intent.
                receipt = SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )
                self.assertEqual(receipt.generation, 0)
                self.assertEqual(receipt.journal_count, 0)
                self.assertTrue(receipt.pending_intent)
                self.assertFalse(receipt.may_recover)

    def test_readonly_audit_rejects_rehashed_postmortem_occurrence(self):
        with TemporaryDirectory() as temp:
            path = str(Path(temp) / "life.db")
            rows = records([death(), closure()])
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=state(),
            ) as store:
                store.begin_intent(expected_generation=0, intent_ref="step:1")
                store.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="step:1", current_state=state(1),
                    events=rows, status="dead",
                )
            # A person with direct DB write access can recompute the hashes,
            # so mere canonicality+chain verification must not grant PASS.
            forged = records([death(), closure(), {
                "kind": "memory_updated", "t_monde": 1, "attempt_ref": "attempt:1",
            }])[-1]
            with sqlite3.connect(path) as db:
                db.execute(
                    "INSERT INTO causal_occurrence "
                    "(idx, event_id, previous_hash, event_hash, canonical_bytes) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (forged["index"], forged["event_id"], forged["previous_hash"],
                     forged["event_hash"], canonical_causal_bytes(forged)),
                )
                db.execute(
                    "UPDATE life_current SET journal_count=?, journal_head=? WHERE slot=1",
                    (3, forged["event_hash"]),
                )
            with self.assertRaisesRegex(RecoveryBlocked, "terminal|death"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )
            with self.assertRaises(RecoveryBlocked):
                SQLiteLifeLedger.open_existing(
                    path=path, expected_individual_id=IDENTITY,
                )

    def test_readonly_audit_rejects_rehashed_mismatched_terminal_closure(self):
        with TemporaryDirectory() as temp:
            path = str(Path(temp) / "life.db")
            original = records([death(), closure()])
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=state(),
            ) as store:
                store.begin_intent(expected_generation=0, intent_ref="step:1")
                store.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="step:1", current_state=state(1),
                    events=original, status="dead",
                )
            bad = closure()
            bad["attempt_ref"] = "attempt:wrong"
            forged = records([death(), bad])[-1]
            with sqlite3.connect(path) as db:
                db.execute(
                    "UPDATE causal_occurrence SET event_hash=?, canonical_bytes=? WHERE idx=1",
                    (forged["event_hash"], canonical_causal_bytes(forged)),
                )
                db.execute(
                    "UPDATE life_current SET journal_head=? WHERE slot=1",
                    (forged["event_hash"],),
                )
            with self.assertRaisesRegex(RecoveryBlocked, "terminal|death"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )


if __name__ == "__main__":
    unittest.main()
