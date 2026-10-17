"""The historical script dependency scanner is non-executing and cautious."""
import json
from hashlib import sha1
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
        "schema": "individual-zero-script-custody/v2", "reviewed": {},
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
        self.assertEqual(report["reviewed_with_import_evidence"], 5)
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


    def test_attestation_requires_exact_source_blob_and_import_line(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            script = root / "scripts/historical.py"
            content = script.read_bytes()
            digest = sha1(
                b"blob " + str(len(content)).encode("ascii") +
                bytes([0]) + content
            ).hexdigest()
            manifest_path = root / "config/script-custody.json"
            manifest = json.loads(manifest_path.read_text())
            claim = {
                "context": "archived_i0_lab_compatibility",
                "verified_import": "lab.journal",
                "verified_line": 1,
                "verified_git_blob_sha1": digest,
                "scientific_oracle": False,
            }
            manifest["reviewed"]["scripts/historical.py"] = claim
            manifest_path.write_text(json.dumps(manifest))
            self.assertEqual(analyze(root)["status"], "PASS_WITH_REVIEW")
            # Even if the old import still exists, changed bytes void review.
            script.write_text(script.read_text() + "# changed after review\n")
            changed = analyze(root)
            self.assertEqual(changed["status"], "FAIL")
            self.assertTrue(any("review import evidence" in e
                                for e in changed["errors"]))
            script.write_bytes(content)
            claim["verified_line"] = 2
            manifest_path.write_text(json.dumps(manifest))
            self.assertEqual(analyze(root)["status"], "FAIL")

    def test_literal_subprocess_execution_of_unreviewed_script_is_rejected(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "scripts/active.py").write_text(
                "from pathlib import Path\nimport subprocess, sys\n"
                'child = Path(__file__).with_name("historical.py")\n'
                "subprocess.run([sys.executable, str(child)], check=False)\n"
            )
            report = analyze(root)
            self.assertEqual(report["status"], "FAIL")
            entry = report["scripts"]["scripts/active.py"]
            self.assertEqual(entry["resolved_subprocess_script_dependencies"],
                             ["scripts/historical.py"])
            self.assertIn("scripts/historical.py", entry["transitive_script_dependencies"])
            self.assertTrue(any("unreviewed scripts" in x for x in report["errors"]))

    def test_literal_repo_script_path_resolves_from_assignment(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "scripts/active.py").write_text(
                "from pathlib import Path\nimport subprocess, sys\n"
                'SCRIPT = Path(".") / "scripts" / "historical.py"\n'
                "subprocess.check_call([sys.executable, str(SCRIPT)])\n"
            )
            report = analyze(root)
            self.assertEqual(report["status"], "FAIL")
            entry = report["scripts"]["scripts/active.py"]
            self.assertEqual(entry["resolved_subprocess_script_dependencies"],
                             ["scripts/historical.py"])

    def test_dynamic_subprocess_is_not_falsely_called_complete(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "scripts/active.py").write_text(
                "import subprocess\n"
                "def launch(command):\n"
                "    return subprocess.run(command, check=False)\n"
            )
            report = analyze(root)
            self.assertEqual(report["status"], "PASS_WITH_REVIEW")
            entry = report["scripts"]["scripts/active.py"]
            self.assertEqual(entry["dependency_completeness"],
                             "INCOMPLETE_DYNAMIC_IMPORTS_OR_SUBPROCESSES")
            self.assertEqual(entry["subprocess_calls"][0]["resolved_script_targets"], [])

    def test_path_literal_is_evidence_not_engine_ownership(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "scripts/historical.py").write_text(
                "from pathlib import Path\n"
                'source = Path("i1-a2-training-manifest.json")\n'
                "raise RuntimeError('never execute old test')\n"
            )
            report = analyze(root)
            self.assertEqual(report["status"], "PASS_WITH_REVIEW")
            self.assertEqual(
                report["scripts"]["scripts/historical.py"]["literal_file_references"],
                [{"line": 2, "literal": "i1-a2-training-manifest.json"}]
            )
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
