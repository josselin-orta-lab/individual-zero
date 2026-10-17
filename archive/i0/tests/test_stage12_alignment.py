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

    def test_canonical_intrinsic_witness_requires_real_evaluated_source(self):
        from lab.stage12_alignment import _positive_canonical_intrinsic, _independently_witnessed_intrinsic
        self.assertTrue(_positive_canonical_intrinsic({"$f64": (0.7).hex()}))
        for bad in (0.7, {"$f64": "nan"}, {"$f64": "0x0.0p+0"},
                    {"$f64": "0x1.0p+0", "extra": 1},
                    {"$f64": "0x1.0p+0garbage"}):
            with self.subTest(bad=bad):
                self.assertFalse(_positive_canonical_intrinsic(bad))
        def witness(data, index=1):
            return (index, {"kind": "stage11_intrinsic_evaluation", "data": data}, {})
        good = {"status": "evaluated", "option_ref": "option:1",
                "intrinsic_value": {"$f64": (0.7).hex()},
                "intrinsic_producers": ["exploration:p48_geographic"]}
        self.assertTrue(_independently_witnessed_intrinsic(
            [witness(good)], before_index=2, option_ref="option:1",
            motive="cible_exploration"))
        for rows in ([witness(good, 2)], [witness(good), witness(good)],
                     [witness({**good, "intrinsic_producers": ["value_needs.q_active"]})],
                     [witness({**good, "intrinsic_value": {"$f64": "0x0.0p+0"}})],
                     [witness({**good, "status": "unevaluated"})]):
            with self.subTest(rows=rows):
                self.assertFalse(_independently_witnessed_intrinsic(
                    rows, before_index=2, option_ref="option:1",
                    motive="cible_exploration"))

    def test_real_exploration_actions_are_not_labeled_unjustified(self):
        from lab.stage11_reference_fixture import build_stage11_reference_runtime
        from lab.stage10_reference_fixture import build_stage10_reference_runtime
        from lab.stage12_runtime import Stage12Runtime
        from i0.modules.stage12_detectors import Stage12DetectionPolicy
        from dataclasses import replace
        with TemporaryDirectory() as directory:
            stage11 = build_stage11_reference_runtime(
                enable_geography=True, autonomous_mortal=True)
            stage10 = build_stage10_reference_runtime(autonomous_mortal=True)
            sleep = replace(stage10._stage10_config.sleep, fatigue_gain=0.0,
                            night_weight=0.0, consolidation_weight=0.0)
            stage10_config = replace(stage10._stage10_config,
                stage9=stage11._stage11_config.stage9, sleep=sleep)
            life = Stage12Runtime(
                world_config=stage11.world.config, layout=stage11.world._layout,
                safety_config=stage11.stage3.substrate.safety._config,
                safety_facts=stage11._canonical_safety._innate,
                protected_integrity_threshold=stage11.stage3.control._config.protected_integrity_threshold,
                stage11_config=stage11._stage11_config,
                stage10_config=stage10_config, equipment=stage11.equipment,
                autonomous_mortal=True,
                wal_path=str(Path(directory) / "life.wal"),
                diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
                detector_policy=Stage12DetectionPolicy(
                    version="alignment-evidence-test-v1", window=12,
                    stagnation_steps=4, stagnation_tolerance=0.05,
                    loop_repetitions=3, loop_max_period=2, entropy_min_samples=4,
                    entropy_warning_fraction=0.25, bias_min_outcomes_each=2,
                    attribution_bias_threshold=0.75))
            self.assertEqual(life.run_step().execution_status, "applied")
            report = evaluate_goal_action_alignment(life.journal.canonical_bytes())
            self.assertEqual(report.as_dict()["counts"][LEGITIMATE_AUTONOMOUS], 1)
            self.assertEqual(report.actions[0].basis, "funded_lived_intrinsic_exploration")

    def test_categorical_vocabulary_remains_exclusively_three_way(self):
        self.assertEqual(CATEGORIES, (
            GOAL_DIRECTED, LEGITIMATE_AUTONOMOUS,
            WITHOUT_TRACEABLE_JUSTIFICATION,
        ))


if __name__ == "__main__":
    unittest.main()
