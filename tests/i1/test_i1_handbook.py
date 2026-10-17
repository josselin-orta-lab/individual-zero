"""Verify that canonical I1 handbook is co-located with its engine."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "src/i1/docs"
REQUIRED = ("README.md", "THEORY.md", "COGNITIVE_FLOW.md",
            "EVIDENCE_MATRIX.md", "DEVELOPMENT_PLAYBOOK.md",
            "OBSERVABILITY.md", "ARCHITECTURE.md", "STATUS.md",
            "TEST_PLAN.md", "WORLD_PRESETS.md",
            "NEEDS_AND_ACTION.md", "MEMORY_AND_LEARNING.md",
            "CONSOLIDATION_AND_PUBLICATION.md", "MORTALITY_AND_M11.md",
            "EXPERIMENT_PROTOCOL.md", "STAGES_AND_INTERFACES.md",
            "UC_AND_SCHEDULING.md", "DATA_CONTRACTS_AND_CUSTODY.md",
            "LIVED_EVIDENCE_WALKTHROUGH.md")


class I1HandbookTests(unittest.TestCase):
    def test_local_canonical_paths_and_entries(self):
        contract = json.loads((ROOT / "src/i1/engine.json").read_text())
        self.assertEqual(contract["paths"]["documentation"], "src/i1/docs")
        self.assertEqual(contract["scientific"]["evidence_index"],
                         "src/i1/docs/EVIDENCE_MATRIX.md")
        for name in REQUIRED:
            self.assertTrue((DOCS / name).is_file(), name)

    def test_handbook_reading_order_is_resolvable(self):
        start = (DOCS / "README.md").read_text()
        for name in REQUIRED:
            if name == "README.md":
                continue  # This page is the index; it need not link to itself.
            self.assertIn(name, start)

    def test_observer_keeps_absent_science_unproven(self):
        matrix = (DOCS / "EVIDENCE_MATRIX.md").read_text()
        observer = (DOCS / "OBSERVABILITY.md").read_text()
        self.assertIn("OPEN / NOT_OBSERVED", matrix)
        self.assertIn("NOT_OBSERVED", observer)
        self.assertIn("hidden", observer.lower() + matrix.lower()
                      + (DOCS / "THEORY.md").read_text().lower())


if __name__ == "__main__":
    unittest.main()
