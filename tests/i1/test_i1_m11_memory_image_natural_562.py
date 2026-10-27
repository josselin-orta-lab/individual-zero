"""#562: M11 operator Memory-image reuse versus full-export reference."""
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
import i1_m11_memory_image

class FullExportReference:
    def before_step(self, owner, *, episode_count):
        image = owner.export_causal_state()
        if len(image["episodes"]) != episode_count:
            raise RuntimeError("reference pre-step drift")
        return image
    def after_step(self, owner, *, episode_count):
        image = owner.export_causal_state()
        if len(image["episodes"]) < episode_count:
            raise RuntimeError("reference post-step drift")
        return image

mode, preset, seed, steps, output = sys.argv[1:]
if mode == "reference":
    with patch.object(i1_m11_memory_image, "CommittedMemoryImage",
                      FullExportReference):
        runner.execute(preset_name=preset, seed=int(seed), steps=int(steps),
                       lives=1, custody="m11", output_dir=Path(output))
else:
    runner.execute(preset_name=preset, seed=int(seed), steps=int(steps),
                   lives=1, custody="m11", output_dir=Path(output))
"""


class M11MemoryImageNaturalParity562(unittest.TestCase):
    def test_natural_reports_are_identical_to_full_export_reference(self):
        # Independent canonical births; no injected Memory, free UC or
        # substituted decisions. Report includes M11 journal-head custody.
        with TemporaryDirectory() as root:
            for preset, seed, steps in (
                ("empty-land", 246, 3),
                ("oasis", 247, 5),
                ("hazard-edge", 248, 4),
            ):
                reports = []
                for mode in ("reference", "incremental"):
                    output = Path(root) / (preset + "-" + mode)
                    proc = subprocess.run(
                        [sys.executable, "-c", PROGRAM, mode, preset,
                         str(seed), str(steps), str(output)],
                        cwd=ROOT, env=os.environ.copy(),
                        text=True, capture_output=True, timeout=240,
                    )
                    self.assertEqual(proc.returncode, 0,
                                     proc.stdout + proc.stderr)
                    report = json.loads((output / "report.json").read_text())
                    self.assertEqual(report["status"],
                                     "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
                    self.assertTrue(report["lives"][0]["steps"])
                    reports.append(report)
                self.assertEqual(
                    json.dumps(reports[0], sort_keys=True, ensure_ascii=False),
                    json.dumps(reports[1], sort_keys=True, ensure_ascii=False),
                    "operator Memory export reuse changed a natural M11 report"
                )


if __name__ == "__main__":
    unittest.main()
