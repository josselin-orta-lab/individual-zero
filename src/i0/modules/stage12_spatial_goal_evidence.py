"""GA-08: pure spatial evidence, not a new mutable owner or journal reader.

Action Control and Metacognition must separately invoke their corresponding
functions on legally sourced paid captures. The prototype cannot establish
that a command actually executed; the runtime must supply that provenance.
"""
from __future__ import annotations
from dataclasses import dataclass
from i0.interfaces import PrimitiveCommand
from .perception import PerceptualCapture

SPATIAL_CONTRACT_VERSION = "stage12-spatial-subcriterion-ga08-v1"
DIRECTIONS = {"north": (0, -1), "south": (0, 1),
              "east": (1, 0), "west": (-1, 0)}


@dataclass(frozen=True, slots=True)
class SpatialGoalPrecommit:
    life_id: str
    intent_ref: str
    assessment_ref: str
    goal_ref: str
    option_ref: str
    command_hash: str
    sent_world_step: int
    origin: tuple[int, int]
    target: tuple[int, int]
    direction: str
    target_kind: str
    distance_before: int
    destination_passable_before: bool
    policy_version: str = SPATIAL_CONTRACT_VERSION

    def validate(self) -> None:
        if (self.policy_version != SPATIAL_CONTRACT_VERSION
                or any(type(x) is not str or not x for x in (
                    self.life_id, self.intent_ref, self.assessment_ref,
                    self.goal_ref, self.option_ref, self.command_hash,
                ))
                or type(self.sent_world_step) is not int
                or self.sent_world_step < 1
                or self.direction not in DIRECTIONS
                or self.target_kind not in ("water", "food")
                or type(self.origin) is not tuple or len(self.origin) != 2
                or type(self.target) is not tuple or len(self.target) != 2
                or any(type(v) is not int for v in self.origin + self.target)
                or type(self.destination_passable_before) is not bool
                or type(self.distance_before) is not int
                or self.distance_before != 1
                or tuple(
                    self.origin[i] + DIRECTIONS[self.direction][i]
                    for i in range(2)
                ) != self.target):
            raise ValueError("invalid or ungrounded GA-08 spatial precommit")

    def as_dict(self) -> dict[str, object]:
        """Canonical owner-image payload, without introducing a second owner."""
        self.validate()
        return {
            name: (list(value) if name in ("origin", "target") else value)
            for name, value in (
                (name, getattr(self, name)) for name in self.__dataclass_fields__
            )
        }

    @classmethod
    def from_dict(cls, state: object) -> "SpatialGoalPrecommit":
        """Reject altered current-generation images before any installation."""
        if (type(state) is not dict
                or set(state) != set(cls.__dataclass_fields__)
                or any(type(state[name]) is not list
                       for name in ("origin", "target"))):
            raise ValueError("invalid GA-08 persisted precommit image")
        value = cls(**{
            **state,
            "origin": tuple(state["origin"]),
            "target": tuple(state["target"]),
        })
        value.validate()
        if value.as_dict() != state:
            raise ValueError("noncanonical GA-08 persisted precommit")
        return value


@dataclass(frozen=True, slots=True)
class SpatialGoalOutcome:
    intent_ref: str
    observed_world_step: int
    outcome: str
    reason: str
    observed_distance: int | None


@dataclass(frozen=True, slots=True)
class SpatialSubjectiveJudgement:
    assessment_ref: str
    observed_world_step: int
    agency: str
    reason: str


def preregister_spatial_subgoal(
    *, life_id: str, intent_ref: str, assessment_ref: str,
    goal_ref: str, option_ref: str, command_hash: str,
    goal_measure: str, command: PrimitiveCommand,
    capture: PerceptualCapture,
) -> SpatialGoalPrecommit | None:
    """Only a locally witnessed target can support the new subcriterion.

    The caller must separately prove the active_goal motive and admission.
    Unknown target or exploratory command -> no precommit.
    """
    if goal_measure not in ("water", "food") or command.primitive != "se_deplacer":
        return None
    direction = command.parameters.get("direction")
    if type(direction) is not str or direction not in DIRECTIONS:
        return None
    cells = [c for c in capture.adjacent if c.direction == direction]
    if len(cells) != 1:
        return None
    cell = cells[0]
    kind = ("water" if cell.water_source else
            "food" if any(k in ("berry_a", "berry_b")
                          for k in cell.resources) else None)
    if kind != goal_measure:
        return None
    origin = (capture.x, capture.y)
    target = (cell.x, cell.y)
    if target != tuple(origin[i] + DIRECTIONS[direction][i] for i in range(2)):
        return None
    result = SpatialGoalPrecommit(
        life_id=life_id, intent_ref=intent_ref,
        assessment_ref=assessment_ref, goal_ref=goal_ref,
        option_ref=option_ref, command_hash=command_hash,
        sent_world_step=capture.t_monde, origin=origin, target=target,
        direction=direction, target_kind=kind,
        distance_before=1, destination_passable_before=cell.passable,
    )
    result.validate()
    return result


def evaluate_spatial_goal_outcome(
    precommit: SpatialGoalPrecommit, *, capture: PerceptualCapture | None,
    world_step: int, diagnostic_paid: bool,
) -> SpatialGoalOutcome:
    """Metacognition: bounded progress, without reading agency."""
    precommit.validate()
    if type(world_step) is not int or world_step <= precommit.sent_world_step:
        raise ValueError("spatial follow-up cannot precede action")
    if not diagnostic_paid or capture is None or world_step != precommit.sent_world_step + 1:
        return SpatialGoalOutcome(
            intent_ref=precommit.intent_ref, observed_world_step=world_step,
            outcome="unknown", reason="unavailable_or_late_observation",
            observed_distance=None,
        )
    if capture.t_monde != world_step:
        raise ValueError("spatial capture time mismatch")
    distance = abs(capture.x - precommit.target[0]) + abs(
        capture.y - precommit.target[1]
    )
    improved = distance < precommit.distance_before
    return SpatialGoalOutcome(
        intent_ref=precommit.intent_ref, observed_world_step=world_step,
        outcome="success" if improved else "failure",
        reason=("strict_perceptual_distance_decrease" if improved
                else "no_strict_perceptual_distance_decrease"),
        observed_distance=distance,
    )


def judge_spatial_agency(
    precommit: SpatialGoalPrecommit, *, capture: PerceptualCapture | None,
    world_step: int, agency_paid: bool, physically_applied: bool,
) -> SpatialSubjectiveJudgement:
    """Action Control: first-person judgement, without reading outcome/P-47.

    Applied command must be authenticated by the actual owner and later
    validated by a separate external audit, never by this pure function.
    """
    precommit.validate()
    if type(world_step) is not int or world_step <= precommit.sent_world_step:
        raise ValueError("agency judgement cannot precede action")
    if not agency_paid or not physically_applied or capture is None or world_step != precommit.sent_world_step + 1:
        return SpatialSubjectiveJudgement(
            precommit.assessment_ref, world_step, "unavailable",
            "missing_paid_applied_lived_capture",
        )
    if capture.t_monde != world_step:
        raise ValueError("agency perception time mismatch")
    observed = (capture.x, capture.y)
    if precommit.destination_passable_before and observed == precommit.target:
        agency, reason = "self", "witnessed_goal_relevant_efferent_displacement"
    elif not precommit.destination_passable_before and observed == precommit.origin:
        agency, reason = "world", "witnessed_goal_relevant_blocked_destination"
    else:
        agency, reason = "unknown", "ambiguous_or_confounded_spatial_cue"
    return SpatialSubjectiveJudgement(
        precommit.assessment_ref, world_step, agency, reason,
    )
