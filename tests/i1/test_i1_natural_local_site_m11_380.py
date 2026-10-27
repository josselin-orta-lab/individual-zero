"""Short authentic oasis life, natural local option to bodily site followup."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class CanonicalLocalSiteM11(unittest.TestCase):
 def test_natural_local_opportunities_and_cold_owner_parity(self):
  with TemporaryDirectory() as d:
   built=Path(d)/"generated";generate(built)
   script=r"""
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset,_birth_parameters
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:380:natural-oasis"
TOTAL,SPLIT=6,3
def fresh():return I1Runtime(birth_life_id=life_id,wal_path=None,autonomous_mortal=True,m11_sqlite_custody=True,**params)
def owners(rt):return {owner.owner_id:owner.export_causal_state() for owner in rt.causal_owners}
def events(rt):return [dict(e.causal_event) for e in rt.journal.entries_since(0)]
def drive(actor,n):
 result=[]
 for _ in range(n):
  x=actor.run_step()
  assert x.status=="active",x
  result.append((x.generation,x.world_step,x.journal_head,x.outcome))
 return result
with TemporaryDirectory() as d:
 a=str(Path(d)/"control.sqlite");b=str(Path(d)/"cold.sqlite")
 with birth_i1_m11(db_path=a,life_id=life_id,**params) as actor:
  control=drive(actor,TOTAL);end=owners(actor._runtime);log=events(actor._runtime)
  actual_site=actor._runtime.exploration.geographic.export_causal_state()
 with birth_i1_m11(db_path=b,life_id=life_id,**params) as actor:
  first=drive(actor,SPLIT);initial=owners(actor._runtime)
 audit=SQLiteLifeLedger.audit_read_only(path=b,expected_individual_id=life_id)
 assert audit.may_recover and audit.generation==SPLIT and not audit.pending_intent
 with recover_i1_m11(db_path=b,life_id=life_id,runtime_factory=fresh) as cold:
  assert owners(cold._runtime)==initial
  rest=drive(cold,TOTAL-SPLIT)
  assert first+rest==control
  assert owners(cold._runtime)==end and events(cold._runtime)==log
  assert cold._runtime.exploration.geographic.export_causal_state()==actual_site
 audit=SQLiteLifeLedger.audit_read_only(path=b,expected_individual_id=life_id)
 assert audit.may_recover and audit.generation==TOTAL and not audit.pending_intent
 counts=Counter(e.get("kind") for e in log)
 proposals=[e for e in log if e.get("kind")=="i1_local_opportunity_proposed"]
 registrations=[e for e in log if e.get("kind")=="i1_local_opportunity_registration"]
 interactions=[e for e in log if e.get("kind")=="command_experienced" and e.get("primitive") in ("collecter","manger","boire","fabriquer_outil","poser_une_pierre")]
 effects=len(actual_site.get("lived_site_effects",[]))
 for e in proposals:
  assert e["data"]["goal_ref"] is None
  assert e["data"]["motor_command_forced"] is False
  assert e["data"]["predicted_result"] is None
 print("I1_380_NATURAL_LOCAL_DIAGNOSTIC "+json.dumps({
  "perceived_events":counts["i1_local_opportunity_perceived"],
  "proposals":len(proposals),
  "registrations":sum(e["data"].get("registered") is True for e in registrations),
  "local_applied":len(interactions),
  "local_applied_primitives":dict(Counter(e["primitive"] for e in interactions)),
  "site_followup_events":counts["i1_lived_site_effect_observed"],
  "site_effect_rows":effects,
  "site_effect_samples":sum(x["samples"] for x in actual_site.get("lived_site_effects",[])),
  "full_cold_parity":True,
  "L3":"NOT_ESTABLISHED"},sort_keys=True))
 assert proposals and registrations
 print("I1_380_LOCAL_M11_COLD_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"),str(ROOT/"tools"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   print(p.stdout,flush=True)
   self.assertIn("I1_380_LOCAL_M11_COLD_OK",p.stdout)
if __name__=="__main__":unittest.main()
