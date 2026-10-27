"""Natural Planning must see nonadjacent contradictory first-person witnesses."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class WitnessRankingRegression(unittest.TestCase):
 def test_generated_natural_ranking_and_owner_recovery(self):
  with TemporaryDirectory() as d:
   built=Path(d)/"generated";generate(built)
   program=r"""
from i1lab.i1_natural_runtime import _rank_current_local_opportunity
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
import inspect
from i1lab.i1_natural_runtime import I1Runtime
memory=build_stage11_reference_runtime(autonomous_mortal=True).memory
sig="i1:affordance:collecter:target=x"
before=dict(energy=50.,food=50.,water=50.,integrity=50.)
for step,delta in ((2,10.),(4,0.),(6,-10.)):
 assert memory.remember_applied_option(signature=sig,source_option_ref=f"option:i1:local:t{step}:collecter:target=x",applied_step=step,cost_uc=1,body_before=before)
 after=dict(before,water=before["water"]+delta)
 assert memory.observe_applied_option_followups(world_step=step+1,body_after=after)
w=memory.observed_option_witnesses(signature=sig,world_step=8)
assert [item["body_delta"]["water"] for item in w]==[10.,0.,-10.]
rank=_rank_current_local_opportunity(learned_evidence=.2,remembered=True,witnesses=w,rotation=0)
neutral=_rank_current_local_opportunity(learned_evidence=.2,remembered=False,witnesses=(),rotation=0)
assert rank==neutral, "nonadjacent contradiction must remove Memory preference"
assert _rank_current_local_opportunity(learned_evidence=.3,remembered=True,witnesses=w,rotation=0) < rank, "learned Q still first"
assert _rank_current_local_opportunity(learned_evidence=.2,remembered=True,witnesses=w[:-1],rotation=0) < rank
image=memory.export_causal_state()
other=type(memory)(memory._config,atomic_world_step_length_boundary=True)
other.restore_causal_state(image)
assert other.export_causal_state()==image
assert _rank_current_local_opportunity(learned_evidence=.2,remembered=True,witnesses=other.observed_option_witnesses(signature=sig,world_step=8),rotation=0)==rank
assert "_rank_current_local_opportunity(" in inspect.getsource(I1Runtime._propose_independent_local)
print("I1_367_NONADJACENT_CONTRADICTION_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,env=env,capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_367_NONADJACENT_CONTRADICTION_OK",p.stdout)
if __name__=="__main__":unittest.main()
