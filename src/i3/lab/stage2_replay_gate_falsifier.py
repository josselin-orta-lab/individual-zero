"""Stage 2.1 replay-gate software mechanism falsifier: one execution, no World.

Protocol: docs/STAGE2_REPLAY_GATE.md (frozen by #1212). Implementation
choices: docs/studies/stage2-replay-gate-software/IMPLEMENTATION_NOTES.md,
committed before execution.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
import sys

from ..modules import p13_replay_gate_mind as RG
from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from ..modules.genome import midpoint
from ..modules.mind import Mind

SCHEMA = "i3-stage2-replay-gate-software-falsifier/v1"
SEED = 211
PRIME = ((("se_deplacer",), (-2., -.2, -.4, 0., 0.)),
         (("attendre",), (-.35, -.2, -.4, .2, 0.)),
         (("dormir",), (3., -.35, -.4, 0., 4.)),
         (("boire",), (-.5, -.2, 35., 0., 0.)))
CYCLE = (PRIME[1][1], PRIME[0][1], PRIME[2][1])
LEVELS_EV = (20.0, 40.0, 60.0, 80.0)
LEVELS_1146 = (20.0, 30.0, 40.0, 50.0)
NEIGHBORS = ((False, ()), None, None, None)
HISTORIES = {
    "S0": {"audited_decisions": 50, "relevant_decisions": 0, "margin_sum": 0.0,
           "decisions_total": 59, "sleep_steps": 5},
    "S1": {"audited_decisions": 50, "relevant_decisions": 25, "margin_sum": 25 * 0.05,
           "decisions_total": 59, "sleep_steps": 5},
}
R3_SHARE = 0.90


def _clamp(x):
    return 0.0 if x < 0.0 else 100.0 if x > 100.0 else x


def _prime(mind):
    mind.map = {}
    for key, delta in PRIME:
        mind.effects.observe(key, delta)
    mind._drift = mind.drift()
    body = (80.0,) * 5
    for t in range(16):
        delta = CYCLE[t % 3]
        after = tuple(_clamp(b + d) for b, d in zip(body, delta))
        err = mind._td(body, after, False)
        mind.buffer.append((abs(err), tuple(body), tuple(after), False))
        body = after
    return mind


TEMPLATES = {}


def template(kind, mode="gate"):
    key = (kind, mode)
    if key not in TEMPLATES:
        if kind == "p13":
            TEMPLATES[key] = _prime(Mind(midpoint(), SEED,
                                         observer_decision_diagnostics=True))
        else:
            TEMPLATES[key] = _prime(RG.P13ReplayGateMind(
                midpoint(), SEED, mode=mode, observer_decision_diagnostics=True))
    return deepcopy(TEMPLATES[key])


def with_history(mind, name):
    for attr, value in HISTORIES[name].items():
        setattr(mind, attr, value)
    return mind


def sleep_bodies():
    return [(e, 80.0, 80.0, 80.0, v) for e in LEVELS_EV for v in LEVELS_EV]


def sleep_step(mind, body):
    before = tuple(_clamp(b - d) for b, d in zip(body, PRIME[2][1]))
    mind.last = (before, ("dormir",), "dormir", None)
    result = {"dead": False, "body": tuple(body), "moved": False}
    budget = CognitiveBudget(tuple(body), BodyLaws())
    base = CognitiveWork(cycles=2, simulated_steps=2 * len(mind.proj_chunks),
                         memory_items=len(mind.buffer) + len(mind.effects.stats) + 1)
    replays = mind.prepare_learning(result, budget)
    work = budget.work
    executed = mind.learn(result, replay_limit=replays or 0)
    return {"prepared": replays, "executed": executed, "work": work, "base": base,
            "values": [list(v) for v in mind.values],
            "buffer": [round(m[0], 15) for m in mind.buffer],
            "gate": getattr(mind, "last_gate", None),
            "gate_simulations": getattr(mind, "gate_simulations", 0)}


def decision_states():
    rows = []
    for channel in range(5):
        for level in LEVELS_1146:
            body = [80.0] * 5
            body[channel] = level
            body = tuple(body)
            rows.append(("water_here", body, {"body": body, "here": (True, ()),
                                              "neighbors": NEIGHBORS, "inventory": ()}))
            rows.append(("carried", body, {"body": body, "here": (False, ()),
                                           "neighbors": (None,) * 4,
                                           "inventory": (("mystery", 2),)}))
    return rows


def _decide(mind, cap):
    budget = CognitiveBudget(cap["body"], BodyLaws())
    action, param, work, info = mind.decide(cap, budget)
    scores = {w["option"]: w["total_score"]
              for w in (info.get("observer") or {}).get("score_witness", [])}
    return {"option": info.get("option"), "action": action, "param": param,
            "work": work, "scores": scores}


def static_isolation():
    tree = ast.parse(inspect.getsource(RG))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
        elif isinstance(node, ast.Import):
            modules.extend(a.name for a in node.names)
    banned = [m for m in modules
              if any(w in m.lower() for w in ("world", "runtime", "oracle", "lab"))]
    return modules, banned


def run(out_path=None):
    r0_mismatch, r0_work, renaming = [], [], []
    for kind, body, cap in decision_states():
        p13 = _decide(template("p13"), cap)
        gate_mind = template("gate", "gate")
        gate = _decide(gate_mind, cap)
        if (p13["option"], p13["action"], p13["param"]) != (
                gate["option"], gate["action"], gate["param"]) or p13["scores"] != gate["scores"]:
            r0_mismatch.append({"capture": kind, "body": body})
        extra = CognitiveWork(*(getattr(gate["work"], k) - getattr(p13["work"], k)
                                for k in ("cycles", "simulated_steps", "memory_items", "replays")))
        if extra not in (CognitiveWork(), CognitiveWork(cycles=1)):
            r0_work.append({"capture": kind, "body": body, "extra": extra.__dict__})
        if kind == "carried":
            other = template("gate", "gate")
            renamed_cap = dict(cap, inventory=(("enigme", 2),))
            again = _decide(other, renamed_cap)
            counters = lambda m: (m.audited_decisions, m.relevant_decisions,
                                  m.margin_sum, m.decisions_total)
            if (gate["option"], gate["scores"], gate["work"], counters(gate_mind)) != (
                    again["option"], again["scores"], again["work"], counters(other)):
                renaming.append({"body": body})
    modules, banned = static_isolation()
    r0 = {"decision_mismatches": r0_mismatch, "unexpected_extra_work": r0_work,
          "renaming_mismatches": renaming, "imports": modules,
          "banned_imports": banned,
          "pass": not (r0_mismatch or r0_work or renaming or banned)}

    r1_mismatch = []
    for name in HISTORIES:
        for body in sleep_bodies():
            fixed = sleep_step(template("p13"), body)
            forced = sleep_step(with_history(template("gate", "forced_open"), name), body)
            if (fixed["prepared"], fixed["executed"], fixed["values"], fixed["buffer"]) != (
                    forced["prepared"], forced["executed"], forced["values"], forced["buffer"]):
                r1_mismatch.append({"history": name, "body": body})
    r1 = {"mismatches": r1_mismatch, "pass": not r1_mismatch}

    rows, r4_violations = [], []
    for name in HISTORIES:
        for mode in ("gate", "zero_perceived_cost"):
            for body in sleep_bodies():
                mind = with_history(template("gate", mode), name)
                replay_work = mind._replay_work()
                out = sleep_step(mind, body)
                base = out["base"]
                overhead = {k: getattr(out["work"], k) - getattr(base, k)
                            - (out["prepared"] or 0) * getattr(replay_work, k)
                            for k in ("cycles", "simulated_steps", "memory_items", "replays")}
                if (overhead["cycles"] > 1 or overhead["memory_items"] != 0
                        or overhead["replays"] != 0 or out["gate_simulations"] > 2):
                    r4_violations.append({"history": name, "mode": mode, "body": body,
                                          "overhead": overhead})
                rows.append({"history": name, "mode": mode, "body": body,
                             "k": out["prepared"], "executed": out["executed"],
                             "gate": out["gate"], "overhead": overhead})

    def k_of(name, mode, body):
        return next(r["k"] for r in rows if r["history"] == name
                    and r["mode"] == mode and r["body"] == body)

    s0_replays = [k_of("S0", "gate", b) for b in sleep_bodies()]
    s1_high = [k_of("S1", "gate", b) for b in sleep_bodies() if b[0] >= 60 and b[4] >= 60]
    r2 = {"S0_replays_by_body": s0_replays, "S1_replays_high_EV": s1_high,
          "pass": all(k == 0 for k in s0_replays) and all(k >= 1 for k in s1_high)}

    ok = total = 0
    bodies = sleep_bodies()
    for a in bodies:
        for b in bodies:
            if a != b and a[0] <= b[0] and a[4] <= b[4]:
                total += 1
                ok += k_of("S1", "gate", a) <= k_of("S1", "gate", b)
    r3 = {"ordered_pairs": total, "non_increasing_when_EV_fall": ok,
          "share": ok / total if total else None,
          "pass": total > 0 and ok / total >= R3_SHARE}

    r4 = {"gate_overhead_violations": r4_violations,
          "audit_extra_work_violations": r0_work,
          "pass": not r4_violations and not r0_work}

    if not (r0["pass"] and r1["pass"] and r4["pass"]):
        verdict = "REPLAY_GATE_DEFECT"
    elif not (r2["pass"] and r3["pass"]):
        verdict = "REPLAY_GATE_NO_CAPACITY"
    else:
        verdict = "REPLAY_GATE_CAPACITY_SHOWN"

    summary = {}
    for name in HISTORIES:
        for mode in ("gate", "zero_perceived_cost"):
            ks = [r["k"] for r in rows if r["history"] == name and r["mode"] == mode]
            summary[f"{name}|{mode}"] = {"replays_by_body": ks,
                                         "mean_replays": sum(ks) / len(ks)}
    fixed_k = [sleep_step(template("p13"), b)["prepared"] for b in sleep_bodies()]
    result = {"schema": SCHEMA, "verdict": verdict, "R0": r0, "R1": r1, "R2": r2,
              "R3": r3, "R4": r4, "summary": summary,
              "fixed_replays_by_body": fixed_k,
              "sleep_bodies": sleep_bodies(),
              "rows": rows}
    text = json.dumps(result, sort_keys=True, separators=(",", ":"), default=str)
    if out_path:
        with open(out_path, "w") as fh:
            fh.write(text + "\n")
    return result


def main(argv):
    result = run(argv[1] if len(argv) > 1 else None)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"},
                     sort_keys=True, indent=1, default=str)[:8000])


if __name__ == "__main__":
    main(sys.argv)
