"""Offline Stage-6 equipment benchmark and conjunctive equivalence gate.

The benchmark is Lab-only. Tolerances are frozen after benchmark definition and
before training, as required by P-46. No single aggregate score can compensate
for failure of a required family, horizon, calibration or systematic-bias
criterion.

Spec: 12.5, P-46, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from i0.equipment import EquipmentCorpus, EquipmentModel, SimulationState
from lab.determinism import canonical_causal_bytes


@dataclass(frozen=True, slots=True)
class EquipmentEquivalenceTolerances:
    version: str
    overall_error_max: float
    unavailable_rate_max: float
    per_family_error_max: Mapping[str, float]
    per_horizon_error_max: Mapping[int, float]
    calibration_brier_max: float
    systematic_bias_abs_max: Mapping[str, float]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("equipment tolerance version must not be empty")
        for name, value in (
            ("overall_error_max", self.overall_error_max),
            ("unavailable_rate_max", self.unavailable_rate_max),
            ("calibration_brier_max", self.calibration_brier_max),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0,1]")
        if not self.per_family_error_max:
            raise ValueError("per-family tolerances must be explicit")
        if not self.per_horizon_error_max:
            raise ValueError("per-horizon tolerances must be explicit")
        if not self.systematic_bias_abs_max:
            raise ValueError("systematic-bias tolerances must be explicit")
        if any(not 0.0 <= value <= 1.0 for value in self.per_family_error_max.values()):
            raise ValueError("per-family error tolerances must lie in [0,1]")
        if any(horizon < 1 for horizon in self.per_horizon_error_max):
            raise ValueError("horizon tolerance keys must be >= 1")
        if any(not 0.0 <= value <= 1.0 for value in self.per_horizon_error_max.values()):
            raise ValueError("per-horizon error tolerances must lie in [0,1]")
        if any(value < 0.0 for value in self.systematic_bias_abs_max.values()):
            raise ValueError("systematic-bias tolerances must be non-negative")


@dataclass(frozen=True, slots=True)
class EquipmentBenchmarkResult:
    equipment_version: str
    corpus_version: str
    tolerance_version: str
    example_count: int
    overall_error: float
    unavailable_rate: float
    per_family_error: Mapping[str, float]
    per_horizon_error: Mapping[int, float]
    calibration_brier: float
    systematic_bias: Mapping[str, float]
    failed_criteria: tuple[str, ...]

    @property
    def equivalent(self) -> bool:
        return not self.failed_criteria


def _state_equal(left: SimulationState, right: SimulationState) -> bool:
    return canonical_causal_bytes(left.as_dict()) == canonical_causal_bytes(
        right.as_dict()
    )


def _numeric_projection(state: SimulationState) -> dict[str, float]:
    return {
        "x": float(state.x),
        "y": float(state.y),
        "energy": float(state.body["energy"]),
        "food": float(state.body["food"]),
        "water": float(state.body["water"]),
        "integrity": float(state.body["integrity"]),
    }


def benchmark_equipment(
    *,
    equipment: EquipmentModel,
    corpus: EquipmentCorpus,
    tolerances: EquipmentEquivalenceTolerances,
) -> EquipmentBenchmarkResult:
    corpus.validate()
    tolerances.validate()

    total = len(corpus.examples)
    errors = 0
    unavailable = 0
    family_totals: dict[str, int] = {}
    family_errors: dict[str, int] = {}
    horizon_totals: dict[int, int] = {1: 0}
    horizon_errors: dict[int, int] = {1: 0}
    calibration_terms: list[float] = []
    bias_sums = {
        key: 0.0
        for key in tolerances.systematic_bias_abs_max
    }
    bias_counts = {
        key: 0
        for key in tolerances.systematic_bias_abs_max
    }

    for example in corpus.examples:
        family_totals[example.family] = family_totals.get(example.family, 0) + 1
        horizon_totals[1] += 1

        try:
            prediction = equipment.predict(
                state=example.state,
                command=example.command,
            )
        except LookupError:
            unavailable += 1
            errors += 1
            family_errors[example.family] = family_errors.get(example.family, 0) + 1
            horizon_errors[1] += 1
            continue

        prediction.validate()
        correct = (
            _state_equal(prediction.next_state, example.observed_next_state)
            and prediction.terminal == example.terminal
        )
        if not correct:
            errors += 1
            family_errors[example.family] = family_errors.get(example.family, 0) + 1
            horizon_errors[1] += 1

        observed = 1.0 if correct else 0.0
        calibration_terms.append((prediction.confidence - observed) ** 2)

        pred_numeric = _numeric_projection(prediction.next_state)
        obs_numeric = _numeric_projection(example.observed_next_state)
        for key in bias_sums:
            if key not in pred_numeric:
                continue
            bias_sums[key] += pred_numeric[key] - obs_numeric[key]
            bias_counts[key] += 1

    per_family_error = {
        family: family_errors.get(family, 0) / count
        for family, count in sorted(family_totals.items())
    }
    per_horizon_error = {
        horizon: horizon_errors.get(horizon, 0) / count
        for horizon, count in sorted(horizon_totals.items())
        if count > 0
    }
    systematic_bias = {
        key: (
            0.0
            if bias_counts[key] == 0
            else bias_sums[key] / bias_counts[key]
        )
        for key in sorted(bias_sums)
    }

    overall_error = errors / total
    unavailable_rate = unavailable / total
    calibration_brier = (
        0.0
        if not calibration_terms
        else sum(calibration_terms) / len(calibration_terms)
    )

    failed: list[str] = []
    if overall_error > tolerances.overall_error_max:
        failed.append("overall_error")
    if unavailable_rate > tolerances.unavailable_rate_max:
        failed.append("unavailable_rate")

    for family, maximum in tolerances.per_family_error_max.items():
        measured = per_family_error.get(family)
        if measured is None:
            failed.append(f"family_missing:{family}")
        elif measured > maximum:
            failed.append(f"family_error:{family}")

    for horizon, maximum in tolerances.per_horizon_error_max.items():
        measured = per_horizon_error.get(horizon)
        if measured is None:
            failed.append(f"horizon_missing:{horizon}")
        elif measured > maximum:
            failed.append(f"horizon_error:{horizon}")

    if calibration_brier > tolerances.calibration_brier_max:
        failed.append("calibration_brier")

    for variable, maximum in tolerances.systematic_bias_abs_max.items():
        measured = systematic_bias.get(variable)
        if measured is None:
            failed.append(f"bias_missing:{variable}")
        elif abs(measured) > maximum:
            failed.append(f"systematic_bias:{variable}")

    return EquipmentBenchmarkResult(
        equipment_version=equipment.version,
        corpus_version=corpus.version,
        tolerance_version=tolerances.version,
        example_count=total,
        overall_error=overall_error,
        unavailable_rate=unavailable_rate,
        per_family_error=per_family_error,
        per_horizon_error=per_horizon_error,
        calibration_brier=calibration_brier,
        systematic_bias=systematic_bias,
        failed_criteria=tuple(sorted(failed)),
    )


def require_equivalent_versions(
    *,
    results: Sequence[EquipmentBenchmarkResult],
    required_versions: Sequence[str],
) -> None:
    by_version = {result.equipment_version: result for result in results}
    missing = sorted(set(required_versions) - set(by_version))
    if missing:
        raise ValueError(
            "missing equipment benchmark versions: " + ", ".join(missing)
        )
    failures = [
        version
        for version in required_versions
        if not by_version[version].equivalent
    ]
    if failures:
        raise ValueError(
            "equipment versions failed conjunctive equivalence: "
            + ", ".join(failures)
        )
