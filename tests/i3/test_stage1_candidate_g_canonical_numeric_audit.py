"""Candidate-G canonical numerical semantics audit tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_canonical_numeric_audit as A


class CandidateGCanonicalNumericAuditTests(unittest.TestCase):
    def test_high_precision_arm_keeps_full_255_forecast(self):
        mind = A.make_high_precision_mind()
        self.assertEqual(mind.proj_chunks, (1,) * 255)

    def test_declared_audit_runs_without_prejudging_classification(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = A.run(fh.name)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertEqual(
            report["arms"]["historical_float_per_step"][
                "selected_epistemic"], 32)
        self.assertEqual(
            report["arms"]["historical_float_per_step"][
                "selected_water_deficit"], 8)
        self.assertEqual(
            report["arms"]["candidate_f_projection"][
                "selected_epistemic"], 24)
        self.assertEqual(
            report["arms"]["candidate_f_projection"][
                "selected_water_deficit"], 0)
        self.assertEqual(
            report["arms"]["canonical_high_precision_per_step"][
                "evaluated"], 80)
        self.assertEqual(
            report["arms"]["canonical_high_precision_per_step"][
                "actual_work_ceiling_violations"], 0)
        self.assertIn(
            report["classification"],
            (
                "HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT",
                "WATER_SELECTIONS_SURVIVE_CANONICAL_NUMERICS",
                "MIXED_WATER_NUMERIC_SEMANTICS",
            ))
        print("CANDIDATE_G_CANONICAL_NUMERIC_AUDIT " + json.dumps({
            "classification": report["classification"],
            "arms": {
                name: {
                    "selected_epistemic":
                        arm["selected_epistemic"],
                    "selected_water_deficit":
                        arm["selected_water_deficit"],
                    "selected_other_deficit":
                        arm["selected_other_deficit"],
                    "declined": arm["declined"],
                    "mean_work": arm["mean_work"],
                }
                for name, arm in report["arms"].items()
            },
            "historical_vs_canonical":
                report["historical_vs_canonical"],
            "canonical_vs_candidate_f":
                report["canonical_vs_candidate_f"],
        }, sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_g_canonical_numeric_audit; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
