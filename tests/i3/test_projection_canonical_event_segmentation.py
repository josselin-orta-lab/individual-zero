"""Stage-1 canonical event segmentation against the end-to-end oracle."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_canonical_event_segmentation as C
from i3.lab import projection_end_to_end_numeric_oracle as O
from i3.modules.genome import midpoint
from i3.modules.mind import PROJECTION_ACCOUNTING


class CanonicalEventSegmentationTests(unittest.TestCase):
    def test_diagnostic_is_not_a_runtime_mode(self):
        self.assertNotIn("canonical_event_exact", PROJECTION_ACCOUNTING)

    def test_exposed_boundary_matches_direct_oracle(self):
        body = (80., 10., 80., 80., 80.)
        event, event_body, _segments, paid = C.direct(
            midpoint(), body, sleep_learned=True)
        oracle, oracle_body, oracle_paid = O.direct_projection(
            midpoint(), body, sleep_learned=True)

        self.assertEqual(paid, 255)
        self.assertEqual(oracle_paid, 255)
        for a, b in zip(event, oracle):
            self.assertAlmostEqual(a, b, delta=1e-10)
        for a, b in zip(event_body, oracle_body):
            self.assertAlmostEqual(a, b, delta=1e-10)

    def test_event_segmentation_actually_compresses_regime_boundaries(self):
        body = (80., 30., 30., 80., 80.)
        _event, _final, segments, paid = C.direct(
            midpoint(), body, sleep_learned=True)
        self.assertLess(segments, paid)
        self.assertEqual(paid, 255)

    def test_full_frozen_grid_records_boundary_verdict(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "canonical-event.json"
            report = C.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertEqual(
            report["paid_endpoint_units"],
            {
                "min": 255,
                "mean": 255.0,
                "max": 255,
                "expected": 255,
            })
        self.assertIn(
            report["classification"],
            (
                "CANONICAL_EVENT_SEGMENTATION_MATCHES_ORACLE",
                "CANONICAL_EVENT_SEGMENTATION_DIFFERS_FROM_ORACLE",
            ))
        self.assertFalse(report["candidate_promoted"])
        self.assertFalse(report["omega_rerun_authorized"])
        print(
            "CANONICAL_EVENT_SEGMENTATION",
            json.dumps({
                "classification": report["classification"],
                "value_error":
                    report[
                        "max_projection_value_error_vs_oracle"],
                "body_error":
                    report[
                        "max_final_body_error_vs_oracle"],
                "segments": report["event_segments"],
                "paid": report["paid_endpoint_units"],
                "cleared":
                    report[
                        "event_boundaries_cleared_for_candidate_e"],
                "worst_cases": report["worst_cases"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_canonical_event_segmentation; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
