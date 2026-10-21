"""Read-only natural later Stage8 site-context trace with M11 recovery.

Absence of a spontaneous spatial return is a valid diagnostic, never filled by
injecting an action, intention, site history, or fabricated personal memory.
"""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class CanonicalLivedSiteStage8M11(unittest.TestCase):
 def test_natural_stage8_site_context_and_cold_owner_parity(self):
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
life_id="i1:381:natural-oasis-followthrough"
TOTAL,SPLIT=12,6
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
 site_followups=[e for e in log if e.get("kind")=="i1_lived_site_effect_observed"]
 spatial_proposals=[e for e in log if e.get("kind")=="i1_place_memory_option_proposed"]
 spatial_assessments=[e for e in log if e.get("kind")=="stage11_intrinsic_evaluation"
                      and str(e.get("data",{}).get("option_ref","")).startswith("option:place-memory:")]
 matched_spatial_proposals=[e for e in spatial_proposals if any(
   previous["t_monde"]<e["t_monde"]
   and tuple(previous["data"]["site"])==tuple(e["data"]["target"])
   for previous in site_followups)]
 contexts=[e for e in spatial_assessments if
   "exploration:lived_site_context_not_causal" in e["data"].get("intrinsic_producers",())]
 for e in contexts:
  sources=[source for source in e["data"].get("signal_ids",()) if source.startswith("lived-site:")]
  assert sources, "contextual Stage8 contribution lacks a first-person source reference"
  assert all(int(source.rsplit("observed-t",1)[1])<e["t_monde"] for source in sources), "Stage8 referenced future or same-step site observation"
  assert any(tuple(sighting["data"]["site"])==tuple(map(int,source.split(":",3)[1:3]))
     and sighting["t_monde"]<=int(source.rsplit("observed-t",1)[1])
     for sighting in site_followups for source in sources), "Stage8 referenced an unobserved place"
 assert sum(effect["samples"] for effect in actual_site.get("lived_site_effects",[]))>=1, "genuine site context was not persisted"
 for e in proposals:
  assert e["data"]["goal_ref"] is None
  assert e["data"]["motor_command_forced"] is False
  assert e["data"]["predicted_result"] is None
 print("I1_381_NATURAL_SITE_STAGE8_DIAGNOSTIC "+json.dumps({
  "perceived_events":counts["i1_local_opportunity_perceived"],
  "proposals":len(proposals),
  "registrations":sum(e["data"].get("registered") is True for e in registrations),
  "local_applied":len(interactions),
  "local_applied_primitives":dict(Counter(e["primitive"] for e in interactions)),
  "site_followup_events":counts["i1_lived_site_effect_observed"],
  "site_effect_rows":effects,
  "site_effect_samples":sum(x["samples"] for x in actual_site.get("lived_site_effects",[])),
  "spatial_proposals":len(spatial_proposals),
  "spatial_proposals_with_prior_matching_lived_site":len(matched_spatial_proposals),
  "spatial_stage8_evaluations":len(spatial_assessments),
  "spatial_stage8_context_contributions":len(contexts),
  "spatial_context_values":[round(float(e["data"]["intrinsic_value"]),6) for e in contexts[:8]],
  "chronological_context_origin_verified":True,
  "full_cold_parity":True,
  "L3":"NOT_ESTABLISHED"},sort_keys=True))
 assert proposals and registrations
 print("I1_381_NATURAL_STAGE8_M11_COLD_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"),str(ROOT/"tools"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   print(p.stdout,flush=True)
   self.assertIn("I1_381_NATURAL_STAGE8_M11_COLD_OK",p.stdout)
if __name__=="__main__":unittest.main()
