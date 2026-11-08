"""Paid multi-option unsupported first-contact value composition.

Software kernel only. Every simultaneously offered unsupported direct resource
trial is evaluated under one conservative Candidate-F forecast body and one
common work ceiling. No motor command is authorized here.
"""
from __future__ import annotations

from dataclasses import asdict
from math import isfinite

from .body import (
    CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL,
    debit_cognition)
from .information_value import WORK_KEYS, _add_work
from .plan_information import _validate_plan
from .recent_rms_effect_prior import (
    paid_recent_rms_zero_mean_effect_prior,
    recent_rms_effect_prior_work_ceiling)
from .reference_branches import ReferenceBranchMemory
from .unknown_action_trial import (
    _minimum_ceiling as _trial_minimum_ceiling,
    _simulation_upper as _trial_simulation_upper,
    paid_unknown_action_trial_value)

SCHEMA = "i3-shared-perceived-first-contact-multi-trial/v1"
TOL = 1e-12
COMMON = (("no-trial", ()),)


def _top(scores):
    if not scores:
        return ()
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items()
        if value >= best - TOL))


def direct_trial_strict_winners(trial_rows, with_information_scores):
    """Return trials satisfying frozen v2 own-no-trial + strict-winner rules."""
    if type(with_information_scores) is not dict:
        raise ValueError("with_information_scores must be a dict")
    winners = []
    for row in trial_rows:
        oid = row["option"]
        informed = row["trial_informed_value"]
        no_trial = row["no_trial_value"]
        if (type(informed) not in (int, float)
                or type(no_trial) not in (int, float)
                or not isfinite(informed) or not isfinite(no_trial)):
            continue
        own_advantage = informed > no_trial + TOL
        strict_best = own_advantage and all(
            informed > value + TOL
            for other, value in with_information_scores.items()
            if other != oid)
        if strict_best:
            winners.append(oid)
    if len(winners) > 1:
        raise RuntimeError("strict first-contact winner cannot be non-unique")
    return tuple(winners)


def _delta(after, before):
    return CognitiveWork(*(
        getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS))


def _leq(left, right):
    return all(
        getattr(left, key) <= getattr(right, key)
        for key in WORK_KEYS)


def _validate_trials(opts, unsupported_trials):
    if type(unsupported_trials) is not tuple or not unsupported_trials:
        raise ValueError("nonempty immutable unsupported-trial tuple required")
    by_id = {oid: (oid, tuple(plan), first) for oid, plan, first in opts}
    if len(by_id) != len(opts):
        raise ValueError("unique offered option identifiers required")

    seen = set()
    out = []
    for item in unsupported_trials:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("trial option/action-key pair required")
        oid, action_key = item
        if type(oid) is not str or oid not in by_id or oid in seen:
            raise ValueError("unique offered trial option required")
        if type(action_key) is not tuple:
            raise ValueError("immutable action key required")
        _validate_plan((action_key,))
        if action_key[0] not in ("boire", "manger"):
            raise ValueError("only directly perceived drink/eat trials allowed")
        if action_key[0] == "boire" and len(action_key) != 1:
            raise ValueError("drink trial cannot carry a token")
        if action_key[0] == "manger" and len(action_key) != 2:
            raise ValueError("food trial requires exact internal token")
        _oid, plan, _first = by_id[oid]
        if plan != (action_key,):
            raise ValueError(
                "direct first-contact trial must be the offered one-action plan")
        seen.add(oid)
        out.append((oid, action_key))
    return by_id, tuple(out)


def _ordinary_upper(model, oid, plan, horizon):
    work = _trial_simulation_upper(model, plan, horizon)
    presence = getattr(model, "_presence", {})
    if oid in presence:
        _probability, travel = presence[oid]
        work = _add_work(
            work, _trial_simulation_upper(model, tuple(travel), horizon))
    return work


def paid_shared_perceived_first_contact(
        model, memory: ReferenceBranchMemory, opts, unsupported_trials,
        horizon: int, budget: CognitiveBudget, *, omega: float,
        competition_cycles: int = 0) -> dict:
    """Evaluate all direct unsupported trials under one paid score geometry."""
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no first-contact cognition after physical death")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer horizon required")
    if type(competition_cycles) is not int or competition_cycles < 0:
        raise ValueError("nonnegative integer competition ceiling required")
    if (not callable(getattr(model, "simulate", None))
            or not hasattr(model, "proj_chunks")
            or not hasattr(model, "d_max")):
        raise ValueError("P1.3-compatible model required")

    opts = tuple(
        (oid, tuple(plan), first)
        for oid, plan, first in opts)
    _by_id, trials = _validate_trials(opts, unsupported_trials)
    trial_ids = {oid for oid, _key in trials}
    ordinary = tuple(
        (oid, plan, first)
        for oid, plan, first in opts if oid not in trial_ids)

    original_work = budget.work
    prior_quote = recent_rms_effect_prior_work_ceiling(memory)

    extra = CognitiveWork()
    trial_quotes = {}
    for oid, action_key in trials:
        post = {
            "stop-after-trial": (),
            "repeat-trial": (action_key,),
        }
        common = {"no-trial": ()}
        _prep, increment = _trial_minimum_ceiling(
            model, prior_quote, (None, None), action_key,
            common, post, horizon, CognitiveWork())
        trial_quotes[oid] = increment
        extra = _add_work(extra, increment)

    for oid, plan, _first in ordinary:
        extra = _add_work(
            extra, _ordinary_upper(model, oid, plan, horizon))

    extra = _add_work(
        extra, CognitiveWork(cycles=competition_cycles))
    ceiling = _add_work(original_work, extra)

    try:
        forecast_body, _ = debit_cognition(
            budget.body, budget.laws, ceiling)
    except CognitiveFundingError:
        return {
            "schema": SCHEMA,
            "status": "UNFUNDED_COMPLETE_FIRST_CONTACT_MATRIX",
            "relevant": False,
            "classification": "PROBE_UNFUNDED",
            "probe_funding": "NO_FUNDED_SCORE",
            "trials": (),
            "ordinary_scores": {},
            "with_information_scores": {},
            "without_information_scores": {},
            "with_information_top": (),
            "without_information_top": (),
            "scored": (),
            "score_witnesses": (),
            "work": asdict(_delta(budget.work, original_work)),
            "forecast_work_ceiling": asdict(ceiling),
            "forecast_start_body": None,
            "body_after_computation": budget.remaining,
            "world_access": False,
            "motor_command_authorized": False,
        }

    trial_rows = []
    complete = True
    for oid, action_key in trials:
        post = (
            ("stop-after-trial", ()),
            ("repeat-trial", (action_key,)),
        )

        def prior_source(allowance, _memory=memory, _omega=omega):
            return paid_recent_rms_zero_mean_effect_prior(
                _memory, allowance, omega=_omega)

        result = paid_unknown_action_trial_value(
            model, action_key, COMMON, post, horizon, budget,
            forecast_work=ceiling, prior_source=prior_source)
        if result["status"] != (
                "COMPLETE_UNKNOWN_ACTION_TRIAL_ESTIMATE_NOT_POLICY"):
            complete = False
        trial_rows.append({
            "option": oid,
            "action_key": action_key,
            "status": result["status"],
            "no_trial_value": result["no_trial_value"],
            "trial_frozen_value": result["trial_frozen_value"],
            "trial_informed_value": result["trial_informed_value"],
            "information_value": result["information_value"],
            "trial_advantage": result["trial_advantage"],
            "prior_record": dict(result["prior_record"]),
            "work": dict(result["work"]),
            "minimum_complete_forecast_work":
                dict(result.get("minimum_complete_forecast_work", {})),
        })
        if not _leq(budget.work, ceiling):
            raise RuntimeError(
                "trial work exceeded common first-contact ceiling")

    ordinary_scores = {}
    ordinary_witness = {}
    for oid, plan, _first in ordinary:
        value, _steps, uncertainty = model.simulate(
            forecast_body, plan, horizon, budget)
        first_forecast = (
            getattr(model, "_observer_first_forecast", None)
            if getattr(model, "observer_decision_diagnostics", False)
            else None)
        if oid in getattr(model, "_presence", {}):
            probability, travel = model._presence[oid]
            failed, _failed_steps, _ = model.simulate(
                forecast_body, tuple(travel), horizon, budget)
            value = probability * value + (1.0 - probability) * failed
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("nonfinite ordinary first-contact score")
        ordinary_scores[oid] = float(value)
        ordinary_witness[oid] = {
            "option": oid,
            "base_return": float(value),
            "curiosity_bonus_computed": 0.0,
            "risk_penalty_computed": 0.0,
            "curiosity_bonus_applied": 0.0,
            "risk_penalty_applied": 0.0,
            "curiosity_risk_bonus": 0.0,
            "total_score": float(value),
            "uncertainty": uncertainty,
            "first_forecast": first_forecast,
            "score_kind": "candidate_f_distress_no_addends",
            "information_value": 0.0,
            "common_forecast_work_ceiling": asdict(ceiling),
        }
        if not _leq(budget.work, ceiling):
            raise RuntimeError(
                "ordinary work exceeded common first-contact ceiling")

    with_information = dict(ordinary_scores)
    without_information = dict(ordinary_scores)
    if complete:
        for row in trial_rows:
            with_information[row["option"]] = float(
                row["trial_informed_value"])
            without_information[row["option"]] = float(
                row["trial_frozen_value"])

    with_top = _top(with_information)
    without_top = _top(without_information)
    strict_winners = (
        direct_trial_strict_winners(
            trial_rows, with_information)
        if complete else ())
    relevant = bool(complete and strict_winners)
    v1_top_set_change = bool(
        complete
        and with_top != without_top
        and any(
            row["option"] in with_top
            and row["information_value"] > TOL
            for row in trial_rows))

    witnesses = []
    scored = []
    if relevant:
        rows_by_option = {
            row["option"]: row for row in trial_rows}
        for oid, _plan, _first in opts:
            if oid in ordinary_witness:
                witness = ordinary_witness[oid]
                score = ordinary_scores[oid]
            else:
                row = rows_by_option[oid]
                score = float(row["trial_informed_value"])
                witness = {
                    "option": oid,
                    "base_return": float(row["trial_frozen_value"]),
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
                    "information_value": float(
                        row["information_value"]),
                    "trial_no_trial_value": row["no_trial_value"],
                    "trial_frozen_value": row["trial_frozen_value"],
                    "trial_advantage": row["trial_advantage"],
                    "shared_effect_prior":
                        dict(row["prior_record"]),
                    "common_forecast_work_ceiling":
                        asdict(ceiling),
                }
            scored.append((oid, score))
            witnesses.append(witness)

    actual = _delta(budget.work, original_work)
    return {
        "schema": SCHEMA,
        "status": (
            "COMPLETE_SHARED_FIRST_CONTACT_MATRIX"
            if complete else
            "COMPLETE_NO_EMPIRICAL_FIRST_CONTACT_CAPACITY"),
        "relevant": relevant,
        "classification": "RELEVANT" if relevant else "FALLBACK",
        "probe_funding": "FUNDED",
        "trials": tuple(trial_rows),
        "ordinary_scores": ordinary_scores,
        "with_information_scores": with_information,
        "without_information_scores": without_information,
        "with_information_top": with_top,
        "without_information_top": without_top,
        "strict_trial_winners": strict_winners,
        "v1_top_set_change_diagnostic": v1_top_set_change,
        "scored": tuple(scored),
        "score_witnesses": tuple(witnesses),
        "work": asdict(actual),
        "forecast_work_ceiling": asdict(ceiling),
        "forecast_start_body": forecast_body,
        "body_after_computation": budget.remaining,
        "world_access": False,
        "motor_command_authorized": False,
        "common_projector": "candidate_f",
        "all_trials_evaluated": len(trial_rows) == len(trials),
        "trial_option_order": tuple(oid for oid, _key in trials),
        "ordinary_option_order": tuple(
            oid for oid, _plan, _first in ordinary),
        "quoted_trial_work": {
            oid: asdict(work) for oid, work in trial_quotes.items()},
    }


__all__ = [
    "SCHEMA", "direct_trial_strict_winners",
    "paid_shared_perceived_first_contact",
]
