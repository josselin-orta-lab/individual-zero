"""#519: closed first-person wait controls share the paid sleep scan."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
class ClosedStationaryControls519(unittest.TestCase):
    def test_control_source_custody_and_unknowns(self):
        with TemporaryDirectory() as folder:
            output=Path(folder)/"out"
            built=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                                  "--output",str(output)],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stdout+built.stderr)
            program=r"""
from i1.modules.memory import EpisodicMemory,Episode
def ep(n,refs):
    return Episode(id=f"e{n}",start_t_monde=n,end_t_monde=n,
      event_refs=tuple(refs),boundary_type="max_length",
      active_goal_ref=None,body_start=None,body_end=None,
      cumulative_reward=0.,surprise=0.,linked_previous_ref=None)
def memory(groups):
    m=object.__new__(EpisodicMemory)
    m._episodes=[ep(i,refs) for i,refs in enumerate(groups)]
    m._seen_event_refs={ref for group in groups for ref in group}
    return m
def body(e=30):
    return dict(energy=e,food=60,water=50,integrity=85)
def cmd(name,step,action):
    return dict(event_id=name,kind="command_experienced",
      t_monde=step,primitive=action,parameters={})
def outcome(name,step,e,site=(2,3),pre=True):
    item=dict(event_id=name,kind="world_transition_experienced",t_monde=step,
      position_after=dict(x=site[0],y=site[1]),body_after=body(e),effects={})
    if pre:item["body_before"]=body()
    return item
events=[cmd("c1",1,"dormir"),outcome("t1",1,35),
        cmd("c2",2,"attendre"),outcome("t2",2,29),
        cmd("c3",3,"attendre"),outcome("t3",3,28,pre=False)]
owned=memory([("c1","t1"),("c2","t2"),("c3","t3")])
def read(ev=events,m=owned,site=(2,3),now=5):
    return m.closed_stationary_site_witnesses(
       autobiography=ev,site=site,now=now)
data=read()
assert set(data)=={"dormir","attendre"}
assert [x["step"] for x in data["attendre"]]==[2,3]
assert [x["step"] for x in data["dormir"]]==[1]
assert owned.closed_sleep_site_witnesses(
    autobiography=events,site=(2,3),now=5)==data["dormir"]
balance=owned.describe_closed_sleep_site(
    witnesses=data["attendre"],site=(2,3))
assert balance["same_step_channels"]["energy"]==dict(
    increase=0,decrease=1,stable=0,unknown=1)
assert balance["causal_attribution"] is False
assert balance["decision_evidence"] is False
assert not read(site=(2,30))["attendre"]
assert [row["step"] for row in read(now=3)["attendre"]]==[2]
assert [row["step"] for row in read(
    m=memory([("c1","t1"),("c2",),("c3","t3")]))["attendre"]==[3]
assert [row["step"] for row in read(ev=events+[events[2]])["attendre"]]==[3]
assert [row["step"] for row in read(
    ev=events[:3]+[outcome("t2",2,29,site=(8,3))]+events[4:])["attendre"]==[3]
assert [row["step"] for row in read(
    ev=events[:3]+[dict(events[3],body_before={"energy":float("nan"),
      "food":60,"water":50,"integrity":85})]+events[4:])["attendre"]==[3]
print("I1_519_CLOSED_STATIONARY_CONTROLS_OK")
"""
            result=subprocess.run([sys.executable,"-c",program],
               env={"PYTHONPATH":str(output)},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_519_CLOSED_STATIONARY_CONTROLS_OK",result.stdout)
if __name__=="__main__":
    unittest.main()
