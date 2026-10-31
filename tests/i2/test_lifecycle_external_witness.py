"""Synthetic external witness protocol. These are NOT real M11 proofs."""
from dataclasses import fields, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.lifecycle_external_witness import (  # noqa: E402
    LatestWitness, WitnessAudit, WITNESS_SCHEMA, LIFECYCLE_SCHEMA,
    ZERO_HASH, WitnessRefusal, compare_audit,
)

LIFE = "life:synthetic-witness"
GENESIS = "genesis:claimed-birth"
HEAD = "a" * 64


def report(*, count=4, head=HEAD, terminal=False):
    return {
        "schema": LIFECYCLE_SCHEMA, "life_ref": LIFE, "genesis_ref": GENESIS,
        "committed": count, "last_step": -1 if count == 0 else count + 5,
        "chain_head": ZERO_HASH if count == 0 else head,
        "synthetic_terminal": terminal,
        "terminal_ref": "terminal:synthetic-death" if terminal else None,
        "terminal_step": count + 5 if terminal else None,
        "m11_authenticated": False, "scheduler_uc_authenticated": False,
        "physiological_death_attested": False, "motor_authority": "NONE",
    }


def record(r=None):
    r = report() if r is None else r
    return LatestWitness(
        WITNESS_SCHEMA, r["life_ref"], r["genesis_ref"], r["schema"],
        r["committed"], r["last_step"], r["chain_head"],
        r["terminal_ref"], r["terminal_step"], "proof:synthetic-only",
    )


class FakeWitness:
    """Deliberately inadequate test double: no crypto or monotonic store."""

    def __init__(self, r=None, valid=True):
        self.latest_record = record() if r is None else r
        self.valid = valid
        self.calls = []

    def read_verified_latest(self, *, life_ref, genesis_ref):
        self.calls.append(("read_verified_latest", life_ref, genesis_ref))
        if self.valid is not True:
            raise ValueError("unverified synthetic latest record")
        return self.latest_record


class WitnessProtocolTests(unittest.TestCase):
    def test_classified_fail_closed_refusals_are_non_authorizing(self):
        cases = (
            ("STALE", report(count=2, head="b"*64), record(report(count=5, head="c"*64))),
            ("UNANCHORED", report(count=5, head="c"*64), record(report())),
            ("FORK", report(), record(report(head="c"*64))),
            ("UNKNOWN", report(), replace(record(), witness_schema="wrong")),
        )
        for reason, local, external in cases:
            with self.subTest(reason=reason):
                with self.assertRaises(WitnessRefusal) as result:
                    compare_audit(report=local, witness=FakeWitness(external))
                self.assertEqual(result.exception.reason, reason)
                self.assertNotIn("authorized", vars(result.exception))

    def test_invalid_external_proof_and_identity_classified_unknown(self):
        for witness in (
            FakeWitness(valid=False),
            FakeWitness(replace(record(), genesis_ref="genesis:foreign")),
            FakeWitness(replace(record(), committed=True)),
        ):
            with self.subTest(witness=witness), self.assertRaises(WitnessRefusal) as failure:
                compare_audit(report=report(), witness=witness)
            self.assertEqual(failure.exception.reason, "UNKNOWN")

    def test_legacy_split_read_verify_protocol_is_refused(self):
        class LegacyWitness:
            def read_latest(self, *, life_ref, genesis_ref):
                raise AssertionError("legacy read must not be called")
            def verify_latest(self, *, record):
                raise AssertionError("legacy proof must not be called")
        with self.assertRaisesRegex(ValueError, "atomic verified-latest"):
            compare_audit(report=report(), witness=LegacyWitness())

    def test_provider_failure_and_invalid_record_fail_closed(self):
        class BrokenWitness:
            def read_verified_latest(self, *, life_ref, genesis_ref):
                raise TimeoutError("remote latest-head unavailable")
        with self.assertRaises(WitnessRefusal) as failure:
            compare_audit(report=report(), witness=BrokenWitness())
        self.assertEqual(failure.exception.reason, "UNKNOWN")

    def test_matching_open_inspection_remains_nonmotor(self):
        witness = FakeWitness()
        result = compare_audit(report=report(), witness=witness)
        self.assertEqual(result.status, "MATCHED_OPEN_INSPECTION")
        self.assertEqual(result.committed, 4)
        self.assertEqual(result.motor_authority, "NONE")
        self.assertIs(result.resumption_authorized, False)
        self.assertIs(result.m11_authenticated, False)
        self.assertFalse({"execute", "admit", "permission", "command"} &
                         {f.name for f in fields(WitnessAudit)})
        self.assertEqual(witness.calls, [("read_verified_latest", LIFE, GENESIS)])

    def test_matching_terminal_is_inspection_not_rebirth(self):
        r = report(terminal=True)
        result = compare_audit(report=r, witness=FakeWitness(record(r)))
        self.assertEqual(result.status, "MATCHED_TERMINAL_INSPECTION")
        self.assertEqual(result.terminal_ref, "terminal:synthetic-death")
        self.assertFalse(result.resumption_authorized)
        self.assertEqual(result.motor_authority, "NONE")

    def test_matching_genesis_only_checkpoint(self):
        r = report(count=0)
        self.assertEqual(compare_audit(report=r, witness=FakeWitness(record(r))).committed, 0)

    def test_expired_old_copy_cannot_match_newer_external_head(self):
        old = report(count=2, head="b"*64)
        latest = report(count=5, head="c"*64, terminal=True)
        with self.assertRaisesRegex(ValueError, "stale local copy"):
            compare_audit(report=old, witness=FakeWitness(record(latest)))

    def test_old_unsealed_copy_cannot_override_terminal_witness(self):
        old = report(terminal=False)
        newer = report(count=5, head="b"*64, terminal=True)
        with self.assertRaisesRegex(ValueError, "stale local copy"):
            compare_audit(report=old, witness=FakeWitness(record(newer)))

    def test_same_count_new_hash_is_a_fork(self):
        local = report()
        other = report(head="c"*64)
        with self.assertRaisesRegex(ValueError, "fork"):
            compare_audit(report=local, witness=FakeWitness(record(other)))

    def test_unnotarized_local_extension_is_fail_closed(self):
        current = report(count=5, head="e"*64)
        witnessed = report(count=4)
        with self.assertRaisesRegex(ValueError, "unanchored local extension"):
            compare_audit(report=current, witness=FakeWitness(record(witnessed)))

    def test_matching_head_with_deleted_terminal_is_rejected(self):
        local = report(terminal=False)
        externally_terminal = report(terminal=True)
        with self.assertRaisesRegex(ValueError, "terminal closure"):
            compare_audit(report=local, witness=FakeWitness(record(externally_terminal)))

    def test_matching_head_with_invented_terminal_is_rejected(self):
        local = report(terminal=True)
        with self.assertRaisesRegex(ValueError, "terminal closure"):
            compare_audit(report=local, witness=FakeWitness(record(report())))

    def test_same_head_wrong_last_step_fails(self):
        w = replace(record(), last_step=11)
        with self.assertRaisesRegex(ValueError, "fork"):
            compare_audit(report=report(), witness=FakeWitness(w))

    def test_external_wrong_life_or_genesis_refused(self):
        for w in (replace(record(), life_ref="life:other"),
                  replace(record(), genesis_ref="genesis:other")):
            with self.subTest(w=w), self.assertRaisesRegex(ValueError, "another identity"):
                compare_audit(report=report(), witness=FakeWitness(w))

    def test_forged_or_unverified_proof_is_not_accepted(self):
        for valid in (False, 1, "true", None, [], object()):
            with self.subTest(valid=valid), self.assertRaisesRegex(ValueError, "unavailable or invalid"):
                compare_audit(report=report(), witness=FakeWitness(valid=valid))

    def test_no_port_does_not_fall_back_to_local_hash(self):
        for w in (None, object(), "witness", FakeWitness):
            with self.subTest(w=w), self.assertRaisesRegex(ValueError, "mandatory"):
                compare_audit(report=report(), witness=w)

    def test_stale_proof_not_pretended_fresh_by_library(self):
        witness = FakeWitness(valid=False)
        with self.assertRaises(ValueError):
            compare_audit(report=report(), witness=witness)
        self.assertEqual(len(witness.calls), 1)

    def test_invalid_record_type_fails_even_if_ports_return_true(self):
        for item in (None, {}, "proof", (record(),)):
            w = FakeWitness()
            w.latest_record = item
            with self.subTest(item=item), self.assertRaisesRegex(ValueError, "exact external witness"):
                compare_audit(report=report(), witness=w)

    def test_witness_strict_type_and_schema_checks(self):
        candidates = [
            replace(record(), witness_schema="another-protocol"),
            replace(record(), journal_schema="other-fixture"),
            replace(record(), committed=True),
            replace(record(), committed=-1),
            replace(record(), last_step=True),
            replace(record(), chain_head="A"*64),
            replace(record(), chain_head="x"*64),
            replace(record(), chain_head="a"*63),
            replace(record(), proof_ref="some proof with whitespace"),
            replace(record(), proof_ref=""),
            replace(record(), life_ref=""),
        ]
        for candidate in candidates:
            with self.subTest(witness=candidate), self.assertRaises(ValueError):
                compare_audit(report=report(), witness=FakeWitness(candidate))

    def test_terminal_witness_required_all_fields(self):
        candidates = [
            replace(record(), terminal_ref="terminal:t"),
            replace(record(), terminal_step=9),
            replace(record(), terminal_ref="bogus:r", terminal_step=9),
            replace(record(), terminal_ref="terminal:r", terminal_step=8),
            replace(record(), terminal_ref="terminal:r", terminal_step=True),
        ]
        for candidate in candidates:
            with self.subTest(witness=candidate), self.assertRaises(ValueError):
                compare_audit(report=report(), witness=FakeWitness(candidate))

    def test_no_events_requires_genesis_step_and_zero_head(self):
        r = report(count=0)
        for local in (dict(r, last_step=0), dict(r, chain_head="b"*64)):
            with self.subTest(local=local), self.assertRaises(ValueError):
                compare_audit(report=local, witness=FakeWitness(record(r)))
        for w in (replace(record(r), last_step=0),
                  replace(record(r), chain_head="a"*64)):
            with self.subTest(w=w), self.assertRaises(ValueError):
                compare_audit(report=r, witness=FakeWitness(w))

    def test_local_report_must_keep_synthetic_authority_flags(self):
        r=report()
        for key,value in (("motor_authority","ADMITTED"),
                          ("m11_authenticated",True),
                          ("scheduler_uc_authenticated",True),
                          ("physiological_death_attested",True)):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,"unauthorized real authority"):
                compare_audit(report=dict(r, **{key:value}), witness=FakeWitness())

    def test_local_report_invalid_schema_counts_and_terminal(self):
        r=report()
        cases=(dict(r,schema="v2"),dict(r,committed=True),
               dict(r,last_step=False),dict(r,chain_head="not-a-hash"),
               dict(r,synthetic_terminal=1),dict(r,terminal_step=3),
               dict(r,terminal_ref="terminal:unexpected"),
               dict(r,life_ref=""),dict(r,genesis_ref=""),)
        for item in cases:
            with self.subTest(item=item),self.assertRaises(ValueError):
                compare_audit(report=item,witness=FakeWitness())

    def test_terminal_step_required_to_match_last_step(self):
        r=report(terminal=True)
        r["terminal_step"]=3
        with self.assertRaisesRegex(ValueError,"terminal seal"):
            compare_audit(report=r, witness=FakeWitness(record(report(terminal=True))))

    def test_missing_witness_latest_propagates_without_retry(self):
        w=FakeWitness()
        def broken(*,life_ref,genesis_ref):
            raise RuntimeError("unavailable independent store")
        w.read_verified_latest=broken
        with self.assertRaisesRegex(WitnessRefusal, "unavailable or invalid"):
            compare_audit(report=report(), witness=w)
        self.assertEqual(w.calls,[])


if __name__ == "__main__":
    unittest.main()
