"""Stage-1 Candidate-G: personal recurrence with decision-local Candidate-F projection.

Opt-in software candidate only. It is not registered in runtime/life.py.

The persistent Mind remains P1.3 reference. A complete decision temporarily
switches every option score to the canonical Candidate-F projector only when
a paid personal information path exists. First contact uses personal recurrence,
never genomic omega.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict

from .body import (
    CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL, capacities,
    debit_cognition)
from .opportunity_recurrence import OpportunityRecurrenceMemory
from .plan_information import (
    _revealed_minimum_ceiling, _validate_revealed,
    paid_revealed_plan_information_value)
from .reference_frontier_information_mind import (
    ReferenceFrontierInformationMind, _add, _leq, _simulation_upper,
    _water_outcomes, _water_probability)
from .reference_opportunity_memory_mind import ReferenceOpportunityMemoryMind
from .unknown_outcomes import paid_frontier_actionable_belief
from .water_future_opportunity import (
    paid_water_one_future_opportunity_value,
    water_one_future_opportunity_work_ceiling)

POLICY = "personal_recurrence_candidate_g_v1"
STOP_AFTER_PREFIX = (("stop-after-prefix", ()),)


class PersonalRecurrenceCandidateGMind(
        ReferenceOpportunityMemoryMind, ReferenceFrontierInformationMind):
    """P1.3 authority + personal recurrence + conditional canonical projection."""

    def __init__(self, genome, life_seed, **kwargs):
        if "simulation_mode" in kwargs:
            raise ValueError("persistent simulation_mode is fixed to reference")
        if (kwargs.get("effect_readout", "full") != "full" or
                kwargs.get("score_addend_mode", "normal") != "normal"):
            raise ValueError(
                "personal recurrence candidate rejects historical score/readout ablations")
        super().__init__(genome, life_seed, simulation_mode="reference", **kwargs)
        self.projection_accounting = "chunk_end"
        self.first_contact_queries = 0
        self.first_contact_options_scored = 0
        self.positive_first_contact_options = 0
        self.post_contact_queries = 0
        self.recurrence_supported_decisions = 0
        self.information_active_decisions = 0
        self.reference_only_decisions = 0
        self._active_frontier_phase = "NO_FRONTIER"
        self._decision_projection_mode = "reference"
        self._decision_recurrence = None

    @contextmanager
    def candidate_f_projection(self):
        """Temporarily make all scores commensurate in the canonical projector."""
        if self.simulation_mode != "reference":
            raise RuntimeError("candidate projector entered from non-reference mode")
        if self.projection_accounting != "chunk_end":
            raise RuntimeError("candidate projector entered from non-reference accounting")
        self.simulation_mode = "candidate_f"
        self.projection_accounting = "event_local_quadratic4"
        try:
            yield
        finally:
            self.simulation_mode = "reference"
            self.projection_accounting = "chunk_end"

    def _finish(self, *args, **kwargs):
        result = super()._finish(*args, **kwargs)
        info = result[3]
        info["experimental_policy"] = POLICY
        info["frontier_phase"] = self._active_frontier_phase
        info["decision_projection_mode"] = self._decision_projection_mode
        info["persistent_simulation_mode"] = "reference"
        info["persistent_projection_accounting"] = "chunk_end"
        info["omega_source"] = "NONE_PERSONAL_RECURRENCE_ONLY"
        if self._decision_recurrence is not None:
            info["personal_recurrence_status"] = self._decision_recurrence["status"]
            info["personal_recurrence_probability"] = self._decision_recurrence[
                "future_matching_opportunity_probability"]
        return result

    def _has_personal_drink_effect(self) -> bool:
        state = self.effects.stats.get(("boire",))
        return state is not None and state[2] > 0

    def _capture_opportunity_presence(self):
        cells = [
            self.map[q] for q in self.visible
            if self.map.get(q) is not None
        ]
        self._pending_opportunity_presence = (
            any(cell[0] for cell in cells),
            any(bool(cell[1]) for cell in cells),
        )

    def _decide_scored(
            self, *, body, inv, opts, cycles, horizon, budget,
            personal_drink, belief, p_water, recurrence_result,
            information_active):
        """Score/control one already-perceived decision under one projection mode."""
        extra = CognitiveWork()
        info_specs = {}

        p_future = (
            None if recurrence_result is None else
            recurrence_result["future_matching_opportunity_probability"])

        for oid, plan, _first in opts:
            if (oid.startswith("explorer:") and personal_drink
                    and p_water > 0.0):
                outcomes, common = _water_outcomes(p_water, plan)
                common_dict, revealed = _validate_revealed(
                    outcomes, common, horizon)
                _prep, quoted = _revealed_minimum_ceiling(
                    self, outcomes, common_dict, revealed, horizon,
                    CognitiveWork())
                extra = _add(extra, quoted)
                info_specs[oid] = ("post_contact", outcomes, common)
            elif (oid.startswith("explorer:") and not personal_drink
                  and recurrence_result is not None
                  and recurrence_result["status"]
                  == "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE"):
                quoted = water_one_future_opportunity_work_ceiling(
                    self, self.branch_memory, tuple(plan),
                    STOP_AFTER_PREFIX, horizon)
                extra = _add(extra, quoted)
                info_specs[oid] = ("first_contact", tuple(plan), p_future)
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
                    _kind, explore_plan, personal_probability = spec
                    value = paid_water_one_future_opportunity_value(
                        self, self.branch_memory, explore_plan,
                        STOP_AFTER_PREFIX, horizon, budget,
                        forecast_work=ceiling,
                        future_opportunity_probability=personal_probability,
                        omega=0.0)
                    if value["innate_mean_shift_omega"] != 0.0:
                        raise RuntimeError("personal recurrence path used omega")
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
                            "PAID_PERSONAL_ONSET_RECURRENCE",
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
                            uncertainty if oid.startswith("explorer:") else None),
                        "common_forecast_work_ceiling": asdict(ceiling),
                        "one_cell_frontier_lower_bound": (
                            oid.startswith("explorer:")),
                        "personal_drink_support": personal_drink,
                        "decision_projection_mode":
                            self._decision_projection_mode,
                        "information_active_decision": information_active,
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
                "personal recurrence frontier scoring exceeded common ceiling")
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
            action, param = self._admit(by_id[oid], inv, budget.remaining)
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

    def decide(self, cap, budget: CognitiveBudget):
        if tuple(cap["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        if any(budget.body[k] <= 0 for k in VITAL):
            raise ValueError("no decision after physical death")
        if self.simulation_mode != "reference" or self.projection_accounting != "chunk_end":
            raise RuntimeError("persistent candidate mode must remain reference")

        self._pending_branch = None
        self._pending_opportunity_presence = None
        self._pending_opportunity_commit = None
        self.last = None
        self._decision_recurrence = None
        self._decision_projection_mode = "reference"

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
            self.reference_only_decisions += 1
            return self._finish(
                budget, (), (), (), "no_processing_budget",
                "NO_PROCESSING_BUDGET")

        cycles, horizon, miss = capacities(body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        self._capture_opportunity_presence()
        opts = self.options(inv, body, horizon)
        self._budget_rng.shuffle(opts)
        self._drift = self.drift()

        explorers = tuple(
            opt for opt in opts if opt[0].startswith("explorer:"))
        personal_drink = self._has_personal_drink_effect()
        belief = None
        p_water = 0.0
        recurrence_result = None
        information_active = False

        if explorers:
            self.frontier_belief_queries += 1
            if personal_drink:
                self._active_frontier_phase = "POST_CONTACT_PERSONAL"
                self.post_contact_queries += 1
                try:
                    belief = paid_frontier_actionable_belief(
                        self, self.branch_memory, budget)
                except CognitiveFundingError:
                    self.reference_only_decisions += 1
                    return self._finish(
                        budget, opts, (), (), "no_funded_score",
                        "NO_FUNDED_SCORE")
                p_water = _water_probability(belief)
                information_active = p_water > 0.0
                if information_active:
                    self.actionable_water_queries += 1
            else:
                self.first_contact_queries += 1
                try:
                    recurrence_result = self.opportunity_memory.estimate(
                        "water", horizon, budget)
                except CognitiveFundingError:
                    self._active_frontier_phase = (
                        "FIRST_CONTACT_RECURRENCE_UNFUNDED")
                    self.reference_only_decisions += 1
                    return self._finish(
                        budget, opts, (), (), "no_funded_score",
                        "NO_FUNDED_SCORE")
                self._decision_recurrence = recurrence_result
                if recurrence_result["status"] == (
                        "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE"):
                    self._active_frontier_phase = (
                        "FIRST_CONTACT_PERSONAL_RECURRENCE")
                    self.recurrence_supported_decisions += 1
                    information_active = True
                else:
                    self._active_frontier_phase = (
                        "FIRST_CONTACT_NO_RECURRENCE_SUPPORT")
        else:
            self._active_frontier_phase = "NO_FRONTIER"

        if information_active:
            self.information_active_decisions += 1
            self._decision_projection_mode = "candidate_f"
            with self.candidate_f_projection():
                return self._decide_scored(
                    body=body, inv=inv, opts=opts, cycles=cycles,
                    horizon=horizon, budget=budget,
                    personal_drink=personal_drink, belief=belief,
                    p_water=p_water, recurrence_result=recurrence_result,
                    information_active=True)

        self.reference_only_decisions += 1
        self._decision_projection_mode = "reference"
        return self._decide_scored(
            body=body, inv=inv, opts=opts, cycles=cycles,
            horizon=horizon, budget=budget,
            personal_drink=personal_drink, belief=belief,
            p_water=p_water, recurrence_result=recurrence_result,
            information_active=False)


__all__ = ["POLICY", "PersonalRecurrenceCandidateGMind", "STOP_AFTER_PREFIX"]
