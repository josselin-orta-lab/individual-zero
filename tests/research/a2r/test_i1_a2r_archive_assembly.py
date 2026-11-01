"""No-birth tests for A2-R complete original archive assembly."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from i1_a2r_archive_assembly import assemble_original_archive, FRAGMENT_SCHEMA
from i1_a2r_archive_guard import origin_lock, ordered_rows, canonical_bytes, sha256_bytes, verify_archive

C="a"*40
T="b"*40
P="c"*64
RUN=42

def build(root, *, failing=False):
    spool=root/"spool";spool.mkdir()
    lock=root/"lock.json"
    lock.write_bytes(canonical_bytes(origin_lock(source_commit=C,source_tree=T,
                                   preset_sha256=P,run_id=RUN)))
    for i,row in enumerate(ordered_rows()):
        folder=spool/row["identity"];folder.mkdir()
        result="FAILED" if failing and i==0 else "COMPLETE"
        report=dict(schema=FRAGMENT_SCHEMA,**row,horizon=192,
            source_commit=C,source_tree=T,preset_sha256=P,
            github_run_id=RUN,github_run_attempt=1,
            result=result,generation=0 if result=="FAILED" else 192,
            status="technical_failure" if result=="FAILED" else "active",
            journal_head="d"*64,state_hash="e"*64,general_L3="NOT_ESTABLISHED")
        (folder/"report.json").write_bytes(canonical_bytes(report))
        if result=="COMPLETE":
            (folder/"life.sqlite").write_bytes(("sqlite "+row["identity"]).encode())
    return spool,lock

def assemble(root,spool,lock,destination="sealed"):
    return assemble_original_archive(spool_root=spool,destination=root/destination,
            external_lock_path=lock,external_lock_sha256=sha256_bytes(lock.read_bytes()),
            source_commit=C,source_tree=T,preset_sha256=P,github_run_id=RUN)

class AssemblyTests(unittest.TestCase):
    def test_full_96_archives_and_guard(self):
        with TemporaryDirectory() as temp:
            root=Path(temp).resolve();spool,lock=build(root)
            receipt=assemble(root,spool,lock)
            self.assertEqual(receipt["original_lives"],96)
            self.assertFalse(receipt["scientific_analysis_admissible"])
            result=verify_archive(root=root/"sealed",expected_commit=C,
                expected_tree=T,expected_preset=P,expected_run_id=RUN,
                expected_lock_sha256=sha256_bytes(lock.read_bytes()),
                expected_manifest_sha256=receipt["manifest_sha256_to_publish_independently"])
            self.assertEqual(result["original_lives"],96)
            with self.assertRaises(ValueError):
                assemble(root,spool,lock)
    def test_missing_original_rejected_before_output(self):
        with TemporaryDirectory() as temp:
            root=Path(temp).resolve();spool,lock=build(root)
            import shutil
            shutil.rmtree(spool/ordered_rows()[0]["identity"])
            with self.assertRaises(ValueError):assemble(root,spool,lock)
            self.assertFalse((root/"sealed").exists())
    def test_report_forgery_rejected(self):
        with TemporaryDirectory() as temp:
            root=Path(temp).resolve();spool,lock=build(root)
            path=spool/ordered_rows()[0]["identity"]/"report.json"
            row=json.loads(path.read_bytes());row["github_run_attempt"]=2
            path.write_bytes(canonical_bytes(row))
            with self.assertRaises(ValueError):assemble(root,spool,lock)
    def test_failures_preserved_not_upgraded(self):
        with TemporaryDirectory() as temp:
            root=Path(temp).resolve();spool,lock=build(root,failing=True)
            receipt=assemble(root,spool,lock)
            self.assertEqual(receipt["individual_failures_preserved"],1)
            self.assertEqual(receipt["status"],"MEASUREMENT_BLOCKED")
            with self.assertRaises(ValueError):
                verify_archive(root=root/"sealed",expected_commit=C,
                    expected_tree=T,expected_preset=P,expected_run_id=RUN,
                    expected_lock_sha256=sha256_bytes(lock.read_bytes()),
                    expected_manifest_sha256=receipt["manifest_sha256_to_publish_independently"])
if __name__=="__main__":
    unittest.main()
