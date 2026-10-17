"""Lossless, non-restoring local custody of one real I0's causal journal."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lab.independent_journal_audit import audit_export_file
from lab.journal_export import export_immutable_journal
from lab.mortal_execution import MortalStatus
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Command


class ImmutableJournalExportTests(unittest.TestCase):
    def test_live_cognitive_export_does_not_change_i0_or_complete_journal(self):
        instance = build_stage4_reference_runtime(autonomous_mortal=True)
        for _ in range(3):
            self.assertEqual(instance.run_step().execution_status, "applied")
        before_world = instance.world.export_causal_state()
        before_brain = instance.s_t.export_causal_state()
        before = instance.journal.canonical_bytes()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "individual-a.jsonl"
            receipt = export_immutable_journal(instance.journal, target)
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(receipt.occurrence_count, len(instance.journal.entries))
            self.assertEqual(receipt.journal_head_hash, instance.journal.head_hash)
            verified = audit_export_file(
                target, expected_head=receipt.journal_head_hash,
                expected_count=receipt.occurrence_count,
            )
            self.assertEqual(verified.world_steps_closed, 3)
            self.assertEqual(verified.terminal_deaths, 0)
            self.assertFalse(receipt.as_dict()["physical_truth_verified"])
            with self.assertRaises(FileExistsError):
                export_immutable_journal(instance.journal, target)
            self.assertEqual(target.read_bytes(), before)
            self.assertFalse(any(x.name.endswith(".staged") for x in Path(directory).iterdir()))
        self.assertEqual(instance.world.export_causal_state(), before_world)
        self.assertEqual(instance.s_t.export_causal_state(), before_brain)
        self.assertEqual(instance.journal.canonical_bytes(), before)
        self.assertEqual(instance.run_step().execution_status, "applied")
        self.assertTrue(instance.journal.verify())

    def test_open_physical_step_is_never_published_as_complete_archive(self):
        instance = build_stage4_reference_runtime(autonomous_mortal=True)
        instance.stage3.substrate.open_step()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.jsonl"
            with self.assertRaisesRegex(ValueError, "unclosed"):
                export_immutable_journal(instance.journal, path)
            self.assertFalse(path.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_after_death_archive_persists_without_oracle_or_revival(self):
        instance = build_stage4_reference_runtime(autonomous_mortal=True)
        runtime = instance.stage3.substrate
        instance.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": instance.world.position.as_dict(), "active": True},
        )
        runtime.open_step()
        self.assertEqual(runtime.execute(Command("attendre")).status, "dead")
        self.assertEqual(runtime.mortal_status, MortalStatus.DEAD)
        before = instance.journal.canonical_bytes()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deceased.jsonl"
            receipt = export_immutable_journal(instance.journal, path)
            self.assertEqual(receipt.terminal_deaths, 1)
            self.assertEqual(path.read_bytes(), before)
            script = Path(__file__).resolve().parents[1] / "scripts" / "verify_i0_journal.py"
            checked = subprocess.run(
                [sys.executable, str(script), str(path),
                 "--expected-head", receipt.journal_head_hash,
                 "--expected-count", str(receipt.occurrence_count)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(instance.journal.canonical_bytes(), before)
        with self.assertRaises(RuntimeError):
            instance.run_step()
        self.assertEqual(runtime.mortal_status, MortalStatus.DEAD)

    def test_stage10_sleep_keeps_full_archive_separate_from_consolidation(self):
        instance = build_stage10_reference_runtime(
            start_fatigued=True, autonomous_mortal=True,
        )
        self.assertEqual(instance.run_step().command_primitive, "dormir")
        self.assertEqual(instance.run_step().source, "sleep")
        history_before = instance.slow_history.export_causal_state()
        journal_before = instance.journal.canonical_bytes()
        with tempfile.TemporaryDirectory() as directory:
            receipt = export_immutable_journal(
                instance.journal, Path(directory) / "sleep.jsonl",
            )
            self.assertGreater(receipt.occurrence_count, 0)
            self.assertEqual(
                audit_export_file(Path(receipt.path)).world_steps_closed, 2,
            )
        self.assertEqual(instance.slow_history.export_causal_state(), history_before)
        self.assertEqual(instance.journal.canonical_bytes(), journal_before)
        self.assertTrue(instance.journal.verify())

    def test_stage11_cognitive_export_never_requires_external_science(self):
        individual = build_stage11_reference_runtime(autonomous_mortal=True)
        self.assertIsNone(individual.bench)
        self.assertEqual(individual.run_step().execution_status, "applied")
        with tempfile.TemporaryDirectory() as directory:
            receipt = export_immutable_journal(
                individual.journal, Path(directory) / "exploration.jsonl",
            )
            self.assertEqual(audit_export_file(Path(receipt.path)).world_steps_closed, 1)
            self.assertTrue(individual.journal.verify())


if __name__ == "__main__":
    unittest.main()
