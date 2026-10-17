from __future__ import annotations

import unittest

from lab.battery_scenarios import BatterySituation
from lab.trait_battery import BatteryScore
from lab.trait_profiles import (
    ReliabilityConfig,
    TraitProfile,
    build_trait_profile,
    evaluate_test_retest,
)


def score(situation: BatterySituation, value: float | None, status: str = "scored"):
    return BatteryScore(
        situation=situation,
        status=status,
        value=value,
        measure=situation.value,
        detail={},
    )


def complete_profile(individual: str, administration: str, values: list[float]):
    return TraitProfile(
        version="profile-v1",
        individual_id=individual,
        administration_ref=administration,
        scores={
            situation.value: value
            for situation, value in zip(BatterySituation, values)
        },
        status="complete",
    )


class TraitProfileTests(unittest.TestCase):
    def test_profile_is_incomplete_when_one_battery_score_is_unavailable(self) -> None:
        scores = {
            situation: score(situation, 0.0)
            for situation in BatterySituation
        }
        scores[BatterySituation.PERSEVERANCE] = score(
            BatterySituation.PERSEVERANCE,
            None,
            status="mechanism_not_expressible_stage5",
        )

        profile = build_trait_profile(
            version="profile-v1",
            individual_id="i0-a",
            administration_ref="day-5",
            scores=scores,
        )

        self.assertEqual(profile.status, "incomplete")
        self.assertEqual(profile.missing, ("perseverance",))
        self.assertNotIn("perseverance", profile.scores)

    def test_perfect_rank_stability_produces_icc_one(self) -> None:
        profiles = {
            "a": [
                complete_profile("a", "r1", [0, 0, 0, 1, 1]),
                complete_profile("a", "r2", [0, 0, 0, 1, 1]),
            ],
            "b": [
                complete_profile("b", "r1", [1, 1, 1, 3, 3]),
                complete_profile("b", "r2", [1, 1, 1, 3, 3]),
            ],
            "c": [
                complete_profile("c", "r1", [2, 2, 2, 5, 5]),
                complete_profile("c", "r2", [2, 2, 2, 5, 5]),
            ],
        }

        report = evaluate_test_retest(
            profiles_by_individual=profiles,
            config=ReliabilityConfig(
                version="rel-v1",
                method="icc_3_1",
                threshold=0.8,
            ),
        )

        self.assertTrue(report.evaluable)
        self.assertTrue(report.passes)
        self.assertTrue(all(item.icc == 1.0 for item in report.traits))

    def test_incomplete_profile_prevents_reliability_gate(self) -> None:
        complete = complete_profile("a", "r1", [0, 0, 0, 1, 1])
        incomplete = TraitProfile(
            version="profile-v1",
            individual_id="a",
            administration_ref="r2",
            scores={
                "patience": 0.0,
                "risk_taking": 0.0,
                "exploration": 0.0,
                "threat_response": 1.0,
            },
            status="incomplete",
            missing=("perseverance",),
        )
        other = [
            complete_profile("b", "r1", [1, 1, 1, 3, 3]),
            complete_profile("b", "r2", [1, 1, 1, 3, 3]),
        ]

        report = evaluate_test_retest(
            profiles_by_individual={
                "a": [complete, incomplete],
                "b": other,
            },
            config=ReliabilityConfig(
                version="rel-v1",
                method="icc_3_1",
                threshold=0.8,
            ),
        )

        self.assertFalse(report.evaluable)
        perseverance = next(
            item for item in report.traits if item.trait == "perseverance"
        )
        self.assertIsNone(perseverance.passes_threshold)

    def test_zero_between_subject_variance_is_not_called_perfect_reliability(self) -> None:
        profiles = {
            "a": [
                complete_profile("a", "r1", [1, 1, 1, 1, 1]),
                complete_profile("a", "r2", [1, 1, 1, 1, 1]),
            ],
            "b": [
                complete_profile("b", "r1", [1, 1, 1, 1, 1]),
                complete_profile("b", "r2", [1, 1, 1, 1, 1]),
            ],
        }

        report = evaluate_test_retest(
            profiles_by_individual=profiles,
            config=ReliabilityConfig(
                version="rel-v1",
                method="icc_3_1",
                threshold=0.8,
            ),
        )

        self.assertFalse(report.evaluable)
        self.assertTrue(
            all(item.status.startswith("not_evaluable:") for item in report.traits)
        )

    def test_reliability_method_and_threshold_are_explicit(self) -> None:
        with self.assertRaises(ValueError):
            ReliabilityConfig(
                version="rel-v1",
                method="unspecified",
                threshold=0.8,
            ).validate()


if __name__ == "__main__":
    unittest.main()
