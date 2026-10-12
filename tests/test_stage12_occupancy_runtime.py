"""Integrated S_t module entropy has explicit UC costs and offline provenance."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from lab.compute_budget import BudgetCharge
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_occupancy_audit import audit_stage12_occupancy
from test_stage12_mortal_runtime import stage12_runtime


def _rechain(rows):
    previous = GENESIS_HASH
    for number, row in enumerate(rows):
        row["index"] = number
        row["previous_hash"] = previous
        previous = sha256(
            bytes.fromhex(previous) + canonical_causal_bytes({
                "event_id": row["event_id"],
                "causal_event": row["causal_event"],
            })
        ).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class Stage12OccupancyRuntimeTests(unittest.TestCase):
    def test_real_lived_s_t_provenance_and_charges(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(
                str(Path(folder) / "occupied.jsonl"), occupancy_cost=2,
            )
            budget = runtime.compute_budget._config
            self.assertEqual(
                budget.operation_costs["stage12_occupancy_entropy"], 2,
            )
            for _ in range(4):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            raw = runtime.journal.canonical_bytes()
            sample_events = [
                row.causal_event
                for row in runtime.journal.entries
                if row.causal_event.get("kind") ==
                "stage12_st_module_occupancy_published"
            ]
            self.assertGreaterEqual(len(sample_events), 4)
            self.assertTrue(all(
                row["data"]["operator_only_diagnostic"] is True
                and row["data"]["charged_uc"] == 2
                and row["data"]["module_universe_size"] == 8
                and row["data"]["st_version"].startswith("S_t:")
                and sum(row["data"]["module_counts"].values()) ==
                    row["data"]["occupied_slots"]
                for row in sample_events
            ))
            result = audit_stage12_occupancy(
                raw, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(result.evaluated_cycles, len(sample_events))
            self.assertEqual(result.deferred_cycles, 0)
            self.assertEqual(result.charged_uc, len(sample_events) * 2)
            self.assertEqual(
                result.occurrences, audit_export_bytes(raw).occurrences,
            )
            self.assertTrue(runtime.journal.verify())

    def test_refused_optional_uc_never_invents_an_occupancy_result(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "refused.jsonl"))
            original = runtime.compute_budget.charge

            def refuse(*, module, operation, count=1):
                if operation == "stage12_occupancy_entropy":
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
            report = audit_stage12_occupancy(runtime.journal.canonical_bytes())
            self.assertEqual(report.evaluated_cycles, 0)
            self.assertGreaterEqual(report.deferred_cycles, 1)
            self.assertEqual(report.charged_uc, 0)
            self.assertTrue(runtime.journal.verify())

    def test_rehashed_forged_occupancy_rejected_beyond_hash_verification(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "forged.jsonl"))
            self.assertEqual(runtime.run_step().execution_status, "applied")
            raw = runtime.journal.canonical_bytes()
            self.assertGreater(audit_stage12_occupancy(raw).evaluated_cycles, 0)
            rows = [json.loads(line) for line in raw.split(b"\n")]
            report = next(
                row for row in rows
                if row["causal_event"].get("kind") ==
                "stage12_st_module_occupancy_published"
            )
            report["causal_event"]["data"]["module_counts"] = {"planning": 999}
            fake = _rechain(rows)
            self.assertEqual(audit_export_bytes(fake).occurrences, len(rows))
            with self.assertRaisesRegex(ValueError, "diverges from admitted"):
                audit_stage12_occupancy(fake)

    def test_operator_cli_verifies_current_custody_without_importing_i0(self):
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "report_stage12_occupancy.py"
        auditor = (
            root / "src" / "lab" / "stage12_occupancy_audit.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("from i0", auditor)
        self.assertNotIn("import i0", auditor)
        with TemporaryDirectory() as folder:
            export = Path(folder) / "canonical.jsonl"
            runtime = stage12_runtime(str(Path(folder) / "life.wal"))
            for _ in range(2):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            export.write_bytes(runtime.journal.canonical_bytes())
            args = [
                sys.executable, str(script), str(export),
                "--expected-head", runtime.journal.head_hash,
                "--expected-count", str(len(runtime.journal.entries)),
            ]
            completed = subprocess.run(
                args, cwd=root, capture_output=True, text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertGreaterEqual(report["evaluated_cycles"], 2)
            self.assertEqual(report["deferred_cycles"], 0)
            denied = subprocess.run(
                [sys.executable, str(script), str(export),
                 "--expected-head", "f" * 64,
                 "--expected-count", str(len(runtime.journal.entries))],
                cwd=root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(denied.returncode, 1)
            self.assertIn("refused", denied.stderr)

    def test_occupancy_cost_cannot_be_zero_or_boolean(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "good.jsonl"))
            from lab.stage12_runtime import Stage12Runtime
            for invalid in (0, -1, True, 0.5):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    Stage12Runtime(
                        detector_policy=runtime._stage12_detector_policy,
                        diagnostic_sample_cost_uc=1,
                        module_occupancy_cost_uc=invalid,
                    )


if __name__ == "__main__":
    unittest.main()
