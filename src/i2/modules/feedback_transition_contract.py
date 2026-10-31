"""Pure G2 guard for a future single-COMMIT H2 state transition.

This does NOT persist state or authorize a life. The sole current owner must
compare a previous digest, apply a validated update, and publish the next
snapshot in its *existing* journal transaction; an external H2 ledger would
create a second owner. No service, WorldBody or M11 authority exists here.
"""
from __future__ import annotations

from dataclasses import dataclass
from .delayed_credit_study import (
    OutcomeFeedbackMemory, FeedbackUpdate, HeldoutForecastScore,
    _feedback_memory_digest,
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
    from fractions import Fraction
    score = update.heldout_score
    if type(score) is not HeldoutForecastScore:
        raise ValueError("exact H2 heldout score required")
    if (type(update.predicted_outcome_difference) is not Fraction or
            type(update.absolute_error) is not Fraction or
            type(update.direction_agreement) is not bool or
            update.absolute_error != abs(
                update.predicted_outcome_difference - score.observed_outcome_difference) or
            update.direction_agreement != (
                ((update.predicted_outcome_difference > 0) -
                 (update.predicted_outcome_difference < 0)) ==
                ((score.observed_outcome_difference > 0) -
                 (score.observed_outcome_difference < 0)))):
        raise ValueError("inconsistent issued H2 feedback score")
    if (type(score.training_episode_refs) is not tuple or
            len(score.training_episode_refs) != 2 or
            len(set(score.training_episode_refs)) != 2):
        raise ValueError("invalid historical H2 episode references")
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
    if (type(score.observed_outcome_difference) is not int or
            not -200 <= score.observed_outcome_difference <= 200 or
            type(score.predicted_outcome_difference) is not int or
            not -200 <= score.predicted_outcome_difference <= 200 or
            type(score.absolute_error) is not int or
            score.absolute_error != abs(
                score.predicted_outcome_difference - score.observed_outcome_difference) or
            type(score.direction_agreement) is not bool or
            score.direction_agreement != (
                ((score.predicted_outcome_difference > 0) -
                 (score.predicted_outcome_difference < 0)) ==
                ((score.observed_outcome_difference > 0) -
                 (score.observed_outcome_difference < 0))) or
            score.interpretation != "HELDOUT_SYNTHETIC_SCORE_NOT_CAUSAL_PROOF" or
            score.motor_authority != "NONE" or
            score.scheduler_uc_authenticated is not False or
            score.m11_authenticated is not False or
            type(score.observed_episode_refs) is not tuple or
            len(score.observed_episode_refs) != 2 or
            len(set(score.observed_episode_refs)) != 2):
        raise ValueError("invalid or motor-capable H2 heldout score")
    # The prospective baseline and the calibrated prediction are different:
    # with no H2 observations the prediction is the historical baseline;
    # afterwards it MUST be the exact mean of the PAST bounded window.
    # An arbitrary post-outcome forecast would make heldout scoring meaningless.
    expected_prediction = (
        Fraction(sum(stored.observed_differences), len(stored.observed_differences))
        if stored.observed_differences else
        Fraction(score.predicted_outcome_difference)
    )
    if update.predicted_outcome_difference != expected_prediction:
        raise ValueError("H2 prediction not derived from prior observations")
    if set(score.training_episode_refs) & set(score.observed_episode_refs):
        raise ValueError("training episode reused as heldout observation")
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
