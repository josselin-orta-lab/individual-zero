"""Once a mortal-world instance starts, its public physical past is immutable.

Forward external batches remain possible through an independent candidate,
without giving callers a generic historical WorldBody restore capability.
"""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus, MortalWorldBoundary
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command, WorldBody, WorldLayout


class ForwardOnlyWorldTests(unittest.TestCase):
    def make_mortal(self):
        runtime = build_stage4_reference_runtime()
        runtime.stage3.substrate.enable_mortal_world()
        return runtime

    def test_direct_import_of_earlier_world_is_forbidden_before_death(self):
        runtime = self.make_mortal()
        before = runtime.world.export_causal_state()
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        committed = runtime.world.export_causal_state()
        self.assertNotEqual(committed["body"], before["body"])
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            runtime.world.restore_causal_state(before)
        self.assertEqual(runtime.world.export_causal_state(), committed)
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.ACTIVE)

    def test_direct_import_cannot_resurrect_fatal_instance(self):
        runtime = self.make_mortal()
        before = runtime.world.export_causal_state()
        initial = runtime.world.position
        for x, y in (
            (initial.x, initial.y), (initial.x - 1, initial.y),
            (initial.x + 1, initial.y),
            (initial.x, initial.y - 1),
            (initial.x, initial.y + 1),
        ):
            runtime.world.apply_scenario_event(
                "set_lethal_zone",
                {"position": {"x": x, "y": y}, "active": True},
            )
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "dead")
        final = runtime.world.export_causal_state()
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            runtime.world.restore_causal_state(before)
        self.assertEqual(runtime.world.export_causal_state(), final)
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_independent_copy_can_import_state_without_rewinding_parent(self):
        runtime = self.make_mortal()
        runtime.run_step()
        parent = runtime.world.export_causal_state()
        copy = WorldBody(config=runtime.world.config, layout=runtime.world._layout)
        copy.restore_causal_state(parent)
        self.assertEqual(copy.export_causal_state(), parent)
        copy.apply_scenario_event(
            "set_danger_zone",
            {"position": {"x": 3, "y": 3}, "active": True},
        )
        self.assertNotEqual(copy.export_causal_state(), parent)
        self.assertEqual(runtime.world.export_causal_state(), parent)
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            runtime.world.restore_causal_state(copy.export_causal_state())

    def test_prepared_external_batch_matches_sequential_physics_without_restore(self):
        runtime = self.make_mortal()
        world = runtime.world
        comparator = WorldBody(config=world.config, layout=world._layout)
        config_before = world.config
        operations = (
            ("set_danger_zone", {
                "position": {"x": 3, "y": 3}, "active": True,
            }),
            ("place_resource", {
                "position": {"x": 2, "y": 2},
                "kind": "wood", "quantity": 2,
            }),
            ("set_action_failure_schedule", {
                "primitive": "attendre", "schedule": [False, True],
            }),
        )
        for operation, payload in operations:
            comparator.apply_scenario_event(operation, payload)
        world.apply_scenario_batch_atomically(operations)
        self.assertIs(world.config, config_before)
        self.assertEqual(
            world.export_causal_state(), comparator.export_causal_state(),
        )
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            world.restore_causal_state(comparator.export_causal_state())
        observed = runtime.stage3.substrate
        observed.open_step()
        actual = observed.execute(Command("attendre"))
        expected = comparator.apply(Command("attendre"), t_monde=1)
        self.assertEqual(actual.status, "applied")
        self.assertEqual(actual.transition.as_dict(), expected.as_dict())
        self.assertEqual(
            world.export_causal_state(), comparator.export_causal_state(),
        )

    def test_invalid_second_external_operation_does_not_partially_publish(self):
        runtime = self.make_mortal()
        before = runtime.world.export_causal_state()
        operations = (
            ("set_danger_zone", {
                "position": {"x": 3, "y": 3}, "active": True,
            }),
            ("place_resource", {
                "position": {"x": 2, "y": 2},
                "kind": "wood", "quantity": -1,
            }),
        )
        with self.assertRaises(ValueError):
            runtime.world.apply_scenario_batch_atomically(operations)
        self.assertEqual(runtime.world.export_causal_state(), before)
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            runtime.world.restore_causal_state(before)

    def test_historical_fixture_world_keeps_independent_loading_interface(self):
        cfg = build_stage4_reference_runtime().world.config
        layout = WorldLayout()
        source = WorldBody(config=cfg, layout=layout)
        before = source.export_causal_state()
        source.apply_scenario_event(
            "set_lethal_zone",
            {"position": {"x": 3, "y": 3}, "active": True},
        )
        source.restore_causal_state(before)
        self.assertEqual(source.export_causal_state(), before)
        with self.assertRaisesRegex(RuntimeError, "requires mortal"):
            source.apply_scenario_batch_atomically((
                ("set_danger_zone", {
                    "position": {"x": 3, "y": 3}, "active": True,
                }),
            ))

    def test_mortal_boundary_directly_seals_the_world_not_only_snapshot_manager(self):
        cfg = build_stage4_reference_runtime().world.config
        world = WorldBody(config=cfg, layout=WorldLayout())
        before = world.export_causal_state()
        boundary = MortalWorldBoundary(world=world)
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            world.restore_causal_state(before)
        result = boundary.execute(Command("attendre"), t_monde=1)
        self.assertEqual(result.status, "applied")
        with self.assertRaisesRegex(RuntimeError, "historical WorldBody"):
            world.restore_causal_state(before)
        self.assertEqual(boundary.status, MortalStatus.ACTIVE)


if __name__ == "__main__":
    unittest.main()
