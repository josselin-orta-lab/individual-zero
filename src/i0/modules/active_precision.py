"""Stage-8 online perceptual precision, owned exclusively by Perception.

11.2 does not prescribe the precision estimator; its deterministic running
squared-error rule and all priors are therefore explicit versioned parameters.
It is independent from DC-06 kappa reliability and Stage-10 consolidation.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Mapping


@dataclass(frozen=True, slots=True)
class PrecisionConfig:
    version: str
    prior_weight: float
    initial_rmse_by_source: Mapping[str, float]
    variance_floor: float
    maximum_precision: float

    def validate(self) -> None:
        if not self.version or self.prior_weight <= 0 or self.variance_floor <= 0:
            raise ValueError("invalid active precision prior")
        if self.maximum_precision <= 0 or not self.initial_rmse_by_source:
            raise ValueError("invalid active precision bound or source registry")
        for source, rmse in self.initial_rmse_by_source.items():
            if not source or rmse <= 0:
                raise ValueError("invalid versioned perceptual source prior")


@dataclass(frozen=True, slots=True)
class PrecisionVerification:
    identifier: str
    source: str
    independent_observation_ref: str
    emission_step: int
    observation_step: int
    squared_error: float
    anchor: str
    independent_provenance: bool
    oracle_derived: bool = False
    rollback_cancelled: bool = False

    def valid_for_online_update(self) -> bool:
        return (
            self.anchor == "monde"
            and self.observation_step > self.emission_step
            and bool(self.independent_observation_ref)
            and self.independent_provenance
            and not self.oracle_derived
            and not self.rollback_cancelled
            and 0 <= self.squared_error < float("inf")
        )


class ActivePerceptualPrecision:
    """A single precision per registered source; never writes consolidated h."""

    def __init__(self, config: PrecisionConfig) -> None:
        config.validate()
        self.config = config
        self._sums: dict[str, tuple[int, float]] = {}
        self._pending: list[PrecisionVerification] = []
        self._seen: set[str] = set()
        self._credited: set[tuple[str, str]] = set()
        self._version = 0

    @property
    def version(self) -> int:
        return self._version

    def precision(self, source: str) -> float:
        try:
            rmse = self.config.initial_rmse_by_source[source]
        except KeyError as exc:
            raise ValueError("unregistered perceptual source") from exc
        n, sum_squared = self._sums.get(source, (0, 0.0))
        variance = (
            self.config.prior_weight * rmse ** 2 + sum_squared
        ) / (self.config.prior_weight + n)
        return min(self.config.maximum_precision, 1.0 / sqrt(max(self.config.variance_floor, variance)))

    def integrate(self, verification: PrecisionVerification) -> None:
        if not verification.identifier or verification.source not in self.config.initial_rmse_by_source:
            raise ValueError("invalid precision verification source")
        if verification.squared_error < 0 or verification.squared_error == float("inf"):
            raise ValueError("invalid squared-error sample")
        if verification.identifier in self._seen or any(
            event.identifier == verification.identifier for event in self._pending
        ):
            raise ValueError("duplicate precision verification identity")
        self._pending.append(verification)

    def publish(self) -> tuple[tuple[str, float, float, str], ...]:
        updates = []
        for v in sorted(self._pending, key=lambda x: (x.source, x.identifier)):
            self._seen.add(v.identifier)
            if not v.valid_for_online_update():
                continue
            credit = (v.source, v.independent_observation_ref)
            if credit in self._credited:
                continue
            self._credited.add(credit)
            before = self.precision(v.source)
            n, squared = self._sums.get(v.source, (0, 0.0))
            self._sums[v.source] = n + 1, squared + v.squared_error
            updates.append((v.source, before, self.precision(v.source), v.identifier))
        self._pending.clear()
        self._version += 1
        return tuple(updates)

    def export_causal_state(self) -> object:
        return {
            "config_version": self.config.version,
            "version": self._version,
            "source_sums": [
                {"source": source, "n": n, "squared": squared}
                for source, (n, squared) in sorted(self._sums.items())
            ],
            "pending": [
                {field: getattr(v, field) for field in v.__dataclass_fields__}
                for v in self._pending
            ],
            "seen": sorted(self._seen),
            "credited": [list(row) for row in sorted(self._credited)],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping) or state.get("config_version") != self.config.version:
            raise ValueError("perceptual precision configuration mismatch")
        sums = {}
        for row in state["source_sums"]:
            source, n, squared = row["source"], row["n"], row["squared"]
            if source not in self.config.initial_rmse_by_source or not isinstance(n, int) or n < 0 or squared < 0:
                raise ValueError("invalid perceptual precision snapshot")
            sums[source] = (n, float(squared))
        pending = [PrecisionVerification(**row) for row in state["pending"]]
        for event in pending:
            if event.source not in self.config.initial_rmse_by_source:
                raise ValueError("unregistered pending precision source")
        self._sums = sums
        self._pending = pending
        self._seen = set(state["seen"])
        self._credited = {tuple(row) for row in state["credited"]}
        self._version = int(state["version"])
