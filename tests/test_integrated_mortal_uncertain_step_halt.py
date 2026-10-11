"""Uncertain integrated mortal steps are terminal, never retried or rewound."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.world import Command
from test_stage11_sleep_integration import integrated_runtime


class UncertainMortalCycleHaltTests(unittest.TestCase):
    def assert_frozen(self, runtime):
        world = runtime.world.export_causal_state()
        journal = runtime.journal.canonical_bytes()
        with self.assertRaises(RuntimeError):
            runtime.run_step()
        # This PR guards the unified mortal dispatch boundary. Direct
        # WorldBody method sealing is the separate PR #61 invariant and
        # is checked in the full integrated security matrix.
        with self.assertRaises(RuntimeError):
            runtime.stage3.substrate._mortal_boundary.execute(
                Command("attendre"), t_monde=runtime.scheduler.t_monde + 1,
            )
        self.assertEqual(runtime.world.export_causal_state(), world)
        self.assertEqual(runtime.journal.canonical_bytes(), journal)
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assertTrue(runtime.journal.verify())
        self.assertEqual(
            HashChainedJournal.audit_durable_wal(runtime._test_wal_path)["head_hash"],
            runtime.journal.head_hash,
        )

    def test_durable_publication_exception_after_step_open_halts_before_dispatch(self):
        runtime = integrated_runtime(geography=True)
        before = runtime.world.export_causal_state()
        normal_append = runtime.journal.append

        def failing_publish(*, event_id, causal_event, noncausal_metadata=None):
            if causal_event.get("kind") == "perceptual_capture":
                raise OSError("injected durable perceptual receipt fault")
            return normal_append(
                event_id=event_id, causal_event=causal_event,
                noncausal_metadata=noncausal_metadata,
            )

        with patch.object(runtime.journal, "append", side_effect=failing_publish):
            with self.assertRaisesRegex(OSError, "perceptual receipt fault"):
                runtime.run_step()
        self.assertEqual(runtime.scheduler.t_monde, 1)
        self.assertEqual(runtime.world.export_causal_state(), before)
        self.assertEqual(runtime.stage3.substrate._mortal_boundary.last_world_step, 0)
        self.assertIn(
            "step_opened",
            [row.causal_event["kind"] for row in runtime.journal.entries],
        )
        self.assert_frozen(runtime)

    def test_exception_after_real_physical_commit_never_undoes_world(self):
        runtime = integrated_runtime(geography=True)
        actual_dispatch = runtime._dispatch_decision

        def fail_after_applied(*args, **kwargs):
            receipt = actual_dispatch(*args, **kwargs)
            if receipt.status != "applied":
                raise AssertionError("reference fixture did not apply real physics")
            raise RuntimeError("injected postphysical cognitive failure")

        with patch.object(runtime, "_dispatch_decision", side_effect=fail_after_applied):
            with self.assertRaisesRegex(RuntimeError, "postphysical cognitive failure"):
                runtime.run_step()
        self.assertEqual(runtime.stage3.substrate._mortal_boundary.last_world_step, 1)
        self.assertEqual(runtime.scheduler.t_monde, 1)
        kinds = [row.causal_event["kind"] for row in runtime.journal.entries]
        self.assertEqual(kinds.count("world_transition_experienced"), 1)
        self.assertEqual(kinds.count("individual_death_confirmed"), 0)
        self.assert_frozen(runtime)

    def test_unresolved_nonlethal_safety_block_is_not_wrongly_called_corruption(self):
        runtime = integrated_runtime()
        sub = runtime.stage3.substrate
        sub.open_step()
        sub.safety.enter_safety_block(reason="injected_diagnostic_block")
        runtime.scheduler.close_step(
            outcome="blocked",
            applied_command_count=0, world_advance_count=0,
        )
        before = runtime.journal.canonical_bytes()
        with self.assertRaisesRegex(RuntimeError, "safety block"):
            runtime.run_step()
        self.assertEqual(sub.mortal_status, MortalStatus.ACTIVE)
        self.assertTrue(sub.safety.blocked)
        self.assertEqual(runtime.journal.canonical_bytes(), before)
        self.assertTrue(runtime.journal.verify())


if __name__ == "__main__":
    unittest.main()
