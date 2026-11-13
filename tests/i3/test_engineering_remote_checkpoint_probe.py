"""Adversarial no-World checkpoint-equality falsifiers for I3 R2.4.

The checkpoint record is NOT a trusted external witness. In particular
restoring it together with the SQLite file must be an accepted negative
control, not a claim of independently anchored M11.
"""
from contextlib import closing
from copy import deepcopy
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_probe import (
    SCHEMA, assert_exact_checkpoint, capture_exact_checkpoint,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import SCHEMA as REQUEST_SCHEMA, claim_data


class ExactCheckpointProbeTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    HEAD0 = "0" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "authority.sqlite3"
        self.store = AuthorityStore(self.path, self.AUTHORITY)
        self.claim = claim_data(make_reservation(
            birth_index=51, life_seed=7719, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))
        self.counter = 0
        self.head = self.HEAD0

    def send(self, op, **fields):
        self.counter += 1
        return self.store.apply(
            {"schema": REQUEST_SCHEMA, "authority_id": self.AUTHORITY,
             "operation": op, "claim": self.claim, **fields},
            request_nonce=f"{self.counter:032x}")

    def register(self):
        result = self.send("register", horizon=2, head_sha256=self.HEAD0)
        self.assertEqual(result["phase"], "COMMITTED")

    def step(self, seq):
        digest = f"{seq + 10:064x}"
        new_head = f"{seq + 20:064x}"
        prepared = self.send("prepare", sequence=seq,
                             previous_head_sha256=self.head,
                             intent_sha256=digest)
        self.assertEqual(prepared["pending_sequence"], seq)
        terminal = "CENSORED" if seq == 2 else "OPEN"
        committed = self.send(
            "commit", sequence=seq, previous_head_sha256=self.head,
            intent_sha256=digest, head_sha256=new_head, terminal=terminal)
        self.assertEqual(committed["sequence"], seq)
        self.head = new_head

    def snapshot_db(self, backup):
        with closing(sqlite3.connect(self.path)) as source:
            with closing(sqlite3.connect(backup)) as target:
                source.backup(target)

    def restore_db(self, backup):
        os.replace(backup, self.path)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(self.path) + suffix)
            if sidecar.exists():
                sidecar.unlink()
        self.store = AuthorityStore(self.path, self.AUTHORITY)

    def test_exact_committed_snapshot_survives_restart_without_mutation(self):
        self.register()
        self.step(1)
        with patch("i3.modules.world.World.__init__",
                   side_effect=AssertionError("World construction forbidden")):
            checkpoint = capture_exact_checkpoint(self.path, self.AUTHORITY)
            self.assertEqual(checkpoint["schema"], SCHEMA)
            self.assertEqual(checkpoint["audit_ordinal"], 3)
            self.assertEqual(checkpoint["request_nonce_count"], 3)
            self.assertEqual(assert_exact_checkpoint(
                self.path, self.AUTHORITY, checkpoint), checkpoint)
            self.store = AuthorityStore(self.path, self.AUTHORITY)
            self.assertEqual(assert_exact_checkpoint(
                self.path, self.AUTHORITY, checkpoint), checkpoint)

    def test_pending_remote_prepared_phase_cannot_be_checkpointed(self):
        self.register()
        self.send("prepare", sequence=1, previous_head_sha256=self.HEAD0,
                  intent_sha256="a" * 64)
        with self.assertRaisesRegex(PermissionError, "PREPARED"):
            capture_exact_checkpoint(self.path, self.AUTHORITY)

    def test_replay_and_forward_commit_are_both_refused_against_stale_checkpoint(self):
        self.register()
        checkpoint = capture_exact_checkpoint(self.path, self.AUTHORITY)
        self.send("verify")
        with self.assertRaisesRegex(PermissionError, "differs"):
            assert_exact_checkpoint(self.path, self.AUTHORITY, checkpoint)
        newest = capture_exact_checkpoint(self.path, self.AUTHORITY)
        self.step(1)
        with self.assertRaisesRegex(PermissionError, "differs"):
            assert_exact_checkpoint(self.path, self.AUTHORITY, newest)
        self.assertEqual(assert_exact_checkpoint(
            self.path, self.AUTHORITY,
            capture_exact_checkpoint(self.path, self.AUTHORITY))["audit_ordinal"], 3)

    def test_unchanged_nonce_count_with_substituted_accepted_nonce_rejected(self):
        self.register()
        checkpoint = capture_exact_checkpoint(self.path, self.AUTHORITY)
        with closing(sqlite3.connect(self.path)) as conn:
            with conn:
                mutated = conn.execute(
                    "UPDATE request_nonces SET nonce=? WHERE nonce=?",
                    ("f" * 32, f"{1:032x}"))
                self.assertEqual(mutated.rowcount, 1, "fault must actually alter stored nonce")
        # The current full audit validates transitions, not nonce membership:
        # equality-checking retained content is necessary in this probe.
        self.assertEqual(capture_exact_checkpoint(
            self.path, self.AUTHORITY)["request_nonce_count"], 1)
        with self.assertRaisesRegex(PermissionError, "differs"):
            assert_exact_checkpoint(self.path, self.AUTHORITY, checkpoint)

    def test_tampered_audit_and_live_head_remain_denied(self):
        self.register()
        pin = capture_exact_checkpoint(self.path, self.AUTHORITY)
        with closing(sqlite3.connect(self.path)) as conn:
            with conn:
                conn.execute("UPDATE audit SET event_sha256=?", ("f"*64,))
        with self.assertRaisesRegex(PermissionError, "audit"):
            assert_exact_checkpoint(self.path, self.AUTHORITY, pin)

    def test_pin_shape_authority_checksum_and_type_are_strict(self):
        self.register()
        pin = capture_exact_checkpoint(self.path, self.AUTHORITY)
        corrupt = []
        bad_key = dict(pin, unauthorized=True)
        corrupt.append(bad_key)
        corrupt.append(dict(pin, audit_ordinal=True))
        corrupt.append(dict(pin, request_nonce_count=False))
        corrupt.append(dict(pin, audit_head_sha256="f" * 63))
        corrupt.append(dict(pin, checkpoint_sha256="f" * 64))
        corrupt.append(dict(pin, authority_id="a" * 64))
        for item in corrupt:
            with self.subTest(item=item):
                with self.assertRaises(PermissionError):
                    assert_exact_checkpoint(self.path, self.AUTHORITY, item)
        # Even a recomputed PUBLIC checksum must not allow a foreign authority.
        with self.assertRaises(PermissionError):
            assert_exact_checkpoint(self.path, "e" * 64, pin)

    def test_missing_authority_is_not_initialized_by_capture(self):
        missing = self.path.parent / "missing.sqlite3"
        with self.assertRaisesRegex(PermissionError, "existing regular"):
            capture_exact_checkpoint(missing, self.AUTHORITY)
        self.assertFalse(missing.exists())

    def test_newer_pin_detects_old_fully_consistent_sqlite_rollback(self):
        self.register()
        self.step(1)
        old = self.path.parent / "authority.old.sqlite3"
        self.snapshot_db(old)
        self.step(2)
        newest = capture_exact_checkpoint(self.path, self.AUTHORITY)
        self.assertEqual(newest["audit_ordinal"], 5)
        self.restore_db(old)
        self.assertEqual(capture_exact_checkpoint(
            self.path, self.AUTHORITY)["audit_ordinal"], 3)
        with self.assertRaisesRegex(PermissionError, "differs"):
            assert_exact_checkpoint(self.path, self.AUTHORITY, newest)

    def test_checkpoint_capture_does_not_invoke_writer_initializer(self):
        self.register()
        self.step(1)
        # The original probe invoked AuthorityStore.__init__, which opens a
        # BEGIN IMMEDIATE write transaction and may change journal mode.
        # Capturing an existing snapshot must work even if that initializer
        # is explicitly forbidden on the inspection path.
        with patch.object(AuthorityStore, "__init__",
                          side_effect=AssertionError("writer initializer called")):
            snapshot = capture_exact_checkpoint(self.path, self.AUTHORITY)
            self.assertEqual(snapshot["audit_ordinal"], 3)
            self.assertEqual(
                assert_exact_checkpoint(self.path, self.AUTHORITY, snapshot),
                snapshot)

    def test_verified_inspection_is_sqlite_readonly_and_cannot_update_head(self):
        self.register()
        before = capture_exact_checkpoint(self.path, self.AUTHORITY)
        with AuthorityStore.open_existing_verified_readonly(
                self.path, self.AUTHORITY) as connection:
            self.assertEqual(connection.execute(
                "PRAGMA query_only").fetchone()[0], 1)
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("UPDATE histories SET head=?", ("f" * 64,))
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute(
                    "INSERT INTO request_nonces VALUES (?,?)",
                    ("e" * 32, "f" * 64))
        self.assertEqual(assert_exact_checkpoint(
            self.path, self.AUTHORITY, before), before)

    def test_verified_readonly_rejects_missing_and_foreign_authority(self):
        missing = self.path.parent / "no_such_authority.sqlite3"
        with self.assertRaises(PermissionError):
            with AuthorityStore.open_existing_verified_readonly(
                    missing, self.AUTHORITY):
                self.fail("missing DB incorrectly admitted")
        self.assertFalse(missing.exists())
        self.register()
        with self.assertRaises(PermissionError):
            with AuthorityStore.open_existing_verified_readonly(
                    self.path, "e" * 64):
                self.fail("foreign authority incorrectly admitted")

    def test_verified_read_transaction_is_consistent_across_concurrent_verify(self):
        self.register()
        with AuthorityStore.open_existing_verified_readonly(
                self.path, self.AUTHORITY) as snapshot:
            before = snapshot.execute(
                "SELECT COUNT(*) FROM request_nonces").fetchone()[0]
            self.assertEqual(before, 1)
            # Writer uses its own SQLite connection while this verified
            # read transaction remains open; no mixed before/after snapshot.
            self.assertEqual(self.send("verify")["phase"], "COMMITTED")
            in_read_tx = snapshot.execute(
                "SELECT COUNT(*) FROM request_nonces").fetchone()[0]
            self.assertEqual(in_read_tx, before)
        with closing(sqlite3.connect(self.path)) as connection:
            after = connection.execute(
                "SELECT COUNT(*) FROM request_nonces").fetchone()[0]
        self.assertEqual(after, 2)
        self.assertEqual(
            capture_exact_checkpoint(self.path, self.AUTHORITY)[
                "request_nonce_count"], 2)

    def test_rollback_both_sqlite_and_pin_is_accepted_negative_control(self):
        self.register()
        self.step(1)
        old_pin = deepcopy(capture_exact_checkpoint(self.path, self.AUTHORITY))
        old_db = self.path.parent / "authority.old.sqlite3"
        self.snapshot_db(old_db)
        self.step(2)
        newer_pin = capture_exact_checkpoint(self.path, self.AUTHORITY)
        self.assertNotEqual(newer_pin["audit_head_sha256"],
                            old_pin["audit_head_sha256"])
        self.restore_db(old_db)
        # Deliberately ACCEPTED: record plus DB are in the SAME adversarial
        # rollback domain. FAIL_INDEPENDENT_M11 is the scientific truth.
        self.assertEqual(
            assert_exact_checkpoint(self.path, self.AUTHORITY, old_pin),
            old_pin)


if __name__ == "__main__":
    unittest.main()
