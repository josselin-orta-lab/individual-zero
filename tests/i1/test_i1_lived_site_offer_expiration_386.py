"""Old, authenticated lived-site offers must expire on a fresh physical capture."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class LivedSiteOfferLifetime(unittest.TestCase):
 def test_generated_owner_new_capture_and_cold_recovery(self):
  with TemporaryDirectory() as tmp:
   out=Path(tmp)/"generated";generate(out)
   program=r"""
from types import SimpleNamespace
from i1.modules.geographic_exploration import GeographicExploration,GeographicExplorationConfig
from i1.modules.spatial_memory import find_lived_site_returns
from i1.modules.observed_frontier_routing import ObservedSurvey
cfg=GeographicExplorationConfig(version="lived-offer-386",novelty_weight=.2,max_distinct_sites=10,
 max_targets_per_cycle=1,observe_routes=True,refresh_surveys=True,remember_entities=True,
 experienced_site_effects=True,max_place_candidates=2)
geo=GeographicExploration(cfg)
def cap(step,x,y):
 return SimpleNamespace(t_monde=step,x=x,y=y)
before=dict(energy=70.,food=50.,water=20.,integrity=90.)
after=dict(before,water=45.)
geo.observe_capture(cap(1,0,0))
assert geo.note_applied_local_action(world_step=1,position=(0,0),
 body_before=before,primitive="boire",option_ref="genuine-local-action")
effect=geo.observe_lived_site_followup(world_step=2,position=(0,0),body_after=after)
assert effect is not None
geo.observe_capture(cap(2,0,0))
geo.observe_capture(cap(3,1,0))
survey=ObservedSurvey(position=(0,0),world_step=1,free_neighbors=((1,0),))
survey.validate()
geo._surveys[(0,0)]=survey
route=find_lived_site_returns(origin=(1,0),visits=frozenset(((0,0),(1,0))),
 surveys=(survey,),lived_sites=(((0,0),2),),
 current_free_neighbors=frozenset(((0,0),)),current_world_step=3)
assert len(route)==1
geo.freeze_lived_sites(route)
assert len(geo.lived_offered)==1
image=geo.export_causal_state()
cold=GeographicExploration(cfg);cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert len(cold.lived_offered)==1
assert cold.observe_capture(cap(4,1,0)) is False
assert cold.lived_offered==(), "expired spatial offer retained after new physical capture"
image2=cold.export_causal_state()
cold2=GeographicExploration(cfg);cold2.restore_causal_state(image2)
assert cold2.export_causal_state()==image2
assert cold2.site_effect_for((0,0))==effect
print("I1_386_LIVED_SITE_OFFER_EXPIRED_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_386_LIVED_SITE_OFFER_EXPIRED_OK",p.stdout)
if __name__=="__main__":unittest.main()
