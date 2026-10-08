"""Minimal Stage-4 Value and Needs owner.

No learning is active at Stage 4. This module owns setpoints/need weights and
computes homeostatic deviation, reward, need alerts and goal proposals.

Spec: 7.1-7.4, DC-03, 20.3 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.contracts import Contribution, GoalProposal


BODY_VARIABLES = ("energy", "food", "water", "integrity")


@dataclass(frozen=True, slots=True)
class ValueNeedsConfig:
    version: str
    setpoints: Mapping[str, float]
    weights: Mapping[str, float]
    normalization_scales: Mapping[str, float]
    p_min: float
    contribution_ttl_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Value/Needs config version must not be empty")
        for name in BODY_VARIABLES:
            if name not in self.setpoints:
                raise ValueError(f"missing setpoint for {name}")
            if name not in self.weights:
                raise ValueError(f"missing need weight for {name}")
            if name not in self.normalization_scales:
                raise ValueError(f"missing normalization scale for {name}")
            if self.weights[name] < 0:
                raise ValueError("need weights must be non-negative")
            if self.normalization_scales[name] <= 0:
                raise ValueError("normalization scales must be > 0")
        if not 0.0 < self.p_min < 1.0:
            raise ValueError("p_min must lie in ]0,1[")
        if self.contribution_ttl_steps < 1:
            raise ValueError("contribution TTL must be >= 1")


@dataclass(frozen=True, slots=True)
class NeedState:
    body: Mapping[str, float]
    deficits: Mapping[str, float]
    pressures: Mapping[str, float]
    deviation: float


class ValueAndNeeds:
    owner_id = "value_and_needs"

    def __init__(self, config: ValueNeedsConfig) -> None:
        config.validate()
        self._config = config
        self._previous_deviation: float | None = None
        self._last_state: NeedState | None = None

    @property
    def config(self) -> ValueNeedsConfig:
        return self._config

    @staticmethod
    def _clip01(value: float) -> float:
        return max(0.0, min(1.0, value))

    def assess(self, telemetry: Mapping[str, float]) -> NeedState:
        body = {name: float(telemetry[name]) for name in BODY_VARIABLES}
        deficits = {
            name: self._clip01(
                (self._config.setpoints[name] - body[name])
                / self._config.normalization_scales[name]
            )
            for name in BODY_VARIABLES
        }

        max_weight = max(self._config.weights.values(), default=0.0)
        if max_weight <= 0:
            normalized_weights = {name: 0.0 for name in BODY_VARIABLES}
        else:
            normalized_weights = {
                name: self._config.weights[name] / max_weight
                for name in BODY_VARIABLES
            }

        pressures = {
            name: self._clip01(normalized_weights[name] * deficits[name])
            for name in BODY_VARIABLES
        }
        deviation = sum(
            self._config.weights[name]
            * abs(body[name] - self._config.setpoints[name])
            for name in BODY_VARIABLES
        )
        state = NeedState(
            body=body,
            deficits=deficits,
            pressures=pressures,
            deviation=deviation,
        )
        self._last_state = state
        return state

    def reward_for(self, state: NeedState) -> float:
        if self._previous_deviation is None:
            reward = 0.0
        else:
            reward = self._previous_deviation - state.deviation
        self._previous_deviation = state.deviation
        return reward

    def produce(
        self,
        *,
        state: NeedState,
        t_monde: int,
        cycle: int,
    ) -> tuple[tuple[Contribution, ...], tuple[GoalProposal, ...]]:
        alerts: list[Contribution] = []
        proposals: list[GoalProposal] = []

        for name in BODY_VARIABLES:
            pressure = state.pressures[name]
            if pressure < self._config.p_min:
                continue

            contribution_id = f"need-alert:{name}:{t_monde}:{cycle}"
            alerts.append(
                Contribution(
                    id=contribution_id,
                    schema_version="mvp-v1.2.1",
                    type="alert",
                    summary=f"{name} below setpoint",
                    subject_ref=f"body:{name}",
                    emitter_module="value_needs",
                    signal_family="value_needs",
                    confidence=1.0,
                    urgency=pressure,
                    risk=pressure if name == "integrity" else 0.0,
                    value=0.0,
                    production_t=t_monde,
                    production_cycle=cycle,
                    expires_at_step=t_monde + self._config.contribution_ttl_steps,
                    payload={
                        "condition": f"{name}_below_setpoint",
                        "severity": pressure,
                        "reflex_taken": False,
                        "ack_required": False,
                    },
                    signal_ids=(f"body-telemetry:{name}:{t_monde}",),
                )
            )
            proposals.append(
                GoalProposal(
                    id=f"goal-proposal:{name}:{t_monde}:{cycle}",
                    source="value_needs",
                    goal_type={
                        "energy": "recover_energy",
                        "food": "eat",
                        "water": "drink",
                        "integrity": "restore_integrity",
                    }[name],
                    target=name,
                    base_pressure=pressure,
                    current_pressure=pressure,
                    justification_ref=contribution_id,
                    t_monde=t_monde,
                    cycle=cycle,
                    rule_version=self._config.version,
                )
            )

        for alert in alerts:
            alert.validate()
        for proposal in proposals:
            proposal.validate()
        return tuple(alerts), tuple(proposals)

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "previous_deviation": self._previous_deviation,
            "last_state": None
            if self._last_state is None
            else {
                "body": dict(self._last_state.body),
                "deficits": dict(self._last_state.deficits),
                "pressures": dict(self._last_state.pressures),
                "deviation": self._last_state.deviation,
            },
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Value/Needs state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Value/Needs config version mismatch")
        previous = state.get("previous_deviation")
        self._previous_deviation = None if previous is None else float(previous)
        raw = state.get("last_state")
        if raw is None:
            self._last_state = None
        elif isinstance(raw, Mapping):
            self._last_state = NeedState(
                body=dict(raw["body"]),
                deficits=dict(raw["deficits"]),
                pressures=dict(raw["pressures"]),
                deviation=float(raw["deviation"]),
            )
        else:
            raise ValueError("invalid Value/Needs last_state")
