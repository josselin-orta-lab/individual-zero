"""Reference-preserving Stage-1 frontier-water information probe.

This is an opt-in DEVELOPMENT mechanism, not the complete Stage-1 candidate.
It preserves the P1.3 repertoire, learned state, Competition, Action Control
and the #1077 branch-memory storage rule. The experimental score removes the
old additive curiosity/relevance/prudence terms. Only a conservative one-cell
frontier-water information mechanism is added.

Unknown food effects and multi-cell joint frontier outcomes are deliberately
not modelled here. Their omission is a falsifiable limitation, not a zero-cost
or favorable prior.
"""
from __future__ import annotations

from dataclasses import asdict

from .body import (
    CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL, capacities,
    debit_cognition)
from .information_value import WORK_KEYS
from .plan_information import (
    RevealedPlanOutcome, _revealed_minimum_ceiling, _validate_revealed,
    paid_revealed_plan_information_value)
from .reference_memory_mind import ReferenceBranchMemoryMind
from .unknown_outcomes import paid_frontier_actionable_belief

ZERO = (0.0,) * 5
POLICY = "reference_frontier_information_v1"


def _add(a: CognitiveWork, b: CognitiveWork) -> CognitiveWork:
    return CognitiveWork(*(getattr(a, k) + getattr(b, k) for k in WORK_KEYS))


def _leq(a: CognitiveWork, b: CognitiveWork) -> bool:
    return all(getattr(a, k) <= getattr(b, k) for k in WORK_KEYS)


def _simulation_upper(model, plan, horizon: int) -> CognitiveWork:
    """No-death upper bound matching Mind.simulate's movement chunking."""
    i = steps = 0
    n = len(plan)
    while i < n and steps < horizon:
        key = plan[i]
        run = 1
        if key[0] == "se_deplacer":
            while i + run < n and plan[i + run] == key and run < horizon:
                run += 1
        i += run
        steps += 1
    return CognitiveWork(
        simulated_steps=steps + len(model.proj_chunks))


def _water_probability(belief: dict) -> float:
    for branch in belief["branches"]:
        if branch["signal"] == "ACTIONABLE_WATER":
            return branch["probability"]
    return 0.0


def _water_outcomes(probability: float, travel) -> tuple:
    if not 0.0 < probability < 1.0:
        raise ValueError("strict actionable-water probability required")
    common = (("explore-only", tuple(travel)),)
    water_plan = tuple(travel) + (("se_deplacer",), ("boire",))
    outcomes = (
        RevealedPlanOutcome(
            1.0 - probability, "NO_ACTIONABLE_WATER_MODEL", ZERO, ()),
        RevealedPlanOutcome(
            probability, "ACTIONABLE_WATER", ZERO,
            (("explore-then-water", water_plan),)),
    )
    return outcomes, common


class ReferenceFrontierInformationMind(ReferenceBranchMemoryMind):
    """P1.3 repertoire plus paid one-cell frontier-water information."""

    def __init__(self, genome, life_seed, **kwargs):
        if (kwargs.get("effect_readout", "full") != "full" or
                kwargs.get("score_addend_mode", "normal") != "normal"):
            raise ValueError(
                "reference frontier candidate rejects historical score/readout ablations")
        super().__init__(genome, life_seed, **kwargs)
        self.frontier_belief_queries = 0
        self.actionable_water_queries = 0
        self.frontier_options_scored = 0
        self.positive_information_options = 0

    def _finish(self, budget, opts, scored, witnesses, outcome, funding,
                *, action=None, param=None, oid=None, horizon=None,
                rejected=0, competition=None, belief=None):
        info = {
            "option": oid,
            "funding": funding,
            "experimental_policy": POLICY,
            "frontier_scope": "one_generic_new_cell_water_only",
        }
        if horizon is not None:
            info["horizon"] = horizon
        if scored:
            info["scored_options"] = len(scored)
            info["top"] = sorted(
                ((round(score, 6), name) for name, score in scored),
                reverse=True)[:3]
        if belief is not None:
            info["frontier_belief_status"] = belief["status"]
            info["frontier_resource_base_rate"] = belief["resource_base_rate"]
        if self.observer_decision_diagnostics:
            diag = {
                "offered_options": len(opts),
                "scored_options": len(scored),
                "rejected_controls": rejected,
                "decision_outcome": outcome,
                "offered_families": self._observer_option_families(
                    o[0] for o in opts),
                "scored_families": self._observer_option_families(
                    o for o, _ in scored),
                "pre_body": budget.body,
                "score_witness": witnesses,
            }
            if competition is not None:
                diag["competition_witness"] = competition
            info["observer"] = diag
        self._branch_decision_work = budget.work
        return action, param, budget.work, info

    def decide(self, cap, budget: CognitiveBudget):
        if tuple(cap["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        if any(budget.body[k] <= 0 for k in VITAL):
            raise ValueError("no decision after physical death")
        self._pending_branch = None
        self.last = None

        body = cap["body"]
        slots = (
            len(self.buffer) + 2 * len(self.map) + len(self.effects.stats)
            + len(self.tokens) + len(self.external) + len(self.acc)
            + sum(len(v) for v in self.values) + 12
            + len(cap["inventory"]) + sum(
                len(cell[1]) for cell in (cap["here"], *cap["neighbors"])
                if cell is not None))
        if not budget.try_spend(CognitiveWork(cycles=3, memory_items=slots)):
            return self._finish(
                budget, (), (), (), "no_processing_budget",
                "NO_PROCESSING_BUDGET")

        cycles, horizon, miss = capacities(body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        opts = self.options(inv, body, horizon)
        self._budget_rng.shuffle(opts)
        self._drift = self.drift()

        explorers = tuple(opt for opt in opts if opt[0].startswith("explorer:"))
        belief = None
        p_water = 0.0
        if explorers:
            self.frontier_belief_queries += 1
            try:
                belief = paid_frontier_actionable_belief(
                    self, self.branch_memory, budget)
            except CognitiveFundingError:
                return self._finish(
                    budget, opts, (), (), "no_funded_score",
                    "NO_FUNDED_SCORE")
            p_water = _water_probability(belief)
            if p_water > 0.0:
                self.actionable_water_queries += 1

        # Quote all remaining option scoring plus a full Competition cycle
        # ceiling before any score is evaluated. This is conservative: early
        # predicted death or movement compression can leave unused work, which
        # is never billed by the runtime.
        extra = CognitiveWork()
        info_specs = {}
        for oid, plan, _first in opts:
            if oid.startswith("explorer:") and p_water > 0.0:
                outcomes, common = _water_outcomes(p_water, plan)
                common_dict, revealed = _validate_revealed(
                    outcomes, common, horizon)
                _prep, quoted = _revealed_minimum_ceiling(
                    self, outcomes, common_dict, revealed, horizon,
                    CognitiveWork())
                extra = _add(extra, quoted)
                info_specs[oid] = (outcomes, common)
            else:
                extra = _add(extra, _simulation_upper(self, plan, horizon))
                if oid in self._presence:
                    _pr, travel = self._presence[oid]
                    extra = _add(
                        extra, _simulation_upper(self, travel, horizon))
        extra = _add(extra, CognitiveWork(cycles=cycles))
        ceiling = _add(budget.work, extra)
        try:
            forecast_body, _ = debit_cognition(
                budget.body, budget.laws, ceiling)
        except CognitiveFundingError:
            return self._finish(
                budget, opts, (), (), "no_funded_score",
                "NO_FUNDED_SCORE", horizon=horizon, belief=belief)

        scored = []
        witnesses = []
        try:
            for oid, plan, _first in opts:
                information_value = 0.0
                if oid in info_specs:
                    outcomes, common = info_specs[oid]
                    value = paid_revealed_plan_information_value(
                        self, outcomes, common, horizon, budget,
                        forecast_work=ceiling)
                    score = value["informed_value"]
                    base_return = value["uninformed_value"]
                    information_value = value["information_value"]
                    self.frontier_options_scored += 1
                    if information_value > 1e-12:
                        self.positive_information_options += 1
                    uncertainty = p_water
                    first_forecast = None
                    score_kind = "frontier_water_expected_distress"
                    kernel_work = value["work"]
                else:
                    score, _steps, uncertainty = self.simulate(
                        forecast_body, plan, horizon, budget)
                    first_forecast = (
                        self._observer_first_forecast
                        if self.observer_decision_diagnostics else None)
                    if oid in self._presence:
                        pr, travel = self._presence[oid]
                        failed, _failed_steps, _ = self.simulate(
                            forecast_body, travel, horizon, budget)
                        score = pr * score + (1.0 - pr) * failed
                    base_return = score
                    score_kind = "reference_distress_no_addends"
                    kernel_work = None
                scored.append((oid, score))
                if self.observer_decision_diagnostics:
                    witness = {
                        "option": oid,
                        "base_return": base_return,
                        "curiosity_bonus_computed": 0.0,
                        "risk_penalty_computed": 0.0,
                        "curiosity_bonus_applied": 0.0,
                        "risk_penalty_applied": 0.0,
                        "curiosity_risk_bonus": 0.0,
                        "total_score": score,
                        "uncertainty": uncertainty,
                        "first_forecast": first_forecast,
                        "score_kind": score_kind,
                        "information_value": information_value,
                        "frontier_water_probability": (
                            p_water if oid.startswith("explorer:") else None),
                        "common_forecast_work_ceiling": asdict(ceiling),
                        "one_cell_frontier_lower_bound": (
                            oid.startswith("explorer:")),
                    }
                    if kernel_work is not None:
                        witness["information_kernel_work"] = kernel_work
                    witnesses.append(witness)
        except CognitiveFundingError as exc:
            raise RuntimeError(
                "funded common decision ceiling did not cover scoring") from exc

        if not _leq(budget.work, ceiling):
            raise RuntimeError("frontier scoring exceeded common decision ceiling")
        if not scored:
            return self._finish(
                budget, opts, (), witnesses, "no_funded_score",
                "NO_FUNDED_SCORE", horizon=horizon, belief=belief)

        winner, used = self._compete(scored, cycles, budget)
        if not _leq(budget.work, ceiling):
            raise RuntimeError("Competition exceeded common decision ceiling")

        ranked = [winner] + [
            name for name, _ in sorted(scored, key=lambda item: -item[1])
            if name != winner]
        by_id = {opt[0]: opt for opt in opts}
        competition = (
            self._observer_competition
            if self.observer_full_competition else None)
        if competition is not None:
            competition["control_order"] = list(ranked)
            competition["control_attempts"] = []

        rejected = 0
        for oid in ranked:
            action, param = self._admit(
                by_id[oid], inv, budget.remaining)
            if competition is not None:
                competition["control_attempts"].append({
                    "option": oid, "admitted": action is not None})
            if action is not None:
                break
            rejected += 1
        else:
            if competition is not None:
                competition.update(
                    status="ALL_CONTROLS_REJECTED",
                    final_admitted_option=None)
            return self._finish(
                budget, opts, scored, witnesses, "control_rejected",
                "NO_FUNDED_MOTOR", horizon=horizon, rejected=rejected,
                competition=competition, belief=belief)

        self.intention = oid if len(by_id[oid][1]) > 1 else None
        key = by_id[oid][1][0]
        self.last = (body, key, action, param)
        if competition is not None:
            competition.update(
                status="ACTION_ADMITTED",
                final_admitted_option=oid,
                final_admitted_action=action,
                intention_after=self.intention)
        result = self._finish(
            budget, opts, scored, witnesses, "action_admitted", "FUNDED",
            action=action, param=param, oid=oid, horizon=horizon,
            rejected=rejected, competition=competition, belief=belief)
        result[3]["cycles"] = used
        result[3]["simulated"] = budget.work.simulated_steps
        return result
