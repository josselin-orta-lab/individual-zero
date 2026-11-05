"""Static, zero-birth checks of proposed #990 manual evidence workflow.

These tests inspect an inert YAML file. They never contact GitHub, reserve
the real protected tag, dispatch a job or instantiate NativePaidI2.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/i2-p4-990-manual-study.yml"


class I2P4990ManualWorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_only_explicit_manual_dispatch_and_single_first_attempt(self):
        src = self.source
        self.assertIn("  workflow_dispatch:", src)
        for disallowed in ("  push:", "  pull_request:", "  schedule:", "  workflow_run:"):
            self.assertNotIn(disallowed, src)
        self.assertIn('test "$RUN_NUMBER" = \'1\'', src)
        self.assertIn('test "$RUN_ATTEMPT" = \'1\'', src)
        self.assertIn("cancel-in-progress: false", src)

    def test_claim_precedes_birth_and_uses_exact_existing_helper(self):
        src = self.source
        first = src.index("tools/i2_p4_990_one_shot_claim.py")
        second = src.index("tools/i2_p4_origin_failure_study_990.py")
        self.assertLess(first, second)
        self.assertIn("I2_P4_990_TAG_RULESET_ID: '26611746'", src)
        self.assertIn("secrets.GITHUB_TOKEN", src)
        self.assertIn("persist-credentials: false", src)
        self.assertIn("PYTHONDONTWRITEBYTECODE: '1'", src)
        self.assertIn("python -B tools/i2_p4_990_one_shot_claim.py", src)
        self.assertIn("python -B tools/i2_p4_origin_failure_study_990.py", src)
        self.assertIn("--execute-protocol-990", src)
        self.assertNotIn("retry:", src)

    def test_source_lock_and_new_external_custody(self):
        src = self.source
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"', src)
        self.assertIn('git status --porcelain --untracked-files=all', src)
        self.assertIn('test ! -e "$STUDY_OUTPUT"', src)
        self.assertIn("runner.temp", src)
        self.assertIn("CLAIM_CONSUMED", src)
        self.assertIn('test -s "$EVIDENCE/claim-receipt.json"', src)

    def test_failure_artifacts_include_complete_and_partial_evidence(self):
        src = self.source
        self.assertGreaterEqual(src.count("if: ${{ always() }}"), 2)
        self.assertIn("SHA256SUMS.txt", src)
        self.assertIn("actions/upload-artifact@v4", src)
        self.assertIn("if-no-files-found: error", src)
        self.assertIn("include-hidden-files: true", src)
        self.assertIn("retention-days: 90", src)
        self.assertNotIn("m11_authenticated: true", src)


if __name__ == "__main__":
    unittest.main()
