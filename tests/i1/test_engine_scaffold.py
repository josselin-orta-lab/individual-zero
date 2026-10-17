"""No implicit registration, accidental overwrites or copied parent runtime."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from new_engine import plan


class EngineScaffoldingTests(unittest.TestCase):
    def test_preview_does_not_create_files(self):
        with TemporaryDirectory() as temp:
            target = Path(temp) / "I2"
            files = plan("I2", "I1", target)
            self.assertFalse(target.exists())
            self.assertIn("lab/__init__.py", files)
            self.assertIn("runtime/__init__.py", files)
            self.assertEqual(json.loads(files["engine.json"])["status"], "proposal")
            self.assertNotIn("i1lab", "".join(files.values()).lower())

    def test_cannot_override_parent_or_existing_generation(self):
        with TemporaryDirectory() as temp:
            out = Path(temp) / "I2"
            for g, parent in (("I1", "I0"), ("I2", "I2"), ("I2", "I42"),
                              ("I0", "I1"), ("I3", "I2")):
                with self.subTest(g=g, parent=parent), self.assertRaises(ValueError):
                    plan(g, parent, out)
            out.mkdir()
            with self.assertRaises(FileExistsError):
                plan("I2", "I1", out)

    def test_proposal_has_no_born_runtime_or_scientific_go(self):
        with TemporaryDirectory() as temp:
            files = plan("I2", "I1", Path(temp) / "I2")
            c = json.loads(files["engine.json"])
            self.assertEqual(c["activation"], "NOT_REGISTERED_NOT_EXECUTABLE")
            self.assertFalse(c["entrypoints"])
            self.assertEqual(c["scientific"]["gate"], "not_established")
            self.assertFalse(c["constraints"]["live_state_rollback"])


if __name__ == "__main__":
    unittest.main()
