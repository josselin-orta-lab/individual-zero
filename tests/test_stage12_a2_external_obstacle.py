"""A2 external obstacle software gate. No autonomous cognition claimed."""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from lab.injected_scenario import ScenarioEvent, InjectedScenario
from lab.journal import HashChainedJournal
from lab.world import WorldBody, Position
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class A2ExternalObstacleTests(unittest.TestCase):
    def make_world(self):
        baseline = build_stage11_reference_runtime()
        start = baseline.world.position
        target = Position(start.x + 1, start.y)
        world = WorldBody(
            config=baseline.world.config,
            layout=replace(
                baseline.world._layout,
                obstacles=frozenset(), water_sources=frozenset({target}),
            ),
        )
        return world, target

    def test_external_obstacle_changes_real_movement_and_next_perception(self):
        world, target = self.make_world()
        perception = SymbolicPerception()
        before = perception.capture(
            local_state=world.capture_local(t_monde=1).as_dict(),
            telemetry=world.telemetry(),
        )
        self.assertTrue(next(c.passable for c in before.adjacent if c.direction == "east"))
        world.forbid_historical_restore()
        journal = HashChainedJournal()
        scheduled = InjectedScenario(
            scenario_id="a2-physical-gate", version="v1",
            events=(ScenarioEvent(
                t_monde=1, sequence=0, operation="set_obstacle",
                payload={"position": {"x": target.x, "y": target.y}, "active": True},
            ),), journal=journal,
        )
        scheduled.apply_for_step_irreversible(t_monde=1, world=world)
        movement = world.apply(PrimitiveCommand(
            "se_deplacer", {"direction": "east"}), t_monde=1,
        )
        after = perception.capture(
            local_state=world.capture_local(t_monde=2).as_dict(),
            telemetry=world.telemetry(),
        )
        self.assertEqual(movement.effects["movement"], "blocked")
        self.assertEqual((before.x, before.y), (after.x, after.y))
        self.assertFalse(next(c.passable for c in after.adjacent if c.direction == "east"))
        self.assertTrue(journal.verify())
        self.assertEqual(
            [r.causal_event["kind"] for r in journal.entries],
            ["external_input_received", "external_input_applied"],
        )

    def test_reject_invalid_and_occupied_cells_without_publishing(self):
        for payload in (
            {"position": {"x": 2, "y": 2}, "active": True},
            {"position": {"x": 3, "y": 2}, "active": 1},
            {"position": {"x": 3, "y": 2}, "active": True, "label": "world"},
        ):
            with self.subTest(payload=payload):
                world, _ = self.make_world()
                world.forbid_historical_restore()
                before = world.export_causal_state()
                with self.assertRaises(ValueError):
                    world.apply_scenario_batch_atomically((
                        ("set_obstacle", payload),
                    ))
                self.assertEqual(before, world.export_causal_state())

    def test_batch_invalid_second_event_is_atomic(self):
        world, target = self.make_world()
        world.forbid_historical_restore()
        previous = world.export_causal_state()
        with self.assertRaises(ValueError):
            world.apply_scenario_batch_atomically((
                ("set_obstacle", {"position": target.as_dict(), "active": True}),
                ("set_obstacle", {"position": target.as_dict(), "active": "yes"}),
            ))
        self.assertEqual(world.export_causal_state(), previous)

    def test_preexisting_obstacle_is_perceived_as_blocked(self):
        world, target = self.make_world()
        world.apply_scenario_event(
            "set_obstacle", {"position": target.as_dict(), "active": True},
        )
        visible = world.capture_local(t_monde=1)
        self.assertFalse(next(c.passable for c in visible.adjacent if c.direction == "east"))


if __name__ == "__main__":
    unittest.main()
