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
}
READING_BUDGETS = {
    "src/i3/docs/README.md": 6000,
    "src/i3/docs/STATUS.md": 6000,
    "src/i3/AGENTS.md": 5000,
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
