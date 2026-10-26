"""#473: signed, bounded situated sleep histories; no safety or motor oracle."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os, subprocess, sys, unittest
ROOT=Path(__file__).resolve().parents[2]
class SituatedSleep473(unittest.TestCase):
    def test_sites_contradictions_unknown_and_saturation(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            build=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(generated)],cwd=ROOT,capture_output=True,text=True,timeout=90)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            code=r"""
from copy import deepcopy
from i1.modules.paid_action_consolidation import record_paid_source,merge_paid_fragments
from i1.modules.situated_sleep_history import describe_situated_sleep_history as describe
def body(e,w):return dict(energy=e,food=80,water=w,integrity=90)
rows=[]
for step,site,before,after in (
    (1,(2,3),body(100,80),body(100,79)),
    (3,(4,5),body(50,70),body(54,69)),
    (5,(2,3),body(45,60),body(44,59))):
    for offset,event in enumerate((
        dict(event_id=f"c{step}",kind="command_experienced",t_monde=step,
             primitive="dormir",parameters={}),
        dict(event_id=f"w{step}",kind="world_transition_experienced",t_monde=step,
             position_after=dict(x=site[0],y=site[1]),
             body_before=before,body_after=after,effects={}),
    )):
        rows=record_paid_source(rows,episode_ref=f"e{step}",event_offset=offset,
            event=event,before_step=12)
fragments=merge_paid_fragments(rows,[],cut_step=12)
result=describe(published_fragments=fragments,current_site=(2,3),before_step=13)
assert result["historical_site_count"]==2 and result["historical_fragment_count"]==3
assert result["same_site_fragment_count"]==2
assert result["other_site_fragment_count"]==1
a,b=result["site_observations"]
assert a["site_ref"]=="sleep-site:2:3" and b["site_ref"]=="sleep-site:4:5"
assert a["sign_counts_by_fragment"]["energy"]["negative"]==1
assert a["sign_counts_by_fragment"]["energy"]["zero"]==1
assert a["observed_full_energy_before_count"]==1
assert a["sign_counts_by_fragment"]["water"]["negative"]==2
assert result["expected_consequence"] is None
assert result["decision_evidence"] is False
assert result["site_safety_inferred"] is False and result["motor_permission"] is False
assert describe(published_fragments=fragments,current_site=(7,8),before_step=13)["current_site_record_status"]=="not_observed_in_bounded_h"
snapshot=deepcopy(fragments)
result["site_observations"][0]["experiences"][0]["observed_body_after"]["energy"]=-2
assert fragments==snapshot
try:
    describe(published_fragments=fragments,current_site=(2,3),before_step=11)
except ValueError:pass
else:raise AssertionError("prepublication read allowed")
try:
    describe(published_fragments=fragments+fragments,current_site=(2,3),before_step=13)
except ValueError:pass
else:raise AssertionError("duplicate source accepted")
print("I1_473_SITUATED_SLEEP_H_OK")
"""
            env=os.environ.copy();env["PYTHONPATH"]=os.pathsep.join((str(generated),str(ROOT/"src")))
            run=subprocess.run([sys.executable,"-c",code],cwd=ROOT,env=env,capture_output=True,text=True,timeout=100)
            self.assertEqual(run.returncode,0,run.stdout+"\n"+run.stderr)
            self.assertIn("I1_473_SITUATED_SLEEP_H_OK",run.stdout)
if __name__=="__main__":unittest.main()
