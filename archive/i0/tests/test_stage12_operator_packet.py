"""One independently anchored packet for every Stage12 operator audit."""
from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_operator_alert_audit import audit_stage12_operator_alerts
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_operator_control_audit import audit_stage12_operator_control
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
            lived = packet["lived_attribution_evidence"]
            self.assertEqual(lived["status"], "unavailable_no_audited_lived_pairs")
            self.assertEqual(lived["admitted_verified_successes"], 0)
            self.assertEqual(lived["admitted_verified_failures"], 0)
            self.assertEqual(lived["admitted_unique_attribution_refs"], 0)
            self.assertEqual(lived["diagnostic_samples_without_admitted_attribution"], 4)
            self.assertTrue(lived["independent_pair_contract_available"])
            self.assertFalse(lived["detector_calibration_supported"])
            self.assertEqual(packet["journal"]["world_steps_closed"], 4)
            self.assertEqual(packet["diagnostics"]["diagnostic_samples"], 4)
            detector_coverage = packet["lived_detector_coverage"]
            self.assertFalse(
                detector_coverage["attribution_bias_calibration_supported"]
            )
            for name in (
                "stagnation", "reasoning_loop", "low_context_entropy",
            ):
                classes = detector_coverage["detectors"][name]
                self.assertEqual(
                    classes["positive"] + classes["negative"]
                    + classes["unavailable"], 4,
                )
                self.assertTrue(
                    set(classes) == {"positive", "negative", "unavailable"}
                )

            goal_receipts = packet["lived_goal_progress"]
            self.assertEqual(
                goal_receipts["schema"], "stage12-independent-goal-progress-audit-v1",
            )
            self.assertFalse(goal_receipts["complete_goal_achievement_verified"])
            self.assertFalse(goal_receipts["subjective_agency_attribution_verified"])
            self.assertFalse(goal_receipts["independent_physical_truth_attested"])
            self.assertEqual(
                goal_receipts["preregistered_one_step_criteria"],
                goal_receipts["verified_one_step_resource_gains"]
                + goal_receipts["verified_one_step_no_gains"]
                + goal_receipts["unavailable_next_step_observations"]
                + goal_receipts["unresolved_at_terminal"],
            )
            self.assertEqual(
                packet["coverage"]["precommitted_goal_progress_criteria"],
                goal_receipts["preregistered_one_step_criteria"],
            )
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
            self.assertTrue(packet["checks"]["operator_control_lineage_audited"])
            self.assertTrue(packet["external_operator_control"]["configured"])
            self.assertTrue(packet["external_operator_control"]["experiment_stopped"])
            self.assertEqual(packet["external_operator_control"]["maximum_world_steps"], 4)
            self.assertEqual(packet["external_operator_control"]["operator_events"], 3)
            self.assertFalse(
                packet["external_operator_control"]["operator_intent_independently_verified"]
            )
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

    def test_rehashed_terminal_policy_cannot_launder_a_forged_stop(self):
        # A coherent SHA-256 chain with an attacker-supplied replacement head
        # is NOT evidence that the operator cap and stop reason are coherent.
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "forgery.wal"))
            Stage12OperatorConsole(
                substrate=runtime.stage3.substrate, mode="campaign",
                policy_version="stage12-packet-forgery-v1",
                maximum_world_steps=3,
            )
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            canonical = runtime.journal.canonical_bytes()
            clean = audit_stage12_operator_control(canonical)
            self.assertTrue(clean.experiment_stopped)
            records = [
                json.loads(line) for line in canonical.split(b"\n")
            ]
            cap = next(
                row["causal_event"]["data"] for row in records
                if row["causal_event"]["kind"] == "operator_step_cap_set"
            )
            stop = next(
                row["causal_event"]["data"] for row in records
                if row["causal_event"]["kind"] == "experiment_stopped"
            )
            cap["maximum_world_steps"] = 4
            stop["maximum_world_steps"] = 4
            previous = GENESIS_HASH
            for i, row in enumerate(records):
                row["index"] = i
                row["previous_hash"] = previous
                previous = sha256(
                    bytes.fromhex(previous) + canonical_causal_bytes({
                        "event_id": row["event_id"],
                        "causal_event": row["causal_event"],
                    }),
                ).hexdigest()
                row["event_hash"] = previous
            forged = b"\n".join(canonical_causal_bytes(row) for row in records)
            # Independently valid cryptographic chain, invalid operator policy.
            structural = audit_export_bytes(forged)
            self.assertEqual(structural.occurrences, len(records))
            with self.assertRaisesRegex(ValueError, "incorrect world step"):
                audit_stage12_operator_control(forged)
            # The *full* operator packet cannot claim this fabricated stop.
            from scripts.report_stage12_operator_packet import evaluate_packet
            with self.assertRaisesRegex(ValueError, "incorrect world step"):
                evaluate_packet(
                    forged, expected_head=structural.head_hash,
                    expected_count=structural.occurrences,
                    expected_world_steps=3, require_terminal_stop=True,
                )

    def test_rehashed_unverified_lived_bias_cannot_launder_calibration(self):
        # A valid hash chain and real physical steps do not authenticate a
        # subjective outcome/agency pair. The external auditor must refuse.
        from scripts.report_stage12_operator_packet import evaluate_packet

        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "forged-bias.wal"))
            Stage12OperatorConsole(
                substrate=runtime.stage3.substrate,
                mode="campaign", policy_version="stage12-bias-negative-v1",
                maximum_world_steps=2,
            )
            for _ in range(2):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            records = [
                json.loads(line)
                for line in runtime.journal.canonical_bytes().split(b"\n")
            ]
            diagnostic = next(
                row["causal_event"]["data"] for row in records
                if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published"
            )
            diagnostic["attribution_bias"] = "self_serving_pattern"
            previous = GENESIS_HASH
            for index, row in enumerate(records):
                row["index"] = index
                row["previous_hash"] = previous
                previous = sha256(
                    bytes.fromhex(previous) + canonical_causal_bytes({
                        "event_id": row["event_id"],
                        "causal_event": row["causal_event"],
                    }),
                ).hexdigest()
                row["event_hash"] = previous
            forged = b"\n".join(canonical_causal_bytes(row) for row in records)
            standalone = audit_export_bytes(forged)
            self.assertEqual(standalone.world_steps_closed, 2)
            with self.assertRaisesRegex(
                ValueError, "unverified lived attribution bias claim",
            ):
                evaluate_packet(
                    forged, expected_head=standalone.head_hash,
                    expected_count=standalone.occurrences,
                    expected_world_steps=2, require_terminal_stop=True,
                )

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
