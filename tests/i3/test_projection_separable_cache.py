"""Exact separable projection-cache structural falsifier tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_separable_cache_characterization as S
from i3.modules.genome import midpoint


class SeparableProjectionCacheTests(unittest.TestCase):
    def test_single_projection_matches_per_step(self):
        body = (80., 30., 30., 80., 80.)
        candidate = S.make_mind(midpoint())
        truth = P.configure(P.make_mind(midpoint()), "per_step")
        c_values, c_body = candidate.project(
            body, candidate._drift)
        t_values, t_body = truth.project(
            body, truth._drift)
        for a, b in zip(c_values, t_values):
            self.assertAlmostEqual(a, b, places=11)
        for a, b in zip(c_body, t_body):
            self.assertAlmostEqual(a, b, places=12)

    def test_identical_projection_reuses_all_channel_traces(self):
        body = (80., 30., 30., 80., 80.)
        mind = S.make_mind(midpoint())
        mind.project(body, mind._drift)
        first = mind.cache_stats()
        self.assertEqual(first["channel_trace_builds"], 5)
        self.assertEqual(first["channel_trace_hits"], 0)
        mind.project(body, mind._drift)
        second = mind.cache_stats()
        self.assertEqual(second["channel_trace_builds"], 5)
        self.assertEqual(second["channel_trace_hits"], 5)
        self.assertEqual(second["channel_samples"], first["channel_samples"])

    def test_frozen_characterization_runs_without_prejudging_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = S.run(fh.name)
        self.assertEqual(
            report["schema"],
            "i3-stage1-separable-projection-cache/v1")
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertEqual(report["projection_grid"]["cases"], 486)
        self.assertEqual(report["nonlinear_option_set"]["bodies"], 10)
        self.assertIn(
            report["verdict"],
            ("SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_PASS",
             "SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_FAIL"))
        print("SEPARABLE_CACHE_REPORT " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "projection_grid": {
                "max_abs_option_value_error":
                    report["projection_grid"][
                        "max_abs_option_value_error"],
                "max_pairwise_decision_bias":
                    report["projection_grid"][
                        "max_pairwise_decision_bias"],
                "projection_equivalent_invariant_max_gap":
                    report["projection_grid"][
                        "projection_equivalent_invariant_max_gap"],
                "max_final_body_channel_error":
                    report["projection_grid"][
                        "max_final_body_channel_error"],
                "work": report["projection_grid"]["work"],
                "worst": report["projection_grid"]["worst"],
            },
            "nonlinear_option_set": {
                "max_abs_option_value_error":
                    report["nonlinear_option_set"][
                        "max_abs_option_value_error"],
                "max_pairwise_decision_bias":
                    report["nonlinear_option_set"][
                        "max_pairwise_decision_bias"],
                "max_final_body_channel_error":
                    report["nonlinear_option_set"][
                        "max_final_body_channel_error"],
                "work": report["nonlinear_option_set"]["work"],
                "worst": report["nonlinear_option_set"]["worst"],
            },
        }, sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_separable_cache_characterization; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
