"""Actual Stage7/10/11 parity after switching Memory from log scans to a queue.

The old technical log remains temporarily for Stage10 cut proofs and other
consumers, but Stage7 Memory does not need to enumerate its complete history.
"""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus
from lab.stage7_reference_fixture import build_stage7_reference_runtime
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime


def start(runtime, *, compact: bool) -> None:
    substrate = runtime.stage3.substrate
    substrate.enable_mortal_world()
    if compact:
        substrate.enable_compact_memory_delivery(
            policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            max_pending_events=1024,
        )


class CompactMemoryIntegrationTests(unittest.TestCase):
    def compare_lives(self, builder, steps: int) -> None:
        original, compact = builder(), builder()
        start(original, compact=False)
        start(compact, compact=True)
        for step in range(1, steps + 1):
            old_result = original.run_step()
            new_result = compact.run_step()
            with self.subTest(step=step, runtime=type(original).__name__):
                self.assertEqual(
                    (new_result.execution_status, new_result.command_primitive),
                    (old_result.execution_status, old_result.command_primitive),
                )
                self.assertEqual(
                    compact.world.export_causal_state(),
                    original.world.export_causal_state(),
                )
                self.assertEqual(
                    compact.memory.export_causal_state(),
                    original.memory.export_causal_state(),
                )
                self.assertEqual(
                    compact.value_needs.export_causal_state(),
                    original.value_needs.export_causal_state(),
                )
                self.assertEqual(compact.scheduler.t_monde, step)
                self.assertEqual(
                    compact.stage3.substrate.mortal_status,
                    original.stage3.substrate.mortal_status,
                )
                self.assertEqual(compact.stage3.substrate.lived_stream.last_step, step)
                self.assertTrue(compact.journal.verify())
                self.assertTrue(original.journal.verify())
                self.assertNotEqual(new_result.execution_status, "dead")

    def test_stage7_memory_episodes_match_history_projection(self):
        self.compare_lives(build_stage7_reference_runtime, steps=12)

    def test_stage10_sleep_and_wake_preserve_memory_and_body(self):
        self.compare_lives(
            lambda: build_stage10_reference_runtime(start_fatigued=True),
            steps=6,
        )

    def test_stage11_exploration_preserves_memory_and_world(self):
        self.compare_lives(
            lambda: build_stage11_reference_runtime(enable_geography=True),
            steps=7,
        )

    def test_compact_delivery_requires_mortal_mode_and_prebirth_selection(self):
        runtime = build_stage7_reference_runtime()
        substrate = runtime.stage3.substrate
        with self.assertRaisesRegex(RuntimeError, "requires mortal"):
            substrate.enable_compact_memory_delivery(
                policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            )
        substrate.enable_mortal_world()
        substrate.enable_compact_memory_delivery(
            policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
        )
        with self.assertRaisesRegex(RuntimeError, "before birth"):
            substrate.enable_compact_memory_delivery(
                policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            )
        self.assertEqual(runtime.run_step().execution_status, "applied")

    def test_physical_death_seals_unconsumed_memory_queue(self):
        runtime = build_stage10_reference_runtime(start_fatigued=True)
        start(runtime, compact=True)
        first = runtime.run_step()
        self.assertEqual(first.execution_status, "applied")
        stream = runtime.stage3.substrate.lived_stream
        self.assertGreaterEqual(stream.pending_count, 2)
        origin = runtime.world.position
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": origin.as_dict(), "active": True},
        )
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(stream.pending_count, 0)
        with self.assertRaises(RuntimeError):
            stream.drain_for_memory()
        with self.assertRaises(RuntimeError):
            runtime.run_step()


if __name__ == "__main__":
    unittest.main()
