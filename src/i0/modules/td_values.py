"""Stage-8 online option values with TD eligibility traces.

The store is owned by Value and Needs. It contains only Q_active; the
consolidated form remains the immutable birth-zero form until Stage 10.

Spec: 11.1, DC-15, P-30 to P-32, INV-07, INV-16.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import tanh
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ValueFeatureConfig:
    version: str
    feature_names: tuple[str, ...]
    position_scale_x: float
    position_scale_y: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("feature schema version must not be empty")
        if not self.feature_names:
            raise ValueError("feature schema must contain at least one feature")
        if len(set(self.feature_names)) != len(self.feature_names):
            raise ValueError("feature names must be unique")
        if self.position_scale_x <= 0 or self.position_scale_y <= 0:
            raise ValueError("position feature scales must be > 0")


@dataclass(frozen=True, slots=True)
class TDLearningConfig:
    version: str
    eta: float
    lambda_e: float
    beta: float
    evidence_scale: float
    features: ValueFeatureConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("TD config version must not be empty")
        if self.eta <= 0:
            raise ValueError("eta must be > 0")
        if not 0.0 <= self.lambda_e <= 1.0:
            raise ValueError("lambda_e must lie in [0,1]")
        if not 0.0 < self.beta < 1.0:
            raise ValueError("beta must lie in ]0,1[")
        if self.evidence_scale <= 0:
            raise ValueError("Q evidence scale must be > 0")
        self.features.validate()


@dataclass(frozen=True, slots=True)
class EvaluationState:
    body: Mapping[str, float]
    x: int
    y: int
    active_goal_type: str | None
    temporal_context: str

    def validate(self) -> None:
        for key in ("energy", "food", "water", "integrity"):
            if key not in self.body:
                raise ValueError(f"evaluation state missing body variable {key}")
        if self.temporal_context not in {"day", "night"}:
            raise ValueError("temporal context must be day or night")


@dataclass(frozen=True, slots=True)
class PendingTDSegment:
    decision_t_monde: int
    state: EvaluationState
    signature: str
    rewards: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class LearnedValue:
    signature: str
    status: str
    value: float | None
    evidence: float | None
    update_count: int


@dataclass(frozen=True, slots=True)
class TDUpdate:
    previous_signature: str
    next_signature: str
    segment_length: int
    return_g: float
    q_previous: float
    q_next: float
    delta: float
    updated_signatures: tuple[str, ...]


class LinearTDValues:
    """Inspectable linear Q_active indexed by learning signature."""

    def __init__(self, config: TDLearningConfig) -> None:
        config.validate()
        self._config = config
        self._weights: dict[str, list[float]] = {}
        self._traces: dict[str, list[float]] = {}
        self._update_counts: dict[str, int] = {}
        self._pending: PendingTDSegment | None = None

    @property
    def config(self) -> TDLearningConfig:
        return self._config


    @property
    def pending_segment(self) -> PendingTDSegment | None:
        return self._pending

    def arrive_decision(
        self,
        *,
        state: EvaluationState,
        signature: str,
        t_monde: int,
    ) -> TDUpdate | None:
        state.validate()
        if t_monde < 0:
            raise ValueError("decision world step must be non-negative")

        update = None
        if self._pending is not None:
            expected_length = t_monde - self._pending.decision_t_monde
            if expected_length < 1:
                raise ValueError("successive cognitive decisions must advance world time")
            if len(self._pending.rewards) != expected_length:
                raise ValueError(
                    "TD segment reward count does not match decision spacing"
                )
            update = self.update_segment(
                previous_state=self._pending.state,
                previous_signature=self._pending.signature,
                rewards=self._pending.rewards,
                next_state=state,
                next_signature=signature,
            )

        self._pending = PendingTDSegment(
            decision_t_monde=t_monde,
            state=state,
            signature=signature,
            rewards=(),
        )
        return update

    def append_experienced_reward(self, reward: float) -> None:
        if self._pending is None:
            return
        self._pending = PendingTDSegment(
            decision_t_monde=self._pending.decision_t_monde,
            state=self._pending.state,
            signature=self._pending.signature,
            rewards=self._pending.rewards + (float(reward),),
        )

    def close_experienced_terminal(self) -> TDUpdate | None:
        if self._pending is None:
            return None
        if not self._pending.rewards:
            raise ValueError("terminal segment has no experienced reward")
        update = self.update_terminal(
            previous_state=self._pending.state,
            previous_signature=self._pending.signature,
            rewards=self._pending.rewards,
        )
        self._pending = None
        return update

    def external_stop(self) -> None:
        """Protocol stop: no synthetic terminal update (DC-15)."""
        self._pending = None

    @property
    def consolidated_birth_form(self) -> Mapping[str, tuple[float, ...]]:
        """Stage-8 consolidated form is the immutable zero/birth form."""
        return {}

    def _zero_vector(self) -> list[float]:
        return [0.0] * len(self._config.features.feature_names)

    def features(self, state: EvaluationState) -> tuple[float, ...]:
        state.validate()
        body = state.body
        available = {
            "bias": 1.0,
            "energy": float(body["energy"]) / 100.0,
            "food": float(body["food"]) / 100.0,
            "water": float(body["water"]) / 100.0,
            "integrity": float(body["integrity"]) / 100.0,
            "x": float(state.x) / self._config.features.position_scale_x,
            "y": float(state.y) / self._config.features.position_scale_y,
            "is_night": 1.0 if state.temporal_context == "night" else 0.0,
            "goal_drink": 1.0 if state.active_goal_type == "drink" else 0.0,
            "goal_eat": 1.0 if state.active_goal_type == "eat" else 0.0,
            "goal_recover_energy": (
                1.0 if state.active_goal_type == "recover_energy" else 0.0
            ),
            "goal_restore_integrity": (
                1.0 if state.active_goal_type == "restore_integrity" else 0.0
            ),
        }
        unknown = [
            name for name in self._config.features.feature_names
            if name not in available
        ]
        if unknown:
            raise ValueError(
                "unknown P-32 feature(s): " + ", ".join(sorted(unknown))
            )
        return tuple(available[name] for name in self._config.features.feature_names)

    def _weights_for(self, signature: str) -> list[float]:
        return self._weights.setdefault(signature, self._zero_vector())

    def q(self, state: EvaluationState, signature: str) -> float:
        phi = self.features(state)
        weights = self._weights_for(signature)
        return sum(weight * feature for weight, feature in zip(weights, phi))

    def learned_value(
        self,
        state: EvaluationState,
        signature: str,
    ) -> LearnedValue:
        count = self._update_counts.get(signature, 0)
        if count <= 0:
            return LearnedValue(
                signature=signature,
                status="unlearned",
                value=None,
                evidence=None,
                update_count=0,
            )
        value = self.q(state, signature)
        return LearnedValue(
            signature=signature,
            status="learned",
            value=value,
            evidence=tanh(value / self._config.evidence_scale),
            update_count=count,
        )

    def update_segment(
        self,
        *,
        previous_state: EvaluationState,
        previous_signature: str,
        rewards: Sequence[float],
        next_state: EvaluationState,
        next_signature: str,
    ) -> TDUpdate:
        if not rewards:
            raise ValueError("TD segment must contain at least one reward")
        length = len(rewards)
        beta = self._config.beta
        return_g = sum(
            (beta ** index) * float(reward)
            for index, reward in enumerate(rewards)
        )
        q_previous = self.q(previous_state, previous_signature)
        q_next = self.q(next_state, next_signature)
        delta = (
            return_g
            + (beta ** length) * q_next
            - q_previous
        )

        decay = (beta * self._config.lambda_e) ** length
        for signature in list(self._traces):
            self._traces[signature] = [
                decay * value for value in self._traces[signature]
            ]

        phi = self.features(previous_state)
        trace = self._traces.setdefault(
            previous_signature,
            self._zero_vector(),
        )
        self._traces[previous_signature] = [
            old + feature for old, feature in zip(trace, phi)
        ]

        updated = []
        for signature in sorted(self._traces):
            eligibility = self._traces[signature]
            weights = self._weights_for(signature)
            if not any(eligibility):
                continue
            self._weights[signature] = [
                weight + self._config.eta * delta * z
                for weight, z in zip(weights, eligibility)
            ]
            self._update_counts[signature] = (
                self._update_counts.get(signature, 0) + 1
            )
            updated.append(signature)

        return TDUpdate(
            previous_signature=previous_signature,
            next_signature=next_signature,
            segment_length=length,
            return_g=return_g,
            q_previous=q_previous,
            q_next=q_next,
            delta=delta,
            updated_signatures=tuple(updated),
        )

    def update_terminal(
        self,
        *,
        previous_state: EvaluationState,
        previous_signature: str,
        rewards: Sequence[float],
    ) -> TDUpdate:
        if not rewards:
            raise ValueError("terminal TD segment must contain rewards")
        length = len(rewards)
        beta = self._config.beta
        return_g = sum(
            (beta ** index) * float(reward)
            for index, reward in enumerate(rewards)
        )
        q_previous = self.q(previous_state, previous_signature)
        delta = return_g - q_previous

        decay = (beta * self._config.lambda_e) ** length
        for signature in list(self._traces):
            self._traces[signature] = [
                decay * value for value in self._traces[signature]
            ]
        phi = self.features(previous_state)
        trace = self._traces.setdefault(
            previous_signature,
            self._zero_vector(),
        )
        self._traces[previous_signature] = [
            old + feature for old, feature in zip(trace, phi)
        ]

        updated = []
        for signature in sorted(self._traces):
            eligibility = self._traces[signature]
            weights = self._weights_for(signature)
            if not any(eligibility):
                continue
            self._weights[signature] = [
                weight + self._config.eta * delta * z
                for weight, z in zip(weights, eligibility)
            ]
            self._update_counts[signature] = (
                self._update_counts.get(signature, 0) + 1
            )
            updated.append(signature)

        return TDUpdate(
            previous_signature=previous_signature,
            next_signature="<terminal>",
            segment_length=length,
            return_g=return_g,
            q_previous=q_previous,
            q_next=0.0,
            delta=delta,
            updated_signatures=tuple(updated),
        )

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "feature_version": self._config.features.version,
            "weights": {
                signature: list(values)
                for signature, values in sorted(self._weights.items())
            },
            "traces": {
                signature: list(values)
                for signature, values in sorted(self._traces.items())
            },
            "update_counts": dict(sorted(self._update_counts.items())),
            "pending": None if self._pending is None else {
                "decision_t_monde": self._pending.decision_t_monde,
                "state": {
                    "body": dict(self._pending.state.body),
                    "x": self._pending.state.x,
                    "y": self._pending.state.y,
                    "active_goal_type": self._pending.state.active_goal_type,
                    "temporal_context": self._pending.state.temporal_context,
                },
                "signature": self._pending.signature,
                "rewards": list(self._pending.rewards),
            },
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("TD state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("TD config version mismatch")
        if state.get("feature_version") != self._config.features.version:
            raise ValueError("TD feature version mismatch")

        def vectors(name: str) -> dict[str, list[float]]:
            raw = state.get(name, {})
            if not isinstance(raw, Mapping):
                raise ValueError(f"TD {name} must be a mapping")
            result = {}
            for signature, values in raw.items():
                if not isinstance(values, list):
                    raise ValueError(f"TD {name} vector must be a list")
                if len(values) != len(self._config.features.feature_names):
                    raise ValueError(f"TD {name} vector size mismatch")
                result[str(signature)] = [float(value) for value in values]
            return result

        self._weights = vectors("weights")
        self._traces = vectors("traces")
        raw_counts = state.get("update_counts", {})
        if not isinstance(raw_counts, Mapping):
            raise ValueError("TD update_counts must be a mapping")
        self._update_counts = {
            str(signature): int(count)
            for signature, count in raw_counts.items()
        }

        raw_pending = state.get("pending")
        if raw_pending is None:
            self._pending = None
        elif isinstance(raw_pending, Mapping):
            raw_state = raw_pending.get("state")
            if not isinstance(raw_state, Mapping):
                raise ValueError("TD pending state is malformed")
            pending_state = EvaluationState(
                body=dict(raw_state["body"]),
                x=int(raw_state["x"]),
                y=int(raw_state["y"]),
                active_goal_type=(
                    None
                    if raw_state.get("active_goal_type") is None
                    else str(raw_state["active_goal_type"])
                ),
                temporal_context=str(raw_state["temporal_context"]),
            )
            pending_state.validate()
            self._pending = PendingTDSegment(
                decision_t_monde=int(raw_pending["decision_t_monde"]),
                state=pending_state,
                signature=str(raw_pending["signature"]),
                rewards=tuple(float(x) for x in raw_pending["rewards"]),
            )
        else:
            raise ValueError("TD pending state must be a mapping or null")
