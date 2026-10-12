"""Stage12 persistent operator warnings over actual mortal world steps.

A permissive *development* warning threshold forces the signal pathway to
exercise, not an assertion of naturally occurring pathology or scientific GO.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.compute_budget import BudgetCharge
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_alert_audit import audit_stage12_operator_alerts
from lab.stage12_runtime import Stage12Runtime


def actual_stage12_runtime(path: str, *, alert_steps: int = 2) -> Stage12Runtime:
    st11 = build_stage11_reference_runtime(autonomous_mortal=True)
    st10 = build_stage10_reference_runtime(autonomous_mortal=True)
    no_sleep = replace(
        st10._stage10_config.sleep,
        fatigue_gain=0.0, night_weight=0.0, consolidation_weight=0.0,
    )
    config = replace(
        st10._stage10_config, stage9=st11._stage11_config.stage9,
        sleep=no_sleep,
    )
    return Stage12Runtime(
        world_config=st11.world.config, layout=st11.world._layout,
        safety_config=st11.stage3.substrate.safety._config,
        safety_facts=st11._canonical_safety._innate,
        protected_integrity_threshold=(
            st11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=st11._stage11_config, stage10_config=config,
        equipment=st11.equipment, autonomous_mortal=True, wal_path=path,
        diagnostic_sample_cost_uc=1,
        operator_alert_persistence_steps=alert_steps,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-operator-alerts-real-fixture-v1",
            window=12, stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3,
            # 1.0 guarantees the detector's *actual* bounded entropy is
            # flagged after min_samples. It is a wiring test, not a scientific
            # false-positive threshold recommendation.
            entropy_warning_fraction=1.0,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


def _rechain(records):
    previous = GENESIS_HASH
    for i, item in enumerate(records):
        item["index"] = i
        item["previous_hash"] = previous
        previous = sha256(
            bytes.fromhex(previous) + canonical_causal_bytes({
                "event_id": item["event_id"],
                "causal_event": item["causal_event"],
            }),
        ).hexdigest()
        item["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(item) for item in records)


class Stage12PersistentOperatorRuntimeTests(unittest.TestCase):
    def test_real_physical_steps_emit_one_alert_and_offline_auditor_confirms(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "alerts.wal"))
            ids = [item.owner_id for item in runtime.causal_owners]
            self.assertEqual(ids.count("metacognition_health"), 1)
            self.assertEqual(len(ids), len(set(ids)))
            for _ in range(7):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            raw = runtime.journal.canonical_bytes()
            entries = [record.causal_event for record in runtime.journal.entries]
            diagnostics = [
                e for e in entries
                if e["kind"] == "stage12_lived_diagnostics_published"
            ]
            alerts = [e for e in entries if e["kind"] == "stage12_operator_alert"]
            self.assertEqual(len(diagnostics), 7)
            entropy_alerts = [
                e for e in alerts if e["data"]["signal"] == "low_context_entropy"
            ]
            self.assertEqual(len(entropy_alerts), 1)
            self.assertEqual(entropy_alerts[0]["t_monde"], 4)
            self.assertEqual(entropy_alerts[0]["data"]["first_world_step"], 3)
            self.assertTrue(all(e["data"]["attribution_bias"] is None for e in diagnostics))
            self.assertTrue(all(e["data"]["operator_only_alert"] for e in alerts))
            report = audit_stage12_operator_alerts(
                raw, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(report.examined_samples, 7)
            self.assertEqual(report.emitted_alerts, len(alerts))
            self.assertEqual(report.counts_by_signal["low_context_entropy"], 1)
            self.assertEqual(
                report.occurrences, audit_export_bytes(raw).occurrences,
            )
            self.assertTrue(runtime.journal.verify())
            self.assertIsNone(runtime.stage3.substrate.bench)
            self.assertIsNone(runtime.stage3.substrate.evaluation_trace)

            state = runtime._meta_custody.export_causal_state()
            self.assertIn("operator_alert_ledger", state)
            distorted = deepcopy(state)
            distorted["operator_alert_ledger"]["last_world_step"] = 1
            with self.assertRaises(ValueError):
                runtime._meta_custody.restore_causal_state(distorted)
            self.assertEqual(runtime._meta_custody.export_causal_state(), state)

    def test_unavailable_diagnostic_cannot_emit_operator_alert(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "deferred.wal"))
            original = runtime.compute_budget.charge

            def refuse(*, module, operation, count=1):
                if operation == "stage12_diagnostic_sample":
                    return BudgetCharge(
                        accepted=False, module=module, operation=operation,
                        requested_uc=1,
                        consumed_cycle_uc=runtime.compute_budget.consumed_cycle_uc,
                        consumed_module_uc=runtime.compute_budget.consumed_module_uc(module),
                        reason="module_envelope",
                    )
                return original(module=module, operation=operation, count=count)

            with patch.object(runtime.compute_budget, "charge", side_effect=refuse):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            self.assertEqual(runtime._stage12_alerts.export_causal_state()["last_world_step"], 0)
            self.assertEqual(
                audit_stage12_operator_alerts(
                    runtime.journal.canonical_bytes(),
                ).emitted_alerts, 0,
            )
            self.assertFalse(any(
                row.causal_event.get("kind") == "stage12_operator_alert"
                for row in runtime.journal.entries
            ))

    def test_rehashed_missing_or_forged_alert_fails_independently(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "tamper.wal"))
            for _ in range(6):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            clean = runtime.journal.canonical_bytes()
            records = [json.loads(line) for line in clean.split(b"\n")]
            removed = deepcopy(records)
            removed[:] = [
                row for row in removed
                if not (
                    row["causal_event"]["kind"] == "stage12_operator_alert"
                    and row["causal_event"]["data"]["signal"] == "low_context_entropy"
                )
            ]
            forged_missing = _rechain(removed)
            self.assertEqual(audit_export_bytes(forged_missing).occurrences, len(removed))
            with self.assertRaisesRegex(ValueError, "missing operator alert"):
                audit_stage12_operator_alerts(forged_missing)

            changed = deepcopy(records)
            one_alert = next(
                row for row in changed
                if row["causal_event"]["kind"] == "stage12_operator_alert"
                and row["causal_event"]["data"]["signal"] == "low_context_entropy"
            )
            one_alert["causal_event"]["data"]["first_world_step"] = 1
            forged_early = _rechain(changed)
            self.assertEqual(audit_export_bytes(forged_early).occurrences, len(changed))
            with self.assertRaisesRegex(ValueError, "forged Stage12 operator alert"):
                audit_stage12_operator_alerts(forged_early)

    def test_rehashed_missing_diagnostic_is_an_unclosed_real_uc_debit(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "missing-sample.wal"))
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            entries = [
                json.loads(row)
                for row in runtime.journal.canonical_bytes().split(b"\n")
            ]
            dropped = False
            without = []
            for row in entries:
                if (not dropped and row["causal_event"]["kind"] ==
                        "stage12_lived_diagnostics_published"):
                    dropped = True
                    continue
                without.append(row)
            self.assertTrue(dropped)
            forged = _rechain(without)
            self.assertEqual(audit_export_bytes(forged).occurrences, len(without))
            with self.assertRaisesRegex(ValueError, "unclosed Stage12 diagnostic charge"):
                audit_stage12_operator_alerts(forged)

    def test_rehashed_missing_refusal_deferral_is_rejected(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "missing-defer.wal"))
            original = runtime.compute_budget.charge

            def refuse(*, module, operation, count=1):
                if operation == "stage12_diagnostic_sample":
                    return BudgetCharge(
                        accepted=False, module=module, operation=operation,
                        requested_uc=1,
                        consumed_cycle_uc=runtime.compute_budget.consumed_cycle_uc,
                        consumed_module_uc=runtime.compute_budget.consumed_module_uc(module),
                        reason="module_envelope",
                    )
                return original(module=module, operation=operation, count=count)

            with patch.object(runtime.compute_budget, "charge", side_effect=refuse):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            entries = [
                json.loads(row)
                for row in runtime.journal.canonical_bytes().split(b"\n")
            ]
            removed = False
            forged_rows = []
            for row in entries:
                if (not removed and row["causal_event"]["kind"] ==
                        "stage12_lived_diagnostics_deferred"):
                    removed = True
                    continue
                forged_rows.append(row)
            self.assertTrue(removed)
            forged = _rechain(forged_rows)
            self.assertEqual(audit_export_bytes(forged).occurrences, len(forged_rows))
            with self.assertRaisesRegex(ValueError, "unclosed Stage12 diagnostic charge"):
                audit_stage12_operator_alerts(forged)

    def test_rehashed_undocumented_attribution_cannot_create_operator_alarm(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "bias.wal"))
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            entries = [
                json.loads(row)
                for row in runtime.journal.canonical_bytes().split(b"\n")
            ]
            diagnostic = next(
                row["causal_event"]["data"] for row in entries
                if row["causal_event"]["kind"] ==
                "stage12_lived_diagnostics_published"
            )
            self.assertIsNone(diagnostic["attribution_bias"])
            diagnostic["attribution_bias"] = "self_serving_pattern"
            forged = _rechain(entries)
            self.assertEqual(audit_export_bytes(forged).occurrences, len(entries))
            with self.assertRaisesRegex(ValueError, "unverified lived attribution"):
                audit_stage12_operator_alerts(forged)

    def test_rehashed_delayed_operator_alert_does_not_pass(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "delayed.wal"))
            for _ in range(5):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            rows = [
                json.loads(raw)
                for raw in runtime.journal.canonical_bytes().split(b"\n")
            ]
            spot = next(
                i for i, row in enumerate(rows)
                if row["causal_event"]["kind"] == "stage12_operator_alert"
                and row["causal_event"]["data"]["signal"] == "low_context_entropy"
            )
            self.assertNotEqual(
                rows[spot + 1]["causal_event"]["kind"], "stage12_operator_alert",
            )
            rows[spot], rows[spot + 1] = rows[spot + 1], rows[spot]
            forged = _rechain(rows)
            self.assertEqual(audit_export_bytes(forged).occurrences, len(rows))
            with self.assertRaisesRegex(ValueError, "missing operator alert"):
                audit_stage12_operator_alerts(forged)

    def test_operator_cli_reports_real_warnings_without_importing_i0(self):
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "report_stage12_operator_alerts.py"
        audit_source = (
            root / "src" / "lab" / "stage12_operator_alert_audit.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("from i0", audit_source)
        self.assertNotIn("import i0", audit_source)
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "life.wal"))
            for _ in range(5):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            export = Path(folder) / "canonical.jsonl"
            export.write_bytes(runtime.journal.canonical_bytes())
            args = [
                sys.executable, str(script), str(export),
                "--expected-head", runtime.journal.head_hash,
                "--expected-count", str(len(runtime.journal.entries)),
            ]
            plain = subprocess.run(
                args, cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(plain.returncode, 0, plain.stderr)
            payload = json.loads(plain.stdout)
            self.assertEqual(payload["counts_by_signal"]["low_context_entropy"], 1)
            signalled = subprocess.run(
                args + ["--exit-on-alert"], cwd=root, capture_output=True,
                text=True, check=False,
            )
            self.assertEqual(signalled.returncode, 2, signalled.stderr)
            invalid = subprocess.run(
                [sys.executable, str(script), str(export),
                 "--expected-head", "f" * 64],
                cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("refused", invalid.stderr)

    def test_fifteen_real_steps_preserve_bounded_diagnostic_evidence(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "long.wal"))
            for _ in range(15):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            receipts = [
                row.causal_event for row in runtime.journal.entries
                if row.causal_event.get("kind") ==
                "stage12_lived_diagnostics_published"
            ]
            self.assertEqual(len(receipts), 15)
            self.assertEqual(
                [r["data"]["evidence_samples"] for r in receipts],
                [*range(1, 13), 12, 12, 12],
            )
            self.assertTrue(all(
                r["data"]["diagnostic_window"] == 12 for r in receipts
            ))
            audit = audit_stage12_operator_alerts(
                runtime.journal.canonical_bytes(),
                expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(audit.examined_samples, 15)
            self.assertEqual(audit.counts_by_signal["low_context_entropy"], 1)
            self.assertTrue(runtime.journal.verify())

    def test_alert_policy_is_validated_before_birth(self):
        with TemporaryDirectory() as folder:
            valid = actual_stage12_runtime(str(Path(folder) / "valid.wal"))
            from lab.stage12_runtime import Stage12Runtime
            for invalid in (0, -1, 1, True, 1.5):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    Stage12Runtime(
                        detector_policy=valid._stage12_detector_policy,
                        diagnostic_sample_cost_uc=1,
                        operator_alert_persistence_steps=invalid,
                    )


if __name__ == "__main__":
    unittest.main()
