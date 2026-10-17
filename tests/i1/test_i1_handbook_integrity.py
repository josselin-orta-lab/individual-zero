"""Negative gates for I1 documentation integrity, without runtime imports."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("check_i1_handbook", ROOT / "scripts/check_i1_handbook.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class HandbookIntegrityTests(unittest.TestCase):
    def test_repository_documents_are_valid(self):
        report = check.inspect(ROOT)
        self.assertEqual(report["status"], "PASS", report["errors"])
        self.assertEqual(report["scientific_gate"], "NOT_EVALUATED")

    def test_broken_internal_link_and_source_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT / "src/i1/docs", root / "src/i1/docs")
            (root / "src/i1/engine.json").write_text(
                (ROOT / "src/i1/engine.json").read_text())
            (root / "config").mkdir()
            (root / "config/engine-registry.json").write_text(
                (ROOT / "config/engine-registry.json").read_text())
            p = root / "src/i1/docs/README.md"
            p.write_text(p.read_text() + "\n[invalid](NO-SUCH-DOC.md)\n")
            report = check.inspect(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("broken link NO-SUCH-DOC.md" in e for e in report["errors"]))
            self.assertTrue(any("missing source path" in e for e in report["errors"]))

    def test_missing_python_symbol_is_rejected_without_importing_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT / "src/i1/docs", root / "src/i1/docs")
            (root / "src/i1/engine.json").write_text(
                (ROOT / "src/i1/engine.json").read_text())
            (root / "config").mkdir()
            (root / "config/engine-registry.json").write_text(
                (ROOT / "config/engine-registry.json").read_text())
            source = root / "src/i1/modules"
            source.mkdir(parents=True)
            (source / "sample.py").write_text(
                "class Sample:\n    def existing(self):\n        pass\n")
            doc = root / "src/i1/docs/README.md"
            doc.write_text(doc.read_text() + "\n`src/i1/modules/sample.py::Sample.missing`\n")
            report = check.inspect(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("missing Python symbol" in e and "Sample.missing" in e
                                for e in report["errors"]), report["errors"])

    def test_registry_mismatch_and_missing_index_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT / "src/i1/docs", root / "src/i1/docs")
            (root / "src/i1/engine.json").write_text(
                (ROOT / "src/i1/engine.json").read_text())
            (root / "config").mkdir()
            (root / "config/engine-registry.json").write_text(
                '{"active_generation": "I0"}')
            (root / "src/i1/docs/UC_AND_SCHEDULING.md").unlink()
            report = check.inspect(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("active generation" in e for e in report["errors"]))
            self.assertTrue(any("missing canonical document" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
