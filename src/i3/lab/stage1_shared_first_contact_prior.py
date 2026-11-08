"""Frozen Stage-1 shared first-contact prior software falsifier.

Protocol: docs/STAGE1_SHARED_FIRST_CONTACT_PRIOR.md.
Software only: no World, life, runtime registration or motor authority.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import math
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    cognitive_cost, debit_cognition)
from ..modules.recent_rms_effect_prior import (
    paid_recent_rms_zero_mean_effect_prior)
from ..modules.reference_frontier_information_mind import (
    _add, _simulation_upper)
from ..modules.unknown_action_trial import (
    _minimum_ceiling as _unknown_minimum_ceiling,
    paid_unknown_action_trial_value)
from ..modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)
from . import stage1_candidate_g_projection_dependence as D
from . import stage1_candidate_g_reference_recurrence_falsifier as G
from . import stage1_candidate_h_post_contact_relevance as P
from . import stage1_candidate_h_relevance_fallback as H
from . import stage1_candidate_h_unified_integration as U

SCHEMA = "i3-stage1-shared-first-contact-prior/v1"
TOL = 1e-12
OMEGAS = (-1.0, -0.5, 0.0, 0.25, 0.5, 1.0)
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
PERCEIVED_COMMON = (("no-trial", ()),)
ORDINARY_PLANS = dict(H.ORDINARY_PLANS)


def _work_from_dict(value):
    return CognitiveWork(*(int(value[key]) for key in WORK_KEYS))


def _work_add(left, right):
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key) for key in WORK_KEYS))


def _work_dict(work):
    return asdict(work)


def _top(scores):
    if not scores:
        return ()
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items()
        if value >= best - TOL))


def _rms_prior_work_ceiling(memory):
    """Exact structural quote for paid_recent_rms_zero_mean_effect_prior."""
    retained = len(memory._samples)
    support = min(retained, 3)
    cycles = 1
    memory_items = 7 * retained + 2
    if support < 2:
        cycles += 1
        memory_items += 2
    else:
        cycles += 2
        memory_items += 5 * support + 12
    return CognitiveWork(cycles=cycles, memory_items=memory_items)


def _same_scores(left, right):
    if left.keys() != right.keys():
        return False, None
    worst = max(
        (abs(left[key] - right[key]) for key in left),
        default=0.0)
    return worst <= TOL, worst


def _reference_perceived_phase(body, horizon, action_key, mind=None):
    """P1.3 score geometry for ordinary plans plus the directly offered trial."""
    mind = G.make_mind() if mind is None else deepcopy(mind)
    plans = dict(ORDINARY_PLANS)
    plans["perceived_trial"] = (tuple(action_key),)
    ceiling = CognitiveWork()
    for plan in plans.values():
        ceiling = _add(ceiling, _simulation_upper(mind, plan, horizon))
    try:
        forecast_body, _ = debit_cognition(body, BodyLaws(), ceiling)
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "scores": None,
            "top": (),
            "work": _work_dict(CognitiveWork()),
            "forecast_work_ceiling": _work_dict(ceiling),
            "body_after_computation": tuple(body),
        }
    budget = CognitiveBudget(body, BodyLaws())
    scores = {}
    for name, plan in plans.items():
        scores[name] = mind.simulate(
            forecast_body, plan, horizon, budget)[0]
    if any(
            getattr(budget.work, key) > getattr(ceiling, key)
            for key in WORK_KEYS):
        raise RuntimeError("perceived P1.3 fallback exceeded its ceiling")
    return {
        "status": "FUNDED",
        "scores": scores,
        "top": _top(scores),
        "work": _work_dict(budget.work),
        "forecast_work_ceiling": _work_dict(ceiling),
        "body_after_computation": budget.remaining,
    }


def _perceived_probe(body, horizon, action_key, omega, memory=None):
    """One generic perceived unsupported-action probe under Candidate-F geometry."""
    memory = G.effect_memory() if memory is None else memory
    model = D.make_mind("candidate_f_projection")
    action_key = tuple(action_key)
    post = (
        ("stop-after-trial", ()),
        ("repeat-trial", (action_key,)),
    )
    prior_quote = _rms_prior_work_ceiling(memory)
    common_dict = {name: plan for name, plan in PERCEIVED_COMMON}
    post_dict = {name: plan for name, plan in post}
    _prep, ceiling = _unknown_minimum_ceiling(
        model, prior_quote, (None, None), action_key,
        common_dict, post_dict, horizon, CognitiveWork())
    for plan in ORDINARY_PLANS.values():
        ceiling = _add(ceiling, _simulation_upper(model, plan, horizon))

    budget = CognitiveBudget(body, BodyLaws())
    try:
        forecast_body, _ = debit_cognition(
            body, BodyLaws(), ceiling)
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "relevant": False,
            "work": _work_dict(CognitiveWork()),
            "forecast_work_ceiling": _work_dict(ceiling),
            "body_after_computation": tuple(body),
        }

    def prior_source(allowance):
        return paid_recent_rms_zero_mean_effect_prior(
            memory, allowance, omega=omega)

    try:
        trial = paid_unknown_action_trial_value(
            model, action_key, PERCEIVED_COMMON, post, horizon, budget,
            forecast_work=ceiling, prior_source=prior_source)
        ordinary = {}
        for name, plan in ORDINARY_PLANS.items():
            ordinary[name] = model.simulate(
                forecast_body, plan, horizon, budget)[0]
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "relevant": False,
            "work": _work_dict(budget.work),
            "forecast_work_ceiling": _work_dict(ceiling),
            "body_after_computation": budget.remaining,
        }

    if any(
            getattr(budget.work, key) > getattr(ceiling, key)
            for key in WORK_KEYS):
        raise RuntimeError("perceived shared-prior probe exceeded common ceiling")
    informed = trial["trial_informed_value"]
    if type(informed) not in (int, float) or not math.isfinite(informed):
        raise RuntimeError("perceived trial did not produce finite informed value")
    relevant = (
        informed > trial["no_trial_value"] + TOL
        and all(informed > value + TOL for value in ordinary.values()))
    scores = dict(ordinary)
    scores["perceived_trial"] = informed
    return {
        "status": "FUNDED",
        "relevant": relevant,
        "trial": trial,
        "ordinary_scores": ordinary,
        "scores": scores,
        "top": _top(scores),
        "work": _work_dict(budget.work),
        "forecast_work_ceiling": _work_dict(ceiling),
        "body_after_computation": budget.remaining,
        "shared_effect_prior": dict(trial["prior_record"]),
    }


def _imagined_row(body, horizon, omega):
    memory = G.effect_memory()
    budget = CognitiveBudget(body, BodyLaws())
    try:
        result = paid_water_personal_recurrence_value(
            D.make_mind("candidate_f_projection"),
            memory, G.recurrence_2_6_10(),
            G.EXPLORE, G.ORDINARY, horizon, budget, omega=omega)
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "relevant": False,
            "work": _work_dict(budget.work),
            "body_after_computation": budget.remaining,
        }
    relevant = (
        "TRIAL" in result["target_node_best_choices"]
        and result["trial_information_value"] > TOL
        and result["trial_advantage"] > TOL)
    return {
        "status": "FUNDED",
        "relevant": relevant,
        "target_choices": tuple(result["target_node_best_choices"]),
        "information_value": result["trial_information_value"],
        "trial_advantage": result["trial_advantage"],
        "trial_frozen_value": result.get("trial_frozen_value"),
        "trial_informed_value": result.get("trial_informed_value"),
        "no_trial_value": result.get("decline_value"),
        "expectation_part": (
            None if result.get("trial_frozen_value") is None
            else result["trial_frozen_value"] - result["decline_value"]),
        "work": dict(result["work"]),
        "forecast_work_ceiling": dict(result["forecast_work_ceiling"]),
        "body_after_computation": tuple(result["body_after_computation"]),
        "shared_effect_prior": dict(result["shared_effect_prior"]),
    }


def _settle(body, first, second):
    combined = _work_add(
        _work_from_dict(first["work"]),
        _work_from_dict(second["work"]))
    try:
        final, _ = debit_cognition(body, BodyLaws(), combined)
    except CognitiveFundingError:
        return combined, None
    return combined, final


def _imagined_full(body, horizon, omega):
    stage_a = _imagined_row(body, horizon, omega)
    pre = H._reference_four_plan_phase(body, horizon)
    if stage_a["status"] != "FUNDED":
        return {
            "status": "STAGE_A_UNFUNDED", "stage_a": stage_a,
            "fallback": None, "control": None, "preprobe": pre,
        }
    if stage_a["relevant"]:
        return {
            "status": "RELEVANT", "stage_a": stage_a,
            "fallback": None, "control": None, "preprobe": pre,
            "combined_work": dict(stage_a["work"]),
            "combined_body_after_computation":
                stage_a["body_after_computation"],
        }
    fallback = H._reference_four_plan_phase(
        stage_a["body_after_computation"], horizon)
    control = H._reference_four_plan_phase(
        stage_a["body_after_computation"], horizon)
    if fallback["status"] != "FUNDED":
        return {
            "status": "FALLBACK_UNFUNDED", "stage_a": stage_a,
            "fallback": fallback, "control": control, "preprobe": pre,
        }
    combined, final = _settle(body, stage_a, fallback)
    return {
        "status": "FALLBACK",
        "stage_a": stage_a,
        "fallback": fallback,
        "control": control,
        "preprobe": pre,
        "combined_work": _work_dict(combined),
        "combined_body_after_computation": final,
    }


def _perceived_full(body, horizon, action_key, omega):
    stage_a = _perceived_probe(body, horizon, action_key, omega)
    pre = _reference_perceived_phase(body, horizon, action_key)
    if stage_a["status"] != "FUNDED":
        return {
            "status": "STAGE_A_UNFUNDED", "stage_a": stage_a,
            "fallback": None, "control": None, "preprobe": pre,
        }
    if stage_a["relevant"]:
        return {
            "status": "RELEVANT", "stage_a": stage_a,
            "fallback": None, "control": None, "preprobe": pre,
            "combined_work": dict(stage_a["work"]),
            "combined_body_after_computation":
                stage_a["body_after_computation"],
        }
    fallback = _reference_perceived_phase(
        stage_a["body_after_computation"], horizon, action_key)
    control = _reference_perceived_phase(
        stage_a["body_after_computation"], horizon, action_key)
    if fallback["status"] != "FUNDED":
        return {
            "status": "FALLBACK_UNFUNDED", "stage_a": stage_a,
            "fallback": fallback, "control": control, "preprobe": pre,
        }
    combined, final = _settle(body, stage_a, fallback)
    return {
        "status": "FALLBACK",
        "stage_a": stage_a,
        "fallback": fallback,
        "control": control,
        "preprobe": pre,
        "combined_work": _work_dict(combined),
        "combined_body_after_computation": final,
    }


def _has_personal_action_support(mind, action_key):
    """Action-class support only; token spelling never enters this predicate."""
    action = tuple(action_key)[0]
    return any(
        key[0] == action and state[2] > 0
        for key, state in mind.effects.stats.items())


def _supported_negative_control(mind, body, horizon, action_key):
    """Supported first actions must bypass the unsupported-action probe."""
    if not _has_personal_action_support(mind, action_key):
        raise RuntimeError("negative control lacks frozen personal action support")
    final = _reference_perceived_phase(body, horizon, action_key, mind)
    control = _reference_perceived_phase(body, horizon, action_key, mind)
    if final["status"] != control["status"]:
        raise RuntimeError("negative-control reference status mismatch")
    if final["status"] != "FUNDED":
        return {
            "probe_executed": False,
            "final": final,
            "control": control,
            "score_identity": True,
            "score_max_error": 0.0,
            "work_identity": final["work"] == control["work"],
        }
    same, error = _same_scores(final["scores"], control["scores"])
    return {
        "probe_executed": False,
        "final": final,
        "control": control,
        "score_identity": same,
        "score_max_error": error,
        "work_identity": final["work"] == control["work"],
    }


def _negative_mind(kind):
    mind = G.make_mind()
    if kind == "P80-SUPPORTED":
        mind.effects.observe(("boire",), (-0.5, -0.2, 35.0, 0.0, 0.0))
    elif kind == "F108-MIXED":
        mind.effects.observe(
            ("manger", "known-safe"), (0.0, 30.0, 0.0, 0.0, 0.0))
        mind.effects.observe(
            ("manger", "known-toxic"), (0.0, 30.0, 0.0, -35.0, 0.0))
    elif kind == "F108-HARMFUL":
        mind.effects.observe(
            ("manger", "known-a"), (0.0, 5.0, 0.0, -20.0, 0.0))
        mind.effects.observe(
            ("manger", "known-b"), (0.0, 10.0, 0.0, -30.0, 0.0))
    else:
        raise ValueError("unknown negative-control history")
    return mind


def _state_key(channel, level, horizon):
    return (channel, float(level), int(horizon))


def _grid80():
    for channel, name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                yield channel, name, level, body, horizon


def _grid108():
    for energy in (35.0, 60.0, 85.0):
        for food in (5.0, 20.0, 40.0):
            for integrity in (20.0, 50.0, 80.0):
                body = (energy, food, 80.0, integrity, 80.0)
                for horizon in G.HORIZONS:
                    yield energy, food, integrity, body, horizon


def _fallback_checks(rows):
    failures = []
    accounting = []
    preprobe_changes = []
    for row in rows:
        if row["status"] != "FALLBACK":
            continue
        same, error = _same_scores(
            row["fallback"]["scores"], row["control"]["scores"])
        if not same or row["fallback"]["top"] != row["control"]["top"]:
            failures.append({
                "identity": row["identity"], "score_error": error})
        if row["fallback"]["top"] != row["preprobe"]["top"]:
            preprobe_changes.append(row["identity"])
        combined = _work_from_dict(row["combined_work"])
        bill = cognitive_cost(BodyLaws(), combined)
        if not all(math.isfinite(x) and x >= 0.0 for x in bill):
            accounting.append({
                "identity": row["identity"], "reason": "INVALID_BILL"})
            continue
        try:
            final, _ = debit_cognition(
                row["body"], BodyLaws(), combined)
        except CognitiveFundingError:
            accounting.append({
                "identity": row["identity"], "reason": "COMBINED_UNFUNDED"})
            continue
        reported = row["combined_body_after_computation"]
        if reported is None or any(
                abs(a - b) > TOL for a, b in zip(final, reported)):
            accounting.append({
                "identity": row["identity"], "reason": "BODY_MISMATCH"})
    return failures, accounting, preprobe_changes


def _phase_accounting_failures(rows):
    failures = []
    for row in rows:
        stage = row["stage_a"]
        stage_work = _work_from_dict(stage["work"])
        try:
            stage_body, _ = debit_cognition(
                row["body"], BodyLaws(), stage_work)
        except CognitiveFundingError:
            failures.append({
                "identity": row["identity"],
                "reason": "STAGE_A_RECORDED_WORK_UNFUNDED"})
            continue
        if any(
                abs(a - b) > TOL
                for a, b in zip(
                    stage_body, stage["body_after_computation"])):
            failures.append({
                "identity": row["identity"],
                "reason": "STAGE_A_BODY_MISMATCH"})
            continue

        if row["status"] == "FALLBACK":
            fallback_work = _work_from_dict(row["fallback"]["work"])
            expected = _work_add(stage_work, fallback_work)
            if _work_from_dict(row["combined_work"]) != expected:
                failures.append({
                    "identity": row["identity"],
                    "reason": "COMBINED_WORK_SUM_MISMATCH"})
                continue
            try:
                final, _ = debit_cognition(
                    row["body"], BodyLaws(), expected)
            except CognitiveFundingError:
                failures.append({
                    "identity": row["identity"],
                    "reason": "COMBINED_RECORDED_WORK_UNFUNDED"})
                continue
            if any(
                    abs(a - b) > TOL
                    for a, b in zip(
                        final, row["combined_body_after_computation"])):
                failures.append({
                    "identity": row["identity"],
                    "reason": "COMBINED_BODY_MISMATCH"})
        elif row["status"] == "RELEVANT":
            if _work_from_dict(row["combined_work"]) != stage_work:
                failures.append({
                    "identity": row["identity"],
                    "reason": "RELEVANT_WORK_NOT_STAGE_A"})
            elif any(
                    abs(a - b) > TOL
                    for a, b in zip(
                        stage_body, row["combined_body_after_computation"])):
                failures.append({
                    "identity": row["identity"],
                    "reason": "RELEVANT_BODY_MISMATCH"})
        elif row["status"] == "FALLBACK_UNFUNDED":
            if row["fallback"]["work"] != _work_dict(CognitiveWork()):
                failures.append({
                    "identity": row["identity"],
                    "reason": "UNFUNDED_FALLBACK_SPENT_WORK"})
    return failures


def _summary(rows):
    return {
        "states": len(rows),
        "relevant": sum(row["status"] == "RELEVANT" for row in rows),
        "fallback": sum(row["status"] == "FALLBACK" for row in rows),
        "fallback_unfunded":
            sum(row["status"] == "FALLBACK_UNFUNDED" for row in rows),
        "stage_a_unfunded":
            sum(row["status"] == "STAGE_A_UNFUNDED" for row in rows),
    }


def characterize():
    # D0: old Candidate-H gates must remain green at the new source.
    first_old = H.characterize()
    post_old = P.characterize()
    unified_old = U.characterize()

    imagined = {}
    perceived_water = {}
    perceived_food = {}
    for omega in OMEGAS:
        krows = []
        prows = []
        for channel, name, level, body, horizon in _grid80():
            kr = _imagined_full(body, horizon, omega)
            kr.update({
                "identity": ("K80", channel, level, horizon),
                "channel": name, "channel_index": channel,
                "level": level, "horizon": horizon, "body": body})
            krows.append(kr)

            pr = _perceived_full(body, horizon, ("boire",), omega)
            pr.update({
                "identity": ("P80", channel, level, horizon),
                "channel": name, "channel_index": channel,
                "level": level, "horizon": horizon, "body": body,
                "action_channel_index": 2})
            prows.append(pr)
        imagined[omega] = krows
        perceived_water[omega] = prows

        frows = []
        for energy, food, integrity, body, horizon in _grid108():
            fr = _perceived_full(
                body, horizon, ("manger", "carried-first-contact"), omega)
            fr.update({
                "identity": (
                    "F108", energy, food, integrity, horizon),
                "energy": energy, "food": food, "integrity": integrity,
                "horizon": horizon, "body": body,
                "action_channel_index": 1})
            frows.append(fr)
        perceived_food[omega] = frows

    # D1 quote identity across omega.
    def quotes(rows):
        return [
            row["stage_a"].get("forecast_work_ceiling")
            for row in rows]
    k_quote_identity = all(
        quotes(imagined[omega]) == quotes(imagined[0.0])
        for omega in OMEGAS)
    p_quote_identity = all(
        quotes(perceived_water[omega]) == quotes(perceived_water[0.0])
        for omega in OMEGAS)
    f_quote_identity = all(
        quotes(perceived_food[omega]) == quotes(perceived_food[0.0])
        for omega in OMEGAS)

    # D2/D3 on all three paths and all arms.
    fallback_identity_failures = []
    accounting_failures = []
    preprobe_changes = []
    for path, arms in (
            ("K80", imagined),
            ("P80", perceived_water),
            ("F108", perceived_food)):
        for omega, rows in arms.items():
            ident, accounting, changed = _fallback_checks(rows)
            phase_accounting = _phase_accounting_failures(rows)
            fallback_identity_failures.extend(
                [{"path": path, "omega": omega, **row} for row in ident])
            accounting_failures.extend(
                [{"path": path, "omega": omega, **row}
                 for row in accounting])
            accounting_failures.extend(
                [{"path": path, "omega": omega, **row}
                 for row in phase_accounting])
            preprobe_changes.extend(
                [{"path": path, "omega": omega, "identity": row}
                 for row in changed])

    # D4: known/supported first actions never enter the perceived probe.
    negative = []
    for _channel, _name, _level, body, horizon in _grid80():
        negative.append(
            ("P80-SUPPORTED",
             _supported_negative_control(
                 _negative_mind("P80-SUPPORTED"),
                 body, horizon, ("boire",))))
    for _energy, _food, _integrity, body, horizon in _grid108():
        negative.append(
            ("F108-MIXED",
             _supported_negative_control(
                 _negative_mind("F108-MIXED"),
                 body, horizon, ("manger", "carried-first-contact"))))
        negative.append(
            ("F108-HARMFUL",
             _supported_negative_control(
                 _negative_mind("F108-HARMFUL"),
                 body, horizon, ("manger", "carried-first-contact"))))
    d4 = all(
        not row["probe_executed"]
        and row["score_identity"]
        and row["work_identity"]
        for _name, row in negative)

    # D6: external/internal token renaming must not matter.
    rename_mismatches = []
    for omega in OMEGAS:
        for energy, food, integrity, body, horizon in _grid108():
            a = _perceived_probe(
                body, horizon, ("manger", "carried-first-contact"), omega)
            b = _perceived_probe(
                body, horizon, ("manger", "renamed-token"), omega)
            comparable = {
                key: a.get(key)
                for key in (
                    "status", "relevant", "ordinary_scores", "scores",
                    "top", "work", "forecast_work_ceiling",
                    "body_after_computation", "shared_effect_prior")}
            renamed = {
                key: b.get(key)
                for key in comparable}
            if comparable != renamed:
                rename_mismatches.append({
                    "omega": omega,
                    "identity": (energy, food, integrity, horizon)})

    # D7: same paid RMS effect-prior record in imagined and perceived paths.
    shared_prior_mismatches = []
    shared_prior_keys = ("status", "rms_scale", "omega", "branch_deltas")
    for omega in OMEGAS:
        for idx, (krow, prow) in enumerate(zip(
                imagined[omega], perceived_water[omega])):
            if (krow["stage_a"]["status"] != "FUNDED"
                    or prow["stage_a"]["status"] != "FUNDED"):
                continue
            ki = krow["stage_a"]["shared_effect_prior"]
            pi = prow["stage_a"]["shared_effect_prior"]
            if any(ki.get(key) != pi.get(key) for key in shared_prior_keys):
                shared_prior_mismatches.append({
                    "omega": omega, "index": idx,
                    "imagined": {key: ki.get(key) for key in shared_prior_keys},
                    "perceived": {key: pi.get(key) for key in shared_prior_keys},
                })

    zero_k = _summary(imagined[0.0])
    zero_p = _summary(perceived_water[0.0])

    # Primary capacity: perceived water first contact newly relevant vs omega=0.
    p0_relevant = {
        row["identity"] for row in perceived_water[0.0]
        if row["status"] == "RELEVANT"}
    newly_relevant = {}
    for omega in OMEGAS:
        if omega <= 0:
            continue
        newly_relevant[str(omega)] = [
            row["identity"] for row in perceived_water[omega]
            if row["status"] == "RELEVANT"
            and row["identity"] not in p0_relevant]

    # Reported direction and secondary paths.
    counts = {
        "K80": {str(o): _summary(rows) for o, rows in imagined.items()},
        "P80": {
            str(o): _summary(rows) for o, rows in perceived_water.items()},
        "F108": {
            str(o): _summary(rows) for o, rows in perceived_food.items()},
    }
    order = list(OMEGAS)
    monotone = {}
    for path in ("K80", "P80", "F108"):
        monotone[path] = all(
            counts[path][str(a)]["relevant"]
            <= counts[path][str(b)]["relevant"]
            for a, b in zip(order, order[1:]))

    need_agnostic = {"P80": {}, "F108": {}}
    for omega in OMEGAS:
        need_agnostic["P80"][str(omega)] = [
            row["identity"] for row in perceived_water[omega]
            if row["status"] == "RELEVANT"
            and row["channel_index"] != 2]
        need_agnostic["F108"][str(omega)] = [
            row["identity"] for row in perceived_food[omega]
            if row["status"] == "RELEVANT"
            and row["food"] > min(
                row["body"][0], row["body"][1], row["body"][3]) + TOL]

    d0 = (
        first_old["verdict"]
        == "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS"
        and post_old["verdict"]
        == "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS"
        and unified_old["verdict"]
        == "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS"
        and zero_k["states"] == 80
        and zero_k["relevant"] == 24
        and zero_k["fallback"] == 56
        and sum(
            row["stage_a"].get("target_choices") == ("DECLINE_TRIAL",)
            for row in imagined[0.0]) == 40
        and all(
            all(
                row["stage_a"]["work"][key]
                <= row["stage_a"]["forecast_work_ceiling"][key]
                for key in WORK_KEYS)
            for row in imagined[0.0]
            if row["stage_a"]["status"] == "FUNDED")
        and abs(
            sum(
                row["stage_a"]["work"]["simulated_steps"]
                for row in imagined[0.0])
            / 80.0 - 470.05) <= 1e-9)
    rules = {
        "D0_candidate_h_identity_at_omega0": d0,
        "D1_quote_identity": (
            k_quote_identity and p_quote_identity and f_quote_identity),
        "D2_fallback_identity": not fallback_identity_failures,
        "D3_physical_accounting": not accounting_failures,
        "D4_negative_controls": d4,
        "D5_authority_and_genericity_boundaries": all(
            record.get("action_identity_used") is False
            and record.get("token_identity_used") is False
            and record.get("body_need_used") is False
            and record.get("world_access") is False
            for arms in (imagined, perceived_water, perceived_food)
            for rows in arms.values()
            for row in rows
            if row["stage_a"].get("status") == "FUNDED"
            for record in (row["stage_a"]["shared_effect_prior"],)),
        "D6_renaming": not rename_mismatches,
        "D7_shared_prior_identity": not shared_prior_mismatches,
    }
    defects_ok = all(rules.values())
    r1 = any(newly_relevant.values())
    verdict = (
        "SHARED_FIRST_CONTACT_PRIOR_DEFECT"
        if not defects_ok else
        "SHARED_FIRST_CONTACT_PRIOR_CAPACITY_SHOWN"
        if r1 else
        "SHARED_FIRST_CONTACT_PRIOR_NO_CAPACITY")

    def path_work(rows):
        complete = [
            row for row in rows
            if row["status"] in ("RELEVANT", "FALLBACK")]
        if not complete:
            return {"states": 0}
        combined = [
            row.get("combined_work", row["stage_a"]["work"])
            for row in complete]
        bills = [
            cognitive_cost(BodyLaws(), _work_from_dict(work))
            for work in combined]
        return {
            "states": len(complete),
            "mean_simulated_steps":
                sum(w["simulated_steps"] for w in combined) / len(combined),
            "max_simulated_steps":
                max(w["simulated_steps"] for w in combined),
            "mean_energy":
                sum(b[0] for b in bills) / len(bills),
            "max_energy": max(b[0] for b in bills),
            "mean_vigilance":
                sum(b[1] for b in bills) / len(bills),
            "max_vigilance": max(b[1] for b in bills),
        }

    work = {
        path: {
            str(omega): path_work(rows)
            for omega, rows in arms.items()}
        for path, arms in (
            ("K80", imagined),
            ("P80", perceived_water),
            ("F108", perceived_food))
    }

    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_SHARED_FIRST_CONTACT_PRIOR.md",
        "world_access": False,
        "lives": 0,
        "runtime_registered": False,
        "motor_command_authorized": False,
        "omega_arms": OMEGAS,
        "counts": counts,
        "direction_monotone": monotone,
        "newly_relevant_p80_vs_omega0": newly_relevant,
        "need_agnostic_relevance": need_agnostic,
        "work": work,
        "rows": {
            "K80": {str(o): rows for o, rows in imagined.items()},
            "P80": {str(o): rows for o, rows in perceived_water.items()},
            "F108": {str(o): rows for o, rows in perceived_food.items()},
        },
        "fallback_identity_failures": fallback_identity_failures,
        "physical_accounting_failures": accounting_failures,
        "fallback_top_changes_vs_preprobe": preprobe_changes,
        "negative_control_count": len(negative),
        "renaming_mismatches": rename_mismatches,
        "shared_prior_mismatches": shared_prior_mismatches,
        "rules": rules,
        "R1_primary_perceived_water_capacity": r1,
        "verdict": verdict,
        "runtime_change_authorized": False,
        "new_live_panel_authorized": False,
        "selection_validation_reserve_authorized": False,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("SHARED_FIRST_CONTACT_PRIOR " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "counts": report["counts"],
        "direction_monotone": report["direction_monotone"],
        "newly_relevant_p80_vs_omega0":
            report["newly_relevant_p80_vs_omega0"],
        "renaming_mismatches": report["renaming_mismatches"],
        "shared_prior_mismatches": report["shared_prior_mismatches"],
    }, sort_keys=True))
