"""External first-person water/replay chronology. Never part of Mind or World.

The observer reads only state already learned by Mind after paid decisions and
a callback with immutable replay indices BEFORE the already prepaid TD update.
The callback's return value is ignored. Nothing observed is fed into decisions.
Observer processing overhead is outside the simulated organism's energy bill,
not falsely claimed as physically paid cognition.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite

from i3.modules.body import W

SCHEMA = "i3-stage2.1-replay-water-chronology/v1"


def _digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def _water_personal(mind):
    """Only personally perceived water at relative cells, never World stocks."""
    records = []
    for pos, hist in sorted(mind.hist.items()):
        n, p_water, _tokens = hist
        if type(n) is not int or n < 0 or not isfinite(p_water):
            raise ValueError("invalid personal history in read-only witness")
        records.append([list(pos), n, float(p_water)])
    return records


class ReplayWaterObserver:
    """One-use per-step begin/replay/commit, with no mutation of the organism."""

    def __init__(self):
        self.steps = []
        self._pending = None

    def prepare(self, *, mind, cap, info, action, param):
        if self._pending is not None:
            raise RuntimeError("replay-water witness cannot skip a commit")
        if not isinstance(cap, dict) or not isinstance(info, dict):
            raise TypeError("requires actual first-person capture and paid decision")
        history = _water_personal(mind)
        water_effect = mind.effects.stats.get(("boire",))
        summary = {
            "step": len(self.steps) + 1,
            "capture_water_before_decision": float(cap["body"][W]),
            "capture_here_water": bool(cap["here"][0]),
            "capture_neighbor_water_cells": sum(
                bool(x[0]) for x in cap["neighbors"] if x is not None),
            "personal_position": list(mind.pos),
            "personal_water_beliefs": history,
            "personal_water_belief_sha256": _digest(history),
            "personally_known_water_cells": sum(
                belief > 0.5 for _, _, belief in history),
            "personally_learned_drink_effect":
                None if water_effect is None else {
                    "samples": water_effect[2],
                    "water_gain_mean": water_effect[1][W]},
            "decision_option": info.get("option"),
            "decision_funding": info.get("funding"),
            "action": action,
            "param": param,
            "replay_count_prepaid": 0,
            "replay_memory_indices": [],
            "replay_priority_indices": [],
            "pre_replay_priority_sha256": None,
        }
        self._pending = summary
        return None

    def replay(self, selected, ranked, priorities):
        if self._pending is None:
            raise RuntimeError("no paid learning step open for replay witness")
        if self._pending["replay_priority_indices"]:
            raise RuntimeError("second replay selection in same step")
        if (type(selected) not in (tuple,list) or
                type(ranked) not in (tuple,list) or
                type(priorities) not in (tuple,list)):
            raise TypeError("replay identity witness requires immutable indices")
        if len(ranked) != len(priorities) or set(ranked) != set(range(len(ranked))):
            raise ValueError("invalid ranked replay buffer")
        if (len(set(selected)) != len(selected) or
                any(type(i) is not int or i not in ranked for i in selected)):
            raise ValueError("invalid replay chosen indices")
        self._pending["replay_count_prepaid"] = len(selected)
        self._pending["replay_memory_indices"] = list(selected)
        self._pending["replay_priority_indices"] = list(ranked[:len(selected)])
        self._pending["pre_replay_priority_sha256"] = _digest(priorities)

    def commit(self, *, mind, world, result, replay_limit, post_audit):
        if self._pending is None:
            raise RuntimeError("replay-water witness missing prepare")
        event = self._pending
        self._pending = None
        if replay_limit is None:
            if event["replay_count_prepaid"] != 0:
                raise RuntimeError("replay executed without prepaid learning")
        elif (event["replay_count_prepaid"] != replay_limit and
              replay_limit != 0):
            raise RuntimeError("observer count does not match prepaid replays")
        event["paid_replays_actual"] = 0 if replay_limit is None else replay_limit
        event["replay_subset_differs_from_priority"] = (
            set(event["replay_memory_indices"]) !=
            set(event["replay_priority_indices"]))
        event["world_step_after_paid_learning"] = world.t
        event["body_water_after_physics_and_learning"] = world.body[W]
        # Water uptake is measured against passive metabolic decay, using
        # only the realized World transaction, never hidden water stocks.
        uptake = (world.body[W] -
                  max(0.0, event["capture_water_before_decision"] -
                      world.laws.water_decay)
                  if event["action"] == "boire" else None)
        event["water_uptake_above_decay"] = uptake
        event["positive_water_uptake"] = uptake is not None and uptake > 1e-9
        event["dead"] = bool(result["dead"])
        event["death_causes"] = list(result["dead"])
        event["paid_learning_energy"] = post_audit["energy"]["paid"]
        event["paid_learning_vigilance"] = post_audit["vigilance"]["paid"]
        after = _water_personal(mind)
        event["personal_water_belief_after_learning_sha256"] = _digest(after)
        self.steps.append(event)

    def report(self):
        if self._pending is not None:
            raise RuntimeError("incomplete observed step")
        return {
            "schema": SCHEMA,
            "scope": "EXTERNAL_OBSERVER_NO_ORGANISM_INPUT",
            "lived_steps": len(self.steps),
            "replay_count_actual": sum(x["paid_replays_actual"] for x in self.steps),
            "content_changed_from_priority_opportunities": sum(
                x["replay_subset_differs_from_priority"] for x in self.steps),
            "steps": self.steps,
        }


def first_divergences(a, b):
    """Only same-step matched comparisons; stop each channel at first mismatch.

    After the first trajectory difference, comparisons describe diverged
    individuals, never equal starting internal states or causal mediation.
    """
    if a["schema"] != SCHEMA or b["schema"] != SCHEMA:
        raise ValueError("source report schema differs")
    channels = {
        "replay_memory_indices": lambda x: x["replay_memory_indices"],
        "personal_water_belief": lambda x: x["personal_water_belief_sha256"],
        "decision": lambda x: (x["decision_option"], x["action"], x["param"]),
        "body_water": lambda x: x["capture_water_before_decision"],
    }
    common = min(len(a["steps"]), len(b["steps"]))
    first = {key: None for key in channels}
    for i in range(common):
        for key, val in channels.items():
            if first[key] is None and val(a["steps"][i]) != val(b["steps"][i]):
                first[key] = i + 1
    return {
        "common_observed_steps": common,
        "first_differences": first,
        "same_step_number_does_not_imply_same_internal_state": True,
        "fixed_count_causal_mediation_claim": False,
    }
