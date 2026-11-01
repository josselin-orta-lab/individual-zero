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
        # A lost acknowledgement must identify the exact atomic H2 content,
        # not just a matching capture and 'open' request. No port is recalled.
        from i2.modules.uncertain_witness_inspection import inspect_uncertain_cognition_with_witness
        from i2.modules.lifecycle_external_witness import WitnessRefusal
        from test_feedback_calibration import (
            Source as FeedbackSource, heldout, forecast, read_feedback, learn_from_feedback,
        )
        from i2.modules.cognitive_cycle_fixture import ZERO_HASH
        cold = CognitiveCycleFixture.reopen(path=self.path, **self.ports)
        expected = dict(
            previous_count=0, previous_head=ZERO_HASH, claim=c,
            method="open", semantic_ref=A, evidence_ref="evidence:30",
            ttl_steps=12,
        )
        start = cold.audit()
        found = cold.inspect_uncertain_cognition(
            **expected, feedback_previous=old, feedback_update=update)
        self.assertEqual(found.outcome, "RECORDED_LOCAL_ONLY")
        self.assertFalse(found.retry_authorized)
        self.assertFalse(found.resumption_authorized)
        self.assertFalse(found.m11_authenticated)
        self.assertEqual(cold.inspect_uncertain_cognition(**expected).outcome,
                         "CONFLICT_LOCAL")
        readout = read_feedback(
            memory=old, forecast=forecast(10), source=FeedbackSource())
        a, b = heldout(12, -7, 4)
        another = learn_from_feedback(
            memory=old, readout=readout,
            prepared=a, control=b, source=FeedbackSource())
        self.assertNotEqual(update.heldout_score, another.heldout_score)
        self.assertEqual(cold.inspect_uncertain_cognition(
            **expected, feedback_previous=old, feedback_update=another).outcome,
            "CONFLICT_LOCAL")
        with self.assertRaisesRegex(ValueError, "both predecessor and update"):
            cold.inspect_uncertain_cognition(**expected, feedback_previous=old)
        with self.assertRaisesRegex(ValueError, "both predecessor and update"):
            cold.inspect_uncertain_cognition(**expected, feedback_update=update)

        class NeverContact:
            calls = 0

            def read_verified_latest(self, *, life_ref, genesis_ref):
                self.calls += 1
                raise AssertionError("foreign witness must not be contacted")

        witness = NeverContact()
        with self.assertRaises(WitnessRefusal) as exc:
            inspect_uncertain_cognition_with_witness(
                fixture=cold, witness=witness, **expected,
                feedback_previous=old, feedback_update=another)
        self.assertEqual(exc.exception.reason, "UNKNOWN")
        self.assertEqual(witness.calls, 0)
        self.assertEqual(cold.audit(), start)
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


    def test_cold_replay_rejects_cross_life_h2_even_with_consistent_hashes(self):
        from dataclasses import replace
        from i2.modules.cognitive_cycle_fixture import (
            ZERO_HASH, _chain, _json, _h2_transition_map, _h2_memory_map,
        )
        from i2.modules.feedback_transition_contract import verify_feedback_transition
        from i2.modules.intention_ingress import ObservationClaim
        from i2.modules.intention_continuity import FirstPersonCapture

        old, update = TransitionTests().transition()
        self.ports["life_ref"] = old.life_ref

        class Subject:
            def verify(self, *, life_ref, claim, digest):
                return True

        self.ports["observation_source"] = Subject()
        fixture = self.make()
        c = ObservationClaim(
            old.life_ref,
            FirstPersonCapture(30, "capture:cycle30", old.goal_ref,
                               tuple(sorted((A, B, C)))),
            "source:cycle30", ("evidence:30",),
        )
        fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:30",
                     ttl_steps=12, feedback_previous=old, feedback_update=update)

        # Reforge both the H2 transition and its local SHA chain. This
        # locally consistent H2 history belongs to another claimed life
        # than the SQLite cognitive owner and first-person capture.
        foreign = "life:foreign-replay"
        previous = replace(old, life_ref=foreign)
        next_memory = replace(update.new_memory, life_ref=foreign)
        score = replace(update.heldout_score, life_ref=foreign)
        altered = replace(update, new_memory=next_memory, heldout_score=score)
        verify_feedback_transition(
            stored=previous,
            expected_previous_digest=_feedback_memory_digest(previous),
            update=altered,
        )
        with sqlite3.connect(self.path) as conn:
            row = conn.execute("SELECT event_json FROM events WHERE seq=1").fetchone()
            event = json.loads(row[0])
            event["feedback_transition"] = _h2_transition_map(previous, altered)
            body = _json(event)
            head = _chain(ZERO_HASH, body)
            conn.execute("UPDATE events SET event_json=?, event_hash=? WHERE seq=1",
                         (body, head))
            conn.execute("UPDATE account SET chain_head=? WHERE id=1", (head,))
            conn.execute("UPDATE feedback SET snapshot_json=? WHERE id=1",
                         (_json(_h2_memory_map(next_memory)),))

        with self.assertRaisesRegex(ValueError, "foreign H2 life"):
            CognitiveCycleFixture.reopen(path=self.path, **self.ports)

if __name__=="__main__":unittest.main()
