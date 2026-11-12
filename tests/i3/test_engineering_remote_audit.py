"""No-World R2.4 authority-store audit and full-store-rollback falsifier.

The audit log is physically in the SAME rollbackable SQLite authority file.
Passing these tests never constitutes independent off-host monotonic custody.
"""
from contextlib import closing
from pathlib import Path
import os
import threading
import sqlite3
import tempfile
import unittest

from i3.lab.engineering_remote_authority import (
    AuthorityStore, AUDIT_SCHEMA, DB_SCHEMA, serve_test_loopback,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA, RemoteEngineeringWitness, claim_data,
)
from i3.runtime.engineering_step_ledger import REMOTE_MODE


class RemoteAuthorityAuditTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    GENESIS = "0" * 64
    NEXT_HEAD = "1" * 64
    INTENT = "e" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.db = self.dir / "authority.sqlite3"
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        self.claim = claim_data(make_reservation(
            birth_index=5, life_seed=42, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))

    def envelope(self, operation, **fields):
        return {"schema": SCHEMA, "authority_id": self.AUTHORITY,
                "operation": operation, "claim": self.claim, **fields}

    def register(self):
        return self.store.apply(self.envelope(
            "register", horizon=3, head_sha256=self.GENESIS))

    def prepare(self):
        return self.store.apply(self.envelope(
            "prepare", sequence=1, previous_head_sha256=self.GENESIS,
            intent_sha256=self.INTENT))

    def commit(self, terminal="OPEN"):
        return self.store.apply(self.envelope(
            "commit", sequence=1, previous_head_sha256=self.GENESIS,
            intent_sha256=self.INTENT, head_sha256=self.NEXT_HEAD,
            terminal=terminal))

    def verify(self):
        return self.store.apply(self.envelope("verify"))

    def test_chain_is_append_only_per_actual_cas_transition_and_cold_reopen(self):
        self.register()
        self.prepare()
        self.commit()
        with closing(sqlite3.connect(self.db)) as conn:
            items = conn.execute("SELECT ordinal,event_json FROM audit ORDER BY ordinal").fetchall()
            self.assertEqual([n for n, _ in items], [1, 2, 3])
            for _, event in items:
                self.assertIn(AUDIT_SCHEMA, event)
            self.assertEqual(conn.execute(
                "SELECT schema FROM metadata WHERE id=1").fetchone()[0], DB_SCHEMA)
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        self.assertEqual(self.verify()["sequence"], 1)

    def test_tampered_live_head_is_refused_with_unchanged_audit(self):
        self.register()
        self.prepare()
        self.commit()
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE histories SET head=?", ("f" * 64,))
        with self.assertRaisesRegex(PermissionError, "audit"):
            self.verify()
        with self.assertRaisesRegex(PermissionError, "audit"):
            AuthorityStore(self.db, self.AUTHORITY)

    def test_mutated_event_digest_is_refused_even_when_history_is_valid(self):
        self.register()
        self.prepare()
        self.commit()
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE audit SET event_sha256=? WHERE ordinal=2", ("f" * 64,))
        with self.assertRaisesRegex(PermissionError, "audit"):
            self.verify()

    def test_removed_last_event_is_refused_when_history_retains_head(self):
        self.register()
        self.prepare()
        self.commit()
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("DELETE FROM audit WHERE ordinal=3")
        with self.assertRaisesRegex(PermissionError, "audit"):
            self.verify()

    def test_reordered_or_gapped_audit_sequence_is_refused(self):
        self.register()
        self.prepare()
        self.commit()
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE audit SET ordinal=20 WHERE ordinal=3")
        with self.assertRaisesRegex(PermissionError, "audit"):
            self.verify()

    def test_signed_http_verify_rejects_corrupt_authority_without_ack(self):
        # End-to-end loopback HTTP test: a valid request/key cannot bypass an
        # audit failure to obtain a signed high-water confirmation.
        key = bytes(range(32))
        srv = serve_test_loopback(self.db, self.AUTHORITY, key, port=0)
        thread = threading.Thread(target=srv.serve_forever,
                                  kwargs={"poll_interval": 0.02}, daemon=True)
        thread.start()
        try:
            client = RemoteEngineeringWitness(
                f"http://127.0.0.1:{srv.server_port}", key=key,
                authority_id=self.AUTHORITY, timeout=2,
                allow_test_loopback_http=True)
            claim = self.claim
            ledger = {"witness_mode": REMOTE_MODE, "sequence": 0,
                      "terminal": "OPEN", "prepared": None,
                      "identity_sha256": claim["identity_sha256"],
                      "horizon": 3, "head_sha256": self.GENESIS}
            # Register from the actual signed test client first.
            from i3.runtime.birth_reservation import make_reservation
            born = make_reservation(birth_index=5,life_seed=42,
                source_sha256="a"*64, world_sha256="b"*64, genome_sha256="c"*64)
            client.register(born, ledger)
            self.assertEqual(client.verify(born, ledger)["sequence"], 0)
            with closing(sqlite3.connect(self.db)) as conn:
                with conn:
                    conn.execute("UPDATE histories SET head=?", ("f" * 64,))
            with self.assertRaisesRegex(PermissionError, "unavailable/rejected"):
                client.verify(born, ledger)
        finally:
            srv.shutdown()
            thread.join(timeout=5)
            srv.server_close()

    def test_changed_authority_metadata_fails_before_signed_answer(self):
        self.register()
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE metadata SET authority_id=? WHERE id=1", ("e" * 64,))
        with self.assertRaisesRegex(PermissionError, "authority schema"):
            self.verify()

    def test_interleaved_lives_have_one_global_event_chain(self):
        self.register()
        other = claim_data(make_reservation(
            birth_index=6, life_seed=43, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))
        self.store.apply({"schema": SCHEMA, "authority_id": self.AUTHORITY,
                          "operation": "register", "claim": other,
                          "horizon": 3, "head_sha256": "8" * 64})
        self.prepare()
        self.commit()
        self.assertEqual(self.verify()["sequence"], 1)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0], 4)
        self.assertEqual(self.store.apply({"schema": SCHEMA,
                         "authority_id": self.AUTHORITY,
                         "operation": "verify", "claim": other})["sequence"], 0)

    def test_dead_state_remains_closed_after_cold_reopen(self):
        self.register()
        self.prepare()
        self.commit("DEAD")
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        self.assertEqual(self.verify()["terminal"], "DEAD")
        with self.assertRaisesRegex(PermissionError, "CAS refused"):
            self.store.apply(self.envelope("prepare", sequence=2,
                          previous_head_sha256=self.NEXT_HEAD,
                          intent_sha256=self.INTENT))

    def test_full_authority_db_rollback_still_succeeds_is_not_independent_m11(self):
        # Deliberately demonstrates the precise unresolved R2.4 failure.
        # SQLite backup includes BOTH histories and audit: a shared privileged
        # operator can replace both with a mutually matching older snapshot.
        self.register()
        backup = self.dir / "old.sqlite3"
        with closing(sqlite3.connect(self.db)) as src:
            with closing(sqlite3.connect(backup)) as dst:
                src.backup(dst)
        self.prepare()
        self.commit()
        self.assertEqual(self.verify()["sequence"], 1)
        os.replace(backup, self.db)
        for suffix in ("-wal", "-shm"):
            leftover = self.dir / (self.db.name + suffix)
            if leftover.exists():
                leftover.unlink()
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        self.assertEqual(self.verify()["sequence"], 0,
                         "consistent rollback must stay an explicit NEGATIVE finding")


if __name__ == "__main__":
    unittest.main()
