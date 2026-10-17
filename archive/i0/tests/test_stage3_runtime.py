from __future__ import annotations

import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from i0.interfaces import PrimitiveCommand
from i0.modules import PreparedCommand, StaticSafetyFacts
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage3_runtime import Stage3Runtime
from lab.world import (
    BerryEffect,
    BodyState,
    Position,
    ToolRecipe,
    WorldLayout,
    WorldPhysicsConfig,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="stage3-runtime-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={
            "se_deplacer": 0.0,
            "collecter": 0.0,
            "manger": 0.0,
            "boire": 0.0,
            "poser_une_pierre": 0.0,
            "fabriquer_outil": 0.0,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
        drink_water_gain=1.0,
        berry_effects={
            "berry_a": BerryEffect(1.0, 0.0),
            "berry_b": BerryEffect(1.0, -100.0),
        },
        creature_damage=0.0,
        danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


def runtime(
    *,
    layout: WorldLayout | None = None,
    facts: StaticSafetyFacts | None = None,
    lethal_max: int = 2,
) -> Stage3Runtime:
    return Stage3Runtime(
        config=physics(),
        layout=layout or WorldLayout(),
        phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        safety_config=SafetyProtocolConfig(
            version="stage3-safety-test-v1",
            lethal_max=lethal_max,
            mode="campaign",
        ),
        safety_facts=facts or StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
    )


class Stage3ReflexRuntimeTests(unittest.TestCase):
    def test_adjacent_creature_reflex_moves_away_without_deliberation(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
            )
        )
        instance.open_step()

        result = instance.run_step()

        self.assertTrue(result.reflex_triggered)
        self.assertEqual(result.source, "reflex")
        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(instance.world.position, Position(1, 2))
        self.assertEqual(instance.captures_this_step, 1)

        kinds = [entry.causal_event["kind"] for entry in instance.journal.entries]
        self.assertIn("reflex_proposed", kinds)
        self.assertIn("command_admitted", kinds)
        self.assertNotIn("reflex_refused", kinds)

    def test_vetoed_reflex_falls_back_to_wait_without_veto_choosing_action(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
            ),
            facts=StaticSafetyFacts(
                known_lethal_positions=frozenset({(1, 2)}),
            ),
        )
        instance.open_step()

        result = instance.run_step()

        self.assertTrue(result.reflex_triggered)
        self.assertEqual(result.source, "stage3_wait_stub")
        self.assertEqual(result.command, PrimitiveCommand("attendre"))
        self.assertEqual(instance.world.position, Position(2, 2))

        events = [entry.causal_event for entry in instance.journal.entries]
        vetoes = [
            event for event in events
            if event.get("kind") == "command_vetoed"
        ]
        self.assertEqual(len(vetoes), 1)
        self.assertEqual(
            vetoes[0]["data"]["rule_id"],
            "lethal_zone_movement",
        )
        self.assertEqual(
            vetoes[0]["data"]["policy_version"],
            "mvp-v1.2.1",
        )

    def test_lethal_reflex_is_rolled_back_and_not_replayed(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
                lethal_zones=frozenset({Position(1, 2)}),
            ),
        )
        instance.open_step()

        result = instance.run_step()

        self.assertTrue(result.reflex_triggered)
        self.assertEqual(result.source, "stage3_wait_stub")
        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(instance.world.position, Position(2, 2))
        self.assertEqual(instance.bench.metrics.lethal_transitions, 1)
        self.assertEqual(instance.bench.metrics.lethal_rollbacks, 1)

        kinds = [entry.causal_event["kind"] for entry in instance.journal.entries]
        self.assertEqual(kinds.count("reflex_proposed"), 1)

        autobiography = instance.substrate.autobiographical_view()
        self.assertEqual(len(autobiography), 2)
        self.assertEqual(autobiography[0]["primitive"], "attendre")

    def test_one_perceptual_capture_per_step(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
                lethal_zones=frozenset({Position(1, 2)}),
            ),
        )
        instance.open_step()
        instance.run_step()

        captures = [
            entry
            for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "perceptual_capture"
        ]
        self.assertEqual(len(captures), 1)


class Stage3ControlTraceTests(unittest.TestCase):
    def test_forbidden_prepared_command_is_never_sent(self) -> None:
        instance = runtime(
            facts=StaticSafetyFacts(
                known_lethal_positions=frozenset({(3, 2)}),
            )
        )
        instance.open_step()
        prepared = PreparedCommand(
            command=PrimitiveCommand(
                "se_deplacer",
                {"direction": "east"},
            ),
            source="test_decision",
        )

        admission, execution = instance.attempt_prepared(prepared)

        self.assertFalse(admission.ok)
        self.assertIsNone(execution)

        sent = [
            entry for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "command_experienced"
        ]
        self.assertEqual(sent, [])

    def test_every_sent_command_has_prior_admission_trace(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
            )
        )
        instance.open_step()
        instance.run_step()

        entries = instance.journal.entries
        admissions = {}
        for index, entry in enumerate(entries):
            event = entry.causal_event
            if event.get("kind") == "command_admitted":
                admissions[event["data"]["command_hash"]] = index

        sent_count = 0
        for index, entry in enumerate(entries):
            event = entry.causal_event
            if event.get("kind") != "command_experienced":
                continue
            sent_count += 1
            command_hash = event["command_hash"]
            self.assertIn(command_hash, admissions)
            self.assertLess(admissions[command_hash], index)

        self.assertEqual(sent_count, 1)

    def test_same_stage3_run_replays_identically(self) -> None:
        def execute() -> tuple[bytes, dict[str, object]]:
            instance = runtime(
                layout=WorldLayout(
                    creatures=frozenset({Position(3, 2)}),
                )
            )
            for _ in range(5):
                instance.open_step()
                result = instance.run_step()
                self.assertIn(result.execution_status, {"applied", "safety_block"})
            return (
                instance.journal.canonical_bytes(),
                instance.substrate.causal_fingerprint(),
            )

        journal_a, state_a = execute()
        journal_b, state_b = execute()

        self.assertEqual(journal_a, journal_b)
        self.assertEqual(state_a, state_b)


if __name__ == "__main__":
    unittest.main()
