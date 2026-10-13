"""Issue 110 independent audit: real WorldBody steps and rehashed forgeries."""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_attribution_provenance_audit import audit_stage12_attribution_provenance
from test_stage12_operator_alert_runtime import actual_stage12_runtime


def _rechain(rows):
    previous = GENESIS_HASH
    for index, row in enumerate(rows):
        row["index"] = index
        row["previous_hash"] = previous
        previous = sha256(bytes.fromhex(previous) + canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class Stage12AttributionProvenanceTests(unittest.TestCase):
    def test_real_physical_life_keeps_unproven_attribution_unavailable(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "life.wal"))
            for _ in range(5):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            raw = runtime.journal.canonical_bytes()
            report = audit_stage12_attribution_provenance(
                raw, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(report.admitted_pairs, 0)
            self.assertEqual(report.unavailable_diagnostics, 5)
            self.assertEqual(
                report.verified_successes + report.verified_failures
                + report.unknown_results,
                len([r for r in runtime.journal.entries
                     if r.causal_event.get("kind") == "stage12_goal_progress_followup"]),
            )
            self.assertIsNone(runtime.detection_report.attribution_bias)
            self.assertFalse(report.as_dict()["bias_calibration_supported"])

    def test_rehashed_diagnostic_attribution_is_not_evidence(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "forge.wal"))
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            rows = [json.loads(x) for x in runtime.journal.canonical_bytes().split(b"\n")]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published")
            target["attribution_ref"] = "invented"
            target["agency"] = "self"
            target["outcome"] = "success"
            forged = _rechain(rows)
            self.assertTrue(audit_export_bytes(forged).world_steps_closed >= 3)
            with self.assertRaisesRegex(ValueError, "uncontracted attribution source"):
                audit_stage12_attribution_provenance(forged)

    def test_rehashed_positive_bias_is_refused(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "bias.wal"))
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            rows = [json.loads(x) for x in runtime.journal.canonical_bytes().split(b"\n")]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "stage12_lived_diagnostics_published")
            target["attribution_bias"] = "self_serving_pattern"
            forged = _rechain(rows)
            audit_export_bytes(forged)
            with self.assertRaisesRegex(ValueError, "unverified lived attribution bias claim"):
                audit_stage12_attribution_provenance(forged)


if __name__ == "__main__":
    unittest.main()
