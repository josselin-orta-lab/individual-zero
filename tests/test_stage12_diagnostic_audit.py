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
            # A rejected optional Stage12 sample may be retried in distinct
            # charged cognitive cycles of the *same* physical world step.
            # Each refused attempt must have one independently attested
            # deferral; no fabricated physical observation is counted.
            refused = [
                e for e in runtime.journal.entries
                if e.causal_event.get("kind") == "stage12_lived_diagnostics_deferred"
            ]
            self.assertGreaterEqual(len(refused), 1)
            self.assertEqual(report.deferred_samples, len(refused))
            self.assertTrue(all(
                e.causal_event["t_monde"] == 1 for e in refused
            ))
            self.assertEqual(report.charged_uc, 0)

    def test_rehashed_sample_count_inflation_is_rejected(self):
        import json
        from hashlib import sha256
        from lab.determinism import canonical_causal_bytes
        from lab.journal import GENESIS_HASH
        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "inflated.jsonl"))
            for _ in range(2):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            rows = [
                json.loads(raw)
                for raw in runtime.journal.canonical_bytes().split(b"\n")
            ]
            diagnostic = [
                row for row in rows
                if row["causal_event"].get("kind") ==
                "stage12_lived_diagnostics_published"
            ]
            self.assertEqual(len(diagnostic), 2)
            diagnostic[-1]["causal_event"]["data"]["evidence_samples"] = 1
            prior = GENESIS_HASH
            for index, row in enumerate(rows):
                row["index"] = index
                row["previous_hash"] = prior
                prior = sha256(
                    bytes.fromhex(prior) + canonical_causal_bytes({
                        "event_id": row["event_id"],
                        "causal_event": row["causal_event"],
                    })
                ).hexdigest()
                row["event_hash"] = prior
            forged = b"\n".join(canonical_causal_bytes(row) for row in rows)
            # A properly rehashed archive is still not valid evidence of
            # diagnostic samples: each actual acceptance increments once.
            self.assertEqual(audit_export_bytes(forged).occurrences, len(rows))
            with self.assertRaisesRegex(ValueError, "sample count drift"):
                audit_stage12_diagnostics(forged)

    def test_long_life_bounded_counter_with_explicit_window_and_attack(self):
        import json
        from hashlib import sha256
        from lab.determinism import canonical_causal_bytes
        from lab.journal import GENESIS_HASH

        def rechain(rows):
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

        with TemporaryDirectory() as folder:
            runtime = stage12_runtime(str(Path(folder) / "long-life.jsonl"))
            for _ in range(15):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            raw = runtime.journal.canonical_bytes()
            # The old runtime wrote the bounded `evidence_samples` but not
            # the policy window. A legacy archive can only be verified
            # until the first ambiguous saturation; it must not invent a
            # window size from an attacker-controlled plateau.
            rows = [json.loads(line) for line in raw.split(b"\n")]
            # Both older Stage12 runtimes and newer versions declaring a
            # window can be exercised: remove the versioned field from a
            # separate archival copy to test the ambiguous legacy case.
            legacy = [json.loads(line) for line in raw.split(b"\n")]
            for row in legacy:
                if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published":
                    row["causal_event"]["data"].pop("diagnostic_window", None)
            with self.assertRaisesRegex(ValueError, "sample count drift"):
                audit_stage12_diagnostics(rechain(legacy))
            diagnostics = [
                row["causal_event"]["data"] for row in rows
                if row["causal_event"]["kind"] ==
                "stage12_lived_diagnostics_published"
            ]
            self.assertEqual(len(diagnostics), 15)
            self.assertEqual([d["evidence_samples"] for d in diagnostics],
                             [*range(1, 13), 12, 12, 12])
            for data in diagnostics:
                data["diagnostic_window"] = 12
            bounded = rechain(rows)
            self.assertEqual(audit_export_bytes(bounded).occurrences, len(rows))
            evidence = audit_stage12_diagnostics(bounded)
            self.assertEqual(evidence.diagnostic_samples, 15)
            self.assertEqual(evidence.deferred_samples, 0)
            self.assertEqual(evidence.charged_uc, 15)

            # Rehashing a forged earlier plateau cannot launder evidence.
            diagnostics[5]["evidence_samples"] = 5
            fake = rechain(rows)
            self.assertEqual(audit_export_bytes(fake).occurrences, len(rows))
            with self.assertRaisesRegex(ValueError, "sample count drift"):
                audit_stage12_diagnostics(fake)
            diagnostics[5]["evidence_samples"] = 6

            diagnostics[12]["diagnostic_window"] = 2
            forged_policy = rechain(rows)
            self.assertEqual(audit_export_bytes(forged_policy).occurrences, len(rows))
            with self.assertRaisesRegex(ValueError, "diagnostic window changed"):
                audit_stage12_diagnostics(forged_policy)

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
