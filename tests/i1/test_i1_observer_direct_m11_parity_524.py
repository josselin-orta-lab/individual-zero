"""#524: first-divergence audit for observed/direct/cold natural M11 births."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ObservedDirectM11Parity524(unittest.TestCase):
    def test_operator_observation_cannot_change_lived_site_trace(self):
        with TemporaryDirectory() as temp:
            generated = Path(temp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], text=True, capture_output=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import execute, load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1lab.determinism import canonical_causal_bytes, sha256_hex

preset, digest = load_preset("empty-land")
params, _ = _birth_parameters(preset)
life_id = "i1:preset:empty-land:246:0"

def cold_factory():
    return I1Runtime(
        birth_life_id=life_id, autonomous_mortal=True, m11_sqlite_custody=True,
        wal_path=None, diagnostic_sample_cost_uc=1,
        module_occupancy_cost_uc=1, **params,
    )

def memory_digest(rt):
    return sha256_hex(canonical_causal_bytes(rt.memory.export_causal_state()))

def recalled(rt):
    return tuple(
        (entry.causal_event["t_monde"], entry.causal_event.get("cycle"),
         entry.causal_event["data"])
        for entry in rt.journal.entries
        if entry.causal_event.get("kind") == "i1_sleep_site_recall_consulted"
    )

def compare_one(actor, observed, label):
    rt = actor._runtime
    count = rt.journal.entry_count
    receipt = actor.run_step()
    new_events = [entry.causal_event
                  for entry in rt.journal.entries_since(count)]
    commands = [row for row in new_events
                if row.get("kind") == "command_experienced"]
    if len(commands) > 1:
        raise AssertionError("multiple applied commands in one M11 generation")
    primitive = None if not commands else commands[0]["primitive"]
    physical = observed["physical_journal_observation"]
    expected = {
        "generation": observed["generation"],
        "world_step": observed["world_step"],
        "status": observed["lifecycle"],
        "journal_head": observed["journal_head"],
        "primitive": None if physical is None else physical["primitive"],
        "position": observed["position_after"],
        "body": observed["body_after"],
    }
    actual = {
        "generation": receipt.generation,
        "world_step": receipt.world_step,
        "status": receipt.status,
        "journal_head": receipt.journal_head,
        "primitive": primitive,
        "position": rt.world.position.as_dict(),
        "body": dict(rt.world.telemetry()),
    }
    if actual != expected:
        print("I1_524_FIRST_DIVERGENCE", label,
              "step", receipt.generation,
              "observed", expected, "direct", actual,
              "memory_sha256", memory_digest(rt), flush=True)
        raise AssertionError("operator/direct M11 generation mismatch")
    return receipt

def verify_recalled(rt):
    memory = rt.memory.export_causal_state()
    closed = {ref for episode in memory["episodes"]
              for ref in episode["event_refs"]}
    commits = {ref for entry in rt.journal.entries
               if entry.causal_event.get("kind") == "auto_segment_commit"
               for ref in entry.causal_event["event_refs"]}
    rows = recalled(rt)
    sleep_refs, wait_refs, paired = set(), set(), 0
    for _, _, row in rows:
        assert row["charged_operation"] == "i1_closed_sleep_recall"
        assert row["evidence_applied"] is False
        assert row["wait_decision_evidence"] is False
        assert row["wait_causal_attribution"] is False
        assert len(row["wait_event_refs"]) == 2*row["wait_witness_count"]
        assert len(row["event_refs"]) == 2*row["witness_count"]
        sleep_refs.update(row["event_refs"])
        wait_refs.update(row["wait_event_refs"])
        paired += bool(row["wait_witness_count"] and row["witness_count"])
    assert not (sleep_refs & wait_refs)
    assert sleep_refs <= closed <= commits
    assert wait_refs <= closed
    return rows, frozenset(sleep_refs), frozenset(wait_refs), paired

with TemporaryDirectory() as temp:
    root = Path(temp)
    report = execute(
        preset_name="empty-land", seed=246, steps=55, lives=1,
        custody="m11", output_dir=root/"operator",
    )
    assert report["status"] == "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
    life = report["lives"][0]
    expected_steps = life["steps"]
    observation = life["matched_stationary_site_audit_521"]
    assert observation["matched_paid_reads"] > 0
    assert observation["sleep_distinct"] > 0
    assert observation["wait_distinct"] > 0
    expected_len = len(expected_steps)
    assert 28 < expected_len <= 55
    with birth_i1_m11(
        db_path=str(root/"unobserved.sqlite"), life_id=life_id,
        **params,
    ) as actor:
        for row in expected_steps:
            compare_one(actor, row, "direct")
        baseline = (actor._runtime.journal.head_hash,
                    memory_digest(actor._runtime),
                    verify_recalled(actor._runtime))
    assert baseline[0] == life["journal_head"]
    assert baseline[2][3] == observation["matched_paid_reads"]
    assert len(baseline[2][1]) == observation["sleep_distinct"]*2
    assert len(baseline[2][2]) == observation["wait_distinct"]*2

    with birth_i1_m11(
        db_path=str(root/"cold.sqlite"), life_id=life_id,
        **params,
    ) as actor:
        for row in expected_steps[:28]:
            compare_one(actor, row, "pre-cold")
        cut = (actor._runtime.journal.head_hash,
               memory_digest(actor._runtime),
               recalled(actor._runtime))
    before = SQLiteLifeLedger.audit_read_only(
        path=str(root/"cold.sqlite"), expected_individual_id=life_id)
    assert before.generation == 28 and before.may_recover
    with recover_i1_m11(
        db_path=str(root/"cold.sqlite"), life_id=life_id,
        runtime_factory=cold_factory,
    ) as actor:
        restored = (actor._runtime.journal.head_hash,
                    memory_digest(actor._runtime),
                    recalled(actor._runtime))
        assert restored == cut, "cold recovery changed authenticated memory"
        for row in expected_steps[28:]:
            compare_one(actor, row, "post-cold")
        after = (actor._runtime.journal.head_hash,
                 memory_digest(actor._runtime),
                 verify_recalled(actor._runtime))
    assert baseline == after, "cold recovery altered matched lived sources"
    final = SQLiteLifeLedger.audit_read_only(
        path=str(root/"cold.sqlite"), expected_individual_id=life_id)
    assert final.generation == expected_len
    assert final.journal_head == baseline[0]
    assert final.status == life["lifecycle"]
    assert final.may_recover == (final.status == "active")
    print("I1_524_OPERATOR_DIRECT_COLD_PARITY",
          "steps", expected_len, "paired", after[2][3],
          "distinct_sleep", len(after[2][1])//2,
          "distinct_wait", len(after[2][2])//2,
          "terminal", final.status, flush=True)
"""
            done = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT/"tools")},
                text=True, capture_output=True,
            )
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("I1_524_OPERATOR_DIRECT_COLD_PARITY", done.stdout)
            print(done.stdout.strip())


if __name__ == "__main__":
    unittest.main()
