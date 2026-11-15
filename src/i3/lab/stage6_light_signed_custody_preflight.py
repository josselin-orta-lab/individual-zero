"""Offline Stage6-light signed custody *consistency* preflight; never a GO.

A signature proves control of a pinned key for supplied bytes, not witness
independence, historical first-seen time, absence of later key compromise, or
native execution. The caller must supply independently retained hashes/pins;
this module cannot establish that they actually came from independent custody.
No signer, network publisher, run_life, World, Mind, seed allocator or admission
interface exists here.
"""
from __future__ import annotations

import base64
import binascii
from hashlib import sha256
import json
from pathlib import Path
import re

METHOD = (Path(__file__).resolve().parents[1] / "docs" / "studies" /
          "stage6-light-preparation" / "STAGE6_LIGHT_PROTOCOL_METHOD_V1.json")
PROTOCOL = "I3_STAGE6_LIGHT_METHOD_V1"
SCHEMA = "i3-stage6-light-external-custody-receipt/v1"
ANCHOR_DOMAIN = b"I3-STAGE6-LIGHT-PRECOMMIT-WITNESS/v1\0"
EVENT_DOMAIN = b"I3-STAGE6-LIGHT-PHASE-RECEIPT/v1\0"
PHASES = (
    "G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
    "SELECT_G2", "G2", "SEAL_G2", "R_FINAL",
)
_MAX_RECEIPT = 4096
_MAX_METHOD = 16384
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_KEY_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_ENVELOPE = {"schema", "payload", "signature"}
_SIGNATURE = {"algorithm", "key_id", "value"}
_PRECOMMIT = {
    "kind", "protocol_id", "run_id", "method_sha256", "source_sha256",
    "transport_sha256", "allocation_sha256", "seed_commitment_sha256",
    "witness_key_id", "publisher_key_id", "publisher_public_key_sha256",
}
_PHASE = {
    "kind", "protocol_id", "run_id", "phase", "ordinal",
    "precommit_sha256", "previous_receipt_sha256", "input_artifact_sha256",
    "artifact_sha256",
}
_DENIED = (
    "worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
    "science_admission_allowed", "auto_start_allowed",
    "adr0017_lineage_exception_accepted",
)
_UNASSIGNED = (
    "owner_decision_sha", "owner_authorized_world_indices",
    "assigned_world_seeds", "assigned_founder_seeds",
    "execution_source_sha", "execution_transport_fingerprint",
    "independent_allocation_manifest_sha256",
    "full_scale_python311_rehearsal_sha", "full_scale_python312_rehearsal_sha",
)


def _sha(value: object) -> bool:
    return type(value) is str and _SHA256.fullmatch(value) is not None


def _key_id(value: object) -> bool:
    return type(value) is str and _KEY_ID.fullmatch(value) is not None


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _unique_pairs(pairs: list) -> dict:
    value = {}
    for name, item in pairs:
        if name in value:
            raise ValueError("duplicate key in signed receipt")
        value[name] = item
    return value


def _parse(raw: bytes, *, payload_keys: set[str]) -> dict:
    if type(raw) is not bytes or not 0 < len(raw) <= _MAX_RECEIPT:
        raise PermissionError("missing, oversized or non-byte signed custody receipt")
    try:
        doc = json.loads(raw, object_pairs_hook=_unique_pairs)
        if (type(doc) is not dict or set(doc) != _ENVELOPE or
                doc["schema"] != SCHEMA or
                type(doc["payload"]) is not dict or
                set(doc["payload"]) != payload_keys or
                type(doc["signature"]) is not dict or
                set(doc["signature"]) != _SIGNATURE or
                doc["signature"]["algorithm"] != "Ed25519" or
                _canonical(doc) != raw):
            raise ValueError("invalid canonical custody receipt")
        return doc
    except (UnicodeError, ValueError, KeyError, TypeError, RecursionError) as exc:
        raise PermissionError("invalid or ambiguous signed custody JSON") from exc


def _verify(raw: bytes, doc: dict, *, key: bytes, key_id: str,
            domain: bytes) -> dict:
    sig = doc["signature"]
    if sig["key_id"] != key_id or type(sig["value"]) is not str:
        raise PermissionError("receipt signer identity differs from external key pin")
    try:
        signature = base64.b64decode(sig["value"], validate=True)
        if (len(signature) != 64 or
                base64.b64encode(signature).decode("ascii") != sig["value"]):
            raise ValueError("noncanonical Ed25519 receipt signature")
    except (ValueError, binascii.Error) as exc:
        raise PermissionError("invalid Ed25519 signature bytes") from exc
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise PermissionError("Ed25519 dependency unavailable; fail closed") from exc
    try:
        Ed25519PublicKey.from_public_bytes(key).verify(
            signature, domain + _canonical({"schema": SCHEMA,
                                            "payload": doc["payload"]}))
    except (ValueError, InvalidSignature) as exc:
        raise PermissionError("signed custody receipt signature mismatch") from exc
    return doc["payload"]


def _assert_denied_method(expected_method_sha256: str) -> None:
    """Read only the frozen deny-all method, never rewrite or admit it."""
    path = Path(METHOD)
    if path.is_symlink() or not path.is_file():
        raise PermissionError("Stage6 method must be a non-symlink regular file")
    raw = path.read_bytes()
    if (not 0 < len(raw) <= _MAX_METHOD or
            sha256(raw).hexdigest() != expected_method_sha256):
        raise PermissionError("externally pinned fixed Stage6 method not present")
    try:
        method = json.loads(raw, object_pairs_hook=_unique_pairs)
        auth = method["authorization"]
        custody = method["custody"]
        if (type(method) is not dict or
                method.get("schema") != "i3-stage6-light-method-preauth/v1" or
                method.get("protocol_id") != PROTOCOL or
                method.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE" or
                method.get("phase") != "design_only" or
                method.get("scientific_verdict") != "NOT_ISSUED" or
                type(auth) is not dict or
                set(auth) != set(_DENIED + _UNASSIGNED) or
                any(auth[k] is not False for k in _DENIED) or
                any(auth[k] is not None for k in _UNASSIGNED) or
                type(custody) is not dict or
                custody.get("scientific_worlds_and_lives_now_allowed") is not False or
                custody.get("rehearsal_worlds_and_lives_now_allowed") is not False or
                custody.get("per_generation_selection_requires_separate_adr0017_acceptance") is not True or
                custody.get("phases") != list(PHASES)):
            raise ValueError("method permissions are not fully denied")
    except (ValueError, TypeError, KeyError, UnicodeError) as exc:
        raise PermissionError("Stage6 method not valid/deny-all") from exc


def inspect_signed_custody_prefix(precommit_raw: bytes, event_receipts: list[bytes], *,
                                  trusted_witness_public_key: bytes,
                                  trusted_publisher_public_key: bytes,
                                  witness_key_id: str, publisher_key_id: str,
                                  retained_precommit_sha256: str,
                                  retained_latest_sha256: str,
                                  expected_run_id: str,
                                  expected_method_sha256: str,
                                  expected_source_sha256: str,
                                  expected_transport_sha256: str,
                                  expected_allocation_sha256: str,
                                  expected_seed_commitment_sha256: str) -> dict:
    """Check a claimed, signed, source/seed-bound G/S/R phase prefix.

    Both SHA high-water values must arrive from an independent retention
    system outside the originator's rollback domain. This *function cannot*
    establish that independence, or an independently witnessed first-seen time.
    Source/seed claims are not seed allocation or evidence that a World ran.
    """
    for name, digest in (
        ("retained precommit", retained_precommit_sha256),
        ("retained latest", retained_latest_sha256),
        ("run ID", expected_run_id),
        ("method", expected_method_sha256),
        ("source", expected_source_sha256),
        ("transport", expected_transport_sha256),
        ("allocation", expected_allocation_sha256),
        ("seed commitment", expected_seed_commitment_sha256),
    ):
        if not _sha(digest):
            raise PermissionError("explicit 64-hex external " + name + " pin required")
    if (type(trusted_witness_public_key) is not bytes or
            len(trusted_witness_public_key) != 32 or
            type(trusted_publisher_public_key) is not bytes or
            len(trusted_publisher_public_key) != 32 or
            trusted_witness_public_key == trusted_publisher_public_key or
            not _key_id(witness_key_id) or not _key_id(publisher_key_id) or
            witness_key_id == publisher_key_id):
        raise PermissionError("two distinct, explicitly pinned Ed25519 keys required")
    if (type(event_receipts) is not list or len(event_receipts) > len(PHASES)):
        raise PermissionError("bounded exact-order phase receipt list required")
    _assert_denied_method(expected_method_sha256)
    if type(precommit_raw) is not bytes or not 0 < len(precommit_raw) <= _MAX_RECEIPT:
        raise PermissionError("missing or oversized external precommit receipt")
    if sha256(precommit_raw).hexdigest() != retained_precommit_sha256:
        raise PermissionError("precommit not equal to retained outside-domain anchor")
    first = _parse(precommit_raw, payload_keys=_PRECOMMIT)
    precommit = _verify(precommit_raw, first,
                        key=trusted_witness_public_key,
                        key_id=witness_key_id, domain=ANCHOR_DOMAIN)
    expected = {
        "kind": "PRECOMMIT", "protocol_id": PROTOCOL,
        "run_id": expected_run_id,
        "method_sha256": expected_method_sha256,
        "source_sha256": expected_source_sha256,
        "transport_sha256": expected_transport_sha256,
        "allocation_sha256": expected_allocation_sha256,
        "seed_commitment_sha256": expected_seed_commitment_sha256,
        "witness_key_id": witness_key_id,
        "publisher_key_id": publisher_key_id,
        "publisher_public_key_sha256": sha256(trusted_publisher_public_key).hexdigest(),
    }
    if precommit != expected:
        raise PermissionError("precommit not pinned to the intended method/source/seed roles")
    anchor_sha = retained_precommit_sha256
    previous_receipt_sha = anchor_sha
    previous_artifact_sha = expected_seed_commitment_sha256
    seen_artifacts = {previous_artifact_sha}
    for index, raw in enumerate(event_receipts):
        event_doc = _parse(raw, payload_keys=_PHASE)
        event = _verify(raw, event_doc,
                        key=trusted_publisher_public_key,
                        key_id=publisher_key_id, domain=EVENT_DOMAIN)
        if (event["kind"] != "PHASE" or
                event["protocol_id"] != PROTOCOL or
                event["run_id"] != expected_run_id or
                event["phase"] != PHASES[index] or
                type(event["ordinal"]) is not int or event["ordinal"] != index+1 or
                event["precommit_sha256"] != anchor_sha or
                event["previous_receipt_sha256"] != previous_receipt_sha or
                event["input_artifact_sha256"] != previous_artifact_sha or
                not _sha(event["artifact_sha256"]) or
                event["artifact_sha256"] in seen_artifacts):
            raise PermissionError("phase order, continuity, dependency or artifact changed")
        seen_artifacts.add(event["artifact_sha256"])
        previous_artifact_sha = event["artifact_sha256"]
        previous_receipt_sha = sha256(raw).hexdigest()
    if previous_receipt_sha != retained_latest_sha256:
        raise PermissionError("signed prefix is not the outside-domain retained latest high-water")
    return {
        "schema": "i3-stage6-light-signed-custody-preflight/v1",
        "status": "SIGNED_PHASE_PREFIX_MATCH_ONLY_NOT_INDEPENDENTLY_ATTESTED",
        "precommit_signature_verified": True,
        "publisher_phase_signatures_verified": len(event_receipts),
        "phases_verified": len(event_receipts),
        "phase_prefix": list(PHASES[:len(event_receipts)]),
        "complete_declared_phase_chain": len(event_receipts) == len(PHASES),
        "external_pins_supplied_but_independence_not_proved": True,
        "historical_first_exposure_time_attested": False,
        "source_executed_and_seed_sampling_attested": False,
        "true_original_gsr_order_attested": False,
        "independent_original_archive_custody_attested": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
        "stage6_execution_status": "STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION",
    }


def run_life(*_args, **_kwargs):
    raise PermissionError("signed custody preflight cannot open a life")


def open_world(*_args, **_kwargs):
    raise PermissionError("signed custody preflight cannot open a World")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("signed custody preflight cannot grant science admission")
