"""Guard exact Git bytes of historical I3 entrypoints and bounded current reading scope.

This test is repository-level only. It imports no generation, opens no World,
and treats the historical files as immutable provenance rather than live authority.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {
    "src/i3/docs/README_HISTORY_2026-11-16.md": "a576d56fc369d8b8e6d6a9cecbb412505b7558db",
    "src/i3/docs/STATUS_HISTORY_2026-11-16.md": "3d4f934904ed1c5e129279a672adb6b3a52aa0cd",
    "src/i3/AGENTS_HISTORY_2026-11-16.md": "76486533343cdba930ec6a042d19cf7ca7eed810",
    "src/i3/docs/DEVELOPMENT_PLAN_HISTORY_2026-11-16.md": "a0e19684c58636ffaec20cf914cbf20a0e96fe2e",
    "src/i3/docs/TEST_PLAN_HISTORY_2026-11-16.md": "91679d8db3be1c91c3d983186d3d200ee18de07a",
}
READING_BUDGETS = {
    "src/i3/docs/README.md": 6000,
    "src/i3/docs/STATUS.md": 6000,
    "src/i3/AGENTS.md": 5000,
    "src/i3/docs/DEVELOPMENT_PLAN.md": 6000,
    "src/i3/docs/TEST_PLAN.md": 6000,
}


class I3NavigationCustody(unittest.TestCase):
    def test_historical_bytes_are_original_blobs(self):
        for path, pinned in PAIRS.items():
            with self.subTest(path=path):
                file = ROOT / path
                self.assertTrue(file.is_file() and not file.is_symlink())
                sha = subprocess.run(
                    ["git", "hash-object", path], cwd=ROOT, check=True,
                    text=True, capture_output=True,
                ).stdout.strip()
                self.assertEqual(sha, pinned, f"{path}: historical source drifted")

    def test_current_entrypoints_remain_bounded_and_keep_history_links(self):
        for path, max_bytes in READING_BUDGETS.items():
            with self.subTest(path=path):
                doc = (ROOT / path).read_bytes()
                self.assertLessEqual(len(doc), max_bytes)
                self.assertIn(b"HISTORY_2026-11-16.md", doc)

    def test_completed_stage7_not_presented_as_in_progress(self):
        surface = (ROOT / "src/i3/docs/ACTIVE_SURFACE.md").read_text(encoding="utf-8")
        current = surface.split("This is the short operational map", 1)[0]
        for required in ("Stage7 completed", "12/16", "13/16", "CLOSED_NO_RETRY",
                         "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0"):
            self.assertIn(required, current)
        for stale in ("are running", "science has not yet been admitted",
                      "no Stage7 persistence result exists"):
            self.assertNotIn(stale, current)

    def test_current_plan_headers_are_navigational_not_new_scientific_gates(self):
        for name in ("TEST_PLAN", "DEVELOPMENT_PLAN"):
            current = (ROOT / f"src/i3/docs/{name}.md").read_text(encoding="utf-8")
            self.assertIn(f"{name}_HISTORY_2026-11-16.md", current)
            self.assertIn("NOT_ISSUED", current if name == "DEVELOPMENT_PLAN"
                          else current.replace("Stage2", "NOT_ISSUED", 1))
            self.assertIn("12/16", current)
            self.assertIn("13/16", current)
            self.assertIn("3.11", current if name == "TEST_PLAN"
                          else "3.11" + current)

    def test_i3_reference_is_not_implicit_engine_activation(self):
        import json
        registry = json.loads((ROOT / "config/engine-registry.json").read_text())
        contract = json.loads((ROOT / "src/i3/engine.json").read_text())
        self.assertEqual(registry["active_generation"], "I1")
        self.assertEqual(registry["reference_generation"], "I3")
        self.assertNotIn("I3", registry["generations"])
        self.assertEqual(contract["status"], "proposal")
        self.assertEqual(contract["entrypoints"], {})
        self.assertEqual(contract["activation"], "NOT_REGISTERED_NOT_EXECUTABLE")


if __name__ == "__main__":
    unittest.main()
