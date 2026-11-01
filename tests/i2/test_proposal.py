"""Static-only I2 proposal checks; never instantiate a living engine."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.assess_engine_proposal import _source_imports_other_generation, inspect_proposal
from tools.new_engine import plan as preview_generation
ROOT=Path(__file__).resolve().parents[2]
class TestI2Proposal(unittest.TestCase):
    def test_not_registered_or_executable(self):
        c=json.loads((ROOT/"src/i2/engine.json").read_text())
        r=json.loads((ROOT/"config/engine-registry.json").read_text())
        self.assertEqual(c["generation"],"I2")
        self.assertEqual(c["status"],"proposal")
        self.assertEqual(c["entrypoints"],{})
        self.assertEqual(c["publication_owners"],[])
        self.assertEqual(c["activation"],"NOT_REGISTERED_NOT_EXECUTABLE")
        self.assertNotIn("I2",r["generations"])
        self.assertEqual(r["active_generation"],"I1")
        self.assertEqual(c["scientific"]["gate"],"not_established")


    def test_inert_i2_still_blocked_and_no_foreign_code(self):
        report = inspect_proposal("I2", root=ROOT)
        self.assertEqual(report["status"], "STRUCTURE_PRESENT_REVIEW_REQUIRED")
        self.assertEqual(set(report["blocked_by"]),
                         set())
        self.assertTrue(report["checks"]["no_parent_runtime_imports"])
        self.assertEqual(report["activation"], "FORBIDDEN")

    def test_foreign_direct_dynamic_and_unverifiable_imports_refused(self):
        forbidden = {
            "parent": "import i1lab.i1_natural_runtime",
            "grandparent": "from i0.lab import world",
            "future": "from i3.modules import cognition",
            "qualified": "from src.i1.runtime import birth",
            "archive": "import archive.i0.lab",
            "from_root": "from src import i0",
            "from_relative": "from .. import i1lab",
            "dynamic": "import importlib as loader\nloader.import_module('i1lab.runtime')",
            "alias": "from importlib import import_module as load\nload('i0.lab')",
            "builtin": "__import__('src.i1.modules')",
            "package": "import importlib\nimportlib.import_module('.lab', package='i1')",
            "unknown": "import importlib\nimportlib.import_module(module_name)",
        }
        allowed = {
            "stdlib": "import hashlib\nfrom pathlib import Path",
            "own": "from i2.modules import cognition",
            "own_lab": "import i2lab.runtime",
            "dynamic_stdlib": "import importlib\nimportlib.import_module('json')",
            "quoted": "note = 'import i1lab.runtime'",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.py"
            for label, code in forbidden.items():
                with self.subTest(forbidden=label):
                    path.write_text(code + "\n")
                    self.assertTrue(_source_imports_other_generation(path, "I2"))
            for label, code in allowed.items():
                with self.subTest(allowed=label):
                    path.write_text(code + "\n")
                    self.assertFalse(_source_imports_other_generation(path, "I2"))

    def test_i2_test_tree_has_no_foreign_generation_imports_or_symlinks(self):
        # CI tests must not accidentally execute borrowed I0/I1 test
        # fixtures. Static AST checks are narrower than dependency audits.
        tree = ROOT / "tests" / "i2"
        self.assertTrue(tree.is_dir())
        self.assertFalse(tree.is_symlink())
        files = sorted(tree.rglob("*"))
        self.assertTrue(any(path.suffix == ".py" for path in files))
        for path in files:
            with self.subTest(path=path.relative_to(tree)):
                self.assertFalse(path.is_symlink(), "symlinked I2 test content")
                if path.is_file() and path.suffix == ".py":
                    self.assertFalse(
                        _source_imports_other_generation(path, "I2"),
                        "direct or unverifiable dynamic import from a foreign generation",
                    )

    def test_future_generation_range_includes_i10_through_i19(self):
        # Structural tool validation only: never writes or registers an engine.
        with tempfile.TemporaryDirectory() as scratch:
            for generation in ("I2", "I9", "I10", "I11", "I19", "I20", "I100"):
                with self.subTest(valid=generation):
                    output = Path(scratch) / generation.lower()
                    files = preview_generation(generation, "I1", output, root=ROOT)
                    self.assertEqual(
                        json.loads(files["engine.json"])["generation"], generation
                    )
                    self.assertFalse(output.exists())
                    audit = inspect_proposal(generation, root=ROOT)
                    self.assertEqual(audit["generation"], generation)
                    self.assertEqual(audit["status"],
                        "STRUCTURE_PRESENT_REVIEW_REQUIRED" if generation == "I2" else "BLOCKED")
                    self.assertEqual(audit["activation"], "FORBIDDEN")
            for generation in ("I0", "I1", "I01", "I02", "I010",
                               "I10beta", "i10", "I-10"):
                with self.subTest(invalid=generation):
                    with self.assertRaises(ValueError):
                        preview_generation(
                            generation, "I1", Path(scratch) / generation, root=ROOT
                        )
                    with self.assertRaises(ValueError):
                        inspect_proposal(generation, root=ROOT)

    def test_symlinked_previous_lab_is_not_an_independent_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = root / "config" / "engine-registry.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(json.dumps({
                "active_generation": "I1", "generations": {"I1": {}},
            }))
            older = root / "src" / "i1" / "lab"
            older.mkdir(parents=True)
            (older / "__init__.py").write_text("")
            engine = root / "src" / "i2"
            engine.mkdir(parents=True)
            (engine / "engine.json").write_text(
                (ROOT / "src/i2/engine.json").read_text())
            for folder in ("modules", "runtime", "config"):
                path = engine / folder
                path.mkdir()
                (path / "__init__.py").write_text("")
            (engine / "lab").symlink_to(older, target_is_directory=True)
            (engine / "docs").mkdir()
            (root / "tests" / "i2").mkdir(parents=True)
            report = inspect_proposal("I2", root=root)
            self.assertFalse(report["checks"]["isolated_lab_layout"])
            self.assertFalse(report["checks"]["no_parent_runtime_imports"])
            self.assertEqual(report["registration"], "FORBIDDEN")

