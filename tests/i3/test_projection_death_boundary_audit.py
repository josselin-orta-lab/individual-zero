"""Stage-1 death-boundary arithmetic audit."""
from decimal import Decimal
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_death_boundary_audit as A


class ProjectionDeathBoundaryAuditTests(unittest.TestCase):
    def test_exposed_boundary_is_delayed_by_repeated_float_addition(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "boundary.json"
            report = A.run(path)

        self.assertEqual(
            report["classification"],
            "FLOAT_ACCUMULATION_DELAYS_REFERENCE_DEATH_BOUNDARY")
        self.assertEqual(report["repeated_unit"]["first_dead_step"], 51)
        self.assertEqual(report["algebraic_endpoint"]["first_dead_step"], 50)
        self.assertEqual(
            Decimal(report["decimal_food"]["50"]), Decimal("0"))

        step50 = report["repeated_unit"]["trace"]["50"]
        self.assertFalse(step50["dead"])
        self.assertGreater(step50["body"][1], 0.0)
        self.assertLess(step50["body"][1], 1e-12)

        algebraic50 = report["algebraic_endpoint"]["trace"]["50"]
        self.assertTrue(algebraic50["dead"])
        self.assertEqual(algebraic50["body"][1], 0.0)

    def test_one_delayed_step_matches_water_integrity_discrepancy(self):
        with tempfile.TemporaryDirectory() as td:
            report = A.run(Path(td) / "boundary.json")

        drift = report["drift"]
        delta = report[
            "death_endpoint_body_delta_repeated_minus_algebraic"]
        self.assertAlmostEqual(delta[2], drift[2], delta=1e-12)
        self.assertAlmostEqual(delta[3], drift[3], delta=1e-12)
        self.assertAlmostEqual(delta[2], -0.4, delta=1e-12)
        self.assertAlmostEqual(delta[3], 0.2, delta=1e-12)

        for actual, expected in zip(
                report["repeated_unit"]["dead_body"],
                report["per_step_final_body"]):
            self.assertAlmostEqual(actual, expected, delta=1e-12)
        for actual, expected in zip(
                report["algebraic_endpoint"]["dead_body"],
                report["event_exact_final_body"]):
            self.assertAlmostEqual(actual, expected, delta=1e-12)

    def test_audit_preserves_historical_and_future_gates(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "boundary.json"
            report = A.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertFalse(report["historical_gate_changed"])
        self.assertFalse(report["candidate_promoted"])
        self.assertFalse(report["omega_rerun_authorized"])
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)

    def test_audit_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_death_boundary_audit; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
