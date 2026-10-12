"""Stage12 alignment is offline provenance, not a scientific intention label."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.mortal_execution import MortalStatus
from lab.stage12_alignment import (
    CATEGORIES, GOAL_DIRECTED, LEGITIMATE_AUTONOMOUS,
    WITHOUT_TRACEABLE_JUSTIFICATION, evaluate_goal_action_alignment,
)
from lab.world import Command
from test_stage12_mortal_runtime import stage12_runtime


class Stage12AlignmentTests(unittest.TestCase):
    def test_only_applied_physical_actions_count_and_all_have_one_category(self):
        with TemporaryDirectory() as directory:
            individual = stage12_runtime(
                str(Path(directory) / "alignment-test.jsonl"),
            )
            for _ in range(3):
                self.assertEqual(
                    individual.run_step().execution_status, "applied",
                )
            raw = individual.journal.canonical_bytes()
            offline = audit_export_bytes(raw)
            report = evaluate_goal_action_alignment(
                raw, expected_head=individual.journal.head_hash,
                expected_count=len(individual.journal.entries),
            )
            self.assertEqual(report.journal_head, offline.head_hash)
            self.assertEqual(len(report.actions), 3)
            d = report.as_dict()
            self.assertEqual(d["executed_physical_actions"], 3)
            self.assertEqual(set(d["counts"]), set(CATEGORIES))
            self.assertEqual(sum(d["counts"].values()), 3)
            self.assertEqual(
                [a.world_step for a in report.actions], [1, 2, 3],
            )
            self.assertTrue(all(
                a.primitive and a.command_event_id and a.basis and a.category in CATEGORIES
                for a in report.actions
            ))
            self.assertFalse(
                any("oracle" in a.basis for a in report.actions),
            )
            self.assertIn("not_motive_truth", d["evidence"])
            self.assertTrue(individual.journal.verify())

    def test_dead_life_counts_lethal_step_without_postmortem_motive(self):
        with TemporaryDirectory() as directory:
            individual = stage12_runtime(
                str(Path(directory) / "terminal-alignment.jsonl"),
            )
            self.assertEqual(individual.run_step().execution_status, "applied")
            individual.world.apply_scenario_event(
                "set_lethal_zone",
                {"position": individual.world.position.as_dict(), "active": True},
            )
            sub = individual.stage3.substrate
            sub.open_step()
            terminal = sub.execute(Command("attendre"))
            self.assertEqual(terminal.status, "dead")
            self.assertEqual(sub.mortal_status, MortalStatus.DEAD)
            before = individual.journal.canonical_bytes()
            with self.assertRaises(RuntimeError):
                individual.run_step()
            self.assertEqual(individual.journal.canonical_bytes(), before)
            report = evaluate_goal_action_alignment(before)
            self.assertEqual(len(report.actions), 2)
            self.assertEqual(report.actions[-1].world_step, 2)
            self.assertEqual(
                report.actions[-1].category,
                WITHOUT_TRACEABLE_JUSTIFICATION,
            )
            self.assertEqual(
                report.actions[-1].basis, "no_unique_matching_admission",
            )
            self.assertEqual(audit_export_bytes(before).terminal_deaths, 1)

    def test_tamper_and_wrong_trusted_head_are_rejected(self):
        with TemporaryDirectory() as directory:
            individual = stage12_runtime(
                str(Path(directory) / "audit-fail.jsonl"),
            )
            self.assertEqual(individual.run_step().execution_status, "applied")
            raw = individual.journal.canonical_bytes()
            with self.assertRaises(ValueError):
                evaluate_goal_action_alignment(
                    raw, expected_head="0" * 64,
                )
            tampered = raw.replace(b"step_opened", b"step_openeX", 1)
            self.assertNotEqual(tampered, raw)
            with self.assertRaises(ValueError):
                evaluate_goal_action_alignment(tampered)

    def test_categorical_vocabulary_remains_exclusively_three_way(self):
        self.assertEqual(CATEGORIES, (
            GOAL_DIRECTED, LEGITIMATE_AUTONOMOUS,
            WITHOUT_TRACEABLE_JUSTIFICATION,
        ))


if __name__ == "__main__":
    unittest.main()
