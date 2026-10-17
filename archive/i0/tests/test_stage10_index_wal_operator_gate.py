"""Independent read-only index WAL audit: terminal and provenance negative matrix.

Tests build small canonical journal fixtures only. No I0, Oracle, Bench or
WorldBody runtime is imported and a prefix is never eligible for recovery.
"""
import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_stage10_index_wal import verify


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def wal_of(events, folder):
    previous = "0" * 64
    entries = []
    for i, event in enumerate(events):
        eid = f"receipt:{i}"
        digest = sha256(bytes.fromhex(previous) + canonical({
            "event_id": eid, "causal_event": event,
        })).hexdigest()
        entries.append(canonical({
            "index": i, "event_id": eid,
            "previous_hash": previous, "event_hash": digest,
            "causal_event": event,
        }) + b"\n")
        previous = digest
    path = Path(folder) / "life.wal"
    path.write_bytes(b"".join(entries))
    return path


def step_open(t, ref):
    return {"kind": "step_opened", "emitter": "scheduler",
            "t_monde": t, "attempt_ref": ref}


def step_close(t, ref, outcome="normal"):
    return {"kind": "step_closed", "emitter": "scheduler",
            "t_monde": t, "attempt_ref": ref, "data": {
                "outcome": outcome, "world_advance_count": 1,
                "applied_command_count": 1}}


def stop():
    return {"kind": "experiment_stopped", "emitter": "operator_console",
            "t_monde": 2, "data": {"physical_death": False}}


def triplet(cid, version, refs):
    pay = {"kind": "stage10_consolidation_index_maintenance_charged",
           "t_monde": 1, "emitter": "stage10",
           "data": {"consolidation_id": cid, "episode_refs": refs,
                    "operation": "index_maintenance",
                    "count": len(refs), "requested_uc": len(refs),
                    "consumed_step_uc": len(refs),
                    "consumed_period_uc": len(refs),
                    "pending_before": 6, "source_history_version": "h:birth"}}
    h = {"kind": "stage10_consolidation_version_activated", "t_monde": 1,
         "emitter": "scheduler", "data": {
             "consolidation_id": cid, "batch": refs,
             "source_history_version": "h:birth",
             "new_history_version": version}}
    retire = {"kind": "stage10_consolidation_index_retired", "t_monde": 1,
              "emitter": "stage10", "data": {
                  "consolidation_id": cid, "episode_refs": refs,
                  "new_history_version": version,
                  "maintenance_charge_uc": len(refs),
                  "pending_after": 6 - len(refs)}}
    return pay, h, retire


class ReadOnlyWalTerminalTests(unittest.TestCase):
    def check(self, events, expected_complete, phrase=None):
        with TemporaryDirectory() as folder:
            result = verify(wal_of(events, folder))
        self.assertEqual(result["publication_boundary_complete"], expected_complete)
        self.assertIs(result["may_resume_stage12"], False)
        self.assertIs(result["recovery_certified"], False)
        if phrase:
            self.assertTrue(any(phrase in p for p in result["problems"]),
                            result["problems"])
        return result

    def test_valid_terminal_archive_and_no_runtime_recovery(self):
        events = [step_open(1, "attempt:1"), *triplet(
            "consolidation:1", "h:v1", ["episode:1", "episode:2"]),
            step_close(1, "attempt:1"), stop()]
        result = self.check(events, True)
        self.assertEqual(result["terminal_kind"], "experiment_stopped")
        self.assertEqual(result["indexed_retirements"], 1)

    def test_valid_prefix_after_closed_step_is_not_complete_life(self):
        self.check([step_open(1, "attempt:1"),
                    step_close(1, "attempt:1")], False,
                   "no terminal evidence")

    def test_terminal_stop_must_be_final(self):
        self.check([step_open(1, "attempt:1"),
                    step_close(1, "attempt:1"), stop(),
                    {"kind": "late_event", "emitter": "test", "t_monde": 2}],
                   False, "nonfinal operator stop")

    def test_repeated_operator_stop_is_incomplete(self):
        self.check([step_open(1, "attempt:1"),
                    step_close(1, "attempt:1"), stop(), stop()],
                   False, "repeated")

    def test_attempt_identity_and_nesting_fail_closed(self):
        self.check([step_open(1, "attempt:a"), step_open(2, "attempt:b"),
                    step_close(2, "attempt:b"), stop()],
                   False, "nested physical step")
        self.check([step_open(1, "attempt:a"),
                    step_close(1, "attempt:b"), stop()],
                   False, "invalid physical step closure")

    def test_republished_episode_fails_with_valid_hashes(self):
        events = [step_open(1, "attempt:1"),
                  *triplet("consolidation:1", "h:v1", ["episode:1"]),
                  *triplet("consolidation:2", "h:v2", ["episode:1"]),
                  step_close(1, "attempt:1"), stop()]
        self.check(events, False, "republished episode")

    def test_missing_retirement_fails_with_valid_hashes(self):
        pay, h, _ = triplet("consolidation:1", "h:v1", ["episode:1"])
        self.check([step_open(1, "attempt:1"), pay, h,
                    step_close(1, "attempt:1"), stop()],
                   False, "unfinished indexed publication")

    def test_duplicate_episode_in_one_charge_is_rejected(self):
        events = [step_open(1, "attempt:1"),
                  *triplet("consolidation:1", "h:v1",
                           ["episode:1", "episode:1"]),
                  step_close(1, "attempt:1"), stop()]
        self.check(events, False, "invalid index maintenance price")


if __name__ == "__main__":
    unittest.main()
