"""Operator-only whole-life I1 ECO-v1 descriptive metrics. Never feeds cognition.

Input is already authenticated by the caller. This does NOT verify M11/WAL
custody, experimental exposure, Q ablation or statistical independence.
"""
from collections import Counter
import math

NEEDS = ("energy", "food", "water", "integrity")
ACTIONS = ("se_deplacer", "collecter", "manger", "boire",
           "poser_une_pierre", "fabriquer_outil", "dormir", "attendre")


def _number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("invalid finite number: " + name)
    return float(value)


def _body(value, label):
    if type(value) is not dict or set(value) != set(NEEDS):
        raise ValueError(label + " must contain exactly four bodily needs")
    result = {name: _number(value[name], label + "." + name)
              for name in NEEDS}
    if any(not 0 <= v <= 100 for v in result.values()):
        raise ValueError(label + " body values out of 0..100")
    return result


def _conditions(setpoints, scales):
    if type(setpoints) is not dict or type(scales) is not dict:
        raise ValueError("setpoints and scales must be dicts")
    if set(setpoints) != set(NEEDS) or set(scales) != set(NEEDS):
        raise ValueError("exactly four setpoints and scales required")
    sp = {key: _number(setpoints[key], "setpoint." + key) for key in NEEDS}
    sc = {key: _number(scales[key], "scale." + key) for key in NEEDS}
    if any(not 0 <= x <= 100 for x in sp.values()) or any(x <= 0 for x in sc.values()):
        raise ValueError("invalid setpoint or scale")
    return sp, sc


def _deficits(body, setpoints, scales):
    return {name: min(1., max(0., (setpoints[name] - body[name]) /
                               scales[name])) for name in NEEDS}


def evaluate_life(*, initial_body, steps, horizon, status, setpoints, scales):
    """Return a descriptive horizon-wide summary; never a causal GO.

    steps: [{step:1, body:{...}, action:'...', status:'active'|'dead'},...]
    A death must be the final recorded step, never silently censored.
    """
    if type(horizon) is not int or not 1 <= horizon <= 300:
        raise ValueError("horizon must be a predeclared integer 1..300")
    if status not in ("active", "dead") or type(steps) is not list or not steps:
        raise ValueError("missing steps or invalid terminal status")
    if len(steps) > horizon:
        raise ValueError("trajectory exceeds fixed horizon")
    _body(initial_body, "initial_body")
    sp, sc = _conditions(setpoints, scales)
    areas = {key: 0. for key in NEEDS}
    actions = Counter()
    death_at = None
    for index, record in enumerate(steps, 1):
        if type(record) is not dict or set(record) != {"step", "body", "action", "status"}:
            raise ValueError("step schema mismatch")
        if type(record["step"]) is not int or record["step"] != index:
            raise ValueError("missing, repeated or reordered world step")
        if record["action"] not in ACTIONS:
            raise ValueError("action outside I1 physical primitive contract")
        if record["status"] not in ("active", "dead"):
            raise ValueError("unknown life status")
        if death_at is not None:
            raise ValueError("dead individual received an extra step")
        if record["status"] == "dead":
            death_at = index
        deficits = _deficits(_body(record["body"], "step.body"), sp, sc)
        for need in NEEDS:
            areas[need] += deficits[need]
        actions[record["action"]] += 1
    if status != steps[-1]["status"]:
        raise ValueError("terminal status conflicts with final event")
    if status == "active" and len(steps) != horizon:
        raise ValueError("active individual is neither dead nor at fixed horizon")
    if status == "dead" and death_at != len(steps):
        raise ValueError("death not recorded as final world step")
    remaining = horizon - len(steps)
    if status == "dead":
        for need in NEEDS:
            areas[need] += remaining  # predeclared worst deficit per remaining step
    elif remaining:
        raise ValueError("active life has missing terminal observations")
    assert all(0. <= areas[k] <= horizon + 1e-8 for k in NEEDS)
    out = {
        "schema": "individual-zero-i1-eco-v1-life-metrics/1",
        "horizon": horizon,
        "observed_steps": len(steps),
        "restricted_life_steps": len(steps),
        "mortality": status == "dead",
        "censored": status == "active",
        "deficit_area_by_need": {k: areas[k] for k in NEEDS},
        "deficit_fraction_by_need": {k: areas[k] / horizon for k in NEEDS},
        "deficit_area_total": sum(areas.values()),
        "actions": dict(sorted(actions.items())),
        "sleep_fraction": actions["dormir"] / len(steps),
        "productive_actions": {"collecter": actions["collecter"],
                               "manger": actions["manger"],
                               "boire": actions["boire"]},
        "learning_use_causal": "NOT_ESTABLISHED",
        "adaptive_benefit": "NOT_ESTABLISHED",
        "scope": "operator_descriptive_not_M11_proof_not_statistical_independence",
    }
    return out
