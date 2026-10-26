"""#553: unforced ordinary-action situated h consultation, postcommit M11 parity."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalGenericSituatedM11553(unittest.TestCase):
    def test_natural_generic_situated_witness_and_cold_recovery(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)], cwd=ROOT,
                capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1.modules.situated_action_history import SCHEMA

preset,_=load_preset("empty-land")
params,_=_birth_parameters(preset)
identity="i1:generic:h:sites:natural:553"
kind="i1_situated_action_h_context_observed"
generic="i1_published_action_stage8_context_observed"

def factory():
    return I1Runtime(birth_life_id=identity,autonomous_mortal=True,
                     m11_sqlite_custody=True,wal_path=None,
                     diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                     **params)

def events(life):
    return [entry.causal_event for entry in life._runtime.journal.entries]

def seen(life,kind):
    return [item for item in events(life) if item["kind"]==kind]

with TemporaryDirectory() as home:
    a=str(Path(home)/"a.sqlite")
    b=str(Path(home)/"b.sqlite")
    with birth_i1_m11(db_path=a,life_id=identity,**params) as life:
        for _ in range(140):
            last=life.run_step()
            receipts=seen(life,kind)
            if receipts or last.status=="dead":break
        assert receipts,"no naturally evaluated generic action with published h witness"
        assert last.status=="active","natural I1 died before h generic witness"
        publications={
            item["data"]["new_history_version"]:item["t_monde"]
            for item in seen(life,"stage10_consolidation_version_activated")
        }
        paid={
            (item["t_monde"],item.get("cycle"))
            for item in seen(life,"compute_charge")
            if item["data"].get("module")=="planning"
            and item["data"].get("operation")=="i1_published_action_recall"
            and item["data"].get("requested_uc")==1
            and item["data"].get("accepted") is True
        }
        ordinary=seen(life,generic)
        committed={
            ref for item in seen(life,"auto_segment_commit")
            for ref in item["event_refs"]
        }
        for receipt in receipts:
            d=receipt["data"]; summary=d["situated"]
            assert (receipt["t_monde"],receipt.get("cycle")) in paid
            assert d["history_version"] in publications
            assert receipt["t_monde"]>=publications[d["history_version"]]
            assert d["owner"]=="SlowHistory"
            assert d["charged_operation"]=="i1_published_action_recall"
            assert d["new_uc_debit_at_stage8"] is False
            assert d["decision_evidence"] is False
            assert d["motor_permission"] is False
            assert d["q_or_p40_augmented"] is False
            assert summary["schema"]==SCHEMA
            assert summary["primitive"]!="dormir"
            assert summary["historical_fragment_count"]>0
            assert not summary["site_safety_inferred"]
            assert summary["expected_consequence"] is None
            matched=[
                item for item in ordinary
                if item["t_monde"]==receipt["t_monde"]
                and item.get("cycle")==receipt.get("cycle")
                and item["data"]["option_ref"]==d["option_ref"]
                and item["data"]["history_version"]==d["history_version"]
                and item["data"]["primitive"]==summary["primitive"]
                and item["data"]["parameters"]==summary["parameters"]
            ]
            assert matched,"generic situated context not attached to evaluated option"
            assert summary["current_site"]==matched[0]["data"]["current_site"]
            originals={row["id"]:row for row in matched[0]["data"]["historical_fragments"]}
            for site in summary["site_observations"]:
                for witness in site["experiences"]:
                    assert witness["fragment_id"] in originals
                    old=originals[witness["fragment_id"]]
                    assert witness["source_event_refs"]==old["source_event_refs"]
                    assert all(ref in committed and life._runtime.journal.get(ref) is not None
                               for ref in witness["source_event_refs"])
        before_step=last.world_step
        before_history=life._runtime.slow_history.export_causal_state()
        before_hash=life._runtime.journal.head_hash
        before_receipts=seen(life,kind)
        before_refs=life._runtime.slow_history.committed_episode_refs()
        next_step=life.run_step()
        after_history=life._runtime.slow_history.export_causal_state()
        after_hash=life._runtime.journal.head_hash
        after_receipts=seen(life,kind)
        assert life._runtime.journal.verify()
    with birth_i1_m11(db_path=b,life_id=identity,**params) as twin:
        for _ in range(before_step):
            current=twin.run_step()
            assert current.status=="active"
        assert twin._runtime.journal.head_hash==before_hash
        assert twin._runtime.slow_history.export_causal_state()==before_history
        assert twin._runtime.slow_history.committed_episode_refs()==before_refs
        assert seen(twin,kind)==before_receipts
    audit=SQLiteLifeLedger.audit_read_only(path=b,expected_individual_id=identity)
    assert audit.may_recover and audit.journal_head==before_hash
    with recover_i1_m11(db_path=b,life_id=identity,runtime_factory=factory) as restored:
        assert restored._runtime.journal.head_hash==before_hash
        assert restored._runtime.slow_history.export_causal_state()==before_history
        assert seen(restored,kind)==before_receipts
        out=restored.run_step()
        assert out.status==next_step.status
        assert restored._runtime.journal.head_hash==after_hash
        assert restored._runtime.slow_history.export_causal_state()==after_history
        assert seen(restored,kind)==after_receipts
        assert restored._runtime.journal.verify()
print("I1_553_NATURAL_GENERIC_SITUATED_M11_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(output), str(ROOT / "src"), str(ROOT / "tools")
            ))
            result = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT,
                env=env, capture_output=True, text=True, timeout=500,
            )
            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertIn("I1_553_NATURAL_GENERIC_SITUATED_M11_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
