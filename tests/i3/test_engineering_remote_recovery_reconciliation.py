"""No-World R2.6 required signed witness reconciliation: STOP unless exact match.

External callback is a *test fixture* and not an independent M11 operator.
Rolling it back together with both SQLite stores must remain ACCEPT negative.
"""
from contextlib import closing
from hashlib import sha256
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_publisher import (
    TestOnlyCheckpointPublisher as Publisher,
)
from i3.lab.engineering_remote_recovery_reconciliation import (
    SCHEMA, reconcile_required_witness,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA as REQUEST_SCHEMA, claim_data,
)


class RequiredWitnessRecoveryTests(unittest.TestCase):
    AUTHORITY = "d"*64
    SOURCE = "a"*64
    KEY_ID = "r26-test-issuer"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.auth_path = root/"authority.sqlite3"
        self.pub_path = root/"publisher.sqlite3"
        self.auth = AuthorityStore(self.auth_path, self.AUTHORITY)
        self.signer = Ed25519PrivateKey.generate()
        self.public = self.signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        self.pub = Publisher(
            self.pub_path, self.auth_path, authority_id=self.AUTHORITY,
            source_sha256=self.SOURCE, key_id=self.KEY_ID,
            trusted_public_key=self.public, sign=self.signer.sign)
        self.claim = claim_data(make_reservation(
            birth_index=301, life_seed=7719, source_sha256=self.SOURCE,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.nonce = 0

    def send(self, op, *, claim=None, **extra):
        self.nonce += 1
        return self.auth.apply({
            "schema": REQUEST_SCHEMA, "authority_id": self.AUTHORITY,
            "operation": op, "claim": self.claim if claim is None else claim,
            **extra,
        }, request_nonce=f"{self.nonce:032x}")

    def genesis(self, *, horizon=2):
        self.send("register", horizon=horizon, head_sha256="0"*64)
        return self.pub.publish("0"*64)

    def next_receipt(self, prior):
        self.send("verify")
        return self.pub.publish(sha256(prior).hexdigest())

    def check(self, raw=None, *, latest=None, identity=None, **overrides):
        if latest is None:
            latest = (lambda: raw)
        args = dict(
            authority_db=self.auth_path, publication_db=self.pub_path,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.KEY_ID, trusted_public_key=self.public,
            target_identity_sha256=(
                self.claim["identity_sha256"] if identity is None else identity),
            fetch_required_latest=latest,
        )
        args.update(overrides)
        return reconcile_required_witness(**args)

    def backup(self, path, label):
        dest = path.with_name(path.stem + "." + label + ".sqlite3")
        with closing(sqlite3.connect(path)) as source:
            with closing(sqlite3.connect(dest)) as target:
                source.backup(target)
        return dest

    def restore(self, path, backup):
        os.replace(backup, path)
        for ext in ("-wal", "-shm"):
            sidecar = Path(str(path) + ext)
            if sidecar.exists():
                sidecar.unlink()

    def test_external_signed_highwater_exact_match_is_observation_only(self):
        first = self.genesis()
        with (patch.object(AuthorityStore, "__init__",
                           side_effect=AssertionError("writer constructor forbidden")),
              patch.object(Publisher, "__init__",
                           side_effect=AssertionError("publisher writer forbidden")),
              patch("i3.modules.world.World.__init__",
                    side_effect=AssertionError("World forbidden"))):
            result = self.check(first)
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["result"], "READ_ONLY_MATCH_NO_MOTOR_AUTHORITY")
        self.assertEqual(result["publication_index"], 1)
        self.assertEqual(result["target_identity_sha256"],
                         self.claim["identity_sha256"])
        self.assertFalse(result["motor_authority"])
        self.assertFalse(result["scientific_world_authorized"])
        self.assertFalse(result["independent_m11_attested"])
        self.assertEqual(result["receipt_sha256"], sha256(first).hexdigest())

    def test_missing_witness_or_connection_failure_never_falls_back_to_local(self):
        first = self.genesis()
        for provider in (None, lambda: None, lambda: "", lambda: b"",
                         lambda: bytearray(first)):
            with self.subTest(provider=repr(provider)):
                with self.assertRaises(PermissionError):
                    self.check(first, latest=provider,
                               **({"fetch_required_latest": None}
                                  if provider is None else {}))
        def timeout():
            raise TimeoutError("synthetic independent witness unavailable")
        with self.assertRaisesRegex(PermissionError, "unavailable"):
            self.check(first, latest=timeout)
        self.assertEqual(self.pub.latest(), first)

    def test_foreign_signed_identity_source_and_key_pins_refused(self):
        first = self.genesis()
        for override in (
            {"trusted_public_key": b"x"*32},
            {"authority_id": "e"*64},
            {"source_sha256": "f"*64},
            {"key_id": "foreign-issuer"},
        ):
            with self.subTest(override=override):
                with self.assertRaises(PermissionError):
                    self.check(first, **override)

    def test_missing_publisher_and_corrupted_signed_journal_refused_readonly(self):
        first = self.genesis()
        with closing(sqlite3.connect(self.pub_path)) as conn:
            with conn:
                modified = conn.execute(
                    "UPDATE publications SET receipt_sha256=? WHERE idx=1",
                    ("f"*64,))
                self.assertEqual(modified.rowcount, 1)
        with self.assertRaises(PermissionError):
            self.check(first)
        self.pub_path.unlink()
        with self.assertRaises(PermissionError):
            self.check(first)
        self.assertFalse(self.pub_path.exists())

    def test_old_authority_under_new_local_publisher_and_witness_denied(self):
        old = self.genesis()
        saved = self.backup(self.auth_path, "old")
        newer = self.next_receipt(old)
        self.restore(self.auth_path, saved)
        with self.assertRaises(PermissionError):
            self.check(newer)
        self.assertEqual(self.pub.latest(), newer)

    def test_old_publisher_under_new_external_tip_denied(self):
        old = self.genesis()
        saved = self.backup(self.pub_path, "old")
        newer = self.next_receipt(old)
        self.restore(self.pub_path, saved)
        with self.assertRaisesRegex(PermissionError, "publisher differs"):
            self.check(newer)
        self.assertNotEqual(newer, old)

    def test_authority_ahead_of_witness_is_stop_not_auto_published(self):
        old = self.genesis()
        self.send("verify")
        with self.assertRaisesRegex(PermissionError, "authority differs"):
            self.check(old)
        self.assertEqual(self.pub.latest(), old)

    def test_old_witness_replayed_under_new_local_publisher_is_rejected(self):
        first = self.genesis()
        newer = self.next_receipt(first)
        with self.assertRaisesRegex(PermissionError, "publisher differs"):
            self.check(first)
        self.assertEqual(self.check(newer)["publication_index"], 2)

    def test_prepared_unknown_and_terminal_life_cannot_be_admitted(self):
        old = self.genesis(horizon=1)
        with self.assertRaisesRegex(PermissionError, "target engineering identity"):
            self.check(old, identity="f"*64)
        self.send("prepare", sequence=1, previous_head_sha256="0"*64,
                  intent_sha256="1"*64)
        with self.assertRaises(PermissionError):
            self.check(old)
        self.send("commit", sequence=1, previous_head_sha256="0"*64,
                  intent_sha256="1"*64, head_sha256="2"*64,
                  terminal="CENSORED")
        terminal_receipt = self.pub.publish(sha256(old).hexdigest())
        with self.assertRaisesRegex(PermissionError, "target engineering identity"):
            self.check(terminal_receipt)

    def test_second_foreign_source_in_audited_authority_is_rejected(self):
        first = self.genesis()
        foreign = claim_data(make_reservation(
            birth_index=302, life_seed=9, source_sha256="e"*64,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.send("register", claim=foreign, horizon=2,
                  head_sha256="0"*64)
        with self.assertRaisesRegex(PermissionError, "foreign source"):
            self.check(first)

    def test_all_three_domains_rolled_back_accept_old_negative_control(self):
        old = self.genesis()
        old_authority = self.backup(self.auth_path, "before")
        old_publisher = self.backup(self.pub_path, "before")
        latest = self.next_receipt(old)
        self.assertEqual(self.check(latest)["publication_index"], 2)
        self.restore(self.auth_path, old_authority)
        self.restore(self.pub_path, old_publisher)
        # A fake/co-rollbackable "external" provider can replay old bytes.
        # This deliberate software ACCEPT demonstrates FAIL_INDEPENDENT_M11.
        restored = self.check(old)
        self.assertEqual(restored["publication_index"], 1)
        self.assertFalse(restored["independent_m11_attested"])


if __name__ == "__main__":
    unittest.main()
