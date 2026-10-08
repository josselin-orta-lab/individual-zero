from __future__ import annotations

import unittest

from lab.battery_scenarios import (
    BatteryScenarioConfig,
    BatterySituation,
    build_battery_scenario,
)
from lab.world import Position


def config() -> BatteryScenarioConfig:
    return BatteryScenarioConfig(
        version="battery-p54-test-v1",
        patience_origin=Position(5, 5),
        patience_berry_kind="berry_a",
        risk_shortcut_zone=Position(6, 5),
        threat_creature_position=Position(8, 5),
        exploration_resource_position=Position(10, 10),
        exploration_resource_kind="wood",
        perseverance_primitive="se_deplacer",
        perseverance_failure_schedule=(True, True, False, True, False),
        max_steps_by_situation={
            "patience": 30,
            "risk_taking": 30,
            "exploration": 30,
            "threat_response": 30,
            "perseverance": 30,
        },
    )


class BatteryScenarioTests(unittest.TestCase):
    def test_all_five_normative_situations_have_versioned_plans(self) -> None:
        plans = [
            build_battery_scenario(situation=situation, config=config())
            for situation in BatterySituation
        ]

        self.assertEqual(
            {plan.situation for plan in plans},
            set(BatterySituation),
        )
        for plan in plans:
            self.assertEqual(plan.version, "battery-p54-test-v1")
            self.assertEqual(plan.termination, {"max_steps": 30})

    def test_patience_mechanism_uses_normative_one_vs_three_after_20_steps(self) -> None:
        plan = build_battery_scenario(
            situation=BatterySituation.PATIENCE,
            config=config(),
        )

        self.assertEqual(plan.mechanism["immediate_quantity"], 1)
        self.assertEqual(plan.mechanism["delayed_quantity"], 3)
        self.assertEqual(plan.mechanism["delay_steps"], 20)
        self.assertEqual(plan.events[0].t_monde, 1)
        self.assertEqual(plan.events[1].t_monde, 21)

    def test_perseverance_failure_schedule_is_explicit_not_random(self) -> None:
        plan = build_battery_scenario(
            situation=BatterySituation.PERSEVERANCE,
            config=config(),
        )

        self.assertEqual(plan.mechanism["tested_primitive"], "se_deplacer")
        self.assertEqual(
            plan.mechanism["action_failure_schedule"],
            [True, True, False, True, False],
        )
        self.assertEqual(len(plan.events), 1)
        self.assertEqual(plan.events[0].operation, "set_action_failure_schedule")
        self.assertEqual(
            plan.events[0].payload["primitive"],
            "se_deplacer",
        )

    def test_same_config_builds_identical_plan(self) -> None:
        first = build_battery_scenario(
            situation=BatterySituation.THREAT_RESPONSE,
            config=config(),
        )
        second = build_battery_scenario(
            situation=BatterySituation.THREAT_RESPONSE,
            config=config(),
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
