"""R2.6 read-only, required-witness reconciliation of an engineering state.

NO native motor/recovery GO, external M11 attestation or automatic publication.
The latest callback is a dependency injection, not evidence of an independent
security principal; a co-rollbackable provider destroys its safety premise.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from i3.lab.engineering_remote_checkpoint_probe import capture_exact_checkpoint
from i3.lab.engineering_remote_checkpoint_publisher import (
    TestOnlyCheckpointPublisher,
)
from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    verify_signed_checkpoint_receipt,
)
from i3.runtime.engineering_remote_witness import canonical

SCHEMA = "i3-test-only-witness-reconciliation/v1"


def reconcile_required_witness(
        authority_db: Path, publication_db: Path, *,
        authority_id: str, source_sha256: str, key_id: str,
        trusted_public_key: bytes, target_identity_sha256: str,
        fetch_required_latest) -> dict:
    """Return a strictly observational match, or STOP closed.

    The callback must return an externally maintained **latest** signed
    receipt for production use. Neither freshness nor operator/host privilege
    is independently verified by this local software. Without a callback,
    never use the local publisher as a substitute. A successful check is NOT
    an executable resume token; Mind/World/RNG/body cannot be reconstructed.
    """
    if not callable(fetch_required_latest):
        raise PermissionError("required witness retrieval missing: STOP")
    try:
        witness_raw = fetch_required_latest()
    except Exception as exc:
        raise PermissionError("required witness unavailable: STOP") from exc
    if type(witness_raw) is not bytes or not witness_raw:
        raise PermissionError("required witness missing exact signed bytes: STOP")

    pins = {
        "trusted_public_key": trusted_public_key,
        "expected_authority_id": authority_id,
        "expected_source_sha256": source_sha256,
        "expected_key_id": key_id,
    }
    signed = verify_signed_checkpoint_receipt(witness_raw, **pins)
    local_tip = TestOnlyCheckpointPublisher.inspect_existing_latest(
        publication_db, authority_db, authority_id=authority_id,
        source_sha256=source_sha256, key_id=key_id,
        trusted_public_key=trusted_public_key)
    if local_tip is None or local_tip != witness_raw:
        raise PermissionError(
            "local publisher differs from required witness high-water: STOP")

    current = capture_exact_checkpoint(
        authority_db, authority_id,
        expected_source_sha256=source_sha256,
        expected_open_identity_sha256=target_identity_sha256)
    if canonical(current) != canonical(signed["payload"]["checkpoint"]):
        raise PermissionError(
            "audited authority differs from required signed witness: STOP")

    # This is only a point-in-time diagnostic. The separate DBs cannot be
    # read atomically together, and a writer may advance after this return.
    return {
        "schema": SCHEMA,
        "result": "READ_ONLY_MATCH_NO_MOTOR_AUTHORITY",
        "authority_id": authority_id,
        "source_sha256": source_sha256,
        "target_identity_sha256": target_identity_sha256,
        "publication_index": signed["payload"]["publication_index"],
        "receipt_sha256": sha256(witness_raw).hexdigest(),
        "motor_authority": False,
        "scientific_world_authorized": False,
        "independent_m11_attested": False,
    }


__all__ = ["SCHEMA", "reconcile_required_witness"]
