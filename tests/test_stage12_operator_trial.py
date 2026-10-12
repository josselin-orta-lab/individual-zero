"""Retained operator run: real mortal actions, external audit and no resurrection."""
from __future__ import annotations

import json
import platform
import re
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

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
