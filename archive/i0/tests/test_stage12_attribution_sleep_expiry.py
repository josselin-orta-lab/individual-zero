"""Issue110 GA-06: a sleeping physical step expires a pair, not a sample.

The tiny physical run is a software regression fixture, not an additional
scientific life. Rehashed missing-expiry journals must fail semantic audit.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_stage12_issue110_food_self_agency as experiment

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs


def rechained(rows):
    prior = GENESIS_HASH
    for index, row in enumerate(rows):
        row["index"] = index
        row["previous_hash"] = prior
        prior = sha256(bytes.fromhex(prior) + canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })).hexdigest()
        row["event_hash"] = prior
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class Stage12SleepingAttributionExpiryTests(unittest.TestCase):
    def test_sleep_gap_expires_once_and_missing_receipt_rehash_rejected(self):
        original_limit = experiment.MAX_STEPS
        try:
            experiment.MAX_STEPS = 8
            with TemporaryDirectory() as directory:
                root = Path(directory)
                report = experiment.run_life(
                    root, "physical_food_corpus", 70.0, "horizon_three",
                )
                self.assertIsNone(report["audit_error"], report["audit_error"])
                raw = (root / "canonical.jsonl").read_bytes()
                receipts = [json.loads(line) for line in raw.splitlines()]
                expired = [row for row in receipts
                           if row["causal_event"]["kind"]
                           == "stage12_attribution_sample_unavailable"
                           and row["causal_event"]["data"].get("reason")
                           == "no_waking_diagnostic_at_due_step"]
                self.assertEqual(len(expired), 1)
                pair_report = audit_stage12_attribution_pairs(
                    raw, expected_head=report["journal_head"],
                    expected_count=report["occurrences"],
                )
                self.assertEqual(pair_report.admitted_pairs, 1)
                self.assertEqual(pair_report.applied_pairs, 0)
                self.assertEqual(pair_report.missed_pairs, 1)
                self.assertEqual(pair_report.join_uc, 1)
                forged = rechained([
                    row for row in receipts
                    if row["event_id"] != expired[0]["event_id"]
                ])
                self.assertEqual(
                    audit_export_bytes(forged).world_steps_closed, 8,
                )
                with self.assertRaisesRegex(
                    ValueError, "admitted pair missing next-step",
                ):
                    audit_stage12_attribution_pairs(forged)

                # Even a perfectly rehashed ledger cannot claim that the
                # intervening physical step was asleep if its original
                # reduced-perception sleep source is missing.
                without_sleep_receipt = rechained([
                    row for row in receipts
                    if not (
                        row["causal_event"]["kind"] == "stage10_reduced_capture"
                        and row["causal_event"]["t_monde"] == 6
                    )
                ])
                self.assertEqual(
                    audit_export_bytes(without_sleep_receipt).world_steps_closed, 8,
                )
                with self.assertRaisesRegex(
                    ValueError, "false sleeping attribution-expiry evidence",
                ):
                    audit_stage12_attribution_pairs(without_sleep_receipt)
        finally:
            experiment.MAX_STEPS = original_limit


if __name__ == "__main__":
    unittest.main()
