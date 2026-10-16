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


class DualScopeService:
    """Action Control subordinate, one pending current first-person result.

    Its output is intentionally an abstaining causal attribution, not a
    laboratory cause or inferred goal success. Serializable under M11.
    """

    schema = DUAL_SCOPE_VERSION

    def __init__(self):
        self._pending = None
        self._last = None
        self._last_sent = 0
        self._seen = set()

    @property
    def pending(self):
        return None if self._pending is None else dict(self._pending)

    @property
    def last_judgement(self):
        return self._last

    def preregister(self, commitment: GoalAgencyCommitment,
                    capture: PerceptualCapture):
        commitment.validate()
        if (self._pending is not None
                or capture.t_monde != commitment.sent_world_step
                or commitment.sent_world_step <= self._last_sent
                or commitment.assessment_ref in self._seen):
            raise ValueError("duplicate or inconsistent dual-scope precommit")
        baseline = capture.body.get(commitment.goal_measure)
        if type(baseline) not in (int, float) or not isfinite(baseline):
            baseline = None
        self._pending = {
            "life_id": commitment.life_id,
            "intent_ref": commitment.intent_ref,
            "proximal_assessment_ref": commitment.assessment_ref,
            "sent_world_step": commitment.sent_world_step,
            "observe_world_step": commitment.observe_world_step,
            "goal_measure": commitment.goal_measure,
            "baseline": baseline,
        }
        self._seen.add(commitment.assessment_ref)
        self._last_sent = commitment.sent_world_step
        return dict(self._pending)

    def evaluate(self, proximal: GoalAgencyJudgement, *,
                 capture: PerceptualCapture | None,
                 cue_ref: str | None, paid: bool):
        raw = self._pending
        if raw is None:
            raise ValueError("dual-scope evaluation lacks pending precommit")
        proximal.validate()
        if (raw["life_id"] != proximal.life_id
                or raw["intent_ref"] != proximal.intent_ref
                or raw["proximal_assessment_ref"] != proximal.assessment_ref
                or raw["sent_world_step"] != proximal.sent_world_step):
            raise ValueError("dual-scope proximal provenance mismatch")
        if capture is not None and capture.t_monde != proximal.observed_world_step:
            raise ValueError("dual-scope perceptual step mismatch")
        available = (paid and capture is not None
                     and proximal.observed_world_step == raw["observe_world_step"])
        if available and (type(cue_ref) is not str or not cue_ref.strip()):
            raise ValueError("dual-scope assessment requires sensory receipt")
        observed = "unknown"
        reason = "goal_change_not_causal_responsibility"
        if not available:
            observed, reason = "unavailable", "scope_uc_or_observation_unavailable"
        elif raw["goal_measure"] == "spatial_distance":
            reason = "spatial_goal_result_not_identifiable_from_one_position"
        else:
            after = capture.body.get(raw["goal_measure"])
            before = raw["baseline"]
            if (type(after) in (int, float) and isfinite(after)
                    and before is not None):
                observed = "improved" if after > before else "not_improved"
        result = OutcomeScopeJudgement(
            policy_version=DUAL_SCOPE_VERSION, life_id=raw["life_id"],
            intent_ref=raw["intent_ref"],
            assessment_ref="scope:" + proximal.assessment_ref,
            sent_world_step=raw["sent_world_step"],
            observed_world_step=proximal.observed_world_step,
            proximal_assessment_ref=proximal.assessment_ref,
            proximal_agency=proximal.subjective_agency,
            observed_outcome=observed,
            subjective_responsibility=("unknown" if available else "unavailable"),
            reason=reason, cue_ref=cue_ref if available else None,
        )
        result.validate()
        self._pending = None
        self._last = result
        return result

    def export_causal_state(self):
        return {"schema": self.schema,
                "pending": None if self._pending is None else dict(self._pending),
                "last_judgement": None if self._last is None else self._last.as_dict(),
                "seen": sorted(self._seen), "last_sent": self._last_sent}

    def restore_causal_state(self, state):
        if (type(state) is not dict
                or set(state) != {"schema", "pending", "last_judgement", "seen", "last_sent"}
                or state["schema"] != self.schema
                or type(state["seen"]) is not list
                or any(type(x) is not str or not x for x in state["seen"])
                or state["seen"] != sorted(set(state["seen"]))
                or type(state["last_sent"]) is not int
                or state["last_sent"] < 0
                or self._seen or self._pending is not None or self._last is not None):
            raise ValueError("invalid or nonfresh dual-scope owner state")
        p = state["pending"]
        if p is not None:
            if (type(p) is not dict or set(p) != {
                "life_id", "intent_ref", "proximal_assessment_ref",
                "sent_world_step", "observe_world_step", "goal_measure", "baseline"
            } or not all(type(p[k]) is str and p[k] for k in
                ("life_id", "intent_ref", "proximal_assessment_ref", "goal_measure"))
                or type(p["sent_world_step"]) is not int
                or p["sent_world_step"] < 1
                or p["observe_world_step"] != p["sent_world_step"] + 1
                or p["proximal_assessment_ref"] not in state["seen"]
                or p["sent_world_step"] != state["last_sent"]
                or (p["baseline"] is not None and
                    (type(p["baseline"]) not in (int, float)
                     or not isfinite(p["baseline"])))):
                raise ValueError("invalid pending dual-scope state")
        last = (None if state["last_judgement"] is None
                else OutcomeScopeJudgement.from_dict(state["last_judgement"]))
        if (last is not None
                and (last.proximal_assessment_ref not in state["seen"]
                     or last.sent_world_step > state["last_sent"])
                or bool(state["seen"]) != (state["last_sent"] > 0)):
            raise ValueError("inconsistent dual-scope judgement lineage")
        self._seen = set(state["seen"])
        self._last_sent = state["last_sent"]
        self._pending = None if p is None else dict(p)
        self._last = last
