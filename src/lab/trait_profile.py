"""Bench-side Stage-5 trait-profile aggregation.

Statistical choices are deliberately explicit inputs. The normative spec
requires confidence intervals and intraclass-correlation reliability but does
not fix the interval estimator, ICC variant, or pass threshold. This module
therefore never invents any of them.

Spec: 19.5, 20.3 Stage 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Mapping, Sequence

from .battery_scenarios import BatterySituation
from .trait_battery import BatteryAdministration


@dataclass(frozen=True, slots=True)
class TraitEstimate:
    situation: BatterySituation
    status: str
    n_numeric: int
    mean: float | None
    confidence_interval: tuple[float, float] | None
    score_statuses: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TraitProfile:
    individual_id: str
    age_t_monde: int
    battery_version: str
    estimates: Mapping[str, TraitEstimate]
    complete: bool


@dataclass(frozen=True, slots=True)
class ReliabilityProtocol:
    version: str
    method: str
    threshold: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("reliability protocol version must not be empty")
        if not self.method:
            raise ValueError("reliability method must not be empty")
        if not -1.0 <= self.threshold <= 1.0:
            raise ValueError("ICC reliability threshold must lie in [-1,1]")


@dataclass(frozen=True, slots=True)
class ReliabilityAssessment:
    protocol_version: str
    method: str
    observed_value: float
    threshold: float
    passed: bool


def build_trait_profile(
    *,
    individual_id: str,
    age_t_monde: int,
    battery_version: str,
    administrations: Sequence[BatteryAdministration],
    confidence_intervals: Mapping[str, tuple[float, float] | None],
) -> TraitProfile:
    """Aggregate raw battery administrations without choosing a CI estimator."""

    if not individual_id:
        raise ValueError("individual_id must not be empty")
    if age_t_monde < 0:
        raise ValueError("age_t_monde must be non-negative")
    if not battery_version:
        raise ValueError("battery_version must not be empty")

    grouped: dict[BatterySituation, list[BatteryAdministration]] = {
        situation: [] for situation in BatterySituation
    }
    for administration in administrations:
        grouped[administration.situation].append(administration)

    expected_keys = {situation.value for situation in BatterySituation}
    if set(confidence_intervals) != expected_keys:
        raise ValueError(
            "confidence intervals must explicitly cover all five situations"
        )

    estimates: dict[str, TraitEstimate] = {}
    complete = True
    for situation in BatterySituation:
        rows = grouped[situation]
        numeric = [
            float(row.score.value)
            for row in rows
            if row.score.value is not None and row.score.status == "scored"
        ]
        statuses = tuple(row.score.status for row in rows)
        interval = confidence_intervals[situation.value]

        status = "estimated"
        if not rows:
            status = "missing_administration"
            complete = False
        elif not numeric:
            status = "not_estimable"
            complete = False
        elif interval is None:
            status = "interval_not_supplied"
            complete = False
        else:
            low, high = interval
            if low > high:
                raise ValueError("confidence interval lower bound exceeds upper")
            if not low <= fmean(numeric) <= high:
                raise ValueError("confidence interval must contain the mean")

        estimates[situation.value] = TraitEstimate(
            situation=situation,
            status=status,
            n_numeric=len(numeric),
            mean=None if not numeric else fmean(numeric),
            confidence_interval=interval,
            score_statuses=statuses,
        )

    return TraitProfile(
        individual_id=individual_id,
        age_t_monde=age_t_monde,
        battery_version=battery_version,
        estimates=estimates,
        complete=complete,
    )


def assess_reliability(
    *,
    observed_icc: float,
    protocol: ReliabilityProtocol,
) -> ReliabilityAssessment:
    """Judge an externally computed preregistered ICC against its frozen gate."""

    protocol.validate()
    if not -1.0 <= observed_icc <= 1.0:
        raise ValueError("observed ICC must lie in [-1,1]")
    return ReliabilityAssessment(
        protocol_version=protocol.version,
        method=protocol.method,
        observed_value=observed_icc,
        threshold=protocol.threshold,
        passed=observed_icc >= protocol.threshold,
    )
