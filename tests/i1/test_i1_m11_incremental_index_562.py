"""#562: the derived incremental M11 source index must preserve the natural audit."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class M11IncrementalClosedIndex562(unittest.TestCase):
    def test_canonical_m11_life_with_incremental_observer_index(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "report"
            proc = subprocess.run([
                sys.executable, str(ROOT / "tools/run_i1_world_preset.py"),
                "--preset", "empty-land", "--custody", "m11",
                "--steps", "3", "--lives", "1",
                "--output-dir", str(output),
            ], cwd=ROOT, env=os.environ.copy(), capture_output=True,
               text=True, timeout=150)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["status"], "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
            self.assertEqual(len(report["lives"]), 1)
            life = report["lives"][0]
            self.assertTrue(life["steps"])
            self.assertEqual(
                life["journal_head"], life["steps"][-1]["journal_head"])
            for step in life["steps"]:
                custody = step["autobiographical_sleep_custody_467"]
                self.assertGreaterEqual(custody["memory_seen_after"],
                                        custody["memory_seen_before"])
                self.assertGreaterEqual(custody["auto_commit_count"], 0)
                self.assertIn(step["lifecycle"], ("active", "dead"))


if __name__ == "__main__":
    unittest.main()
