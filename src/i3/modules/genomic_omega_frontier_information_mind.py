"""Opt-in live Stage-1 water-frontier candidate with inherited first-contact omega.

This candidate composes two already-tested paths:
- GenomicOmegaCandidateFMind: genome-v4 omega + Candidate-F simulation;
- ReferenceFrontierInformationMind: P1.3 repertoire, Competition, Action
  Control and paid personal branch-memory lifecycle.

Omega is consulted only while the individual has no personal drink effect.
After any personally learned drink effect exists, scoring returns to the
existing omega-free personal frontier path.
"""
from __future__ import annotations

from dataclasses import asdict

from .body import (
    CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL, capacities,
    debit_cognition)
from .genomic_omega_candidate_f import GenomicOmegaCandidateFMind
from .plan_information import (
    _revealed_minimum_ceiling, _validate_revealed,
    paid_revealed_plan_information_value)
from .reference_frontier_information_mind import (
    ReferenceFrontierInformationMind, _add, _leq, _simulation_upper,
    _water_outcomes, _water_probability)
from .unknown_outcomes import paid_frontier_actionable_belief
from .water_future_opportunity import (
    paid_water_one_future_opportunity_value,
    water_one_future_opportunity_work_ceiling)

POLICY = "genomic_omega_frontier_information_v1"
STOP_AFTER_PREFIX = (("stop-after-prefix", ()),)


class GenomicOmegaFrontierInformationMind(
        GenomicOmegaCandidateFMind, ReferenceFrontierInformationMind):
    """Candidate-F water frontier with omega only before personal drink support."""

    def __init__(self, genome, life_seed, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        self.first_contact_queries = 0
        self.first_contact_options_scored = 0
        self.positive_first_contact_options = 0
        self.post_contact_queries = 0
        self._active_frontier_phase = "NO_FRONTIER"

    def _finish(self, *args, **kwargs):
        result = super()._finish(*args, **kwargs)
        info = result[3]
        info["experimental_policy"] = POLICY
        info["frontier_phase"] = self._active_frontier_phase
        info["simulation_mode"] = self.simulation_mode
        info["projection_accounting"] = self.projection_accounting
        info["omega_source"] = "genome_v4_first_contact_only"
        return result

    def _has_personal_drink_effect(self) -> bool:
        state = self.effects.stats.get(("boire",))
        return state is not None and state[2] > 0

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
            self._active_frontier_phase = "NO_PROCESSING_BUDGET"
            return self._finish(
                budget, (), (), (), "no_processing_budget",
                "NO_PROCESSING_BUDGET")

        cycles, horizon, miss = capacities(body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        opts = self.options(inv, body, horizon)
        self._budget_rng.shuffle(opts)
        self._drift = self.drift()

        explorers = tuple(
            opt for opt in opts if opt[0].startswith("explorer:"))
        personal_drink = self._has_personal_drink_effect()
        belief = None
        p_water = 0.0
        if explorers:
            self.frontier_belief_queries += 1
            if personal_drink:
                self._active_frontier_phase = "POST_CONTACT_PERSONAL"
                self.post_contact_queries += 1
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
            else:
                self._active_frontier_phase = "FIRST_CONTACT_GENOMIC_OMEGA"
                self.first_contact_queries += 1
        else:
            self._active_frontier_phase = "NO_FRONTIER"

        # One common forecast body covers every remaining option score and the
        # complete Competition cycle. First-contact quotes use only structural
        # map/memory sizes; empirical sample values are read later, for pay.
        extra = CognitiveWork()
        info_specs = {}
        for oid, plan, _first in opts:
            if oid.startswith("explorer:") and personal_drink and p_water > 0.0:
                outcomes, common = _water_outcomes(p_water, plan)
                common_dict, revealed = _validate_revealed(
                    outcomes, common, horizon)
                _prep, quoted = _revealed_minimum_ceiling(
                    self, outcomes, common_dict, revealed, horizon,
                    CognitiveWork())
                extra = _add(extra, quoted)
                info_specs[oid] = ("post_contact", outcomes, common)
            elif oid.startswith("explorer:") and not personal_drink:
                quoted = water_one_future_opportunity_work_ceiling(
                    self, self.branch_memory, tuple(plan),
                    STOP_AFTER_PREFIX, horizon)
                extra = _add(extra, quoted)
                info_specs[oid] = ("first_contact", tuple(plan))
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
                first_contact_fields = None
                spec = info_specs.get(oid)
                if spec is not None and spec[0] == "post_contact":
                    _kind, outcomes, common = spec
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
                elif spec is not None and spec[0] == "first_contact":
                    _kind, explore_plan = spec
                    value = paid_water_one_future_opportunity_value(
                        self, self.branch_memory, explore_plan,
                        STOP_AFTER_PREFIX, horizon, budget,
                        forecast_work=ceiling,
                        omega=self.first_contact_omega)
                    score = value["frontier_expected_value"]
                    base_return = value["decline_value"]
                    information_value = value["water_revelation_advantage"]
                    self.frontier_options_scored += 1
                    self.first_contact_options_scored += 1
                    if information_value > 1e-12:
                        self.positive_information_options += 1
                        self.positive_first_contact_options += 1
                    uncertainty = value["water_probability"]
                    first_forecast = None
                    score_kind = "frontier_water_expected_distress"
                    kernel_work = value["work"]
                    first_contact_fields = {
                        "first_contact_omega": self.first_contact_omega,
                        "trial_information_value":
                            value["trial_information_value"],
                        "trial_advantage": value["trial_advantage"],
                        "water_revelation_advantage":
                            value["water_revelation_advantage"],
                        "target_node_best_choices":
                            value["target_node_best_choices"],
                        "subjective_leaf_count":
                            value["subjective_leaf_count"],
                        "future_water_opportunity_probability":
                            value["future_water_opportunity_probability"],
                        "future_opportunity_probability_source":
                            value["future_opportunity_probability_source"],
                    }
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
                            uncertainty
                            if oid.startswith("explorer:") else None),
                        "common_forecast_work_ceiling": asdict(ceiling),
                        "one_cell_frontier_lower_bound": (
                            oid.startswith("explorer:")),
                        "personal_drink_support": personal_drink,
                    }
                    if kernel_work is not None:
                        witness["information_kernel_work"] = kernel_work
                    if first_contact_fields is not None:
                        witness.update(first_contact_fields)
                    witnesses.append(witness)
        except CognitiveFundingError as exc:
            raise RuntimeError(
                "funded common decision ceiling did not cover scoring") from exc

        if not _leq(budget.work, ceiling):
            raise RuntimeError(
                "genomic frontier scoring exceeded common decision ceiling")
        if not scored:
            return self._finish(
                budget, opts, (), witnesses, "no_funded_score",
                "NO_FUNDED_SCORE", horizon=horizon, belief=belief)

        winner, used = self._compete(scored, cycles, budget)
        if not _leq(budget.work, ceiling):
            raise RuntimeError(
                "Competition exceeded common decision ceiling")

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


__all__ = ["GenomicOmegaFrontierInformationMind", "POLICY"]
