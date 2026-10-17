"""Fast smoke for the full 600-step independent mortal Stage11 diagnostic."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex


class Stage11AutonomousFullJournalProbeTests(unittest.TestCase):
    def test_small_real_cognitive_trajectory_uses_no_external_science(self):
        completed = subprocess.run(
            [sys.executable, "-m", "lab.stage11_autonomous_600_step_probe",
             "--steps", "3"],
            capture_output=True, text=True, timeout=90,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        prefix = "stage11_autonomous_600_step="
        self.assertTrue(completed.stdout.startswith(prefix), completed.stdout)
        result = json.loads(completed.stdout[len(prefix):])
        signature = result.pop("evidence_sha256")
        self.assertEqual(sha256_hex(canonical_causal_bytes(result)), signature)
        self.assertEqual(result["steps_physically_executed"], 3)
        self.assertEqual(result["perceptual_captures"], 3)
        self.assertEqual(result["cognitive_autobiographical_commits"], 3)
        self.assertEqual(result["world_transitions"], 3)
        self.assertEqual(result["terminal_deaths"], 0)
        self.assertIsNone(result["scientific_verdict"])
        self.assertTrue(result["offline_audit_completed"])
        self.assertFalse(result["external_oracle_loaded"])
        self.assertFalse(result["external_bench_loaded"])
        self.assertEqual([a["world_step"] for a in result["journal_prefix_anchors"]], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
