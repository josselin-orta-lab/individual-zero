"""No public WorldBody mutation API can advance a dead/halted individual.

Normative v1.3.1 M-01, M-03, M-04: physical effects are final, not
snapshotted away. Historical fixture worlds retain their original behavior.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from lab.mortal_execution import MortalStatus
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command, WorldBody


class MortalWorldTerminalFreezeTests(unittest.TestCase):
    @staticmethod
    def instance():
        return build_stage4_reference_runtime(autonomous_mortal=True)

    @staticmethod
    def assert_cannot_mutate(world):
        before = world.export_causal_state()
        with unittest.TestCase().assertRaisesRegex(RuntimeError, "terminal or halted"):
            world.apply(Command("attendre"), t_monde=2)
        with unittest.TestCase().assertRaisesRegex(RuntimeError, "terminal or halted"):
            world.apply_scenario_event("set_danger_zone", {
                "position": {"x": 3, "y": 3}, "active": True,
            })
        with unittest.TestCase().assertRaisesRegex(RuntimeError, "terminal or halted"):
            world.apply_scenario_batch_atomically((
                ("set_danger_zone", {
                    "position": {"x": 3, "y": 3}, "active": True,
                }),
            ))
        assert world.export_causal_state() == before

    def test_fatal_world_transition_matches_unmodified_world_and_freezes(self):
        individual = self.instance()
        world = individual.world
        baseline = WorldBody(config=world.config, layout=world._layout)
        hazard = {"position": world.position.as_dict(), "active": True}
        world.apply_scenario_event("set_lethal_zone", hazard)
        baseline.apply_scenario_event("set_lethal_zone", hazard)
        substrate = individual.stage3.substrate
        substrate.open_step()
        fatal = substrate.execute(Command("attendre"))
        raw = baseline.apply(Command("attendre"), t_monde=1)
        self.assertEqual(fatal.status, "dead")
        self.assertEqual(substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(fatal.transition.as_dict(), raw.as_dict())
        self.assertEqual(world.export_causal_state(), baseline.export_causal_state())
        self.assertIsNone(individual.scheduler.active_attempt)
        self.assert_cannot_mutate(world)
        with self.assertRaisesRegex(RuntimeError, "dead or halted"):
            substrate.open_step()

    def test_technical_halt_also_protects_uncertain_physical_state(self):
        individual = self.instance()
        substrate = individual.stage3.substrate
        substrate.open_step()
        with patch.object(individual.world, "apply", side_effect=OSError("injected physics failure")):
            with self.assertRaisesRegex(OSError, "physics failure"):
                substrate.execute(Command("attendre"))
        self.assertEqual(substrate.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assert_cannot_mutate(individual.world)
        with self.assertRaisesRegex(RuntimeError, "dead or halted"):
            substrate.open_step()

    def test_independent_legacy_world_is_not_frozen(self):
        individual = build_stage4_reference_runtime()
        world = individual.world
        world.apply(Command("attendre"), t_monde=1)
        world.apply(Command("attendre"), t_monde=2)
        self.assertNotEqual(world.export_causal_state(), {})


if __name__ == "__main__":
    unittest.main()
