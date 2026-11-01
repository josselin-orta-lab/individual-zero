"""Read-only research document catalog contracts: no engine or study execution."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_location_index", ROOT / "tools/research_location_index.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ResearchLocationCatalogTests(unittest.TestCase):
    def test_filename_hints_are_not_scientific_status(self):
        self.assertEqual(module.classify("stage12-abc-results.md")["family"], "stage-12")
        self.assertEqual(module.classify("I1_ECO_A1C_PREREGISTRATION.md")["family"], "i1")
        self.assertEqual(module.classify("stage11-audit.md")["filename_hint"], "audit-hint")

    def test_original_paths_and_git_blobs_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            base = root / "docs/research"
            base.mkdir(parents=True)
            first = base / "stage12-case-results.md"
            first.write_bytes(b"# Original evidence\n")
            (base / "i1-prereg.md").write_bytes(b"# Preregistration\n")
            index = module.catalog(root)
            self.assertEqual(index["status"], "PATH_INVENTORY_ONLY")
            self.assertEqual(index["scientific_verdict"], "NOT_EVALUATED")
            self.assertEqual(index["families"], {"i1": 1, "stage-12": 1})
            self.assertEqual(index["documents"][-1]["blob_sha"],
                             module.blob_sha(first.read_bytes()))
            self.assertEqual(index["documents"][-1]["path"],
                             "docs/research/stage12-case-results.md")

    def test_symlinked_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            base = root / "docs/research"
            base.mkdir(parents=True)
            source = root / "outside.md"
            source.write_text("fake", encoding="utf-8")
            (base / "stage9-foreign.md").symlink_to(source)
            with self.assertRaisesRegex(ValueError, "unsafe"):
                module.catalog(root)


if __name__ == "__main__":
    unittest.main()
