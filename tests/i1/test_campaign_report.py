"""Reports must distinguish observed gates from absent, corrupt or false ones."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from campaign_report import generate_report, markdown_report, _git_head


class CampaignEvidenceTests(unittest.TestCase):
    def test_missing_evidence_never_claims_ci_passed(self):
        with TemporaryDirectory() as tmp:
            report = generate_report(
                root=ROOT, report_dir=Path(tmp), engine="I1",
                python_version="3.11", env={})
            self.assertEqual(report["software"]["status"], "PARTIAL_EVIDENCE")
            self.assertEqual(report["local_head"], _git_head(ROOT))
            self.assertIn("m11", report["software"]["not_observed"])
            self.assertEqual(report["scientific"]["status"], "NOT_EVALUATED")
            self.assertEqual(report["merge_status"], "NOT_VERIFIED_WITH_GITHUB")
            self.assertIn("NOT EVALUATED", markdown_report(report))

    def test_valid_suite_needs_matching_head_and_no_false_success(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            sample = {
                "engine": "I1", "suite": "structure", "local_head": _git_head(ROOT),
                "executed": True, "scientific_gate": "NOT_EVALUATED",
                "status": "PASS", "steps": [{"status": "PASS", "returncode": 0}],
            }
            path = folder / "i1-structure-3.11.json"
            path.write_text(json.dumps(sample))
            report = generate_report(root=ROOT, report_dir=folder,
                                     engine="I1", python_version="3.11", env={})
            self.assertEqual(report["software"]["suites"]["structure"]["status"], "PASS")
            sample["local_head"] = "0" * 40
            path.write_text(json.dumps(sample))
            report = generate_report(root=ROOT, report_dir=folder,
                                     engine="I1", python_version="3.11", env={})
            self.assertEqual(report["software"]["status"], "EVIDENCE_FAILURE")
            self.assertEqual(report["software"]["suites"]["structure"]["status"], "INVALID")

    def test_junit_is_parsed_but_never_scholarly_evidence(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "i1-3.12.xml").write_text(
                '<testsuite tests="2" failures="0" errors="0"><testcase name="a"/>'
                '<testcase name="b"/></testsuite>')
            report = generate_report(root=ROOT, report_dir=folder,
                                     engine="I1", python_version="3.12", env={})
            self.assertEqual(report["software"]["junit"]["smoke"]["status"], "PASS")
            self.assertEqual(report["software"]["junit"]["smoke"]["tests"], 2)
            self.assertEqual(report["scientific"]["stage10_nonempty_publication"], "NOT_PROVEN")
            (folder / "i1-3.12.xml").write_text("<broken")
            self.assertEqual(
                generate_report(root=ROOT, report_dir=folder,
                                engine="I1", python_version="3.12", env={})
                ["software"]["status"], "EVIDENCE_FAILURE")

    def test_wrong_generation_is_refused(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                generate_report(root=ROOT, report_dir=Path(tmp),
                                engine="I2", python_version="3.11", env={})


if __name__ == "__main__":
    unittest.main()
