"""One genuine mortal Stage11 life explores, sleeps, consolidates and fsyncs.

Review-only integration test for the *combined* Stage10 six-pass and Stage11
WAL runtime. No second cognitive scheduler, scientific approval or rollback.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_sleep_runtime import Stage11SleepRuntime
from test_stage10_live_sixpass_runtime import configured_runtime


class MortalLiveSleepDurabilityTests(unittest.TestCase):
    def test_six_passes_from_lived_exploration_publish_once_with_fsynced_wal(self):
        # Fixture construction below supplies known, versioned policy config.
        # Neither fixture is attached to the one real integrated I0.
        stage11 = build_stage11_reference_runtime(
            enable_geography=False, autonomous_mortal=True,
        )
        stage10_fixture = configured_runtime()
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "unique-mortal-life.jsonl")
            i0 = Stage11SleepRuntime(
                stage11_config=stage11._stage11_config,
                stage10_config=stage10_fixture._stage10_config,
                wal_path=path,
                world_config=stage11.world.config,
                layout=stage11.world._layout,
                safety_config=stage11.stage3.substrate.safety._config,
                safety_facts=stage11._canonical_safety._innate,
                protected_integrity_threshold=(
                    stage11.stage3.control._config.protected_integrity_threshold
                ),
                equipment=stage11.equipment,
                autonomous_mortal=True,
            )
            self.assertIsNone(i0.stage3.substrate.bench)
            self.assertIs(i0.stage3.substrate.journal, i0.journal)
            self.assertIs(i0.stage3.substrate.world, i0.world)
            owner_ids = [o.owner_id for o in i0.causal_owners]
            self.assertEqual(len(owner_ids), len(set(owner_ids)))

            initial_history = i0.slow_history.current_version
            waking_commands = []
            for _ in range(30):
                if i0.memory.episodes:
                    break
                step = i0.run_step()
                waking_commands.append(step.command_primitive)
                self.assertEqual(step.execution_status, "applied")
            self.assertTrue(i0.memory.episodes, waking_commands)

            p = i0.sleep_health.export_causal_state()
            p["fatigue"] = 1.0
            i0.sleep_health.restore_causal_state(p)
            for _ in range(12):
                step = i0.run_step()
                self.assertEqual(step.execution_status, "applied")
                if step.command_primitive == "dormir":
                    break
            else:
                self.fail("single Stage11 individual never admitted physical sleep")

            actual_sleep_steps = 0
            for _ in range(24):
                step = i0.run_step()
                self.assertEqual(step.execution_status, "applied")
                if step.source == "sleep":
                    actual_sleep_steps += 1
                if i0.slow_history.current_version != initial_history:
                    break
            self.assertGreater(actual_sleep_steps, 0)
            self.assertNotEqual(i0.slow_history.current_version, initial_history)
            kinds = [r.causal_event["kind"] for r in i0.journal.entries]
            self.assertEqual(kinds.count("stage10_consolidation_pass_checkpointed"), 6)
            self.assertEqual(kinds.count("stage10_consolidation_version_activated"), 1)
            self.assertTrue(i0.journal.verify())
            durable = HashChainedJournal.audit_durable_wal(path)
            self.assertEqual(durable["verified_entries"], len(i0.journal.entries))
            self.assertEqual(durable["head_hash"], i0.journal.head_hash)
            audit = audit_export_bytes(
                i0.journal.canonical_bytes(),
                expected_count=len(i0.journal.entries),
                expected_head=i0.journal.head_hash,
            )
            self.assertEqual(audit.terminal_deaths, 0)
            self.assertEqual(audit.world_steps_closed, i0.scheduler.t_monde)
            h = i0.slow_history.read_committed()
            self.assertTrue(h["consolidated_episode_refs"])
            self.assertTrue(all(
                rule["status"] == "hypothese_causale"
                and rule["validated_for_safety"] is False
                for rule in h["hypotheses"]
            ))


if __name__ == "__main__":
    unittest.main()
