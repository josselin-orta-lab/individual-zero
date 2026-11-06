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

from i3.modules.body import CognitiveBudget, CognitiveWork
from i3.modules.genome import digest as genome_digest
from i3.runtime.provenance import build_manifest, digest
from i3.modules.mind import Mind
from i3.modules.world import World, WorldSpec


def run_life(genome: dict, spec: WorldSpec, life_seed: int, horizon: int,
             *, keep_trace: bool = False,
             protocol: str = "UNREGISTERED_ENGINEERING",
             learning_mode: str = "normal",
             observer_mind_digest: bool = False,
             effect_readout: str = "full",
             observer_decision_diagnostics: bool = False) -> dict:
    started = time.perf_counter()
    if learning_mode not in (
            "normal", "shadow_discard", "discard_effects",
            "discard_values", "discard_replay"):
        raise ValueError("unknown P4b/P5a learning intervention")
    if type(observer_mind_digest) is not bool:
        raise TypeError("observer_mind_digest must be bool")
    if type(observer_decision_diagnostics) is not bool:
        raise TypeError("observer_decision_diagnostics must be bool")
    if effect_readout not in (
            "full", "blind_predictions", "blind_sources", "blind_all"):
        raise ValueError("unknown P5b effect readout")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer horizon required")
    manifest = build_manifest(genome, spec, life_seed, horizon, protocol)
    manifest_id = digest(manifest)
    evidence_head = manifest_id
    totals = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
              for c in ("energy", "vigilance")}
    shortfall_steps = 0
    world = World(spec)
    mind = Mind(genome, life_seed, effect_readout=effect_readout,
                observer_decision_diagnostics=observer_decision_diagnostics)
    head = sha256(json.dumps([genome_digest(genome), spec.name, life_seed, horizon],
                             separators=(",", ":")).encode()).hexdigest()
    trace = []
    actions: Counter = Counter()
    drinks = meals = 0
    first_drink = None
    elapsed = 0.0
    learning_updates = replays_done = inactive_steps = 0
    observer_counts = {
        "no_processing_budget": 0, "no_funded_score": 0,
        "control_rejected": 0, "action_admitted": 0,
        "offered_options": 0, "scored_options": 0,
        "rejected_controls": 0,
        "offered_families": {k: 0 for k in
            ("resource", "movement", "exploration", "rest")},
        "scored_families": {k: 0 for k in
            ("resource", "movement", "exploration", "rest")}}
    while world.t < horizon and not world.dead:
        t0 = time.perf_counter()
        allowance = CognitiveBudget(world.body, world.laws)
        action, param, work, info = mind.decide(world.capture(), allowance)
        if observer_decision_diagnostics:
            diagnostic = info["observer"]
            observer_counts[diagnostic["decision_outcome"]] += 1
            for item in ("offered_options", "scored_options", "rejected_controls"):
                observer_counts[item] += diagnostic[item]
            for kind in ("offered_families", "scored_families"):
                for family, value in diagnostic[kind].items():
                    observer_counts[kind][family] += value
        if work != allowance.work:
            raise ValueError("declared decision bill does not match consumed allowance")
        result = world.step(action, param, work)
        before_learning = result["body"]
        learning = CognitiveBudget(before_learning, world.laws)
        replay_limit = None
        if not result["dead"] and mind.last is not None:
            # Included in the prepaid control block, not in a learning ablation.
            mind.observe_outcome(result)
            replay_limit = mind.prepare_learning(result, learning)
        if replay_limit is not None:
            post_audit = world.pay_cognition(learning.work)
            result["body"] = world.body
            # P4b: run exactly the prepaid outcome-model computation on
            # a detached mind, then discard its new learned state. The actual
            # mind still keeps ordinary perception, spatial beliefs and the
            # paid sensorimotor orientation update. No fictitious cognition
            # is billed: the shadow computation really executes.
            if learning_mode == "shadow_discard":
                from copy import deepcopy
                target = deepcopy(mind)
            else:
                target = mind
            # Development-only selective ablations: run the normal prepaid
            # computation first and restore only one targeted state component.
            # Costs are not manually adjusted, and paid sensorimotor/spatial
            # state is not rolled back.
            if learning_mode == "discard_effects":
                from copy import deepcopy
                preserved = deepcopy(mind.effects)
            elif learning_mode == "discard_values":
                preserved = [v[:] for v in mind.values]
            else:
                preserved = None
            replays = target.learn_from_outcome(
                result, replay_limit=replay_limit,
                replay_retention=(learning_mode != "discard_replay"))
            if learning_mode == "discard_effects":
                mind.effects = preserved
            elif learning_mode == "discard_values":
                mind.values = preserved
            if replays != replay_limit:
                raise RuntimeError("executed replay count differs from prepaid count")
            learning_updates += 1
            replays_done += replays
        else:
            post_audit = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
                          for c in totals}
        phases = {
            "decision": {"work": asdict(work), "accounting": result["cognitive_accounting"],
                         "body_before": list(allowance.body),
                         "body_after_debit": list(allowance.remaining)},
            "learning": {"work": asdict(learning.work), "accounting": post_audit,
                         "body_before": list(before_learning),
                         "body_after_debit": list(world.body)},
        }
        accounting = {c: {k: result["cognitive_accounting"][c][k] + post_audit[c][k]
                           for k in totals[c]} for c in totals}
        work = CognitiveWork(*(getattr(work, k) + getattr(learning.work, k)
                               for k in ("cycles", "simulated_steps", "memory_items", "replays")))
        shortfall_steps += any(accounting[c]["unpaid"] > 1e-12 for c in totals)
        for channel in totals:
            for key in totals[channel]:
                totals[channel][key] += accounting[channel][key]
        elapsed += time.perf_counter() - t0
        actions[action if action is not None else "physical_inactivity"] += 1
        inactive_steps += action is None
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
                                "work": asdict(work), "accounting": accounting,
                                "funding_phases": phases})
        if keep_trace:
            record["cognitive_work"] = asdict(work)
            record["cognitive_accounting"] = accounting
            record["funding_phases"] = phases
            record["info"] = info
            trace.append(record)
    steps = world.t
    out = {
        "manifest": manifest, "manifest_id": manifest_id,
        "evidence_head": evidence_head,
        "cognitive_accounting": {"schema": "i3-cognitive-funding/v2",
                                 "totals": totals, "shortfall_steps": shortfall_steps,
                                 "pending_replays": 0, "pending_energy": 0.0,
                                 "pending_vigilance": 0.0,
                                 "learning_updates": learning_updates,
                                 "replays_executed": replays_done,
                                 "inactive_steps": inactive_steps,
                                 "status": "SETTLED_FOR_DECLARED_WORK"},
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
    if effect_readout != "full" or observer_decision_diagnostics:
        out["effect_readout"] = effect_readout
    if observer_decision_diagnostics:
        out["observer_decision_diagnostics"] = dict(observer_counts)
    if learning_mode != "normal" or observer_mind_digest:
        out["learning_intervention"] = learning_mode
        # Component ablations retain the base outcome pipeline and discard
        # only one declared learned substate; only full shadow_discard drops
        # the entire outcome update. This counter is pipeline executions,
        # NOT proof each individual learned component survived.
        out["retained_outcome_learning_updates"] = (
            learning_updates if learning_mode != "shadow_discard" else 0)
        out["shadow_discarded_outcome_updates"] = (
            learning_updates if learning_mode == "shadow_discard" else 0)
    if observer_mind_digest:
        # Observer-only postmortem/life-end signature. Never enters Mind.decide.
        # Tokens and locations are internal, relative to this individual's
        # first-person history; no external world schedule is exposed.
        effects = [[list(k), v] for k, v in
                   sorted(mind.effects.stats.items(), key=lambda item: repr(item[0]))]
        spatial = [[list(pos), hist] for pos, hist in sorted(mind.hist.items())]
        out["outcome_model_sha256"] = digest({
            "values": mind.values, "effects": effects,
            "buffer": list(mind.buffer)})
        out["spatial_beliefs_sha256"] = digest({
            "hist": spatial,
            "map": [[list(pos), cell] for pos, cell in sorted(mind.map.items())]})
        out["observer_internal_position"] = list(mind.pos)
    out["evidence_head"] = digest({"previous": evidence_head,
                                   "terminal": out["terminal"],
                                   "accounting": out["cognitive_accounting"]})
    if keep_trace:
        out["trace"] = trace
    out["run_elapsed_ms"] = round(1000.0 * (time.perf_counter() - started), 4)
    return out
