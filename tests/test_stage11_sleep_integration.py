"""v1.3.1: one mortal substrate for Stage-10 sleep and Stage-11 cognition."""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_sleep_runtime import Stage11SleepRuntime
from lab.world import Command


def integrated_runtime(*, geography=False, fatigued=False):
    # Build versioned development *configuration* objects independently.
    # Only the resulting integrated runtime has authority over its own life.
    stage11 = build_stage11_reference_runtime(
        enable_geography=geography, autonomous_mortal=True,
    )
    stage10 = build_stage10_reference_runtime(autonomous_mortal=True)
    result = Stage11SleepRuntime(
        world_config=stage11.world.config,
        layout=stage11.world._layout,
        safety_config=stage11.stage3.substrate.safety._config,
        safety_facts=stage11._canonical_safety._innate,
        protected_integrity_threshold=(
            stage11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=stage11._stage11_config,
        stage10_config=stage10._stage10_config,
        equipment=stage11.equipment,
        autonomous_mortal=True,
    )
    if fatigued:
        state = result.sleep_health.export_causal_state()
        state["fatigue"] = 1.0
        result.sleep_health.restore_causal_state(state)
    return result


class IntegratedStage10Stage11Tests(unittest.TestCase):
    def test_single_mortal_owner_graph_and_exploration_step(self):
        runtime = integrated_runtime(geography=True)
        self.assertEqual(runtime.stage3.substrate.mortal_status, MortalStatus.ACTIVE)
        self.assertIsNone(runtime.stage3.substrate.bench)
        self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
        self.assertIs(runtime.stage3.substrate.world, runtime.world)
        self.assertIs(runtime.stage3.substrate.journal, runtime.journal)
        ids = [owner.owner_id for owner in runtime.causal_owners]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("consolidation", ids)
        self.assertIn("consolidation_work_budget", ids)
        self.assertIn("individual.slow_history", ids)
        self.assertIn("exploration", ids)
        self.assertIn("global_modulation", ids)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(runtime.scheduler.t_monde, 1)
        self.assertTrue(runtime.journal.verify())
        kinds = [entry.causal_event["kind"] for entry in runtime.journal.entries]
        self.assertIn("stage10_sleep_pressure_frozen", kinds)

    def test_death_stops_both_sleep_and_exploration(self):
        runtime = integrated_runtime()
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": runtime.world.position.as_dict(), "active": True},
        )
        substrate = runtime.stage3.substrate
        substrate.open_step()
        result = substrate.execute(Command("attendre"))
        self.assertEqual(result.status, "dead")
        self.assertEqual(substrate.mortal_status, MortalStatus.DEAD)
        owners_before = {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
        }
        with self.assertRaises(RuntimeError):
            runtime.run_step()
        owners_after = {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
        }
        self.assertEqual(owners_before, owners_after)
        self.assertTrue(runtime.journal.verify())

    def test_combined_runtime_forbids_legacy_nonmortal_mode(self):
        stage11 = build_stage11_reference_runtime()
        stage10 = build_stage10_reference_runtime()
        with self.assertRaises(ValueError):
            Stage11SleepRuntime(
                world_config=stage11.world.config,
                layout=stage11.world._layout,
                safety_config=stage11.stage3.substrate.safety._config,
                safety_facts=stage11._canonical_safety._innate,
                protected_integrity_threshold=(
                    stage11.stage3.control._config.protected_integrity_threshold
                ),
                stage11_config=stage11._stage11_config,
                stage10_config=stage10._stage10_config,
                equipment=stage11.equipment,
                autonomous_mortal=False,
            )


if __name__ == "__main__":
    unittest.main()
