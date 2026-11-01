"""Pure structural routing tests; do not instantiate any living engine."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_layout", ROOT / "tools/repository_layout.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class RepositoryLayoutTests(unittest.TestCase):
    def test_generation_owned_routes_and_nonpromotion(self):
        self.assertEqual(module.bucket("tests", "tests/i1/test_memory.py"), "i1")
        self.assertEqual(module.bucket("tests", "tests/i2/test_fixture.py"), "i2")
        self.assertEqual(module.bucket("tests", "archive/i0/tests/test_historical.py"), "i0-frozen")
        self.assertEqual(module.bucket("docs", "src/i2/docs/STATUS.md"), "i2-owned")
        self.assertEqual(module.bucket("docs", "docs/research/studies/README.md"), "research-studies")
        self.assertEqual(module.bucket("archives", "docs/research/archive/old.md"), "research-historical")
        self.assertIsNone(module.bucket("tests", "docs/experiments-vs-tests.md"))

    def test_inventory_filter_and_audit_are_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in ("docs/research/stage12-one.md", "docs/research/stage9-two.md",
                         "archive/i0/tests/test_history.py", "tests/i1/test_memory.py",
                         "tools/research/tests/test_review.py"):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("fixture\n", encoding="utf-8")
            result = module.inventory(root, kind="docs", match="stage12", limit=1)
            self.assertEqual(result["matched"], 1)
            self.assertEqual(result["paths"][0]["path"], "docs/research/stage12-one.md")
            snapshot = module.audit(root)
            self.assertEqual(snapshot["research_documents_at_directory_root"], 2)
            self.assertEqual(snapshot["frozen_i0_files"], 1)
            self.assertEqual(snapshot["embedded_tool_tests"], 1)
            self.assertEqual(snapshot["scientific_verdict"], "NOT_EVALUATED")

    def test_new_root_generation_test_is_rejected_without_renaming_legacy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in module.ENTRYPOINTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("# Fixture\n", encoding="utf-8")
            tests = root / "tests"
            (tests / "test_i1_active_birth.py").write_text("# Existing\n")
            self.assertEqual(module.check(root)["status"], "PASS")
            (tests / "test_i2_unscoped.py").write_text("# New\n")
            outcome = module.check(root)
            self.assertEqual(outcome["status"], "FAIL")
            self.assertIn("tests/iN/", outcome["errors"][0])


if __name__ == "__main__":
    unittest.main()
