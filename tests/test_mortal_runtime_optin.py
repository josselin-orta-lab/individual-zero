"""Opt-in mortality crosses Stage 2, reflex, cognition, sleep and exploration.

Legacy v1.2.1 rollback fixtures remain separate until full v1.3 migration.
None of these tests use an oracle read or change WorldBody physics.
"""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus
from lab.snapshots import SnapshotType
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Command, Position


def fatal_current_cell(runtime) -> None:
    """Declare an unknown lethal world hazard in the physical test fixture."""
    position = runtime.world.position
    runtime.world.apply_scenario_event(
        "set_lethal_zone",
        {"position": position.as_dict(), "active": True},
    )


def fatal_neighborhood(runtime) -> None:
    """Make any admissible move or wait from the starting tile truly lethal."""
    position = runtime.world.position
    for x, y in (
        (position.x, position.y),
        (position.x + 1, position.y),
        (position.x - 1, position.y),
        (position.x, position.y + 1),
        (position.x, position.y - 1),
    ):
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": {"x": x, "y": y}, "active": True},
        )


def enable(runtime) -> None:
    runtime.stage3.substrate.enable_mortal_world()


class MortalRuntimeIntegrationTests(unittest.TestCase):
    def test_stage2_commits_fatal_wait_without_checkpoint_or_restart(self):
        runtime = build_stage4_reference_runtime()
        enable(runtime)
        fatal_current_cell(runtime)
        substrate = runtime.stage3.substrate
        substrate.open_step()
        result = substrate.execute(Command("attendre"))
        self.assertEqual(result.status, "dead")
        self.assertTrue(result.transition.lethal)
        self.assertEqual(runtime.world.position, Position(2, 2))
        self.assertEqual(substrate.mortal_status, MortalStatus.DEAD)
        self.assertIsNone(runtime.scheduler.active_attempt)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        self.assertEqual(runtime.bench.metrics.lethal_rollbacks, 0)
        kinds = [e.causal_event["kind"] for e in runtime.journal.entries]
        self.assertIn("world_transition_experienced", kinds)
        self.assertNotIn("snapshot_taken", kinds)
        self.assertNotIn("lethal_rollback_completed", kinds)
        self.assertNotIn("protocol_mask_rejected_command", kinds)
        self.assertEqual(substrate.autobiographical_view(), ())
        with self.assertRaises(RuntimeError):
            substrate.open_step()
        with self.assertRaises(RuntimeError):
            substrate.execute(Command("attendre"))

    def test_stage3_lethal_reflex_is_not_followed_by_wait_or_cognition(self):
        runtime = build_stage4_reference_runtime()
        enable(runtime)
        # The threat is visible, the retreat is physically lethal but unknown.
        runtime.world.apply_scenario_event(
            "place_creature",
            {"position": {"x": 3, "y": 2}},
        )
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": {"x": 1, "y": 2}, "active": True},
        )
        runtime.stage3.open_step()  # Stage 3 control consumes one pre-opened capture.
        result = runtime.stage3.run_step()
        self.assertTrue(result.reflex_triggered)
        self.assertEqual(result.source, "reflex")
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(runtime.world.position, Position(1, 2))
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_stage4_cognitive_step_reports_terminal_without_retry(self):
        runtime = build_stage4_reference_runtime()
        enable(runtime)
        fatal_neighborhood(runtime)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "dead")
        self.assertGreaterEqual(result.cycles_used, 1)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        self.assertEqual(runtime.bench.metrics.lethal_rollbacks, 0)
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertIsNone(runtime.scheduler.active_attempt)
        events = [e.causal_event for e in runtime.journal.entries]
        self.assertEqual(
            len([e for e in events if e["kind"] == "command_experienced"]), 1,
        )
        self.assertEqual(
            len([e for e in events if e["kind"] == "step_closed"]), 1,
        )
        self.assertEqual(
            [e["data"]["outcome"] for e in events if e["kind"] == "step_closed"],
            ["dead"],
        )
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_stage10_sleep_owner_cannot_continue_after_fatal_waking_step(self):
        runtime = build_stage10_reference_runtime()
        enable(runtime)
        fatal_neighborhood(runtime)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_stage11_exploration_stops_after_dead_world_transition(self):
        runtime = build_stage11_reference_runtime(enable_geography=True)
        enable(runtime)
        fatal_neighborhood(runtime)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(runtime.bench.metrics.lethal_transitions, 1)
        self.assertEqual(runtime.bench.metrics.lethal_rollbacks, 0)
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_mortal_mode_cannot_rewind_even_an_explicit_old_snapshot(self):
        runtime = build_stage4_reference_runtime()
        substrate = runtime.stage3.substrate
        record = substrate.snapshots.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id=runtime.individual_id,
            t_monde=0, cycle=0, attempt_ref=None,
            owners=(runtime.world,), versions={},
        )
        enable(runtime)
        with self.assertRaisesRegex(RuntimeError, "lethal checkpoints"):
            substrate.snapshots.take(
                snapshot_type=SnapshotType.LETHAL_CHECKPOINT,
                individual_id=runtime.individual_id,
                t_monde=0, cycle=0, attempt_ref="a:1",
                owners=(runtime.world,), versions={},
            )
        fatal_neighborhood(runtime)
        self.assertEqual(runtime.run_step().execution_status, "dead")
        dead_world = runtime.world.export_causal_state()
        with self.assertRaisesRegex(RuntimeError, "life restoration"):
            substrate.snapshots.restore(
                record.id, owners=(runtime.world,),
            )
        self.assertEqual(runtime.world.export_causal_state(), dead_world)
        self.assertEqual(substrate.mortal_status, MortalStatus.DEAD)

    def test_mode_must_be_selected_before_birth(self):
        runtime = build_stage4_reference_runtime()
        enable(runtime)
        with self.assertRaises(RuntimeError):
            enable(runtime)
        ordinary = runtime.run_step()
        self.assertEqual(ordinary.execution_status, "applied")
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.ACTIVE)
        with self.assertRaises(RuntimeError):
            enable(runtime)

    def test_default_legacy_mode_is_unchanged_for_historical_fixtures(self):
        runtime = build_stage4_reference_runtime()
        self.assertIsNone(runtime.stage3.substrate.mortal_status)
        normal = runtime.run_step()
        self.assertEqual(normal.execution_status, "applied")
        self.assertIsNone(runtime.stage3.substrate.mortal_status)


if __name__ == "__main__":
    unittest.main()
