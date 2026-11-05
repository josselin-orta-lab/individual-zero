"""Run one I3 life: (code, genome, world spec, life seed) -> one exact history.

No retry, no reset, no action after death. The per-step trace is laboratory
custody (spec 'Traçabilité'), hashed in a chain; the mind never reads it.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from hashlib import sha256
import json
import time

from i3.modules.body import CognitiveWork, cognitive_cost
from i3.modules.genome import digest as genome_digest
from i3.runtime.provenance import build_manifest, digest
from i3.modules.mind import Mind
from i3.modules.world import World, WorldSpec


def run_life(genome: dict, spec: WorldSpec, life_seed: int, horizon: int,
             *, keep_trace: bool = False,
             protocol: str = "UNREGISTERED_ENGINEERING") -> dict:
    started = time.perf_counter()
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer horizon required")
    manifest = build_manifest(genome, spec, life_seed, horizon, protocol)
    manifest_id = digest(manifest)
    evidence_head = manifest_id
    totals = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
              for c in ("energy", "vigilance")}
    shortfall_steps = 0
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
        accounting = result["cognitive_accounting"]
        shortfall_steps += any(accounting[c]["unpaid"] > 1e-12 for c in totals)
        for channel in totals:
            for key in totals[channel]:
                totals[channel][key] += accounting[channel][key]
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
        evidence_head = digest({"previous": evidence_head, "record": record,
                                "work": asdict(work), "accounting": accounting})
        if keep_trace:
            record["cognitive_work"] = asdict(work)
            record["cognitive_accounting"] = accounting
            record["info"] = info
            trace.append(record)
    steps = world.t
    pending_energy, pending_vigilance = cognitive_cost(
        spec.laws, CognitiveWork(replays=mind.pending_replays))
    payment_status = ("SHORTFALL" if shortfall_steps else
                      "PENDING_REPLAY" if mind.pending_replays else
                      "SETTLED_FOR_DECLARED_WORK")
    out = {
        "manifest": manifest, "manifest_id": manifest_id,
        "evidence_head": evidence_head,
        "cognitive_accounting": {"totals": totals, "shortfall_steps": shortfall_steps,
                                 "pending_replays": mind.pending_replays,
                                 "pending_energy": pending_energy,
                                 "pending_vigilance": pending_vigilance,
                                 "status": payment_status},
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
    out["evidence_head"] = digest({"previous": evidence_head,
                                   "terminal": out["terminal"],
                                   "accounting": out["cognitive_accounting"]})
    if keep_trace:
        out["trace"] = trace
    out["run_elapsed_ms"] = round(1000.0 * (time.perf_counter() - started), 4)
    return out
