"""Adversarial no-World Ed25519 receipt and retained-high-water tests.

Private keys are generated in this test process only. These fixtures do NOT
attest independently operated signers, hosts, storage, source or physical life.
"""
import base64
from contextlib import closing
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_probe import capture_exact_checkpoint
from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    SCHEMA, DOMAIN, assert_signed_checkpoint_transition,
    verify_signed_checkpoint_receipt,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA as REQUEST_SCHEMA, canonical, claim_data,
)


class SignedCheckpointReceiptTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    SOURCE = "a" * 64
    KEY_ID = "test-issuer-1"
    HEAD = "0" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "authority.sqlite3"
        self.store = AuthorityStore(self.path, self.AUTHORITY)
        self.claim = claim_data(make_reservation(
            birth_index=81, life_seed=7719, source_sha256=self.SOURCE,
            world_sha256="b" * 64, genome_sha256="c" * 64))
        self.counter = 0
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)

    def send(self, operation, **fields):
        self.counter += 1
        return self.store.apply({
            "schema": REQUEST_SCHEMA, "authority_id": self.AUTHORITY,
            "operation": operation, "claim": self.claim, **fields,
        }, request_nonce=f"{self.counter:032x}")

    def register(self):
        self.send("register", horizon=3, head_sha256=self.HEAD)

    def pins(self, **override):
        return dict({
            "trusted_public_key": self.public,
            "expected_authority_id": self.AUTHORITY,
            "expected_source_sha256": self.SOURCE,
            "expected_key_id": self.KEY_ID,
        }, **override)

    def sign(self, checkpoint, *, index=1, previous=None, key=None,
             source=None, authority=None, key_id=None, payload_change=None):
        payload = {
            "authority_id": authority or self.AUTHORITY,
            "source_sha256": source or self.SOURCE,
            "key_id": key_id or self.KEY_ID,
            "publication_index": index,
            "previous_receipt_sha256": ("0" * 64 if previous is None
                                       else sha256(previous).hexdigest()),
            "checkpoint": deepcopy(checkpoint),
        }
        if payload_change:
            payload.update(payload_change)
        unsigned = {"schema": SCHEMA, "payload": payload}
        signer = self.private if key is None else key
        signature = base64.b64encode(
            signer.sign(DOMAIN + canonical(unsigned))).decode("ascii")
        return canonical(dict(unsigned, signature={
            "algorithm": "Ed25519", "key_id": payload["key_id"],
            "value": signature,
        }))

    def checkpoint(self):
        return capture_exact_checkpoint(self.path, self.AUTHORITY)

    def accept(self, raw, *, prior=None, **pins_override):
        return assert_signed_checkpoint_transition(
            self.path, raw, retained_latest_raw=prior,
            **self.pins(**pins_override))

    def snapshot_db(self, name="old.sqlite3"):
        backup = self.path.parent / name
        with closing(sqlite3.connect(self.path)) as source:
            with closing(sqlite3.connect(backup)) as dest:
                source.backup(dest)
        return backup

    def restore_db(self, old):
        os.replace(old, self.path)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(self.path) + suffix)
            if sidecar.exists():
                sidecar.unlink()
        self.store = AuthorityStore(self.path, self.AUTHORITY)

    def test_pinned_ed25519_genesis_valid_but_not_independent_m11(self):
        self.register()
        signed = self.sign(self.checkpoint())
        got = verify_signed_checkpoint_receipt(signed, **self.pins())
        self.assertEqual(got["payload"]["publication_index"], 1)
        self.assertEqual(self.accept(signed), got)
        self.assertEqual(got["payload"]["source_sha256"], self.SOURCE)

    def test_fresh_signed_verify_only_publication_advances_nonce_counter(self):
        self.register()
        old = self.sign(self.checkpoint())
        self.assertEqual(self.accept(old)["payload"]["publication_index"], 1)
        self.send("verify")
        new = self.sign(self.checkpoint(), index=2, previous=old)
        self.assertEqual(self.accept(new, prior=old)["payload"][
            "checkpoint"]["request_nonce_count"], 2)
        with self.assertRaises(PermissionError):
            self.accept(old, prior=new)
        with self.assertRaises(PermissionError):
            self.accept(new, prior=new)

    def test_wrong_pinned_public_key_issuer_source_or_authority_rejected(self):
        self.register()
        checkpoint = self.checkpoint()
        valid = self.sign(checkpoint)
        foreign = Ed25519PrivateKey.generate()
        other_public = foreign.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaises(PermissionError):
            self.accept(valid, trusted_public_key=other_public)
        with self.assertRaises(PermissionError):
            self.accept(valid, expected_key_id="test-issuer-2")
        with self.assertRaises(PermissionError):
            self.accept(valid, expected_authority_id="e" * 64)
        with self.assertRaises(PermissionError):
            self.accept(valid, expected_source_sha256="f" * 64)
        with self.assertRaises(PermissionError):
            self.accept(self.sign(checkpoint, key=foreign))
        with self.assertRaises(PermissionError):
            self.accept(self.sign(checkpoint, source="f" * 64))
        with self.assertRaises(PermissionError):
            self.accept(self.sign(checkpoint, authority="e" * 64))
        with self.assertRaises(PermissionError):
            self.accept(self.sign(checkpoint, key_id="other-signer"))

    def test_signature_tamper_and_checksum_change_rejected(self):
        self.register()
        valid = self.sign(self.checkpoint())
        data = json.loads(valid)
        data["payload"]["checkpoint"]["audit_ordinal"] += 1
        with self.assertRaises(PermissionError):
            self.accept(canonical(data))
        data = json.loads(valid)
        data["signature"]["value"] = "AA" + data["signature"]["value"][2:]
        with self.assertRaises(PermissionError):
            self.accept(canonical(data))
        data = json.loads(valid)
        data["payload"]["source_sha256"] = "f" * 64
        with self.assertRaises(PermissionError):
            self.accept(canonical(data))

    def test_signed_forks_skipped_index_and_duplicate_checkpoint_refused(self):
        self.register()
        old_checkpoint = self.checkpoint()
        old = self.sign(old_checkpoint)
        self.send("verify")
        fresh = self.checkpoint()
        with self.assertRaisesRegex(PermissionError, "sequence/fork"):
            self.accept(self.sign(fresh, index=3, previous=old), prior=old)
        with self.assertRaisesRegex(PermissionError, "sequence/fork"):
            self.accept(self.sign(fresh, index=1, previous=old), prior=old)
        with self.assertRaisesRegex(PermissionError, "sequence/fork"):
            self.accept(self.sign(fresh, index=2, previous=None), prior=old)
        with self.assertRaisesRegex(PermissionError, "not advancing"):
            self.accept(self.sign(old_checkpoint, index=2, previous=old),
                        prior=old)

    def test_signed_checkpoint_cannot_override_actual_store_state(self):
        self.register()
        old = self.sign(self.checkpoint())
        self.send("verify")
        # Signature is valid, but old exact checkpoint no longer equals live.
        with self.assertRaisesRegex(PermissionError, "differs"):
            self.accept(old)

    def test_signed_receipt_malformed_json_and_bool_index_fail_closed(self):
        self.register()
        valid = self.sign(self.checkpoint())
        for altered in (
            b"{", valid + b"\n",
            b'{"schema":"x","schema":"x"}',
            canonical(dict(json.loads(valid), unexpected=True)),
            self.sign(self.checkpoint(),
                      payload_change={"publication_index": True}),
            self.sign(self.checkpoint(),
                      payload_change={"publication_index": 0}),
            self.sign(self.checkpoint(),
                      payload_change={"previous_receipt_sha256": "X"*64}),
            self.sign(self.checkpoint(),
                      payload_change={"checkpoint": {"malformed": True}}),
        ):
            with self.subTest(wire=altered[:80]):
                with self.assertRaises(PermissionError):
                    self.accept(altered)
        with self.assertRaises(PermissionError):
            self.accept(valid, trusted_public_key=b"x"*31)

    def test_missing_crypto_dependency_fails_closed_without_fallback(self):
        self.register()
        valid = self.sign(self.checkpoint())
        import builtins
        orig = builtins.__import__
        def blocked(name, *args, **kwargs):
            if name.startswith("cryptography"):
                raise ImportError("cryptography unavailable")
            return orig(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=blocked):
            with self.assertRaisesRegex(PermissionError, "verifier missing"):
                self.accept(valid)

    def test_old_authority_and_old_signed_receipt_refused_by_surviving_latest(self):
        self.register()
        old = self.sign(self.checkpoint())
        saved = self.snapshot_db()
        self.send("verify")
        latest = self.sign(self.checkpoint(), index=2, previous=old)
        self.assertEqual(self.accept(latest, prior=old)["payload"][
            "publication_index"], 2)
        self.restore_db(saved)
        # The latest receipt is held in a DIFFERENT trusted rollback domain
        # for this test. It is not itself proof that such a domain exists.
        with self.assertRaises(PermissionError):
            self.accept(old, prior=latest)
        with self.assertRaises(PermissionError):
            self.accept(latest, prior=old)

    def test_complete_rollback_of_db_and_external_pin_remains_negative(self):
        self.register()
        old = self.sign(self.checkpoint())
        saved = self.snapshot_db()
        self.send("verify")
        latest = self.sign(self.checkpoint(), index=2, previous=old)
        self.accept(latest, prior=old)
        self.restore_db(saved)
        # Deliberately accepted if the "external" high-water also disappears.
        # Software PASS of this counterexample == FAIL_INDEPENDENT_M11.
        self.assertEqual(self.accept(old)["payload"]["publication_index"], 1)


if __name__ == "__main__":
    unittest.main()
