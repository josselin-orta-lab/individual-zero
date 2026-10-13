"""Stage12 pre-action lived goal-progress contracts, never P-47 outcomes.

An issued criterion is the *one-step increase* of an accessible body measure
for a goal-motivated, admitted command. A success means that this criterion
was met on the next lived perception, NOT that the overall goal was achieved,
and NOT that the agent caused the gain. Source judgement of self/world agency
is separate and remains unavailable until independently supported.
No Lab, journal, Oracle, Bench or WorldBody dependency is permitted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .perception import PerceptualCapture
from .stage12_spatial_goal_evidence import (
    SPATIAL_CONTRACT_VERSION, SpatialGoalPrecommit,
    evaluate_spatial_goal_outcome,
)


ALLOWED_MEASURES = frozenset({"water", "food", "energy", "integrity"})
CONTRACT_VERSION = "stage12-lived-goal-progress-one-step-v1"


def _measurement(value: object) -> float | None:
    if type(value) not in (int, float):
        return None
    try:
        number = float(value)
    except (OverflowError, ValueError):
        return None
    return number if isfinite(number) and number >= 0 else None


@dataclass(frozen=True, slots=True)
class LivedGoalProgressIntent:
    intent_ref: str
    goal_ref: str
    option_ref: str
    command_hash: str
    measure: str
    value_before: float
    sent_world_step: int
    observe_world_step: int
    contract_version: str = CONTRACT_VERSION

    def validate(self) -> None:
        if (self.contract_version != CONTRACT_VERSION
                or type(self.measure) is not str
                or self.measure not in ALLOWED_MEASURES
                or type(self.sent_world_step) is not int
                or self.sent_world_step < 1
                or type(self.observe_world_step) is not int
                or self.observe_world_step != self.sent_world_step + 1
                or any(type(ref) is not str or not ref for ref in (
                    self.intent_ref, self.goal_ref, self.option_ref,
                    self.command_hash,
                ))
                or _measurement(self.value_before) is None):
            raise ValueError("invalid preregistered lived goal-progress criterion")

    def as_dict(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class LivedGoalProgressFollowup:
    intent_ref: str
    sent_world_step: int
    observed_world_step: int
    measure: str
    value_before: float
    value_after: float | None
    criterion_outcome: str
    reason: str
    contract_version: str = CONTRACT_VERSION

    def as_dict(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class LivedSpatialGoalProgressFollowup:
    """Spatial goal result, independent of the subjective agency judgement."""
    intent_ref: str
    sent_world_step: int
    observed_world_step: int
    measure: str
    value_before: float
    value_after: int | None
    criterion_outcome: str
    reason: str
    contract_version: str = SPATIAL_CONTRACT_VERSION

    def as_dict(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


class Stage12GoalProgressLedger:
    """One pending pre-action criterion in the canonical Metacognition owner.

    The same submitted identifier or physical time cannot be counted twice.
    A missed next-step perception or refused diagnostic UC yields UNKNOWN,
    never an inferred failure. No Stage9 prediction or attribution is read.
    """

    def __init__(self) -> None:
        self._pending: LivedGoalProgressIntent | SpatialGoalPrecommit | None = None
        self._spatial_enabled = False
        self._last_registered_world_step = 0
        self._registered_refs: set[str] = set()

    def enable_spatial(self) -> None:
        """Birth-only opt-in; state remains owned by this existing ledger."""
        if (self._spatial_enabled or self._pending is not None
                or self._registered_refs or self._last_registered_world_step):
            raise ValueError("GA-08 cannot be enabled after cognitive history")
        self._spatial_enabled = True

    @property
    def pending(self) -> LivedGoalProgressIntent | SpatialGoalPrecommit | None:
        return self._pending

    def preregister(
        self, intent: LivedGoalProgressIntent | SpatialGoalPrecommit,
    ) -> None:
        if (type(intent) is not LivedGoalProgressIntent
                and not (self._spatial_enabled and type(intent) is SpatialGoalPrecommit)):
            raise TypeError("authorized lived body/spatial goal-progress intent required")
        intent.validate()
        if (self._pending is not None
                or intent.sent_world_step <= self._last_registered_world_step
                or intent.intent_ref in self._registered_refs):
            raise ValueError("duplicated or unclosed goal-progress intention")
        self._pending = intent
        self._last_registered_world_step = intent.sent_world_step
        self._registered_refs.add(intent.intent_ref)

    def followup(
        self, *, world_step: int, body: Mapping[str, object] | None,
        diagnostic_paid: bool = True,
        capture: PerceptualCapture | None = None,
    ) -> LivedGoalProgressFollowup | LivedSpatialGoalProgressFollowup | None:
        if type(world_step) is not int or world_step < 1:
            raise ValueError("invalid observed physical time")
        intent = self._pending
        if intent is None or world_step <= intent.sent_world_step:
            return None
        # Malformed incoming observations cannot erase a registered intention.
        # Validate before mutating the one-owner ledger; missing readings
        # remain explicit unknown evidence rather than invented failures.
        if body is not None and not isinstance(body, Mapping):
            raise ValueError("lived goal-progress body must be a mapping or unavailable")
        if capture is not None and not isinstance(capture, PerceptualCapture):
            raise ValueError("invalid spatial lived perception")
        if type(intent) is SpatialGoalPrecommit:
            # Both producers observe the same lived capture, but neither
            # receives the other producer's result. A missed/UC-refused
            # observation is UNKNOWN, never a goal failure.
            value = evaluate_spatial_goal_outcome(
                intent, capture=capture, world_step=world_step,
                diagnostic_paid=diagnostic_paid,
            )
            self._pending = None
            return LivedSpatialGoalProgressFollowup(
                intent_ref=intent.intent_ref,
                sent_world_step=intent.sent_world_step,
                observed_world_step=world_step,
                measure="spatial_distance",
                value_before=float(intent.distance_before),
                value_after=value.observed_distance,
                criterion_outcome=value.outcome,
                reason=value.reason,
            )
        value = None if body is None else _measurement(body.get(intent.measure))
        self._pending = None
        if not diagnostic_paid:
            outcome, reason = "unknown", "diagnostic_uc_not_available"
        elif world_step != intent.observe_world_step:
            outcome, reason = "unknown", "one_step_observation_window_missed"
        elif value is None:
            outcome, reason = "unknown", "lived_measure_unavailable"
        else:
            outcome, reason = (
                ("success", "measured_strict_gain")
                if value > intent.value_before
                else ("failure", "no_measured_strict_gain")
            )
        return LivedGoalProgressFollowup(
            intent_ref=intent.intent_ref,
            sent_world_step=intent.sent_world_step,
            observed_world_step=world_step,
            measure=intent.measure,
            value_before=intent.value_before,
            value_after=value if diagnostic_paid and world_step == intent.observe_world_step else None,
            criterion_outcome=outcome,
            reason=reason,
        )

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": (
                CONTRACT_VERSION + "+ga08" if self._spatial_enabled
                else CONTRACT_VERSION
            ),
            "pending_intent": None if self._pending is None else self._pending.as_dict(),
            "last_registered_world_step": self._last_registered_world_step,
            "registered_intent_refs": sorted(self._registered_refs),
        }

    def restore_causal_state(self, state: object) -> None:
        """Install a fully validated current ledger only into its empty owner.

        This is not a historical rewind of an already published intention.
        M11 prepares it on a fresh never-executed runtime after SQLite
        authenticates the single current generation.
        """
        if (type(state) is not dict
                or set(state) != {"schema", "pending_intent",
                                  "last_registered_world_step", "registered_intent_refs"}
                or state["schema"] != (
                    CONTRACT_VERSION + "+ga08" if self._spatial_enabled
                    else CONTRACT_VERSION
                )
                or type(state["last_registered_world_step"]) is not int
                or state["last_registered_world_step"] < 0
                or type(state["registered_intent_refs"]) is not list):
            raise ValueError("invalid current goal-progress custody")
        refs = state["registered_intent_refs"]
        if (any(type(ref) is not str or not ref for ref in refs)
                or sorted(set(refs)) != refs):
            raise ValueError("invalid distinct goal-progress intention references")
        raw = state["pending_intent"]
        pending = None
        if raw is not None:
            if (self._spatial_enabled and type(raw) is dict
                    and raw.get("policy_version") == SPATIAL_CONTRACT_VERSION):
                pending = SpatialGoalPrecommit.from_dict(raw)
            else:
                if (type(raw) is not dict
                        or set(raw) != set(LivedGoalProgressIntent.__dataclass_fields__)):
                    raise ValueError("invalid current goal-progress intent")
                pending = LivedGoalProgressIntent(**raw)
                pending.validate()
            if (pending.intent_ref not in refs
                    or pending.sent_world_step != state["last_registered_world_step"]):
                raise ValueError("pending goal-progress intent ledger differs")
        if ((refs and state["last_registered_world_step"] < 1)
                or (not refs and state["last_registered_world_step"] != 0)
                or self._pending is not None or self._registered_refs
                or self._last_registered_world_step != 0):
            raise ValueError("goal-progress historic rewind forbidden")
        self._pending = pending
        self._last_registered_world_step = state["last_registered_world_step"]
        self._registered_refs = set(refs)
