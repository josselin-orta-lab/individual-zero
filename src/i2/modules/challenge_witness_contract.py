"""G2 contract for a challenge-bound witness, not a deployed trust service.

The verifier and trusted policy are injected and independently operated.
No cryptographic algorithm, private key, signer, motor or M11 lives here.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Protocol
from .lifecycle_external_witness import LatestWitness, _ref

SCHEMA = "i2-challenge-bound-witness-proposal-v1"
_HEX = frozenset("0123456789abcdef")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


@dataclass(frozen=True, slots=True)
class TrustPolicy:
    authority_ref: str
    key_ref: str
    valid_from: int
    valid_until: int
    revoked: bool = False

    def validate(self) -> None:
        _ref(self.authority_ref, "authority")
        _ref(self.key_ref, "key")
        if (type(self.valid_from) is not int or type(self.valid_until) is not int
                or self.valid_from < 0 or self.valid_until <= self.valid_from
                or type(self.revoked) is not bool):
            raise ValueError("invalid trust policy")


@dataclass(frozen=True, slots=True)
class SignedClaim:
    schema: str
    authority_ref: str
    key_ref: str
    challenge: str
    issued_at: int
    expires_at: int
    record: LatestWitness
    signature: bytes


class SignatureVerifier(Protocol):
    def verify(self, *, authority_ref: str, key_ref: str,
               message: bytes, signature: bytes) -> bool: ...


def verify_claim(*, claim: SignedClaim, policy: TrustPolicy, challenge: str,
                 now: int, verifier: SignatureVerifier) -> LatestWitness:
    """Only structure/authenticity of a claimed reply, NEVER real freshness."""
    if type(claim) is not SignedClaim or type(policy) is not TrustPolicy:
        raise ValueError("exact signed claim and policy required")
    policy.validate()
    if type(challenge) is not str or len(challenge) != 64 or not set(challenge) <= _HEX:
        raise ValueError("a 256-bit hex challenge is required")
    if type(now) is not int or now < 0:
        raise ValueError("invalid trusted time")
    if (claim.schema != SCHEMA or claim.authority_ref != policy.authority_ref
            or claim.key_ref != policy.key_ref or policy.revoked):
        raise ValueError("untrusted authority or revoked key")
    if claim.challenge != challenge:
        raise ValueError("witness challenge mismatch")
    if (type(claim.issued_at) is not int or type(claim.expires_at) is not int
            or not policy.valid_from <= claim.issued_at <= now < claim.expires_at
            or claim.expires_at > policy.valid_until):
        raise ValueError("witness outside trusted validity window")
    if type(claim.record) is not LatestWitness:
        raise ValueError("exact latest witness record required")
    claim.record.validate()
    if type(claim.signature) is not bytes or not claim.signature:
        raise ValueError("signature missing")
    if isinstance(verifier, type) or not callable(getattr(verifier, "verify", None)):
        raise ValueError("independent verifier required")
    payload = canonical({
        "schema": claim.schema, "authority_ref": claim.authority_ref,
        "key_ref": claim.key_ref, "challenge": claim.challenge,
        "issued_at": claim.issued_at, "expires_at": claim.expires_at,
        "record": {
            "witness_schema": claim.record.witness_schema,
            "life_ref": claim.record.life_ref,
            "genesis_ref": claim.record.genesis_ref,
            "journal_schema": claim.record.journal_schema,
            "committed": claim.record.committed,
            "last_step": claim.record.last_step,
            "chain_head": claim.record.chain_head,
            "terminal_ref": claim.record.terminal_ref,
            "terminal_step": claim.record.terminal_step,
            "proof_ref": claim.record.proof_ref,
        },
    })
    try:
        verified = verifier.verify(authority_ref=claim.authority_ref,
                                   key_ref=claim.key_ref, message=payload,
                                   signature=claim.signature)
    except Exception as exc:
        raise ValueError("independent signature verification unavailable") from exc
    if verified is not True:
        raise ValueError("independent signature verification failed")
    return claim.record
