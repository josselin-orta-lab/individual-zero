"""Stage-1 end-to-end high-precision numerical oracle."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import projection_end_to_end_numeric_oracle as O
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint
from i3.modules.mind import PROJECTION_ACCOUNTING


class EndToEndNumericOracleTests(unittest.TestCase):
    def test_oracle_is_lab_only(self):
        self.assertNotIn(
            "end_to_end_high_precision", PROJECTION_ACCOUNTING)
        self.assertNotIn("high_precision", PROJECTION_ACCOUNTING)
        self.assertNotIn("event_exact", PROJECTION_ACCOUNTING)

    def test_exposed_boundary_uses_high_precision_state_semantics(self):
        body = (80., 10., 80., 80., 80.)
        _projection, final_body, paid = O.direct_projection(
            midpoint(), body, sleep_learned=True)
        self.assertEqual(paid, 255)
        self.assertAlmostEqual(final_body[1], 0.0, delta=1e-10)
        self.assertAlmostEqual(final_body[2], 60.0, delta=1e-10)
        self.assertAlmostEqual(final_body[3], 90.0, delta=1e-10)

    def test_projection_equivalent_wait_is_end_to_end_consistent(self):
        genome = midpoint()
        body = (80., 20., 80., 80., 80.)
        values = O.values(
            genome, body,
            sleep_learned=False,
            projection_equivalent=True)
        self.assertAlmostEqual(
            values["plus_1_wait"] - values["prefix"],
            0.0,
            delta=1e-10)
        self.assertAlmostEqual(
            values["plus_3_waits"] - values["prefix"],
            0.0,
            delta=1e-10)

    def test_plan_and_bootstrap_share_one_paid_chain(self):
        body = (80., 30., 30., 80., 80.)
        mind = P.make_mind(
            midpoint(),
            sleep_learned=False,
            projection_equivalent=True)
        budget = CognitiveBudget(body, BodyLaws())
        _value, steps, _u = O.simulate_end_to_end(
            mind,
            body,
            P.PLANS["plus_3_waits"],
            P.HORIZON,
            budget)
        self.assertEqual(steps, 4)
        self.assertEqual(budget.work.simulated_steps, 4 + 255)

    def test_full_frozen_grid_records_gate_without_runtime_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "oracle.json"
            report = O.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(report["cases"], 486)
        self.assertEqual(
            report["direct_projection_units"],
            {
                "min": 255,
                "mean": 255.0,
                "max": 255,
                "expected": 255,
                "pass": True,
            })
        self.assertIn(
            report["classification"],
            (
                "END_TO_END_HIGH_PRECISION_ORACLE_AUTHORIZED_FOR_FUTURE_CANDIDATES",
                "END_TO_END_HIGH_PRECISION_ORACLE_REJECTED",
            ))
        self.assertFalse(report["historical_gates_changed"])
        self.assertFalse(report["candidate_promoted"])
        self.assertFalse(report["omega_rerun_authorized"])
        print(
            "END_TO_END_NUMERIC_ORACLE",
            json.dumps({
                "classification": report["classification"],
                "invariant":
                    report[
                        "oracle_projection_equivalent_invariant_max_gap"],
                "boundary": report["boundary_witness"],
                "units": report["direct_projection_units"],
                "comparisons": report["comparisons"],
                "gate": report["gate"],
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
            "import i3.lab.projection_end_to_end_numeric_oracle; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
