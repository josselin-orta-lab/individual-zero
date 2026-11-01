"""Adversarial same-snapshot I2 witness ancestry for uncertain commits."""
from pathlib import Path
import sys
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE,A,claim,ObservationPort,Values,Current,Safety,Terminal
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture,ZERO_HASH
from i2.modules.lifecycle_external_witness import LatestWitness,WITNESS_SCHEMA,WitnessRefusal
from i2.modules.uncertain_witness_inspection import inspect_uncertain_cognition_with_witness,inspect_uncertain_terminal_with_witness

def checkpoint(x):
    return LatestWitness(WITNESS_SCHEMA,x["life_ref"],x["genesis_ref"],x["schema"],
                         x["committed"],x["last_step"],x["chain_head"],
                         x["terminal_ref"],x["terminal_step"],"proof:synthetic")
class Witness:
    def __init__(self,record,on_read=None):
        self.record=record
        self.on_read=on_read
        self.calls=0
    def read_verified_latest(self,*,life_ref,genesis_ref):
        self.calls+=1
        if self.on_read is not None:
            self.on_read()
        return self.record
class AncestryTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.source=ObservationPort()
        self.ports=dict(life_ref=LIFE,genesis_ref="genesis:uncertain-prefix",
                        observation_source=self.source,valuation_source=Values(),
                        current_source=Current(),safety_source=Safety(),terminal_source=Terminal())
    def make(self,name):
        return CognitiveCycleFixture.create(path=self.root/name,synthetic_uc=20,**self.ports)
    def write(self,f,step,semantic=A):
        c=self.source.add(claim(step))
        f.open(claim=c,semantic_ref=semantic,evidence_ref=f"evidence:{step}",ttl_steps=12)
        return c
    def check(self,f,c,w,floor,count=0,head=ZERO_HASH):
        return inspect_uncertain_cognition_with_witness(
            fixture=f,witness=w,previous_count=count,previous_head=head,
            claim=c,method="open",semantic_ref=A,
            evidence_ref=f"evidence:{c.capture.step}",ttl_steps=12,
            minimum_witness=floor)
    def test_same_latest_head_can_hide_different_ancestor(self):
        a=self.make("a.sqlite")
        b=self.make("b.sqlite")
        self.write(a,3)
        floor=checkpoint(a.audit())
        self.write(b,3,semantic="affordance:eat:berry_a")
        c=self.write(b,4)
        w=Witness(checkpoint(b.audit()))
        with self.assertRaises(WitnessRefusal) as x:
            self.check(b,c,w,floor,count=1,head=b.audited_local_prefix(committed=1).prefix_head)
        self.assertEqual(x.exception.reason,"FORK")
        self.assertEqual(w.calls,0)
    def test_valid_cognitive_prefix_remains_non_authorizing(self):
        f=self.make("valid.sqlite")
        self.write(f,3)
        floor=checkpoint(f.audit())
        c=self.write(f,4)
        prior=f.audited_local_prefix(committed=1)
        w=Witness(checkpoint(f.audit()))
        result=self.check(f,c,w,floor,count=1,head=prior.prefix_head)
        self.assertEqual(result.local.outcome,"RECORDED_LOCAL_ONLY")
        self.assertEqual(result.local.audited_prefix.prefix_head,floor.chain_head)
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)
        self.assertEqual(w.calls,1)
    def test_terminal_prefix_and_concurrent_change(self):
        f=self.make("terminal.sqlite")
        self.write(f,3)
        floor=checkpoint(f.audit())
        f.seal_terminal(physical_step=4,terminal_ref="terminal:done",evidence_ref="evidence:done")
        result=inspect_uncertain_terminal_with_witness(
            fixture=f,witness=Witness(checkpoint(f.audit())),
            previous_count=1,previous_head=floor.chain_head,
            physical_step=4,terminal_ref="terminal:done",evidence_ref="evidence:done",
            minimum_witness=floor)
        self.assertEqual(result.local.outcome,"RECORDED_LOCAL_ONLY")
        self.assertFalse(result.retry_authorized)
    def test_invalid_minimum_refused_before_probing_or_external_read(self):
        f=self.make("invalid-floor.sqlite")
        c=self.source.add(claim(3))
        w=Witness(checkpoint(f.audit()))
        for invalid in (object(), "not-a-witness", True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.check(f,c,w,invalid)
            with self.subTest(terminal=invalid), self.assertRaises(ValueError):
                inspect_uncertain_terminal_with_witness(
                    fixture=f,witness=w,previous_count=0,previous_head=ZERO_HASH,
                    physical_step=3,terminal_ref="terminal:test",evidence_ref="evidence:test",
                    minimum_witness=invalid,
                )
        from dataclasses import replace
        foreign=replace(checkpoint(f.audit()),life_ref="life:foreign")
        with self.assertRaises(ValueError):
            self.check(f,c,w,foreign)
        self.assertEqual(w.calls,0)
        self.assertEqual(f.audit()["committed"],0)

    def test_local_refusal_race_requires_final_audit_before_classification(self):
        # Compare each stable local refusal with an identical read where
        # another writer seals the fixture after local_probe returned.
        # There is no external witness contact in any of these cases.
        for case in ("STALE", "FORK", "CONFLICT_LOCAL"):
            with self.subTest(case=case):
                f = self.make(f"early-{case.lower()}.sqlite")
                floor = None
                previous_count, previous_head = 0, ZERO_HASH
                if case == "STALE":
                    c = self.source.add(claim(3))
                    floor = LatestWitness(
                        WITNESS_SCHEMA, f.life_ref, f.genesis_ref, f.schema,
                        1, 3, "a" * 64, None, None, "proof:synthetic",
                    )
                else:
                    self.write(f, 3)
                    c = self.source.add(claim(4))
                    if case == "FORK":
                        floor = replace(checkpoint(f.audit()), chain_head="f" * 64)
                        previous_count, previous_head = (
                            f.audit()["committed"], f.audit()["chain_head"]
                        )
                w = Witness(checkpoint(f.audit()))
                with self.assertRaises(WitnessRefusal) as stable:
                    self.check(f, c, w, floor,
                               count=previous_count, head=previous_head)
                self.assertEqual(stable.exception.reason,
                                 case if case != "CONFLICT_LOCAL" else "UNKNOWN")
                self.assertEqual(w.calls, 0)

                original = f.inspect_uncertain_cognition

                def probe_then_seal(**kwargs):
                    snapshot = original(**kwargs)
                    f.seal_terminal(
                        physical_step=5,
                        terminal_ref=f"terminal:race:{case.lower()}",
                        evidence_ref="evidence:done",
                    )
                    return snapshot

                with patch.object(CognitiveCycleFixture, "inspect_uncertain_cognition",
                                  side_effect=probe_then_seal):
                    with self.assertRaises(WitnessRefusal) as raced:
                        self.check(f, c, w, floor,
                                   count=previous_count, head=previous_head)
                self.assertEqual(raced.exception.reason, "UNKNOWN")
                self.assertIn("changed during uncertain inspection",
                              str(raced.exception))
                self.assertEqual(w.calls, 0)
                self.assertTrue(f.audit()["synthetic_terminal"])

    def test_local_probe_exception_still_checks_concurrent_journal_change(self):
        f = self.make("probe-error-race.sqlite")
        c = self.source.add(claim(3))
        w = Witness(checkpoint(f.audit()))

        def faulty_probe(**kwargs):
            f.seal_terminal(
                physical_step=5, terminal_ref="terminal:probe-error",
                evidence_ref="evidence:done",
            )
            raise ValueError("rejected local request during concurrent write")

        with patch.object(CognitiveCycleFixture, "inspect_uncertain_cognition",
                          side_effect=faulty_probe):
            with self.assertRaises(WitnessRefusal) as raced:
                self.check(f, c, w, None)
        self.assertEqual(raced.exception.reason, "UNKNOWN")
        self.assertIn("changed during uncertain inspection",
                      str(raced.exception))
        self.assertEqual(w.calls, 0)
        self.assertTrue(f.audit()["synthetic_terminal"])

    def test_provider_race_is_unknown_even_after_valid_prefix(self):
        f=self.make("race.sqlite")
        c=self.write(f,3)
        floor=checkpoint(f.audit())
        old=checkpoint(f.audit())
        def seal():
            f.seal_terminal(physical_step=4,terminal_ref="terminal:race",evidence_ref="evidence:race")
        with self.assertRaises(WitnessRefusal) as x:
            self.check(f,c,Witness(old,on_read=seal),floor)
        self.assertEqual(x.exception.reason,"UNKNOWN")
if __name__=="__main__":
    unittest.main()
