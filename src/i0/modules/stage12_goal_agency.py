"""GA-01/GA-04: I0 first-person responsibility about goal-directed action.

An agent's attribution is a *fallible judgment*, NOT an inferred physical
cause, a goal-outcome score, or a P-47 prediction-comparison label. Input is
only the efferent voluntary command and the authorized Perception captures.
Owned as a bounded subordinate facet of canonical Action Control.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.interfaces import PrimitiveCommand
from .perception import PerceptualCapture

GOAL_AGENCY_VERSION = "stage12-first-person-goal-agency-v1"


def _ref(value: object) -> bool:
    return type(value) is str and bool(value.strip())


@dataclass(frozen=True, slots=True)
class GoalAgencyCommitment:
    assessment_ref: str
    intent_ref: str
    life_id: str
    goal_ref: str
    option_ref: str
    command_hash: str
    sent_world_step: int
    observe_world_step: int
    goal_measure: str
    action_primitive: str
    action_target: str | None
    start_position: tuple[int, int]
    inventory_before: int | None
    mechanism: str
    policy_version: str = GOAL_AGENCY_VERSION

    def validate(self) -> None:
        if (self.policy_version != GOAL_AGENCY_VERSION
                or not all(_ref(x) for x in (
                    self.assessment_ref, self.intent_ref, self.life_id,
                    self.goal_ref, self.option_ref, self.command_hash,
                    self.goal_measure, self.action_primitive,
                ))
                or type(self.sent_world_step) is not int
                or self.sent_world_step < 1
                or type(self.observe_world_step) is not int
                or self.observe_world_step != self.sent_world_step + 1
                or not isinstance(self.start_position, tuple)
                or len(self.start_position) != 2
                or any(type(x) is not int for x in self.start_position)
                or self.mechanism not in ("ingested_from_inventory", "unresolved")
                or (self.action_target is not None and not _ref(self.action_target))
                or (self.inventory_before is not None
                    and (type(self.inventory_before) is not int
                         or self.inventory_before < 0))):
            raise ValueError("invalid first-person goal-agency commitment")
        if self.mechanism == "ingested_from_inventory" and (
            self.goal_measure != "food" or self.action_primitive != "manger"
            or self.action_target not in ("berry_a", "berry_b")
            or self.inventory_before is None or self.inventory_before < 1
        ):
            raise ValueError("goal agency mechanism not connected to food goal")

    def as_dict(self) -> dict[str, object]:
        return {
            **{k: getattr(self, k) for k in self.__dataclass_fields__
               if k != "start_position"},
            "start_position": list(self.start_position),
        }

    @classmethod
    def from_dict(cls, raw: object) -> "GoalAgencyCommitment":
        if type(raw) is not dict or set(raw) != set(cls.__dataclass_fields__):
            raise ValueError("invalid serialized goal agency commitment")
        if type(raw.get("start_position")) is not list:
            raise ValueError("invalid first-person position")
        data = {**raw, "start_position": tuple(raw["start_position"])}
        value = cls(**data)
        value.validate()
        return value


@dataclass(frozen=True, slots=True)
class GoalAgencyJudgement:
    assessment_ref: str
    intent_ref: str
    life_id: str
    sent_world_step: int
    observed_world_step: int
    subjective_agency: str
    reason: str
    cue_ref: str | None
    policy_version: str = GOAL_AGENCY_VERSION

    def validate(self) -> None:
        if (self.policy_version != GOAL_AGENCY_VERSION
                or not all(_ref(x) for x in (
                    self.assessment_ref, self.intent_ref, self.life_id,
                    self.reason,
                ))
                or self.subjective_agency not in (
                    "self", "world", "unknown", "unavailable",
                )
                or type(self.sent_world_step) is not int
                or self.sent_world_step < 1
                or type(self.observed_world_step) is not int
                or self.observed_world_step <= self.sent_world_step
                or (self.cue_ref is not None and not _ref(self.cue_ref))
                or (self.subjective_agency in ("self", "world", "unknown")
                    and self.cue_ref is None)
                or (self.subjective_agency == "unavailable"
                    and self.cue_ref is not None)):
            raise ValueError("invalid subjective goal-agency judgement")

    def as_dict(self) -> dict[str, object]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, raw: object) -> "GoalAgencyJudgement":
        if type(raw) is not dict or set(raw) != set(cls.__dataclass_fields__):
            raise ValueError("invalid immutable goal agency judgement image")
        judgement = cls(**raw)
        judgement.validate()
        return judgement


class GoalAgencyService:
    """Action Control's opt-in, versioned *owner-local* first-person service.

    A direct, goal-relevant ingestion cue is currently the only supported
    self-mechanism. No available first-person cue can safely justify `world`
    for the existing strict-body-gain criteria; other situations return
    explicit unknown. The vocabulary includes world for future *proven*
    cue policies, not as an invitation to infer blame from failure.
    """

    schema = GOAL_AGENCY_VERSION

    def __init__(self) -> None:
        self._pending: GoalAgencyCommitment | None = None
        self._seen: set[str] = set()
        self._last_sent = 0
        self._last_judgement: GoalAgencyJudgement | None = None

    @property
    def pending(self) -> GoalAgencyCommitment | None:
        return self._pending

    @property
    def last_judgement(self) -> GoalAgencyJudgement | None:
        return self._last_judgement

    def preregister(
        self, *, assessment_ref: str, intent_ref: str, life_id: str,
        goal_ref: str, option_ref: str, command_hash: str,
        world_step: int, measure: str, command: PrimitiveCommand,
        capture: PerceptualCapture,
    ) -> GoalAgencyCommitment:
        if capture.t_monde != world_step:
            raise ValueError("agency precommit needs same lived capture")
        if self._pending is not None or world_step <= self._last_sent:
            raise ValueError("duplicate or unclosed subjective agency assessment")
        target = command.parameters.get("target")
        if target is not None and type(target) is not str:
            raise ValueError("invalid efferent target")
        original = None
        mechanism = "unresolved"
        if (measure == "food" and command.primitive == "manger"
                and target in ("berry_a", "berry_b")):
            amount = capture.inventory.get(target)
            if type(amount) is int and amount >= 1:
                original = amount
                mechanism = "ingested_from_inventory"
        value = GoalAgencyCommitment(
            assessment_ref=assessment_ref, intent_ref=intent_ref,
            life_id=life_id, goal_ref=goal_ref, option_ref=option_ref,
            command_hash=command_hash, sent_world_step=world_step,
            observe_world_step=world_step + 1, goal_measure=measure,
            action_primitive=command.primitive, action_target=target,
            start_position=(capture.x, capture.y),
            inventory_before=original, mechanism=mechanism,
        )
        value.validate()
        if value.assessment_ref in self._seen:
            raise ValueError("duplicate subjective agency reference")
        self._pending = value
        self._seen.add(value.assessment_ref)
        self._last_sent = world_step
        return value

    def evaluate(
        self, *, capture: PerceptualCapture | None,
        world_step: int, cue_ref: str | None, paid: bool,
    ) -> GoalAgencyJudgement | None:
        commitment = self._pending
        if commitment is None or world_step <= commitment.sent_world_step:
            return None
        if type(world_step) is not int or world_step < 1:
            raise ValueError("invalid subjective agency time")
        if (capture is not None
                and (not isinstance(capture, PerceptualCapture)
                     or capture.t_monde != world_step)):
            raise ValueError("invalid first-person capture")
        if paid and capture is not None and not _ref(cue_ref):
            raise ValueError("paid judgement needs original observed cue receipt")
        agency, reason = "unknown", "no_distinct_goal_relevant_agency_cue"
        if (not paid or capture is None
                or world_step != commitment.observe_world_step):
            agency, reason = "unavailable", (
                "agency_uc_refused" if not paid else "agency_observation_missed"
            )
        elif commitment.mechanism == "ingested_from_inventory":
            after = capture.inventory.get(commitment.action_target)
            if (type(after) is int
                    and after == commitment.inventory_before - 1
                    and (capture.x, capture.y) == commitment.start_position):
                agency, reason = "self", "witnessed_goal_relevant_inventory_decrement"
            else:
                reason = "ingestion_cue_absent_or_confounded"
        value = GoalAgencyJudgement(
            assessment_ref=commitment.assessment_ref,
            intent_ref=commitment.intent_ref,
            life_id=commitment.life_id,
            sent_world_step=commitment.sent_world_step,
            observed_world_step=world_step, subjective_agency=agency,
            reason=reason, cue_ref=cue_ref if agency != "unavailable" else None,
        )
        value.validate()
        self._pending = None
        self._last_judgement = value
        return value

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "last_judgement": (None if self._last_judgement is None
                               else self._last_judgement.as_dict()),
            "pending_commitment": (
                None if self._pending is None else self._pending.as_dict()
            ),
            "seen_assessment_refs": sorted(self._seen),
            "last_registered_world_step": self._last_sent,
        }

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict or set(state) != {
            "schema", "pending_commitment", "seen_assessment_refs",
            "last_judgement",
            "last_registered_world_step",
        } or state["schema"] != self.schema
                or type(state["seen_assessment_refs"]) is not list
                or type(state["last_registered_world_step"]) is not int
                or state["last_registered_world_step"] < 0):
            raise ValueError("invalid Action Control agency custody")
        seen = state["seen_assessment_refs"]
        if (any(not _ref(v) for v in seen)
                or seen != sorted(set(seen))):
            raise ValueError("invalid unique agency references")
        pending = state["pending_commitment"]
        candidate = (None if pending is None
                     else GoalAgencyCommitment.from_dict(pending))
        last = (None if state["last_judgement"] is None
                else GoalAgencyJudgement.from_dict(state["last_judgement"]))
        if last is not None and (last.assessment_ref not in seen
                                or last.sent_world_step > state["last_registered_world_step"]):
            raise ValueError("subjective agency last judgement contradicts ledger")
        if candidate is not None and (
            candidate.assessment_ref not in seen
            or candidate.sent_world_step != state["last_registered_world_step"]
        ):
            raise ValueError("pending agency does not match persisted owner")
        if (bool(seen) != (state["last_registered_world_step"] > 0)
                or self._pending is not None or self._seen or self._last_sent
                or self._last_judgement is not None):
            raise ValueError("historic Action Control agency restore prohibited")
        self._pending, self._seen, self._last_sent = (
            candidate, set(seen), state["last_registered_world_step"],
        )
        self._last_judgement = last
