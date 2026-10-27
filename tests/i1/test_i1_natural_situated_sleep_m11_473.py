"""#473: a naturally evaluated sleep option observes paid, committed sites.

A single autonomous I1 life must produce the new non-scoring Stage8 receipt,
then an independent canonical twin must preserve and replay it across an M11
cold boundary. No forced movement, sleep command, wakeup or Oracle advice.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalSituatedSleepM11473(unittest.TestCase):
    def test_natural_situated_sleep_receipt_and_cold_parity(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)],
                cwd=ROOT, text=True, capture_output=True, timeout=90,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1.modules.situated_sleep_history import SCHEMA

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
identity = "i1:situated:sleep:h:natural:473"
observed_kind = "i1_situated_sleep_h_context_observed"
generic_kind = "i1_published_action_stage8_context_observed"

def factory():
    return I1Runtime(
        birth_life_id=identity, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        **params,
    )

def events(life):
    return [row.causal_event for row in life._runtime.journal.entries]

def by_kind(life, kind):
    return [event for event in events(life) if event["kind"] == kind]

with TemporaryDirectory() as home:
    uninterrupted_db = str(Path(home) / "uninterrupted.sqlite")
    interrupted_db = str(Path(home) / "interrupted.sqlite")
    with birth_i1_m11(db_path=uninterrupted_db, life_id=identity, **params) as life:
        for _ in range(220):
            last = life.run_step()
            situated_receipts = by_kind(life, observed_kind)
            if situated_receipts:
                break
            assert last.status == "active", "natural I1 died before situated h recall"
        else:
            raise AssertionError(
                "no genuinely evaluated situated sleep h recall before step 220"
            )
        assert life._runtime.journal.verify()
        activations = {
            item["data"]["new_history_version"]: item["t_monde"]
            for item in by_kind(life, "stage10_consolidation_version_activated")
        }
        assert activations, "no published Stage10 historical version"
        charges = [
            item for item in by_kind(life, "compute_charge")
            if item["data"].get("operation") == "i1_published_action_recall"
            and item["data"].get("module") == "planning"
            and item["data"].get("requested_uc") == 1
            and item["data"].get("accepted") is True
        ]
        paid_cycles = {(item["t_monde"], item.get("cycle")) for item in charges}
        assert len(paid_cycles) == len(charges), "double h charge in one cycle"
        generic = by_kind(life, generic_kind)
        closed_sources = {
            ref for item in by_kind(life, "auto_segment_commit")
            for ref in item["event_refs"]
        }
        for ev in situated_receipts:
            data = ev["data"]
            summary = data["situated"]
            assert data["owner"] == "SlowHistory"
            assert data["history_version"] in activations
            assert ev["t_monde"] >= activations[data["history_version"]]
            assert data["charged_operation"] == "i1_published_action_recall"
            assert (ev["t_monde"], ev.get("cycle")) in paid_cycles
            assert data["q_or_p40_augmented"] is False
            assert data["motor_permission"] is False
            assert summary["schema"] == SCHEMA
            assert summary["primitive"] == "dormir"
            assert summary["historical_fragment_count"] > 0
            assert summary["historical_site_count"] >= 1
            assert summary["decision_evidence"] is False
            assert summary["causal_attribution"] is False
            assert summary["site_safety_inferred"] is False
            assert summary["expected_consequence"] is None
            assert summary["motor_permission"] is False
            paired = [
                item for item in generic
                if item["t_monde"] == ev["t_monde"]
                and item.get("cycle") == ev.get("cycle")
                and item["data"]["option_ref"] == data["option_ref"]
                and item["data"]["history_version"] == data["history_version"]
                and item["data"]["primitive"] == "dormir"
            ]
            assert paired, "site context not attached to a real Stage8 sleep option"
            original = paired[0]["data"]
            assert summary["current_site"] == original["current_site"]
            refs = {
                fragment["id"]: fragment
                for fragment in original["historical_fragments"]
            }
            for location in summary["site_observations"]:
                assert location["site_ref"].startswith("sleep-site:")
                for witness in location["experiences"]:
                    assert witness["fragment_id"] in refs
                    historical = refs[witness["fragment_id"]]
                    assert witness["source_event_refs"] == historical["source_event_refs"]
                    assert all(
                        ref in closed_sources and life._runtime.journal.get(ref) is not None
                        for ref in witness["source_event_refs"]
                    )
                    assert historical["last_step"] < historical["consolidation_cut_step"]
        cut_step = last.world_step
        cut_history = life._runtime.slow_history.export_causal_state()
        cut_journal = life._runtime.journal.head_hash
        cut_refs = life._runtime.slow_history.committed_episode_refs()
        cut_receipts = by_kind(life, observed_kind)
        after = life.run_step()
        assert after.status == "active"
        after_history = life._runtime.slow_history.export_causal_state()
        after_journal = life._runtime.journal.head_hash
        after_receipts = by_kind(life, observed_kind)
        assert life._runtime.journal.verify()

    with birth_i1_m11(db_path=interrupted_db, life_id=identity, **params) as twin:
        for _ in range(cut_step):
            event = twin.run_step()
            assert event.status == "active"
        assert twin._runtime.slow_history.export_causal_state() == cut_history
        assert twin._runtime.slow_history.committed_episode_refs() == cut_refs
        assert twin._runtime.journal.head_hash == cut_journal
        assert by_kind(twin, observed_kind) == cut_receipts
        assert twin._runtime.journal.verify()
    audit = SQLiteLifeLedger.audit_read_only(
        path=interrupted_db, expected_individual_id=identity,
    )
    assert audit.may_recover and audit.journal_head == cut_journal
    with recover_i1_m11(
        db_path=interrupted_db, life_id=identity, runtime_factory=factory,
    ) as restored:
        assert restored._runtime.slow_history.export_causal_state() == cut_history
        assert restored._runtime.slow_history.committed_episode_refs() == cut_refs
        assert restored._runtime.journal.head_hash == cut_journal
        assert by_kind(restored, observed_kind) == cut_receipts
        result = restored.run_step()
        assert result.status == after.status == "active"
        assert restored._runtime.slow_history.export_causal_state() == after_history
        assert restored._runtime.journal.head_hash == after_journal
        assert by_kind(restored, observed_kind) == after_receipts
        assert restored._runtime.journal.verify()
print("I1_473_NATURAL_SITUATED_H_M11_PARITY_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(output), str(ROOT / "src"), str(ROOT / "tools")
            ))
            run = subprocess.run(
                [sys.executable, "-c", program],
                cwd=ROOT, text=True, capture_output=True,
                env=env, timeout=480,
            )
            self.assertEqual(run.returncode, 0, run.stdout + "\n" + run.stderr)
            self.assertIn("I1_473_NATURAL_SITUATED_H_M11_PARITY_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
