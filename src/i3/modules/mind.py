"""I3 mind: every learned product reaches the decision (spec section 'Cognition').

One step = perceive (noisy, capacity-limited) -> propose options -> self-model
rollouts scored by predicted innate distress -> Competition with stable
semantic accumulators (no privileged default, no tie abstention) -> Action
Control (admissibility + innate veto) -> learn from the perceived consequence.

The mind sees only ``World.capture()``. World tokens are relabelled by order
of first perception and positions are relative to birth, so no decision can
depend on a world name or absolute coordinate (renaming invariance).
"""
from __future__ import annotations

from collections import deque
from math import sqrt, tanh
import random

from .body import (ACTION_COSTS, CognitiveBudget, CognitiveFundingError,
                   CognitiveWork, E, F, W, I, V, capacities)
from .genome import channel_vector, validate
from .world import DIRECTIONS

DIRS = tuple((n, dx, dy) for n, dx, dy in DIRECTIONS)
LEAK, GAIN, THRESHOLD, RESIDUAL = 0.2, 1.0, 1.5, 0.5
MAX_WATER_OPTIONS, MAX_FOOD_OPTIONS, MAX_FRONTIER_OPTIONS = 2, 3, 2
REPLAYS_PER_SLEEP = 16
BELIEF_FLOOR = 0.05
# Innate self-projection: geometric chunks covering 255 future steps.
PROJECTION_CHUNKS = (1, 2, 4, 8, 16, 32, 64, 128)
VETO_INTEGRITY = 10.0


class EffectsModel:
    """Per (action, internal token) running mean/variance of the 5-channel delta."""

    def __init__(self):
        self.stats: dict[tuple, list] = {}   # key -> [n_eff, mean(5), count]

    def _upd(self, key, delta):
        s = self.stats.get(key)
        if s is None:
            s = self.stats[key] = [0.0, [0.0] * 5, 0]
        s[0] += 1.0
        s[2] += 1
        m = s[1]
        inv = 1.0 / s[0]
        for c in range(5):
            m[c] += (delta[c] - m[c]) * inv

    def observe(self, key, delta):
        self._upd(key, delta)
        if len(key) > 1:
            self._upd((key[0], None), delta)
        self._upd(("*",), delta)

    def predict(self, key):
        """(mean delta, uncertainty). Unknown key -> action level -> global."""
        s = self.stats.get(key)
        n = s[0] if s else 0.0
        for k in (key, (key[0], None), ("*",)):
            t = self.stats.get(k)
            if t and t[0] > 0:
                return t[1], 1.0 / sqrt(1.0 + n)
        return (0.0,) * 5, 1.0

    def known_positive(self, key, channel) -> bool:
        s = self.stats.get(key)
        return bool(s and s[2] > 0 and s[1][channel] > 0.0)

    def forget(self, factor):
        for s in self.stats.values():
            s[0] *= factor


class Mind:
    def __init__(self, genome: dict, life_seed: int,
                 *, effect_readout: str = "full",
                 observer_decision_diagnostics: bool = False,
                 score_addend_mode: str = "normal"):
        if type(observer_decision_diagnostics) is not bool:
            raise TypeError("observer diagnostics flag must be bool")
        self.observer_decision_diagnostics = observer_decision_diagnostics
        if score_addend_mode not in (
                "normal", "discard_curiosity_bonus",
                "discard_risk_penalty", "discard_both_bonus_terms"):
            raise ValueError("unknown P5c score addend intervention")
        self.score_addend_mode = score_addend_mode
        if effect_readout not in (
                "full", "blind_predictions", "blind_action_predictions",
                "blind_sleep_forecast", "blind_sources", "blind_all",
                "action_agnostic_prior"):
            raise ValueError("unknown effect-model readout intervention")
        self.effect_readout = effect_readout
        validate(genome)
        g = genome["genes"]
        self.theta = channel_vector(genome, "theta")
        self.p = channel_vector(genome, "p")
        self.w = channel_vector(genome, "w")
        self.gammas = (g["gamma1"], g["gamma2"], g["gamma3"])
        self.alpha = g["alpha"]
        self.beta_u = g["beta_u"] * (1.0 + 0.5 * g["temperament.exploration"])
        self.lambda_r = g["lambda_r"] * (1.0 + 0.5 * g["temperament.threat_sensitivity"])
        self.kappa0 = 0.05 * (1.0 + g["temperament.exploration"])
        self.inertia = 0.3 * (1.0 + g["temperament.goal_protection"]) / 2.0
        self.n_base, self.h_max = g["n_base"], g["h_max"]
        self.m_max = int(round(g["m_max"]))
        self.belief_rate = g["belief_rate"]
        self.d_max = sum(self.w)
        # Learned residual on top of the innate self-projection (starts at zero).
        self.values = [[0.0] * 6 for _ in self.gammas]
        self.proj_chunks = PROJECTION_CHUNKS
        self.rng = random.Random(f"i3-life:{life_seed}")
        self._budget_rng = random.Random(f"i3-budget-order:{life_seed}")
        self.effects = EffectsModel()
        self.map: dict[tuple, tuple] = {}   # rel pos -> last (water, tokens) | None for edge
        # rel pos -> [observations, water belief, {token: belief}]; beliefs are
        # recency-weighted (rate = gene belief_rate): a source that dried up
        # stops being believed, at a speed the lineage can select (P1.3).
        self.hist: dict[tuple, list] = {}
        self.visible: tuple = ()
        self.pos = (0, 0)
        self.tokens: dict[str, str] = {}     # world token -> internal id
        self.external: dict[str, str] = {}   # internal id -> world token
        self.acc: dict[str, float] = {}
        self.intention: str | None = None
        self.buffer: deque = deque()
        self.last = None
        self._drift = ((0.0,) * 5, None)

    # ---- innate distress and learned value --------------------------------
    def feats(self, b):
        th, p = self.theta, self.p
        out = [1.0]
        for c in range(5):
            x = (th[c] - b[c]) / th[c]
            out.append(x ** p[c] if x > 0.0 else 0.0)
        return out

    def distress(self, phi):
        w = self.w
        return w[0] * phi[1] + w[1] * phi[2] + w[2] * phi[3] + w[3] * phi[4] + w[4] * phi[5]

    def _read_effect_prediction(self, key):
        """Read the SAME paid, personally learned model, or blind its output.

        No hidden world laws or physics outcomes are injected; the actual
        effect statistics remain stored and priced even in blind modes.
        """
        if self.effect_readout in ("blind_predictions", "blind_all"):
            return (0.0,) * 5, 1.0
        return self.effects.predict(key)

    def _read_plan_prediction(self, key):
        """Mask only simulated action transitions, not passive/sleep drift."""
        if self.effect_readout == "blind_action_predictions":
            return (0.0,) * 5, 1.0
        if self.effect_readout == "action_agnostic_prior":
            # The existing global ('*',) running mean is updated from the
            # individual's OWN paid lived outcomes. Its learned magnitude
            # can support an intact forecast interface, but its value and
            # uncertainty contain NO information about the proposed action
            # label or token. No new estimate, heuristic, privileged facts,
            # or unbilled work is introduced.
            return self.effects.predict(("*",))
        return self._read_effect_prediction(key)

    def _read_source_sign(self, key, channel) -> bool:
        if self.effect_readout in ("blind_sources", "blind_all"):
            return False
        return self.effects.known_positive(key, channel)

    def drift(self):
        """Personally observed passive drift, plus personally observed sleep.

        Food, water and integrity drift as observed while waiting (else as
        the mean of any step). Energy and vigilance are not frozen: if sleep
        has ever restored energy, the projection lets sleep bring them back
        up to their distress thresholds, paying sleep's extra food cost.
        (P1 froze them, so any plan ending tired looked costly forever.)
        """
        wait, _ = self._read_effect_prediction(("attendre",))
        sleep = (None if self.effect_readout in (
                     "blind_predictions", "blind_sleep_forecast", "blind_all")
                 else self.effects.stats.get(("dormir",)))
        restore = None
        if sleep and sleep[2] > 0 and sleep[1][E] > 0:
            restore = (sleep[1][E], max(0.0, sleep[1][V]), sleep[1][F] - wait[F])
        return (0.0, wait[F], wait[W], wait[I], 0.0), restore

    def project(self, b, drift, budget=None):
        """Innate self-projection over 255 future steps (chunks 1, 2, 4 ... 128).

        Death (a vital channel at zero) counts as maximal distress forever.
        """
        if budget is not None:
            # One paid model integration unit per geometric projection chunk.
            budget.spend(CognitiveWork(simulated_steps=len(self.proj_chunks)))
        drift, restore = drift
        th = self.theta
        b = list(b)
        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = False
        r = 0.0
        for run in self.proj_chunks:
            if not dead:
                for c in (F, W, I):
                    b[c] += run * drift[c]
                if restore is not None:
                    need = max(0.0, th[E] - b[E]) / restore[0]
                    if restore[1] > 0.0:
                        need = max(need, max(0.0, th[V] - b[V]) / restore[1])
                    n = min(float(run), need)
                    b[E] += n * restore[0]
                    b[V] += n * restore[1]
                    b[F] += n * restore[2]
                for c in range(5):
                    b[c] = 0.0 if b[c] < 0.0 else 100.0 if b[c] > 100.0 else b[c]
                dead = b[F] <= 0.0 or b[W] <= 0.0 or b[I] <= 0.0
                r = -self.d_max if dead else -self.distress(self.feats(b))
            for k, gk in enumerate(self.gammas):
                g_run = gk ** run
                ret[k] += disc[k] * r * ((1.0 - g_run) / (1.0 - gk))
                disc[k] *= g_run
        for k, gk in enumerate(self.gammas):
            ret[k] += disc[k] * (r / (1.0 - gk))
        return ret, b

    def value(self, k, phi, proj):
        wk = self.values[k]
        return proj[k] + sum(a * c for a, c in zip(wk, phi))

    # ---- perception -------------------------------------------------------
    def _internal(self, token):
        t = self.tokens.get(token)
        if t is None:
            t = self.tokens[token] = f"tok{len(self.tokens)}"
            self.external[t] = token
        return t

    def perceive(self, cap, miss):
        here = cap["here"]
        seen = [(self.pos, here[0], tuple(self._internal(t) for t in here[1]))]
        for (name, dx, dy), cell in zip(DIRS, cap["neighbors"]):
            q = (self.pos[0] + dx, self.pos[1] + dy)
            if cell is None:
                self.map[q] = None
                continue
            water, toks = cell
            if (water or toks) and self.rng.random() < miss:
                water, toks = False, ()
            seen.append((q, water, tuple(self._internal(t) for t in toks)))
        for q, water, toks in seen:
            self.map[q] = (water, toks)
            h = self.hist.get(q)
            rho = self.belief_rate
            if h is None:
                h = self.hist[q] = [0, 1.0 if water else 0.0, {}]
                for t in toks:
                    h[2][t] = 1.0
            else:
                h[1] += rho * ((1.0 if water else 0.0) - h[1])
                for t in toks:
                    if t not in h[2]:
                        h[2][t] = 0.0
                for t in h[2]:
                    h[2][t] += rho * ((1.0 if t in toks else 0.0) - h[2][t])
            h[0] += 1
        self.visible = tuple(q for q, _, _ in seen)
        inv = tuple((self._internal(k), n) for k, n in cap["inventory"])
        return inv

    def presence(self, q, token=None):
        """Belief that water (or a token) is at q now, from personal observation."""
        if q in self.visible:
            c = self.map[q]
            return 1.0 if (c[0] if token is None else token in c[1]) else 0.0
        h = self.hist.get(q)
        if h is None:
            return 0.0
        b = h[1] if token is None else h[2].get(token, 0.0)
        return b if b > BELIEF_FLOOR else 0.0

    # ---- options ----------------------------------------------------------
    def _bfs(self, limit):
        """Distances over known passable cells from current position."""
        start = self.pos
        prev = {start: None}
        dist = {start: 0}
        order = []
        q = deque([start])
        while q:
            u = q.popleft()
            order.append(u)
            if dist[u] >= limit:
                continue
            for _, dx, dy in DIRS:
                v = (u[0] + dx, u[1] + dy)
                if v in dist or self.map.get(v) is None:
                    continue
                dist[v] = dist[u] + 1
                prev[v] = u
                q.append(v)
        return order, dist, prev

    def _first_dir(self, target, prev):
        cur = target
        while prev[cur] != self.pos:
            cur = prev[cur]
        for name, dx, dy in DIRS:
            if (self.pos[0] + dx, self.pos[1] + dy) == cur:
                return name
        raise RuntimeError("path does not start at an adjacent cell")

    def options(self, inv, body, horizon):
        self._unknown = {}
        self._presence = {}
        here = self.map[self.pos]
        carried = [t for t, n in inv if n > 0]
        opts = [("dormir", [("dormir",)], None), ("attendre", [("attendre",)], None)]
        if here[0]:
            opts.append(("boire", [("boire",)], None))
        for t in here[1]:
            opts.append((f"collecter:{t}", [("collecter", t)], ("collecter", t)))
            opts.append((f"collecter+manger:{t}", [("collecter", t), ("manger", t)],
                         ("collecter", t)))
        for t in carried:
            opts.append((f"manger:{t}", [("manger", t)], ("manger", t)))
        if body[E] >= ACTION_COSTS["se_deplacer"]:
            for name, dx, dy in DIRS:
                if self.map.get((self.pos[0] + dx, self.pos[1] + dy)) is not None:
                    opts.append((f"move:{name}", [("se_deplacer",)], ("se_deplacer", name)))
            order, dist, prev = self._bfs(horizon * horizon)
            nw = nf = nx = 0
            for cell in order[1:]:
                d = dist[cell]
                info = self.map[cell]
                rel = f"{cell[0]},{cell[1]}"
                travel = [("se_deplacer",)] * d
                h = self.hist.get(cell)
                if h is not None and h[1] > BELIEF_FLOOR and nw < MAX_WATER_OPTIONS:
                    pw = self.presence(cell)
                    if pw > 0.0:
                        nw += 1
                        oid = f"goto-boire:{rel}"
                        self._presence[oid] = (pw, travel)
                        opts.append((oid, travel + [("boire",)],
                                     ("se_deplacer", self._first_dir(cell, prev))))
                for t in (h[2] if h is not None else ()):
                    pf = self.presence(cell, t)
                    if pf > 0.0 and nf < MAX_FOOD_OPTIONS:
                        nf += 1
                        oid = f"goto-manger:{t}:{rel}"
                        self._presence[oid] = (pf, travel)
                        opts.append((oid, travel + [("collecter", t), ("manger", t)],
                                     ("se_deplacer", self._first_dir(cell, prev))))
                unknown = sum((cell[0] + dx, cell[1] + dy) not in self.map for _, dx, dy in DIRS)
                if nx < MAX_FRONTIER_OPTIONS and unknown:
                    nx += 1
                    self._unknown[f"explorer:{rel}"] = unknown
                    opts.append((f"explorer:{rel}", travel, ("se_deplacer", self._first_dir(cell, prev))))
        return opts

    # ---- self-model ---------------------------------------------------------
    def _sources(self, inv):
        """Best personal belief that a source known to work is available.

        Water: drinking must have personally raised water, then the best
        presence belief over remembered water places. Food: a token whose
        eating personally raised food, carried (1.0) or remembered somewhere.
        """
        p_water = 0.0
        if self._read_source_sign(("boire",), W):
            for q, h in self.hist.items():
                if h[1] > BELIEF_FLOOR:
                    p_water = max(p_water, self.presence(q))
        carried = {t for t, n in inv if n > 0}
        p_food = 0.0
        source_stats = (() if self.effect_readout in ("blind_sources", "blind_all")
                        else self.effects.stats.items())
        for key, st in source_stats:
            if key[0] == "manger" and key[1] is not None and st[2] > 0 and st[1][F] > 0:
                t = key[1]
                if t in carried:
                    return p_water, 1.0
                for q, h in self.hist.items():
                    if t in h[2]:
                        p_food = max(p_food, self.presence(q, t))
        return p_water, p_food

    def simulate(self, body, plan, horizon, budget):
        """Predicted normalised discounted distress (negated) per horizon, steps used.

        Consecutive travel moves are simulated as chunks of at most ``horizon``
        moves (one simulated step each); at most ``horizon`` simulated steps
        are run before bootstrapping on the learned value. Low vigilance
        shortens both, so a degraded mind sees less far (spec: capacities).
        """
        b = list(body)
        steps = 0
        if self.observer_decision_diagnostics:
            # Readout sidecar from existing, funded simulated transitions.
            self._observer_first_forecast = None
        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = False
        u_max = 0.0
        i, n = 0, len(plan)
        while i < n and steps < horizon:
            budget.spend(CognitiveWork(simulated_steps=1))
            key = plan[i]
            run = 1
            if key[0] == "se_deplacer":
                while i + run < n and plan[i + run] == key and run < horizon:
                    run += 1
            i += run
            mean, u = self._read_plan_prediction(key)
            if self.observer_decision_diagnostics and steps == 0:
                self._observer_first_forecast = {
                    "action_key": tuple(key),
                    "delta": tuple(mean), "uncertainty": u}
            u_max = max(u_max, u)
            for c in range(5):
                x = b[c] + run * mean[c]
                b[c] = 0.0 if x < 0.0 else 100.0 if x > 100.0 else x
            steps += 1
            if b[F] <= 0.0 or b[W] <= 0.0 or b[I] <= 0.0:
                dead = True
            r = -self.d_max if dead else -self.distress(self.feats(b))
            for k, gk in enumerate(self.gammas):
                g_run = gk ** run
                ret[k] += disc[k] * r * ((1.0 - g_run) / (1.0 - gk))
                disc[k] *= g_run
            if dead:
                break
        phi = self.feats(b)
        proj = None if dead else self.project(b, self._drift, budget)[0]
        out = 0.0
        for k, gk in enumerate(self.gammas):
            boot = -self.d_max / (1.0 - gk) if dead else self.value(k, phi, proj)
            out += (1.0 - gk) * (ret[k] + disc[k] * boot)
        return out / 3.0, steps, u_max

    # ---- decision -------------------------------------------------------------
    @staticmethod
    def _observer_option_families(options):
        """Categorize first-person proposed/evaluated choices, read only."""
        families = {"resource": 0, "movement": 0, "exploration": 0, "rest": 0}
        for oid in options:
            if oid in ("dormir", "attendre"):
                families["rest"] += 1
            elif oid.startswith("explorer:"):
                families["exploration"] += 1
            elif oid.startswith("move:"):
                families["movement"] += 1
            else:
                families["resource"] += 1
        return families

    def decide(self, cap, budget: CognitiveBudget):
        body = cap["body"]
        if tuple(body) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        self.last = None
        # Three block allocations: perception/memory service, option/model
        # preparation, and control/outcome bookkeeping. Not CPU instructions.
        slots = (len(self.buffer) + 2 * len(self.map) + len(self.effects.stats)
                 + len(self.tokens) + len(self.external) + len(self.acc)
                 + sum(len(v) for v in self.values) + 12
                 + len(cap["inventory"]) + sum(len(c[1]) for c in
                   (cap["here"], *cap["neighbors"]) if c is not None))
        if not budget.try_spend(CognitiveWork(cycles=3, memory_items=slots)):
            info = {"option": None, "funding": "NO_PROCESSING_BUDGET"}
            if self.observer_decision_diagnostics:
                info["observer"] = {
                    "offered_options": 0, "scored_options": 0,
                    "rejected_controls": 0, "decision_outcome": "no_processing_budget",
                    "offered_families": self._observer_option_families(()),
                    "scored_families": self._observer_option_families(()),
                    "pre_body": tuple(body), "score_witness": []}
            return None, None, budget.work, info
        cycles, horizon, miss = capacities(body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        opts = self.options(inv, body, horizon)
        observer_offered = len(opts)
        observer_families = (self._observer_option_families(o[0] for o in opts)
                             if self.observer_decision_diagnostics else None)
        # No privileged default when the budget covers only a subset.
        self._budget_rng.shuffle(opts)
        p_water, p_food = self._sources(inv)
        phi_now = self.feats(body)
        self._drift = self.drift()
        # Anticipated need: distress of channels without a known source, on the
        # body projected over the longest value horizon (capped at 255 steps).
        reach = min(255, int(1.0 / (1.0 - self.gammas[2])))
        ahead = [min(100.0, max(0.0, body[c] + reach * self._drift[0][c])) for c in range(5)]
        phi_ahead = self.feats(ahead)
        need_w = self.w[W] * phi_ahead[1 + W] * (1.0 - p_water)
        need_f = self.w[F] * phi_ahead[1 + F] * (1.0 - p_food)
        urgency = self.kappa0 + need_w + need_f
        # Personal base rate of resources per perceived cell (Laplace).
        seen = [c for c in self.map.values() if c is not None]
        p_res = (sum(1 for c in seen if c[0] or c[1]) + 1.0) / (len(seen) + 2.0)
        scored = []
        score_witness = [] if self.observer_decision_diagnostics else None
        sim_steps = 0
        for oid, plan, _ in opts:
            try:
                j, steps, u = self.simulate(body, plan, horizon, budget)
                first_forecast = (self._observer_first_forecast
                                  if self.observer_decision_diagnostics else None)
                sim_steps += steps
                if oid in self._presence:
                    # A plan is usable only when both branches were funded.
                    pr, travel = self._presence[oid]
                    j_fail, steps_fail, _ = self.simulate(body, travel, horizon, budget)
                    sim_steps += steps_fail
                    j = pr * j + (1.0 - pr) * j_fail
            except CognitiveFundingError:
                break  # Partial computation stays paid; no uncomputed score.
            # Need-relevant curiosity: only what could answer an unmet need is
            # boosted by that need; other uncertainty gets general curiosity.
            if oid.startswith("explorer:"):
                # Expected chance that the cells revealed there hold a resource.
                u = min(1.0, self._unknown[oid] * p_res)
                relevance = urgency
            elif any(k[0] == "boire" for k in plan):
                relevance = self.kappa0 + need_w
            elif any(k[0] == "manger" for k in plan):
                relevance = self.kappa0 + need_f
            else:
                relevance = self.kappa0
            # Both original addends are genuinely computed under the
            # unchanged funded decision loop, even when a P5c intervention
            # discards one AFTER computation, before action competition.
            curiosity = self.beta_u * u * relevance
            risk_penalty = 0.0
            if any(k[0] == "manger" for k in plan):
                # Prudence scales with the vulnerability of the threatened
                # channel: an unknown meal matters more when integrity is low.
                risk_penalty = -self.lambda_r * u * (
                    self.w[I] * phi_now[1 + I] + self.kappa0)
            use_curiosity = self.score_addend_mode not in (
                "discard_curiosity_bonus", "discard_both_bonus_terms")
            use_risk = self.score_addend_mode not in (
                "discard_risk_penalty", "discard_both_bonus_terms")
            bonus = (curiosity if use_curiosity else 0.0) + (
                risk_penalty if use_risk else 0.0)
            scored.append((oid, j + bonus))
            if self.observer_decision_diagnostics:
                # Audit values computed in the ORIGINAL paid score path.
                # Suppressed addends remain visible but not effective.
                score_witness.append({
                    "option": oid, "base_return": j,
                    "curiosity_bonus_computed": curiosity,
                    "risk_penalty_computed": risk_penalty,
                    "curiosity_bonus_applied": curiosity if use_curiosity else 0.0,
                    "risk_penalty_applied": risk_penalty if use_risk else 0.0,
                    "curiosity_risk_bonus": bonus, "total_score": j + bonus,
                    "uncertainty": u, "first_forecast": first_forecast})
        if not scored:
            info = {"option": None, "funding": "NO_FUNDED_SCORE"}
            if self.observer_decision_diagnostics:
                info["observer"] = {
                    "offered_options": observer_offered, "scored_options": 0,
                    "rejected_controls": 0, "decision_outcome": "no_funded_score",
                    "offered_families": observer_families,
                    "scored_families": self._observer_option_families(()),
                    "pre_body": tuple(body), "score_witness": score_witness}
            return None, None, budget.work, info
        winner, used = self._compete(scored, cycles, budget)
        ranked = [winner] + [o for o, _ in sorted(scored, key=lambda x: -x[1]) if o != winner]
        by_id = {o[0]: o for o in opts}
        rejected_controls = 0
        for oid in ranked:
            action, param = self._admit(by_id[oid], inv, budget.remaining)
            if action is not None:
                break
            rejected_controls += 1
        else:
            info = {"option": None, "funding": "NO_FUNDED_MOTOR"}
            if self.observer_decision_diagnostics:
                info["observer"] = {
                    "offered_options": observer_offered,
                    "scored_options": len(scored),
                    "rejected_controls": rejected_controls,
                    "decision_outcome": "control_rejected",
                    "offered_families": observer_families,
                    "scored_families": self._observer_option_families(o for o, _ in scored),
                    "pre_body": tuple(body), "score_witness": score_witness}
            return None, None, budget.work, info
        self.intention = oid if len(by_id[oid][1]) > 1 else None
        work = budget.work
        key = by_id[oid][1][0]
        self.last = (body, key, action, param)
        info = {"option": oid, "cycles": used, "horizon": horizon,
                "simulated": work.simulated_steps, "urgency": round(urgency, 6),
                "funding": "FUNDED", "scored_options": len(scored),
                "top": sorted(((round(s, 6), o) for o, s in scored), reverse=True)[:3]}
        if self.observer_decision_diagnostics:
            info["observer"] = {
                "offered_options": observer_offered,
                "scored_options": len(scored),
                "rejected_controls": rejected_controls,
                "decision_outcome": "action_admitted",
                "admitted_action": action,
                "offered_families": observer_families,
                "scored_families": self._observer_option_families(o for o, _ in scored),
                "pre_body": tuple(body), "score_witness": score_witness}
        return action, param, work, info

    def _compete(self, scored, cycles, budget=None):
        vals = [s for _, s in scored]
        mean = sum(vals) / len(vals)
        sd = sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
        ev = {o: (tanh((s - mean) / sd) if sd > 1e-9 else 0.0) for o, s in scored}
        acc = {o: self.acc.get(o, 0.0) for o, _ in scored}
        winner = None
        used = 0
        for _ in range(cycles):
            if budget is not None and not budget.try_spend(CognitiveWork(cycles=1)):
                break
            used += 1
            crossed = []
            for o, _s in scored:
                acc[o] = max(0.0, (1.0 - LEAK) * acc[o] + GAIN * ev[o])
                th = THRESHOLD * (1.0 - self.inertia if o == self.intention else 1.0)
                if acc[o] >= th:
                    crossed.append(((acc[o] - th) / th, o))
            if crossed:
                best = max(m for m, _ in crossed)
                tied = sorted(o for m, o in crossed if m == best)
                winner = self._tie(tied)
                break
        if winner is None:  # no abstention by default: best evaluated option
            best = max(vals)
            winner = self._tie(sorted(o for o, s in scored if s >= best - 1e-12))
        for o in acc:
            acc[o] = 0.0 if o == winner else acc[o] * RESIDUAL
        self.acc = acc
        return winner, used

    def _tie(self, tied):
        if len(tied) == 1:
            return tied[0]
        if self.intention in tied:
            return self.intention
        return tied[self.rng.randrange(len(tied))]

    def _admit(self, opt, inv, body):
        """Action Control: physical admissibility + innate integrity veto."""
        oid, plan, first = opt
        key = plan[0]
        if key[0] != "dormir" and body[E] < ACTION_COSTS[key[0]]:
            return None, None
        carried = {t for t, n in inv if n > 0}
        here = self.map[self.pos]
        if key[0] == "se_deplacer":
            name = first[1]
            dx, dy = {n: (a, b) for n, a, b in DIRS}[name]
            if body[E] < ACTION_COSTS["se_deplacer"] or self.map.get(
                    (self.pos[0] + dx, self.pos[1] + dy)) is None:
                return None, None
            return "se_deplacer", name
        if key[0] == "boire":
            return ("boire", None) if here[0] else (None, None)
        if key[0] == "collecter":
            return ("collecter", self.external[key[1]]) if key[1] in here[1] else (None, None)
        if key[0] == "manger":
            if key[1] not in carried:
                return None, None
            s = (None if self.effect_readout == "blind_all"
                 else self.effects.stats.get(("manger", key[1])))
            if body[I] <= VETO_INTEGRITY and s and s[2] > 0 and s[1][I] < 0:
                return None, None
            return "manger", self.external[key[1]]
        return key[0], None

    # ---- learning -------------------------------------------------------------
    def prepare_learning(self, result, budget: CognitiveBudget):
        """Allocate learned updates and replay BEFORE any of them execute.

        Return None if the base update cannot be paid. Replay is optional work,
        limited by both actual reserves and available memories. Runtime debits
        this allowance before calling the pure learned-update helper below.
        """
        if result["dead"] or self.last is None:
            return None
        if tuple(result["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("learning allowance must match the current body")
        # Effects/TD update and memory/forgetting service, with both projections.
        base = CognitiveWork(cycles=2, simulated_steps=2 * len(self.proj_chunks),
                             memory_items=len(self.buffer) + len(self.effects.stats) + 1)
        if not budget.try_spend(base):
            return None
        limit = min(REPLAYS_PER_SLEEP, self.m_max, len(self.buffer) + 1)
        replays = 0
        if self.last[2] == "dormir":
            for _ in range(limit):
                if not budget.try_spend(CognitiveWork(
                        simulated_steps=2 * len(self.proj_chunks), replays=1)):
                    break
                replays += 1
        return replays

    def learn(self, result, *, replay_limit=0):
        """Pure outcome pipeline; runtime must prepay the learned-update block.

        Position bookkeeping belongs to the already-funded control block.
        The helper alone is not a laboratory execution or payment authority.
        """
        if result["dead"] or self.last is None:
            return 0
        self.observe_outcome(result)
        return self.learn_from_outcome(result, replay_limit=replay_limit)

    def observe_outcome(self, result):
        """Update position from the paid movement outcome, independently of learning."""
        _, _, action, param = self.last
        if action == "se_deplacer" and result["moved"]:
            dx, dy = {n: (a, b) for n, a, b in DIRS}[param]
            self.pos = (self.pos[0] + dx, self.pos[1] + dy)

    def learn_from_outcome(self, result, *, replay_limit=0, replay_retention=True):
        """Prepaid learned updates only; controls must retain orientation.

        P5a replay_retention=False genuinely computes replay on a detached
        snapshot, discarding ONLY its persistent effect on values/buffer.
        It does not skip or pretend to pay for any replay computation.
        """
        if type(replay_limit) is not int or not 0 <= replay_limit <= REPLAYS_PER_SLEEP:
            raise ValueError("invalid prepaid replay count")
        if type(replay_retention) is not bool:
            raise TypeError("replay_retention must be a boolean")
        if result["dead"] or self.last is None:
            return 0
        before, key, action, param = self.last
        after = result["body"]
        real_key = key if action != "se_deplacer" else ("se_deplacer",)
        self.effects.observe(real_key, [a - b for a, b in zip(after, before)])
        dead = bool(result["dead"])
        err = self._td(before, after, dead)
        self.buffer.append((abs(err), tuple(before), tuple(after), dead))
        while len(self.buffer) > self.m_max:
            self.buffer.popleft()
        replays = 0
        if action == "dormir":
            # Replay retention is a separate intervention from the ordinary
            # paid base TD update. The deepcopy is observer bookkeeping, not
            # fake mind work; _td genuinely runs on the detached state.
            if not replay_retention and replay_limit:
                from copy import deepcopy
                replay_mind = deepcopy(self)
            else:
                replay_mind = self
            best = sorted(range(len(replay_mind.buffer)),
                          key=lambda i: -replay_mind.buffer[i][0])
            for i in best[:replay_limit]:
                _, a, b, d = replay_mind.buffer[i]
                replay_mind.buffer[i] = (
                    abs(replay_mind._td(a, b, d)), a, b, d)
                replays += 1
        if after[V] < 50.0:
            self.effects.forget(1.0 - 0.02 * (1.0 - after[V] / 50.0))
        return replays

    def _td(self, b0, b1, dead):
        phi0, phi1 = self.feats(b0), self.feats(b1)
        drift = self.drift()
        p0 = self.project(b0, drift)[0]
        p1 = None if dead else self.project(b1, drift)[0]
        r = -self.d_max if dead else -self.distress(phi1)
        norm = sum(x * x for x in phi0)
        errs = 0.0
        for k, gk in enumerate(self.gammas):
            target = r + gk * (-self.d_max / (1.0 - gk) if dead else self.value(k, phi1, p1))
            delta = target - self.value(k, phi0, p0)
            step = self.alpha * delta / norm
            wk = self.values[k]
            for j in range(6):
                wk[j] += step * phi0[j]
            errs += abs(delta) * (1.0 - gk)
        return errs / 3.0
