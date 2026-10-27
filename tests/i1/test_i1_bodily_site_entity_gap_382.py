"""A lived bodily site is not automatically an entity-place or a motor goal.

Generated-I1 technical regression of the missing overlap between owner
memories and the existing spatial-return candidate type. No behavior forced.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class PersonallyExperiencedSiteGap(unittest.TestCase):
    def test_generated_owner_preserves_lived_site_without_forging_entity(self):
        with TemporaryDirectory(prefix="i1-382-") as tmp:
            built = Path(tmp) / "generated"
            generate(built)
            code = r"""
from types import SimpleNamespace
from copy import deepcopy
from i1.modules.geographic_exploration import GeographicExploration, GeographicExplorationConfig
from i1.modules.spatial_memory import find_spatial_returns
from i1.modules.observed_frontier_routing import ObservedSurvey

def capture(step, at):
    return SimpleNamespace(
        t_monde=step,x=at[0],y=at[1],
        adjacent=tuple(SimpleNamespace(direction=d,x=at[0]+dx,y=at[1]+dy,
            passable=True,creature=False)
            for d,dx,dy in (("north",0,-1),("east",1,0),
                            ("south",0,1),("west",-1,0))),
        visible_entities=(),
    )
def owner():
    return GeographicExploration(GeographicExplorationConfig(
        version="gap382", novelty_weight=.15,max_distinct_sites=24,
        max_targets_per_cycle=1,observe_routes=True,
        refresh_surveys=True,remember_entities=True,
        experienced_site_effects=True,max_place_candidates=3,
    ))
geo=owner()
body=dict(energy=50.,food=50.,water=50.,integrity=50.)
geo.observe_capture(capture(1,(0,0)))
geo.observe_entities(capture(1,(0,0)),observer_id="i1:382")
assert geo.note_applied_local_action(world_step=1,position=(0,0),
    body_before=body,primitive="boire",option_ref="option:personally-observed")
geo.observe_capture(capture(2,(0,0)))
after=dict(body,water=60.)
site=geo.observe_lived_site_followup(world_step=2,position=(0,0),body_after=after)
assert site is not None and site.samples==1 and site.position==(0,0)
assert geo.place_memories==(), "a bodily association cannot forge an entity"
geo.observe_entities(capture(2,(0,0)),observer_id="i1:382")
geo.observe_capture(capture(3,(1,0)))
geo.observe_entities(capture(3,(1,0)),observer_id="i1:382")
assert geo.site_effect_for((0,0))==site
assert geo.place_memories==()
routes=find_spatial_returns(origin=(1,0),visits=frozenset({(0,0),(1,0)}),
    surveys=(ObservedSurvey(position=(0,0),world_step=2,free_neighbors=((1,0),)),),
    places=geo.place_memories,current_free_neighbors=frozenset({(0,0)}),
    current_world_step=3)
assert routes==(), "existing entity-only Planning cannot recall bodily site alone"
image=geo.export_causal_state()
cold=owner();cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert cold.site_effect_for((0,0))==site and cold.place_memories==()
fake=deepcopy(image)
fake["lived_site_effects"][0]["last_observed_step"]=99
before=cold.export_causal_state()
try: cold.restore_causal_state(fake)
except ValueError: pass
else: raise AssertionError("future bodily observation accepted by M11 owner")
assert cold.export_causal_state()==before
print("I1_382_BODILY_SITE_ENTITY_DISTINCTION_OK")
"""
            env=dict(os.environ,
                     PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"))),
                     PYTHONDONTWRITEBYTECODE="1")
            run=subprocess.run([sys.executable,"-B","-c",code],
                cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertIn("I1_382_BODILY_SITE_ENTITY_DISTINCTION_OK",run.stdout)

if __name__=="__main__":
    unittest.main()
