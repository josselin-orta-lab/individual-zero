"""#330: distinct local targets vs same one-hop geographic intention."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class GeographicIdentityTests(unittest.TestCase):
    def test_generated_frontier_and_transit_key_semantics(self):
        with TemporaryDirectory(prefix="i1-330-") as d:
            generate(Path(d)/"built")
            script=r"""
from types import SimpleNamespace
from i1.modules.geographic_exploration import GeographicTarget,GeographicExploration,GeographicExplorationConfig
from i1.modules.geographic_planning import propose_geographic_frontier
def option(t, x=0):
    target=GeographicTarget(
        ref=f"frontier:{x+1}:0:from:{x}:0",source_t_monde=t,
        origin=(x,0),destination=(x+1,0),direction="east")
    initial=SimpleNamespace(x=x,y=0,validate=lambda:None,
        adjacent=(SimpleNamespace(direction="east",passable=True,creature=False,x=x+1,y=0),))
    simulator=SimpleNamespace(rollout=lambda **kw:SimpleNamespace(
        complete=False,reason="equipment_input_unseen"))
    return propose_geographic_frontier(target=target,initial_state=initial,
        simulator=simulator,st_version="local-observation",t_monde=t,ttl_steps=20),target
p,a=option(10)
q,b=option(11)
different,_=option(11,x=3)
assert p is not None and q is not None
assert p.option.id==q.option.id
assert p.option.id!=different.option.id
assert p.option.expires_at_step!=q.option.expires_at_step
geo=GeographicExploration(GeographicExplorationConfig(
    version="unit",novelty_weight=0.1,max_distinct_sites=32,
    max_targets_per_cycle=1))
geo._offered=(b,)
assert geo.target_for(p.option)==b
geo._offered=()
assert geo.target_for(p.option) is None
print("I1_GEOGRAPHIC_STABLE_OPTION_KEY_OK")
"""
            result=subprocess.run([sys.executable,"-c",script],
                cwd=ROOT,env={"PYTHONPATH":str(Path(d)/"built")+":"+str(ROOT/"src")},
                text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
