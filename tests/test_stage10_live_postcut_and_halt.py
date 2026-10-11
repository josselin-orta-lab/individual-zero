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
