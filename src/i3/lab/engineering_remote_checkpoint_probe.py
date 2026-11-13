"""R2.4 test-only, exact-state checkpoint equality: NOT an off-host M11 anchor.

A caller must retain the returned public checksum/record independently.  It
does not authenticate itself; if an attacker controls checkpoint and SQLite
together, rollback is still accepted. No production CAS fast path is added.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

from i3.lab.engineering_remote_authority import AuthorityStore, DB_SCHEMA
from i3.runtime.engineering_remote_witness import canonical

SCHEMA = "i3-remote-cas-checkpoint-probe/v1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX32 = re.compile(r"[0-9a-f]{32}\Z")
_KEYS = frozenset({
    "schema", "store_schema", "authority_id", "audit_ordinal",
    "audit_head_sha256", "histories_sha256", "request_nonces_sha256",
    "request_nonce_count", "checkpoint_sha256",
})


def _digest(value) -> str:
    return sha256(canonical(value)).hexdigest()


def _checked_checkpoint(checkpoint: dict, authority_id: str) -> None:
    if type(checkpoint) is not dict or set(checkpoint) != _KEYS:
        raise PermissionError("checkpoint has incorrect shape")
    if (checkpoint["schema"] != SCHEMA
            or checkpoint["store_schema"] != DB_SCHEMA
            or type(checkpoint["authority_id"]) is not str
            or checkpoint["authority_id"] != authority_id
            or type(checkpoint["audit_ordinal"]) is not int
            or checkpoint["audit_ordinal"] < 1
            or type(checkpoint["request_nonce_count"]) is not int
            or checkpoint["request_nonce_count"] < 1
            or any(type(checkpoint[k]) is not str
                   or HEX64.fullmatch(checkpoint[k]) is None
                   for k in ("audit_head_sha256", "histories_sha256",
                             "request_nonces_sha256", "checkpoint_sha256"))):
        raise PermissionError("checkpoint fields are invalid")
    payload = {key: value for key, value in checkpoint.items()
               if key != "checkpoint_sha256"}
    if _digest(payload) != checkpoint["checkpoint_sha256"]:
        raise PermissionError("checkpoint checksum mismatch")


def capture_exact_checkpoint(database: Path, authority_id: str, *,
                             expected_source_sha256: str | None = None,
                             expected_open_identity_sha256: str | None = None) -> dict:
    """Fully re-audit a *stable COMMITTED* local DB and seal a public digest.

    This call is O(audit events + accepted nonces), has no speed advantage and
    cannot attest that the caller protects the record independently.
    """
    if (expected_source_sha256 is not None
            and (type(expected_source_sha256) is not str
                 or HEX64.fullmatch(expected_source_sha256) is None)):
        raise PermissionError("expected source must be exact lowercase SHA256")
    if (expected_open_identity_sha256 is not None
            and (type(expected_open_identity_sha256) is not str
                 or HEX64.fullmatch(expected_open_identity_sha256) is None)):
        raise PermissionError("expected open identity must be lowercase SHA256")
    path = Path(database)
    if not path.is_file() or path.is_symlink():
        raise PermissionError("existing regular v3 authority required")
    # One consistent audited read snapshot, without creating the store,
    # changing its journaling policy or acquiring a writer transaction.
    with AuthorityStore.open_existing_verified_readonly(path, authority_id) as conn:
        try:
            histories = conn.execute(
                "SELECT identity,claim_json,horizon,sequence,head,phase,"
                "terminal,pending_seq,pending_intent FROM histories "
                "ORDER BY identity"
            ).fetchall()
            if not histories:
                raise PermissionError("cannot checkpoint empty authority")
            if expected_source_sha256 is not None:
                # Audit validation already checked canonical full birth claims;
                # this additional read remains inside that SAME snapshot.
                try:
                    sources = [json.loads(row[1])["source_sha256"]
                               for row in histories]
                except (TypeError, ValueError, KeyError) as exc:
                    raise PermissionError("bad source in audited claim") from exc
                if any(src != expected_source_sha256 for src in sources):
                    raise PermissionError("foreign source in authority checkpoint")
            if expected_open_identity_sha256 is not None:
                candidates = [row for row in histories
                              if row[0] == expected_open_identity_sha256]
                if (len(candidates) != 1
                        or candidates[0][5] != "COMMITTED"
                        or candidates[0][6] != "OPEN"
                        or candidates[0][7] is not None
                        or candidates[0][8] is not None
                        or candidates[0][3] >= candidates[0][2]):
                    raise PermissionError(
                        "target engineering identity is not open and unambiguous")
            if any(row[5] != "COMMITTED" or row[7] is not None
                   or row[8] is not None for row in histories):
                raise PermissionError("unresolved PREPARED state not checkpointable")
            audit = conn.execute(
                "SELECT ordinal,event_sha256 FROM audit "
                "ORDER BY ordinal DESC LIMIT 1"
            ).fetchone()
            if audit is None or type(audit[0]) is not int:
                raise PermissionError("no committed audit genesis")
            nonces = conn.execute(
                "SELECT nonce,request_sha256 FROM request_nonces ORDER BY nonce"
            ).fetchall()
            if not nonces or any(
                    type(nonce) is not str
                    or HEX32.fullmatch(nonce) is None
                    or type(request_digest) is not str
                    or HEX64.fullmatch(request_digest) is None
                    for nonce, request_digest in nonces):
                raise PermissionError("invalid accepted request-nonce set")
            payload = {
                "schema": SCHEMA,
                "store_schema": DB_SCHEMA,
                "authority_id": authority_id,
                "audit_ordinal": audit[0],
                "audit_head_sha256": audit[1],
                "histories_sha256": _digest(histories),
                "request_nonces_sha256": _digest(nonces),
                "request_nonce_count": len(nonces),
            }
            # The checksum is public and forgeable. It identifies bytes only.
            return dict(payload, checkpoint_sha256=_digest(payload))
        except sqlite3.DatabaseError as exc:
            raise PermissionError("authority checkpoint cannot be read") from exc


def assert_exact_checkpoint(database: Path, authority_id: str,
                            held_checkpoint: dict) -> dict:
    """Require exactly the retained state; no implicit forward or rollback GO."""
    _checked_checkpoint(held_checkpoint, authority_id)
    current = capture_exact_checkpoint(database, authority_id)
    if canonical(current) != canonical(held_checkpoint):
        raise PermissionError("authority differs from retained checkpoint")
    return current


__all__ = ["SCHEMA", "capture_exact_checkpoint", "assert_exact_checkpoint"]
