"""Laboratory probes. Never part of an individual, never a source of its beliefs.

``oracle_survival`` knows the whole world: it only tells whether a world is
livable at all (spec: 'sonde de faisabilité'). ``reference_survival`` sees
exactly what an I3 individual sees (``World.capture``) and pays a fixed small
cognitive cost; it sweeps space in lanes three cells apart, the systematic
coverage that one-cell perception allows. It estimates the ceiling of search
under the same body laws, so that a failure of I3 can be told apart from an
unlivable world.

Funding under body laws v2 (docs/COGNITIVE_FUNDING.md) is applied by
``_funded_step``: a probe acts only after paying ``PROBE_WORK`` from the same
reserves as an individual, never on credit. These rules only make the
probes executable under v2; they are not a revalidation of the probes as
scientific comparators (P2), and ``PROBE_WORK`` itself is unchanged.
"""
from __future__ import annotations

from collections import deque

from i3.modules.body import (ACTION_COSTS, CognitiveBudget, CognitiveWork, E, F, W, V,
                             cognitive_cost)
from i3.modules.world import DIRECTIONS, World

PROBE_WORK = CognitiveWork(cycles=2, simulated_steps=10, memory_items=50)
IDLE = CognitiveWork()
DELTA = {n: (dx, dy) for n, dx, dy in DIRECTIONS}


def _funded_step(w: World, act: str, par, *,
                 decision_work: CognitiveWork = PROBE_WORK,
                 learning_work: CognitiveWork = IDLE,
                 audit: list | None = None):
    """One probe step: prepaid decision, motor, then prepaid post-action bill.

    A P2 comparator can provide a prescribed external work tariff. The tariff
    never enters the probe's perception or strategy. If payment fails, recorded
    work is *not* fabricated: the probe is physically inactive or the post bill
    is skipped and the audit marks that tick UNMATCHED. The caller must never
    report an unmatched probe as a cost-equivalent comparator.

    With the default fixed PROBE_WORK and no audit, this preserves the v2 probe
    behavior already tested in P1.
    """
    if not isinstance(decision_work, CognitiveWork) or not isinstance(learning_work, CognitiveWork):
        raise TypeError("CognitiveWork bills required")
    before = w.body
    spent_decision = IDLE
    spent_learning = IDLE
    status = "MATCHED"
    budget = CognitiveBudget(w.body, w.laws)
    if decision_work == IDLE:
        # A physically inactive individual is not a license for free probing.
        result, done = w.step(None, None, IDLE), None
    elif not budget.try_spend(decision_work):
        result, done = w.step(None, None, IDLE), None
        status = "UNFUNDED_DECISION"
    else:
        spent_decision = decision_work
        if act != "dormir":
            bill_e, bill_v = cognitive_cost(w.laws, decision_work)
            left = budget.remaining
            if left[E] - ACTION_COSTS[act] < bill_e or left[V] < bill_v:
                act, par = "dormir", None
        result, done = w.step(act, par, decision_work), act
        if learning_work != IDLE and not result["dead"]:
            learning = CognitiveBudget(w.body, w.laws)
            if learning.try_spend(learning_work):
                w.pay_cognition(learning_work)
                result["body"] = w.body
                spent_learning = learning_work
            else:
                status = "UNFUNDED_POST_ACTION"
        elif learning_work != IDLE and result["dead"]:
            status = "TERMINAL_BEFORE_POST_ACTION"
    if audit is not None:
        audit.append({
            "t": w.t, "status": status,
            "before": before,
            "after": w.body,
            "command": done,
            "dead": bool(result["dead"]),
            "requested_decision": decision_work,
            "requested_learning": learning_work,
            "paid_decision": spent_decision,
            "paid_learning": spent_learning,
        })
    return result, done

def _step_towards(pos, target, passable):
    """First direction of a shortest path over cells accepted by ``passable``."""
    if pos == target:
        return None
    prev = {pos: None}
    q = deque([pos])
    while q:
        u = q.popleft()
        if u == target:
            break
        for n, dx, dy in DIRECTIONS:
            v = (u[0] + dx, u[1] + dy)
            if v not in prev and passable(v):
                prev[v] = (u, n)
                q.append(v)
    if target not in prev:
        return None
    cur = target
    while prev[cur][0] != pos:
        cur = prev[cur][0]
    return prev[cur][1]


def oracle_survival(spec, horizon: int, *, work_schedule=None, audit=None) -> int:
    """Steps survived by a full-knowledge greedy keeper (lab only)."""
    w = World(spec)
    good = {t for t, (fg, di) in w.effects.items() if fg > 0 and di >= 0}
    inside = lambda c: 0 <= c[0] < spec.width and 0 <= c[1] < spec.height
    while w.t < horizon and not w.dead:
        b, pos = w.body, w.pos
        act, par = "attendre", None
        waters = [c for c, s in w.water.items() if s.stock is None or s.stock > 0]
        foods = [c for c, p in w.food.items() if p.quantity > 0 and p.token in good]
        carried = [t for t in good if w.inventory.get(t, 0) > 0]
        def go(targets):
            t = min(targets, key=lambda c: abs(c[0] - pos[0]) + abs(c[1] - pos[1]))
            return _step_towards(pos, t, inside)
        if b[W] < 55 and waters:
            if pos in waters:
                act = "boire"
            else:
                act, par = "se_deplacer", go(waters)
        elif b[F] < 55 and (carried or foods):
            if carried:
                act, par = "manger", carried[0]
            elif pos in foods:
                act, par = "collecter", w.food[pos].token
            else:
                act, par = "se_deplacer", go(foods)
        elif b[E] < 30 or b[V] < 40:
            act = "dormir"
        if act == "se_deplacer" and par is None:
            act, par = "dormir", None
        if work_schedule is not None and w.t >= len(work_schedule):
            break  # comparison stops when the independent work witness ends
        decision, learning = (PROBE_WORK, IDLE) if work_schedule is None else work_schedule[w.t]
        _funded_step(w, act, par, decision_work=decision,
                     learning_work=learning, audit=audit)
    return w.t


def reference_survival(spec, horizon: int, *, work_schedule=None, audit=None) -> int:
    """Steps survived by a systematic lane-sweeping searcher with capture only."""
    w = World(spec)
    pos = (0, 0)                   # personal coordinates, like the individual
    cells: dict = {}               # rel -> (water, tokens) | None
    verdict: dict = {}             # token -> True (good) / False (bad)
    pending = None                 # (token, body before eating)
    while w.t < horizon and not w.dead:
        cap = w.capture()
        b = cap["body"]
        cells[pos] = (cap["here"][0], cap["here"][1])
        for (n, dx, dy), c in zip(DIRECTIONS, cap["neighbors"]):
            cells[(pos[0] + dx, pos[1] + dy)] = c
        inv = dict(cap["inventory"])
        known = lambda c: cells.get(c) is not None
        act, par = None, None
        water_cells = [c for c, v in cells.items() if v is not None and v[0]]
        def nearest(cs):
            return min(cs, key=lambda c: abs(c[0] - pos[0]) + abs(c[1] - pos[1]))
        good_carried = [t for t, n in inv.items() if n > 0 and verdict.get(t)]
        untested_carried = [t for t, n in inv.items() if n > 0 and t not in verdict]
        here_tokens = cells[pos][1]
        food_cells = [c for c, v in cells.items() if v is not None and
                      any(verdict.get(t, True) for t in v[1])]
        if b[W] < 60 and water_cells:
            act = "boire" if cells[pos][0] else ("se_deplacer",
                                                 _step_towards(pos, nearest(water_cells), known))
        elif b[F] < 60 and (good_carried or untested_carried):
            t = (good_carried or untested_carried)[0]
            act, par = "manger", t
            if t not in verdict:
                pending = (t, b)
        elif b[F] < 60 and food_cells:
            tok = [t for t in here_tokens if verdict.get(t, True)]
            if tok:
                act, par = "collecter", tok[0]
            else:
                act = ("se_deplacer", _step_towards(pos, nearest(food_cells), known))
        elif b[E] < 25 or b[V] < 40:
            act = "dormir"
        if act is None:
            frontier = [c for c, v in cells.items() if v is not None and any(
                (c[0] + dx, c[1] + dy) not in cells for _, dx, dy in DIRECTIONS)]
            lanes = [c for c in frontier if c[1] % 3 == 0] or frontier
            if lanes:
                act = ("se_deplacer", _step_towards(pos, nearest(lanes), known))
            else:
                act = "attendre"
        if isinstance(act, tuple):
            act, par = act
            if par is None:
                act, par = "dormir", None
        if work_schedule is not None and w.t >= len(work_schedule):
            break  # no unpaid or invented reference work beyond the witness
        decision, learning = (PROBE_WORK, IDLE) if work_schedule is None else work_schedule[w.t]
        res, done = _funded_step(w, act, par, decision_work=decision,
                                 learning_work=learning, audit=audit)
        if done == "se_deplacer":
            dx, dy = DELTA[par]
            pos = (pos[0] + dx, pos[1] + dy)
        if pending is not None and done == "manger":
            t, before = pending
            verdict[t] = res["body"][3] >= before[3] - 1e-9 and res["body"][F] > before[F]
        pending = None  # a meal that did not happen leaves no stale test
    return w.t
