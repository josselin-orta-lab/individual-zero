"""Post-hoc audit of Candidate-F observed-effect proxy dispatch."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_f_observed_effect_dispatch_audit as A


class CandidateFObservedEffectDispatchAuditTests(unittest.TestCase):
    def test_reference_separates_candidate_f_collapses_before_fix(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "dispatch-audit.json"
            report = A.run(path)
            loaded = json.loads(path.read_text())

        self.assertEqual(loaded, report)
        self.assertTrue(report["reference_separates_observed_effects"])
        self.assertTrue(report["candidate_f_collapses_observed_effects"])
        self.assertEqual(
            report["classification"],
            "OBSERVED_EFFECT_VIEW_BYPASSED_BY_CANDIDATE_F_DISPATCH")
        self.assertFalse(report["first_omega_rerun_measurement_valid"])
        self.assertFalse(report["scientific_no_capacity_claim_authorized"])
        print(
            "CANDIDATE_F_OBSERVED_EFFECT_DISPATCH_AUDIT",
            json.dumps({
                "reference": report["reference"],
                "candidate_f": report["candidate_f"],
                "classification": report["classification"],
                "measurement_valid":
                    report["first_omega_rerun_measurement_valid"],
            }, sort_keys=True))

    def test_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_candidate_f_observed_effect_dispatch_audit; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
