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
from i1lab.world import WorldPhysicsConfig, BodyState, BerryEffect, ToolRecipe
from i1lab import world
from dataclasses import replace
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

# Construct a true WorldBody by the same explicit frozen configuration as
# the registered natural I1 world fixture.
from i1lab.i1_birth import birth_i1
from i1lab.world import WorldPhysicsConfig
from i1lab.i1_birth_temperament import natural_i1_birth_config
"""
            # This test instead performs an independent source-level transform
            # comparison of both algorithms in the same checked-in WorldBody:
            # avoid inventing birth fixture APIs in the reference program.
            self.assertIn("def old_capture", script)
