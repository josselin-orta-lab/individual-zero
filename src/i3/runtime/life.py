"""Run one I3 life: (code, genome, world spec, life seed) -> one exact history.

No retry, no reset, no action after death. The per-step trace is laboratory
custody (spec 'Traçabilité'), hashed in a chain; the mind never reads it.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import time

from i3.modules.genome import digest as genome_digest
from i3.modules.mind import Mind
from i3.modules.world import World, WorldSpec


def run_life(genome: dict, spec: WorldSpec, life_seed: int, horizon: int,
             *, keep_trace: bool = False) -> dict:
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer horizon required")
    world = World(spec)
    mind = Mind(genome, life_seed)
    head = sha256(json.dumps([genome_digest(genome), spec.name, life_seed, horizon],
                             separators=(",", ":")).encode()).hexdigest()
    trace = []
    actions: Counter = Counter()
    drinks = meals = 0
    first_drink = None
    elapsed = 0.0
    while world.t < horizon and not world.dead:
        t0 = time.perf_counter()
        action, param, work, info = mind.decide(world.capture())
        result = world.step(action, param, work)
        mind.learn(result)
        elapsed += time.perf_counter() - t0
        actions[action] += 1
        if action == "boire":
            drinks += 1
            first_drink = first_drink or world.t
        elif action == "manger":
            meals += 1
        record = {"t": world.t, "action": action, "param": param,
                  "option": info["option"], "body": list(result["body"]),
                  "pos": list(world.pos), "dead": list(result["dead"])}
        head = sha256((head + json.dumps(record, separators=(",", ":"),
                                         sort_keys=True)).encode()).hexdigest()
        if keep_trace:
            record["info"] = info
            trace.append(record)
    steps = world.t
    out = {
        "world": spec.name, "life_seed": life_seed, "horizon": horizon,
        "genome": genome_digest(genome),
        "steps_lived": steps,
        "terminal": "dead" if world.dead else "censored",
        "death_causes": list(world.dead),
        "drinks": drinks, "meals": meals, "first_drink_step": first_drink,
        "actions": dict(sorted(actions.items())),
        "final_body": [round(x, 6) for x in world.body],
        "mean_step_ms": round(1000.0 * elapsed / max(1, steps), 4),
        "trace_head": head,
    }
    if keep_trace:
        out["trace"] = trace
    return out
