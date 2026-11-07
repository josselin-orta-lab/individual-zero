"""Candidate F rerun of the frozen Stage-1 omega software falsifier."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_omega_candidate_f_falsifier as F
from i3.lab import stage1_omega_falsifier as W


class CandidateFOmegaFalsifierTests(unittest.TestCase):
    def test_candidate_configuration_is_exact(self):
        mind = F.make_candidate_f_mind()
        self.assertEqual(mind.simulation_mode, "candidate_f")
        self.assertEqual(
            mind.projection_accounting,
            "event_local_quadratic4")

    def test_grid_and_omega_arms_are_the_historical_frozen_ones(self):
        self.assertEqual(
            W.OMEGAS, (-1.0, -0.5, 0.0, 0.25, 0.5, 1.0))
        self.assertEqual(len(tuple(W.grid())), 80)

    def test_full_frozen_candidate_f_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "omega-f.json"
            report = F.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertTrue(
            report["rules"][
                "R0F_all_80_states_evaluated_each_arm"])
        self.assertTrue(
            report["rules"][
                "R1F_common_ceiling_and_actual_work_covered"])
        self.assertIn(
            report["verdict"],
            (
                "CAPACITY_SHOWN_WITH_CANDIDATE_F",
                "NO_CAPACITY_THROUGH_CANDIDATE_F",
            ))
        self.assertFalse(report["reference_adoption_authorized"])
        self.assertFalse(report["survival_claim_authorized"])
        print(
            "OMEGA_CANDIDATE_F_FALSIFIER",
            json.dumps({
                "summary": report["summary"],
                "newly_positive":
                    report[
                        "states_newly_positive_vs_omega0"],
                "cost": report["cost_diagnostics"],
                "rules": report["rules"],
                "verdict": report["verdict"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_candidate_f_falsifier; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
