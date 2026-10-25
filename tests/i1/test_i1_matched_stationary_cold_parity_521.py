"""#521: born M11 paid waking-link receipts survive authentic cold recovery."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalStationaryColdParity521(unittest.TestCase):
    def test_cold_recover_preserves_paid_matched_stationary_sources(self):
        with TemporaryDirectory() as directory:
            generated = Path(directory) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger

preset,_ = load_preset("empty-land")
params,_ = _birth_parameters(preset)
life_id="i1:521:cold-stationary-sources"
def factory():
    return I1Runtime(birth_life_id=life_id,
                     autonomous_mortal=True, m11_sqlite_custody=True,
                     wal_path=None, diagnostic_sample_cost_uc=1,
                     module_occupancy_cost_uc=1, **params)
def witness(runtime):
    memory=runtime.memory.export_causal_state()
    commits={
        ref for e in runtime.journal.entries
        if e.causal_event.get("kind")=="auto_segment_commit"
        for ref in e.causal_event["event_refs"]
    }
    seen=set(memory["seen_event_refs"])
    closed={r for ep in memory["episodes"] for r in ep["event_refs"]}
    assert closed <= seen <= commits
    observations=[]
    for e in runtime.journal.entries:
        row=e.causal_event
        if row.get("kind")!="i1_sleep_site_recall_consulted":
            continue
        data=row["data"]
        assert data["evidence_applied"] is False
        assert data["continuous_subjective_session_proven"] is False
        for link in data["waking_links"]:
            assert set(link["sleep_source_refs"]) <= closed
            assert {link["waking_cue_ref"],
                    link["waking_applied_command_ref"],
                    link["waking_applied_transition_ref"]} <= closed
            assert link["waking_step"] == link["sleep_step"] + 1
        observations.append((row["t_monde"], data))
    sleep_ids=set()
    wait_ids=set()
    for _, data in observations:
        assert data["charged_operation"]=="i1_closed_sleep_recall"
        assert data["evidence_applied"] is False
        assert data["wait_decision_evidence"] is False
        assert data["wait_causal_attribution"] is False
        assert len(data["wait_event_refs"])==2*data["wait_witness_count"]
        for ref in data["wait_event_refs"]:
            assert ref in closed and ref in seen
        for ref in data["event_refs"]:
            assert ref in closed and ref in seen
        wait_ids.update(data["wait_event_refs"])
        sleep_ids.update(data["event_refs"])
    assert not (sleep_ids & wait_ids)
    ids={
        (tuple(link["sleep_source_refs"]), link["waking_cue_ref"],
         link["waking_applied_command_ref"],
         link["waking_applied_transition_ref"])
        for _,data in observations for link in data["waking_links"]
    }
    return (runtime.journal.head_hash, memory, tuple(observations),
            frozenset(ids),frozenset(sleep_ids),frozenset(wait_ids))
def advance(actor, n):
    for _ in range(n):
        receipt=actor.run_step()
        assert receipt.status=="active",receipt

with TemporaryDirectory() as folder:
    straight=str(Path(folder)/"straight.sqlite")
    recovered=str(Path(folder)/"recovered.sqlite")
    with birth_i1_m11(db_path=straight,life_id=life_id,**params) as actor:
        advance(actor,55)
        baseline=witness(actor._runtime)
    with birth_i1_m11(db_path=recovered,life_id=life_id,**params) as actor:
        advance(actor,28)
        cut=witness(actor._runtime)
    before=SQLiteLifeLedger.audit_read_only(
        path=recovered,expected_individual_id=life_id)
    assert before.generation==28 and before.may_recover
    with recover_i1_m11(db_path=recovered,life_id=life_id,
                         runtime_factory=factory) as actor:
        assert witness(actor._runtime)==cut, "cold restore altered recalled sources"
        advance(actor,27)
        after=witness(actor._runtime)
    assert after==baseline, "recovered life diverged from uninterrupted life"
    assert after[2], "no natural paid Memory consult"
    assert after[3], "no natural closed waking links after 55 steps"
    assert after[4], "no natural closed sleep sources"
    assert after[5], "no natural closed wait controls"
    assert any(d["wait_witness_count"] and d["witness_count"] for _,d in after[2]), "no matched paid first-person site contrast"
    audit=SQLiteLifeLedger.audit_read_only(
        path=recovered,expected_individual_id=life_id)
    assert audit.generation==55 and audit.journal_head==baseline[0]
    print("I1_521_COLD_STATIONARY_PARITY_OK",len(after[2]),len(after[4]),len(after[5]))
"""
            finished = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "tools")},
                capture_output=True, text=True)
            self.assertEqual(finished.returncode, 0, finished.stdout + finished.stderr)
            self.assertIn("I1_521_COLD_STATIONARY_PARITY_OK", finished.stdout)


if __name__ == "__main__":
    unittest.main()
