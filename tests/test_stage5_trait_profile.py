from __future__ import annotations

import unittest

from lab.battery_scenarios import BatterySituation
from lab.trait_battery import BatteryAdministration, BatteryScore
from lab.trait_profile import (
    ReliabilityProtocol,
    assess_reliability,
    build_trait_profile,
)


def administration(
    situation: BatterySituation,
    value: float | None,
    *,
    status: str = "scored",
) -> BatteryAdministration:
    return BatteryAdministration(
        copy_id=f"copy:{situation.value}",
        copy_snapshot_id=f"snapshot:{situation.value}",
        situation=situation,
        scenario_version="battery-v1",
        start_t_monde=0,
        stop_t_monde=3,
        steps_run=3,
        stop_reason="max_steps",
        score=BatteryScore(
            situation=situation,
            status=status,
            value=value,
            measure=situation.value,
            detail={},
        ),
    )


class TraitProfileTests(unittest.TestCase):
    def test_complete_profile_requires_all_numeric_scores_and_intervals(self) -> None:
        rows = [
            administration(BatterySituation.PATIENCE, 1.0),
            administration(BatterySituation.RISK_TAKING, 0.0),
            administration(BatterySituation.EXPLORATION, 1.0),
            administration(BatterySituation.THREAT_RESPONSE, 3.0),
            administration(BatterySituation.PERSEVERANCE, 4.0),
        ]
        intervals = {
            "patience": (0.8, 1.0),
            "risk_taking": (0.0, 0.2),
            "exploration": (0.8, 1.0),
            "threat_response": (2.5, 3.5),
            "perseverance": (3.5, 4.5),
        }

        profile = build_trait_profile(
            individual_id="i0",
            age_t_monde=1500,
            battery_version="battery-v1",
            administrations=rows,
            confidence_intervals=intervals,
        )

        self.assertTrue(profile.complete)
        self.assertEqual(profile.estimates["perseverance"].mean, 4.0)

    def test_current_unexpressible_perseverance_keeps_profile_incomplete(self) -> None:
        rows = [
            administration(BatterySituation.PATIENCE, 1.0),
            administration(BatterySituation.RISK_TAKING, 0.0),
            administration(BatterySituation.EXPLORATION, 1.0),
            administration(BatterySituation.THREAT_RESPONSE, 3.0),
            administration(
                BatterySituation.PERSEVERANCE,
                None,
                status="mechanism_not_expressible_stage5",
            ),
        ]
        intervals = {
            "patience": (0.8, 1.0),
            "risk_taking": (0.0, 0.2),
            "exploration": (0.8, 1.0),
            "threat_response": (2.5, 3.5),
            "perseverance": None,
        }

        profile = build_trait_profile(
            individual_id="i0",
            age_t_monde=1500,
            battery_version="battery-v1",
            administrations=rows,
            confidence_intervals=intervals,
        )

        self.assertFalse(profile.complete)
        self.assertEqual(
            profile.estimates["perseverance"].status,
            "not_estimable",
        )

    def test_reliability_gate_has_no_hidden_threshold_or_icc_variant(self) -> None:
        protocol = ReliabilityProtocol(
            version="analysis-v1",
            method="ICC variant preregistered externally",
            threshold=0.75,
        )

        passed = assess_reliability(observed_icc=0.80, protocol=protocol)
        failed = assess_reliability(observed_icc=0.70, protocol=protocol)

        self.assertTrue(passed.passed)
        self.assertFalse(failed.passed)
        self.assertEqual(passed.threshold, 0.75)
        self.assertEqual(
            passed.method,
            "ICC variant preregistered externally",
        )


if __name__ == "__main__":
    unittest.main()
