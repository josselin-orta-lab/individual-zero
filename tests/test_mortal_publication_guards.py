"""Fail-closed invariants for irreversible autonomous execution (v1.3.1)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from lab.independent_journal_audit import audit_export_bytes
from lab.mortal_execution import MortalStatus
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command


class MortalPublicationGuardsTests(unittest.TestCase):
    def test_missing_step_open_receipt_halts_without_physical_dispatch(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        substrate = runtime.stage3.substrate
        initial = runtime.world.export_causal_state()
        real_append = runtime.journal.append

        def fail_open(*, event_id, causal_event, **kwargs):
            if causal_event.get("kind") == "step_opened":
                raise OSError("injected journal publication outage")
            return real_append(event_id=event_id, causal_event=causal_event, **kwargs)

        with patch.object(runtime.journal, "append", side_effect=fail_open):
            with self.assertRaisesRegex(OSError, "publication outage"):
                substrate.open_step()

        self.assertEqual(substrate.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assertEqual(substrate._mortal_boundary.failed_step, 1)
        self.assertEqual(runtime.world.export_causal_state(), initial)
        self.assertFalse(any(
            e.causal_event["kind"] == "world_transition_experienced"
            for e in runtime.journal.entries
        ))
        with self.assertRaisesRegex(RuntimeError, "dead or halted"):
            substrate.execute(Command("attendre"))
        with self.assertRaisesRegex(RuntimeError, "dead or halted"):
            substrate.open_step()

    def test_safety_block_closes_step_once_and_forbids_subsequent_actions(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        substrate = runtime.stage3.substrate
        substrate.open_step()
        initial = runtime.world.export_causal_state()
        substrate.safety.enter_safety_block(reason="no_admissible_safe_command")
        runtime.scheduler.close_step(
            outcome="blocked", applied_command_count=0, world_advance_count=0,
        )
        journal_before = runtime.journal.canonical_bytes()
        self.assertEqual(
            audit_export_bytes(journal_before).world_steps_closed, 1,
        )
        with self.assertRaisesRegex(RuntimeError, "safety-blocked"):
            substrate.open_step()
        with self.assertRaisesRegex(RuntimeError, "safety-blocked"):
            substrate.send_admitted_command(Command("attendre"), source="test")
        self.assertEqual(runtime.journal.canonical_bytes(), journal_before)
        self.assertEqual(runtime.world.export_causal_state(), initial)
        self.assertEqual(substrate.mortal_status, MortalStatus.ACTIVE)


if __name__ == "__main__":
    unittest.main()
