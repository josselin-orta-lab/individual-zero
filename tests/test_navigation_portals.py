"""Synthetic tests for current navigation links; never runs science."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("check_navigation_portals",
    Path(__file__).resolve().parents[1] / "tools/check_navigation_portals.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class PortalTests(unittest.TestCase):
    def test_healthy_link_and_ignored_fenced_examples(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = root / "docs/research/studies/README.md"
            p.parent.mkdir(parents=True)
            (p.parent / "good.md").write_text("# Good\n")
            p.write_text("[good](good.md)\n```md\n[example](absent.md)\n```\n")
            report = mod.audit(root, ("docs/research/studies/README.md",))
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["local_links_checked"], 1)
            self.assertEqual(report["scientific_verdict"], "NOT_EVALUATED")

    def test_stage_indexes_are_navigation_only_and_links_are_valid(self):
        root = Path(__file__).resolve().parents[1]
        result = mod.audit(root)
        self.assertEqual(result["status"], "PASS", result["problems"])
        self.assertGreater(result["local_links_checked"], 0)

    def test_missing_link_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = root / "tests/research/README.md"
            p.parent.mkdir(parents=True)
            original = "[bad](absent.md)\n"
            p.write_text(original)
            report = mod.audit(root, ("tests/research/README.md",))
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["problems"]), 1)
            self.assertEqual(p.read_text(), original)


if __name__ == "__main__":
    unittest.main()
