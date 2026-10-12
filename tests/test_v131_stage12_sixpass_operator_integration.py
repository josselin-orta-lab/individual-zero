"""All-module v1.3.1 software integration, without Oracle or Bench.

Not a Stage13 campaign. No historical life is restored; one physical world,
one mortal identity, one durable hash journal, one Metacognition owner.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_runtime import Stage12Runtime
from test_stage10_live_sixpass_runtime import configured_runtime


def integrated_all_module_runtime(path):
    stage11 = build_stage11_reference_runtime(autonomous_mortal=True)
    stage10 = configured_runtime()
    # A versioned Stage11 configuration retains its physical/coherent
    # computation graph; exploration remains instantiated and operative.
    stage11_config = replace(stage11._stage11_config, intrinsic_weight=0.0)
    stage10_config = replace(
        stage10._stage10_config, stage9=stage11_config.stage9,
    )
    return Stage12Runtime(
        world_config=stage11.world.config,
        layout=stage11.world._layout,
        safety_config=stage11.stage3.substrate.safety._config,
        safety_facts=stage11._canonical_safety._innate,
        protected_integrity_threshold=(
            stage11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=stage11_config,
        stage10_config=stage10_config,
        equipment=stage11.equipment,
        autonomous_mortal=True,
        wal_path=path,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-sixpass-live-cross-dev-v1",
            window=12, stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.2,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


class V131AllModuleSmokes(unittest.TestCase):
    def test_one_life_sleeps_consolidates_detects_then_operator_stops(self):
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "i0-v131-full.jsonl")
            runtime = integrated_all_module_runtime(path)
            console = Stage12OperatorConsole(
                substrate=runtime.stage3.substrate,
                mode="campaign",
                policy_version="stage12-all-modules-dev-v1",
                maximum_world_steps=50,
            )
            self.assertIsNone(runtime.stage3.substrate.bench)
            self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
            ids = [o.owner_id for o in runtime.causal_owners]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(ids.count("metacognition_health"), 1)
            self.assertEqual(ids.count("operator_console"), 1)

            for _ in range(16):
                if runtime.memory.episodes:
                    break
                self.assertEqual(runtime.run_step().execution_status, "applied")
            self.assertTrue(runtime.memory.episodes)
            self.assertGreater(runtime.detection_report.evidence_samples, 0)
            start_h = runtime.slow_history.current_version

            fatigue = runtime.sleep_health.export_causal_state()
            fatigue["fatigue"] = 1.0
            runtime.sleep_health.restore_causal_state(fatigue)
            for _ in range(10):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                if result.command_primitive == "dormir":
                    break
            else:
                self.fail("Stage12/11/10 did not select physical sleep")

            for _ in range(18):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                if runtime.slow_history.current_version != start_h:
                    break
            self.assertNotEqual(runtime.slow_history.current_version, start_h)
            self.assertIsNone(runtime.consolidation.current)
            kinds = [entry.causal_event["kind"] for entry in runtime.journal.entries]
            self.assertEqual(kinds.count("stage10_consolidation_pass_checkpointed"), 6)
            self.assertEqual(kinds.count("stage10_consolidation_version_activated"), 1)
            self.assertGreaterEqual(
                kinds.count("stage12_lived_diagnostics_published"), 1,
            )
            self.assertTrue(runtime.journal.verify())

            console.arreter(reason="software_integration_smoke_complete")
            self.assertEqual(
                runtime.stage3.substrate.mortal_status,
                MortalStatus.EXPERIMENT_STOPPED,
            )
            self.assertEqual(runtime.journal.entries[-1].causal_event["kind"],
                             "experiment_stopped")
            self.assertTrue(runtime.journal.verify())
            offline = audit_export_bytes(
                runtime.journal.canonical_bytes(),
                expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(offline.consolidation_publications, 1)
            self.assertEqual(offline.terminal_deaths, 0)
            self.assertEqual(
                HashChainedJournal.audit_durable_wal(path)["head_hash"],
                runtime.journal.head_hash,
            )
            with self.assertRaises(RuntimeError):
                runtime.run_step()


if __name__ == "__main__":
    unittest.main()
