"""One independently anchored packet for every Stage12 operator audit."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_operator_alert_audit import audit_stage12_operator_alerts
from test_stage12_operator_alert_runtime import actual_stage12_runtime


class Stage12OperatorPacketTests(unittest.TestCase):
    def test_four_applied_steps_produce_one_trusted_cross_auditor_packet(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "report_stage12_operator_packet.py"
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "life.wal"))
            Stage12OperatorConsole(
                substrate=runtime.stage3.substrate,
                mode="campaign", policy_version="stage12-packet-test-v1",
                maximum_world_steps=4,
            )
            for _ in range(4):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            self.assertTrue(runtime.journal.verify())
            exported = runtime.journal.canonical_bytes()
            export_path = Path(folder) / "canonical-export.jsonl"
            export_path.write_bytes(exported)
            expected = [
                "--expected-head", runtime.journal.head_hash,
                "--expected-count", str(len(runtime.journal.entries)),
            ]
            run = subprocess.run(
                [sys.executable, str(script), str(export_path),
                 *expected, "--expected-world-steps", "4",
                 "--require-terminal-stop"],
                cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            packet = json.loads(run.stdout)
            self.assertEqual(packet["schema"], "stage12-operator-evidence-packet-v1")
            self.assertTrue(packet["trusted_tail_anchors_provided"])
            self.assertEqual(
                packet["technical_validation"],
                "export_consistency_verified_only",
            )
            self.assertTrue(packet["coverage"]["every_physical_action_diagnosed"])
            self.assertTrue(
                packet["coverage"]["s_t_occupancy_observed_on_every_action"]
            )
            self.assertFalse(packet["coverage"]["lived_attribution_bias_validated"])
            self.assertEqual(packet["journal"]["world_steps_closed"], 4)
            self.assertEqual(packet["diagnostics"]["diagnostic_samples"], 4)
            self.assertEqual(
                packet["coverage"]["physical_action_steps_with_paid_diagnostic"], 4,
            )
            self.assertEqual(
                packet["coverage"]["physical_action_steps_with_s_t_measurement"], 4,
            )
            self.assertEqual(packet["coverage"]["distinct_steps_with_s_t_measurement"], 4)
            self.assertEqual(packet["persistent_operator_alerts"]["examined_samples"], 4)
            self.assertGreaterEqual(
                packet["st_module_occupancy"]["evaluated_cycles"], 4,
            )
            self.assertEqual(
                packet["goal_action_alignment"]["executed_physical_actions"], 4,
            )
            self.assertTrue(packet["checks"]["terminal_operator_stop_verified"])
            self.assertFalse(packet["operator_stage_accepted"])
            self.assertFalse(packet["physical_truth_independently_verified"])
            self.assertEqual(
                packet["persistent_operator_alerts"]["emitted_alerts"],
                audit_stage12_operator_alerts(exported).emitted_alerts,
            )
            for extras in (
                ["--expected-world-steps", "5"],
                ["--require-terminal-stop", "--expected-world-steps", "5"],
            ):
                denied = subprocess.run(
                    [sys.executable, str(script), str(export_path),
                     *expected, *extras],
                    cwd=root, capture_output=True, text=True, check=False,
                )
                self.assertEqual(denied.returncode, 1)
                self.assertIn("refused", denied.stderr)
            wrong_head = subprocess.run(
                [sys.executable, str(script), str(export_path),
                 "--expected-head", "f" * 64,
                 "--expected-count", str(len(runtime.journal.entries))],
                cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(wrong_head.returncode, 1)
            self.assertIn("refused", wrong_head.stderr)

    def test_operator_packet_requires_trusted_head_and_count(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "report_stage12_operator_packet.py"
        for args in ([], ["--expected-head", "f" * 64],
                     ["--expected-count", "2"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, str(script), "missing.jsonl", *args],
                    cwd=root, capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
