"""Contradicted entity places cannot silently remain return targets in natural I1.

Controlled owner tests are not demonstrations of spontaneous choice or survival.
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


class ContradictedPlaceIntegration(unittest.TestCase):
    def test_generated_spatial_producer_and_owner_m11(self):
        with TemporaryDirectory(prefix="i1-373-") as tmp:
            built = Path(tmp) / "generated"
            generate(built)
            code = r"""
from copy import deepcopy
from types import SimpleNamespace
import inspect
from i1.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from i1.modules.spatial_memory import find_spatial_returns
from i1lab.stage11_runtime import Stage11Runtime

observer = "i1:373:first-person"
def owner():
    return GeographicExploration(GeographicExplorationConfig(
        version="i1-373-place-memory", novelty_weight=.15,
        max_distinct_sites=32, max_targets_per_cycle=1,
        observe_routes=True, refresh_surveys=True,
        remember_entities=True, max_place_candidates=3,
    ))
def capture(t, seen=False, site=(1,0), location=(0,0)):
    x,y = location
    return SimpleNamespace(
        t_monde=t, x=x, y=y,
        adjacent=tuple(SimpleNamespace(
            direction=d, x=x+dx, y=y+dy, passable=True, creature=False)
            for d,dx,dy in (("north",0,-1),("east",1,0),
                            ("south",0,1),("west",-1,0))),
        visible_entities=(
            (SimpleNamespace(entity_id="perceived:berry_a",
                entity_type="berry_a",x=site[0],y=site[1]),)
            if seen else ()),
    )
def perceive(geo,c):
    geo.observe_capture(c)
    return geo.observe_entities(c,observer_id=observer)
def recall(geo,t,places=None):
    return find_spatial_returns(
        origin=(0,0), visits=frozenset({(0,0)}), surveys=(),
        places=geo.place_memories if places is None else places,
        current_free_neighbors=frozenset({(1,0)}),
        current_world_step=t, max_candidates=3,
    )

# Short interval: a contrary local capture lowers confidence but still left
# enough quality (> .12) for the old Planning producer to offer this site.
short=owner()
perceive(short,capture(1,seen=True))
assert len(recall(short,2))==1
perceive(short,capture(2,seen=False))
site=short.place_memories[0]
assert site.last_seen_step==1 and site.contradiction_step==2
assert site.confidence>0 and site.contradictions==1
assert recall(short,2)==(), "Planning reconsidered a directly contradicted premise"

# The physical absence is retained as owner history through an M11 cold image.
image=short.export_causal_state()
cold=owner()
cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert cold.place_memories[0].contradictions==1
assert recall(cold,2)==()
for mode in ("future","duplicate"):
    forged=deepcopy(image)
    if mode=="future":
        forged["entity_places"][0]["contradiction_step"]=1000
    else:
        forged["entity_places"].append(deepcopy(forged["entity_places"][0]))
    original=cold.export_causal_state()
    try:cold.restore_causal_state(forged)
    except ValueError:pass
    else:raise AssertionError("forged M11 spatial image accepted: "+mode)
    assert cold.export_causal_state()==original

# Long interval: Planning reads the old frozen owner before an observation
# updates it. The aged target's quality is LOWER than post-contradiction
# confidence, so the previous freeze_places confidence-only guard passed it.
aged=owner()
perceive(aged,capture(1,seen=True))
aged_capture=capture(800,seen=False)
aged.observe_capture(aged_capture)
frozen=aged.place_memories
target=recall(aged,800,places=frozen)
assert len(target)==1 and .12<=target[0].confidence<=.14,target
aged.observe_entities(aged_capture,observer_id=observer)
assert aged.place_memories[0].contradiction_step==800
assert target[0].confidence <= aged.place_memories[0].confidence
aged.freeze_places(target)
assert aged.place_offered==(), "stale Phase-0 route survived fresh contradiction"
assert aged.place_memories[0].confidence>0, "must keep the historic memory"

# A subsequent genuinely perceived re-sighting makes the exact site relevant
# again, without manufacturing success, causal reward or motor eligibility.
perceive(short,capture(3,seen=True))
new=short.place_memories[0]
assert new.last_seen_step==3
assert new.contradiction_step==2
assert recall(short,4)
short.observe_capture(capture(4,seen=True))
fresh=recall(short,4)
short.observe_entities(capture(4,seen=True),observer_id=observer)
short.freeze_places(fresh)
assert len(short.place_offered)==1
assert short.place_offered[0].entity_id==new.entity_id

# An absence outside the sensor's local neighborhood is not a contradiction.
remote=owner()
perceive(remote,capture(1,seen=True))
perceive(remote,capture(2,location=(8,8)))
assert remote.place_memories[0].contradiction_step is None

# Real natural I1 producer uses this paid Planning -> owner-freeze chain.
source=inspect.getsource(Stage11Runtime._phase_hooks)
assert "find_spatial_returns(" in source
assert "geo.freeze_places(" in source
assert "geo.observe_entities(" in source
assert 'operation="geographic_route_search"' in source
assert 'operation="competition_register"' in source
print("I1_373_CONTRADICTED_SPATIAL_PREMISE_OK")
"""
            env = dict(
                os.environ,
                PYTHONPATH=os.pathsep.join((str(built), str(ROOT / "src"))),
                PYTHONDONTWRITEBYTECODE="1",
            )
            run = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=ROOT,
                env=env, capture_output=True, text=True,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_373_CONTRADICTED_SPATIAL_PREMISE_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
