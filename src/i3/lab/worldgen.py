"""World families for I3 (spec: 'World and World-family generator').

A family is a generator plus a seed range. Development uses the 'dev' seeds;
seeds at or above RESERVED_FROM are never used while developing and serve
only preregistered held-out checks. Token names, positions and effects are
drawn per world, so no name or place carries a role (renaming invariance).
"""
from __future__ import annotations

import random

from i3.modules.world import FoodPatch, WaterSource, WorldSpec

RESERVED_FROM = 1_000_000
FAMILIES = ("dev", "E", "R")


def _name(rng):
    return "".join(rng.choice("bcdfghjklmnpqrstvwxz") + rng.choice("aeiouy") for _ in range(3))


def _cell(rng, w, h, spawn, lo, hi, taken):
    for _ in range(500):
        q = (rng.randrange(w), rng.randrange(h))
        d = abs(q[0] - spawn[0]) + abs(q[1] - spawn[1])
        if lo <= d <= hi and q not in taken:
            taken.add(q)
            return q
    raise RuntimeError("could not place a resource")


def generate(family: str, seed: int, *, development: bool = True) -> WorldSpec:
    """One world of a family. ``development=True`` refuses reserved seeds."""
    if family not in FAMILIES:
        raise ValueError("unknown world family")
    if development and seed >= RESERVED_FROM:
        raise ValueError("reserved seeds are for preregistered held-out checks only")
    rng = random.Random(f"i3-world:{family}:{seed}")
    if family == "R":
        return _revision_world(rng, seed)
    w, h = rng.randint(10, 18), rng.randint(10, 18)
    spawn = (rng.randrange(1, w - 1), rng.randrange(1, h - 1))
    taken = {spawn}
    water = {}
    n_water = rng.randint(1, 3)
    for i in range(n_water):
        q = _cell(rng, w, h, spawn, 3 if i == 0 else 4, 9 if i == 0 else w + h, taken)
        if rng.random() < 0.5:
            water[q] = WaterSource(gain=rng.uniform(25.0, 40.0))
        else:
            stock = rng.randint(2, 5)
            water[q] = WaterSource(gain=rng.uniform(25.0, 40.0), stock=stock, max_stock=stock,
                                   restock_every=rng.choice((0, 8, 12, 20)))
    good, bad = _name(rng), _name(rng)
    effects = {good: (rng.uniform(8.0, 15.0), 0.0),
               bad: (rng.uniform(3.0, 8.0), -rng.uniform(4.0, 12.0))}
    food = {}
    for i in range(rng.randint(2, 4)):
        token = good if i == 0 or rng.random() < 0.6 else bad
        q = _cell(rng, w, h, spawn, 2, w + h, taken)
        qty = rng.randint(2, 4)
        food[q] = FoodPatch(token, qty, qty, restock_every=rng.randint(8, 20))
    body = (rng.uniform(65, 85), rng.uniform(40, 60), rng.uniform(35, 55),
            rng.uniform(85, 100), 100.0)
    return WorldSpec(name=f"{family}-{seed}", width=w, height=h, spawn=spawn, body=body,
                     water=water, food=food, token_effects=effects)


def _revision_world(rng, seed) -> WorldSpec:
    """Family R (strategy revision): a near finite well that runs dry for good,
    a far unlimited one out of sight, food near both. Livable by design."""
    w, h = rng.randint(12, 18), rng.randint(10, 16)
    spawn = (rng.randrange(1, w - 1), rng.randrange(1, h - 1))
    taken = {spawn}
    near = _cell(rng, w, h, spawn, 1, 2, taken)
    far = _cell(rng, w, h, spawn, 8, 14, taken)
    stock = rng.randint(3, 6)
    water = {near: WaterSource(gain=rng.uniform(25.0, 35.0), stock=stock, max_stock=stock,
                               restock_every=0),
             far: WaterSource(gain=rng.uniform(25.0, 35.0))}
    token = _name(rng)
    food = {}
    for anchor in (near, far):
        for _ in range(20):
            q = (anchor[0] + rng.randint(-2, 2), anchor[1] + rng.randint(-2, 2))
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in taken:
                taken.add(q)
                food[q] = FoodPatch(token, 3, 3, restock_every=rng.randint(8, 14))
                break
    body = (rng.uniform(70, 85), rng.uniform(55, 70), rng.uniform(45, 60),
            rng.uniform(90, 100), 100.0)
    return WorldSpec(name=f"R-{seed}", width=w, height=h, spawn=spawn, body=body,
                     water=water, food=food, token_effects={token: (rng.uniform(10.0, 14.0), 0.0)})
