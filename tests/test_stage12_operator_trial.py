"""Retained operator run: real mortal actions, external audit and no resurrection."""
from __future__ import annotations

import importlib
import json
import platform
import re
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch as mock_patch

from lab.independent_journal_audit import audit_export_bytes


class RetainedStage12TrialTests(unittest.TestCase):
    def test_retains_a_terminal_four_step_life_and_refuses_overwrite(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "run_stage12_operator_trial.py"
        with TemporaryDirectory() as folder:
            output = Path(folder) / "independent-trial"
            cmd = [sys.executable, str(script), "--output-dir", str(output),
                   "--steps", "4"]
            run = subprocess.run(
                cmd, cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            stdout = json.loads(run.stdout)
            manifest = json.loads(
                (output / "trial-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["status"], "complete_technically_audited")
            self.assertEqual(manifest["physically_applied_steps"], 4)
            self.assertEqual(manifest["mortal_status"], "experiment_stopped")
            self.assertIsNone(manifest["failure"])
            self.assertIsNone(manifest["audit_failure"])
            self.assertFalse(manifest["operator_accepted"])
            self.assertFalse(manifest["m11_atomic_recovery_certified"])
            self.assertTrue(manifest["execution_provenance_unchanged"])
            provenance = manifest["execution_provenance"]
            self.assertTrue(provenance["tracked_checkout_clean"])
            self.assertRegex(
                provenance["tracked_source_tree_sha256"], r"^[0-9a-f]{64}$",
            )
            self.assertGreater(provenance["tracked_files_count"], 0)
            self.assertIsNotNone(provenance["code_commit"])
            self.assertEqual(
                provenance["python_patch_version"], platform.python_version(),
            )
            self.assertEqual(provenance["python_implementation"],
                             platform.python_implementation())
            for digest_key in (
                "normative_spec_sha256", "deterministic_engine_sha256",
                "package_manifest_sha256",
            ):
                self.assertRegex(provenance[digest_key], r"^[0-9a-f]{64}$")
            if provenance["code_commit"] is not None:
                self.assertRegex(provenance["code_commit"], r"^[0-9a-f]{40,64}$")
            self.assertFalse(provenance["fully_locked_reference_environment"])
            self.assertFalse(
                provenance["human_execution_provenance_independently_attested"]
            )
            self.assertEqual(stdout["head_hash"], manifest["head_hash"])
            self.assertEqual(stdout["occurrences"], manifest["occurrences"])
            content = (output / "canonical-export.jsonl").read_bytes()
            external = audit_export_bytes(
                content, expected_head=manifest["head_hash"],
                expected_count=manifest["occurrences"],
            )
            self.assertEqual(external.world_steps_closed, 4)
            self.assertEqual(
                manifest["cross_auditor_packet"]["journal"]["world_steps_closed"], 4,
            )
            self.assertTrue((output / "individual-zero-life.wal").is_file())
            self.assertEqual(
                manifest["cross_auditor_packet"]["coverage"][
                    "physical_action_steps_with_s_t_measurement"
                ], 4,
            )
            denied = subprocess.run(
                cmd, cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(denied.returncode, 1)
            self.assertIn("refused", denied.stderr)
            self.assertEqual(
                (output / "canonical-export.jsonl").read_bytes(), content,
            )

    @staticmethod
    def _runner_module():
        script_dir = str(Path(__file__).resolve().parents[1] / "scripts")
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        return importlib.import_module("run_stage12_operator_trial")

    def test_staged_git_source_fingerprint_detects_changed_or_missing_bytes(self):
        runner = self._runner_module()
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            subprocess.run(
                ["git", "-C", str(repo), "init", "-q"], check=True,
                capture_output=True,
            )
            source = repo / "tracked-source.py"
            source.write_text("VERSION = 1\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(repo), "add", "tracked-source.py"],
                check=True, capture_output=True,
            )
            first, count = runner._tracked_source_fingerprint(repo)
            self.assertEqual(count, 1)
            self.assertRegex(first, r"^[0-9a-f]{64}$")
            source.write_text("VERSION = 2\n", encoding="utf-8")
            second, count = runner._tracked_source_fingerprint(repo)
            self.assertEqual(count, 1)
            self.assertNotEqual(second, first)
            source.unlink()
            missing, count = runner._tracked_source_fingerprint(repo)
            self.assertIsNone(missing)
            self.assertEqual(count, 0)

    def test_dirty_or_unknown_provenance_is_refused_before_birth(self):
        runner = self._runner_module()
        basis = runner._execution_provenance()
        self.assertTrue(basis["tracked_checkout_clean"])
        with TemporaryDirectory() as folder:
            for mutation in (
                {"tracked_checkout_clean": False},
                {"tracked_checkout_clean": None},
                {"tracked_source_tree_sha256": None},
                {"code_commit": None},
                {"normative_spec_sha256": None},
            ):
                with self.subTest(mutation=mutation):
                    source = dict(basis)
                    source.update(mutation)
                    destination = Path(folder) / ("bad-" + next(iter(mutation)))
                    with mock_patch.object(
                        runner, "_execution_provenance", return_value=source,
                    ):
                        with self.assertRaisesRegex(
                            ValueError, "clean, identified, complete",
                        ):
                            runner.run_trial(destination, 1)
                    self.assertFalse(destination.exists())

    def test_source_changes_during_trial_keep_archives_but_withhold_pass(self):
        runner = self._runner_module()
        before = runner._execution_provenance()
        self.assertTrue(before["tracked_checkout_clean"])
        after = dict(before)
        after["tracked_source_tree_sha256"] = "0" * 64
        self.assertNotEqual(after["tracked_source_tree_sha256"],
                            before["tracked_source_tree_sha256"])
        with TemporaryDirectory() as folder:
            destination = Path(folder) / "drifted-life"
            with mock_patch.object(
                runner, "_execution_provenance",
                side_effect=[before, after],
            ):
                exit_code, manifest = runner.run_trial(destination, 1)
            self.assertEqual(exit_code, 2)
            self.assertEqual(manifest["status"], "incomplete_do_not_resume")
            self.assertFalse(manifest["execution_provenance_unchanged"])
            self.assertIn("changed during", manifest["audit_failure"])
            self.assertTrue((destination / "canonical-export.jsonl").exists())
            self.assertTrue((destination / "individual-zero-life.wal").exists())

    def test_untracked_normative_reference_is_not_a_versioned_checkout(self):
        runner = self._runner_module()
        with TemporaryDirectory() as folder:
            repo = Path(folder) / "checkout"
            repo.mkdir()
            subprocess.run(["git", "-C", str(repo), "init", "-q"],
                           check=True, capture_output=True)
            untracked = (
                "docs/architecture/reference/en/mvp-specification-v1.3.1.md"
            )
            for relative in runner._REQUIRED_TRACKED_TRIAL_PATHS:
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(repo), "add", "--",
                 *(name for name in runner._REQUIRED_TRACKED_TRIAL_PATHS
                   if name != untracked)],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=Test",
                 "-c", "user.email=test@example.invalid", "commit", "-qm",
                 "tracked source without versioned normative specification"],
                check=True, capture_output=True,
            )
            output = Path(folder) / "must-not-be-born"
            with mock_patch.object(
                runner, "__file__", str(repo / "scripts" /
                                        "run_stage12_operator_trial.py"),
            ), mock_patch.object(
                runner, "_runtime_imports_match_checkout", return_value=True,
            ):
                provenance = runner._execution_provenance()
                self.assertTrue(provenance["git_root_matches_runner"])
                self.assertTrue(provenance["tracked_checkout_clean"])
                self.assertIsNotNone(provenance["normative_spec_sha256"])
                self.assertFalse(provenance["required_source_paths_tracked"])
                with self.assertRaisesRegex(ValueError, "clean, identified, complete"):
                    runner.run_trial(output, 1)
            self.assertFalse(output.exists())

    def test_git_parent_repository_cannot_impersonate_checkout_root(self):
        runner = self._runner_module()
        with TemporaryDirectory() as folder:
            parent = Path(folder) / "parent"
            nested = parent / "unversioned-runner-root"
            nested.mkdir(parents=True)
            subprocess.run(["git", "-C", str(parent), "init", "-q"],
                           check=True, capture_output=True)
            for relative in runner._REQUIRED_TRACKED_TRIAL_PATHS:
                path = nested / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(parent), "add", "unversioned-runner-root"],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(parent), "-c", "user.name=Test",
                 "-c", "user.email=test@example.invalid", "commit", "-qm",
                 "tracked nested folder"],
                check=True, capture_output=True,
            )
            output = Path(folder) / "must-not-be-born"
            with mock_patch.object(
                runner, "__file__", str(nested / "scripts" /
                                        "run_stage12_operator_trial.py"),
            ), mock_patch.object(
                runner, "_runtime_imports_match_checkout", return_value=True,
            ):
                provenance = runner._execution_provenance()
                self.assertFalse(provenance["git_root_matches_runner"])
                self.assertIsNone(provenance["code_commit"])
                with self.assertRaisesRegex(ValueError, "clean, identified, complete"):
                    runner.run_trial(output, 1)
            self.assertFalse(output.exists())

    def test_foreign_python_runtime_import_refused_before_birth(self):
        runner = self._runner_module()
        trusted = runner._execution_provenance()
        self.assertTrue(trusted["runtime_modules_from_checkout"])
        module = sys.modules["lab.stage12_runtime"]
        with TemporaryDirectory() as folder:
            output = Path(folder) / "must-not-be-born"
            with mock_patch.object(
                module, "__file__", str(Path(folder) / "foreign" / "stage12_runtime.py"),
            ):
                provenance = runner._execution_provenance()
                self.assertFalse(provenance["runtime_modules_from_checkout"])
                with self.assertRaisesRegex(ValueError, "clean, identified, complete"):
                    runner.run_trial(output, 1)
            self.assertFalse(output.exists())

    def test_unreadable_normative_reference_fails_closed_not_crashes(self):
        runner = self._runner_module()
        with TemporaryDirectory() as folder:
            output = Path(folder) / "must-not-be-born"
            with mock_patch.object(
                Path, "read_bytes", side_effect=PermissionError("unreadable reference"),
            ):
                provenance = runner._execution_provenance()
                self.assertIsNone(provenance["normative_spec_sha256"])
                with self.assertRaisesRegex(ValueError, "clean, identified, complete"):
                    runner.run_trial(output, 1)
            self.assertFalse(output.exists())

    def test_invalid_steps_refuse_before_birth_and_output_creation(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "run_stage12_operator_trial.py"
        with TemporaryDirectory() as folder:
            for bad in ("0", "-1", "601"):
                out = Path(folder) / ("trial-" + bad)
                run = subprocess.run(
                    [sys.executable, str(script), "--output-dir", str(out),
                     "--steps", bad],
                    cwd=root, capture_output=True, text=True, check=False,
                )
                self.assertEqual(run.returncode, 1)
                self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
