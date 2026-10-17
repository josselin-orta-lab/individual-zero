"""No implicit registration, accidental overwrites or copied parent runtime."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from new_engine import plan, plan_workspace, apply_workspace


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

    def test_workspace_has_dedicated_lab_tests_docs_and_inert_ci(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "config/engine-registry.json").write_bytes(
                (ROOT / "config/engine-registry.json").read_bytes())
            target = root / "src/i2"
            files = plan_workspace("I2", "I1", target, root=root)
            self.assertFalse(target.exists())
            self.assertIn("src/i2/lab/__init__.py", files)
            self.assertIn("tests/i2/test_proposal.py", files)
            self.assertIn("src/i2/docs/CI_WORKFLOW_TEMPLATE.yml", files)
            self.assertFalse((root / ".github/workflows").exists())
            created = apply_workspace("I2", "I1", target, root=root)
            self.assertEqual(sorted(files), created)
            self.assertTrue((root / "src/i2/engine.json").exists())
            self.assertTrue((root / "tests/i2/test_proposal.py").exists())
            self.assertFalse((root / ".github/workflows").exists())
            self.assertNotIn(
                "I2", json.loads(
                    (root / "config/engine-registry.json").read_text()
                )["generations"]
            )
            with self.assertRaises(FileExistsError):
                apply_workspace("I2", "I1", target, root=root)

    def test_workspace_cannot_overwrite_existing_test_owner(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "config/engine-registry.json").write_bytes(
                (ROOT / "config/engine-registry.json").read_bytes())
            (root / "tests/i2").mkdir(parents=True)
            sentinel = root / "tests/i2/keep.txt"
            sentinel.write_text("DO NOT OVERWRITE")
            with self.assertRaises(FileExistsError):
                apply_workspace("I2", "I1", root / "src/i2", root=root)
            self.assertEqual(sentinel.read_text(), "DO NOT OVERWRITE")
            self.assertFalse((root / "src/i2").exists())

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
