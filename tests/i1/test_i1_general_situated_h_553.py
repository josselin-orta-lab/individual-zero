"""#553: exact-action situated history with no site or motor reward."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
class GeneralSituated553(unittest.TestCase):
 def test_wait_sleep_and_unknown_sites(self):
  with TemporaryDirectory() as tmp:
   built=Path(tmp)/"generated"
   result=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),"--output",str(built)],cwd=ROOT,text=True,capture_output=True,timeout=90)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   program=r"""
from copy import deepcopy
from i1.modules.paid_action_consolidation import record_paid_source,merge_paid_fragments
from i1.modules.situated_action_history import describe_situated_action_history as describe
def body(e,w):return dict(energy=e,water=w,food=60,integrity=90)
rows=[]
for t,primitive,site,e0,e1 in ((1,"attendre",(2,3),40,39),(3,"dormir",(2,3),39,43),(5,"attendre",(4,5),35,35),(7,"attendre",(2,3),45,46)):
 for i,event in enumerate((
   dict(event_id=f"cmd{t}",kind="command_experienced",t_monde=t,primitive=primitive,parameters={}),
   dict(event_id=f"world{t}",kind="world_transition_experienced",t_monde=t,position_after={"x":site[0],"y":site[1]},body_before=body(e0,70),body_after=body(e1,69),effects={}),
  )):
  rows=record_paid_source(rows,episode_ref=f"ep{t}",event_offset=i,event=event,before_step=10)
fragments=merge_paid_fragments(rows,[],cut_step=10)
wait=describe(published_fragments=fragments,current_site=(2,3),before_step=11,primitive="attendre",parameters={})
assert wait["historical_fragment_count"]==3
assert wait["same_site_fragment_count"]==2 and wait["other_site_fragment_count"]==1
assert wait["site_observations"][0]["sign_counts_by_fragment"]["energy"]["contradictory"]
assert wait["decision_evidence"] is False and wait["motor_permission"] is False
assert wait["expected_consequence"] is None and not wait["site_safety_inferred"]
sleep=describe(published_fragments=fragments,current_site=(2,3),before_step=11,primitive="dormir",parameters={})
assert sleep["historical_fragment_count"]==1
assert describe(published_fragments=fragments,current_site=(9,9),before_step=11,primitive="attendre",parameters={})["current_site_record_status"]=="not_observed_in_bounded_h"
assert describe(published_fragments=fragments,current_site=(2,3),before_step=11,primitive="collecter",parameters={})["historical_fragment_count"]==0
assert describe(published_fragments=fragments,current_site=(2,3),before_step=11,primitive="attendre",parameters={"x":1})["historical_fragment_count"]==0
original=deepcopy(fragments)
wait["site_observations"][0]["experiences"][0]["observed_body_after"]["energy"]=-999
assert original==fragments
for invalid in (fragments+fragments,):
 try:describe(published_fragments=invalid,current_site=(2,3),before_step=11,primitive="attendre",parameters={})
 except ValueError:pass
 else:raise AssertionError("duplicate sources accepted")
try:describe(published_fragments=fragments,current_site=(2,3),before_step=9,primitive="attendre",parameters={})
except ValueError:pass
else:raise AssertionError("unpublished fragments accepted")
print("I1_553_GENERAL_SITUATED_H_OK")
"""
   env=os.environ.copy();env["PYTHONPATH"]=os.pathsep.join((str(built),str(ROOT/"src")))
   test=subprocess.run([sys.executable,"-c",program],cwd=ROOT,env=env,text=True,capture_output=True,timeout=120)
   self.assertEqual(test.returncode,0,test.stdout+"\n"+test.stderr)
   self.assertIn("I1_553_GENERAL_SITUATED_H_OK",test.stdout)
if __name__=="__main__":unittest.main()
