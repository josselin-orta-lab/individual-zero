"""Detached attestation signature verification, independent of imported archives.

An authenticated signature establishes a custody claim from a configured
issuer, not the physical truth of any claimed world frame.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re

HASH = re.compile(r"[0-9a-f]{64}\Z")
MAX_ATTESTATION = 16 * 1024


def verify_detached_attestation(attestation_path: Path, frames_path: Path, *,
                                trusted_public_key_b64: str,
                                expected_key_id: str) -> dict:
    result = {"signature_valid": False, "frames_digest_matches": False,
              "trusted_issuer_authenticated": False,
              "physical_truth_verified": False, "map_authorized": False,
              "payload": None, "error": None}
    def fail(reason):
        result["error"] = reason
        return result
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        with attestation_path.open("rb") as stream:
            raw = stream.read(MAX_ATTESTATION + 1)
        if len(raw) > MAX_ATTESTATION:
            return fail("attestation_too_large")
        def pairs(items):
            value = {}
            for key, item in items:
                if key in value:
                    raise ValueError("duplicate_json_key")
                value[key] = item
            return value
        attestation = json.loads(raw, object_pairs_hook=pairs)
        if not isinstance(attestation, dict) or set(attestation) != {"schema", "payload", "signature"} or attestation["schema"] != "observer-detached-attestation-v1":
            return fail("invalid_attestation_envelope")
        payload = attestation["payload"]
        signature = attestation["signature"]
        required = {"individual_id", "life_generation", "attempt_ref", "frames_sha256", "journal_head_sha256", "journal_event_count", "issuer", "purpose"}
        if not isinstance(payload, dict) or set(payload) != required or not isinstance(signature, dict) or set(signature) != {"algorithm", "key_id", "value"}:
            return fail("invalid_attestation_fields")
        if payload["purpose"] != "observer-frame-custody-only" or signature["algorithm"] != "Ed25519" or signature["key_id"] != expected_key_id:
            return fail("untrusted_signature_identity")
        if not all(isinstance(payload[k], str) and 0 < len(payload[k]) <= 128 for k in ("individual_id", "attempt_ref", "issuer")) or type(payload["life_generation"]) is not int or payload["life_generation"] < 0 or type(payload["journal_event_count"]) is not int or payload["journal_event_count"] < 1 or not all(isinstance(payload[k], str) and HASH.fullmatch(payload[k]) for k in ("frames_sha256", "journal_head_sha256")):
            return fail("invalid_payload")
        public_key = base64.b64decode(trusted_public_key_b64, validate=True)
        signed = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        Ed25519PublicKey.from_public_bytes(public_key).verify(base64.b64decode(signature["value"], validate=True), signed)
        result["signature_valid"] = True
        result["trusted_issuer_authenticated"] = True
        with frames_path.open("rb") as stream:
            digest = hashlib.sha256(stream.read(16 * 1024 * 1024 + 1)).hexdigest()
        result["frames_digest_matches"] = digest == payload["frames_sha256"]
        if not result["frames_digest_matches"]:
            return fail("frames_digest_mismatch")
        result["payload"] = payload
        return result
    except ImportError:
        return fail("cryptography_dependency_unavailable")
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, OverflowError):
        return fail("invalid_attestation_or_key")
    except Exception:
        return fail("signature_verification_failed")
