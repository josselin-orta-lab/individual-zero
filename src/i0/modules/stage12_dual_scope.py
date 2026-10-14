"""Versioned first-person action / outcome scope, without physical oracle truth.

Pure subordinate cognitive policy. Runtime wiring needs separate M11/UC gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from i0.modules.stage12_goal_agency import GoalAgencyCommitment, GoalAgencyJudgement
from i0.modules.perception import PerceptualCapture

DUAL_SCOPE_VERSION = "stage12-dual-scope-agency-v1"
OUTCOMES = frozenset(("improved", "not_improved", "unknown", "unavailable"))
RESPONSIBILITIES = frozenset(("unknown", "unavailable"))


@dataclass(frozen=True, slots=True)
class OutcomeScopeJudgement:
    policy_version: str
    life_id: str
    intent_ref: str
    assessment_ref: str
    sent_world_step: int
    observed_world_step: int
    proximal_assessment_ref: str
    proximal_agency: str
    observed_outcome: str
    subjective_responsibility: str
    reason: str
    cue_ref: str | None

    def validate(self) -> None:
        if (self.policy_version != DUAL_SCOPE_VERSION
                or any(type(v) is not str or not v.strip() for v in (
                    self.life_id, self.intent_ref, self.assessment_ref,
                    self.proximal_assessment_ref, self.reason))
                or self.observed_outcome not in OUTCOMES
                or self.subjective_responsibility not in RESPONSIBILITIES
                or self.proximal_agency not in ("self", "world", "unknown", "unavailable")
                or type(self.sent_world_step) is not int
                or type(self.observed_world_step) is not int
                or self.sent_world_step < 1
                or self.observed_world_step <= self.sent_world_step
                or (self.subjective_responsibility == "unavailable")
                   != (self.observed_outcome == "unavailable")
                or (self.cue_ref is None) != (self.observed_outcome == "unavailable")
                or (self.cue_ref is not None and
                    (type(self.cue_ref) is not str or not self.cue_ref.strip()))):
            raise ValueError("invalid dual-scope outcome judgement")

    def as_dict(self) -> dict[str, object]:
        return {key: getattr(self, key) for key in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, raw: object) -> "OutcomeScopeJudgement":
        if type(raw) is not dict or set(raw) != set(cls.__dataclass_fields__):
            raise ValueError("invalid dual-scope state image")
        value = cls(**raw)
        value.validate()
        return value


def evaluate_outcome_scope(
    commitment: GoalAgencyCommitment,
    proximal: GoalAgencyJudgement,
    *,
    original: PerceptualCapture,
    observed: PerceptualCapture | None,
    paid: bool,
    cue_ref: str | None,
) -> OutcomeScopeJudgement:
    """Report perceived change, abstain from distal causation unconditionally.

    No reading of body effects, oracle outcomes or physical causes. Intended
    as an independent, separately charged output of Action Control.
    """
    commitment.validate()
    proximal.validate()
    if (proximal.assessment_ref != commitment.assessment_ref
            or proximal.intent_ref != commitment.intent_ref
            or proximal.life_id != commitment.life_id
            or original.t_monde != commitment.sent_world_step
            or proximal.sent_world_step != commitment.sent_world_step
            or (observed is not None and observed.t_monde != proximal.observed_world_step)):
        raise ValueError("dual-scope action/observation provenance mismatch")
    available = (paid and observed is not None
                 and proximal.observed_world_step == commitment.observe_world_step)
    if available and (type(cue_ref) is not str or not cue_ref.strip()):
        raise ValueError("dual-scope paid judgement requires cue ref")
    outcome = "unknown"
    reason = "observed_goal_change_not_causal_responsibility"
    if not available:
        outcome, reason = "unavailable", "scope_uc_or_observation_unavailable"
    elif commitment.goal_measure == "spatial_distance":
        outcome = "unknown"
        reason = "spatial_goal_change_not_proven_by_action_position"
    else:
        before = original.body.get(commitment.goal_measure)
        after = observed.body.get(commitment.goal_measure)
        if (type(before) in (int, float) and type(after) in (int, float)
                and isfinite(before) and isfinite(after)):
            # The body state is a sensed criterion, not an authenticated cause.
            outcome = "improved" if after > before else "not_improved"
    value = OutcomeScopeJudgement(
        policy_version=DUAL_SCOPE_VERSION, life_id=commitment.life_id,
        intent_ref=commitment.intent_ref,
        assessment_ref="scope:" + commitment.assessment_ref,
        sent_world_step=commitment.sent_world_step,
        observed_world_step=proximal.observed_world_step,
        proximal_assessment_ref=proximal.assessment_ref,
        proximal_agency=proximal.subjective_agency,
        observed_outcome=outcome,
        subjective_responsibility="unavailable" if not available else "unknown",
        reason=reason, cue_ref=cue_ref if available else None,
    )
    value.validate()
    return value
