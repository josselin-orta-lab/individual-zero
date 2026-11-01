"""Read-only G2 diagnosis of uncertain local v5 COMMITs, never M11."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE, A, B, C, claim, ObservationPort, Values, Current, Safety, Terminal
from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost, FaultInjected, ZERO_HASH,
)


class UncertainLocalCommitTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "one-v5.sqlite"
        self.source = ObservationPort()
        self.values = Values()
        self.current = Current()
        self.safety = Safety()
        self.ports = dict(
            path=self.path, life_ref=LIFE, genesis_ref="genesis:uncertain-v5",
            observation_source=self.source, valuation_source=self.values,
            current_source=self.current, safety_source=self.safety,
            terminal_source=Terminal(),
        )
        self.fixture = CognitiveCycleFixture.create(synthetic_uc=20, **self.ports)

    def cold(self):
        return CognitiveCycleFixture.reopen(**self.ports)

    def inspect(self, c, count=0, head=ZERO_HASH, *,
                method="open", semantic_ref=A, evidence_ref=None, ttl_steps=12):
        if evidence_ref is None and method == "open":
            evidence_ref = f"evidence:{c.capture.step}"
        return self.cold().inspect_uncertain_cognition(
            previous_count=count, previous_head=head, claim=c,
            method=method, semantic_ref=semantic_ref,
            evidence_ref=evidence_ref, ttl_steps=ttl_steps,
        )

    def test_no_commit_is_absent_local_only_without_retry_permission(self):
        c = self.source.add(claim(3))
        before = self.fixture.audit()
        with self.assertRaises(FaultInjected):
            self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                              ttl_steps=12, _fault_at="before_commit")
        result = self.inspect(c)
        self.assertEqual(result.outcome, "ABSENT_LOCAL_ONLY")
        self.assertIsNone(result.recorded_event_head)
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)
        self.assertEqual(result.motor_authority, "NONE")
        self.assertEqual(self.fixture.audit(), before)

    def test_ack_loss_locates_exact_cognitive_event_without_reexecution(self):
        c = self.source.add(claim(3))
        with self.assertRaises(CommitAcknowledgmentLost):
            self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                              ttl_steps=12, _fault_at="after_commit")
        port_calls = (len(self.source.calls), len(self.values.calls),
                      len(self.current.calls), len(self.safety.calls))
        found = self.inspect(c)
        self.assertEqual(found.outcome, "RECORDED_LOCAL_ONLY")
        self.assertEqual(found.recorded_event_head, self.fixture.audit()["chain_head"])
        self.assertEqual(found.expected_seq, 1)
        self.assertFalse(found.retry_authorized)
        self.assertFalse(found.m11_authenticated)
        self.assertEqual(port_calls, (len(self.source.calls), len(self.values.calls),
                                     len(self.current.calls), len(self.safety.calls)))

    def test_wrong_attempt_or_forged_predecessor_conflicts(self):
        first = self.source.add(claim(3))
        self.fixture.open(claim=first, semantic_ref=A, evidence_ref="evidence:3",
                          ttl_steps=12)
        other = self.source.add(claim(4))
        self.assertEqual(self.inspect(other).outcome, "CONFLICT_LOCAL")
        prior = self.fixture.audit()
        self.assertEqual(self.inspect(first, count=1, head="a"*64).outcome,
                         "CONFLICT_LOCAL")
        self.assertEqual(self.inspect(other, count=1, head=prior["chain_head"]).outcome,
                         "ABSENT_LOCAL_ONLY")
        self.assertEqual(self.inspect(first, count=1, head=prior["chain_head"]).outcome,
                         "ABSENT_LOCAL_ONLY")


    def test_same_capture_different_intention_requests_are_not_found(self):
        c = self.source.add(claim(3))
        self.fixture.open(claim=c, semantic_ref=A, evidence_ref="evidence:3",
                          ttl_steps=12)
        before = (len(self.source.calls), len(self.values.calls),
                  len(self.current.calls), len(self.safety.calls))
        self.assertEqual(self.inspect(c).outcome, "RECORDED_LOCAL_ONLY")
        variants = (
            dict(method="observe", semantic_ref=None, evidence_ref=None, ttl_steps=None),
            dict(method="open", semantic_ref=B, evidence_ref="evidence:3", ttl_steps=12),
            dict(method="open", semantic_ref=A, evidence_ref="evidence:other", ttl_steps=12),
            dict(method="open", semantic_ref=A, evidence_ref="evidence:3", ttl_steps=11),
        )
        for attempted in variants:
            with self.subTest(attempted=attempted):
                result = self.cold().inspect_uncertain_cognition(
                    previous_count=0, previous_head=ZERO_HASH, claim=c, **attempted,
                )
                self.assertEqual(result.outcome, "CONFLICT_LOCAL")
                self.assertIsNone(result.recorded_event_head)
                self.assertFalse(result.retry_authorized)
                self.assertFalse(result.resumption_authorized)
        self.assertEqual(before, (len(self.source.calls), len(self.values.calls),
                                  len(self.current.calls), len(self.safety.calls)))

    def test_observe_attempt_is_distinct_from_open_on_same_capture(self):
        c = self.source.add(claim(3))
        self.fixture.observe(claim=c)
        self.assertEqual(self.inspect(c, method="observe", semantic_ref=None,
                                      evidence_ref=None, ttl_steps=None).outcome,
                         "RECORDED_LOCAL_ONLY")
        self.assertEqual(self.inspect(c).outcome, "CONFLICT_LOCAL")

    def test_invalid_inspection_request_refused_before_audit(self):
        c = self.source.add(claim(3))
        invalid = (
            dict(method="delete"),
            dict(method="observe", ttl_steps=12),
            dict(method="open", semantic_ref=A, evidence_ref="evidence:3", ttl_steps=True),
            dict(method="open", semantic_ref=A, evidence_ref="evidence:3", ttl_steps=None),
        )
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.cold().inspect_uncertain_cognition(
                    previous_count=0, previous_head=ZERO_HASH, claim=c, **values,
                )

    def test_terminal_lost_ack_is_only_locally_recorded(self):
        with self.assertRaises(CommitAcknowledgmentLost):
            self.fixture.seal_terminal(
                physical_step=3, terminal_ref="terminal:uncertain",
                evidence_ref="evidence:terminal", _fault_at="after_commit",
            )
        result = self.cold().inspect_uncertain_terminal(
            previous_count=0, previous_head=ZERO_HASH,
            physical_step=3, terminal_ref="terminal:uncertain",
            evidence_ref="evidence:terminal",
        )
        self.assertEqual(result.outcome, "RECORDED_LOCAL_ONLY")
        self.assertFalse(result.retry_authorized)
        self.assertFalse(result.resumption_authorized)
        mismatch = self.cold().inspect_uncertain_terminal(
            previous_count=0, previous_head=ZERO_HASH,
            physical_step=3, terminal_ref="terminal:uncertain",
            evidence_ref="evidence:other",
        )
        self.assertEqual(mismatch.outcome, "CONFLICT_LOCAL")

    def test_malformed_expected_inputs_refused(self):
        c = self.source.add(claim(3))
        invalid = ((True, ZERO_HASH), (0, "bad"), (-1, ZERO_HASH),
                   (0, "a"*64), (1, ZERO_HASH))
        for count, head in invalid:
            with self.subTest(count=count, head=head), self.assertRaises(ValueError):
                self.inspect(c, count=count, head=head)
        with self.assertRaises(ValueError):
            self.cold().inspect_uncertain_terminal(
                previous_count=0, previous_head=ZERO_HASH, physical_step=0,
                terminal_ref="capture:not-terminal", evidence_ref="evidence:x",
            )

if __name__ == "__main__":
    unittest.main()
