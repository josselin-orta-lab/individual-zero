"""Exploratory feasibility probes for an affordable consistent projection.

Declared exploratory (no protocol, no adoption, no World, no life). Two cheap
ideas are measured against the per-step projection on the #1146 fixtures:

1. local sensitivity: one accurate projection at the current body plus a
   finite-difference gradient, reused for every option's end state;
2. anchored grid: chunk_end accounting on geometric boundaries anchored at the
   decision time (1, 3, 7 ... 255) instead of restarting at each plan's end.

    python -m i3.archive.stage1.lab.stage1_affordable_projection_probes OUTPUT.json
"""
from __future__ import annotations

import json
import sys

from i3.archive.stage1.lab import stage1_candidate_g_projection_dependence as D
from i3.modules.mind import E, F, I, V, W

BOUNDS = (1, 3, 7, 15, 31, 63, 127, 255)
DELTAS = {"wait": (-.35, -.2, -.4, .2, 0.), "sleep": (3., -.35, -.4, 0., 4.),
          "drink": (-.5, -.2, 30., 0., 0.), "eat": (-.5, 12., -.4, 0., 0.)}
MOVE = (-2., -.2, -.4, 0., 0.)
PLANS = {"prefix": [MOVE], "plus_wait": [MOVE, DELTAS["wait"]],
         "plus_3_waits": [MOVE] + [DELTAS["wait"]] * 3,
         "drink": [MOVE, MOVE, DELTAS["drink"]], "eat": [MOVE, DELTAS["eat"]],
         "sleep": [DELTAS["sleep"]]}
BODIES = ([(80., 80., w, 80., 80.) for w in (10., 20., 30., 50.)]
          + [(80., f, 80., 80., 80.) for f in (10., 20., 40.)]
          + [(30., 30., 30., 80., 80.), (80.,) * 5, (50., 80., 80., 80., 30.)])


def _normalized(mind, ret):
    return sum((1 - g) * r for g, r in zip(mind.gammas, ret)) / 3


def anchored_project(mind, b, start):
    drift, restore = mind._drift
    th, b = mind.theta, list(b)
    ret, disc, dead, r, t = [0., 0., 0.], [1., 1., 1.], False, 0.0, start
    for bound in BOUNDS:
        if bound <= t:
            continue
        run, t = bound - t, bound
        if not dead:
            for c in (F, W, I):
                b[c] += run * drift[c]
            if restore is not None:
                need = max(0., th[E] - b[E]) / restore[0]
                if restore[1] > 0:
                    need = max(need, max(0., th[V] - b[V]) / restore[1])
                n = min(float(run), need)
                b[E] += n * restore[0]
                b[V] += n * restore[1]
                b[F] += n * restore[2]
            for c in range(5):
                b[c] = 0. if b[c] < 0 else 100. if b[c] > 100 else b[c]
            dead = b[F] <= 0 or b[W] <= 0 or b[I] <= 0
            r = -mind.d_max if dead else -mind.distress(mind.feats(b))
        for k, gk in enumerate(mind.gammas):
            g_run = gk ** run
            ret[k] += disc[k] * r * ((1 - g_run) / (1 - gk))
            disc[k] *= g_run
    for k, gk in enumerate(mind.gammas):
        ret[k] += disc[k] * (r / (1 - gk))
    return ret


def plan_value(mind, body, deltas, project):
    b, ret, disc, length = list(body), [0., 0., 0.], [1., 1., 1.], 0
    for d in deltas:
        for c in range(5):
            b[c] = min(100., max(0., b[c] + d[c]))
        length += 1
        r = -mind.distress(mind.feats(b))
        for k, gk in enumerate(mind.gammas):
            ret[k] += disc[k] * r
            disc[k] *= gk
    p = project(b, length)
    return sum((1 - gk) * (ret[k] + disc[k] * p[k]) for k, gk in enumerate(mind.gammas)) / 3


def local_sensitivity_probe():
    exact = D.make_mind("per_step")
    value = lambda b: _normalized(exact, exact.project(b, exact._drift)[0])
    worst = {k: 0.0 for k in DELTAS}
    for body in BODIES:
        v0 = value(body)
        grad = []
        for c in range(5):
            b = list(body)
            b[c] += 1.0
            grad.append(value(tuple(b)) - v0)
        for name, d in DELTAS.items():
            end = tuple(min(100., max(0., x + y)) for x, y in zip(body, d))
            linear = v0 + sum(g * (e - x) for g, e, x in zip(grad, end, body))
            worst[name] = max(worst[name], abs(value(end) - linear))
    return worst


def anchored_grid_probe():
    ref, exact = D.make_mind("reference"), D.make_mind("per_step")
    projections = {
        "truth": lambda b, L: exact.project(b, exact._drift)[0],
        "reference": lambda b, L: ref.project(b, ref._drift)[0],
        "anchored": lambda b, L: anchored_project(ref, b, L),
    }
    worst = {"reference": 0.0, "anchored": 0.0}
    for body in BODIES:
        vals = {name: {lab: plan_value(ref, body, plan, proj)
                       for lab, proj in projections.items()}
                for name, plan in PLANS.items()}
        names = list(PLANS)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                truth = vals[a]["truth"] - vals[b]["truth"]
                for lab in worst:
                    worst[lab] = max(worst[lab], abs((vals[a][lab] - vals[b][lab]) - truth))
    return worst


def run(out_path):
    report = {"schema": "i3-stage1-affordable-projection-probes/v1",
              "status": "EXPLORATORY_NOT_A_PROTOCOL", "world_access": False, "lives": 0,
              "local_sensitivity_max_error_by_option": local_sensitivity_probe(),
              "max_decision_bias_vs_per_step": anchored_grid_probe(),
              "decision_bias_limit_used_elsewhere": 1e-3}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1))
