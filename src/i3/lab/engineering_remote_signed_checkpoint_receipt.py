"""Detached test-only I3 checkpoint verification, NOT independent M11 release.

A signature establishes pinned key possession, not independent custody,
freshness, physical motor truth, or protected monotonic storage. The caller
must retain its latest receipt outside the rollback domain.
No private signing keys are accepted or stored here.
"""
from __future__ import annotations

import base64
from hashlib import sha256
import json
from pathlib import Path
import re

from i3.lab.engineering_remote_checkpoint_probe import (
    _checked_checkpoint, assert_exact_checkpoint,
)
from i3.runtime.engineering_remote_witness import canonical

SCHEMA = "i3-remote-cas-signed-checkpoint-receipt/v1"
DOMAIN = b"I3-R24-SIGNED-CHECKPOINT-RECEIPT/v1\0"
_MAX_BYTES = 8192
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_KEY_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_TOP = {"schema", "payload", "signature"}
_PAYLOAD = {
    "authority_id", "source_sha256", "key_id", "publication_index",
    "previous_receipt_sha256", "checkpoint",
}
_SIGNATURE = {"algorithm", "key_id", "value"}


def _unique_pairs(items):
    out = {}
    for key, val in items:
        if key in out:
            raise ValueError("duplicate JSON key")
        out[key] = val
    return out


def _hex64(v):
    return type(v) is str and _HEX64.fullmatch(v) is not None


def verify_signed_checkpoint_receipt(raw: bytes, *,
                                     trusted_public_key: bytes,
                                     expected_authority_id: str,
                                     expected_source_sha256: str,
                                     expected_key_id: str) -> dict:
    """Authenticate exact canonical envelope against a pinned public key.

    Does not by itself check monotonic sequence or the live SQLite authority.
    """
    if (type(raw) is not bytes or not 0 < len(raw) <= _MAX_BYTES
            or type(trusted_public_key) is not bytes
            or len(trusted_public_key) != 32
            or not _hex64(expected_authority_id)
            or not _hex64(expected_source_sha256)
            or type(expected_key_id) is not str
            or _KEY_ID.fullmatch(expected_key_id) is None):
        raise PermissionError("signed checkpoint inputs invalid")
    try:
        envelope = json.loads(raw, object_pairs_hook=_unique_pairs)
        if (type(envelope) is not dict or set(envelope) != _TOP
                or envelope["schema"] != SCHEMA
                or type(envelope["payload"]) is not dict
                or set(envelope["payload"]) != _PAYLOAD
                or type(envelope["signature"]) is not dict
                or set(envelope["signature"]) != _SIGNATURE
                or canonical(envelope) != raw):
            raise ValueError("noncanonical or malformed signed envelope")
        payload = envelope["payload"]
        signature = envelope["signature"]
        if (payload["authority_id"] != expected_authority_id
                or payload["source_sha256"] != expected_source_sha256
                or payload["key_id"] != expected_key_id
                or type(payload["publication_index"]) is not int
                or not 1 <= payload["publication_index"] <= 2**63-1
                or not _hex64(payload["previous_receipt_sha256"])
                or type(payload["checkpoint"]) is not dict
                or signature["algorithm"] != "Ed25519"
                or signature["key_id"] != expected_key_id
                or type(signature["value"]) is not str):
            raise ValueError("invalid identity or signed payload shape")
        _checked_checkpoint(payload["checkpoint"], expected_authority_id)
        signed = DOMAIN + canonical({"schema": SCHEMA, "payload": payload})
        sig = base64.b64decode(signature["value"], validate=True)
        if (len(sig) != 64 or base64.b64encode(sig).decode("ascii")
                != signature["value"]):
            raise ValueError("invalid Ed25519 signature encoding")
        try:
            from cryptography.exceptions import InvalidSignature
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PublicKey,
            )
        except ImportError as exc:
            raise PermissionError("Ed25519 verifier missing: fail closed") from exc
        try:
            Ed25519PublicKey.from_public_bytes(trusted_public_key).verify(
                sig, signed)
        except (InvalidSignature, ValueError) as exc:
            raise PermissionError("Ed25519 checkpoint signature invalid") from exc
        return envelope
    except (ValueError, TypeError, UnicodeError, KeyError) as exc:
        raise PermissionError("malformed signed checkpoint: fail closed") from exc


def assert_signed_checkpoint_transition(
        database: Path, new_receipt_raw: bytes, *,
        retained_latest_raw: bytes | None, trusted_public_key: bytes,
        expected_authority_id: str, expected_source_sha256: str,
        expected_key_id: str) -> dict:
    """Verify signer, expected monotonic step and exact live audited state.

    The caller MUST retain latest receipt independently. No protected storage,
    network authentication, signing service or independent M11 is supplied.
    """
    pins = {
        "trusted_public_key": trusted_public_key,
        "expected_authority_id": expected_authority_id,
        "expected_source_sha256": expected_source_sha256,
        "expected_key_id": expected_key_id,
    }
    new = verify_signed_checkpoint_receipt(new_receipt_raw, **pins)
    proposed = new["payload"]
    if retained_latest_raw is None:
        if (proposed["publication_index"] != 1
                or proposed["previous_receipt_sha256"] != "0" * 64):
            raise PermissionError("genesis receipt not first publication")
    else:
        prior = verify_signed_checkpoint_receipt(retained_latest_raw, **pins)
        prev = prior["payload"]
        if (proposed["publication_index"] != prev["publication_index"] + 1
                or proposed["previous_receipt_sha256"]
                != sha256(retained_latest_raw).hexdigest()):
            raise PermissionError("signed checkpoint sequence/fork/replay")
        newer = proposed["checkpoint"]
        older = prev["checkpoint"]
        if (newer["audit_ordinal"] < older["audit_ordinal"]
                or newer["request_nonce_count"] < older["request_nonce_count"]
                or (newer["audit_ordinal"] == older["audit_ordinal"]
                    and newer["request_nonce_count"]
                    == older["request_nonce_count"])
                or newer["checkpoint_sha256"] == older["checkpoint_sha256"]):
            raise PermissionError("signed checkpoint not advancing")
    # A signed checksum is not evidence of history extension if the signing
    # key or authority can be rolled back. Require exact local equality only.
    assert_exact_checkpoint(
        database, expected_authority_id, proposed["checkpoint"])
    return new


__all__ = [
    "SCHEMA", "DOMAIN", "verify_signed_checkpoint_receipt",
    "assert_signed_checkpoint_transition",
]
