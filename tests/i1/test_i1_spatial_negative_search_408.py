"""A skipped route search is not evidence that a remembered route disappeared."""
import os,sys,subprocess,unittest,inspect
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class SpatialNegativeSearchProvenance(unittest.TestCase):
 def test_generated_I1_search_completion_guard(self):
  with TemporaryDirectory(prefix="i1-408-") as home:
   out=Path(home)/"generated";generate(out)
   code=r"""
import inspect
from i1lab.stage11_runtime import Stage11Runtime
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
normal=inspect.getsource(Stage11Runtime._phase_hooks)
native=inspect.getsource(I1Runtime._phase_hooks)
assert "self._stage11_place_search_completed_cycle = None" in normal
assert normal.index('operation="geographic_route_search"') < normal.index('self._stage11_place_search_completed_cycle = (capture.t_monde, cycle)')
assert normal.index('frozen_place_targets = find_spatial_returns(') < normal.index('self._stage11_place_search_completed_cycle = (capture.t_monde, cycle)')
guard=native[native.index("def plan_independent_local(ctx):"):native.index("def register_independent_local(ctx):")]
assert guard.index('_stage11_place_search_completed_cycle') < guard.index("self.memory.reconcile_option_intentions(")
assert "== (capture.t_monde, cycle)" in guard
memory=build_stage11_reference_runtime(autonomous_mortal=True).memory
sig="memory_place_return:known"
assert memory.remember_considered_option(signature=sig,
 source_option_ref="option:place-memory:place:known:at:3:0:from:1:0:via:2:0",
 considered_step=2,cost_uc=1)
before=memory.export_causal_state()
# No charged search: neither a suspended option nor a fabricated sighting.
assert before==memory.export_causal_state()
assert memory.reconcile_option_intentions(available_signatures=frozenset(),
 world_step=3,namespace="memory_place_return:")
assert next(i for i in memory.intentions if i.target==sig).state=="suspended"
assert memory.reconcile_option_intentions(available_signatures=frozenset({sig}),
 world_step=3,namespace="memory_place_return:")
assert next(i for i in memory.intentions if i.target==sig).state=="pending"
print("I1_408_ROUTE_SEARCH_PROVENANCE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_408_ROUTE_SEARCH_PROVENANCE_OK",p.stdout)
