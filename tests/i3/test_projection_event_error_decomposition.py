"""Stage-1 event projection residual-source decomposition."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_event_error_decomposition as X
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint


class EventProjectionErrorDecompositionTests(unittest.TestCase):
    def test_event_exact_is_diagnostic_not_runtime_accounting_mode(self):
        mind = P.make_mind(midpoint())
        self.assertNotIn("event_exact", getattr(
            __import__("i3.modules.mind", fromlist=["PROJECTION_ACCOUNTING"]),
            "PROJECTION_ACCOUNTING"))
        self.assertEqual(mind.projection_accounting, "chunk_end")

    def test_event_exact_matches_per_step_on_representative_projection(self):
        genome = midpoint()
        body = (80., 30., 30., 80., 80.)
        event_values, event_body, event_paid = X.direct_event_exact(
            genome, body, sleep_learned=True)
        truth_values, truth_body, truth_paid = X.direct_per_step(
            genome, body, sleep_learned=True)
        for a, b in zip(event_values, truth_values):
            self.assertAlmostEqual(a, b, delta=1e-10)
        for a, b in zip(event_body, truth_body):
            self.assertAlmostEqual(a, b, delta=1e-10)
        self.assertEqual(event_paid, len(P.PER_STEP))
        self.assertEqual(truth_paid, len(P.PER_STEP))

    def test_event_exact_plan_view_matches_per_step_representative(self):
        genome = midpoint()
        body = (80., 30., 30., 80., 80.)
        event = X.event_exact_values(
            genome, body, sleep_learned=False)
        truth = P.values(
            genome, body, "per_step", sleep_learned=False)
        for key in P.PLANS:
            self.assertAlmostEqual(event[key], truth[key], delta=1e-10)

    def test_full_frozen_decomposition_records_source_without_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "decomposition.json"
            report = X.run(path)
            self.assertEqual(
                report["cases"],
                3 * len(tuple(P.genomes())) * len(tuple(P.bodies())))
            self.assertIn(
                report["classification"],
                (
                    "INTERPOLATION_SOURCE_CONFIRMED_ON_FROZEN_GRID",
                    "NO_MATERIAL_RESIDUAL_AT_NUMERICAL_TOLERANCE",
                    "SEGMENTED_BODY_EVOLUTION_CONTRIBUTES",
                ))
            self.assertFalse(report["candidate_promoted"])
            self.assertFalse(report["omega_rerun_authorized"])
            self.assertEqual(json.loads(path.read_text()), report)
            print(
                "EVENT_PROJECTION_ERROR_DECOMPOSITION",
                json.dumps({
                    "event_exact_vs_per_step":
                        report["event_exact_vs_per_step"],
                    "event_quartic_vs_event_exact":
                        report["event_quartic_vs_event_exact"],
                    "paid_event_exact_projection_units":
                        report["paid_event_exact_projection_units"],
                    "classification": report["classification"],
                    "worst_cases": report["worst_cases"],
                }, sort_keys=True))

    def test_diagnostic_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.projection_event_error_decomposition; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
