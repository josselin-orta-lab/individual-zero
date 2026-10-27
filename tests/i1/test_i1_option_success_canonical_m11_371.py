"""Canonical two-step M11 custody cannot manufacture option success."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class CanonicalOptionSuccessM11(unittest.TestCase):
    def test_cold_restore_does_not_infer_option_success(self):
        with TemporaryDirectory(prefix="i1-371-") as folder:
            built = Path(folder) / "generated"
            generate(built)
            code = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset,_birth_parameters

preset,_ = load_preset("oasis")
params,_ = _birth_parameters(preset)
params = dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id = "i1:371:canonical-option-success"
def fresh():
    return I1Runtime(birth_life_id=life_id,wal_path=None,
        autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory(prefix="i1-371-lived-") as tmp:
    db = str(Path(tmp)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=life_id,**params) as actor:
        receipt = actor.run_step()
        assert receipt.status == "active",receipt
        runtime = actor._runtime
        events = [entry.causal_event for entry in runtime.journal.entries_since(0)]
        assert any(e["kind"] == "i1_nonspatial_intention_prospected" for e in events)
        before = runtime.memory.export_causal_state()
        options = [e for e in before["intentions"] if e["trigger_type"]=="option"]
        assert options and all(e["state"]!="done" for e in options)
        assert runtime.stage3.substrate.bench is None
    audit = SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert audit.may_recover and audit.generation == 1 and not audit.pending_intent
    with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as cold:
        assert cold._runtime.memory.export_causal_state()==before
        next_receipt=cold.run_step()
        assert next_receipt.status=="active" and next_receipt.generation==2
        later=cold._runtime.memory.export_causal_state()
        assert all(e["state"]!="done" for e in later["intentions"]
                   if e["trigger_type"]=="option")
        for record in later["intentions"]:
            if record["trigger_type"]=="option":
                try: cold._runtime.memory.complete_intention(record["id"])
                except ValueError: pass
                else: raise AssertionError("unobserved semantic completion")
    final=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert final.may_recover and final.generation==2 and not final.pending_intent
print("I1_371_CANONICAL_COLD_NO_FALSE_SUCCESS_OK")
"""
            env = dict(os.environ,PYTHONPATH=os.pathsep.join(
                (str(built),str(ROOT/"src"),str(ROOT/"tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",code],
                cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_371_CANONICAL_COLD_NO_FALSE_SUCCESS_OK",p.stdout)

if __name__=="__main__":
    unittest.main()
