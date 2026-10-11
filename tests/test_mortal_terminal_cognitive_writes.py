"""Post-terminal cognitive writes must never resume a mortal individual."""
from __future__ import annotations

import unittest

from lab.stage7_reference_fixture import build_stage7_reference_runtime
from lab.stage8_reference_fixture import build_stage8_reference_runtime
from lab.world import Command


class TerminalCognitiveMutationTests(unittest.TestCase):
    @staticmethod
    def kill(runtime):
        substrate = runtime.stage3.substrate
        # Covers both construction-time mortality and prebirth opt-in.
        if substrate.mortal_status is None:
            substrate.enable_mortal_world()
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": runtime.world.position.as_dict(), "active": True},
        )
        substrate.open_step()
        result = substrate.execute(Command("attendre"))
        assert result.status == "dead"
        return substrate

    def test_mortal_intention_rejected_after_death_without_state_change(self):
        for autonomous_mortal in (False, True):
            with self.subTest(autonomous_mortal=autonomous_mortal):
                runtime = build_stage7_reference_runtime(autonomous_mortal=autonomous_mortal)
                self.kill(runtime)
                before = runtime.memory.export_causal_state()
                count = len(runtime.journal.entries)
                with self.assertRaises(RuntimeError):
                    runtime.create_intention(object())
                self.assertEqual(runtime.memory.export_causal_state(), before)
                self.assertEqual(len(runtime.journal.entries), count)

    def test_mortal_online_verifications_rejected_after_death(self):
        for autonomous_mortal in (False, True):
            with self.subTest(autonomous_mortal=autonomous_mortal):
                runtime = build_stage8_reference_runtime(autonomous_mortal=autonomous_mortal)
                self.kill(runtime)
                precision_before = runtime.precision_active.export_causal_state()
                kappa_before = runtime.kappa_active.export_causal_state()
                count = len(runtime.journal.entries)
                with self.assertRaises(RuntimeError):
                    runtime.integrate_precision_verification(object())
                with self.assertRaises(RuntimeError):
                    runtime.integrate_kappa_verification(object())
                self.assertEqual(runtime.precision_active.export_causal_state(), precision_before)
                self.assertEqual(runtime.kappa_active.export_causal_state(), kappa_before)
                self.assertEqual(len(runtime.journal.entries), count)


if __name__ == "__main__":
    unittest.main()
