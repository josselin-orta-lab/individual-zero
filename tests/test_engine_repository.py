"""Registry invariants independent of the cognitive actor's behavior."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineToolingTests(unittest.TestCase):
    def test_registry_and_original_archive_are_consistent(self):
        proc = subprocess.run([sys.executable, "scripts/check_engine_repository.py", "--json"],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["active_generation"], "I1")
        self.assertEqual(report["archived"], {"workflows": 127, "tests": 297})

    def test_original_engine_sources_are_present(self):
        for name in ("i0", "i1", "lab", "i1/runtime"):
            self.assertTrue((ROOT / "src" / name).is_dir(), name)


if __name__ == "__main__":
    unittest.main()
