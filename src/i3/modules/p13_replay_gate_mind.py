"""Stage 2.1 replay gate: P1.3 that replays only when it is worth its price in D.

Protocol: docs/STAGE2_REPLAY_GATE.md (frozen by #1212). Opt-in software
candidate; not registered in runtime/life.py.

One change to P1.3. During a sleep step, each prepaid replay runs only if its
expected viability gain exceeds its cost, both expressed through the same
distress-based value. The gain comes from the individual's own record of when
its learned residual values changed its decisions:

    G = r_hat * m_hat * H,
    g_i = G * |delta_i| / sum_j |delta_j|,
    c = V_sleep(body) - V_sleep(body - w).

Decisions, Competition, Action Control, curiosity, prudence, base learning,
the effects model and P1.3's replay priority order are unchanged. `simulate`
and `decide` are verbatim copies of the P1.3 reference paths, plus residual
bookkeeping and a paid post-decision audit that cannot alter the choice.
"""
from __future__ import annotations

from .body import (CognitiveBudget, CognitiveFundingError, CognitiveWork,
                   capacities, cognitive_cost)
from .mind import (F, I, Mind, REPLAYS_PER_SLEEP, W)

POLICY = "p13_replay_gate_v1"
MODES = ("gate", "zero_perceived_cost", "forced_open")
TOP_MARGIN = 1e-12
E_INDEX, V_INDEX = 0, 4


def strict_top(scores: dict):
    if not scores:
        return None
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    if len(ranked) == 1 or ranked[0][1] - ranked[1][1] > TOP_MARGIN:
        return ranked[0][0]
    return None


class P13ReplayGateMind(Mind):
    def __init__(self, genome: dict, life_seed: int, *, mode: str = "gate",
                 observer_decision_diagnostics: bool = False,
                 observer_full_competition: bool = False,
                 effect_readout: str = "full",
                 score_addend_mode: str = "normal"):
        if mode not in MODES:
            raise ValueError("unknown replay-gate mode")
        if effect_readout != "full" or score_addend_mode != "normal":
            raise ValueError("the replay gate keeps P1.3's readout and addends")
        super().__init__(genome, life_seed,
                         observer_decision_diagnostics=observer_decision_diagnostics,
                         observer_full_competition=observer_full_competition)
        self.replay_gate_mode = mode
        self.decisions_total = 0
        self.audited_decisions = 0
        self.relevant_decisions = 0
        self.margin_sum = 0.0
        self.sleep_steps = 0
        self._last_residual = 0.0
        self.last_gate = None
        self.gate_simulations = 0

    def simulate(self, body, plan, horizon, budget):
        if self.simulation_mode != "reference":
            raise ValueError("the replay gate is defined on P1.3 reference simulation")
        b = list(body)
        steps = 0
        if self.observer_decision_diagnostics:
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
        residual = 0.0
        for k, gk in enumerate(self.gammas):
            if dead:
                boot = -self.d_max / (1.0 - gk)
            else:
                boot = self.value(k, phi, proj)
                residual += (1.0 - gk) * disc[k] * (boot - proj[k])
            out += (1.0 - gk) * (ret[k] + disc[k] * boot)
        self._last_residual = residual / 3.0
        return out / 3.0, steps, u_max

    def decide(self, cap, budget: CognitiveBudget):
        body = cap["body"]
        if tuple(body) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        self.last = None
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
        self._budget_rng.shuffle(opts)
        p_water, p_food = self._sources(inv)
        phi_now = self.feats(body)
        self._drift = self.drift()
        reach = min(255, int(1.0 / (1.0 - self.gammas[2])))
        ahead = [min(100.0, max(0.0, body[c] + reach * self._drift[0][c])) for c in range(5)]
        phi_ahead = self.feats(ahead)
        need_w = self.w[W] * phi_ahead[1 + W] * (1.0 - p_water)
        need_f = self.w[F] * phi_ahead[1 + F] * (1.0 - p_food)
        urgency = self.kappa0 + need_w + need_f
        seen = [c for c in self.map.values() if c is not None]
        p_res = (sum(1 for c in seen if c[0] or c[1]) + 1.0) / (len(seen) + 2.0)
        scored = []
        residuals = {}
        score_witness = [] if self.observer_decision_diagnostics else None
        sim_steps = 0
        for oid, plan, _ in opts:
            try:
                j, steps, u = self.simulate(body, plan, horizon, budget)
                residual = self._last_residual
                first_forecast = (self._observer_first_forecast
                                  if self.observer_decision_diagnostics else None)
                sim_steps += steps
                if oid in self._presence:
                    pr, travel = self._presence[oid]
                    j_fail, steps_fail, _ = self.simulate(body, travel, horizon, budget)
                    sim_steps += steps_fail
                    j = pr * j + (1.0 - pr) * j_fail
                    residual = pr * residual + (1.0 - pr) * self._last_residual
            except CognitiveFundingError:
                break
            if oid.startswith("explorer:"):
                u = min(1.0, self._unknown[oid] * p_res)
                relevance = urgency
            elif any(k[0] == "boire" for k in plan):
                relevance = self.kappa0 + need_w
            elif any(k[0] == "manger" for k in plan):
                relevance = self.kappa0 + need_f
            else:
                relevance = self.kappa0
            curiosity = self.beta_u * u * relevance
            risk_penalty = 0.0
            if any(k[0] == "manger" for k in plan):
                risk_penalty = -self.lambda_r * u * (
                    self.w[I] * phi_now[1 + I] + self.kappa0)
            use_curiosity = self.score_addend_mode not in (
                "discard_curiosity_bonus", "discard_both_bonus_terms")
            use_risk = self.score_addend_mode not in (
                "discard_risk_penalty", "discard_both_bonus_terms")
            bonus = (curiosity if use_curiosity else 0.0) + (
                risk_penalty if use_risk else 0.0)
            scored.append((oid, j + bonus))
            residuals[oid] = residual
            if self.observer_decision_diagnostics:
                score_witness.append({
                    "option": oid, "base_return": j,
                    "curiosity_bonus_computed": curiosity,
                    "risk_penalty_computed": risk_penalty,
                    "curiosity_bonus_applied": curiosity if use_curiosity else 0.0,
                    "risk_penalty_applied": risk_penalty if use_risk else 0.0,
                    "curiosity_risk_bonus": bonus, "total_score": j + bonus,
                    "uncertainty": u, "first_forecast": first_forecast})
        action, param, work, info = self._finalize_scored_decision(
            body=body, inv=inv, opts=opts, scored=scored,
            score_witness=score_witness, cycles=cycles, budget=budget,
            horizon=horizon, urgency=urgency,
            observer_offered=observer_offered,
            observer_families=observer_families)
        if scored:
            self.decisions_total += 1
            if budget.try_spend(CognitiveWork(cycles=1)):
                self._audit(scored, residuals)
                work = budget.work
        return action, param, work, info

    def _audit(self, scored, residuals):
        with_residual = dict(scored)
        without = {oid: s - residuals.get(oid, 0.0) for oid, s in scored}
        top_with, top_without = strict_top(with_residual), strict_top(without)
        self.audited_decisions += 1
        if (top_with is not None and top_without is not None
                and top_with != top_without):
            self.relevant_decisions += 1
            self.margin_sum += with_residual[top_with] - with_residual[top_without]

    def gate_inputs(self):
        # Frozen by #1212: denominator is all scored decisions, not only
        # decisions whose audit cycle happened to be fundable.
        r_hat = (self.relevant_decisions + 1.0) / (self.decisions_total + 2.0)
        m_hat = (self.margin_sum / self.relevant_decisions
                 if self.relevant_decisions else 0.0)
        horizon_of_use = (self.decisions_total + 1.0) / (self.sleep_steps + 1.0)
        return r_hat, m_hat, horizon_of_use

    def _replay_work(self):
        return CognitiveWork(simulated_steps=2 * len(self.proj_chunks), replays=1)

    def _gate(self, body, budget, limit):
        self.last_gate = None
        self.gate_simulations = 0
        priorities = sorted((m[0] for m in self.buffer), reverse=True)[:limit]
        if not priorities:
            return 0
        if not budget.try_spend(CognitiveWork(cycles=1)):
            return 0
        horizon = capacities(body, self.n_base, self.h_max)[1]
        energy, vigilance = cognitive_cost(budget.laws, self._replay_work())
        lighter = list(body)
        lighter[E_INDEX] = max(0.0, lighter[E_INDEX] - energy)
        lighter[V_INDEX] = max(0.0, lighter[V_INDEX] - vigilance)
        try:
            self.gate_simulations += 1
            v_body, _s, _u = self.simulate(tuple(body), [("dormir",)], horizon, budget)
            self.gate_simulations += 1
            v_lighter, _s, _u = self.simulate(tuple(lighter), [("dormir",)], horizon, budget)
        except CognitiveFundingError:
            return 0
        perceived = v_body - v_lighter
        cost = 0.0 if self.replay_gate_mode == "zero_perceived_cost" else perceived
        r_hat, m_hat, horizon_of_use = self.gate_inputs()
        gain = r_hat * m_hat * horizon_of_use
        total = sum(priorities)
        k = 0
        for p in priorities:
            credit = gain * p / total if total > 0.0 else 0.0
            if credit > cost:
                k += 1
            else:
                break
        self.last_gate = {"r_hat": r_hat, "m_hat": m_hat, "H": horizon_of_use,
                          "G": gain, "cost_per_replay": perceived,
                          "cost_used": cost, "eligible": len(priorities),
                          "k": k}
        return k

    def prepare_learning(self, result, budget: CognitiveBudget):
        if result["dead"] or self.last is None:
            return None
        if tuple(result["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("learning allowance must match the current body")
        base = CognitiveWork(cycles=2, simulated_steps=2 * len(self.proj_chunks),
                             memory_items=len(self.buffer) + len(self.effects.stats) + 1)
        if not budget.try_spend(base):
            return None
        limit = min(REPLAYS_PER_SLEEP, self.m_max, len(self.buffer) + 1)
        replays = 0
        if self.last[2] == "dormir":
            if self.replay_gate_mode == "forced_open":
                allowed = limit
            else:
                allowed = self._gate(tuple(result["body"]), budget, limit)
            self.sleep_steps += 1
            for _ in range(allowed):
                if not budget.try_spend(self._replay_work()):
                    break
                replays += 1
        return replays
