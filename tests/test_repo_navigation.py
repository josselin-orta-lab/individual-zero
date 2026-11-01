"""Focused tests for the static navigation checker; no active engine runs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_repo_navigation",
                                             ROOT / "tools/check_repo_navigation.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class NavigationSanity(unittest.TestCase):
    def test_architecture_portal_is_required_and_not_archived(self):
        self.assertIn("docs/architecture/ATLAS.md", module.ENTRYPOINTS)
        self.assertIn("archive/README.md", module.ENTRYPOINTS)
        self.assertIn("tests/README.md", module.ENTRYPOINTS)
        self.assertFalse(module.is_historical("archive/README.md"))
        self.assertIn("docs/architecture/proposals/README.md", module.ENTRYPOINTS)
        self.assertFalse(module.is_historical("docs/architecture/proposals/README.md"))
        self.assertTrue(module.is_historical(
            "docs/architecture/proposals/i1-isolated-fork-2026-10-16.md"))

    def test_proposals_index_detects_missing_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "docs/architecture/proposals"
            folder.mkdir(parents=True)
            index = folder / "README.md"
            item = folder / "proposal-example.md"
            index.write_text("# Index\n")
            item.write_text("# Historical proposal\n")
            self.assertEqual(module.unindexed_architecture_proposals(root),
                             ["proposal-example.md"])
            index.write_text("[example](proposal-example.md)\n")
            self.assertEqual(module.unindexed_architecture_proposals(root), [])

    def test_live_entrypoints(self):
        outcome = module.inspect(ROOT)
        self.assertEqual(outcome["status"], "PASS", outcome["errors"])
        self.assertEqual(outcome["scientific_gate"], "NOT_EVALUATED")

    def test_broken_link_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for p in module.ENTRYPOINTS:
                target = root / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# Entry\n")
            for gen in ("i1", "i2"):
                (root / f"src/{gen}/docs/STATUS_HISTORY.md").write_text("# History\n")
                (root / f"src/{gen}/engine.json").write_text(
                    '{"paths": {"documentation": "src/' + gen + '/docs"}, "entrypoints": {}}')
            cfg = root / "config/engine-registry.json"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text('{"active_generation": "I1", "generations": {"I1": {}}}')
            (root / "docs/README.md").write_text("[missing](nothing.md)\n")
            outcome = module.inspect(root)
            self.assertTrue(any("broken local link" in e for e in outcome["errors"]))
            self.assertEqual(outcome["status"], "FAIL")


    def test_historical_links_are_warnings_unless_strict(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for p in module.ENTRYPOINTS:
                target = root / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# Entry\n")
            for gen in ("i1", "i2"):
                (root / f"src/{gen}/docs/STATUS_HISTORY.md").write_text("# History\n")
                (root / f"src/{gen}/engine.json").write_text(
                    '{"generation": "I' + gen[1:] +
                    '", "status": "' + ("active" if gen == "i1" else "proposal") +
                    '", "paths": {"documentation": "src/' + gen +
                    '/docs"}, "entrypoints": {}}')
            cfg = root / "config/engine-registry.json"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text('{"active_generation": "I1", "generations": {"I1": {}}}')
            (root / "docs/research").mkdir(exist_ok=True)
            (root / "docs/research/old-study.md").write_text("[old](unavailable.md)\n")
            report = module.inspect(root, scope="all")
            self.assertEqual(report["status"], "PASS", report["errors"])
            self.assertTrue(any("broken local link" in msg for msg in report["warnings"]))
            strict = module.inspect(root, scope="all", strict_historical=True)
            self.assertEqual(strict["status"], "FAIL")

    def test_fenced_examples_are_not_navigation_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for p in module.ENTRYPOINTS:
                target = root / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("# Entry\n")
            for gen in ("i1", "i2"):
                (root / f"src/{gen}/docs/STATUS_HISTORY.md").write_text("# History\n")
                (root / f"src/{gen}/engine.json").write_text(
                    '{"generation": "I' + gen[1:] +
                    '", "status": "' + ("active" if gen == "i1" else "proposal") +
                    '", "paths": {"documentation": "src/' + gen +
                    '/docs"}, "entrypoints": {}}')
            cfg = root / "config/engine-registry.json"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text('{"active_generation": "I1", "generations": {"I1": {}}}')
            ticks = chr(96) * 3
            (root / "docs/README.md").write_text(
                ticks + "md\n[fictional](missing.md)\n" + ticks + "\n")
            self.assertEqual(module.inspect(root)["status"], "PASS")


    def test_docs_only_i2_updates_use_lightweight_navigation_ci(self):
        heavy = (ROOT / ".github/workflows/i2-proposal-safety.yml").read_text(encoding="utf-8")
        light = (ROOT / ".github/workflows/agent-context-static.yml").read_text(encoding="utf-8")
        self.assertIn("'src/i2/**'", heavy)
        self.assertIn("'!src/i2/docs/**'", heavy)
        self.assertIn("'!src/i2/AGENTS.md'", heavy)
        self.assertIn("'tests/i2/**'", heavy)
        self.assertIn("'.github/workflows/i2-proposal-safety.yml'", heavy)
        for path in ("src/i2/docs/STATUS.md", "src/i2/docs/STATUS_HISTORY.md",
                     "src/i2/docs/README.md", "src/i2/AGENTS.md"):
            self.assertIn("'" + path + "'", light)
        self.assertIn("check_repo_navigation.py --scope current", light)


if __name__ == "__main__":
    unittest.main()
