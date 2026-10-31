"""Isolated proposal-policy tests; no born I2, UC ledger or M11 runtime."""
import copy
import json
from pathlib import Path
import sys
import unittest
from dataclasses import fields

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.intention_continuity import (  # noqa: E402
    FirstPersonCapture, IntentionContinuity, SemanticIntention, POLICY,
)

SEM = "affordance:berry_a"
GOAL = "goal:hunger:1"


def capture(step, *, visible=True, goal=GOAL, conflict=False, ref=None):
    return FirstPersonCapture(
        step, ref or f"capture:{step}", goal,
        (SEM,) if visible else (),
        (SEM,) if conflict else (),
    )


def open_owner(*, at=3, ttl=8):
    owner = IntentionContinuity()
    event = owner.open(capture=capture(at), semantic_ref=SEM,
                       evidence_ref=f"evidence:{at}:lived", ttl_steps=ttl,
                       work_ref=f"charge:{at}")
    assert event.kind == "opened"
    return owner


class TestIntentionContinuity(unittest.TestCase):
    def test_new_owner_is_empty_and_not_an_engine(self):
        obj = IntentionContinuity()
        self.assertIsNone(obj.current)
        self.assertEqual(obj.export_state(), {
            "policy": POLICY, "last_step": -1,
            "last_capture_ref": None, "current": None,
        })
        self.assertFalse(any(name in {f.name for f in fields(SemanticIntention)}
                             for name in ("option_ref", "command", "accumulator", "winner", "admission", "threshold")))
        self.assertFalse(hasattr(obj, "run_step"))
        self.assertFalse(hasattr(obj, "birth"))

    def test_new_intent_requires_visible_personal_context(self):
        cases = [capture(3,visible=False),capture(3,goal=None)]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                IntentionContinuity().open(capture=bad,semantic_ref=SEM,
                    evidence_ref="evidence:3",ttl_steps=5,work_ref="charge:3")
        self.assertIsNone(IntentionContinuity().current)

    def test_open_rejects_missing_or_unbounded_work_and_ttl(self):
        for ttl in (0,-1,65,True,1.0):
            with self.subTest(ttl=ttl), self.assertRaises(ValueError):
                IntentionContinuity().open(capture=capture(3),semantic_ref=SEM,
                    evidence_ref="evidence:3",ttl_steps=ttl,work_ref="charge:3")
        for ref in ("", "white space", "\x00", 1, None):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                IntentionContinuity().open(capture=capture(3),semantic_ref=SEM,
                    evidence_ref="evidence:3",ttl_steps=5,work_ref=ref)

    def test_intent_identity_is_deterministic_and_provenance_bound(self):
        a=open_owner()
        b=open_owner()
        self.assertEqual(a.current.ref,b.current.ref)
        other=IntentionContinuity()
        other.open(capture=capture(4),semantic_ref=SEM,
                   evidence_ref="evidence:4",ttl_steps=8,work_ref="charge:4")
        self.assertNotEqual(a.current.ref,other.current.ref)
        self.assertEqual(a.current.origin_capture_ref,"capture:3")
        self.assertEqual(a.current.origin_evidence_ref,"evidence:3:lived")

    def test_two_captures_retain_semantics_not_motor_state(self):
        owner=open_owner()
        earlier=owner.current
        e=owner.observe(capture=capture(4),work_ref="charge:4")
        self.assertEqual(e.kind,"retained")
        self.assertEqual(owner.current.ref,earlier.ref)
        self.assertEqual(owner.current.created_step,3)
        self.assertEqual(owner.current.last_checked_step,4)
        self.assertEqual(owner.current.status,"active")
        self.assertEqual(set(owner.export_state()["current"]),set(earlier.__dataclass_fields__))

    def test_hidden_affordance_suspends_without_claiming_disappearance(self):
        owner=open_owner()
        self.assertEqual(owner.observe(capture=capture(4,visible=False),work_ref="charge:4").kind,"suspended")
        self.assertEqual(owner.current.status,"suspended")
        self.assertEqual(owner.observe(capture=capture(5,visible=False),work_ref="charge:5").kind,"still_suspended")
        self.assertEqual(owner.observe(capture=capture(6),work_ref="charge:6").kind,"resumed")
        self.assertEqual(owner.current.ref,open_owner().current.ref)

    def test_changed_goal_cancels_even_when_affordance_visible(self):
        owner=open_owner()
        self.assertEqual(owner.observe(capture=capture(4,goal="goal:water"),work_ref="charge:4").kind,"goal_changed")
        self.assertIsNone(owner.current)

    def test_personally_reported_contradiction_cancels(self):
        owner=open_owner()
        self.assertEqual(owner.observe(capture=capture(4,visible=False,conflict=True),work_ref="charge:4").kind,"contradicted")
        self.assertIsNone(owner.current)

    def test_expiration_is_exclusive_and_handles_sleep_step_gaps(self):
        owner=open_owner(ttl=3)
        self.assertEqual(owner.observe(capture=capture(5),work_ref="charge:5").kind,"retained")
        self.assertEqual(owner.observe(capture=capture(6),work_ref="charge:6").kind,"expired")
        self.assertIsNone(owner.current)

    def test_replay_and_double_work_on_same_capture_refuse_atomically(self):
        owner=open_owner()
        before=owner.export_state()
        for wrong in (capture(3),capture(2),capture(4,ref="capture:3")):
            with self.subTest(wrong=wrong),self.assertRaises(ValueError):
                owner.observe(capture=wrong,work_ref="charge:4")
            self.assertEqual(owner.export_state(),before)

    def test_failed_proposal_cannot_replace_or_recharge_active_intent(self):
        owner=open_owner()
        before=owner.export_state()
        with self.assertRaises(ValueError):
            owner.open(capture=capture(4),semantic_ref=SEM,
                       evidence_ref="evidence:4",ttl_steps=4,work_ref="charge:4")
        self.assertEqual(owner.export_state(),before)

    def test_bad_frame_rejected_before_state_mutation(self):
        owner=open_owner()
        before=owner.export_state()
        bad=[FirstPersonCapture(True,"capture:4",GOAL,(SEM,)),
             FirstPersonCapture(4,"capture:4",GOAL,(SEM,SEM)),
             FirstPersonCapture(4,"capture:4",GOAL,(SEM,), (SEM,)),
             FirstPersonCapture(4,"capture:4",GOAL,[SEM]),
             FirstPersonCapture(4,"capture:4","",(SEM,)),
             FirstPersonCapture(4,"capture:4",GOAL,("zzz","aaa"))]
        for x in bad:
            with self.subTest(x=x),self.assertRaises(ValueError):
                owner.observe(capture=x,work_ref="charge:4")
            self.assertEqual(owner.export_state(),before)

    def test_plain_snapshot_roundtrip_does_not_claim_m11_recovery(self):
        owner=open_owner()
        owner.observe(capture=capture(4,visible=False),work_ref="charge:4")
        raw=json.loads(json.dumps(owner.export_state()))
        restored=IntentionContinuity.from_untrusted_snapshot(raw)
        self.assertEqual(owner.export_state(),restored.export_state())
        restored.observe(capture=capture(5),work_ref="charge:5")
        self.assertEqual(owner.current.status,"suspended")
        self.assertEqual(restored.current.status,"active")

    def test_snapshot_rejects_motor_smuggling_and_schema_errors(self):
        valid=open_owner().export_state()
        bad=[]
        v=copy.deepcopy(valid);v["winner"]="force_manger";bad.append(v)
        v=copy.deepcopy(valid);v["current"]["accumulator"]=1.0;bad.append(v)
        v=copy.deepcopy(valid);v["policy"]="another";bad.append(v)
        v=copy.deepcopy(valid);v["current"]["status"]="engaged";bad.append(v)
        v=copy.deepcopy(valid);v["current"]["last_checked_step"]=4;bad.append(v)
        v=copy.deepcopy(valid);v["current"]["expires_at_step"]=3;bad.append(v)
        v=copy.deepcopy(valid);v["last_step"]=999;bad.append(v)
        v=copy.deepcopy(valid);v["current"]["origin_evidence_ref"]="evidence:forged";bad.append(v)
        v=copy.deepcopy(valid);v["current"]["ref"]="intent:i2:fake";bad.append(v)
        v=copy.deepcopy(valid);del v["current"]["origin_evidence_ref"];bad.append(v)
        for v in bad:
            with self.subTest(v=v),self.assertRaises((ValueError,TypeError)):
                IntentionContinuity.from_untrusted_snapshot(v)

    def test_empty_owner_snapshot_clock_and_idle(self):
        owner=IntentionContinuity.from_untrusted_snapshot({
            "policy":POLICY,"last_step":-1,"last_capture_ref":None,"current":None})
        self.assertEqual(owner.observe(capture=capture(4),work_ref="charge:4").kind,"idle")
        self.assertIsNone(owner.current)
        self.assertEqual(owner.export_state()["last_step"],4)

    def test_snapshot_owner_clock_consistency(self):
        owner=open_owner()
        data=owner.export_state()
        data["last_capture_ref"]="capture:wrong"
        with self.assertRaises(ValueError):
            IntentionContinuity.from_untrusted_snapshot(data)

    def test_work_reference_is_a_syntactic_receipt_not_verified_uc(self):
        owner=open_owner()
        t=owner.observe(capture=capture(4),work_ref="external-unverified:4")
        self.assertEqual(t.work_ref,"external-unverified:4")
        self.assertNotIn("paid",owner.export_state())

if __name__=="__main__":
    unittest.main()