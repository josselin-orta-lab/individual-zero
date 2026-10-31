"""Pure G2 guard for a future single-COMMIT H2 state transition.

This does NOT persist state or authorize a life. The sole current owner must
compare a previous digest, apply a validated update, and publish the next
snapshot in its *existing* journal transaction; an external H2 ledger would
create a second owner. No service, WorldBody or M11 authority exists here.
"""
from __future__ import annotations

from dataclasses import dataclass
from .delayed_credit_study import (
    OutcomeFeedbackMemory, FeedbackUpdate, _feedback_memory_digest,
)


@dataclass(frozen=True, slots=True)
class FeedbackTransitionProof:
    previous_digest: str
    next_digest: str
    previous_version: int
    next_version: int
    life_ref: str
    motor_authority: str = "NONE"
    m11_authenticated: bool = False


def verify_feedback_transition(
    *, stored: OutcomeFeedbackMemory, expected_previous_digest: str,
    update: FeedbackUpdate,
) -> FeedbackTransitionProof:
    """Validate optimistic-CAS inputs before a future owner's single COMMIT.

    The caller is responsible for acquiring the *same* database transaction
    that owns cognition, debits and the causal event, and for authenticating
    the source of update. Neither is implemented by this pure validator.
    """
    if type(stored) is not OutcomeFeedbackMemory or type(update) is not FeedbackUpdate:
        raise ValueError("exact H2 memory and update required")
    stored.validate()
    if type(expected_previous_digest) is not str:
        raise ValueError("exact previous H2 digest required")
    previous = _feedback_memory_digest(stored)
    if previous != expected_previous_digest:
        raise ValueError("stale H2 memory version or replaced snapshot")
    if (update.motor_authority != "NONE" or
            update.interpretation != "SYNTHETIC_ADAPTATION_NOT_CAUSAL_OR_MOTOR_PROOF"):
        raise ValueError("motor-capable or foreign H2 update")
    current = update.new_memory
    if type(current) is not OutcomeFeedbackMemory:
        raise ValueError("exact successor H2 snapshot required")
    current.validate()
    identity = (
        "life_ref", "goal_ref", "context_signature", "preparatory_action_ref",
        "alternative_action_ref", "completion_action_ref",
    )
    if any(getattr(stored, key) != getattr(current, key) for key in identity):
        raise ValueError("H2 successor changes life, goal or subjective context")
    if (current.total_observations != stored.total_observations + 1 or
            current.last_observed_step <= stored.last_observed_step):
        raise ValueError("H2 history did not advance exactly once")
    score = update.heldout_score
    if (score.life_ref != stored.life_ref or
            score.issue_capture_ref in stored.used_issue_captures or
            any(ref in stored.used_episode_refs for ref in score.observed_episode_refs) or
            current.observed_differences !=
            (stored.observed_differences + (score.observed_outcome_difference,))[-16:] or
            current.used_issue_captures !=
            (stored.used_issue_captures + (score.issue_capture_ref,))[-16:] or
            current.used_episode_refs !=
            (stored.used_episode_refs + score.observed_episode_refs)[-32:]):
        raise ValueError("H2 successor does not match scored evidence")
    from hashlib import sha256
    import json
    payload = json.dumps(
        ["i2-h2-feedback-history-v1", stored.history_head,
         score.issue_capture_ref, list(score.observed_episode_refs),
         score.observed_outcome_difference],
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")
    if current.history_head != sha256(payload).hexdigest():
        raise ValueError("H2 transition history head mismatch")
    return FeedbackTransitionProof(
        previous, _feedback_memory_digest(current),
        stored.total_observations, current.total_observations,
        stored.life_ref,
    )
