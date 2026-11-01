"""Pure structural routing tests; do not instantiate any living engine."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_layout", ROOT / "tools/repository_layout.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class RepositoryLayoutTests(unittest.TestCase):
    @staticmethod
    def _seed_research_baseline(root):
        research = root / "docs/research"
        research.mkdir(parents=True, exist_ok=True)
        (research / "README.md").write_text("Historical index")
        manifest = root / module.HISTORICAL_RESEARCH_MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("# Historical root\n- `README.md`\n")


    def test_ga08_archive_custody_detects_mutation_and_unindexed_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / module.GA08_ARCHIVE
            source = archive / "tests"
            source.mkdir(parents=True)
            entries = []
            for index in range(12):
                rel = f"tests/fixture_{index}.py"
                raw = f"old fixture {index}\n".encode()
                (archive / rel).write_bytes(raw)
                digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                entries.append(f"| [`{rel}`]({rel}) | `{digest}` |")
            (archive / "README.md").write_text("\n".join(entries) + "\n", encoding="utf-8")
            self.assertEqual(module.check_ga08_archive_custody(root), [])
            (archive / "tests/fixture_0.py").write_text("changed")
            self.assertTrue(any("blob mismatch" in e for e in module.check_ga08_archive_custody(root)))
            (archive / "tests/fixture_0.py").unlink()
            self.assertTrue(any("missing GA08" in e for e in module.check_ga08_archive_custody(root)))
            (archive / "tests/unindexed.py").write_text("added")
            self.assertTrue(any("unindexed GA08" in e for e in module.check_ga08_archive_custody(root)))
            (archive / "tests/unindexed.py").unlink()
            (archive / "tests/fixture_0.py").write_text("old fixture 0\n")
            index_file = archive / "README.md"
            index_file.write_text(index_file.read_text().replace(
                "](tests/fixture_0.py)", "](tests/renamed.py)", 1))
            self.assertTrue(any("unsafe GA08" in e for e in module.check_ga08_archive_custody(root)))

    def test_generation_owned_routes_and_nonpromotion(self):
        self.assertEqual(module.bucket("tests", "tests/i1/test_memory.py"), "i1")
        self.assertEqual(module.bucket("tests", "tests/i2/test_fixture.py"), "i2")
        self.assertEqual(module.LEGACY_ROOT_GENERATION_TESTS, frozenset())
        self.assertEqual(module.bucket("tests", "tests/research/a1p/test_replay.py"), "a1p-tooling")
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

    def test_deprecated_embedded_research_test_location_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in module.ENTRYPOINTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("# Fixture\n", encoding="utf-8")
            self._seed_research_baseline(root)
            self.assertEqual(module.check(root)["status"], "PASS")
            obsolete = root / "tools/research/tests/test_backslide.py"
            obsolete.parent.mkdir(parents=True)
            obsolete.write_text("# Fixture\n", encoding="utf-8")
            self.assertEqual(module.check(root)["status"], "FAIL")
            obsolete.unlink()
            self._seed_research_baseline(root)
            self.assertEqual(module.check(root)["status"], "PASS")

    def test_historical_research_root_cannot_grow_or_silently_shrink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = root / module.HISTORICAL_RESEARCH_MANIFEST
            manifest.parent.mkdir(parents=True)
            manifest.write_text("# Historical paths\n- `README.md`\n- `stage12-old.md`\n")
            research = root / "docs/research"
            research.mkdir(parents=True, exist_ok=True)
            (research / "README.md").write_text("Index")
            (research / "stage12-old.md").write_text("Original")
            self.assertEqual(module.check_research_root_placement(root), [])
            extra = research / "stage12-new.md"
            extra.write_text("New")
            self.assertIn("new root-level", module.check_research_root_placement(root)[0])
            extra.unlink()
            (research / "stage12-old.md").unlink()
            self.assertIn("historical research path missing",
                          module.check_research_root_placement(root)[0])

    def test_new_root_generation_test_is_rejected_without_renaming_legacy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in module.ENTRYPOINTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("# Fixture\n", encoding="utf-8")
            tests = root / "tests"
            (tests / "test_repo_navigation.py").write_text("# Existing infrastructure\n")
            self._seed_research_baseline(root)
            self.assertEqual(module.check(root)["status"], "PASS")
            (tests / "test_i2_unscoped.py").write_text("# New\n")
            outcome = module.check(root)
            self.assertEqual(outcome["status"], "FAIL")
            self.assertIn("tests/iN/", outcome["errors"][0])


if __name__ == "__main__":
    unittest.main()
