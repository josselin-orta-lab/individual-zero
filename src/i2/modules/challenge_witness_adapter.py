"""Inert challenge/response adapter for a claimed latest-head witness.

All trust inputs and the transport are injected. No physical or M11 authority.
A fresh unpredictable challenge MUST be guaranteed by the caller's provider.
"""
from __future__ import annotations
from threading import Lock
from typing import Protocol
from .challenge_witness_contract import (
    SignedClaim, SignatureVerifier, TrustPolicy, verify_claim,
)
from .lifecycle_external_witness import LatestWitness, _ref

_CHALLENGE_HEX = frozenset("0123456789abcdef")


class ChallengeSource(Protocol):
    def next_challenge(self) -> str: ...


class TrustedClock(Protocol):
    def now(self) -> int: ...


class WitnessTransport(Protocol):
    def request_latest(self, *, life_ref: str, genesis_ref: str,
                       challenge: str) -> SignedClaim: ...


class ChallengeBoundWitness:
    """One request per read; not a provably independent monotonic authority."""

    def __init__(self, *, challenge_source: ChallengeSource, clock: TrustedClock,
                 transport: WitnessTransport, verifier: SignatureVerifier,
                 policy: TrustPolicy) -> None:
        if type(policy) is not TrustPolicy:
            raise ValueError("exact key policy required")
        policy.validate()
        for port, method in ((challenge_source, "next_challenge"),
                             (clock, "now"), (transport, "request_latest"),
                             (verifier, "verify")):
            if isinstance(port, type) or not callable(getattr(port, method, None)):
                raise ValueError("mandatory injected witness port unavailable")
        self._challenge_source = challenge_source
        self._clock = clock
        self._transport = transport
        self._verifier = verifier
        self._policy = policy
        # G2 session-only deduplication: no persisted key, shared ledger or
        # authority to attest monotonicity after process restart.
        self._seen_challenges: set[str] = set()
        self._challenge_lock = Lock()

    def read_verified_latest(self, *, life_ref: str,
                             genesis_ref: str) -> LatestWitness:
        _ref(life_ref, "witness life")
        _ref(genesis_ref, "witness genesis")
        # Reserve a syntactically valid challenge BEFORE the external call.
        # The short critical section prevents two threads from sending one
        # nonce, even if a provider times out after responding to the first.
        # Never release a reserved nonce after failure: acknowledgment may
        # have been lost. A new instance does not inherit this ledger.
        with self._challenge_lock:
            challenge = self._challenge_source.next_challenge()
            if (type(challenge) is not str or len(challenge) != 64
                    or not set(challenge) <= _CHALLENGE_HEX):
                raise ValueError("invalid 256-bit witness challenge")
            if challenge in self._seen_challenges:
                raise ValueError("duplicate witness challenge in this instance")
            self._seen_challenges.add(challenge)
        # No transport, signature, clock or M11 authority is implemented here.
        response = self._transport.request_latest(
            life_ref=life_ref, genesis_ref=genesis_ref, challenge=challenge,
        )
        verified = verify_claim(
            claim=response, policy=self._policy,
            challenge=challenge, now=self._clock.now(),
            verifier=self._verifier,
        )
        if verified.life_ref != life_ref or verified.genesis_ref != genesis_ref:
            raise ValueError("verified response belongs to another life")
        return verified
