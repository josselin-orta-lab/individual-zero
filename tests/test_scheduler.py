from __future__ import annotations

import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from lab.journal import HashChainedJournal
from lab.scheduler import CyclePhase, Scheduler


class SchedulerTests(unittest.TestCase):
    def make_scheduler(self) -> tuple[Scheduler, HashChainedJournal]:
        journal = HashChainedJournal()
        scheduler = Scheduler(
            journal=journal,
            phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        )
        return scheduler, journal

    def hooks_recording(self, trace: list[tuple[int, str]]):
        hooks = {}
        for phase_value, components in MVP_CYCLE_PHASE_COMPONENT_ORDER.items():
            phase = CyclePhase(phase_value)
            hooks[phase] = {}
            for component in components:
                def make_hook(name: str, phase_id: int):
                    def hook(context):
                        self.assertEqual(context.phase.value, phase_id)
                        trace.append((phase_id, name))
                    return hook
                hooks[phase][component] = make_hook(component, phase_value)
        return hooks

    def test_open_step_advances_world_clock_once(self) -> None:
        scheduler, _ = self.make_scheduler()

        first = scheduler.open_step()
        scheduler.close_step(
            outcome="normal",
            applied_command_count=1,
            world_advance_count=1,
        )
        second = scheduler.open_step()

        self.assertEqual(first.t_monde, 1)
        self.assertEqual(second.t_monde, 2)

    def test_rollback_attempt_changes_attempt_ref_without_advancing_world_time(self) -> None:
        scheduler, _ = self.make_scheduler()
        first = scheduler.open_step()

        second = scheduler.new_attempt_after_rollback()

        self.assertEqual(first.t_monde, second.t_monde)
        self.assertEqual(first.t_monde, 1)
        self.assertEqual(first.attempt_index, 0)
        self.assertEqual(second.attempt_index, 1)
        self.assertNotEqual(first.attempt_ref, second.attempt_ref)
        self.assertEqual(scheduler.t_monde, 1)

    def test_cycle_runs_all_phases_in_normative_order(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()
        trace: list[tuple[int, str]] = []

        scheduler.run_cycle(
            cycle=3,
            hooks=self.hooks_recording(trace),
        )

        expected = []
        for phase_value in range(6):
            for component in MVP_CYCLE_PHASE_COMPONENT_ORDER[phase_value]:
                expected.append((phase_value, component))

        self.assertEqual(trace, expected)

    def test_cycle_index_is_supplied_not_owned_by_scheduler(self) -> None:
        scheduler, journal = self.make_scheduler()
        scheduler.open_step()

        scheduler.run_cycle(
            cycle=7,
            hooks=self.hooks_recording([]),
        )

        cycle_events = [
            entry.causal_event
            for entry in journal.entries
            if entry.causal_event.get("kind") in {"cycle_opened", "cycle_closed"}
        ]
        self.assertEqual(
            tuple(event["cycle"] for event in cycle_events),
            (7, 7),
        )

    def test_same_schedule_produces_byte_identical_journal(self) -> None:
        def run_once() -> bytes:
            scheduler, journal = self.make_scheduler()
            scheduler.open_step()
            scheduler.run_cycle(
                cycle=1,
                hooks=self.hooks_recording([]),
            )
            scheduler.close_step(
                outcome="normal",
                applied_command_count=1,
                world_advance_count=1,
            )
            return journal.canonical_bytes()

        self.assertEqual(run_once(), run_once())

    def test_normal_step_requires_one_command_and_one_world_advance(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()

        with self.assertRaises(ValueError):
            scheduler.close_step(
                outcome="normal",
                applied_command_count=0,
                world_advance_count=0,
            )

        self.assertIsNotNone(scheduler.active_attempt)

    def test_blocked_step_requires_zero_command_and_zero_world_advance(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()

        scheduler.close_step(
            outcome="blocked",
            applied_command_count=0,
            world_advance_count=0,
        )

        self.assertIsNone(scheduler.active_attempt)

    def test_blocked_step_rejects_world_advance(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()

        with self.assertRaises(ValueError):
            scheduler.close_step(
                outcome="blocked",
                applied_command_count=0,
                world_advance_count=1,
            )

    def test_missing_phase_hook_is_rejected(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()
        hooks = self.hooks_recording([])
        del hooks[CyclePhase.SELECTION]["gatekeeper"]

        with self.assertRaises(ValueError):
            scheduler.run_cycle(cycle=1, hooks=hooks)

    def test_opening_second_step_while_first_is_active_is_rejected(self) -> None:
        scheduler, _ = self.make_scheduler()
        scheduler.open_step()

        with self.assertRaises(RuntimeError):
            scheduler.open_step()


if __name__ == "__main__":
    unittest.main()
