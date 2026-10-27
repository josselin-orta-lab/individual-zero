"""One genuine natural M11 step: prospective memory must be journal-backed.

Technical witness only. No forced motor action, seeded option, or cohorts.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate


class NaturalProspectiveWitness(unittest.TestCase):
    def test_first_person_formation_and_cold_memory_image(self):
        with TemporaryDirectory(prefix="i1-363-") as directory:
            built=Path(directory)/"generated"
            generate(built)
            code=r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset,_birth_parameters

preset,_=load_preset("oasis")
settings,_=_birth_parameters(preset)
params=dict(settings,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:363:unforced-prospective"
def fresh():
    return I1Runtime(birth_life_id=life_id,wal_path=None,
        autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as temp:
    db=str(Path(temp)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=life_id,**params) as actor:
        receipt=actor.run_step()
        assert receipt.status=="active",receipt
        current=actor._runtime
        assert current.stage3.substrate.bench is None
        entries=[e.causal_event for e in current.journal.entries_since(0)]
        offered=[e for e in entries if e.get("kind")=="i1_local_opportunity_proposed"]
        registered=[e for e in entries if e.get("kind")=="i1_local_opportunity_registration"]
        seen=[e for e in entries if e.get("kind")=="i1_nonspatial_intention_prospected"]
        assert offered and registered,(offered,registered)
        assert seen,"natural I1 failed to form any prospective memory in oasis"
        image=current.memory.export_causal_state()
        prospective={i["id"]:i for i in image["intentions"]
                     if i["trigger_type"]=="option" and "considered_step" in i["trigger_value"]}
        assert prospective, (seen,image["intentions"])
        for item in seen:
            d=item["data"]
            signature=d["signature"]
            owner_ref="intention:i1:option:"+signature
            assert owner_ref in prospective,(d,prospective)
            row=prospective[owner_ref]
            assert row["trigger_value"]["source_option_ref"]==d["option_ref"]
            assert row["trigger_value"]["considered_step"]==d["world_step"]
            assert d["stage8_evaluated"] is True
            assert d["motor_admission_inherited"] is False
            assert d["action_applied"] is False
        assert current.memory.check_intentions(
            st=None,t_monde=2,cycle=1,pressure_fn=lambda **kwargs:.5)==()
    audit=SQLiteLifeLedger.audit_read_only(path=db,expected_individual_id=life_id)
    assert audit.may_recover and audit.generation==1 and not audit.pending_intent
    with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as cold:
        assert cold._runtime.memory.export_causal_state()==image
        assert cold._runtime.stage3.substrate.bench is None
        result=cold.run_step()
        assert result.status=="active" and result.generation==2
print("I1_363_REAL_PROSPECTIVE_M11_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((
                str(built),str(ROOT/"src"),str(ROOT/"tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            result=subprocess.run([sys.executable,"-B","-c",code],
                cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_363_REAL_PROSPECTIVE_M11_OK",result.stdout)

if __name__=="__main__":
    unittest.main()
