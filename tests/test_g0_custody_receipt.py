"""Offline G0 export-receipt tests, using only synthetic provider bytes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "g0_custody_receipt", ROOT / "tools/research/g0_custody_receipt.py")
tool = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(tool)


class G0CustodyReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "A1P").mkdir()
        self.name = "a1-native-s1-canonical"
        self.bytes = b"synthetic github artifact archive bytes"
        self.record = {
            "id": 1, "name": self.name, "filename": self.name + ".zip",
            "expected_provider_digest": "sha256:" + hashlib.sha256(self.bytes).hexdigest(),
            "expected_size_bytes": len(self.bytes), "expires_at": "2026-11-28T19:13:23Z"
        }
        self.plan = {
            "repository": "josselin-orta-lab/individual-zero",
            "inventory_sha256": "a" * 64,
            "campaigns": {"A1P": {"run_id": 40938021102, "run_conclusion": "failure",
                                 "artifacts": [self.record]},
                          "A1C": {"run_id": 40944104333, "run_conclusion": "success",
                                  "artifacts": []}},
        }
        (self.root / "A1P" / self.record["filename"]).write_bytes(self.bytes)

    def check(self, root=None, campaign="A1P"):
        return tool.verify_provider_exports(root or self.root, self.plan, campaign)

    def test_real_pinned_inventory_plan_contains_58_and_preserves_negative_provenance(self):
        plan = tool.trusted_plan(ROOT)
        self.assertEqual(plan["status"], "PROVIDER_METADATA_PLAN_ONLY")
        self.assertEqual(sum(len(p["artifacts"]) for p in plan["campaigns"].values()), 58)
        self.assertEqual(plan["campaigns"]["A1P"]["run_conclusion"], "failure")
        self.assertEqual(plan["campaigns"]["A1C"]["run_conclusion"], "success")
        self.assertFalse(plan["external_durable_custody_attested"])
        self.assertEqual(plan["scientific_verdict"], "NOT_EVALUATED")

    def test_synthetic_provider_bytes_verify_but_not_original_m11(self):
        result = self.check()
        self.assertEqual(result["status"], "PROVIDER_PACKAGE_BYTES_MATCH_METADATA")
        self.assertEqual(result["verified_provider_packages"], 1)
        self.assertFalse(result["complete_two_campaign_provider_set"])
        self.assertFalse(result["original_inner_m11_zip_sha256_verified"])
        self.assertFalse(result["original_m11_chain_audited"])
        self.assertFalse(result["independent_durable_custody_attested"])
        self.assertEqual(result["G0_scientific_gate"], "PARTIAL")
        self.assertEqual(result["scientific_verdict"], "NOT_EVALUATED")

    def test_same_length_tampering_fails_sha_and_length_change_fails_size(self):
        path = self.root / "A1P" / self.record["filename"]
        path.write_bytes(b"X" * len(self.bytes))
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.check()
        path.write_bytes(self.bytes + b"!")
        with self.assertRaisesRegex(ValueError, "byte size mismatch"):
            self.check()

    def test_missing_extra_or_partial_artifact_fails_closed(self):
        path = self.root / "A1P" / self.record["filename"]
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            self.check()
        path.write_bytes(self.bytes)
        (self.root / "A1P" / ".g0-partial.123").write_bytes(b"partial")
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            self.check()

    def test_symlinked_files_and_directory_are_rejected(self):
        path = self.root / "A1P" / self.record["filename"]
        original = self.root / "other"
        original.write_bytes(self.bytes)
        path.unlink()
        path.symlink_to(original)
        with self.assertRaisesRegex(ValueError, "symlinked provider file"):
            self.check()
        path.unlink()
        (self.root / "A1P").rmdir()
        (self.root / "A1P").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "campaign directory"):
            self.check()

    def test_hardlinked_file_rejected(self):
        path = self.root / "A1P" / self.record["filename"]
        os.link(path, self.root / "hardlink")
        with self.assertRaisesRegex(ValueError, "hard-linked"):
            self.check()

    def test_receipts_are_private_and_never_overwritten(self):
        dest = self.root / "receipt.json"
        record = self.check()
        tool.write_new_receipt(dest, record)
        self.assertEqual(json.loads(dest.read_text())["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            tool.write_new_receipt(dest, {"claim": "APPROVED"})
        self.assertNotIn("APPROVED", dest.read_text())

    def test_shell_plan_prints_commands_only_without_embedded_secrets(self):
        plan = tool.trusted_plan(ROOT)
        script = tool.shell_plan(plan)
        self.assertEqual(script.count("gh api --method GET"), 58)
        self.assertIn("mktemp", script)
        self.assertIn("ln \"$tmp\"", script)
        self.assertIn("test ! -e", script)
        self.assertNotIn("GH_TOKEN=", script)
        self.assertIn("set -euo pipefail", script)
        self.assertEqual(plan["scientific_verdict"], "NOT_EVALUATED")

    def test_invalid_artifact_names_or_digest_cannot_escape_export_root(self):
        self.record["name"] = "../escape"
        with self.assertRaisesRegex(ValueError, "invalid provider filename"):
            self.check()
        self.record["name"] = self.name
        self.record["expected_provider_digest"] = "sha256:0000"
        with self.assertRaisesRegex(ValueError, "invalid provider digest"):
            self.check()

    def test_absent_second_campaign_is_not_silently_full_custody(self):
        with self.assertRaisesRegex(ValueError, "campaign directory"):
            self.check(campaign="ALL")


if __name__ == "__main__":
    unittest.main()
