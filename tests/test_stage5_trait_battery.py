from __future__ import annotations

import unittest

from lab.battery_scenarios import (
    BatteryScenarioConfig,
    BatterySituation,
    build_battery_scenario,
)
from lab.stage5_reference_fixture import build_stage5_reference_runtime
from lab.trait_battery import administer_battery_situation
from lab.world import Position


def battery_config() -> BatteryScenarioConfig:
    return BatteryScenarioConfig(
        version="stage5-battery-test-v1",
        patience_origin=Position(2, 2),
        patience_berry_kind="berry_a",
        risk_shortcut_zone=Position(3, 2),
        threat_creature_position=Position(3, 2),
        exploration_resource_position=Position(5, 2),
        exploration_resource_kind="berry_a",
        perseverance_primitive="se_deplacer",
        perseverance_failure_schedule=(True, True, False),
        max_steps_by_situation={
            "patience": 3,
            "risk_taking": 3,
            "exploration": 3,
            "threat_response": 3,
            "perseverance": 6,
        },
    )


def owner_state(runtime):
    return {
        owner.owner_id: owner.export_causal_state()
        for owner in runtime.causal_owners
    }


class Stage5TraitBatteryTests(unittest.TestCase):
    def test_every_situation_runs_on_disposable_copy_without_parent_reinjection(self) -> None:
        parent = build_stage5_reference_runtime()
        for _ in range(2):
            parent.run_step()
        state_before = owner_state(parent)

        results = []
        for situation in BatterySituation:
            plan = build_battery_scenario(
                situation=situation,
                config=battery_config(),
            )
            result = administer_battery_situation(
                parent,
                plan=plan,
                administration_ref=f"admin:{situation.value}",
            )
            results.append(result)

        self.assertEqual(owner_state(parent), state_before)
        self.assertEqual(
            {result.situation for result in results},
            set(BatterySituation),
        )
        self.assertTrue(all(result.copy_id != parent.individual_id for result in results))
        self.assertTrue(all(result.steps_run <= 3 for result in results))

    def test_threat_response_produces_observable_flight_score(self) -> None:
        parent = build_stage5_reference_runtime()
        plan = build_battery_scenario(
            situation=BatterySituation.THREAT_RESPONSE,
            config=battery_config(),
        )

        result = administer_battery_situation(
            parent,
            plan=plan,
            administration_ref="threat:0",
        )

        self.assertEqual(result.score.status, "scored")
        self.assertEqual(result.score.measure, "flight_distance")
        self.assertIsNotNone(result.score.value)
        self.assertGreaterEqual(result.score.value, 1.0)

    def test_risk_and_exploration_scores_are_bench_observations(self) -> None:
        for situation, measure in (
            (BatterySituation.RISK_TAKING, "shortcut_choice"),
            (BatterySituation.EXPLORATION, "unknown_zone_entry"),
        ):
            parent = build_stage5_reference_runtime()
            plan = build_battery_scenario(
                situation=situation,
                config=battery_config(),
            )
            result = administer_battery_situation(
                parent,
                plan=plan,
                administration_ref=f"{situation.value}:0",
            )
            self.assertEqual(result.score.status, "scored")
            self.assertEqual(result.score.measure, measure)
            self.assertIn(result.score.value, (0.0, 1.0))

    def test_perseverance_uses_explicit_forced_failure_mechanism(self) -> None:
        parent = build_stage5_reference_runtime()
        plan = build_battery_scenario(
            situation=BatterySituation.PERSEVERANCE,
            config=battery_config(),
        )

        result = administer_battery_situation(
            parent,
            plan=plan,
            administration_ref="perseverance:0",
        )

        self.assertIn(result.score.status, {"scored", "right_censored"})
        self.assertEqual(
            result.score.measure,
            "attempts_before_abandonment",
        )
        self.assertEqual(
            result.score.detail["tested_primitive"],
            "se_deplacer",
        )
        self.assertGreaterEqual(
            int(result.score.detail["forced_failures_observed"]),
            1,
        )
        if result.score.status == "scored":
            self.assertIsNotNone(result.score.value)
            self.assertGreaterEqual(result.score.value, 1.0)
        else:
            self.assertIsNone(result.score.value)

    def test_same_battery_administration_is_deterministic(self) -> None:
        def execute():
            parent = build_stage5_reference_runtime()
            plan = build_battery_scenario(
                situation=BatterySituation.THREAT_RESPONSE,
                config=battery_config(),
            )
            result = administer_battery_situation(
                parent,
                plan=plan,
                administration_ref="deterministic:0",
            )
            return result

        self.assertEqual(execute(), execute())


if __name__ == "__main__":
    unittest.main()
