from __future__ import annotations

import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from lab.determinism import canonical_causal_bytes
from lab.injected_scenario import ScenarioEvent
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage2_runtime import ScriptedStage2Runtime
from lab.world import (
    BerryEffect,
    BodyState,
    Command,
    Position,
    ToolRecipe,
    WorldLayout,
    WorldPhysicsConfig,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="stage2-runtime-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(2, 2),
        food_decay_per_step=0.1,
        water_decay_per_step=0.2,
        action_energy_costs={
            "se_deplacer": 0.5,
            "collecter": 0.5,
            "manger": 0.2,
            "boire": 0.2,
            "poser_une_pierre": 0.5,
            "fabriquer_outil": 0.5,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=1.0,
        rest_integrity_gain=0.0,
        drink_water_gain=10.0,
        berry_effects={
            "berry_a": BerryEffect(5.0, 0.0),
            "berry_b": BerryEffect(5.0, -100.0),
        },
        creature_damage=10.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


def runtime(
    *,
    layout: WorldLayout | None = None,
    lethal_max: int = 2,
    mode: str = "campaign",
    scenario_events: tuple[ScenarioEvent, ...] = (),
) -> ScriptedStage2Runtime:
    return ScriptedStage2Runtime(
        config=physics(),
        layout=layout or WorldLayout(),
        phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        safety_config=SafetyProtocolConfig(
            version="stage2-safety-test-v1",
            lethal_max=lethal_max,
            mode=mode,
        ),
        scenario_id="stage2-test-scenario" if scenario_events else None,
        scenario_version="v1" if scenario_events else None,
        scenario_events=scenario_events,
    )


class Stage2RollbackTests(unittest.TestCase):
    def test_induced_death_restores_checkpoint_and_is_not_autobiographical(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                lethal_zones=frozenset({Position(3, 2)}),
            )
        )
        instance.open_step()
        before = instance.world.export_causal_state()
        first_attempt = instance.scheduler.active_attempt
        self.assertIsNotNone(first_attempt)

        result = instance.execute(
            Command("se_deplacer", {"direction": "east"})
        )

        self.assertEqual(result.status, "rolled_back")
        self.assertEqual(instance.world.export_causal_state(), before)
        self.assertEqual(instance.bench.metrics.lethal_transitions, 1)
        self.assertEqual(instance.bench.metrics.lethal_rollbacks, 1)
        self.assertEqual(instance.autobiographical_view(), ())

        resumed = instance.scheduler.active_attempt
        self.assertIsNotNone(resumed)
        self.assertEqual(resumed.t_monde, 1)
        self.assertNotEqual(resumed.attempt_ref, first_attempt.attempt_ref)

        safe = instance.execute(Command("attendre"))
        self.assertEqual(safe.status, "applied")

        autobiography = instance.autobiographical_view()
        self.assertEqual(len(autobiography), 2)
        self.assertEqual(autobiography[0]["primitive"], "attendre")
        self.assertFalse(instance.safety.is_masked(
            Command("se_deplacer", {"direction": "east"})
        ))

    def test_protocol_mask_rejects_same_lethal_command_during_resumption(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                lethal_zones=frozenset({Position(3, 2)}),
            )
        )
        instance.open_step()
        command = Command("se_deplacer", {"direction": "east"})

        first = instance.execute(command)
        second = instance.execute(command)

        self.assertEqual(first.status, "rolled_back")
        self.assertEqual(second.status, "masked")
        self.assertEqual(instance.bench.metrics.lethal_transitions, 1)
        self.assertEqual(instance.world.position, Position(2, 2))

    def test_exceeding_lethal_max_blocks_campaign_branch_and_alerts(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                lethal_zones=frozenset({
                    Position(3, 2),
                    Position(2, 3),
                }),
            ),
            lethal_max=1,
            mode="campaign",
        )
        instance.open_step()

        first = instance.execute(
            Command("se_deplacer", {"direction": "east"})
        )
        second = instance.execute(
            Command("se_deplacer", {"direction": "south"})
        )

        self.assertEqual(first.status, "rolled_back")
        self.assertEqual(second.status, "safety_block")
        self.assertTrue(instance.safety.blocked)
        self.assertFalse(instance.safety.suspended)
        self.assertEqual(instance.bench.metrics.lethal_transitions, 2)
        self.assertEqual(instance.bench.metrics.lethal_rollbacks, 2)
        self.assertEqual(instance.bench.metrics.safety_blocks, 1)
        self.assertEqual(instance.bench.metrics.operator_alerts, 1)
        self.assertEqual(instance.world.position, Position(2, 2))
        self.assertIsNone(instance.scheduler.active_attempt)

    def test_diagnostic_block_is_suspended_not_campaign_closed_semantics(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                lethal_zones=frozenset({
                    Position(3, 2),
                    Position(2, 3),
                }),
            ),
            lethal_max=1,
            mode="diagnostic",
        )
        instance.open_step()
        instance.execute(Command("se_deplacer", {"direction": "east"}))
        result = instance.execute(
            Command("se_deplacer", {"direction": "south"})
        )

        self.assertEqual(result.status, "safety_block")
        self.assertTrue(instance.safety.suspended)


class Stage2OracleLeakTests(unittest.TestCase):
    def test_oracle_canary_never_enters_individual_causal_or_autobiographical_state(self) -> None:
        instance = runtime(
            layout=WorldLayout(oracle_canary="STAGE2_ORACLE_CANARY")
        )
        truth = instance.bench.oracle_truth()
        self.assertEqual(truth["oracle_canary"], "STAGE2_ORACLE_CANARY")

        instance.open_step()
        result = instance.execute(Command("attendre"))
        self.assertEqual(result.status, "applied")

        causal = canonical_causal_bytes(instance.causal_fingerprint())
        autobiographical = canonical_causal_bytes(
            list(instance.autobiographical_view())
        )

        self.assertNotIn(b"STAGE2_ORACLE_CANARY", causal)
        self.assertNotIn(b"STAGE2_ORACLE_CANARY", autobiographical)


class Stage2ReplayTests(unittest.TestCase):
    def scripted_run(self, *, steps: int) -> ScriptedStage2Runtime:
        events = (
            ScenarioEvent(
                t_monde=2,
                sequence=0,
                operation="place_resource",
                payload={
                    "position": {"x": 2, "y": 2},
                    "kind": "wood",
                    "quantity": 2,
                },
            ),
            ScenarioEvent(
                t_monde=3,
                sequence=0,
                operation="place_creature",
                payload={"position": {"x": 4, "y": 4}},
            ),
        )
        instance = runtime(scenario_events=events)
        for _ in range(steps):
            instance.open_step()
            outcome = instance.execute(Command("attendre"))
            self.assertEqual(outcome.status, "applied")
        return instance

    def test_injected_scenario_replays_identically(self) -> None:
        first = self.scripted_run(steps=5)
        second = self.scripted_run(steps=5)

        self.assertEqual(
            first.journal.canonical_bytes(),
            second.journal.canonical_bytes(),
        )
        self.assertEqual(
            first.causal_fingerprint(),
            second.causal_fingerprint(),
        )
        self.assertTrue(first.journal.verify())
        self.assertTrue(second.journal.verify())

    def test_full_scripted_day_replays_identically(self) -> None:
        def run_day() -> tuple[bytes, dict[str, object]]:
            instance = runtime()
            for _ in range(300):
                instance.open_step()
                result = instance.execute(Command("attendre"))
                self.assertEqual(result.status, "applied")
            return instance.journal.canonical_bytes(), instance.causal_fingerprint()

        journal_a, state_a = run_day()
        journal_b, state_b = run_day()

        self.assertEqual(journal_a, journal_b)
        self.assertEqual(state_a, state_b)

    def test_scenario_input_is_logged_before_application(self) -> None:
        events = (
            ScenarioEvent(
                t_monde=1,
                sequence=0,
                operation="set_lethal_zone",
                payload={
                    "position": {"x": 3, "y": 2},
                    "active": True,
                },
            ),
        )
        instance = runtime(scenario_events=events)
        instance.open_step()

        kinds = [entry.causal_event["kind"] for entry in instance.journal.entries]

        self.assertIn("external_input_received", kinds)
        self.assertIn("external_input_applied", kinds)
        self.assertLess(
            kinds.index("external_input_received"),
            kinds.index("external_input_applied"),
        )


if __name__ == "__main__":
    unittest.main()
