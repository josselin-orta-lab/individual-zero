"""Differential first-person perception regression on generated I1, not I0.

Compare the optimized capture with a faithful reference implementation of
the former world resource observation algorithm. Never pass operator truth
to a living actor.
"""
import os
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
import os
import sys
import time
import statistics

def old_capture(world_body, t):
    current = world_body._position
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
    # Remote objects still participate in global indices. Sorting first
    # must retain the exact visible IDs after the preallocation filter.
    fake._water_sources.update(Position(i, 1) for i in range(1, 31))
    fake._creatures.update(Position(i, 2) for i in range(1, 31))
    fake._shelters.update(Position(i, 3) for i in range(1, 31))
    fake._water_sources.add(current)
    fake._creatures.add(current.moved("west"))
    fake._shelters.add(current.moved("south"))
    got = WorldBody.capture_local(fake,t_monde=case+1).as_dict()
    expected = old_capture(fake,case+1).as_dict()
    assert got == expected, (case,got,expected)

# Optional informational microbenchmark. No speed threshold is enforced.
# The source of each path is the current built I1 source and the frozen
# pre-change local-capture algorithm above, on identical synthetic worlds.
if os.environ.get("I1_CAPTURE_BENCH") == "1":
    kinds = ("berry_a", "berry_b", "wood", "stone")
    positions = [Position(x, y) for x in range(1, 31) for y in range(1, 31)]
    keys = [(p, kind) for p in positions for kind in kinds]
    random.Random(101).shuffle(keys)
    rows = []
    for requested in (16, 128, 512, 2000, 3400):
        resources = {key: 1 for key in keys[:requested]}
        center = Position(16, 16)
        # Keep locally perceivable resources in every workload.
        resources.update({
            (center, "berry_a"): 3,
            (center.moved("east"), "berry_b"): 2,
            (center.moved("north"), "stone"): 1,
        })
        fake = SimpleNamespace(
            _position=center, _resources=resources, _obstacles=set(),
            _water_sources={Position(1, 1), center},
            _creatures={Position(4, 4)}, _shelters=set(),
            _inventory={"berry_a": 2},
            _is_interior=lambda p: 0 <= p.x < 32 and 0 <= p.y < 32,
        )
        assert old_capture(fake, 1).as_dict() == WorldBody.capture_local(fake, t_monde=1).as_dict()
        older = []
        newer = []
        for rep in range(5):
            old_capture(fake, 1)
            WorldBody.capture_local(fake, t_monde=1)
            tests = [
                (lambda: old_capture(fake, 1), older),
                (lambda: WorldBody.capture_local(fake, t_monde=1), newer),
            ]
            if rep % 2:
                tests.reverse()
            for run_capture, samples in tests:
                start = time.perf_counter_ns()
                for _ in range(60):
                    run_capture()
                samples.append((time.perf_counter_ns() - start) / 60)
        old_ns = statistics.median(older)
        new_ns = statistics.median(newer)
        rows.append({
            "resource_rows": len(resources),
            "old_median_us": round(old_ns / 1000, 2),
            "optimized_median_us": round(new_ns / 1000, 2),
            "ratio": round(old_ns / new_ns, 2) if new_ns else None,
        })
    print("I1_LOCAL_CAPTURE_BENCH_JSON " + json.dumps({
        "kind": "synthetic_microbenchmark_not_scientific_evidence",
        "python": sys.version.split()[0],
        "repetitions": 5,
        "captures_per_repetition": 60,
        "workloads": rows,
    }, sort_keys=True))

print("I1_LOCAL_PERCEPTION_PARITY_OK")
"""
            process = subprocess.run(
                [sys.executable, "-c", script], capture_output=True, text=True,
                env={"PYTHONPATH": str(output),
                     "I1_CAPTURE_BENCH": os.environ.get("I1_CAPTURE_BENCH", "0")},
                check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("I1_LOCAL_PERCEPTION_PARITY_OK", process.stdout)
            if os.environ.get("I1_CAPTURE_BENCH") == "1":
                self.assertIn("I1_LOCAL_CAPTURE_BENCH_JSON ", process.stdout)
                print(process.stdout.split("I1_LOCAL_CAPTURE_BENCH_JSON ", 1)[1].splitlines()[0], flush=True)
