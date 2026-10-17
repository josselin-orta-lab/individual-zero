"""Read-only census cannot make unknown, sleep or pending count as evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_calibration_feasibility import coverage_census


class CoverageCensusTests(unittest.TestCase):
    def test_sleep_expiry_and_horizon_are_not_usable_samples(self):
        trace = [
            {"step": 2, "receipts": [
                {"event": "intent"}, {"event": "agency_precommit"}]},
            {"step": 3, "receipts": [
                {"event": "agency_judgement", "agency": "self"},
                {"event": "pair_admitted", "outcome": "success", "agency": "self"}]},
            {"step": 4, "receipts": [
                {"event": "sleep_reduced_capture"}]},
            {"step": 5, "receipts": [
                {"event": "pair_unavailable",
                 "reason": "no_waking_diagnostic_at_due_step"}]},
            {"step": 6, "receipts": [
                {"event": "agency_judgement", "agency": "unknown"},
                {"event": "pair_admitted", "outcome": "failure", "agency": "world"}]},
        ]
        report = coverage_census(trace)
        self.assertEqual(report["admitted_pairs"], 2)
        self.assertEqual(report["applied_pairs"], 0)
        self.assertEqual(report["sleep_expired_pairs"], 1)
        self.assertEqual(report["unresolved_at_horizon"], 1)
        self.assertEqual(report["unknown_judgements"], 1)

    def test_refuse_duplicate_or_missing_custody(self):
        trace = [{"step": 2, "receipts": [
            {"event": "pair_admitted"}, {"event": "pair_unavailable",
             "reason": "diagnostic_uc_refused"},
            {"event": "diagnostic", "pair_applied": True},
        ]}]
        with self.assertRaises(ValueError):
            coverage_census(trace)

    def test_unrecognized_expiry_is_not_normalized_to_sleep(self):
        with self.assertRaises(ValueError):
            coverage_census([{"step": 3, "receipts": [
                {"event": "pair_admitted"},
                {"event": "pair_unavailable", "reason": "unknown"},
            ]}])


if __name__ == "__main__":
    unittest.main()
