"""External Stage12 diagnostic audits reject forged but rehashed receipts."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.independent_journal_audit import audit_export_bytes
from test_stage12_mortal_runtime import stage12_runtime


class Stage12IndependentDiagnosticAuditTests(unittest.TestCase):
    def test_real_runtime_debits_match_each_diagnostic_publication(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "life.jsonl"))
            for _ in range(5):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            data = runtime.journal.canonical_bytes()
            report = audit_stage12_diagnostics(
                data, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(report.world_steps_closed, 5)
            self.assertEqual(report.diagnostic_samples, 5)
            self.assertEqual(report.deferred_samples, 0)
            self.assertEqual(report.charged_uc, 5)
            self.assertEqual(report.occurrences, audit_export_bytes(data).occurrences)
            self.assertTrue(runtime.journal.verify())

    def test_real_budget_refusal_does_not_create_a_sample(self):
        from unittest.mock import patch
        from lab.compute_budget import BudgetCharge
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "refused.jsonl"))
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
            report = audit_stage12_diagnostics(runtime.journal.canonical_bytes())
            self.assertEqual(report.diagnostic_samples, 0)
            self.assertEqual(report.deferred_samples, 1)
            self.assertEqual(report.charged_uc, 0)

    def test_untrusted_content_and_head_fail_closed(self):
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "tamper.jsonl"))
            runtime.run_step()
            raw = runtime.journal.canonical_bytes()
            with self.assertRaises(ValueError):
                audit_stage12_diagnostics(raw, expected_head="f" * 64)
            tampered = raw.replace(
                b"stage12_lived_diagnostics_published",
                b"stage12_lived_diagnostics_malformed",
                1,
            )
            self.assertNotEqual(tampered, raw)
            with self.assertRaises(ValueError):
                audit_stage12_diagnostics(tampered)


if __name__ == "__main__":
    unittest.main()
