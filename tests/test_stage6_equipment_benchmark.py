from __future__ import annotations

import unittest

from i0.equipment import (
    EquipmentCorpus,
    EquipmentCorpusExample,
    train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from lab.equipment_benchmark import (
    EquipmentEquivalenceTolerances,
    benchmark_equipment,
    require_equivalent_versions,
)

from test_stage6_equipment import state


def training_corpus() -> EquipmentCorpus:
    return EquipmentCorpus(
        version="bench-corpus-v1",
        examples=(
            EquipmentCorpusExample(
                family="movement_free",
                state=state(x=2),
                command=PrimitiveCommand(
                    "se_deplacer",
                    {"direction": "east"},
                ),
                observed_next_state=state(x=3),
                terminal=False,
            ),
        ),
    )


def tolerances() -> EquipmentEquivalenceTolerances:
    return EquipmentEquivalenceTolerances(
        version="bench-tolerance-v1",
        overall_error_max=0.0,
        unavailable_rate_max=0.0,
        per_family_error_max={"movement_free": 0.0},
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


class EquipmentBenchmarkTests(unittest.TestCase):
    def test_exact_version_passes_every_conjunctive_criterion(self) -> None:
        corpus = training_corpus()
        model = train_exact_transition_table(
            corpus=corpus,
            equipment_version="E-v1",
        )

        result = benchmark_equipment(
            equipment=model,
            corpus=corpus,
            tolerances=tolerances(),
        )

        self.assertTrue(result.equivalent)
        self.assertEqual(result.failed_criteria, ())
        self.assertEqual(result.overall_error, 0.0)
        self.assertEqual(result.unavailable_rate, 0.0)
        self.assertEqual(result.calibration_brier, 0.0)

    def test_unseen_benchmark_input_fails_coverage_and_error(self) -> None:
        model = train_exact_transition_table(
            corpus=training_corpus(),
            equipment_version="E-v1",
        )
        benchmark = EquipmentCorpus(
            version="unseen-bench-v1",
            examples=(
                EquipmentCorpusExample(
                    family="movement_free",
                    state=state(x=5),
                    command=PrimitiveCommand(
                        "se_deplacer",
                        {"direction": "east"},
                    ),
                    observed_next_state=state(x=6),
                    terminal=False,
                ),
            ),
        )

        result = benchmark_equipment(
            equipment=model,
            corpus=benchmark,
            tolerances=tolerances(),
        )

        self.assertFalse(result.equivalent)
        self.assertIn("overall_error", result.failed_criteria)
        self.assertIn("unavailable_rate", result.failed_criteria)

    def test_three_versions_must_each_pass(self) -> None:
        corpus = training_corpus()
        results = [
            benchmark_equipment(
                equipment=train_exact_transition_table(
                    corpus=corpus,
                    equipment_version=version,
                ),
                corpus=corpus,
                tolerances=tolerances(),
            )
            for version in ("E-v1", "E-v2", "E-v3")
        ]

        require_equivalent_versions(
            results=results,
            required_versions=("E-v1", "E-v2", "E-v3"),
        )

    def test_missing_version_cannot_be_called_equivalent(self) -> None:
        corpus = training_corpus()
        result = benchmark_equipment(
            equipment=train_exact_transition_table(
                corpus=corpus,
                equipment_version="E-v1",
            ),
            corpus=corpus,
            tolerances=tolerances(),
        )

        with self.assertRaisesRegex(ValueError, "missing equipment benchmark"):
            require_equivalent_versions(
                results=(result,),
                required_versions=("E-v1", "E-v2", "E-v3"),
            )


if __name__ == "__main__":
    unittest.main()
