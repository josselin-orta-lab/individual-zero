"""Read-only I2 candidate reconstruction from the current *claimed* capture.

This is an inert research component, NOT a planner or Competition adapter.
It produces non-authoritative semantic descriptors for *all* currently
accessible affordances. An intention can add provenance metadata to exactly
one descriptor, but can neither add/withdraw candidates nor supply preference,
accumulated evidence, a command, a winner or motor admission.

A caller must have separately authenticated the first-person source, paid for
all actual cognition and admitted a current transition. These guarantees are
NOT supplied or established by this pure deterministic function; even a
matching IntentionTransition.work_ref is only a correlation string.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .intention_continuity import (
    IntentionTransition,
    SemanticIntention,
    _ref,
)
from .intention_ingress import ObservationClaim

RECONSTRUCTION_SCHEMA = "i2-semantic-candidate-reconstruction-v1"
_ACTIVE_TRANSITIONS = frozenset({"opened", "retained", "resumed"})
_SUSPENDED_TRANSITIONS = frozenset({"suspended", "still_suspended"})
_CLEARED_TRANSITIONS = frozenset({"expired", "goal_changed", "contradicted", "idle"})


def _bound_id(kind: str, *parts: str) -> str:
    # Canonical length-delimited JSON avoids delimiter collisions in source refs.
    raw = json.dumps((RECONSTRUCTION_SCHEMA, kind, *parts),
                     separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return f"{kind}:i2:" + sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class SemanticCandidate:
    """One ephemeral, NON-ADMITTED semantic possibility; no executable action."""

    candidate_ref: str
    semantic_ref: str
    intention_ref: str | None


@dataclass(frozen=True, slots=True)
class CandidateFrame:
    """Read-only proposals; a downstream *independent* gate must recheck all."""

    frame_ref: str
    life_ref: str
    capture_ref: str
    physical_step: int
    claim_digest: str
    work_correlation_ref: str
    candidates: tuple[SemanticCandidate, ...]


def reconstruct_candidates(
    *, claim: ObservationClaim, transition: IntentionTransition,
    current: SemanticIntention | None,
) -> CandidateFrame:
    """Rebuild all visible candidates, never an executable command or ranking.

    Preconditions are strictly *consistency* checks, not M11/source/UC
    authentication. The owner must have consumed this very capture already.
    No mutable option/Competition state is read or retained.
    """
    if type(claim) is not ObservationClaim:
        raise ValueError("exact subjective observation claim required")
    claim.validate()
    if type(transition) is not IntentionTransition:
        raise ValueError("exact owner transition required")
    if type(transition.kind) is not str or transition.kind not in (
        _ACTIVE_TRANSITIONS | _SUSPENDED_TRANSITIONS | _CLEARED_TRANSITIONS
    ):
        raise ValueError("unrecognized owner transition")
    if (type(transition.step) is not int or type(transition.capture_ref) is not str
            or transition.step != claim.capture.step or transition.capture_ref != claim.capture.ref):
        raise ValueError("owner transition belongs to another capture")
    _ref(transition.work_ref, "unverified work correlation")

    if current is None:
        if transition.kind not in _CLEARED_TRANSITIONS:
            raise ValueError("missing current intention after active transition")
        if transition.kind == "idle":
            if transition.intention_ref is not None:
                raise ValueError("idle transition cannot reference an intention")
        else:
            _ref(transition.intention_ref, "previous intention ref")
    else:
        if type(current) is not SemanticIntention:
            raise ValueError("exact owner intention required")
        current.validate()
        if transition.kind not in _ACTIVE_TRANSITIONS | _SUSPENDED_TRANSITIONS:
            raise ValueError("inconsistent intention transition kind")
        if transition.intention_ref != current.ref:
            raise ValueError("transition references another intention")
        if (current.last_checked_step != claim.capture.step
                or current.last_capture_ref != claim.capture.ref):
            raise ValueError("stale intention relative to current capture")
        if current.goal_ref != claim.capture.goal_ref:
            raise ValueError("intention goal differs from current goal")
        if current.semantic_ref in claim.capture.contradicted_semantics:
            raise ValueError("contradicted intention still present")
        visible = current.semantic_ref in claim.capture.accessible_semantics
        if visible != (current.status == "active"):
            raise ValueError("intention status inconsistent with visibility")
        if current.status == "active" and transition.kind not in _ACTIVE_TRANSITIONS:
            raise ValueError("active intention with suspended transition")
        if current.status == "suspended" and transition.kind not in _SUSPENDED_TRANSITIONS:
            raise ValueError("suspended intention with active transition")
        if transition.kind == "opened" and (
            current.created_step != claim.capture.step
            or current.origin_capture_ref != claim.capture.ref
            or current.origin_evidence_ref not in claim.subjective_evidence_refs
        ):
            raise ValueError("new intention's origin not in current capture")

    digest = claim.digest()  # content binding only, never a signature
    descriptors = tuple(
        SemanticCandidate(
            candidate_ref=_bound_id("candidate", claim.life_ref, digest, semantic),
            semantic_ref=semantic,
            intention_ref=(current.ref if current is not None and
                           current.status == "active" and
                           current.semantic_ref == semantic else None),
        )
        for semantic in claim.capture.accessible_semantics
    )
    return CandidateFrame(
        frame_ref=_bound_id("frame", claim.life_ref, digest, transition.work_ref,
                            transition.kind, transition.intention_ref or "absent"),
        life_ref=claim.life_ref, capture_ref=claim.capture.ref,
        physical_step=claim.capture.step, claim_digest=digest,
        work_correlation_ref=transition.work_ref,
        candidates=descriptors,
    )
