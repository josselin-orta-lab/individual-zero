"""Exploratory projection probes: deterministic, software only."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_affordable_projection_probes as P


class AffordableProjectionProbeTests(unittest.TestCase):
    def test_anchored_grid_equals_reference_when_started_at_zero_on_one_step(self):
        mind = P.D.make_mind("reference")
        body = (80., 80., 30., 80., 80.)
        self.assertEqual(P.anchored_project(mind, body, 0), mind.project(body, mind._drift)[0])

    def test_probe_results_are_reproduced(self):
        self.assertAlmostEqual(P.local_sensitivity_probe()["drink"], 1.9099881563816057, places=9)
        self.assertAlmostEqual(P.anchored_grid_probe()["anchored"], 0.21527509401870826, places=9)

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([sys.executable, "-c",
                        "import sys; sys.path.insert(0, " + repr(root) + "); "
                        "import i3.lab.stage1_affordable_projection_probes; "
                        "assert 'i3.runtime.life' not in sys.modules"], check=True)


if __name__ == "__main__":
    unittest.main()
