"""Offline G0 export-receipt tests, using only synthetic provider bytes."""
from __future__ import annotations

import hashlib
import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
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


    def test_real_frozen_original_pins_are_read_statically_not_executed(self):
        original = tool._original_a1p_expectations(ROOT)
        self.assertEqual(len(original), 8)
        self.assertIn("a1-native-s1-td-read-masked.zip", original)
        self.assertEqual(original["a1-native-s1-canonical.zip"]["sha256"],
                         "e909d0faea78c09f5e2b4dca101caaf946c47a2a058b104bf8666bde642a03be")
        manifest_digest = tool._source_literal(
            ROOT / "tools/research/i1_a1c_reward_shadow_audit.py",
            tool.A1C_READER_BLOB, "ORIGINAL_MANIFEST_SHA256")
        self.assertEqual(manifest_digest, tool.A1C_MANIFEST_SHA256)
        self.assertEqual(len(tool.trusted_plan(ROOT)["campaigns"]["A1C"]["run_head_sha"]), 40)

    def test_original_archive_bytes_can_match_frozen_sha_without_approving_science(self):
        original_dir = self.root / "originals"
        original_dir.mkdir()
        expected = {}
        for i in range(8):
            name = f"synthetic-original-{i}.zip"
            raw = f"not an actual M11 ZIP {i}".encode("ascii")
            (original_dir / name).write_bytes(raw)
            expected[name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        receipt = tool._verify_original_files(original_dir, expected, "A1P")
        self.assertEqual(receipt["original_zip_files_checked"], 8)
        self.assertEqual(receipt["status"], "ORIGINAL_M11_ZIP_BYTES_MATCH_HISTORICAL_PINS")
        self.assertFalse(receipt["original_m11_chain_audited"])
        self.assertFalse(receipt["independent_source_authentication_attested"])
        self.assertFalse(receipt["independent_durable_custody_attested"])
        self.assertEqual(receipt["G0_scientific_gate"], "PARTIAL")
        self.assertEqual(receipt["scientific_verdict"], "NOT_EVALUATED")
        name = "synthetic-original-0.zip"
        (original_dir / name).write_bytes(b"X" * expected[name]["bytes"])
        with self.assertRaisesRegex(ValueError, "original M11 ZIP SHA-256 mismatch"):
            tool._verify_original_files(original_dir, expected, "A1P")

    def test_original_zip_staging_fails_closed_on_extra_missing_or_linked_files(self):
        root = self.root / "orig-stage"
        root.mkdir()
        name = "original-0.zip"
        content = b"synthetic original"
        path = root / name
        path.write_bytes(content)
        expected = {name: {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}}
        (root / "unexpected.zip").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            tool._verify_original_files(root, expected, "A1P")
        (root / "unexpected.zip").unlink()
        other = self.root / "other-real.zip"
        other.write_bytes(content)
        path.unlink()
        path.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            tool._verify_original_files(root, expected, "A1P")
        path.unlink()
        path.write_bytes(content)
        os.link(path, self.root / "hardlink-original")
        with self.assertRaisesRegex(ValueError, "hard-linked"):
            tool._verify_original_files(root, expected, "A1P")

    def test_original_byte_size_bound_and_expected_size_are_enforced(self):
        root = self.root / "orig-bounds"
        root.mkdir()
        p = root / "sample.zip"
        raw = b"some zipped bytes"
        p.write_bytes(raw)
        exp = {"sample.zip": {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw) - 1}}
        with self.assertRaisesRegex(ValueError, "byte size differs"):
            tool._verify_original_files(root, exp, "A1C")
        exp["sample.zip"]["bytes"] = len(raw)
        with patch.object(tool, "ORIGINAL_MAX_BYTES", len(raw) - 1):
            with self.assertRaisesRegex(ValueError, "invalid original M11 ZIP byte size"):
                tool._verify_original_files(root, exp, "A1C")

    def test_pinned_manifest_rejects_tamper_duplicates_and_nonfinite(self):
        manifest = self.root / "a1c-original-manifest.json"
        raw = b'{"original_run_id":40944104333,"x":1}\n'
        manifest.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(tool._load_small_pinned_json(manifest, digest)["original_run_id"],
                         40944104333)
        with self.assertRaisesRegex(ValueError, "manifest SHA-256 differs"):
            tool._load_small_pinned_json(manifest, "0" * 64)
        dup = b'{"x":1,"x":2}'
        manifest.write_bytes(dup)
        with self.assertRaisesRegex(ValueError, "duplicate original manifest JSON key"):
            tool._load_small_pinned_json(manifest, hashlib.sha256(dup).hexdigest())
        nan = b'{"x":NaN}'
        manifest.write_bytes(nan)
        with self.assertRaisesRegex(ValueError, "nonfinite original manifest value"):
            tool._load_small_pinned_json(manifest, hashlib.sha256(nan).hexdigest())

    def test_a1c_manifest_matrix_and_source_must_match_frozen_provenance(self):
        plan = tool.trusted_plan(ROOT)["campaigns"]["A1C"]
        root = self.root / "original-a1c"
        root.mkdir()
        records = []
        for role in ("native", "reversed"):
            for seed in range(101, 113):
                for arm in ("canonical", "td_read_masked"):
                    name = f"a1c-{role}-s{seed}-{arm}.zip"
                    raw = f"synthetic A1C {name}".encode("ascii")
                    (root / name).write_bytes(raw)
                    records.append({"name": name, "bytes": len(raw),
                                    "sha256": hashlib.sha256(raw).hexdigest()})
        manifest = self.root / "locked-original-a1c.json"
        payload = {
            "original_run_id": plan["run_id"], "original_source_sha": plan["run_head_sha"],
            "archived_independent_lives": 48, "original_zip_archives": records,
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        manifest.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        with patch.object(tool, "_source_literal", return_value=digest):
            with patch.object(tool, "A1C_MANIFEST_SHA256", digest):
                actual = tool.verify_originals(original_dir=root, campaign="A1C",
                                               manifest=manifest, repo_root=ROOT)
                self.assertEqual(actual["original_zip_files_checked"], 48)
                self.assertEqual(actual["G0_scientific_gate"], "PARTIAL")
                payload["original_zip_archives"][1]["name"] = payload["original_zip_archives"][0]["name"]
                corrupt = json.dumps(payload).encode("utf-8")
                manifest.write_bytes(corrupt)
                with patch.object(tool, "A1C_MANIFEST_SHA256",
                                  hashlib.sha256(corrupt).hexdigest()):
                    with patch.object(tool, "_source_literal",
                                      return_value=hashlib.sha256(corrupt).hexdigest()):
                        with self.assertRaisesRegex(ValueError, "duplicate"):
                            tool._original_a1c_expectations(manifest, ROOT)
        self.assertEqual(tool.trusted_plan(ROOT)["scientific_verdict"], "NOT_EVALUATED")

    def test_a1c_manifest_missing_or_conflicting_source_never_creates_receipt(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main([
                "verify-originals", "--campaign", "A1C",
                "--originals-dir", str(self.root),
                "--receipt", str(self.root / "nonexistent-receipt.json")]), 2)
        self.assertFalse((self.root / "nonexistent-receipt.json").exists())
        with redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main([
                "verify-originals", "--campaign", "A1P", "--originals-dir",
                str(self.root), "--manifest", str(self.root / "fake.json")]), 2)

    def test_frozen_reader_hash_fails_closed_on_source_drift(self):
        file_path = self.root / "frozen_reader.py"
        file_path.write_text("ORIGINAL_SHA256={'x.zip': 'a'}\n")
        with self.assertRaisesRegex(ValueError, "frozen reader Git blob changed"):
            tool._source_literal(file_path, "0" * 40, "ORIGINAL_SHA256")
        with self.assertRaisesRegex(ValueError, "frozen reader missing/duplicate"):
            raw = file_path.read_bytes()
            expected = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            tool._source_literal(file_path, expected, "ORIGINAL_MANIFEST_SHA256")


    def test_export_and_receipts_must_remain_outside_git_checkout(self):
        # This must fail before touching any files under the real checkout.
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            tool.verify_provider_exports(ROOT, self.plan, "A1P")
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            tool._verify_original_files(ROOT, {}, "A1P")
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            tool.write_new_receipt(ROOT / "forbidden-test-receipt.json", {"x": 1})
        shell = tool.shell_plan(tool.trusted_plan(ROOT))
        self.assertIn("git rev-parse --show-toplevel", shell)
        self.assertIn("Refusing export inside Git repository", shell)

    def test_a1p_original_run_and_source_must_match_inventory(self):
        reader = ROOT / "tools/research/i1_a1p_h48_reproduce.py"
        self.assertEqual(tool._source_literal(reader, tool.A1P_READER_BLOB, "ORIGIN_RUN"),
                         40938021102)
        self.assertEqual(tool._source_literal(reader, tool.A1P_READER_BLOB, "SOURCE_SHA"),
                         tool.trusted_plan(ROOT)["campaigns"]["A1P"]["run_head_sha"])
        expected = tool._original_a1p_expectations(ROOT)
        self.assertEqual(len(set(expected)), 8)
        self.assertTrue(all(x["bytes"] is None for x in expected.values()))


if __name__ == "__main__":
    unittest.main()
