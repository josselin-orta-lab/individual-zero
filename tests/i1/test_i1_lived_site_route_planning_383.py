"""Distinct visited-site routing contracts, no entity or motor authority."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class LivedSiteRouting(unittest.TestCase):
 def test_generated_bounded_first_person_routes(self):
  with TemporaryDirectory() as d:
   generated=Path(d)/"generated";generate(generated)
   script=r"""
from dataclasses import replace
from i1.modules.spatial_memory import find_lived_site_returns
from i1.modules.observed_frontier_routing import ObservedSurvey
def find(**overrides):
 args=dict(origin=(2,0),visits=frozenset(((0,0),(1,0),(2,0))),
  surveys=(ObservedSurvey(position=(1,0),world_step=2,
    free_neighbors=((0,0),(2,0))),),
  lived_sites=(((0,0),2),),current_free_neighbors=frozenset(((1,0),)),
  current_world_step=4)
 args.update(overrides);return find_lived_site_returns(**args)
targets=find()
assert len(targets)==1
t=targets[0]
assert t.observed_position==(0,0) and t.destination==(1,0)
assert t.observed_step==2 and t.direction=="west"
assert t.visited_path==((2,0),(1,0),(0,0))
assert t.ref.startswith("lived-site:0:0:observed-t2:")
assert "entity" not in t.ref
t.validate()
assert not find(origin=(0,0),current_free_neighbors=frozenset(((1,0),)))
assert not find(lived_sites=())
assert not find(current_free_neighbors=frozenset())
for kwargs in (dict(lived_sites=(((0,0),5),)),
 dict(lived_sites=(((9,9),2),)),
 dict(lived_sites=(((0,0),2),((0,0),2))),
 dict(surveys=(ObservedSurvey(position=(1,0),world_step=9,
     free_neighbors=((0,0),(2,0))),))):
 try: find(**kwargs)
 except ValueError: pass
 else: raise AssertionError("future, remote or duplicate source accepted")
for forged in (replace(t,observed_step=6),
 replace(t,visited_path=((2,0),(0,0))),
 replace(t,ref="place:sighting:fake:0:0")):
 try: forged.validate()
 except ValueError: pass
 else: raise AssertionError("invalid target accepted")
print("I1_383_LIVED_SITE_ROUTE_GUARDS_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(generated),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_383_LIVED_SITE_ROUTE_GUARDS_OK",p.stdout)
if __name__=="__main__":unittest.main()
