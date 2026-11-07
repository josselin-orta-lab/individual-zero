"""Candidate-F post-contact guard for the owner-approved omega hypothesis."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_omega_post_contact_candidate_f_guard as G

SRC = Path(__file__).resolve().parents[2] / "src" / "i3" / "modules"


class OmegaPostContactCandidateFGuardTests(unittest.TestCase):
    def test_full_frozen_guard(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "guard.json"
            report = G.run(path)
            self.assertEqual(json.loads(path.read_text()), report)

        self.assertEqual(
            report["verdict"],
            "POST_CONTACT_PERSONAL_HISTORY_OVERRIDES_INNATE_EXPECTATION")
        self.assertTrue(report["gate"]["mixed_safe_repeat_toxic_stop"])
        self.assertTrue(report["gate"]["uniformly_harmful_stops"])
        self.assertTrue(
            report["gate"]["actual_work_within_forecast_ceiling"])
        self.assertFalse(report["gate"]["personal_path_reads_omega"])
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["genome_change_authorized_by_this_report"])
        print(
            "OMEGA_POST_CONTACT_CANDIDATE_F_GUARD",
            json.dumps({
                "mixed": report["grid"]["mixed"],
                "harmful": report["grid"]["harmful"],
                "gate": report["gate"],
                "verdict": report["verdict"],
            }, sort_keys=True))

    def test_personal_post_contact_modules_do_not_read_omega(self):
        for name in (
                "carried_food_information.py",
                "reference_branches.py",
                "personal_outcomes.py",
                "observed_effect_view.py"):
            self.assertNotIn(
                "omega", (SRC / name).read_text(), name)

    def test_candidate_is_exact_integrated_f_mode(self):
        mind = G.make_candidate(G.MIXED)
        self.assertEqual(mind.simulation_mode, "candidate_f")
        self.assertEqual(
            mind.projection_accounting, "event_local_quadratic4")

    def test_import_does_not_load_world_or_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_post_contact_candidate_f_guard; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
