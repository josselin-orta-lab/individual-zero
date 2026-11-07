"""Stage-1 high-precision state oracle for future projection candidates."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_event_error_decomposition as X
from i3.lab import projection_high_precision_oracle as H
from i3.modules.genome import midpoint


class ProjectionHighPrecisionOracleTests(unittest.TestCase):
    def test_exposed_death_boundary_matches_event_exact_not_raw_per_step(self):
        body = (80., 10., 80., 80., 80.)
        _hv, high_body, paid = H.direct_high_precision(
            midpoint(), body, sleep_learned=True)
        _ev, event_body, _epaid = X.direct_event_exact(
            midpoint(), body, sleep_learned=True)
        _rv, raw_body, _rpaid = X.direct_per_step(
            midpoint(), body, sleep_learned=True)

        self.assertEqual(paid, 255)
        for a, b in zip(high_body, event_body):
            self.assertAlmostEqual(a, b, delta=1e-10)
        self.assertGreater(
            max(abs(a - b) for a, b in zip(high_body, raw_body)),
            0.1)

    def test_oracle_is_laboratory_only(self):
        from i3.modules.mind import PROJECTION_ACCOUNTING
        self.assertNotIn("high_precision", PROJECTION_ACCOUNTING)
        self.assertNotIn("event_exact", PROJECTION_ACCOUNTING)

    def test_full_frozen_grid_records_prospective_oracle_verdict(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "oracle.json"
            report = H.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertEqual(
            report["paid_high_precision_projection_units"],
            {
                "min": 255,
                "mean": 255.0,
                "max": 255,
                "historical_per_step": 255,
            })
        self.assertIn(
            report["classification"],
            (
                "EVENT_EXACT_MATCHES_HIGH_PRECISION_ORACLE",
                "NO_NUMERICAL_SEMANTICS_DIFFERENCE_ON_FROZEN_GRID",
                "EVENT_SEGMENTATION_DIFFERS_FROM_HIGH_PRECISION_ORACLE",
            ))
        self.assertFalse(report["historical_gates_changed"])
        self.assertFalse(report["candidate_promoted"])
        self.assertFalse(report["omega_rerun_authorized"])
        print(
            "HIGH_PRECISION_PROJECTION_ORACLE",
            json.dumps({
                "classification": report["classification"],
                "oracle_invariant":
                    report[
                        "oracle_projection_equivalent_invariant_max_gap"],
                "comparisons": report["comparisons"],
                "paid": report[
                    "paid_high_precision_projection_units"],
                "authorized":
                    report[
                        "oracle_authorized_for_future_candidates"],
                "worst_cases": report["worst_cases"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_high_precision_oracle; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
