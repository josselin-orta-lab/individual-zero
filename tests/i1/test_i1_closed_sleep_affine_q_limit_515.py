"""#515: affine Q cannot encode an arbitrary closed lived A/B/C site pattern."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]

class AffineSleepSite515(unittest.TestCase):
    def test_generated_i1_three_site_contrast(self):
        with TemporaryDirectory() as folder:
            generated=Path(folder)/"generated"
            built=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(generated)],text=True,capture_output=True)
            self.assertEqual(built.returncode,0,built.stdout+built.stderr)
            program=r"""
from i1.modules.memory import EpisodicMemory, Episode
from i1.modules.td_values import (
    LinearTDValues, ValueFeatureConfig, TDLearningConfig, EvaluationState)
def body(e):return {"energy":float(e),"food":60.,"water":60.,"integrity":100.}
def pair(i,x,change):
    before=body(50)
    after=body(50+change)
    command={"event_id":f"c{i}","kind":"command_experienced",
      "t_monde":i,"primitive":"dormir","parameters":{}}
    transition={"event_id":f"t{i}","kind":"world_transition_experienced",
      "t_monde":i,"position_after":{"x":x,"y":2},"body_before":before,
      "body_after":after,"effects":{}}
    return command,transition
events=[pair(1,1,5),pair(2,2,-5),pair(3,3,5)]
m=object.__new__(EpisodicMemory)
m._episodes=[
  Episode(id=f"ep{i}",start_t_monde=i,end_t_monde=i,
    event_refs=(c["event_id"],t["event_id"]),
    boundary_type="max_length",active_goal_ref=None,
    body_start=None,body_end=None,cumulative_reward=0.,
    surprise=0.,linked_previous_ref=None)
  for i,(c,t) in enumerate(events,1)]
m._seen_event_refs={v["event_id"] for pair in events for v in pair}
history=[v for pair in events for v in pair]
directions=[]
for x in (1,2,3):
    witnesses=m.closed_sleep_site_witnesses(
        autobiography=history,site=(x,2),now=4)
    assert len(witnesses)==1
    assert witnesses[0]["source_event_refs"]==(f"c{x}",f"t{x}")
    summary=m.describe_closed_sleep_site(witnesses=witnesses,site=(x,2))
    assert summary["decision_evidence"] is False
    assert summary["causal_attribution"] is False
    directions.append(summary["same_step_channels"]["energy"])
assert directions[0]["increase"]==1 and directions[1]["decrease"]==1
assert directions[2]["increase"]==1
assert not m.closed_sleep_site_witnesses(
    autobiography=history,site=(4,2),now=4)
# Only the already-closed owner may disclose an episode.
m._episodes=m._episodes[:2]
assert not m.closed_sleep_site_witnesses(
    autobiography=history,site=(3,2),now=4)
cfg=ValueFeatureConfig(version="affine-515",feature_names=(
  "bias","energy","food","water","integrity","x","y","is_night",
  "goal_recover_energy"),position_scale_x=10.,position_scale_y=10.)
q=LinearTDValues(TDLearningConfig(version="td-515",eta=.1,
  lambda_e=.5,beta=.9,evidence_scale=1.,features=cfg))
def state(x):
    return EvaluationState(body=body(50),x=x,y=2,
      active_goal_type="recover_energy",temporal_context="night")
signature="primitive:dormir"
for w in ([0.]*9,[.1,.2,-.3,.4,-.5,.6,-.7,.8,-.9],
          [-3.,4.,5.,-6.,7.,8.,-9.,10.,11.]):
    q._weights[signature]=list(w)
    a,b,c=(q.q(state(x),signature) for x in (1,2,3))
    assert abs(2*b-a-c)<1e-10,(a,b,c)
# Equal high A/C, low B can never be represented simultaneously.
print("I1_515_CLOSED_SLEEP_AFFINE_Q_LIMIT_OK")
"""
            run=subprocess.run([sys.executable,"-c",program],
                 env={"PYTHONPATH":str(generated)},text=True,capture_output=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertIn("I1_515_CLOSED_SLEEP_AFFINE_Q_LIMIT_OK",run.stdout)

if __name__=="__main__":
    unittest.main()
