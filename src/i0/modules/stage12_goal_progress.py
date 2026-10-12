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


class Stage12GoalProgressLedger:
    """One pending pre-action criterion in the canonical Metacognition owner.

    The same submitted identifier or physical time cannot be counted twice.
    A missed next-step perception or refused diagnostic UC yields UNKNOWN,
    never an inferred failure. No Stage9 prediction or attribution is read.
    """

    def __init__(self) -> None:
        self._pending: LivedGoalProgressIntent | None = None
        self._last_registered_world_step = 0
        self._registered_refs: set[str] = set()

    @property
    def pending(self) -> LivedGoalProgressIntent | None:
        return self._pending

    def preregister(self, intent: LivedGoalProgressIntent) -> None:
        if type(intent) is not LivedGoalProgressIntent:
            raise TypeError("lived goal-progress intent required")
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
    ) -> LivedGoalProgressFollowup | None:
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
            "schema": CONTRACT_VERSION,
            "pending_intent": None if self._pending is None else self._pending.as_dict(),
            "last_registered_world_step": self._last_registered_world_step,
            "registered_intent_refs": sorted(self._registered_refs),
        }
