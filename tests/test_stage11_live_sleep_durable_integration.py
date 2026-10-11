"""Cross-component Stage10/11 sleep, six-pass semantics and durable life audit.

Development software evidence only: not Stage-13 scientific acceptance.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_sleep_runtime import Stage11SleepRuntime
from test_stage10_live_sixpass_runtime import configured_runtime


def integrated_live_sleep(path: str):
    exploration = build_stage11_reference_runtime(autonomous_mortal=True)
    sleep = configured_runtime()
    # Stage 11 amends the Stage-9 UC budget before Stage 10 config installation.
    stage11_config = replace(exploration._stage11_config, intrinsic_weight=0.0)
    stage10_config = replace(
        sleep._stage10_config,
        stage9=stage11_config.stage9,
    )
    return Stage11SleepRuntime(
        world_config=exploration.world.config,
        layout=exploration.world._layout,
        safety_config=exploration.stage3.substrate.safety._config,
        safety_facts=exploration._canonical_safety._innate,
        protected_integrity_threshold=(
            exploration.stage3.control._config.protected_integrity_threshold
        ),
        equipment=exploration.equipment,
        stage11_config=stage11_config,
        stage10_config=stage10_config,
        autonomous_mortal=True,
        wal_path=path,
    )


class IntegratedLiveSleepTests(unittest.TestCase):
    def test_six_pass_sleep_uses_one_mortal_stage11_world_and_durable_journal(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "i0-lived-sleep.jsonl")
            runtime = integrated_live_sleep(path)
            self.assertIsNone(runtime.stage3.substrate.bench)
            self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
            self.assertIs(runtime.stage3.substrate.journal, runtime.journal)
            self.assertIs(runtime.stage3.substrate.world, runtime.world)
            self.assertTrue(runtime.journal.durable_wal_enabled)
            owner_ids = [owner.owner_id for owner in runtime.causal_owners]
            self.assertEqual(len(owner_ids), len(set(owner_ids)))
            self.assertIn("exploration", owner_ids)
            self.assertIn("individual.slow_history", owner_ids)

            waking = []
            for _ in range(16):
                if runtime.memory.episodes:
                    break
                result = runtime.run_step()
                waking.append((result.source, result.command_primitive))
                self.assertEqual(result.execution_status, "applied")
            self.assertTrue(runtime.memory.episodes, waking)

            initial_version = runtime.slow_history.current_version
            fatigued = runtime.sleep_health.export_causal_state()
            fatigued["fatigue"] = 1.0
            runtime.sleep_health.restore_causal_state(fatigued)
            for _ in range(10):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                if result.command_primitive == "dormir":
                    break
            else:
                self.fail("real Stage11/10 Competition never admitted sleep")

            for _ in range(18):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                if runtime.slow_history.current_version != initial_version:
                    break
            self.assertNotEqual(runtime.slow_history.current_version, initial_version)
            self.assertIsNone(runtime.consolidation.current)

            kinds = [row.causal_event["kind"] for row in runtime.journal.entries]
            self.assertEqual(kinds.count("stage10_consolidation_pass_checkpointed"), 6)
            self.assertEqual(kinds.count("stage10_consolidation_version_activated"), 1)
            self.assertTrue(runtime.journal.verify())
            durability = HashChainedJournal.audit_durable_wal(path)
            self.assertEqual(durability["verified_entries"], len(runtime.journal.entries))
            self.assertEqual(durability["head_hash"], runtime.journal.head_hash)
            audited = audit_export_bytes(
                runtime.journal.canonical_bytes(),
                expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(audited.world_steps_closed, runtime.scheduler.t_monde)
            self.assertEqual(audited.consolidation_publications, 1)
            self.assertEqual(audited.terminal_deaths, 0)


if __name__ == "__main__":
    unittest.main()
