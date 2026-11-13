"""No-World R2.4 authority-v3 host-cost and deterministic state-growth checks.

These tests measure no physiology, cognition tariff or production release.
Timing observations are intentionally not used as pass/fail thresholds.
"""
import json
import unittest

from i3.lab.engineering_remote_authority_cost_probe import probe
from i3.lab.engineering_remote_authority import DB_SCHEMA


class AuthorityCostProbeTests(unittest.TestCase):
    def test_refuses_nonpositive_noninteger_or_over_horizon(self):
        for steps in (None, False, True, 0, -1, 101, 1.0, "8"):
            with self.subTest(steps=steps):
                with self.assertRaisesRegex(ValueError, "integer"):
                    probe(steps)

    def test_small_single_step_is_terminal_and_nonce_count_is_exact(self):
        result = probe(1)
        self.assertEqual(result["schema"], DB_SCHEMA)
        self.assertEqual(result["audit_events"], 3)
        self.assertEqual(result["accepted_request_nonces"], 4)
        self.assertEqual(result["terminal"], "CENSORED")
        self.assertEqual(result["world_steps"], 0)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertFalse(result["independent_m11_attested"])

    def test_three_length_host_profile_records_actual_cost_without_a_release_claim(self):
        rows = [probe(steps) for steps in (8, 32, 80)]
        for row in rows:
            with self.subTest(steps=row["steps"]):
                n = row["steps"]
                self.assertEqual(row["schema"], DB_SCHEMA)
                self.assertEqual(row["audit_events"], 1 + 2 * n)
                self.assertEqual(row["accepted_request_nonces"], 1 + 3 * n)
                self.assertEqual(row["terminal"], "CENSORED")
                self.assertEqual(row["world_steps"], 0)
                self.assertEqual(row["scientific_lives"], 0)
                self.assertFalse(row["independent_m11_attested"])
                self.assertGreater(row["disk_bytes_db_wal_shm"], 0)
                self.assertEqual(row["verify"]["samples"], n)
                self.assertEqual(row["prepare"]["samples"], n)
                self.assertEqual(row["commit"]["samples"], n)
                self.assertEqual(row["cas_step_host_only"]["samples"], n)
                self.assertLessEqual(
                    row["first_quarter_step"]["median_ms"],
                    row["first_quarter_step"]["max_ms"])
                self.assertLessEqual(
                    row["last_quarter_step"]["median_ms"],
                    row["last_quarter_step"]["max_ms"])
                self.assertGreater(row["cas_step_host_only"]["p95_ms"], 0)
                # Diagnostic only: no timing/size comparison is a pass gate.
                print("R24_AUTHORITY_COST " + json.dumps(row, sort_keys=True),
                      flush=True)


if __name__ == "__main__":
    unittest.main()
