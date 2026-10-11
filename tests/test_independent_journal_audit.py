"""Portable audit validates complete I0 history without relying on Oracle.

These are SOFTWARE tests of record consistency, never external world truth.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes, audit_export_file
from lab.journal import HashChainedJournal
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command


def record(journal, identifier, kind, *, step=1, attempt="a1", **extra):
    journal.append(
        event_id=identifier,
        causal_event={
            "kind": kind, "emitter": "test", "t_monde": step,
            "attempt_ref": attempt, **extra,
        },
    )


def stable_journal(*, death=False):
    journal = HashChainedJournal()
    record(journal, "open1", "step_opened", data={"attempt_index": 0})
    record(
        journal, "cmd1", "command_experienced",
        primitive="attendre", parameters={}, command_hash="commandhash",
    )
    record(
        journal, "transition1", "world_transition_experienced",
        position_after={"x": 2, "y": 2},
        body_after={"integrity": {"$f64": "0x1.9000000000000p+6"}},
        effects={},
    )
    if death:
        record(
            journal, "death1", "individual_death_confirmed",
            command_hash="commandhash", reasons=["lethal_zone"],
            position_after={"x": 2, "y": 2},
            body_after={"integrity": {"$f64": "0x1.9000000000000p+6"}},
        )
    else:
        record(
            journal, "auto1", "auto_segment_commit", event_refs=["cmd1", "transition1"],
            filter_version="stage2-autobio-v1",
        )
    record(
        journal, "close1", "step_closed",
        data={
            "outcome": "dead" if death else "normal",
            "applied_command_count": 1, "world_advance_count": 1,
        },
    )
    assert journal.verify()
    return journal


def reseal(rows):
    previous = "00" * 32
    for i, row in enumerate(rows):
        row["index"] = i
        row["previous_hash"] = previous
        content = canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })
        digest = sha256(bytes.fromhex(previous) + content).hexdigest()
        row["event_hash"] = digest
        previous = digest
    return b"\n".join(canonical_causal_bytes(row) for row in rows)



def valid_stage10_journal(*, stale_postcut=False):
    """One physically complete step with an actual-form consolidation receipt.

    This fixture checks exported record consistency; it does not reproduce the
    six scientific/semantic consolidation passes or claim real-world truth.
    """
    j = HashChainedJournal()
    record(j, "open1", "step_opened", emitter="scheduler", data={"attempt_index": 0})
    record(j, "cmd1", "command_experienced", command_hash="command-hash",
           primitive="attendre", parameters={})
    record(j, "physical1", "world_transition_experienced",
           position_after={"x": 2, "y": 2}, body_after={"water": 50}, effects={})
    record(j, "autobio1", "auto_segment_commit",
           event_refs=["cmd1", "physical1"], filter_version="stage2-autobio-v1")
    frozen_index = len(j.entries) - 1
    frozen_hash = j.head_hash
    if stale_postcut:
        record(j, "td-update-late", "td_update_published",
               emitter="value_needs", data={"delta": 1})
    activation_index = len(j.entries)
    record(
        j, "activation1", "stage10_consolidation_version_activated",
        emitter="scheduler",
        data={
            "source_history_version": "h:0",
            "new_history_version": "h:1",
            "consolidation_id": "c:1",
            "cut": {
                "world_step": 1, "journal_index": 0,
                "journal_event_id": "open1",
                "journal_hash": j.entries[0].event_hash,
                "history_version": "h:0",
            },
            "batch": ["episode1"],
            "batch_digest": "a" * 64,
            "candidate_digest": "b" * 64,
            "postcut_journal_end_index": frozen_index,
            "postcut_journal_end_hash": frozen_hash,
            "commit_index": activation_index,
        },
    )
    record(j, "close1", "step_closed", emitter="scheduler", data={
        "outcome": "normal", "applied_command_count": 1,
        "world_advance_count": 1,
    })
    assert j.verify()
    return j


class IndependentJournalAuditTests(unittest.TestCase):
    def test_ordinary_and_terminal_export_are_auditable_after_stopping(self):
        for dead in (False, True):
            with self.subTest(dead=dead):
                journal = stable_journal(death=dead)
                out = audit_export_bytes(
                    journal.canonical_bytes(),
                    expected_head=journal.head_hash,
                    expected_count=len(journal.entries),
                )
                self.assertEqual(out.occurrences, len(journal.entries))
                self.assertEqual(out.world_steps_closed, 1)
                self.assertEqual(out.terminal_deaths, int(dead))
                self.assertFalse(out.as_dict()["physical_truth_verified"])

    def test_alteration_middle_omission_duplicate_and_reorder_are_rejected(self):
        raw = stable_journal().canonical_bytes()
        rows = raw.split(b"\n")
        modified = list(rows)
        modified[1] = modified[1].replace(b"attendre", b"manger")
        corruptions = (
            b"\n".join(modified),
            b"\n".join(rows[:2] + rows[3:]),
            b"\n".join(rows[:2] + rows[1:]),
            b"\n".join([rows[1], rows[0]] + rows[2:]),
        )
        for example in corruptions:
            with self.subTest(description=example[:35]):
                with self.assertRaises(ValueError):
                    audit_export_bytes(example)

    def test_suffix_truncation_requires_independent_trusted_anchor(self):
        journal = stable_journal()
        truncated = b"\n".join(journal.canonical_bytes().split(b"\n")[:-1])
        # Without an externally retained head or count, a valid prefix may
        # still hash correctly; a complete world-step closure check catches
        # this particular truncation, but other valid prefixes may not.
        with self.assertRaises(ValueError):
            audit_export_bytes(
                truncated, expected_head=journal.head_hash,
                expected_count=len(journal.entries),
            )

    def test_rehashed_false_provenance_is_still_rejected(self):
        journal = stable_journal()
        rows = [json.loads(x) for x in journal.canonical_bytes().split(b"\n")]
        rows[3]["causal_event"]["event_refs"] = ["cmd1", "missing-id"]
        with self.assertRaisesRegex(ValueError, "source"):
            audit_export_bytes(reseal(rows))
        rows = [json.loads(x) for x in journal.canonical_bytes().split(b"\n")]
        rows[3]["causal_event"]["event_refs"] = ["cmd1", "cmd1"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit_export_bytes(reseal(rows))

    def test_oracle_event_is_not_a_permissible_internal_causal_record(self):
        j = stable_journal()
        record(j, "oracle-read", "oracle_read", step=2, attempt="a2", data={"truth": 1})
        with self.assertRaisesRegex(ValueError, "oracle"):
            audit_export_bytes(j.canonical_bytes())

    def test_postmortem_cognitive_event_is_rejected_even_if_hashes_match(self):
        j = stable_journal(death=True)
        record(j, "postmortem-cognition", "episode_closed", step=1, attempt="a1")
        self.assertTrue(j.verify())
        with self.assertRaisesRegex(ValueError, "after death"):
            audit_export_bytes(j.canonical_bytes())

    def test_stage10_false_cut_and_postcut_references_are_rejected(self):
        j = stable_journal()
        record(j, "bad-activation", "stage10_consolidation_version_activated",
               emitter="scheduler",
               data={
                   "source_history_version": "h:0",
                   "new_history_version": "h:1",
                   "consolidation_id": "c:1",
                   "batch": [], "batch_digest": "a" * 64,
                   "candidate_digest": "b" * 64,
                   "cut": {
                       "world_step": 1, "history_version": "h:0",
                       "journal_index": 0, "journal_event_id": "wrong",
                       "journal_hash": "deadbeef",
                   },
                   "postcut_journal_end_index": 4,
                   "postcut_journal_end_hash": j.entries[4].event_hash,
                   "commit_index": 5,
               })
        with self.assertRaisesRegex(ValueError, "cut"):
            audit_export_bytes(j.canonical_bytes())

    def test_nonlethal_commit_must_reference_the_actual_physical_result(self):
        journal = stable_journal()
        rows = [json.loads(raw) for raw in journal.canonical_bytes().split(b"\n")]
        rows[3]["causal_event"]["event_refs"] = ["cmd1"]
        # Even a recomputed valid chain cannot turn an incomplete lived-source
        # receipt into a genuinely committed command+transition pair.
        with self.assertRaisesRegex(ValueError, "omits command/transition"):
            audit_export_bytes(reseal(rows))

    def test_valid_stage10_cut_version_and_postcut_receipt(self):
        journal = valid_stage10_journal()
        result = audit_export_bytes(
            journal.canonical_bytes(), expected_head=journal.head_hash,
            expected_count=len(journal.entries),
        )
        self.assertEqual(result.consolidation_publications, 1)
        self.assertEqual(result.world_steps_closed, 1)
        self.assertEqual(result.autobiographical_commits, 1)

    def test_rehashed_stale_stage10_freeze_cannot_drop_postcut_learning(self):
        journal = valid_stage10_journal(stale_postcut=True)
        self.assertTrue(journal.verify())
        with self.assertRaisesRegex(ValueError, "latest causal head"):
            audit_export_bytes(journal.canonical_bytes())

    def test_rehashed_invalid_consolidation_history_lineage_is_rejected(self):
        journal = valid_stage10_journal()
        rows = [json.loads(raw) for raw in journal.canonical_bytes().split(b"\n")]
        cases = (
            ("source_history_version", "unrelated-history", "history version"),
            ("batch_digest", "not-a-sha256", "invalid digest"),
            ("new_history_version", "h:0", "version"),
        )
        for field, forged, message in cases:
            with self.subTest(field=field):
                modified = json.loads(json.dumps(rows))
                modified[4]["causal_event"]["data"][field] = forged
                with self.assertRaisesRegex(ValueError, message):
                    audit_export_bytes(reseal(modified))

    def test_operator_cli_runs_without_importing_i0_or_scientific_services(self):
        journal = stable_journal(death=True)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "life.jsonl"
            file.write_bytes(journal.canonical_bytes())
            script = (Path(__file__).resolve().parents[1]
                      / "scripts" / "verify_i0_journal.py")
            proc = subprocess.run(
                [sys.executable, str(script), str(file),
                 "--expected-head", journal.head_hash,
                 "--expected-count", str(len(journal.entries))],
                capture_output=True, text=True, timeout=25,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["terminal_deaths"], 1)
            blocked = subprocess.run(
                [sys.executable, "-c", r'''
import importlib.abc, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "i0" or name in ("lab.oracle", "lab.bench"):
            raise ImportError("forbidden import " + name)
        return None
sys.meta_path.insert(0, Block())
from lab.independent_journal_audit import audit_export_file
result = audit_export_file(Path(sys.argv[1]))
assert result.terminal_deaths == 1
assert "lab.oracle" not in sys.modules
assert "lab.bench" not in sys.modules
assert "i0" not in sys.modules
print("independent_audit:OK")
''', str(file), str(Path(__file__).resolve().parents[1] / "src")],
                capture_output=True, text=True, timeout=25,
            )
            self.assertEqual(blocked.returncode, 0, blocked.stderr)
            self.assertIn("independent_audit:OK", blocked.stdout)

    def test_six_hundred_real_physical_steps_preserve_full_auditable_log(self):
        runtime = build_stage4_reference_runtime()
        substrate = runtime.stage3.substrate
        substrate.enable_mortal_world()
        for _ in range(600):
            substrate.open_step()
            result = substrate.execute(Command("attendre"))
            self.assertEqual(result.status, "applied")
        self.assertEqual(runtime.scheduler.t_monde, 600)
        self.assertTrue(runtime.journal.verify())
        exported = runtime.journal.canonical_bytes()
        count = len(runtime.journal.entries)
        result = audit_export_bytes(
            exported, expected_head=runtime.journal.head_hash,
            expected_count=count,
        )
        self.assertEqual(result.world_steps_closed, 600)
        self.assertEqual(result.autobiographical_commits, 600)
        self.assertEqual(result.terminal_deaths, 0)
        self.assertEqual(result.occurrences, count)


if __name__ == "__main__":
    unittest.main()
