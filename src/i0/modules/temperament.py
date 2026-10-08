"""Stage-5 temperament projection.

All innate individuality is projected exactly once at birth. Consumers receive
only immutable derived coefficients and never read tau directly.

Spec: 7.3, 20.3 Stage 5, INV-30, INV-40.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Temperament:
    reward_sensitivity: float
    threat_sensitivity: float
    exploration: float
    goal_protection: float
    affiliation: float

    def validate(self) -> None:
        for name, value in self.as_dict().items():
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"temperament dimension {name} must be in [-1,1]")

    def as_dict(self) -> dict[str, float]:
        return {
            "reward_sensitivity": self.reward_sensitivity,
            "threat_sensitivity": self.threat_sensitivity,
            "exploration": self.exploration,
            "goal_protection": self.goal_protection,
            "affiliation": self.affiliation,
        }


@dataclass(frozen=True, slots=True)
class TemperamentMappingConfig:
    version: str

    gatekeeper_base_weights: Mapping[str, float]
    gatekeeper_alpha: Mapping[str, float]

    extrinsic_alpha: float
    risk_alpha: float
    uncertainty_linear_strength: float
    protective_threshold_linear_strength: float
    inertia_linear_strength: float
    integrity_weight_alpha: float
    exploration_linear_strength: float

    beta_neutral: float
    beta_min: float
    beta_max: float
    beta_linear_span: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("temperament mapping version must not be empty")

        required_weights = {"b", "n", "urg", "risk", "value"}
        if set(self.gatekeeper_base_weights) != required_weights:
            raise ValueError("gatekeeper base weights must define b,n,urg,risk,value")
        if set(self.gatekeeper_alpha) != required_weights:
            raise ValueError("gatekeeper alpha must define b,n,urg,risk,value")
        if any(value < 0 for value in self.gatekeeper_base_weights.values()):
            raise ValueError("gatekeeper base weights must be non-negative")

        if not 0.0 < self.beta_min <= self.beta_neutral <= self.beta_max < 1.0:
            raise ValueError("beta bounds must satisfy 0 < min <= neutral <= max < 1")
        if self.beta_linear_span < 0:
            raise ValueError("beta linear span must be non-negative")
        if self.uncertainty_linear_strength < 0:
            raise ValueError("uncertainty temperament strength must be non-negative")
        if self.protective_threshold_linear_strength < 0:
            raise ValueError("protective threshold strength must be non-negative")
        if self.inertia_linear_strength < 0:
            raise ValueError("inertia temperament strength must be non-negative")
        if self.exploration_linear_strength < 0:
            raise ValueError("exploration temperament strength must be non-negative")


@dataclass(frozen=True, slots=True)
class TemperamentParameters:
    mapping_version: str

    gatekeeper_weights: Mapping[str, float]

    extrinsic_value_gain: float
    risk_penalty_multiplier: float
    uncertainty_penalty_multiplier: float
    protective_threshold_delta_multiplier: float
    inertia_multiplier: float

    body_weight_multipliers: Mapping[str, float]
    beta_individual: float
    exploration_multiplier: float

    def validate(self) -> None:
        if not self.mapping_version:
            raise ValueError("mapping version must not be empty")
        required = {"b", "n", "urg", "risk", "value"}
        if set(self.gatekeeper_weights) != required:
            raise ValueError("derived gatekeeper weights incomplete")
        if any(value < 0 for value in self.gatekeeper_weights.values()):
            raise ValueError("derived gatekeeper weights must be non-negative")
        if self.extrinsic_value_gain <= 0 or self.risk_penalty_multiplier <= 0:
            raise ValueError("derived exponential gains must be positive")
        if self.uncertainty_penalty_multiplier < 0:
            raise ValueError("uncertainty multiplier must be non-negative")
        if self.protective_threshold_delta_multiplier < 0:
            raise ValueError("protective threshold multiplier must be non-negative")
        if self.inertia_multiplier < 0:
            raise ValueError("inertia multiplier must be non-negative")
        if self.exploration_multiplier < 0:
            raise ValueError("exploration multiplier must be non-negative")
        if not 0.0 < self.beta_individual < 1.0:
            raise ValueError("beta_individual must lie in ]0,1[")
        for name in ("energy", "food", "water", "integrity"):
            if name not in self.body_weight_multipliers:
                raise ValueError(f"missing body weight multiplier for {name}")
            if self.body_weight_multipliers[name] < 0:
                raise ValueError("body weight multipliers must be non-negative")


class TemperamentProjector:
    """The only component authorized to read raw temperament tau."""

    owner_id = "snapshots_and_individual_parameters"

    def __init__(
        self,
        *,
        tau: Temperament,
        config: TemperamentMappingConfig,
    ) -> None:
        tau.validate()
        config.validate()
        self._tau = tau
        self._config = config
        self._parameters = self._project(tau, config)

    @property
    def parameters(self) -> TemperamentParameters:
        return self._parameters

    @staticmethod
    def _clip(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    @classmethod
    def _project(
        cls,
        tau: Temperament,
        config: TemperamentMappingConfig,
    ) -> TemperamentParameters:
        t = tau

        dimension_for_weight = {
            "b": t.goal_protection,
            "n": t.exploration,
            "urg": t.threat_sensitivity,
            "risk": t.threat_sensitivity,
            "value": t.reward_sensitivity,
        }
        gatekeeper_weights = {
            name: config.gatekeeper_base_weights[name]
            * exp(config.gatekeeper_alpha[name] * dimension_for_weight[name])
            for name in sorted(config.gatekeeper_base_weights)
        }

        # Explicit normative exponential forms are preserved where specified.
        extrinsic_gain = exp(config.extrinsic_alpha * t.reward_sensitivity)
        risk_multiplier = exp(config.risk_alpha * t.threat_sensitivity)

        # Remaining amplitudes are table parameters centered on neutral=1.
        uncertainty_multiplier = max(
            0.0,
            1.0
            + config.uncertainty_linear_strength * t.threat_sensitivity,
        )
        protective_multiplier = max(
            0.0,
            1.0
            + config.protective_threshold_linear_strength
            * t.threat_sensitivity,
        )
        inertia_multiplier = max(
            0.0,
            1.0
            + config.inertia_linear_strength * t.goal_protection,
        )
        exploration_multiplier = max(
            0.0,
            1.0
            + config.exploration_linear_strength * t.exploration,
        )

        body_weight_multipliers = {
            "energy": 1.0,
            "food": 1.0,
            "water": 1.0,
            "integrity": exp(
                config.integrity_weight_alpha * t.threat_sensitivity
            ),
        }

        beta = cls._clip(
            config.beta_neutral
            + config.beta_linear_span * t.reward_sensitivity,
            config.beta_min,
            config.beta_max,
        )

        projected = TemperamentParameters(
            mapping_version=config.version,
            gatekeeper_weights=gatekeeper_weights,
            extrinsic_value_gain=extrinsic_gain,
            risk_penalty_multiplier=risk_multiplier,
            uncertainty_penalty_multiplier=uncertainty_multiplier,
            protective_threshold_delta_multiplier=protective_multiplier,
            inertia_multiplier=inertia_multiplier,
            body_weight_multipliers=body_weight_multipliers,
            beta_individual=beta,
            exploration_multiplier=exploration_multiplier,
        )
        projected.validate()
        return projected

    def export_causal_state(self) -> object:
        return {
            "mapping_version": self._config.version,
            "tau": self._tau.as_dict(),
            "parameters": {
                "gatekeeper_weights": dict(self._parameters.gatekeeper_weights),
                "extrinsic_value_gain": self._parameters.extrinsic_value_gain,
                "risk_penalty_multiplier": self._parameters.risk_penalty_multiplier,
                "uncertainty_penalty_multiplier": (
                    self._parameters.uncertainty_penalty_multiplier
                ),
                "protective_threshold_delta_multiplier": (
                    self._parameters.protective_threshold_delta_multiplier
                ),
                "inertia_multiplier": self._parameters.inertia_multiplier,
                "body_weight_multipliers": dict(
                    self._parameters.body_weight_multipliers
                ),
                "beta_individual": self._parameters.beta_individual,
                "exploration_multiplier": self._parameters.exploration_multiplier,
            },
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("temperament state must be a mapping")
        if state.get("mapping_version") != self._config.version:
            raise ValueError("temperament mapping version mismatch")

        tau_raw = state.get("tau")
        if not isinstance(tau_raw, Mapping):
            raise ValueError("temperament snapshot missing tau")
        restored_tau = Temperament(
            reward_sensitivity=float(tau_raw["reward_sensitivity"]),
            threat_sensitivity=float(tau_raw["threat_sensitivity"]),
            exploration=float(tau_raw["exploration"]),
            goal_protection=float(tau_raw["goal_protection"]),
            affiliation=float(tau_raw["affiliation"]),
        )
        restored_tau.validate()
        if restored_tau != self._tau:
            raise ValueError("INV-30: temperament tau cannot change during a life")

        expected = self._project(self._tau, self._config)
        if expected != self._parameters:
            raise ValueError("derived temperament parameters are not immutable")
