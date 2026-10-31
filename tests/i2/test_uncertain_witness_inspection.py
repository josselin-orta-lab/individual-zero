"""Only inspect uncertain G2 SQLite events alongside an injected witness."""
from dataclasses import fields
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE, A, claim, ObservationPort, Values, Current, Safety, Terminal
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture, ZERO_HASH, CommitAcknowledgmentLost
from i2.modules.lifecycle_external_witness import LatestWitness, WITNESS_SCHEMA, WitnessRefusal
from i2.modules.uncertain_witness_inspection import (
    UncertainWitnessInspection, inspect_uncertain_cognition_with_witness,
    inspect_uncertain_terminal_with_witness,
)


class TestUncertainWitness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "one.sqlite"
        self.source = ObservationPort()
        self.ports = dict(
            path=self.path, life_ref=LIFE, genesis_ref="genesis:uncertain-witness",
            observation_source=self.source, valuation_source=Values(),
            current_source=Current(), safety_source=Safety(),
            terminal_source=Terminal(),
        )
        self.fixture = CognitiveCycleFixture.create(synthetic_uc=20, **self.ports)

    def witness(self, *, record=None, fail=False, on_read=None):
        class FakeWitness:
            def __init__(self, value):
                self.value = value
                self.calls = 0

            def read_verified_latest(self, *, life_ref, genesis_ref):
                self.calls += 1
                if on_read is not None:
                    on_read()
                if fail:
                    raise TimeoutError("external unavailable")
                return self.value

        report = self.fixture.audit()
        return FakeWitness(record if record is not None else LatestWitness(
            WITNESS_SCHEMA, report["life_ref"], report["genesis_ref"],
            report["schema"], report["committed"], report["last_step"],
            report["chain_head"], report["terminal_ref"],
            report["terminal_step"], "proof:test-only",
        ))

    def inspection(self, c, witness, *, count=0, head=ZERO_HASH):
        return inspect_uncertain_cognition_with_witness(
            fixture=self.fixture, witness=witness,
            previous_count=count, previous_head=head, claim=c,
        )

    def test_lost_ack_correlated_without_permissions_or_port_reexecution(self):
        c = self.source.add(claim(3))
        with self.assertRaises(CommitAcknowledgmentLost):
            self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                              ttl_steps=12, _fault_at="after_commit")
        calls = len(self.source.calls)
        w = self.witness()
        result = self.inspection(c, w)
        self.assertIs(type(result), UncertainWitnessInspection)
        self.assertEqual(result.local.outcome, "RECORDED_LOCAL_ONLY")
        self.assertEqual(result.witness.status, "MATCHED_OPEN_INSPECTION")
        self.assertEqual(w.calls, 1)
        self.assertEqual(len(self.source.calls), calls)
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)
        self.assertFalse(result.m11_authenticated)
        self.assertEqual(result.motor_authority, "NONE")
        self.assertFalse({"command", "admit", "dispatch"} &
                         {field.name for field in fields(result)})

    def test_absent_locally_and_witnessed_genesis_never_permits_retry(self):
        c = self.source.add(claim(3))
        result = self.inspection(c, self.witness())
        self.assertEqual(result.local.outcome, "ABSENT_LOCAL_ONLY")
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)

    def test_wrong_attempt_rejected_before_witness_contact(self):
        first = self.source.add(claim(3))
        self.fixture.open(claim=first, semantic_ref=A, evidence_ref="evidence:3",
                          ttl_steps=12)
        bad = self.source.add(claim(4))
        w = self.witness()
        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(bad, w)
        self.assertEqual(exc.exception.reason, "UNKNOWN")
        self.assertEqual(w.calls, 0)

    def test_local_ahead_is_unanchored_not_resolved(self):
        c = self.source.add(claim(3))
        old = self.witness().value
        self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                          ttl_steps=12)
        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(c, self.witness(record=old))
        self.assertEqual(exc.exception.reason, "UNANCHORED")

    def test_external_ahead_is_stale_local(self):
        c = self.source.add(claim(3))
        old = self.witness().value
        later = replace(old, committed=1, last_step=3, chain_head="a" * 64)
        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(c, self.witness(record=later))
        self.assertEqual(exc.exception.reason, "STALE")

    def test_equal_sequence_different_head_is_fork(self):
        c = self.source.add(claim(3))
        self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                          ttl_steps=12)
        current = self.witness().value
        other = replace(current, chain_head="f"*64)
        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(c, self.witness(record=other))
        self.assertEqual(exc.exception.reason, "FORK")

    def test_witness_failure_is_unknown_not_local_fallback(self):
        c = self.source.add(claim(3))
        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(c, self.witness(fail=True))
        self.assertEqual(exc.exception.reason, "UNKNOWN")

    def test_concurrent_local_terminal_change_overrides_stale_witness_result(self):
        c = self.source.add(claim(3))
        origin = self.witness().value

        def seal():
            self.fixture.seal_terminal(physical_step=4, terminal_ref="terminal:race",
                                       evidence_ref="evidence:race")

        with self.assertRaises(WitnessRefusal) as exc:
            self.inspection(c, self.witness(record=origin, on_read=seal))
        self.assertEqual(exc.exception.reason, "UNKNOWN")
        self.assertTrue(self.fixture.audit()["synthetic_terminal"])

    def test_terminal_ack_loss_is_corroborated_only_locally(self):
        with self.assertRaises(CommitAcknowledgmentLost):
            self.fixture.seal_terminal(
                physical_step=3, terminal_ref="terminal:uncertain",
                evidence_ref="evidence:terminal", _fault_at="after_commit",
            )
        result = inspect_uncertain_terminal_with_witness(
            fixture=self.fixture, witness=self.witness(),
            previous_count=0, previous_head=ZERO_HASH,
            physical_step=3, terminal_ref="terminal:uncertain",
            evidence_ref="evidence:terminal",
        )
        self.assertEqual(result.local.outcome, "RECORDED_LOCAL_ONLY")
        self.assertEqual(result.witness.status, "MATCHED_TERMINAL_INSPECTION")
        self.assertFalse(result.resumption_authorized)
        self.assertFalse(result.retry_authorized)


if __name__ == "__main__":
    unittest.main()
