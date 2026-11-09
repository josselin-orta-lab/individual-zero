"""Frozen composite-funding reducer repair tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.archive.stage1.lab import stage1_composite_funding_reducer_repair as G


class CompositeFundingReducerRepairTests(unittest.TestCase):
    def test_frozen_gate_passes_without_world_or_evidence(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = G.run(fh.name)
        self.assertEqual(
            report["verdict"],
            "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS")
        self.assertTrue(all(report["rules"].values()))
        self.assertTrue(all(report["legacy_reproduction"].values()))
        self.assertTrue(all(report["invalid_rejections"].values()))
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["evidence_branch_access"])
        self.assertFalse(report["retroactive_58_59_completion_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])

    def test_legacy_predicate_rejects_both_declared_composite_fixtures(self):
        no_processing = G._set_decision(
            G._life(),
            public="NO_FUNDED_RELEVANCE_PROBE",
            nested="NO_PROCESSING_BUDGET",
            outcome="no_processing_budget",
            work=G.ZERO,
            action=None)
        no_score = G._set_decision(
            G._life(),
            public="NO_FUNDED_RELEVANCE_PROBE",
            nested="NO_FUNDED_SCORE",
            outcome="no_funded_score",
            work=G.WORK,
            action=None)
        self.assertTrue(G._legacy_rejects(no_processing))
        self.assertTrue(G._legacy_rejects(no_score))

    def test_import_does_not_load_world_runtime_or_evidence_helpers(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.archive.stage1.lab.stage1_composite_funding_reducer_repair; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.worldgen' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
