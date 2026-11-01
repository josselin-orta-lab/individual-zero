"""G2 local ancestry verification against an externally supplied pinned head."""
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE,A,claim,ObservationPort,Values,Current,Safety,Terminal
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.lifecycle_external_witness import (
    LatestWitness,WITNESS_SCHEMA,WitnessRefusal,verify_fixture,
)

def pinned(report):
    return LatestWitness(WITNESS_SCHEMA,report["life_ref"],report["genesis_ref"],
                         report["schema"],report["committed"],report["last_step"],
                         report["chain_head"],report["terminal_ref"],
                         report["terminal_step"],"proof:lab-only")

class Provider:
    def __init__(self, latest):
        self.latest=latest
        self.calls=0
    def read_verified_latest(self, *, life_ref, genesis_ref):
        self.calls+=1
        return self.latest

class LocalAncestryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source=ObservationPort()
        self.ports=dict(life_ref=LIFE,genesis_ref="genesis:ancestry",
                        observation_source=self.source,valuation_source=Values(),
                        current_source=Current(),safety_source=Safety(),
                        terminal_source=Terminal())

    def make(self,name):
        return CognitiveCycleFixture.create(
            path=Path(self.tmp.name)/name,synthetic_uc=20,**self.ports)

    def write(self,fixture,step,semantic=A):
        c=self.source.add(claim(step))
        return fixture.open(claim=c,semantic_ref=semantic,
                            evidence_ref=f"evidence:{step}",ttl_steps=12)

    def test_local_head_matches_provider_but_forks_from_pinned_ancestor(self):
        first=self.make("first.sqlite")
        second=self.make("second.sqlite")
        self.write(first,3)
        ancestor=pinned(first.audit())
        self.write(second,3,semantic="affordance:eat:berry_a")
        self.write(second,4)
        latest=Provider(pinned(second.audit()))
        self.assertNotEqual(ancestor.chain_head,second.audited_local_prefix(committed=1).prefix_head)
        with self.assertRaises(WitnessRefusal) as err:
            verify_fixture(fixture=second,witness=latest,minimum_witness=ancestor)
        self.assertEqual(err.exception.reason,"FORK")
        self.assertEqual(latest.calls,0)
        self.assertFalse(second.audit()["m11_authenticated"])

    def test_valid_prefix_still_non_authorizing(self):
        f=self.make("valid.sqlite")
        self.write(f,3)
        ancestor=pinned(f.audit())
        self.write(f,4)
        result=verify_fixture(fixture=f,witness=Provider(pinned(f.audit())),
                              minimum_witness=ancestor)
        self.assertEqual(result.status,"MATCHED_OPEN_INSPECTION")
        self.assertEqual(result.motor_authority,"NONE")
        self.assertFalse(result.resumption_authorized)

    def test_cold_prefix_zero_and_out_of_range(self):
        f=self.make("empty.sqlite")
        zero=f.audited_local_prefix(committed=0)
        self.assertEqual(zero.prefix_head,"0"*64)
        self.assertIsNone(f.audited_local_prefix(committed=1).prefix_head)
        for invalid in (True,-1,"1"):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                f.audited_local_prefix(committed=invalid)

if __name__=="__main__":
    unittest.main()
