"""Consolidation failures halt life; private h cannot erase postcut learning."""
from __future__ import annotations

from copy import deepcopy
from unittest.mock import patch
import unittest

from lab.mortal_execution import MortalStatus
from lab.consolidation_publication import Stage10PublicationCoordinator
from test_stage10_consolidation_publication import fixture
from test_stage10_live_sixpass_runtime import configured_runtime


class SleepFailClosedTests(unittest.TestCase):
    def test_semantic_publication_exception_halts_mortal_life_before_next_dispatch(self):
        runtime = configured_runtime()
        fatigued = runtime.sleep_health.export_causal_state()
        fatigued["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(fatigued)

        first = runtime.run_step()
        self.assertEqual(first.execution_status, "applied")
        self.assertEqual(first.command_primitive, "dormir")
        physical = deepcopy(runtime.world.export_causal_state())

        with patch.object(
            runtime, "_run_live_consolidation",
            side_effect=RuntimeError("injected consolidation commit failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "injected consolidation"):
                runtime.run_step()
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assertEqual(runtime.world.export_causal_state(), physical)
        self.assertTrue(runtime.journal.verify())
        with self.assertRaises(RuntimeError):
            runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), physical)

    def test_failed_sleep_admission_after_semantic_work_halts_without_physics(self):
        runtime = configured_runtime()
        fatigued = runtime.sleep_health.export_causal_state()
        fatigued["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(fatigued)
        first = runtime.run_step()
        self.assertEqual(first.command_primitive, "dormir")
        physical = deepcopy(runtime.world.export_causal_state())
        with patch.object(
            runtime.stage3.control, "admit",
            side_effect=OSError("injected postconsolidation control error"),
        ):
            with self.assertRaisesRegex(OSError, "postconsolidation control"):
                runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), physical)
        self.assertEqual(runtime.stage3.substrate.mortal_status,
                         MortalStatus.TECHNICAL_HALT)
        self.assertTrue(runtime.journal.verify())
        with self.assertRaises(RuntimeError):
            runtime.run_step()

    def test_physical_sleep_committed_then_recovery_error_halts_without_rollback(self):
        runtime = configured_runtime()
        fatigued = runtime.sleep_health.export_causal_state()
        fatigued["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(fatigued)
        first = runtime.run_step()
        self.assertEqual(first.command_primitive, "dormir")
        before_time = runtime.scheduler.t_monde
        old_world = deepcopy(runtime.world.export_causal_state())
        with patch.object(
            runtime.sleep_health, "recover_sleep_step",
            side_effect=OSError("injected postphysics sleep error"),
        ):
            with self.assertRaisesRegex(OSError, "postphysics sleep"):
                runtime.run_step()
        self.assertEqual(runtime.scheduler.t_monde, before_time + 1)
        self.assertIsNone(runtime.scheduler.active_attempt)
        self.assertNotEqual(runtime.world.export_causal_state(), old_world)
        self.assertEqual(runtime.stage3.substrate.mortal_status,
                         MortalStatus.TECHNICAL_HALT)
        self.assertTrue(runtime.journal.verify())
        kinds = [entry.causal_event["kind"] for entry in runtime.journal.entries]
        self.assertEqual(kinds[-1], "step_closed")
        last_body = deepcopy(runtime.world.export_causal_state())
        with self.assertRaises(RuntimeError):
            runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), last_body)

    def test_semantic_identity_rebase_keeps_real_postcut_owner_state(self):
        journal, tx, slot, history, owners, coordinator = fixture()
        journal.append(
            event_id="kappa:postcut:1",
            causal_event={
                "emitter": "stage4-runtime",
                "kind": "kappa_update_published",
                "t_monde": 4,
                "data": {"verification_ref": "independent:lived:1"},
            },
        )
        # Model an already applied canonical online update. This is a
        # state-preservation test, not proof of independent kappa calibration.
        owners["metacognition_health"].state["generation"] = 9
        baseline = {
            key: deepcopy(owner.export_causal_state())
            for key, owner in owners.items()
        }

        def keep_live_active_form(_candidate, state, _updates):
            return deepcopy(state)

        prepared = coordinator.prepare(
            transaction=tx,
            technical_validator=lambda item: isinstance(item, dict),
            owner_rebasers={
                key: keep_live_active_form
                for key in Stage10PublicationCoordinator.REQUIRED
            },
        )
        self.assertEqual(
            len(prepared.postcut_slice.for_owner("metacognition_health")), 1,
        )
        receipt = coordinator.publish(
            prepared=prepared, transaction=tx, world_step=5,
            scheduler_sync_authorized=True,
        )
        self.assertEqual(
            history.current_version, receipt.new_history_version,
        )
        for name, owner in owners.items():
            self.assertEqual(owner.export_causal_state(), baseline[name])
        self.assertTrue(journal.verify())
        self.assertIsNone(slot.current)


if __name__ == "__main__":
    unittest.main()
