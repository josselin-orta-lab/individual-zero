"""Differential first-person perception regression on generated I1, not I0.

Compare the optimized capture with a faithful reference implementation of
the former world resource observation algorithm. Never pass operator truth
to a living actor.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LocalPerceptionOptimizationTests(unittest.TestCase):
    def test_generated_world_matches_original_capture_across_resource_layouts(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "built"
            run = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            script = r"""
from i1lab.world import WorldBody, WorldLayout, Position, VisibleEntity
from types import SimpleNamespace
from i1lab import world
import json
import random

def old_capture(world_body, t):
    current = world_body.position
    def resource_kinds(position):
        return tuple(sorted(kind for (p, kind), qty in world_body._resources.items()
                            if p == position and qty > 0))
    adjacent = []
    for direction in ("north", "south", "east", "west"):
        p = current.moved(direction)
        adjacent.append(world.LocalCell(
            direction=direction, position=p,
            passable=world_body._is_interior(p) and p not in world_body._obstacles,
            water_source=p in world_body._water_sources,
            resources=resource_kinds(p),
            creature=p in world_body._creatures,
        ))
    entities = []
    for index, p in enumerate(sorted(world_body._water_sources)):
        entities.append(VisibleEntity("water_source:" + str(index), "water_source", p, {}))
    for (p, kind), qty in sorted(world_body._resources.items(),
                                key=lambda r: (r[0][0].x, r[0][0].y, r[0][1])):
        if qty > 0:
            entities.append(VisibleEntity(f"{kind}:{p.x}:{p.y}", kind, p, {"quantity":qty}))
    for kind, ps in (("creature",world_body._creatures),("shelter",world_body._shelters)):
        for index,p in enumerate(sorted(ps)):
            entities.append(VisibleEntity(f"{kind}:{index}", kind,p,{}))
    entities = [x for x in entities if abs(x.position.x-current.x)+abs(x.position.y-current.y)<=1]
    return world.LocalWorldState(
        t_monde=t, position=current,
        current_water_source=current in world_body._water_sources,
        current_resources=resource_kinds(current),
        adjacent=tuple(adjacent),
        visible_entities=tuple(sorted(entities,key=lambda e:(e.entity_type,e.entity_id))),
        inventory=dict(sorted(world_body._inventory.items()))
    )

# Exercise the real method with a read-only physical owner stub. The method
# reads exactly these attributes and cannot dispatch or mutate the world.
rng = random.Random(246)
for case in range(100):
    current = Position(rng.randrange(1,31), rng.randrange(1,31))
    resources = {}
    for i in range(200 + case):
        p = Position(rng.randrange(1,31), rng.randrange(1,31))
        kind = ("berry_a","berry_b","wood","stone")[i%4]
        resources[p,kind] = rng.randrange(0,4)
    for delta,kind in [((0,0),"berry_a"),((1,0),"berry_b"),((-1,0),"wood"),((0,1),"stone")]:
        p=Position(current.x+delta[0],current.y+delta[1])
        resources[p,kind] = 2
    fake = SimpleNamespace(
        _position=current, _resources=resources, _obstacles=set(),
        _water_sources={Position(2,2),current}, _creatures={Position(3,3)},
        _shelters={current.moved("north")}, _inventory={"berry_a":case%3},
        _is_interior=lambda p: 0 <= p.x < 32 and 0 <= p.y < 32
    )
    got = WorldBody.capture_local(fake,t_monde=case+1).as_dict()
    expected = old_capture(fake,case+1).as_dict()
    assert got == expected, (case,got,expected)
print("I1_LOCAL_PERCEPTION_PARITY_OK")
"""
            process = subprocess.run(
                [sys.executable, "-c", script], capture_output=True, text=True,
                env={"PYTHONPATH": str(output)}, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("I1_LOCAL_PERCEPTION_PARITY_OK", process.stdout)
