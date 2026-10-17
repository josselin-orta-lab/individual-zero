"""Fail-closed in-process faults at the paid-index h publication boundary.

A valid WAL is never used to re-open a halted Stage10/12 individual.
The tests exercise the REAL mortal sleep path and unchanged UC prices.
"""
from __future__ import annotations

from copy import deepcopy
from unittest.mock import patch
import unittest

from i0.modules.consolidation_pending_index import ChargedPendingEpisodeIndex
from lab.consolidation_publication import Stage10PublicationCoordinator
from lab.mortal_execution import MortalStatus
from lab.stage10_runtime import Stage10Runtime
from test_stage10_live_sixpass_runtime import configured_runtime


CHARGE = "stage10_consolidation_index_maintenance_charged"
ACTIVATE = "stage10_consolidation_version_activated"
RETIRE = "stage10_consolidation_index_retired"


class PaidIndexSoftFaultTests(unittest.TestCase):
    def _exercise(self, mode: str):
        runtime = configured_runtime(
            maximum_passes_per_sleep_step=6, paid_pending_index=True,
        )
        for _ in range(12):
            if runtime.memory.episodes:
                break
            self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertTrue(runtime.memory.episodes)
        sleep_state = runtime.sleep_health.export_causal_state()
        sleep_state["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(sleep_state)

        def before_publish(self, *args, **kwargs):
            raise RuntimeError("injected: before h")

        def after_activation(self, *args, **kwargs):
            raise RuntimeError("injected: after h before index retirement")

        orig_write = Stage10Runtime._write
        def after_retirement(self, *args, **kwargs):
            result = orig_write(self, *args, **kwargs)
            if kwargs.get("kind") == RETIRE:
                raise RuntimeError("injected: after durable index retirement")
            return result

        if mode == "before_h":
            target, attr, replacement = (
                Stage10PublicationCoordinator, "publish", before_publish,
            )
        elif mode == "after_h":
            target, attr, replacement = (
                ChargedPendingEpisodeIndex, "acknowledge_published",
                after_activation,
            )
        elif mode == "after_retire":
            target, attr, replacement = (
                Stage10Runtime, "_write", after_retirement,
            )
        else:
            raise AssertionError("undeclared injection")

        with patch.object(target, attr, replacement):
            for _ in range(75):
                before_world = deepcopy(runtime.world.export_causal_state())
                before_journal = [
                    entry.causal_event["kind"] for entry in runtime.journal.entries
                ]
                before_transitions = before_journal.count(
                    "world_transition_experienced"
                )
                try:
                    outcome = runtime.run_step()
                except RuntimeError as error:
                    self.assertIn("injected:", str(error))
                    break
                else:
                    self.assertEqual(outcome.execution_status, "applied")
            else:
                self.fail("no paid index publication reached in 75 physical steps")

        kinds = [entry.causal_event["kind"] for entry in runtime.journal.entries]
        self.assertEqual(runtime.stage3.substrate.mortal_status,
                         MortalStatus.TECHNICAL_HALT)
        self.assertEqual(runtime.world.export_causal_state(), before_world)
        self.assertEqual(kinds.count("world_transition_experienced"),
                         before_transitions)
        self.assertTrue(runtime.journal.verify())
        self.assertIn(CHARGE, kinds)
        expected = {
            "before_h": [CHARGE],
            "after_h": [CHARGE, ACTIVATE],
            "after_retire": [CHARGE, ACTIVATE, RETIRE],
        }[mode]
        self.assertEqual(kinds[-len(expected):], expected)
        self.assertEqual(kinds.count(ACTIVATE), int(mode != "before_h"))
        self.assertEqual(kinds.count(RETIRE), int(mode == "after_retire"))
        world_after_halt = deepcopy(runtime.world.export_causal_state())
        journal_after_halt = runtime.journal.canonical_bytes()
        with self.assertRaises(RuntimeError):
            runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), world_after_halt)
        self.assertEqual(runtime.journal.canonical_bytes(), journal_after_halt)

    def test_maintenance_paid_and_publish_fails_halts(self):
        self._exercise("before_h")

    def test_h_durable_but_retirement_fails_halts(self):
        self._exercise("after_h")

    def test_retirement_durable_but_postreceipt_fails_halts(self):
        self._exercise("after_retire")


if __name__ == "__main__":
    unittest.main()
