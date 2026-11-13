"""R2.5 no-World publisher fault controls; never independent M11 attestation."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_publisher import (
    TestOnlyCheckpointPublisher as Publisher,
)
from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    verify_signed_checkpoint_receipt,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import SCHEMA as REQUEST_SCHEMA, claim_data


class PublisherFaultTests(unittest.TestCase):
    AUTHORITY = "d"*64
    SOURCE = "a"*64
    KEY_ID = "test-issuer-r25"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.auth_path = root / "authority.sqlite3"
        self.pub_path = root / "publisher.sqlite3"
        self.auth = AuthorityStore(self.auth_path, self.AUTHORITY)
        self.claim = claim_data(make_reservation(
            birth_index=201, life_seed=19, source_sha256=self.SOURCE,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.count = 0
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        self.publisher = self.make_publisher()

    def make_publisher(self, **changes):
        kwargs = dict(
            publication_db=self.pub_path, authority_db=self.auth_path,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.KEY_ID, trusted_public_key=self.public,
            sign=self.private.sign)
        kwargs.update(changes)
        return Publisher(**kwargs)

    def send(self, op, *, claim=None, **fields):
        self.count += 1
        return self.auth.apply(
            {"schema": REQUEST_SCHEMA, "authority_id": self.AUTHORITY,
             "operation": op, "claim": self.claim if claim is None else claim,
             **fields},
            request_nonce=f"{self.count:032x}")

    def register(self):
        self.send("register", horizon=3, head_sha256="0"*64)

    def decoded(self, raw):
        return verify_signed_checkpoint_receipt(
            raw, trusted_public_key=self.public,
            expected_authority_id=self.AUTHORITY,
            expected_source_sha256=self.SOURCE,
            expected_key_id=self.KEY_ID)["payload"]

    def db_rows(self):
        with closing(sqlite3.connect(self.pub_path)) as conn:
            return conn.execute("SELECT idx FROM publications ORDER BY idx").fetchall()

    def backup(self, path, suffix):
        dest = path.parent / (path.stem + suffix + ".sqlite3")
        with closing(sqlite3.connect(path)) as s:
            with closing(sqlite3.connect(dest)) as d:
                s.backup(d)
        return dest

    def restore(self, original, backup):
        os.replace(backup, original)
        for suffix in ("-wal", "-shm"):
            p = Path(str(original) + suffix)
            if p.exists():
                p.unlink()

    def test_genesis_and_next_nonce_publication_are_durable_and_source_bound(self):
        self.register()
        with patch("i3.modules.world.World.__init__",
                   side_effect=AssertionError("World forbidden")):
            first = self.publisher.publish("0"*64)
            self.assertEqual(self.decoded(first)["publication_index"], 1)
            self.assertEqual(self.publisher.latest(), first)
            self.send("verify")
            second = self.publisher.publish(sha256(first).hexdigest())
        self.assertEqual(self.db_rows(), [(1,), (2,)])
        self.assertEqual(self.decoded(second)["publication_index"], 2)
        self.assertEqual(self.decoded(second)["previous_receipt_sha256"],
                         sha256(first).hexdigest())
        self.assertEqual(self.decoded(second)["checkpoint"][
            "request_nonce_count"], 2)
        self.assertEqual(self.make_publisher().latest(), second)

    def test_competing_publishers_same_predecessor_exactly_one_wins(self):
        self.register()
        first = self.publisher.publish("0"*64)
        self.send("verify")
        expected = sha256(first).hexdigest()
        def attempt(_):
            try:
                self.make_publisher().publish(expected)
                return "accepted"
            except PermissionError:
                return "rejected"
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, range(2)))
        self.assertEqual(sorted(outcomes), ["accepted", "rejected"])
        self.assertEqual(self.db_rows(), [(1,), (2,)])

    def test_lost_ack_can_be_read_after_restart_no_implicit_retry(self):
        self.register()
        first = self.publisher.publish("0"*64)
        self.send("verify")
        delivered = self.publisher.publish(sha256(first).hexdigest())
        # Treat the return value as an ACK lost to the caller.
        recovered = self.make_publisher().latest()
        self.assertEqual(recovered, delivered)
        with self.assertRaisesRegex(PermissionError, "stale publisher predecessor"):
            self.make_publisher().publish(sha256(first).hexdigest())
        self.assertEqual(self.db_rows(), [(1,), (2,)])

    def test_no_publication_without_newly_accepted_authority_state(self):
        self.register()
        first = self.publisher.publish("0"*64)
        with self.assertRaises(PermissionError):
            self.publisher.publish(sha256(first).hexdigest())
        self.assertEqual(self.db_rows(), [(1,)])
        self.send("verify")
        self.assertEqual(self.decoded(self.publisher.publish(
            sha256(first).hexdigest()))["publication_index"], 2)

    def test_failing_signer_and_foreign_signer_roll_back_without_consuming_index(self):
        self.register()
        def fail(_):
            raise RuntimeError("injected signer outage")
        self.publisher.sign = fail
        with self.assertRaisesRegex(RuntimeError, "injected signer outage"):
            self.publisher.publish("0"*64)
        self.assertEqual(self.db_rows(), [])
        foreign = Ed25519PrivateKey.generate()
        self.publisher.sign = foreign.sign
        with self.assertRaises(PermissionError):
            self.publisher.publish("0"*64)
        self.assertEqual(self.db_rows(), [])
        self.publisher.sign = self.private.sign
        self.assertEqual(self.decoded(
            self.publisher.publish("0"*64))["publication_index"], 1)

    def test_pending_cas_and_corrupt_authority_cannot_be_signed(self):
        self.register()
        self.send("prepare", sequence=1, previous_head_sha256="0"*64,
                  intent_sha256="f"*64)
        with self.assertRaisesRegex(PermissionError, "PREPARED"):
            self.publisher.publish("0"*64)
        self.assertEqual(self.db_rows(), [])
        # An attacker modifying a live head but not its full audit is denied.
        with closing(sqlite3.connect(self.auth_path)) as conn:
            with conn:
                conn.execute("UPDATE histories SET head=?", ("e"*64,))
        with self.assertRaises(PermissionError):
            self.publisher.publish("0"*64)
        self.assertEqual(self.db_rows(), [])

    def test_all_claimed_sources_must_match_signature_source(self):
        self.register()
        first = self.publisher.publish("0"*64)
        foreign_claim = claim_data(make_reservation(
            birth_index=202, life_seed=20, source_sha256="f"*64,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.send("register", claim=foreign_claim, horizon=3,
                  head_sha256="0"*64)
        with self.assertRaisesRegex(PermissionError, "foreign source"):
            self.publisher.publish(sha256(first).hexdigest())
        self.assertEqual(self.db_rows(), [(1,)])

    def test_tampered_publication_or_metadata_rejected_after_restart(self):
        self.register()
        self.publisher.publish("0"*64)
        with closing(sqlite3.connect(self.pub_path)) as conn:
            with conn:
                conn.execute("UPDATE publications SET receipt_sha256=? WHERE idx=1",
                             ("f"*64,))
        with self.assertRaises(PermissionError):
            self.make_publisher()
        with self.assertRaises(PermissionError):
            self.publisher.latest()
        with self.assertRaises(PermissionError):
            self.publisher.publish("0"*64)
        self.assertEqual(self.db_rows(), [(1,)])

    def test_same_database_foreign_identity_key_and_missing_authority_denied(self):
        with self.assertRaisesRegex(PermissionError, "distinct"):
            self.make_publisher(publication_db=self.auth_path)
        with self.assertRaises(PermissionError):
            self.make_publisher(source_sha256="f"*64)
        with self.assertRaises(PermissionError):
            self.make_publisher(trusted_public_key=b"x"*32)
        with self.assertRaises(PermissionError):
            self.make_publisher(authority_db=self.pub_path.parent/"missing.db")
        self.assertFalse((self.pub_path.parent/"missing.db").exists())
        self.assertEqual(self.publisher.latest(), None)

    def test_rollback_of_authority_alone_is_refused_under_retained_publisher(self):
        self.register()
        old = self.publisher.publish("0"*64)
        auth_old = self.backup(self.auth_path, ".old")
        self.send("verify")
        new = self.publisher.publish(sha256(old).hexdigest())
        self.restore(self.auth_path, auth_old)
        self.auth = AuthorityStore(self.auth_path, self.AUTHORITY)
        self.assertEqual(self.make_publisher().latest(), new)
        with self.assertRaises(PermissionError):
            self.make_publisher().publish(sha256(new).hexdigest())
        self.assertEqual(self.db_rows(), [(1,), (2,)])

    def test_full_rollback_of_both_stores_accepts_old_state_negative_control(self):
        self.register()
        old = self.publisher.publish("0"*64)
        auth_old = self.backup(self.auth_path, ".before")
        pub_old = self.backup(self.pub_path, ".before")
        self.send("verify")
        new = self.publisher.publish(sha256(old).hexdigest())
        self.assertEqual(self.decoded(new)["publication_index"], 2)
        self.restore(self.auth_path, auth_old)
        self.restore(self.pub_path, pub_old)
        self.auth = AuthorityStore(self.auth_path, self.AUTHORITY)
        restored = self.make_publisher()
        # Intentionally accepted: local store + local publisher + supposed
        # retained high-water share one rollback principal. FAIL_M11.
        self.assertEqual(restored.latest(), old)
        self.send("verify")
        self.assertEqual(self.decoded(restored.publish(
            sha256(old).hexdigest()))["publication_index"], 2)


if __name__ == "__main__":
    unittest.main()
