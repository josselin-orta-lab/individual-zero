"""Stage-1 Candidate F common forecast-cost ceiling."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.lab import stage1_candidate_f_forecast_ceiling as C
from i3.modules.forecast_work import projection_simulated_steps_ceiling
from i3.modules.genome import midpoint
from i3.modules.mind import Mind


class CandidateFForecastCeilingTests(unittest.TestCase):
    def test_reference_and_trapezoid_quotes_are_unchanged(self):
        mind = P.make_mind(midpoint())
        self.assertEqual(projection_simulated_steps_ceiling(mind), 8)
        mind.projection_accounting = "trapezoid"
        self.assertEqual(projection_simulated_steps_ceiling(mind), 8)

    def test_local_quadratic_quote_is_structural_horizon_bound(self):
        mind = P.make_mind(midpoint())
        mind.projection_accounting = "event_local_quadratic4"
        self.assertEqual(
            projection_simulated_steps_ceiling(mind),
            1 + sum(mind.proj_chunks))
        self.assertEqual(projection_simulated_steps_ceiling(mind), 256)

    def test_candidate_f_requires_local_quadratic_quote(self):
        mind = Mind(midpoint(), 97, simulation_mode="candidate_f")
        with self.assertRaises(ValueError):
            projection_simulated_steps_ceiling(mind)
        mind.projection_accounting = "event_local_quadratic4"
        self.assertEqual(projection_simulated_steps_ceiling(mind), 256)

    def test_rejected_dynamic_modes_fail_closed(self):
        for mode in ("event_quadratic", "event_quartic"):
            mind = P.make_mind(midpoint())
            mind.projection_accounting = mode
            with self.assertRaises(ValueError):
                projection_simulated_steps_ceiling(mind)

    def test_full_frozen_forecast_ceiling_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "forecast.json"
            report = C.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertEqual(
            report["verdict"],
            "CANDIDATE_F_FORECAST_CEILING_PASS")
        self.assertEqual(report["reference_projection_quote"], 8)
        self.assertEqual(report["candidate_f_projection_quote"], 256)
        self.assertLessEqual(
            report["candidate_f_direct_actual"]["max"], 256)
        self.assertTrue(
            report["omega_zero_kernel"][
                "all_actual_work_within_ceiling"])
        self.assertGreater(
            report["omega_zero_kernel"]["evaluated"], 0)
        self.assertTrue(report["omega_rerun_authorized"])
        self.assertFalse(report["reference_adoption_authorized"])
        print(
            "CANDIDATE_F_FORECAST_CEILING",
            json.dumps({
                "reference_quote":
                    report["reference_projection_quote"],
                "candidate_quote":
                    report["candidate_f_projection_quote"],
                "direct_actual":
                    report["candidate_f_direct_actual"],
                "omega_zero": {
                    key: report["omega_zero_kernel"][key]
                    for key in (
                        "cases", "evaluated", "unfunded",
                        "all_actual_work_within_ceiling",
                        "max_actual_simulated_steps",
                        "max_forecast_ceiling_simulated_steps")
                },
                "gate": report["gate"],
                "verdict": report["verdict"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_f_forecast_ceiling; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
