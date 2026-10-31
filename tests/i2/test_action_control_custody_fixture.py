"""Inert SQLite review tests: no born life, M11, Scheduler or motor command."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from test_action_control_boundary import (  # synthetic providers, never authorities
    LIFE, SEMANTICS, SyntheticCurrent, SyntheticSafety, frame, advice,
)
from i2.modules.action_control_boundary import ControlReview
from i2.modules.action_control_custody_fixture import (
    ActionControlCustodyFixture, CustodyReviewReceipt,
    FaultInjected, CommitAcknowledgmentLost, _chain, _canonical,
)


class TestControlCustody(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "control.sqlite"
        self.source = SyntheticCurrent()
        self.safety = SyntheticSafety()

    def create(self, balance=4, *, path=None):
        return ActionControlCustodyFixture.create(
            path=path or self.path, life_ref=LIFE, synthetic_uc=balance,
            current_source=self.source, safety_source=self.safety)

    def reopen(self):
        return ActionControlCustodyFixture.reopen(
            path=self.path, life_ref=LIFE,
            current_source=self.source, safety_source=self.safety)

    def reviewed(self, obj=None, *, step=3, scores=None, fault=None):
        obj = obj or self.create()
        f = frame(step)
        return obj.review(frame=f, advice=advice(f, scores=scores), _fault_at=fault)

    def edit_event(self, transform, *, recompute_chain=True):
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT seq,event_json,previous_hash FROM events ORDER BY seq").fetchone()
            seq, raw, previous = row
            data = json.loads(raw)
            transform(data)
            body = _canonical(data)
            h = _chain(previous, body)
            conn.execute("UPDATE events SET event_json=?,event_hash=? WHERE seq=?", (body,h,seq))
            if recompute_chain:
                conn.execute("UPDATE account SET chain_head=? WHERE id=1", (h,))

    def test_no_birth_command_admission_or_motor_authority(self):
        f = self.create()
        r = self.reviewed(f)
        self.assertEqual(r.motor_authority, "NONE")
        self.assertEqual(f.audit()["motor_authority"], "NONE")
        for forbidden in ("birth", "run_step", "dispatch", "execute", "admit", "command", "cold_recover"):
            self.assertFalse(hasattr(f, forbidden))
        self.assertFalse({"command", "admission", "action", "winner", "permit"} &
                         {x.name for x in fields(CustodyReviewReceipt)})

    def test_missing_external_sources_not_accepted(self):
        for current, safety in ((None,self.safety),(self.source,None)):
            with self.subTest(current=current,safety=safety), self.assertRaises(ValueError):
                ActionControlCustodyFixture(path=self.path, life_ref=LIFE,
                                            current_source=current, safety_source=safety)

    def test_creation_is_non_destructive_and_empty(self):
        f = self.create(6)
        v = f.audit()
        self.assertEqual((v["remaining_synthetic_uc"],v["committed"],v["last_step"]), (6,0,-1))
        self.assertFalse(v["m11_authenticated"])
        self.assertFalse(v["scheduler_uc_authenticated"])
        with self.assertRaises(FileExistsError):
            self.create(1)

    def test_negative_bool_and_invalid_capacity_rejected(self):
        for capacity in (-1,True,0.2,1000001):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                self.create(capacity)
        self.assertFalse(self.path.exists())

    def test_funded_review_and_exact_synthetic_debit(self):
        f = self.create(2)
        r = self.reviewed(f)
        self.assertEqual((r.seq,r.status,r.units_spent), (1,"REVIEWED_NOT_ADMITTED",1))
        self.assertIsNotNone(r.suggested_candidate_ref)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],1)
        self.assertEqual(f.lookup(capture_ref=r.capture_ref),r)
        self.assertEqual(len(self.safety.calls),1)
        self.assertTrue(self.safety.calls[0][-1].startswith("synthetic:control:"))

    def test_safety_veto_masks_candidate_but_is_not_admission(self):
        self.safety.veto=True
        f=self.create()
        r=self.reviewed(f)
        self.assertEqual(r.status,"VETOED")
        self.assertIsNone(r.suggested_candidate_ref)
        self.assertEqual(r.motor_authority,"NONE")
        self.assertEqual(f.audit()["remaining_synthetic_uc"],3)

    def test_no_advice_is_committed_without_charge(self):
        f=self.create(2)
        r=self.reviewed(f,scores={})
        self.assertEqual((r.status,r.units_spent), ("NO_ADVICE",0))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],2)
        self.assertEqual(self.safety.calls,[])

    def test_ambiguous_tie_does_not_bill_control_review(self):
        f=self.create(2)
        r=self.reviewed(f,scores={SEMANTICS[0]:4, SEMANTICS[1]:4})
        self.assertEqual(r.status,"NO_ADVICE")
        self.assertEqual(r.units_spent,0)
        self.assertEqual(self.safety.calls,[])

    def test_no_uc_is_persisted_unfunded_without_veto(self):
        f=self.create(0)
        r=self.reviewed(f)
        self.assertEqual((r.status,r.units_spent,r.suggested_candidate_ref), ("UNFUNDED",0,None))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],0)
        self.assertEqual(self.safety.calls,[])

    def test_exact_budget_and_second_frame_new_step_is_unfunded(self):
        f=self.create(1)
        self.reviewed(f,step=3)
        r=self.reviewed(f,step=4)
        self.assertEqual(r.status,"UNFUNDED")
        self.assertEqual(f.audit()["committed"],2)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],0)

    def test_reopen_does_not_reverify_or_rebill(self):
        f=self.create()
        original=self.reviewed(f)
        calls=(len(self.source.calls),len(self.safety.calls))
        other=self.reopen()
        self.assertEqual(other.lookup(capture_ref="capture:3"),original)
        self.assertEqual((len(self.source.calls),len(self.safety.calls)),calls)
        self.assertEqual(other.audit()["committed"],1)

    def test_duplicate_capture_same_frame_is_not_recharged(self):
        f=self.create()
        original=self.reviewed(f)
        with self.assertRaises(ValueError):
            self.reviewed(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],3)
        self.assertEqual(f.lookup(capture_ref="capture:3"), original)

    def test_replay_from_reopened_session_is_rejected(self):
        first=self.create()
        self.reviewed(first)
        other=self.reopen()
        with self.assertRaises(ValueError):
            self.reviewed(other)
        self.assertEqual(other.audit()["remaining_synthetic_uc"],3)
        self.assertEqual(len(self.safety.calls),1)

    def test_same_capture_new_frame_identity_cannot_reset_replay(self):
        f=self.create()
        self.reviewed(f,step=3)
        changed=frame(4,capture_ref="capture:3")
        with self.assertRaises(ValueError):
            f.review(frame=changed,advice=advice(changed))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],3)

    def test_old_step_rejected_from_second_session(self):
        f=self.create()
        self.reviewed(f,step=6)
        old=frame(4)
        with self.assertRaises(ValueError):
            self.reopen().review(frame=old,advice=advice(old))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],3)

    def test_invalid_current_source_no_charge_or_database_event(self):
        f=self.create()
        self.source.overrule=False
        with self.assertRaises(ValueError):self.reviewed(f)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(self.safety.calls,[])

    def test_truthy_nonbool_current_source_fails_closed(self):
        f=self.create()
        self.source.overrule=1
        with self.assertRaises(ValueError):self.reviewed(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_life_and_advice_shape_rejected_before_external_ports(self):
        f=self.create()
        foreign=frame(life="life:other")
        with self.assertRaises(ValueError):f.review(frame=foreign,advice=advice(foreign))
        fresh=frame()
        forged=replace(advice(fresh),suggested_candidate_ref=fresh.candidates[0].candidate_ref)
        with self.assertRaises(ValueError):f.review(frame=fresh,advice=forged)
        self.assertEqual(self.source.calls,[])
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_invalid_safety_finding_rolls_back_paid_review(self):
        f=self.create()
        self.safety.tamper=lambda finding: replace(finding,control_receipt_ref="receipt:other")
        with self.assertRaises(ValueError):self.reviewed(f)
        self.assertEqual((f.audit()["committed"],f.audit()["remaining_synthetic_uc"]),(0,4))

    def test_safety_exception_rolls_back_synthetic_uc(self):
        f=self.create()
        self.safety.throw=True
        with self.assertRaises(RuntimeError):self.reviewed(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_context_changed_before_commit_rolls_back(self):
        class ChangingCurrent(SyntheticCurrent):
            def verify_current(self, *, life_ref, frame, advice):
                self.calls.append(frame.frame_ref)
                return len(self.calls)==1
        self.source=ChangingCurrent()
        f=self.create()
        with self.assertRaises(ValueError):self.reviewed(f)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_injected_faults_precommit_are_atomic(self):
        for fault in ("after_control_debit","after_safety","before_commit"):
            with self.subTest(fault=fault):
                p=Path(self.temp.name)/f"control_{fault}.sqlite"
                f=self.create(path=p)
                f2=frame()
                with self.assertRaises(FaultInjected):
                    f.review(frame=f2,advice=advice(f2),_fault_at=fault)
                self.assertEqual((f.audit()["committed"],f.audit()["remaining_synthetic_uc"]),(0,4))

    def test_after_commit_lost_ack_readonly_resolves(self):
        f=self.create()
        with self.assertRaises(CommitAcknowledgmentLost):
            self.reviewed(f,fault="after_commit")
        historical=f.lookup(capture_ref="capture:3")
        self.assertEqual(historical.status,"REVIEWED_NOT_ADMITTED")
        self.assertEqual(historical.units_spent,1)
        with self.assertRaises(ValueError):self.reviewed(f)
        self.assertEqual((f.audit()["committed"],f.audit()["remaining_synthetic_uc"]),(1,3))
        self.assertEqual(len(self.safety.calls),1)

    def test_two_sessions_compete_for_single_capture_commit(self):
        f=self.create()
        g=self.reopen()
        v=frame()
        def attempt(obj):
            try:return obj.review(frame=v,advice=advice(v)).status
            except ValueError:return "REPLAY_REFUSED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            result=list(pool.map(attempt,(f,g)))
        self.assertCountEqual(result,["REVIEWED_NOT_ADMITTED","REPLAY_REFUSED"])
        self.assertEqual(f.audit()["remaining_synthetic_uc"],3)
        self.assertEqual(len(self.safety.calls),1)

    def test_corrupt_account_balance_detected_before_review(self):
        f=self.create();self.reviewed(f)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE account SET remaining_uc=remaining_uc+1 WHERE id=1")
        with self.assertRaises(ValueError):f.audit()

    def test_corrupt_event_chain_detected(self):
        f=self.create();self.reviewed(f)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE events SET event_hash=? WHERE seq=1",("0"*64,))
        with self.assertRaises(ValueError):f.lookup(capture_ref="capture:3")

    def test_tampered_stored_veto_detected_even_after_rehash(self):
        f=self.create();self.reviewed(f)
        self.edit_event(lambda d:d["safety_finding"].update(veto=True))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_synthetic_spend_detected_even_after_rehash(self):
        f=self.create();self.reviewed(f)
        self.edit_event(lambda d:d.update(units_spent=0))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_review_status_detected_even_after_rehash(self):
        f=self.create();self.reviewed(f)
        self.edit_event(lambda d:d["review"].update(status="ADMITTED"))
        with self.assertRaises(ValueError):f.audit()

    def test_stored_motor_authority_forgery_detected(self):
        f=self.create();self.reviewed(f)
        self.edit_event(lambda d:d["review"].update(motor_authority="GRANTED"))
        with self.assertRaises(ValueError):f.audit()

    def test_intention_tag_is_not_motor_or_safety_authority(self):
        for index,tagged in enumerate((False,True)):
            p=Path(self.temp.name)/f"tagged_{index}.sqlite"
            obj=self.create(path=p)
            f=frame(tagged=tagged)
            r=obj.review(frame=f,advice=advice(f))
            self.assertEqual((r.status,r.motor_authority,r.units_spent),
                             ("REVIEWED_NOT_ADMITTED","NONE",1))

    def test_symlink_and_foreign_life_never_reopened(self):
        f=self.create()
        self.reviewed(f)
        with self.assertRaises(ValueError):
            ActionControlCustodyFixture.reopen(path=self.path,life_ref="life:foreign",
                                               current_source=self.source,safety_source=self.safety)
        link=Path(self.temp.name)/"linked.sqlite"
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            ActionControlCustodyFixture.reopen(path=link,life_ref=LIFE,
                                               current_source=self.source,safety_source=self.safety)

    def test_unknown_fault_never_pays(self):
        f=self.create()
        with self.assertRaises(ValueError):self.reviewed(f,fault="after_world_action")
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_no_external_source_verification_on_audit(self):
        f=self.create();self.reviewed(f)
        calls=(len(self.source.calls),len(self.safety.calls))
        self.reopen().audit()
        self.assertEqual((len(self.source.calls),len(self.safety.calls)),calls)


if __name__=="__main__":
    unittest.main()
