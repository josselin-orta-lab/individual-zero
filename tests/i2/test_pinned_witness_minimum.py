"""Pinned monotone witness regression checks remain synthetic only."""
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE,A,claim,ObservationPort,Values,Current,Safety,Terminal
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture, ZERO_HASH
from i2.modules.lifecycle_external_witness import (
    LatestWitness, WITNESS_SCHEMA, WitnessRefusal, compare_audit,
)
from i2.modules.uncertain_witness_inspection import inspect_uncertain_cognition_with_witness


def witness_from(report):
    return LatestWitness(
        WITNESS_SCHEMA,report["life_ref"],report["genesis_ref"],report["schema"],
        report["committed"],report["last_step"],report["chain_head"],
        report["terminal_ref"],report["terminal_step"],"proof:mock-only",
    )


class Mock:
    def __init__(self, record):
        self.record=record
        self.calls=0

    def read_verified_latest(self, *,life_ref,genesis_ref):
        self.calls+=1
        return self.record


class PinnedMinimumTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.path=Path(t.name)/"fixture.sqlite"
        self.source=ObservationPort()
        self.ports=dict(path=self.path,life_ref=LIFE,genesis_ref="genesis:pinned-floor",
                        observation_source=self.source,valuation_source=Values(),
                        current_source=Current(),safety_source=Safety(),
                        terminal_source=Terminal())
        self.owner=CognitiveCycleFixture.create(synthetic_uc=20,**self.ports)
        self.genesis=self.owner.audit()

    def inspect(self,c,remote,minimum=None):
        port=Mock(remote)
        return inspect_uncertain_cognition_with_witness(
            fixture=self.owner,witness=port,previous_count=0,
            previous_head=ZERO_HASH,claim=c,minimum_witness=minimum,
        )

    def test_complete_local_and_remote_rollback_needs_out_of_domain_minimum(self):
        # Simulated fully restored local and witness reports are mutually
        # consistent. Only a minimum saved OUTSIDE this rollback domain
        # distinguishes them from the historically newer pinned revision.
        old=self.genesis
        c=self.source.add(claim(3))
        self.owner.open(claim=c,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=12)
        advanced=witness_from(self.owner.audit())
        restored=witness_from(old)
        self.assertEqual(
            compare_audit(report=old,witness=Mock(restored)).status,
            "MATCHED_OPEN_INSPECTION",
        )
        with self.assertRaises(WitnessRefusal) as err:
            compare_audit(report=old,witness=Mock(restored),
                          minimum_witness=advanced)
        self.assertEqual(err.exception.reason,"STALE")

    def test_same_sequence_altered_head_is_equivocation(self):
        c=self.source.add(claim(3))
        self.owner.open(claim=c,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=12)
        current=witness_from(self.owner.audit())
        other=replace(current,chain_head="f"*64)
        with self.assertRaises(WitnessRefusal) as err:
            self.inspect(c,other,minimum=current)
        self.assertEqual(err.exception.reason,"FORK")

    def test_same_head_and_valid_advanced_minimum_remain_non_authorizing(self):
        c=self.source.add(claim(3))
        self.owner.open(claim=c,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=12)
        advanced=witness_from(self.owner.audit())
        result=self.inspect(c,advanced,minimum=advanced)
        self.assertEqual(result.local.outcome,"RECORDED_LOCAL_ONLY")
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)
        self.assertFalse(result.m11_authenticated)

    def test_foreign_and_invalid_minimum_rejected_before_provider(self):
        current=witness_from(self.genesis)
        for minimum in (replace(current,life_ref="life:other"),
                        replace(current,witness_schema="obsolete"),object()):
            with self.subTest(minimum=minimum):
                port=Mock(current)
                with self.assertRaises(ValueError):
                    compare_audit(report=self.genesis,witness=port,
                                  minimum_witness=minimum)
                self.assertEqual(port.calls,0)

    def test_extension_of_terminal_pinned_minimum_is_rejected(self):
        self.owner.seal_terminal(physical_step=0,terminal_ref="terminal:sealed",
                                 evidence_ref="evidence:sealed")
        terminal=witness_from(self.owner.audit())
        forged=replace(terminal,committed=terminal.committed+1,
                       last_step=terminal.last_step+1,chain_head="b"*64)
        with self.assertRaises(WitnessRefusal) as err:
            compare_audit(report=self.owner.audit(),witness=Mock(forged),
                          minimum_witness=terminal)
        self.assertEqual(err.exception.reason,"FORK")


if __name__=="__main__":
    unittest.main()
