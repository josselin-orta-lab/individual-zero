"""Stage-5 trait profiles and preregistered test-retest reliability.

This module belongs to the evaluation bench. It consumes BatteryScore objects
after disposable-copy tests and never feeds profile or reliability information
back into the individual.

The normative specification requires intraclass correlation but does not fix
the ICC variant. The reference bench therefore makes the selected method an
explicit, versioned preregistration choice.

Spec: 19.5, 20.3 Stage 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .battery_scenarios import BatterySituation
from .trait_battery import BatteryScore


TRAIT_ORDER = (
    BatterySituation.PATIENCE,
    BatterySituation.RISK_TAKING,
    BatterySituation.EXPLORATION,
    BatterySituation.THREAT_RESPONSE,
    BatterySituation.PERSEVERANCE,
)


@dataclass(frozen=True, slots=True)
class TraitProfile:
    version: str
    individual_id: str
    administration_ref: str
    scores: Mapping[str, float]
    status: str
    missing: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "individual_id": self.individual_id,
            "administration_ref": self.administration_ref,
            "scores": dict(sorted(self.scores.items())),
            "status": self.status,
            "missing": list(self.missing),
        }


def build_trait_profile(
    *,
    version: str,
    individual_id: str,
    administration_ref: str,
    scores: Mapping[BatterySituation, BatteryScore],
) -> TraitProfile:
    if not version or not individual_id or not administration_ref:
        raise ValueError("profile version, individual and administration are required")
    if set(scores) != set(TRAIT_ORDER):
        raise ValueError("exactly one score per battery situation is required")

    values: dict[str, float] = {}
    missing: list[str] = []
    for situation in TRAIT_ORDER:
        score = scores[situation]
        if score.status == "scored" and score.value is not None:
            values[situation.value] = float(score.value)
        else:
            missing.append(situation.value)

    return TraitProfile(
        version=version,
        individual_id=individual_id,
        administration_ref=administration_ref,
        scores=values,
        status="complete" if not missing else "incomplete",
        missing=tuple(missing),
    )


@dataclass(frozen=True, slots=True)
class ReliabilityConfig:
    version: str
    method: str
    threshold: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("reliability config version must not be empty")
        if self.method != "icc_3_1":
            raise ValueError("reference implementation currently supports icc_3_1")
        if not -1.0 <= self.threshold <= 1.0:
            raise ValueError("ICC threshold must lie in [-1,1]")


@dataclass(frozen=True, slots=True)
class TraitReliability:
    trait: str
    status: str
    icc: float | None
    subject_count: int
    repeat_count: int
    passes_threshold: bool | None


@dataclass(frozen=True, slots=True)
class ReliabilityReport:
    config_version: str
    method: str
    threshold: float
    traits: tuple[TraitReliability, ...]

    @property
    def evaluable(self) -> bool:
        return all(item.status == "scored" for item in self.traits)

    @property
    def passes(self) -> bool:
        return self.evaluable and all(
            item.passes_threshold is True for item in self.traits
        )


def _icc_3_1(matrix: Sequence[Sequence[float]]) -> float:
    """Two-way mixed-effects, consistency, single-measure ICC(3,1).

    Rows are individuals and columns are repeated administrations.
    """

    n = len(matrix)
    if n < 2:
        raise ValueError("ICC requires at least two individuals")
    k = len(matrix[0]) if matrix else 0
    if k < 2:
        raise ValueError("ICC requires at least two repeated administrations")
    if any(len(row) != k for row in matrix):
        raise ValueError("ICC matrix must be rectangular")

    row_means = [sum(row) / k for row in matrix]
    grand = sum(row_means) / n
    col_means = [
        sum(matrix[i][j] for i in range(n)) / n
        for j in range(k)
    ]

    ss_rows = k * sum((mean - grand) ** 2 for mean in row_means)
    ss_cols = n * sum((mean - grand) ** 2 for mean in col_means)
    ss_total = sum(
        (matrix[i][j] - grand) ** 2
        for i in range(n)
        for j in range(k)
    )
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))

    denominator = ms_rows + (k - 1) * ms_error
    if denominator == 0.0:
        # All subjects and repeats identical: no between-individual variance,
        # therefore reliability is undefined rather than artificially perfect.
        raise ValueError("ICC undefined when between-individual variance is zero")
    return (ms_rows - ms_error) / denominator


def evaluate_test_retest(
    *,
    profiles_by_individual: Mapping[str, Sequence[TraitProfile]],
    config: ReliabilityConfig,
) -> ReliabilityReport:
    config.validate()
    if not profiles_by_individual:
        raise ValueError("reliability requires profiles")

    individual_ids = sorted(profiles_by_individual)
    repeat_counts = {
        len(profiles_by_individual[individual_id])
        for individual_id in individual_ids
    }
    if len(repeat_counts) != 1:
        raise ValueError("all individuals must have the same repeat count")
    repeat_count = next(iter(repeat_counts))
    if repeat_count < 2:
        raise ValueError("test-retest reliability requires at least two repeats")

    traits: list[TraitReliability] = []
    for situation in TRAIT_ORDER:
        trait = situation.value
        matrix: list[list[float]] = []
        missing = False
        for individual_id in individual_ids:
            row: list[float] = []
            for profile in profiles_by_individual[individual_id]:
                if profile.status != "complete" or trait not in profile.scores:
                    missing = True
                    break
                row.append(float(profile.scores[trait]))
            if missing:
                break
            matrix.append(row)

        if missing:
            traits.append(
                TraitReliability(
                    trait=trait,
                    status="incomplete_profiles",
                    icc=None,
                    subject_count=len(individual_ids),
                    repeat_count=repeat_count,
                    passes_threshold=None,
                )
            )
            continue

        try:
            value = _icc_3_1(matrix)
        except ValueError as exc:
            traits.append(
                TraitReliability(
                    trait=trait,
                    status=f"not_evaluable:{exc}",
                    icc=None,
                    subject_count=len(individual_ids),
                    repeat_count=repeat_count,
                    passes_threshold=None,
                )
            )
            continue

        traits.append(
            TraitReliability(
                trait=trait,
                status="scored",
                icc=value,
                subject_count=len(individual_ids),
                repeat_count=repeat_count,
                passes_threshold=value >= config.threshold,
            )
        )

    return ReliabilityReport(
        config_version=config.version,
        method=config.method,
        threshold=config.threshold,
        traits=tuple(traits),
    )
