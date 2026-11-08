"""Runnable Candidate-I: shared inherited first-contact prior + relevance.

DEVELOPMENT software candidate only. Persistent projection remains P1.3
reference/chunk_end. Unsupported first contact may temporarily score the
complete option set in canonical Candidate-F geometry, but final motor authority
always remains the ordinary Mind Competition and ActionControl.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from math import isfinite

from .body import (
    CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL,
    capacities, debit_cognition)
from .information_value import WORK_KEYS, _add_work
from .mind import Mind
from .personal_recurrence_candidate_g_mind import (
    STOP_AFTER_PREFIX)
from .personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind,
    first_contact_relevant_fields,
    post_contact_relevant_scores)
from .recent_rms_effect_prior import (
    paid_recent_rms_zero_mean_effect_prior,
    recent_rms_effect_prior_work_ceiling)
from .shared_first_contact_trials import direct_trial_strict_winners
from .reference_frontier_information_mind import (
    _simulation_upper)
from .unknown_action_trial import (
    _minimum_ceiling as _trial_minimum_ceiling,
    paid_unknown_action_trial_value)
from .water_future_opportunity import (
    paid_water_one_future_opportunity_value,
    water_one_future_opportunity_work_ceiling)

POLICY = "personal_shared_prior_candidate_i_v1"
TOL = 1e-12
COMMON = (("no-trial", ()),)


def _add(left, right):
    return _add_work(left, right)


def _leq(left, right):
    return all(
        getattr(left, key) <= getattr(right, key)
        for key in WORK_KEYS)


def _delta(after, before):
    return CognitiveWork(*(
        getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS))


def _top(scores):
    if not scores:
        return ()
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items()
        if value >= best - TOL))


class PersonalSharedPriorCandidateIMind(PersonalRelevanceCandidateHMind):
    """Candidate-H post-contact + shared-prior first-contact final authority."""

    def __init__(self, genome, life_seed, *,
                 first_contact_omega_override=None, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        native = genome["genes"]["omega"]
        if first_contact_omega_override is None:
            self.first_contact_omega = float(native)
            self.first_contact_omega_source = "GENOME_V4_OMEGA"
        else:
            value = first_contact_omega_override
            if (type(value) not in (int, float) or type(value) is bool
                    or not isfinite(value) or not -1.0 <= value <= 1.0):
                raise ValueError(
                    "first_contact_omega_override must be finite in [-1,1]")
            self.first_contact_omega = float(value)
            self.first_contact_omega_source = "SOFTWARE_OMEGA_ABLATION"
        self.candidate_i_first_contact_decisions = 0
        self.candidate_i_relevant_final = 0
        self.candidate_i_base_fallback_final = 0
        self.candidate_i_probe_unfunded = 0

    def _probe_state_snapshot(self):
        return {
            "map": deepcopy(self.map),
            "hist": deepcopy(self.hist),
            "tokens": deepcopy(self.tokens),
            "external": deepcopy(self.external),
            "acc": deepcopy(self.acc),
            "intention": self.intention,
            "visible": tuple(self.visible),
            "pos": tuple(self.pos),
            "unknown": (
                deepcopy(self._unknown)
                if hasattr(self, "_unknown") else None),
            "presence": (
                deepcopy(self._presence)
                if hasattr(self, "_presence") else None),
            "drift": deepcopy(self._drift),
            "rng": self.rng.getstate(),
            "budget_rng": self._budget_rng.getstate(),
            "observer_competition":
                deepcopy(getattr(self, "_observer_competition", None)),
            "observer_first_forecast":
                deepcopy(getattr(self, "_observer_first_forecast", None)),
        }

    def _restore_probe_state(self, snap):
        self.map = deepcopy(snap["map"])
        self.hist = deepcopy(snap["hist"])
        self.tokens = deepcopy(snap["tokens"])
        self.external = deepcopy(snap["external"])
        self.acc = deepcopy(snap["acc"])
        self.intention = snap["intention"]
        self.visible = tuple(snap["visible"])
        self.pos = tuple(snap["pos"])
        if snap["unknown"] is None:
            if hasattr(self, "_unknown"):
                del self._unknown
        else:
            self._unknown = deepcopy(snap["unknown"])
        if snap["presence"] is None:
            if hasattr(self, "_presence"):
                del self._presence
        else:
            self._presence = deepcopy(snap["presence"])
        self._drift = deepcopy(snap["drift"])
        self.rng.setstate(snap["rng"])
        self._budget_rng.setstate(snap["budget_rng"])
        self._observer_competition = deepcopy(
            snap["observer_competition"])
        self._observer_first_forecast = deepcopy(
            snap["observer_first_forecast"])

    def _clear_first_contact_learning_authority(self):
        """Clear state that a detached first-contact rollback must never own."""
        self._pending_branch = None
        self._clear_branch_decision_settlement()
        self._pending_opportunity_presence = None
        self._pending_opportunity_commit = None
        self.last = None

    def _cap_has_potential_unsupported_direct_trial(self, cap):
        """Conservative pre-perception gate for offered direct resource trials."""
        here = cap.get("here")
        if (isinstance(here, tuple) and len(here) == 2
                and here[0]
                and not self._exact_personal_support(("boire",))):
            return True
        inventory = cap.get("inventory", ())
        for item in inventory:
            if (not isinstance(item, tuple) or len(item) != 2
                    or type(item[1]) is not int or item[1] <= 0):
                continue
            external = item[0]
            internal = self.tokens.get(external)
            if internal is None:
                return True
            if not self._exact_personal_support(
                    ("manger", internal)):
                return True
        return False

    def _exact_personal_support(self, action_key):
        state = self.effects.stats.get(tuple(action_key))
        return state is not None and state[2] > 0

    def _direct_trials(self, opts):
        out = []
        for oid, plan, _first in opts:
            plan = tuple(plan)
            if len(plan) != 1:
                continue
            key = tuple(plan[0])
            if key[0] == "boire" and len(key) == 1:
                if not self._exact_personal_support(key):
                    out.append((oid, key))
            elif key[0] == "manger" and len(key) == 2:
                if not self._exact_personal_support(key):
                    out.append((oid, key))
        return tuple(out)

    def _probe_unfunded(
            self, budget, *, body, offered_options,
            offered_families, nested, stage_work,
            reason):
        self._clear_first_contact_learning_authority()
        self.candidate_i_probe_unfunded += 1
        info = {
            "option": None,
            "funding": "NO_FUNDED_RELEVANCE_PROBE",
            "experimental_policy": POLICY,
            "candidate_i_route": "PROBE_UNFUNDED",
            "candidate_i_relevance": "PROBE_UNFUNDED",
            "candidate_i_probe_funding": nested,
            "candidate_h_probe_funding": nested,
            "candidate_i_probe_reason": reason,
            "candidate_i_stage_a_work": asdict(stage_work),
            "candidate_i_stage_b_work": asdict(CognitiveWork()),
            "candidate_i_total_work": asdict(budget.work),
            "candidate_i_body_after_cognition": tuple(budget.remaining),
            "persistent_simulation_mode": "reference",
            "persistent_projection_accounting": "chunk_end",
            "first_contact_omega": self.first_contact_omega,
            "omega_source": self.first_contact_omega_source,
            "decision_projection_mode": "candidate_f",
        }
        if self.observer_decision_diagnostics:
            outcome = (
                "no_processing_budget"
                if nested == "NO_PROCESSING_BUDGET"
                else "no_funded_score")
            empty = self._observer_option_families(())
            info["observer"] = {
                "offered_options": offered_options,
                "scored_options": 0,
                "rejected_controls": 0,
                "decision_outcome": outcome,
                "offered_families": (
                    dict(offered_families)
                    if offered_families is not None else dict(empty)),
                "scored_families": dict(empty),
                "pre_body": tuple(body),
                "score_witness": [],
            }
        return None, None, budget.work, info

    def _first_contact_score(
            self, *, body, inv, opts, cycles, horizon, budget,
            recurrence_result):
        """Score the complete first-contact set in one Candidate-F geometry."""
        original_work = budget.work
        direct = self._direct_trials(opts)
        direct_ids = {oid for oid, _key in direct}

        imagined = {}
        p_future = None
        if (recurrence_result is not None
                and recurrence_result["status"]
                == "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE"):
            p_future = recurrence_result[
                "future_matching_opportunity_probability"]
            for oid, plan, _first in opts:
                if oid.startswith("explorer:"):
                    imagined[oid] = tuple(plan)

        info_ids = direct_ids | set(imagined)
        prior_quote = recent_rms_effect_prior_work_ceiling(
            self.branch_memory)

        extra = CognitiveWork()
        direct_quotes = {}
        for oid, action_key in direct:
            post = {
                "stop-after-trial": (),
                "repeat-trial": (action_key,),
            }
            common = {"no-trial": ()}
            _prep, quote = _trial_minimum_ceiling(
                self, prior_quote, (None, None), action_key,
                common, post, horizon, CognitiveWork())
            direct_quotes[oid] = quote
            extra = _add(extra, quote)

        for oid, plan in imagined.items():
            quote = water_one_future_opportunity_work_ceiling(
                self, self.branch_memory, plan,
                STOP_AFTER_PREFIX, horizon)
            extra = _add(extra, quote)

        for oid, plan, _first in opts:
            if oid in info_ids:
                continue
            extra = _add(
                extra, _simulation_upper(self, tuple(plan), horizon))
            if oid in self._presence:
                _probability, travel = self._presence[oid]
                extra = _add(
                    extra, _simulation_upper(
                        self, tuple(travel), horizon))

        # Relevant finalization uses the ordinary Competition. Reserve all of
        # its cycles in the common forecast body before any score is computed.
        extra = _add(extra, CognitiveWork(cycles=cycles))
        ceiling = _add(budget.work, extra)
        try:
            forecast_body, _ = debit_cognition(
                budget.body, budget.laws, ceiling)
        except CognitiveFundingError:
            return {
                "status": "UNFUNDED",
                "probe_funding": "NO_FUNDED_SCORE",
                "work": _delta(budget.work, original_work),
                "body_after_computation": budget.remaining,
                "forecast_work_ceiling": ceiling,
                "offered_options": len(opts),
                "offered_families": (
                    self._observer_option_families(
                        o[0] for o in opts)
                    if self.observer_decision_diagnostics else None),
            }

        direct_rows = {}
        for oid, action_key in direct:
            post = (
                ("stop-after-trial", ()),
                ("repeat-trial", (action_key,)),
            )

            def prior_source(
                    allowance, _memory=self.branch_memory,
                    _omega=self.first_contact_omega):
                return paid_recent_rms_zero_mean_effect_prior(
                    _memory, allowance, omega=_omega)

            value = paid_unknown_action_trial_value(
                self, action_key, COMMON, post,
                horizon, budget,
                forecast_work=ceiling,
                prior_source=prior_source)
            direct_rows[oid] = value
            if not _leq(budget.work, ceiling):
                raise RuntimeError(
                    "Candidate-I direct trial exceeded common ceiling")

        imagined_rows = {}
        if p_future is not None:
            for oid, plan in imagined.items():
                value = paid_water_one_future_opportunity_value(
                    self, self.branch_memory, plan,
                    STOP_AFTER_PREFIX, horizon, budget,
                    forecast_work=ceiling,
                    future_opportunity_probability=p_future,
                    omega=self.first_contact_omega)
                imagined_rows[oid] = value
                if not _leq(budget.work, ceiling):
                    raise RuntimeError(
                        "Candidate-I imagined trial exceeded common ceiling")

        ordinary_scores = {}
        ordinary_meta = {}
        for oid, plan, _first in opts:
            if oid in info_ids:
                continue
            score, _steps, uncertainty = self.simulate(
                forecast_body, tuple(plan), horizon, budget)
            first_forecast = (
                self._observer_first_forecast
                if self.observer_decision_diagnostics else None)
            if oid in self._presence:
                probability, travel = self._presence[oid]
                failed, _failed_steps, _ = self.simulate(
                    forecast_body, tuple(travel), horizon, budget)
                score = (
                    probability * score
                    + (1.0 - probability) * failed)
            ordinary_scores[oid] = float(score)
            ordinary_meta[oid] = (
                uncertainty, first_forecast)
            if not _leq(budget.work, ceiling):
                raise RuntimeError(
                    "Candidate-I ordinary score exceeded common ceiling")

        # A missing empirical RMS prior is a completed no-capacity probe, not
        # a physical funding failure. It therefore cannot activate information.
        direct_complete = all(
            row["status"]
            == "COMPLETE_UNKNOWN_ACTION_TRIAL_ESTIMATE_NOT_POLICY"
            for row in direct_rows.values())

        scored_map = dict(ordinary_scores)
        without_direct = dict(ordinary_scores)
        witnesses = {}
        positive_direct = []
        if direct_complete:
            for oid, row in direct_rows.items():
                scored_map[oid] = float(row["trial_informed_value"])
                without_direct[oid] = float(row["trial_frozen_value"])
                if row["information_value"] > TOL:
                    positive_direct.append(oid)
        else:
            # With no empirical scale, direct first-contact information has no
            # score authority. The eventual route is FALLBACK.
            for oid in direct_rows:
                pass

        imagined_relevant = False
        for oid, row in imagined_rows.items():
            scored_map[oid] = float(row["frontier_expected_value"])
            without_direct[oid] = float(row["frontier_expected_value"])
            if first_contact_relevant_fields(
                    row.get("target_node_best_choices"),
                    row.get("trial_information_value"),
                    row.get("trial_advantage")):
                imagined_relevant = True

        direct_strict_winners = (
            direct_trial_strict_winners(
                tuple({
                    "option": oid,
                    "trial_informed_value":
                        row["trial_informed_value"],
                    "no_trial_value":
                        row["no_trial_value"],
                } for oid, row in direct_rows.items()),
                scored_map)
            if direct_complete and direct_rows else ())
        direct_relevant = bool(direct_strict_winners)
        relevant = direct_relevant or imagined_relevant

        # If direct empirical support is absent and there is no independently
        # relevant imagined path, the complete probe falls back.
        if not direct_complete and not imagined_relevant:
            relevant = False

        scored = []
        score_witness = []
        if relevant:
            for oid, plan, _first in opts:
                if oid in ordinary_scores:
                    score = ordinary_scores[oid]
                    uncertainty, first_forecast = ordinary_meta[oid]
                    witness = {
                        "option": oid,
                        "base_return": score,
                        "curiosity_bonus_computed": 0.0,
                        "risk_penalty_computed": 0.0,
                        "curiosity_bonus_applied": 0.0,
                        "risk_penalty_applied": 0.0,
                        "curiosity_risk_bonus": 0.0,
                        "total_score": score,
                        "uncertainty": uncertainty,
                        "first_forecast": first_forecast,
                        "score_kind":
                            "candidate_f_distress_no_addends",
                        "information_value": 0.0,
                        "common_forecast_work_ceiling":
                            asdict(ceiling),
                    }
                elif oid in direct_rows:
                    row = direct_rows[oid]
                    score = float(row["trial_informed_value"])
                    witness = {
                        "option": oid,
                        "base_return":
                            float(row["trial_frozen_value"]),
                        "curiosity_bonus_computed": 0.0,
                        "risk_penalty_computed": 0.0,
                        "curiosity_bonus_applied": 0.0,
                        "risk_penalty_applied": 0.0,
                        "curiosity_risk_bonus": 0.0,
                        "total_score": score,
                        "uncertainty": 1.0,
                        "first_forecast": None,
                        "score_kind":
                            "first_contact_information_expected_distress",
                        "information_value":
                            float(row["information_value"]),
                        "trial_no_trial_value":
                            row["no_trial_value"],
                        "trial_frozen_value":
                            row["trial_frozen_value"],
                        "trial_advantage":
                            row["trial_advantage"],
                        "shared_effect_prior":
                            dict(row["prior_record"]),
                        "common_forecast_work_ceiling":
                            asdict(ceiling),
                    }
                else:
                    row = imagined_rows[oid]
                    score = float(row["frontier_expected_value"])
                    witness = {
                        "option": oid,
                        "base_return": float(row["decline_value"]),
                        "curiosity_bonus_computed": 0.0,
                        "risk_penalty_computed": 0.0,
                        "curiosity_bonus_applied": 0.0,
                        "risk_penalty_applied": 0.0,
                        "curiosity_risk_bonus": 0.0,
                        "total_score": score,
                        "uncertainty": row["water_probability"],
                        "first_forecast": None,
                        "score_kind":
                            "frontier_water_expected_distress",
                        "information_value":
                            row["water_revelation_advantage"],
                        "first_contact_omega":
                            self.first_contact_omega,
                        "trial_information_value":
                            row["trial_information_value"],
                        "trial_advantage":
                            row["trial_advantage"],
                        "water_revelation_advantage":
                            row["water_revelation_advantage"],
                        "target_node_best_choices":
                            row["target_node_best_choices"],
                        "subjective_leaf_count":
                            row["subjective_leaf_count"],
                        "future_water_opportunity_probability":
                            row[
                                "future_water_opportunity_probability"],
                        "future_opportunity_probability_source":
                            "PAID_PERSONAL_ONSET_RECURRENCE",
                        "common_forecast_work_ceiling":
                            asdict(ceiling),
                    }
                scored.append((oid, score))
                score_witness.append(witness)

        return {
            "status": "FUNDED",
            "probe_funding": "FUNDED",
            "classification":
                "RELEVANT" if relevant else "FALLBACK",
            "relevant": relevant,
            "direct_relevant": direct_relevant,
            "direct_strict_winners": direct_strict_winners,
            "imagined_relevant": imagined_relevant,
            "v1_top_set_change_diagnostic": (
                direct_complete
                and bool(direct_rows)
                and post_contact_relevant_scores(
                    scored_map, without_direct,
                    positive_direct)),
            "direct_trial_count": len(direct),
            "imagined_trial_count": len(imagined_rows),
            "direct_trials": tuple(direct),
            "recurrence": recurrence_result,
            "scored": tuple(scored),
            "score_witness": tuple(score_witness),
            "with_information_scores": scored_map,
            "without_direct_information_scores":
                without_direct,
            "with_information_top": _top(scored_map),
            "without_direct_information_top":
                _top(without_direct),
            "work": _delta(budget.work, original_work),
            "body_after_computation": budget.remaining,
            "forecast_work_ceiling": ceiling,
            "forecast_start_body": forecast_body,
            "offered_options": len(opts),
            "offered_families": (
                self._observer_option_families(
                    o[0] for o in opts)
                if self.observer_decision_diagnostics else None),
            "all_direct_trials_complete": direct_complete,
            "direct_quotes": {
                oid: asdict(work)
                for oid, work in direct_quotes.items()},
        }

    @staticmethod
    def _cap_with_body(cap, body):
        out = dict(cap)
        out["body"] = tuple(body)
        return out

    def decide(self, cap, budget: CognitiveBudget):
        if tuple(cap["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError(
                "fresh allowance must match the perceived body")
        if any(budget.body[k] <= 0 for k in VITAL):
            raise ValueError("no decision after physical death")
        if (self.simulation_mode, self.projection_accounting) != (
                "reference", "chunk_end"):
            raise RuntimeError(
                "Candidate-I persistent mode must remain reference/chunk_end")

        # Exact #1163/H post-contact authority once drinking has personal
        # support, but never at the expense of a simultaneously offered
        # unsupported direct resource trial. That trial still requires the
        # shared first-contact matrix.
        if (self._has_personal_drink_effect()
                and not self._cap_has_potential_unsupported_direct_trial(cap)):
            result = super().decide(cap, budget)
            action, param, work, old_info = result
            info = dict(old_info)
            info["experimental_policy"] = POLICY
            info["candidate_i_route"] = "POST_CONTACT_CANDIDATE_H"
            info["candidate_i_first_contact_omega_used"] = False
            info["candidate_i_post_contact_source"] = (
                "CANDIDATE_H_1163_UNCHANGED")
            return action, param, work, info

        self.candidate_i_first_contact_decisions += 1

        # Rollback may restore first-person perception/RNG state only. Any
        # learning authority belongs to the new real decision and must be
        # empty before the reversible probe baseline is captured.
        self._clear_first_contact_learning_authority()
        probe_state = self._probe_state_snapshot()

        body = cap["body"]
        slots = (
            len(self.buffer) + 2 * len(self.map)
            + len(self.effects.stats)
            + len(self.tokens) + len(self.external)
            + len(self.acc)
            + sum(len(v) for v in self.values) + 12
            + len(cap["inventory"])
            + sum(
                len(cell[1])
                for cell in (cap["here"], *cap["neighbors"])
                if cell is not None))
        if not budget.try_spend(
                CognitiveWork(cycles=3, memory_items=slots)):
            return self._probe_unfunded(
                budget, body=body, offered_options=0,
                offered_families=None,
                nested="NO_PROCESSING_BUDGET",
                stage_work=budget.work,
                reason="BASE_PROCESSING_UNFUNDED")

        cycles, horizon, miss = capacities(
            body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        self._capture_opportunity_presence()
        opts = self.options(inv, body, horizon)
        self._budget_rng.shuffle(opts)
        self._drift = self.drift()

        explorers = tuple(
            opt for opt in opts
            if opt[0].startswith("explorer:"))
        recurrence = None
        if explorers:
            try:
                recurrence = self.opportunity_memory.estimate(
                    "water", horizon, budget)
            except CognitiveFundingError:
                self._restore_probe_state(probe_state)
                return self._probe_unfunded(
                    budget, body=body,
                    offered_options=len(opts),
                    offered_families=(
                        self._observer_option_families(
                            o[0] for o in opts)
                        if self.observer_decision_diagnostics
                        else None),
                    nested="NO_FUNDED_SCORE",
                    stage_work=budget.work,
                    reason="RECURRENCE_READ_UNFUNDED")

        with self.candidate_f_projection():
            stage_a = self._first_contact_score(
                body=body, inv=inv, opts=opts,
                cycles=cycles, horizon=horizon,
                budget=budget,
                recurrence_result=recurrence)

            if stage_a["status"] != "FUNDED":
                self._restore_probe_state(probe_state)
                return self._probe_unfunded(
                    budget, body=body,
                    offered_options=stage_a[
                        "offered_options"],
                    offered_families=stage_a[
                        "offered_families"],
                    nested=stage_a["probe_funding"],
                    stage_work=budget.work,
                    reason="COMMON_MATRIX_UNFUNDED")

            stage_a_total_work = budget.work
            stage_a_total_body = tuple(budget.remaining)

            if stage_a["relevant"]:
                self.candidate_i_relevant_final += 1
                result = self._finalize_scored_decision(
                    body=body, inv=inv, opts=opts,
                    scored=list(stage_a["scored"]),
                    score_witness=list(
                        stage_a["score_witness"]),
                    cycles=cycles, budget=budget,
                    horizon=horizon, urgency=0.0,
                    observer_offered=len(opts),
                    observer_families=stage_a[
                        "offered_families"])
                self._last_candidate_i_body = tuple(
                    budget.remaining)
                self._set_branch_decision_settlement(
                    budget.body, budget.work)
                if (self.simulation_mode,
                        self.projection_accounting) != (
                        "candidate_f",
                        "event_local_quadratic4"):
                    raise RuntimeError(
                        "Candidate-I local projector changed inside scope")
                # Context manager restores persistent state after return from
                # this block; decorate outside the mode-sensitive fields.
                final = result
                route = "INFORMATION_FINAL"
            else:
                final = None
                route = "P1.3_BASE_FINAL"

        if route == "INFORMATION_FINAL":
            if (self.simulation_mode,
                    self.projection_accounting) != (
                    "reference", "chunk_end"):
                raise RuntimeError(
                    "Candidate-I information final leaked projector mode")
            info = dict(final[3])
            info["experimental_policy"] = POLICY
            info["candidate_i_route"] = route
            info["candidate_i_relevance"] = "RELEVANT"
            info["candidate_i_probe_funding"] = "FUNDED"
            info["candidate_h_probe_funding"] = "FUNDED"
            stage_b_work = _delta(
                budget.work, stage_a_total_work)
            info["candidate_i_stage_a_work"] = asdict(
                stage_a_total_work)
            info["candidate_i_stage_a_body_after"] = tuple(
                stage_a_total_body)
            info["candidate_i_stage_b_work"] = asdict(
                stage_b_work)
            info["candidate_i_total_work"] = asdict(
                budget.work)
            info["candidate_i_body_after_cognition"] = tuple(
                budget.remaining)
            info["candidate_i_direct_trial_count"] = (
                stage_a["direct_trial_count"])
            info["candidate_i_imagined_trial_count"] = (
                stage_a["imagined_trial_count"])
            info["persistent_simulation_mode"] = "reference"
            info["persistent_projection_accounting"] = "chunk_end"
            info["first_contact_omega"] = (
                self.first_contact_omega)
            info["omega_source"] = (
                self.first_contact_omega_source)
            info["decision_projection_mode"] = "candidate_f"
            return final[0], final[1], budget.work, info

        # FALLBACK: discard all temporary first-contact perception/probe state,
        # preserve its physical bill, then execute one real addend-free final
        # decision from the post-probe body. This prevents double perception.
        self.candidate_i_base_fallback_final += 1
        self._restore_probe_state(probe_state)
        self._clear_first_contact_learning_authority()
        post_probe_body = tuple(budget.remaining)
        final_cap = self._cap_with_body(
            cap, post_probe_body)
        final_budget = CognitiveBudget(
            post_probe_body, budget.laws)

        old_mode = self.score_addend_mode
        self.score_addend_mode = "discard_both_bonus_terms"
        try:
            final = Mind.decide(
                self, final_cap, final_budget)
        finally:
            self.score_addend_mode = old_mode

        budget.spend(final_budget.work)
        total = budget.work
        expected = _add(
            stage_a_total_work, final_budget.work)
        if total != expected:
            raise RuntimeError(
                "Candidate-I cumulative work does not equal Stage A + Stage B")
        if any(
                not isfinite(value)
                for value in (
                    total.cycles, total.simulated_steps,
                    total.memory_items, total.replays)):
            raise RuntimeError("Candidate-I invalid cumulative work")
        settlement_gap = max(
            abs(a - b)
            for a, b in zip(
                budget.remaining,
                final_budget.remaining))
        if settlement_gap > 1e-12:
            raise RuntimeError(
                "Candidate-I fallback cumulative body mismatch")

        self._set_branch_decision_settlement(budget.body, total)
        if (self.simulation_mode,
                self.projection_accounting) != (
                "reference", "chunk_end"):
            raise RuntimeError(
                "Candidate-I fallback leaked projector mode")

        action, param, _old, old_info = final
        info = dict(old_info)
        info["experimental_policy"] = POLICY
        info["candidate_i_route"] = "P1.3_BASE_FINAL"
        info["candidate_i_relevance"] = "FALLBACK"
        info["candidate_i_probe_funding"] = "FUNDED"
        info["candidate_h_probe_funding"] = "FUNDED"
        info["candidate_i_stage_a_work"] = asdict(
            stage_a_total_work)
        info["candidate_i_stage_a_body_after"] = tuple(
            stage_a_total_body)
        info["candidate_i_stage_b_work"] = asdict(
            final_budget.work)
        info["candidate_i_total_work"] = asdict(total)
        info["candidate_i_body_after_cognition"] = tuple(
            budget.remaining)
        info["candidate_i_direct_trial_count"] = (
            stage_a["direct_trial_count"])
        info["candidate_i_imagined_trial_count"] = (
            stage_a["imagined_trial_count"])
        info["persistent_simulation_mode"] = "reference"
        info["persistent_projection_accounting"] = "chunk_end"
        info["first_contact_omega"] = self.first_contact_omega
        info["omega_source"] = self.first_contact_omega_source
        info["decision_projection_mode"] = "reference"
        info["candidate_i_first_contact_addend_mode"] = (
            "discard_both_bonus_terms")
        return action, param, total, info


__all__ = [
    "POLICY", "PersonalSharedPriorCandidateIMind",
]
