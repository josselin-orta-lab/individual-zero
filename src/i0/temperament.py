"""Stage-5 temperament projection.

Tau is private birth configuration. Consuming cognitive components receive only
the immutable derived ParametresTemperament object produced here.

Spec: 6.4, 7.1, 7.3, 8.5-8.6, 20.3 Stage 5, INV-30, INV-40.
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
    affiliation: float = 0.0

    def validate(self) -> None:
        for name, value in (
            ("reward_sensitivity", self.reward_sensitivity),
            ("threat_sensitivity", self.threat_sensitivity),
            ("exploration", self.exploration),
            ("goal_protection", self.goal_protection),
            ("affiliation", self.affiliation),
        ):
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [-1,1]")

    def as_dict(self) -> dict[str, float]:
        self.validate()
        return {
            "reward_sensitivity": self.reward_sensitivity,
            "threat_sensitivity": self.threat_sensitivity,
            "exploration": self.exploration,
            "goal_protection": self.goal_protection,
            "affiliation": self.affiliation,
        }


@dataclass(frozen=True, slots=True)
class LinearTemperamentCurve:
    """Versioned three-point projection for a pathway not numerically fixed by spec.

    The neutral value is mandatory and must reproduce the Stage-4 neutral system.
    Endpoints are preregistered table values, not runtime tuning knobs.
    """

    at_minus_one: float
    at_zero: float
    at_plus_one: float

    def value(self, tau: float) -> float:
        if not -1.0 <= tau <= 1.0:
            raise ValueError("temperament coordinate must lie in [-1,1]")
        if tau < 0.0:
            return self.at_zero + (-tau) * (self.at_minus_one - self.at_zero)
        return self.at_zero + tau * (self.at_plus_one - self.at_zero)


@dataclass(frozen=True, slots=True)
class TemperamentMappingConfig:
    version: str
    gatekeeper_base_weights: Mapping[str, float]
    gatekeeper_alpha: Mapping[str, float]
    reward_extrinsic_alpha: float
    risk_k_pi: float
    risk_alpha_pi: float
    uncertainty_k_chi: float
    protective_threshold_delta: float
    base_inertia: float
    goal_protection_inertia_curve: LinearTemperamentCurve
    base_body_weights: Mapping[str, float]
    integrity_weight_curve: LinearTemperamentCurve
    discount_beta: float | None = None

    def validate(self) -> None:
        if not self.version:
            raise ValueError("temperament mapping version must not be empty")

        required_gate = {"b", "n", "urg", "risk", "value"}
        if set(self.gatekeeper_base_weights) != required_gate:
            raise ValueError("gatekeeper base weights must define b,n,urg,risk,value")
        if any(value < 0.0 for value in self.gatekeeper_base_weights.values()):
            raise ValueError("gatekeeper base weights must be non-negative")

        required_alpha = {"b", "n", "urg", "risk", "value"}
        if set(self.gatekeeper_alpha) != required_alpha:
            raise ValueError("gatekeeper alpha table must define b,n,urg,risk,value")

        if self.risk_k_pi < 0.0 or self.uncertainty_k_chi < 0.0:
            raise ValueError("risk/uncertainty scales must be non-negative")
        if self.protective_threshold_delta < 0.0:
            raise ValueError("protective threshold delta must be non-negative")
        if self.base_inertia < 0.0:
            raise ValueError("base inertia must be non-negative")
        if self.goal_protection_inertia_curve.at_zero != self.base_inertia:
            raise ValueError(
                "goal-protection curve neutral point must equal Stage-4 inertia"
            )

        required_body = {"energy", "food", "water", "integrity"}
        if set(self.base_body_weights) != required_body:
            raise ValueError("body weights must define all four MVP variables")
        if any(value < 0.0 for value in self.base_body_weights.values()):
            raise ValueError("body weights must be non-negative")
        if (
            self.integrity_weight_curve.at_zero
            != self.base_body_weights["integrity"]
        ):
            raise ValueError(
                "integrity curve neutral point must equal neutral body weight"
            )

        if self.discount_beta is not None and not 0.0 < self.discount_beta < 1.0:
            raise ValueError("discount beta must lie in ]0,1[")


@dataclass(frozen=True, slots=True)
class ParametresTemperament:
    mapping_version: str
    gatekeeper_weights: Mapping[str, float]
    extrinsic_value_gain: float
    risk_penalty_scale: float
    uncertainty_penalty_scale: float
    protective_threshold_reduction: float
    inertia: float
    body_weights: Mapping[str, float]
    exploration_coefficient: float
    discount_beta: float | None

    def validate(self) -> None:
        if not self.mapping_version:
            raise ValueError("mapping version must not be empty")
        if any(value < 0.0 for value in self.gatekeeper_weights.values()):
            raise ValueError("derived gatekeeper weights must be non-negative")
        if self.extrinsic_value_gain <= 0.0:
            raise ValueError("extrinsic value gain must be > 0")
        if self.risk_penalty_scale < 0.0:
            raise ValueError("risk penalty must be non-negative")
        if self.uncertainty_penalty_scale < 0.0:
            raise ValueError("uncertainty penalty must be non-negative")
        if self.protective_threshold_reduction < 0.0:
            raise ValueError("protective threshold reduction must be non-negative")
        if self.inertia < 0.0:
            raise ValueError("inertia must be non-negative")
        if any(value < 0.0 for value in self.body_weights.values()):
            raise ValueError("derived body weights must be non-negative")
        if self.discount_beta is not None and not 0.0 < self.discount_beta < 1.0:
            raise ValueError("discount beta must lie in ]0,1[")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "mapping_version": self.mapping_version,
            "gatekeeper_weights": dict(sorted(self.gatekeeper_weights.items())),
            "extrinsic_value_gain": self.extrinsic_value_gain,
            "risk_penalty_scale": self.risk_penalty_scale,
            "uncertainty_penalty_scale": self.uncertainty_penalty_scale,
            "protective_threshold_reduction": self.protective_threshold_reduction,
            "inertia": self.inertia,
            "body_weights": dict(sorted(self.body_weights.items())),
            "exploration_coefficient": self.exploration_coefficient,
            "discount_beta": self.discount_beta,
        }


class TemperamentProjection:
    """Sole code boundary allowed to read raw tau."""

    owner_id = "snapshots_and_individual_parameters"

    def __init__(
        self,
        *,
        temperament: Temperament,
        mapping: TemperamentMappingConfig,
        individual_id: str = "i0-stage5",
        lineage_id: str | None = None,
        parent_id: str | None = None,
        copy_snapshot_id: str | None = None,
        battery_copy: bool = False,
    ) -> None:
        temperament.validate()
        mapping.validate()
        if not individual_id:
            raise ValueError("individual_id must not be empty")
        self._individual_id = individual_id
        self._lineage_id = lineage_id or individual_id
        self._parent_id = parent_id
        self._copy_snapshot_id = copy_snapshot_id
        self._battery_copy = bool(battery_copy)
        self._tau = temperament
        self._mapping = mapping
        self._derived = self._project_once(temperament, mapping)

    @property
    def parameters(self) -> ParametresTemperament:
        return self._derived

    @property
    def mapping_version(self) -> str:
        return self._mapping.version

    @property
    def individual_id(self) -> str:
        return self._individual_id

    @property
    def lineage_id(self) -> str:
        return self._lineage_id

    @property
    def parent_id(self) -> str | None:
        return self._parent_id

    @property
    def copy_snapshot_id(self) -> str | None:
        return self._copy_snapshot_id

    @property
    def battery_copy(self) -> bool:
        return self._battery_copy

    @staticmethod
    def _project_once(
        tau: Temperament,
        mapping: TemperamentMappingConfig,
    ) -> ParametresTemperament:
        # Section 7.3 maps threat sensitivity to w_r and w_u.
        # In Gatekeeper notation, w_u is the weight of urgency.
        coordinates = {
            "b": tau.goal_protection,
            "n": tau.exploration,
            "urg": tau.threat_sensitivity,
            "risk": tau.threat_sensitivity,
            "value": tau.reward_sensitivity,
        }
        gatekeeper_weights = {
            name: mapping.gatekeeper_base_weights[name]
            * exp(mapping.gatekeeper_alpha[name] * coordinates[name])
            for name in sorted(mapping.gatekeeper_base_weights)
        }

        body_weights = dict(mapping.base_body_weights)
        body_weights["integrity"] = mapping.integrity_weight_curve.value(
            tau.threat_sensitivity
        )

        derived = ParametresTemperament(
            mapping_version=mapping.version,
            gatekeeper_weights=gatekeeper_weights,
            # DC-01 exact formula gamma_v = exp(alpha_v * tau_reward).
            extrinsic_value_gain=exp(
                mapping.reward_extrinsic_alpha * tau.reward_sensitivity
            ),
            # DC-01 exact formula pi = k_pi * exp(alpha_pi*tau_threat) * R.
            risk_penalty_scale=(
                mapping.risk_k_pi
                * exp(mapping.risk_alpha_pi * tau.threat_sensitivity)
            ),
            # DC-01 exact scale for chi(U).
            uncertainty_penalty_scale=(
                mapping.uncertainty_k_chi
                * (1.0 + tau.threat_sensitivity)
                / 2.0
            ),
            # Section 8.6 exact protective threshold reduction.
            protective_threshold_reduction=(
                mapping.protective_threshold_delta
                * (1.0 + tau.threat_sensitivity)
                / 2.0
            ),
            inertia=mapping.goal_protection_inertia_curve.value(
                tau.goal_protection
            ),
            body_weights=body_weights,
            # Stage 11 consumes this. Stage 5 only projects and freezes it.
            exploration_coefficient=tau.exploration,
            discount_beta=mapping.discount_beta,
        )
        derived.validate()
        return derived

    def export_causal_state(self) -> object:
        return {
            "mapping_version": self._mapping.version,
            "individual_id": self._individual_id,
            "lineage_id": self._lineage_id,
            "parent_id": self._parent_id,
            "copy_snapshot_id": self._copy_snapshot_id,
            "battery_copy": self._battery_copy,
            "tau": self._tau.as_dict(),
            "derived": self._derived.as_dict(),
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("temperament projection state must be a mapping")
        if state.get("mapping_version") != self._mapping.version:
            raise ValueError("temperament mapping version mismatch")

        raw_tau = state.get("tau")
        if not isinstance(raw_tau, Mapping):
            raise ValueError("temperament snapshot is missing tau")
        restored_tau = Temperament(
            reward_sensitivity=float(raw_tau["reward_sensitivity"]),
            threat_sensitivity=float(raw_tau["threat_sensitivity"]),
            exploration=float(raw_tau["exploration"]),
            goal_protection=float(raw_tau["goal_protection"]),
            affiliation=float(raw_tau["affiliation"]),
        )
        restored_tau.validate()

        # Tau is immutable throughout the life. Restoration may only restore
        # the same birth temperament, never replace it.
        if restored_tau != self._tau:
            raise ValueError("INV-30: tau cannot change during a life")

        recomputed = self._project_once(restored_tau, self._mapping)
        raw_derived = state.get("derived")
        if raw_derived != recomputed.as_dict():
            raise ValueError("derived temperament parameters do not match table")
        self._derived = recomputed

        if state.get("individual_id") != self._individual_id:
            raise ValueError("individual identity mismatch on ordinary restoration")
        if state.get("lineage_id") != self._lineage_id:
            raise ValueError("lineage mismatch on ordinary restoration")
        if state.get("parent_id") != self._parent_id:
            raise ValueError("parent mismatch on ordinary restoration")
        if state.get("copy_snapshot_id") != self._copy_snapshot_id:
            raise ValueError("copy point mismatch on ordinary restoration")
        if bool(state.get("battery_copy", False)) != self._battery_copy:
            raise ValueError("battery-copy status mismatch on ordinary restoration")

    def restore_copy_causal_state(self, state: object) -> None:
        """Restore inherited parameters while preserving the new branch identity."""
        if not isinstance(state, Mapping):
            raise ValueError("copy temperament state must be a mapping")
        if state.get("mapping_version") != self._mapping.version:
            raise ValueError("temperament mapping version mismatch")
        raw_tau = state.get("tau")
        if not isinstance(raw_tau, Mapping):
            raise ValueError("copy snapshot is missing tau")
        inherited = Temperament(
            reward_sensitivity=float(raw_tau["reward_sensitivity"]),
            threat_sensitivity=float(raw_tau["threat_sensitivity"]),
            exploration=float(raw_tau["exploration"]),
            goal_protection=float(raw_tau["goal_protection"]),
            affiliation=float(raw_tau["affiliation"]),
        )
        inherited.validate()
        if inherited != self._tau:
            raise ValueError("copy must inherit the exact parent temperament")
        recomputed = self._project_once(inherited, self._mapping)
        if state.get("derived") != recomputed.as_dict():
            raise ValueError("copy derived temperament parameters mismatch")
        self._derived = recomputed
