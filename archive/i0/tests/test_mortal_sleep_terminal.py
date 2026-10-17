"""MVP v1.3 death during actual Stage-10 sleep and reduced-perception reflex.

The physics remains WorldBody's unmodified rule set. A sleeping individual's
terminal world transition is not erased, nor credited as a waking memory or TD
reward. The historical reference fixture remains unchanged by default.
"""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus
from lab.stage10_reference_fixture import build_stage10_reference_runtime


class Stage10MortalSleepTests(unittest.TestCase):
    @staticmethod
    def sleeping():
        runtime = build_stage10_reference_runtime(start_fatigued=True)
        runtime.stage3.substrate.enable_mortal_world()
        first = runtime.run_step()
        assert first.execution_status == "applied"
        assert first.command_primitive == "dormir"
        assert runtime.scheduler.t_monde == 1
        return runtime

    def test_fatal_sleep_step_preserves_world_and_never_recovers_fatigue(self):
        runtime = self.sleeping()
        runtime.world.apply_scenario_event(
            "set_lethal_zone", {
                "position": runtime.world.position.as_dict(),
                "active": True,
            },
        )
        previous_q = runtime.q_active.export_causal_state()
        fatigue = runtime.sleep_health.fatigue
        result = runtime.run_step()
        self.assertEqual(result.source, "sleep")
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(result.command_primitive, "dormir")
        self.assertEqual(runtime.scheduler.t_monde, 2)
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(runtime.sleep_health.fatigue, fatigue)
        self.assertEqual(runtime.q_active.export_causal_state(), previous_q)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        self.assertEqual(runtime.bench.metrics.lethal_rollbacks, 0)
        self.assertIsNone(runtime.scheduler.active_attempt)
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_fatal_sleep_reflex_does_not_start_waking_cognition(self):
        runtime = self.sleeping()
        runtime.world.apply_scenario_event(
            "place_creature", {"position": {"x": 3, "y": 2}},
        )
        runtime.world.apply_scenario_event(
            "set_lethal_zone", {
                "position": {"x": 1, "y": 2}, "active": True,
            },
        )
        previous_q = runtime.q_active.export_causal_state()
        result = runtime.run_step()
        self.assertEqual(result.source, "reflex")
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(result.cycles_used, 0)
        self.assertEqual(runtime.world.position.as_dict(), {"x": 1, "y": 2})
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(runtime.q_active.export_causal_state(), previous_q)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        self.assertIsNone(runtime.scheduler.active_attempt)
        with self.assertRaises(RuntimeError):
            runtime.run_step()


if __name__ == "__main__":
    unittest.main()
