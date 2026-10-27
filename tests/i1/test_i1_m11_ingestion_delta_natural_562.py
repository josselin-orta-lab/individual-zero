"""#562: compare complete M11 reports with the legacy full first-ingestion scan."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = r"""
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path.cwd() / "tools"))
import run_i1_world_preset as runner
import i1_m11_ingestion_delta

legacy_calls = 0

def old_scan(first, current, *, world_step):
    global legacy_calls
    legacy_calls += 1
    for ref in current:
        first.setdefault(ref, world_step)

mode, preset, seed, steps, output = sys.argv[1:]
if mode == "reference":
    with patch.object(i1_m11_ingestion_delta,
                      "update_first_memory_ingestion", old_scan):
        # The runner imports the helper inside _m11_life on each birth.
        runner.execute(preset_name=preset, seed=int(seed), steps=int(steps),
                       lives=1, custody="m11", output_dir=Path(output))
    assert legacy_calls > 0, "reference first-ingestion loop was never exercised"
    print("M11_REFERENCE_SCAN_CALLED:", legacy_calls)
else:
    runner.execute(preset_name=preset, seed=int(seed), steps=int(steps),
                   lives=1, custody="m11", output_dir=Path(output))
"""

class NaturalFirstIngestionParity562(unittest.TestCase):
    def test_reports_match_legacy_first_ingestion_scan(self):
        with TemporaryDirectory() as tmp:
            for preset, seed, steps in (("empty-land", 246, 3),
                                        ("oasis", 247, 5),
                                        ("hazard-edge", 248, 4)):
                reports = []
                for mode in ("reference", "delta"):
                    output = Path(tmp) / f"{preset}-{mode}"
                    proc = subprocess.run([sys.executable, "-c", PROGRAM,
                        mode, preset, str(seed), str(steps), str(output)],
                        cwd=ROOT, env=os.environ.copy(), text=True,
                        capture_output=True, timeout=240)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    if mode == "reference":
                        self.assertIn("M11_REFERENCE_SCAN_CALLED:", proc.stdout)
                    report = json.loads((output / "report.json").read_text())
                    self.assertEqual(report["status"],
                                     "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
                    reports.append(report)
                self.assertEqual(reports[0], reports[1], preset)

if __name__ == "__main__":
    unittest.main()
