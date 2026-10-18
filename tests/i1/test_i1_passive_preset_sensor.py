"""Operator-only I1 sensor contract: no action invention or feedback to I1."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PassivePresetSensorTests(unittest.TestCase):
    def test_natural_wal_report_exposes_execution_aligned_action_metadata(self):
        with TemporaryDirectory(prefix="i1-sensor-") as tmp:
            folder = Path(tmp) / "birth"
            p = subprocess.run([
                sys.executable, str(ROOT / "tools/run_i1_world_preset.py"),
                "--preset", "oasis", "--seed", "246", "--steps", "2",
                "--lives", "1", "--custody", "wal", "--output-dir", str(folder)
            ], cwd=ROOT, text=True, capture_output=True, timeout=120)
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
            report = json.loads((folder / "report.json").read_text())
            self.assertEqual(report["engine"], "I1")
            self.assertEqual(report["status"], "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
            self.assertEqual(len(report["lives"]), 1)
            steps = report["lives"][0]["steps"]
            self.assertGreater(len(steps), 0)
            for step in steps:
                self.assertIn(step["execution"], ("applied", "dead", "safety_block"))
                self.assertIn("action_primitive", step)
                self.assertIn("action_source", step)
                self.assertIsInstance(step["reflex_triggered"], bool)
                self.assertIsInstance(step["fallback_used"], bool)
                self.assertIsInstance(step["cycles_used"], int)
                if step["execution"] in ("applied", "dead"):
                    self.assertIsInstance(step["action_primitive"], str)
                    self.assertTrue(step["action_primitive"])
            self.assertIn("journal_head", report["lives"][0])
            self.assertNotIn("action_primitive", report.get("environment", {}))


if __name__ == "__main__":
    unittest.main()
