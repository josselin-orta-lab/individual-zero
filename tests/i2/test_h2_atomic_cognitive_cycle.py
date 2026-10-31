"""G2: H2 feedback, cognition and UC share one v5 SQLite COMMIT."""
from pathlib import Path
import sqlite3
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE,A,B,C,claim,ObservationPort,Values,Current,Safety,Terminal
from test_feedback_transition_contract import TransitionTests
from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture,FaultInjected,CommitAcknowledgmentLost,SCHEMA,
)
from i2.modules.delayed_credit_study import _feedback_memory_digest

class AtomicH2Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/"only-v5.sqlite"
        self.source=ObservationPort()
        self.values=Values()
        self.current=Current()
        self.safety=Safety()
        self.terminal=Terminal()
        self.ports=dict(life_ref=LIFE,observation_source=self.source,
                        valuation_source=self.values,current_source=self.current,
                        safety_source=self.safety,genesis_ref="genesis:test-h2-v5",
                        terminal_source=self.terminal)

    def make(self):
        return CognitiveCycleFixture.create(path=self.path,synthetic_uc=20,**self.ports)

    def record(self,step):
        c=self.source.add(claim(step,visible=(A,B,C)))
        return c

    def test_one_commit_and_cold_replay(self):
        fixture=self.make()
        old,update=TransitionTests().transition()
        # H2 data comes from a separate claimed life; it must be rejected
        with self.assertRaises(ValueError):
            fixture.open(claim=self.record(30),semantic_ref=A,evidence_ref="evidence:30",
                         ttl_steps=12,feedback_previous=old,feedback_update=update)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"],20)
        self.assertEqual(fixture.audit()["feedback_version"],0)

    def test_valid_same_life_atomic_and_ack_resolution(self):
        from dataclasses import replace
        old,update=TransitionTests().transition()
        # Build an independent test fixture with exactly the claimed synthetic life,
        # never a real WorldBody identity.
        self.ports["life_ref"]=old.life_ref
        class Subject:
            def verify(self,*,life_ref,claim,digest):return True
        self.ports["observation_source"]=Subject()
        f=self.make()
        from i2.modules.intention_ingress import ObservationClaim
        from i2.modules.intention_continuity import FirstPersonCapture
        c=ObservationClaim(old.life_ref,FirstPersonCapture(30,"capture:cycle30",old.goal_ref,
              tuple(sorted((A,B,C)))),"source:cycle30",("evidence:30",))
        with self.assertRaises(CommitAcknowledgmentLost):
            f.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12,
                   feedback_previous=old,feedback_update=update,_fault_at="after_commit")
        self.assertEqual(f.audit()["feedback_version"],1)
        self.assertEqual(CognitiveCycleFixture.reopen(path=self.path,**self.ports).audit()["feedback_version"],1)
        self.assertEqual(f.lookup(capture_ref="capture:cycle30").motor_authority,"NONE")
        with self.assertRaises(ValueError):
            f.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12,
                   feedback_previous=old,feedback_update=update)
        self.assertEqual(f.audit()["committed"],1)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],15)

    def test_crash_before_commit_rolls_back_feedback_and_uc(self):
        from i2.modules.intention_ingress import ObservationClaim
        from i2.modules.intention_continuity import FirstPersonCapture
        old,update=TransitionTests().transition()
        self.ports["life_ref"]=old.life_ref
        class Subject:
            def verify(self,*,life_ref,claim,digest):return True
        self.ports["observation_source"]=Subject()
        f=self.make()
        c=ObservationClaim(old.life_ref,FirstPersonCapture(30,"capture:cycle30",old.goal_ref,
              tuple(sorted((A,B,C)))),"source:cycle30",("evidence:30",))
        with self.assertRaises(FaultInjected):
            f.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12,
                   feedback_previous=old,feedback_update=update,_fault_at="before_commit")
        self.assertEqual(f.audit()["feedback_version"],0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],20)
        self.assertEqual(f.audit()["committed"],0)

    def test_empty_scorecard_is_read_only_and_nonmotor(self):
        f=self.make()
        before=f.audit()
        first=f.feedback_scorecard()
        second=CognitiveCycleFixture.reopen(path=self.path,**self.ports).feedback_scorecard()
        self.assertEqual(first,second)
        self.assertEqual(first["samples"],0)
        self.assertIsNone(first["adaptive_mae"])
        self.assertIsNone(first["historical_mae"])
        self.assertIsNone(first["persistence_mae"])
        self.assertEqual(first["motor_authority"],"NONE")
        self.assertFalse(first["m11_authenticated"])
        self.assertEqual(f.audit(),before)

    def test_v4_fixture_is_not_silently_migrated(self):
        f=self.make()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE identity SET schema_id=? WHERE id=1",
                         ("i2-unified-cognitive-lifecycle-fixture-v4",))
        with self.assertRaises(ValueError):
            CognitiveCycleFixture.reopen(path=self.path,**self.ports)

    def test_stored_feedback_snapshot_tampering_refused_by_cold_audit(self):
        from i2.modules.intention_ingress import ObservationClaim
        from i2.modules.intention_continuity import FirstPersonCapture
        old,update=TransitionTests().transition()
        self.ports["life_ref"]=old.life_ref
        class Subject:
            def verify(self,*,life_ref,claim,digest):return True
        self.ports["observation_source"]=Subject()
        f=self.make()
        c=ObservationClaim(old.life_ref,FirstPersonCapture(
            30,"capture:cycle30",old.goal_ref,tuple(sorted((A,B,C)))),
            "source:cycle30",("evidence:30",))
        f.open(claim=c,semantic_ref=A,evidence_ref="evidence:30",ttl_steps=12,
               feedback_previous=old,feedback_update=update)
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE feedback SET snapshot_json=NULL WHERE id=1")
        with self.assertRaisesRegex(ValueError,"H2 owner and replay journal diverge"):
            CognitiveCycleFixture.reopen(path=self.path,**self.ports)

if __name__=="__main__":unittest.main()
