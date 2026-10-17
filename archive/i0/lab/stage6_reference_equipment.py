"""Stage-6 software-reference equipment bundle.

The three exact-table versions are independent immutable artifacts trained from
the controlled software corpus. This fixture proves the versioning/equivalence
gate itself; it is not a scientific equipment-training result.

Spec: 12.5, P-46, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass

from i0.equipment import FrozenTableEquipment, train_exact_transition_table

from .equipment_benchmark import (
    EquipmentBenchmarkResult,
    EquipmentEquivalenceTolerances,
    benchmark_equipment,
    require_equivalent_versions,
)
from .equipment_corpus import REQUIRED_EQUIPMENT_FAMILIES
from .stage6_reference_corpus import build_stage6_reference_corpus


REFERENCE_EQUIPMENT_VERSIONS = ("E-v1-reference", "E-v2-reference", "E-v3-reference")


@dataclass(frozen=True, slots=True)
class Stage6ReferenceEquipmentBundle:
    models: tuple[FrozenTableEquipment, ...]
    benchmark_results: tuple[EquipmentBenchmarkResult, ...]
    tolerance_version: str

    def model(self, version: str) -> FrozenTableEquipment:
        for model in self.models:
            if model.version == version:
                return model
        raise KeyError(version)


def reference_equivalence_tolerances() -> EquipmentEquivalenceTolerances:
    return EquipmentEquivalenceTolerances(
        version="stage6-reference-equivalence-v1",
        overall_error_max=0.0,
        unavailable_rate_max=0.0,
        per_family_error_max={
            family: 0.0
            for family in sorted(REQUIRED_EQUIPMENT_FAMILIES)
        },
        per_horizon_error_max={1: 0.0},
        calibration_brier_max=0.0,
        systematic_bias_abs_max={
            "x": 0.0,
            "y": 0.0,
            "energy": 0.0,
            "food": 0.0,
            "water": 0.0,
            "integrity": 0.0,
        },
    )


def build_stage6_reference_equipment_bundle() -> Stage6ReferenceEquipmentBundle:
    corpus = build_stage6_reference_corpus()
    tolerances = reference_equivalence_tolerances()

    models = tuple(
        train_exact_transition_table(
            corpus=corpus,
            equipment_version=version,
        )
        for version in REFERENCE_EQUIPMENT_VERSIONS
    )
    results = tuple(
        benchmark_equipment(
            equipment=model,
            corpus=corpus,
            tolerances=tolerances,
        )
        for model in models
    )
    require_equivalent_versions(
        results=results,
        required_versions=REFERENCE_EQUIPMENT_VERSIONS,
    )
    return Stage6ReferenceEquipmentBundle(
        models=models,
        benchmark_results=results,
        tolerance_version=tolerances.version,
    )
