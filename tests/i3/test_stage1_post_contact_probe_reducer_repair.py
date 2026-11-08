"""Frozen post-contact Candidate-H probe reducer repair tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_post_contact_probe_reducer_repair as G


class PostContactProbeReducerRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = G.characterize()

    def test_q0_q9_gate_passes_without_live_or_evidence_authority(self):
        self.assertEqual(
            self.report["verdict"],
            "POST_CONTACT_PROBE_REDUCER_REPAIR_PASS")
        self.assertTrue(all(self.report["rules"].values()))
        self.assertFalse(self.report["world_access"])
        self.assertFalse(self.report["runtime_life_access"])
        self.assertFalse(self.report["p2_ecology_access"])
        self.assertFalse(self.report["evidence_branch_access"])
        self.assertEqual(self.report["lives"], 0)
        self.assertFalse(self.report["66_67_retry_authorized"])
        self.assertFalse(
            self.report["retroactive_66_67_admission_authorized"])
        self.assertFalse(self.report["J1_J7_verdict_authorized"])
        self.assertFalse(self.report["new_live_panel_authorized"])

    def test_exact_legacy_failure_is_preserved_as_reproducer(self):
        self.assertEqual(
            self.report["legacy_reproduction"],
            {
                "type": "ValueError",
                "message":
                    "invalid Candidate-I post-contact processing receipt",
            })

    def test_declared_post_contact_and_direct_h_shapes_are_accepted(self):
        self.assertTrue(all(self.report["accepted"].values()))
        self.assertEqual(
            self.report["prerequisites"]["composite"],
            "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS")
        self.assertEqual(
            self.report["prerequisites"]["multiphase"],
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS")
        self.assertEqual(
            self.report["prerequisites"]["lifecycle_v2"],
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS")

    def test_all_adversarial_receipts_fail_closed(self):
        self.assertTrue(all(self.report["invalid_rejections"].values()))

    def test_run_serializes_same_verdict(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertEqual(report["verdict"], self.report["verdict"])
        self.assertEqual(report["rules"], self.report["rules"])

    def test_import_does_not_load_world_life_or_p2(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_post_contact_probe_reducer_repair; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.worldgen' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
