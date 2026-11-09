"""Declared distress-evaluation reuse diagnostic tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_distress_reuse_diagnostic as R


class DistressReuseDiagnosticTests(unittest.TestCase):
    def test_probe_observes_without_changing_existing_work(self):
        row = R.evaluate_state((80., 80., 30., 80., 80.), 6)
        self.assertEqual(row["project_calls"], 5)
        self.assertEqual(
            row["actual_simulated_steps"],
            row["work_unchanged"]["simulated_steps"])
        self.assertEqual(
            row["projection_paid_endpoints"],
            row["feature_evaluations"] + row["death_endpoint_units"])
        self.assertLessEqual(
            row["decision_memo_lower_total"],
            row["last_feature_reuse_total"])
        self.assertLessEqual(
            row["last_feature_reuse_total"],
            row["actual_simulated_steps"])

    def test_declared_80_state_probe_runs_without_prejudging_result(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = R.run(fh.name)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["work_accounting_changed"])
        self.assertEqual(report["summary"]["evaluated"], 80)
        self.assertEqual(report["summary"]["selected_epistemic"], 32)
        self.assertEqual(report["summary"]["selected_water_deficit"], 8)
        self.assertIn(
            report["verdict"],
            (
                "LAST_FEATURE_REUSE_PLAUSIBLE",
                "DECISION_LOCAL_FEATURE_MEMO_PLAUSIBLE",
                "FEATURE_REUSE_INSUFFICIENT",
            ))
        print("DISTRESS_REUSE_DIAGNOSTIC " + json.dumps(
            report["summary"], sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_distress_reuse_diagnostic; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
