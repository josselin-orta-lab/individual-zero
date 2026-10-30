"""Pure adversarial A2-R archive custody contracts; never birth I1."""
import copy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from i1_a2r_archive_guard import (origin_lock, ordered_rows, canonical_bytes,
    sha256_bytes, verify_archive, load_canonical_json, validate_lock)

SRC="a"*40
TREE="b"*40
PRESET="c"*64
RUN=123456


def fixture(root):
    lock=origin_lock(source_commit=SRC,source_tree=TREE,preset_sha256=PRESET,run_id=RUN)
    lock_raw=canonical_bytes(lock)
    (root/"lock.json").write_bytes(lock_raw)
    rows=[]
    (root/"lives").mkdir()
    for entry in ordered_rows():
        folder=root/"lives"/entry["identity"]
        folder.mkdir()
        payload=(entry["identity"]+" original M11 test bytes").encode()
        report=b'{"test":true}\n'
        (folder/"life.sqlite").write_bytes(payload)
        (folder/"report.json").write_bytes(report)
        rows.append({**entry,"run_attempt":1,"source_commit":SRC,"result":"COMPLETE",
          "generation":192,"status":"active","journal_head":"d"*64,"state_hash":"e"*64,
          "files":{"life.sqlite":sha256_bytes(payload),"report.json":sha256_bytes(report)}})
    manifest={"schema":"individual-zero-i1-a2r-original-archive/1",
       "lock_sha256":sha256_bytes(lock_raw),"source_commit":SRC,"github_run_id":RUN,
       "github_run_attempt":1,"horizon":192,"lives":rows,"general_L3":"NOT_ESTABLISHED"}
    (root/"manifest.json").write_bytes(canonical_bytes(manifest))
    return manifest


def verify(root):
    return verify_archive(root=root,expected_commit=SRC,expected_tree=TREE,
       expected_preset=PRESET,expected_run_id=RUN,
       expected_lock_sha256=sha256_bytes((root/"lock.json").read_bytes()),
       expected_manifest_sha256=sha256_bytes((root/"manifest.json").read_bytes()))


class ArchiveGuardTests(unittest.TestCase):
    def test_complete_96_identity_roster_not_scientific_go(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve()
            fixture(root)
            result=verify(root)
            self.assertEqual(result["original_lives"],96)
            self.assertEqual(result["independent_seed_blocks"],24)
            self.assertFalse(result["study_admissible"])
            self.assertFalse(result["source_runtime_execution_attested"])
            self.assertEqual(result["adaptive_learning_go"],"NOT_ESTABLISHED")

    def test_lock_rejects_wrong_run_and_source(self):
        lock=origin_lock(source_commit=SRC,source_tree=TREE,preset_sha256=PRESET,run_id=RUN)
        for changed in (dict(lock,github_run_attempt=2),dict(lock,source_commit="f"*40)):
            with self.assertRaises(ValueError):
                validate_lock(changed,expected_commit=SRC,expected_tree=TREE,
                              expected_preset=PRESET,expected_run_id=RUN)

    def test_missing_and_extra_originals(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve(); original=fixture(root)
            target=root/"lives"/original["lives"][0]["identity"]/"life.sqlite"
            target.unlink()
            with self.assertRaises(ValueError):
                verify(root)

    def test_file_tampering_detected_even_with_unmodified_manifest(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve(); original=fixture(root)
            target=root/"lives"/original["lives"][0]["identity"]/"life.sqlite"
            target.write_bytes(b"forged")
            with self.assertRaises(ValueError):
                verify(root)

    def test_external_anchor_required(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve();fixture(root)
            with self.assertRaises(ValueError):
                verify_archive(root=root,expected_commit=SRC,expected_tree=TREE,
                expected_preset=PRESET,expected_run_id=RUN,
                expected_lock_sha256="0"*64,
                expected_manifest_sha256=sha256_bytes((root/"manifest.json").read_bytes()))

    def test_symlink_is_not_original(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve(); original=fixture(root)
            target=root/"lives"/original["lives"][0]["identity"]/"life.sqlite"
            other=target.with_name("copy");other.write_bytes(target.read_bytes())
            target.unlink();target.symlink_to(other)
            with self.assertRaises(ValueError):
                verify(root)

    def test_failure_not_selectively_dropped(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve();manifest=fixture(root)
            manifest["lives"][0]["result"]="FAILED"
            (root/"manifest.json").write_bytes(canonical_bytes(manifest))
            with self.assertRaisesRegex(ValueError,"failure"):
                verify(root)

    def test_json_duplicate_keys_rejected(self):
        with TemporaryDirectory() as d:
            root=Path(d).resolve()
            b=b'{"x":1,"x":2}\n'
            path=root/"duplicate.json";path.write_bytes(b)
            with self.assertRaises(ValueError):
                load_canonical_json(path,expected_digest=sha256_bytes(b))

if __name__=="__main__":
    unittest.main()
