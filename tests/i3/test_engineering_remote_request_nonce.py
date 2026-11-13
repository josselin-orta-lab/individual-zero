"""Test-only remote authority request-nonce replay journal, not M11 release.

No Mind, World, motor or scientific birth is constructed by these tests.
Signed HTTP requests use a fixed synthetic HMAC key on 127.0.0.1.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
import hmac
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from i3.lab.engineering_remote_authority import (
    AuthorityStore, DB_SCHEMA, serve_test_loopback,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA, canonical, claim_data,
)


class DurableRequestNonceStoreTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    HEAD = "0" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "authority.sqlite3"
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        self.claim = claim_data(make_reservation(
            birth_index=51, life_seed=7719, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))

    def command(self, op, **fields):
        return {"schema": SCHEMA, "authority_id": self.AUTHORITY,
                "operation": op, "claim": self.claim, **fields}

    def register(self, nonce="1" * 32):
        return self.store.apply(
            self.command("register", horizon=4, head_sha256=self.HEAD),
            request_nonce=nonce)

    def nonce_rows(self):
        with closing(sqlite3.connect(self.db)) as conn:
            return conn.execute(
                "SELECT nonce,request_sha256 FROM request_nonces ORDER BY nonce"
            ).fetchall()

    def test_fresh_registered_and_verified_nonces_are_durable_without_audit_append(self):
        self.register()
        out = self.store.apply(self.command("verify"), request_nonce="2" * 32)
        self.assertEqual(out["sequence"], 0)
        self.assertEqual(len(self.nonce_rows()), 2)
        self.assertEqual(self.nonce_rows()[1][1],
                         sha256(canonical(self.command("verify"))).hexdigest())
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM audit").fetchone()[0], 1)
            self.assertEqual(conn.execute(
                "SELECT schema FROM metadata").fetchone()[0], DB_SCHEMA)
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        with self.assertRaisesRegex(PermissionError, "nonce replay"):
            self.store.apply(self.command("verify"), request_nonce="2" * 32)
        self.assertEqual(self.store.apply(
            self.command("verify"), request_nonce="3" * 32)["sequence"], 0)

    def test_nonce_unique_across_operations_and_identities(self):
        self.register("a" * 32)
        with self.assertRaisesRegex(PermissionError, "nonce replay"):
            self.store.apply(self.command("verify"), request_nonce="a" * 32)
        other = claim_data(make_reservation(
            birth_index=52, life_seed=7719, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))
        foreign_op = dict(self.command("register", horizon=4,
                                       head_sha256=self.HEAD), claim=other)
        with self.assertRaisesRegex(PermissionError, "nonce replay"):
            self.store.apply(foreign_op, request_nonce="a" * 32)
        self.assertEqual(len(self.nonce_rows()), 1)

    def test_refused_cas_rollback_does_not_consume_the_nonce(self):
        invalid = self.command("prepare", sequence=1,
                               previous_head_sha256=self.HEAD,
                               intent_sha256="e" * 64)
        with self.assertRaisesRegex(PermissionError, "unknown or foreign"):
            self.store.apply(invalid, request_nonce="a" * 32)
        self.assertEqual(self.nonce_rows(), [])
        self.register("a" * 32)
        self.assertEqual(len(self.nonce_rows()), 1)
        with self.assertRaisesRegex(PermissionError, "nonce replay"):
            self.register("a" * 32)
        self.assertEqual(len(self.nonce_rows()), 1)

    def test_invalid_nonce_format_denied_before_state_change(self):
        for nonce in (None, True, 12, "", "0" * 31, "F" * 32, "z" * 32):
            with self.subTest(nonce=nonce):
                with self.assertRaisesRegex(PermissionError, "32-hex"):
                    self.store.apply(
                        self.command("register", horizon=4,
                                     head_sha256=self.HEAD),
                        request_nonce=nonce)
        self.assertEqual(self.nonce_rows(), [])

    def test_legacy_v2_authority_never_silently_migrates(self):
        # Emulate the earlier v2 shape: no nonce table, old metadata schema.
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute("UPDATE metadata SET schema=?",
                             ("i3-remote-cas-authority-store/v2",))
                conn.execute("DROP TABLE request_nonces")
        with self.assertRaisesRegex(PermissionError, "foreign or mismatched"):
            AuthorityStore(self.db, self.AUTHORITY)

    def test_whole_authority_database_rollback_reopens_nonce_negative_control(self):
        # Expected security failure: table, audit and state share one rollback
        # domain. A full old snapshot can erase a successfully used nonce.
        self.register()
        old = self.root / "coherent_old.sqlite3"
        with closing(sqlite3.connect(self.db)) as src:
            with closing(sqlite3.connect(old)) as dest:
                src.backup(dest)
        first = self.store.apply(
            self.command("verify"), request_nonce="2" * 32)
        self.assertEqual(first["sequence"], 0)
        with self.assertRaisesRegex(PermissionError, "nonce replay"):
            self.store.apply(
                self.command("verify"), request_nonce="2" * 32)
        os.replace(old, self.db)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(self.db) + suffix)
            if sidecar.exists():
                sidecar.unlink()
        self.store = AuthorityStore(self.db, self.AUTHORITY)
        # Intentionally ACCEPTED again: FAIL_INDEPENDENT_M11, despite a PASS
        # in this software regression that documents the missing guarantee.
        self.assertEqual(self.store.apply(
            self.command("verify"), request_nonce="2" * 32)["sequence"], 0)


class SignedRequestNonceLoopbackTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    HEAD = "0" * 64
    KEY = bytes(range(32))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "server.sqlite3"
        self.claim = claim_data(make_reservation(
            birth_index=71, life_seed=17, source_sha256="a" * 64,
            world_sha256="b" * 64, genome_sha256="c" * 64))
        self.server = None
        self.thread = None
        self.start()
        self.addCleanup(self.stop)

    def start(self):
        self.server = serve_test_loopback(self.db, self.AUTHORITY, self.KEY,
                                          port=0)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.thread.join(timeout=5)
            self.server.server_close()
            self.server = None

    def command(self, operation, **fields):
        return {"schema": SCHEMA, "authority_id": self.AUTHORITY,
                "operation": operation, "claim": self.claim, **fields}

    def send(self, envelope, nonce, key=None):
        body = canonical(envelope)
        secret = self.KEY if key is None else key
        signature = hmac.new(
            secret, b"Q\n" + nonce.encode("ascii") + b"\n" + body,
            sha256).hexdigest()
        req = Request(
            f"http://127.0.0.1:{self.server.server_port}/v1/command",
            data=body, method="POST", headers={
                "Content-Type": "application/json",
                "X-I3-Nonce": nonce,
                "X-I3-Signature": signature,
            })
        try:
            with urlopen(req, timeout=2) as resp:
                resp.read()
                return resp.status
        except HTTPError as exc:
            try:
                return exc.code
            finally:
                exc.close()

    def register(self):
        return self.send(
            self.command("register", horizon=4, head_sha256=self.HEAD),
            "1" * 32)

    def test_same_signed_verify_request_rejected_across_cold_restart(self):
        self.assertEqual(self.register(), 200)
        verify = self.command("verify")
        self.assertEqual(self.send(verify, "2" * 32), 200)
        self.assertEqual(self.send(verify, "2" * 32), 409)
        self.stop()
        self.start()  # New process-equivalent service using retained disk DB
        self.assertEqual(self.send(verify, "2" * 32), 409)
        self.assertEqual(self.send(verify, "3" * 32), 200)

    def test_bad_hmac_does_not_consume_nonce_and_fresh_valid_request_succeeds(self):
        register = self.command("register", horizon=4, head_sha256=self.HEAD)
        self.assertEqual(self.send(register, "b" * 32, key=b"z" * 32), 403)
        self.assertEqual(self.send(register, "b" * 32), 200)
        self.assertEqual(self.send(register, "b" * 32), 409)

    def test_http_cas_failure_does_not_consume_nonce(self):
        failed = self.command("prepare", sequence=1,
                              previous_head_sha256=self.HEAD,
                              intent_sha256="e" * 64)
        self.assertEqual(self.send(failed, "7" * 32), 409)
        register = self.command("register", horizon=4, head_sha256=self.HEAD)
        self.assertEqual(self.send(register, "7" * 32), 200)

    def test_two_concurrent_signed_replays_have_exactly_one_success(self):
        self.assertEqual(self.register(), 200)
        verify = self.command("verify")
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes = list(pool.map(
                lambda _: self.send(verify, "8" * 32), (1, 2)))
        self.assertEqual(sorted(codes), [200, 409])


if __name__ == "__main__":
    unittest.main()
