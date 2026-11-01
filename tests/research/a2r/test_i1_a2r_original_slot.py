"""Pure one-shot custody tests; no births or live cohort."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i1_a2r_archive_guard import canonical_bytes, origin_lock
from i1_eco_a2r_launch_gate import (
    REPOSITORY, WORKFLOW_REF, PROTOCOL, validate_launch_context,
)
from i1_eco_a2r_original_slot import reserve_original_slot, finalize_original_slot


def context():
    source="a"*40
    lock=canonical_bytes(origin_lock(
        source_commit=source, source_tree="b"*40,
        preset_sha256="c"*64, run_id=12345))
    digest=sha256(lock).hexdigest()
    return validate_launch_context(
        role="native",seed=2001,mode="CANONICAL_ABS",
        raw_lock=lock,externally_pinned_sha256=digest,
        github={"GITHUB_ACTIONS":"true","GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REPOSITORY":REPOSITORY,"GITHUB_REF":"refs/heads/main",
                "GITHUB_WORKFLOW_REF":WORKFLOW_REF,"GITHUB_RUN_ATTEMPT":"1",
                "GITHUB_RUN_ID":"12345","GITHUB_SHA":source},
        approval={"A2R_REVIEWED_PROTOCOL":PROTOCOL,
                  "A2R_REVIEWED_SOURCE_SHA":source,
                  "A2R_REVIEWED_LOCK_SHA256":digest,
                  "A2R_REVIEWED_RUN_ID":"12345"})


class SlotCustodyTests(unittest.TestCase):
    def test_pending_blocks_rebirth_and_incomplete_complete(self):
        with TemporaryDirectory() as td:
            ctx=context()
            one=reserve_original_slot(spool_root=td,context=ctx)
            self.assertFalse(one["launch_authorized"])
            with self.assertRaisesRegex(ValueError,"already reserved"):
                reserve_original_slot(spool_root=td,context=ctx)
            slot=Path(one["slot_path"])
            self.assertIn(b'"result":"PENDING"',(slot/"report.json").read_bytes())
            with self.assertRaisesRegex(ValueError,"lacks unlinked M11"):
                finalize_original_slot(spool_root=td,context=ctx,result="COMPLETE",
                    receipt={"generation":192,"status":"active",
                             "journal_head":"a"*64,"state_hash":"b"*64})
            self.assertIn(b'"result":"PENDING"',(slot/"report.json").read_bytes())

    def test_irreversible_failure_and_no_second_terminal(self):
        with TemporaryDirectory() as td:
            ctx=context()
            reserve_original_slot(spool_root=td,context=ctx)
            result=finalize_original_slot(spool_root=td,context=ctx,result="FAILED",
                receipt={"generation":0,"status":"technical_failure",
                         "journal_head":None,"state_hash":None})
            self.assertEqual(result["result"],"FAILED")
            with self.assertRaisesRegex(ValueError,"already finalized"):
                finalize_original_slot(spool_root=td,context=ctx,result="FAILED",
                    receipt={"generation":0,"status":"technical_failure",
                             "journal_head":None,"state_hash":None})
            with self.assertRaisesRegex(ValueError,"already reserved"):
                reserve_original_slot(spool_root=td,context=ctx)

    def test_complete_syntactic_not_authentic(self):
        with TemporaryDirectory() as td:
            ctx=context()
            slot=Path(reserve_original_slot(spool_root=td,context=ctx)["slot_path"])
            (slot/"life.sqlite").write_bytes(b"not a real sqlite")
            result=finalize_original_slot(spool_root=td,context=ctx,result="COMPLETE",
                receipt={"generation":192,"status":"active",
                         "journal_head":"a"*64,"state_hash":"b"*64})
            self.assertFalse(result["bytes_from_M11_independently_verified"])
            self.assertFalse(result["study_admissible"])
            with self.assertRaisesRegex(ValueError,"already finalized"):
                finalize_original_slot(spool_root=td,context=ctx,result="FAILED",
                    receipt={"generation":0,"status":"technical_failure",
                             "journal_head":None,"state_hash":None})

    def test_tampered_context_and_sidecar_rejected(self):
        with TemporaryDirectory() as td:
            ctx=context()
            slot=Path(reserve_original_slot(spool_root=td,context=ctx)["slot_path"])
            bad=dict(ctx,seed=2002)
            with self.assertRaises(ValueError):
                finalize_original_slot(spool_root=td,context=bad,result="FAILED",
                    receipt={"generation":0,"status":"technical_failure",
                             "journal_head":None,"state_hash":None})
            (slot/"surprise").write_bytes(b"x")
            with self.assertRaisesRegex(ValueError,"unaccounted"):
                finalize_original_slot(spool_root=td,context=ctx,result="FAILED",
                    receipt={"generation":0,"status":"technical_failure",
                             "journal_head":None,"state_hash":None})


if __name__=="__main__":
    unittest.main()
