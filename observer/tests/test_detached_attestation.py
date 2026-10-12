import base64
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from observer_app.detached_attestation import verify_detached_attestation


def make_signed(tmp_path):
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)
    key = base64.b64encode(public).decode()
    frames = tmp_path / "frames.json"
    frames.write_bytes(b'{"example":"not-physical-truth"}')
    payload = {"individual_id": "i0", "life_generation": 0, "attempt_ref": "a",
               "frames_sha256": hashlib.sha256(frames.read_bytes()).hexdigest(),
               "journal_head_sha256": "a" * 64, "journal_event_count": 2,
               "issuer": "operator-trusted-key", "purpose": "observer-frame-custody-only"}
    message = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
    signature = base64.b64encode(private.sign(message)).decode()
    document = {"schema": "observer-detached-attestation-v1", "payload": payload,
                "signature": {"algorithm": "Ed25519", "key_id": "operator-key", "value": signature}}
    attestation = tmp_path / "attestation.json"
    attestation.write_text(json.dumps(document))
    return attestation, frames, key


def test_signature_and_digest_do_not_prove_physical_truth(tmp_path):
    attestation, frames, key = make_signed(tmp_path)
    result = verify_detached_attestation(attestation, frames,
                                         trusted_public_key_b64=key, expected_key_id="operator-key")
    assert result["signature_valid"] is True
    assert result["frames_digest_matches"] is True
    assert result["physical_truth_verified"] is False
    assert result["map_authorized"] is False


def test_tampered_frames_rejected(tmp_path):
    attestation, frames, key = make_signed(tmp_path)
    frames.write_bytes(b"tampered")
    result = verify_detached_attestation(attestation, frames,
                                         trusted_public_key_b64=key, expected_key_id="operator-key")
    assert result["error"] == "frames_digest_mismatch"


def test_wrong_trusted_key_rejected(tmp_path):
    attestation, frames, _ = make_signed(tmp_path)
    other = Ed25519PrivateKey.generate().public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    result = verify_detached_attestation(attestation, frames,
                                         trusted_public_key_b64=base64.b64encode(other).decode(),
                                         expected_key_id="operator-key")
    assert result["signature_valid"] is False
    assert result["map_authorized"] is False


def test_untrusted_key_identifier_rejected(tmp_path):
    attestation, frames, key = make_signed(tmp_path)
    result = verify_detached_attestation(attestation, frames,
                                         trusted_public_key_b64=key, expected_key_id="another-key")
    assert result["error"] == "untrusted_signature_identity"
