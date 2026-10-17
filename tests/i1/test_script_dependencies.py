"""The historical script dependency scanner is non-executing and cautious."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from scan_script_dependencies import analyze


def fixture(root):
    (root / "scripts").mkdir()
    (root / "config").mkdir()
    (root / "config/tool-inventory.json").write_text(json.dumps({
        "active_ci_scripts": ["scripts/active.py"],
        "research_or_legacy_review": ["scripts/historical.py"],
    }))
    (root / "config/script-custody.json").write_text(json.dumps({
        "schema": "individual-zero-script-custody/v1", "reviewed": {},
    }))
    (root / "scripts/active.py").write_text("from pathlib import Path\n")
    (root / "scripts/historical.py").write_text(
        "from lab.journal import HashChainedJournal\n"
        "raise RuntimeError('HISTORICAL CODE MUST NOT RUN')\n")


class ScriptDependencyScanTests(unittest.TestCase):
    def test_current_inventory_is_complete_and_non_scientific(self):
        report = analyze(ROOT)
        self.assertEqual(report["status"], "PASS_WITH_REVIEW", report["errors"])
        self.assertEqual(report["active_scripts"], 5)
        self.assertEqual(report["review_pending"], 148)
        self.assertEqual(report["reviewed_with_import_evidence"], 2)
        self.assertEqual(report["scientific_conclusion"], "NOT_EVALUATED")
        self.assertIn("scripts/audit_i0_sqlite.py", report["scripts"])

    def test_active_import_of_unreviewed_script_fails_closed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            self.assertEqual(analyze(root)["status"], "PASS_WITH_REVIEW")
            (root / "scripts/active.py").write_text("from historical import x\n")
            report = analyze(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("unreviewed scripts" in x for x in report["errors"]))

    def test_false_review_evidence_is_rejected(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            p = root / "config/script-custody.json"
            bad = json.loads(p.read_text())
            bad["reviewed"]["scripts/historical.py"] = {
                "context": "archived_i0_lab_compatibility",
                "verified_import": "lab.absent",
                "scientific_oracle": False,
            }
            p.write_text(json.dumps(bad))
            report = analyze(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("import evidence" in x for x in report["errors"]))

    def test_broken_unreviewed_script_is_recorded_not_executed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "scripts/historical.py").write_text("if (:\n")
            report = analyze(root)
            self.assertEqual(report["status"], "PASS_WITH_REVIEW")
            self.assertTrue(report["scripts"]["scripts/historical.py"]["parse_error"])
            self.assertEqual(report["scientific_conclusion"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
