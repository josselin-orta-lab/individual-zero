"""Candidate-G reference-recurrence falsifier; no World or I3 life."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G


class CandidateGReferenceRecurrenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = G.characterize()

    def test_fixed_grid_and_reference_architecture(self):
        r = self.result
        self.assertEqual(r["lives"], 0)
        self.assertFalse(r["world_access"])
        self.assertEqual(r["simulation_mode"], "reference")
        self.assertEqual(r["projection_accounting"], "chunk_end")
        self.assertFalse(r["omega_read"])
        self.assertEqual(r["summary"]["evaluated"], 80)
        self.assertEqual(
            r["summary"]["future_probabilities"],
            [1. / 3., 2. / 3., 1.0])

    def test_personal_recurrence_and_cost_invariants_are_hard_requirements(self):
        rules = self.result["rules"]
        self.assertTrue(rules["R0_exact_80_states"])
        self.assertTrue(rules["R1_reference_projection_only"])
        self.assertTrue(rules["R2_personal_recurrence_only"])
        self.assertTrue(rules["R3_actual_work_within_common_ceiling"])

    def test_behavioral_gate_is_reported_not_engineered(self):
        print("CANDIDATE_G_REFERENCE_RECURRENCE " + json.dumps(
            self.result, sort_keys=True))
        rules = self.result["rules"]
        expected = (
            "CANDIDATE_G_REFERENCE_RECURRENCE_SOFTWARE_GATE_PASS"
            if all(rules.values()) else
            "CANDIDATE_G_REFERENCE_RECURRENCE_SOFTWARE_GATE_FAIL")
        self.assertEqual(self.result["verdict"], expected)
        self.assertEqual(
            self.result["summary"]["selected_epistemic"],
            len(self.result["selected_states"]))
        self.assertEqual(
            self.result["summary"]["declined"],
            len(self.result["declined_states"]))

    def test_selected_state_rows_are_fully_auditable(self):
        for row in self.result["selected_states"]:
            self.assertIn(row["channel"], G.CHANNEL_NAMES)
            self.assertIn(row["level"], G.LEVELS)
            self.assertIn(row["horizon"], G.HORIZONS)
            self.assertGreater(row["information_value"], 1e-12)
            self.assertIn("TRIAL", row["target_choices"])
            self.assertEqual(
                row["source"], "PAID_PERSONAL_ONSET_RECURRENCE")
            for key, value in row["work"].items():
                self.assertLessEqual(
                    value, row["forecast_work_ceiling"][key])

    def test_lab_import_does_not_load_runtime_or_create_a_life(self):
        # Mind itself imports world.DIRECTIONS as an architectural constant, so
        # requiring the world module to be absent would be a false isolation
        # claim. The falsifier must still remain detached from runtime/life.
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_g_reference_recurrence_falsifier as g; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert g.SCHEMA.endswith('/v1')"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
