"""Test-only R2.5 checkpoint publication with serialized local SQLite CAS.

This is NOT independently administered M11: two local SQLite files and an
externally injected test signer can be rolled back together. No server, network
transport, private-key deployment, motor, World, or scientific owner is here.
"""
from __future__ import annotations

import base64
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import re
import sqlite3

from i3.lab.engineering_remote_checkpoint_probe import capture_exact_checkpoint
from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    DOMAIN, SCHEMA, assert_signed_checkpoint_transition,
    verify_signed_checkpoint_receipt,
)
from i3.runtime.engineering_remote_witness import canonical

DB_SCHEMA = "i3-test-only-checkpoint-publisher/v1"
APP_ID = 0x49335035
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_KEY = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_OBJECTS = {("table", "metadata"), ("table", "publications")}


def _valid_hash(v):
    return type(v) is str and _HASH.fullmatch(v) is not None


def _monotone(new, old):
    a, b = new["checkpoint"], old["checkpoint"]
    return (
        new["publication_index"] == old["publication_index"] + 1
        and a["audit_ordinal"] >= b["audit_ordinal"]
        and a["request_nonce_count"] >= b["request_nonce_count"]
        and (a["audit_ordinal"] > b["audit_ordinal"]
             or a["request_nonce_count"] > b["request_nonce_count"])
        and a["checkpoint_sha256"] != b["checkpoint_sha256"]
    )


class TestOnlyCheckpointPublisher:
    """Local reference publication journal for *synthetic* engineering states.

    The signing callable is supplied by a unit test; a real signer and
    independently protected high-water must be designed and attested later.
    """

    def __init__(self, publication_db: Path, authority_db: Path, *,
                 authority_id: str, source_sha256: str, key_id: str,
                 trusted_public_key: bytes, sign):
        self.publication_db = Path(publication_db)
        self.authority_db = Path(authority_db)
        self.authority_id = authority_id
        self.source_sha256 = source_sha256
        self.key_id = key_id
        self.public_key = trusted_public_key
        self.sign = sign
        if (not _valid_hash(authority_id)
                or not _valid_hash(source_sha256)
                or type(key_id) is not str or _KEY.fullmatch(key_id) is None
                or type(trusted_public_key) is not bytes
                or len(trusted_public_key) != 32
                or not callable(sign)):
            raise PermissionError("test publisher needs explicit pinned identity and signer")
        if (self.publication_db.resolve() == self.authority_db.resolve()
                or self.publication_db.is_symlink()
                or self.publication_db.parent.is_symlink()
                or not self.publication_db.parent.is_dir()
                or (self.publication_db.exists()
                    and not self.publication_db.is_file())
                or self.authority_db.is_symlink()
                or self.authority_db.parent.is_symlink()
                or not self.authority_db.is_file()):
            raise PermissionError("two distinct regular existing/owned database paths required")
        with closing(sqlite3.connect(self.publication_db,
                                     isolation_level=None, timeout=5)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                app_id = conn.execute("PRAGMA application_id").fetchone()[0]
                objects = set(conn.execute(
                    "SELECT type,name FROM sqlite_master "
                    "WHERE name NOT LIKE 'sqlite_%'").fetchall())
                if app_id == 0 and not objects:
                    conn.execute(f"PRAGMA application_id={APP_ID}")
                    conn.execute(
                        "CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK(id=1),"
                        "schema TEXT NOT NULL, authority_id TEXT NOT NULL,"
                        "source_sha256 TEXT NOT NULL, key_id TEXT NOT NULL,"
                        "public_key_sha256 TEXT NOT NULL)")
                    conn.execute("INSERT INTO metadata VALUES (1,?,?,?,?,?)",
                                 self._metadata())
                    conn.execute(
                        "CREATE TABLE publications ("
                        "idx INTEGER PRIMARY KEY, raw BLOB NOT NULL,"
                        "receipt_sha256 TEXT NOT NULL)")
                self._walk(conn)
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise

    def _metadata(self):
        return (DB_SCHEMA, self.authority_id, self.source_sha256,
                self.key_id, sha256(self.public_key).hexdigest())

    def _pins(self):
        return {
            "trusted_public_key": self.public_key,
            "expected_authority_id": self.authority_id,
            "expected_source_sha256": self.source_sha256,
            "expected_key_id": self.key_id,
        }

    def _walk(self, conn) -> bytes | None:
        """Full source/receipt chain check: deliberate O(n) safety baseline."""
        app_id = conn.execute("PRAGMA application_id").fetchone()[0]
        objects = set(conn.execute(
            "SELECT type,name FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%'").fetchall())
        metadata = conn.execute(
            "SELECT schema,authority_id,source_sha256,key_id,"
            "public_key_sha256 FROM metadata WHERE id=1").fetchall() \
            if ("table", "metadata") in objects else []
        if app_id != APP_ID or objects != _OBJECTS or metadata != [self._metadata()]:
            raise PermissionError("foreign or modified checkpoint publisher database")
        previous_raw = None
        previous_payload = None
        for expected_idx, (idx, raw, digest) in enumerate(conn.execute(
                "SELECT idx,raw,receipt_sha256 FROM publications ORDER BY idx"), 1):
            if (type(idx) is not int or idx != expected_idx
                    or type(raw) is not bytes
                    or not _valid_hash(digest)
                    or sha256(raw).hexdigest() != digest):
                raise PermissionError("publisher receipt journal altered")
            payload = verify_signed_checkpoint_receipt(
                raw, **self._pins())["payload"]
            if payload["publication_index"] != expected_idx:
                raise PermissionError("publisher receipt ordinal mismatch")
            if previous_raw is None:
                if payload["previous_receipt_sha256"] != "0" * 64:
                    raise PermissionError("publisher genesis receipt not anchored")
            elif (payload["previous_receipt_sha256"]
                  != sha256(previous_raw).hexdigest()
                  or not _monotone(payload, previous_payload)):
                raise PermissionError("publisher receipt chain not advancing")
            previous_raw, previous_payload = raw, payload
        return previous_raw

    def latest(self) -> bytes | None:
        """Read and validate one local immutable *logical* publication chain.

        Bytes on disk remain mutable by the same privileged OS principal.
        """
        if not self.publication_db.is_file() or self.publication_db.is_symlink():
            raise PermissionError("publisher database absent or replaced")
        try:
            with closing(sqlite3.connect(
                    self.publication_db.absolute().as_uri() + "?mode=ro",
                    uri=True, isolation_level=None, timeout=5)) as conn:
                conn.execute("PRAGMA query_only=ON")
                conn.execute("BEGIN")
                try:
                    return self._walk(conn)
                finally:
                    conn.execute("ROLLBACK")
        except sqlite3.DatabaseError as exc:
            raise PermissionError("publisher read failed closed") from exc

    def publish(self, expected_previous_receipt_sha256: str) -> bytes:
        """Serialize, sign, verify and commit a single checkpoint publication.

        The caller-provided expected hash is NOT protected here. The provider
        cannot recover from an ambiguous signed/committed result by retrying
        a motor; it can only re-read latest and STOP/reconcile externally.
        """
        if not _valid_hash(expected_previous_receipt_sha256):
            raise PermissionError("exact expected latest receipt digest required")
        with closing(sqlite3.connect(self.publication_db,
                                     isolation_level=None, timeout=5)) as conn:
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                previous_raw = self._walk(conn)
                old_hash = ("0" * 64 if previous_raw is None
                            else sha256(previous_raw).hexdigest())
                if old_hash != expected_previous_receipt_sha256:
                    raise PermissionError("stale publisher predecessor: no retry")
                old_idx = (0 if previous_raw is None else
                           verify_signed_checkpoint_receipt(
                               previous_raw, **self._pins())[
                               "payload"]["publication_index"])
                if old_idx >= 2**63 - 1:
                    raise PermissionError("publication index exhausted")
                # The pinning check MUST be in the SAME full-audit read
                # snapshot as checkpoint capture. It verifies only local
                # source-claim consistency, never actual source authenticity.
                point = capture_exact_checkpoint(
                    self.authority_db, self.authority_id,
                    expected_source_sha256=self.source_sha256)
                payload = {
                    "authority_id": self.authority_id,
                    "source_sha256": self.source_sha256,
                    "key_id": self.key_id,
                    "publication_index": old_idx + 1,
                    "previous_receipt_sha256": old_hash,
                    "checkpoint": point,
                }
                message = DOMAIN + canonical({
                    "schema": SCHEMA, "payload": payload})
                signature = self.sign(message)
                if type(signature) is not bytes or len(signature) != 64:
                    raise PermissionError("invalid test signer response")
                raw = canonical({
                    "schema": SCHEMA, "payload": payload,
                    "signature": {
                        "algorithm": "Ed25519", "key_id": self.key_id,
                        "value": base64.b64encode(signature).decode("ascii"),
                    },
                })
                # Enforce that the signer actually matches the pinned key.
                # Rechecking the audited DB may fail closed if a concurrent
                # authority writer moved it after the first capture.
                assert_signed_checkpoint_transition(
                    self.authority_db, raw,
                    retained_latest_raw=previous_raw, **self._pins())
                conn.execute("INSERT INTO publications VALUES (?,?,?)",
                             (old_idx+1, raw, sha256(raw).hexdigest()))
                conn.execute("COMMIT")
                return raw
            except BaseException:
                conn.execute("ROLLBACK")
                raise


__all__ = ["TestOnlyCheckpointPublisher", "DB_SCHEMA"]
