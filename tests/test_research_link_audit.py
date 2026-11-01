"""Pure synthetic tests for research local-link triage."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("research_link_audit", ROOT / "tools/research_link_audit.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ResearchLinkAuditTests(unittest.TestCase):
    def test_detects_missing_and_preserves_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            base = root / "docs/research"
            base.mkdir(parents=True)
            (base / "present.md").write_text("# present\n")
            source = base / "stage12-record.md"
            original = ("[good](present.md) [bad](missing.md) [web](https://example.org/a)\n"
                        "```md\n[code](missing-in-example.md)\n```\n")
            source.write_text(original)
            report = module.audit(root)
            self.assertEqual(report["links_examined"], 2)
            self.assertEqual(report["total_issues"] if "total_issues" in report else len(report["issues"]), 1)
            self.assertEqual(report["issues"][0]["status"], "REVIEW_MISSING_LOCAL_TARGET")
            self.assertEqual(source.read_text(), original)
            self.assertEqual(report["scientific_verdict"], "NOT_EVALUATED")

    def test_outside_repository_is_review_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "docs/research/example.md"
            source.parent.mkdir(parents=True)
            result = module.check_link(root, source, "../../../outside.md")
            self.assertEqual(result["status"], "REVIEW_PATH_ESCAPES_REPOSITORY")

    def test_no_false_external_or_anchor_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "docs/research/example.md"
            self.assertIsNone(module.check_link(root, source, "#anchor"))
            self.assertIsNone(module.check_link(root, source, "https://example.com"))
            self.assertIsNone(module.check_link(root, source, "mailto:a@example.com"))


if __name__ == "__main__":
    unittest.main()
