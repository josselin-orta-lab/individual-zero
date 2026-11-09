"""Frozen physical-accounting sensitivity for the exact separable cache.

Protocol: docs/STAGE1_SEPARABLE_CACHE_ACCOUNTING.md.
No World, life, runtime projection mode or adoption.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import math
import sys

from . import stage1_candidate_g_reference_recurrence_falsifier as G
from . import stage1_candidate_g_projection_dependence as D
from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    E, F, W, I, V, cognitive_cost,
)
from ..modules.forecast_work import projection_simulated_steps_ceiling
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.water_future_opportunity import (
    paid_water_one_future_opportunity_value,
    water_one_future_opportunity_work_ceiling,
)

SCHEMA = "i3-stage1-separable-cache-accounting/v1"
ARMS = ("bundle5_lower", "scalar1_upper")
STEPS = 255
TRACE_KEY_ITEMS = 13
TRACE_STORE_ITEMS = 4 * STEPS + 2 + TRACE_KEY_ITEMS
TRACE_READ_ITEMS = 19
TRACES_PER_PROJECT = 5
COMPLETE_PROJECT_CALLS = 5
SIM_PER_TRACE = {"bundle5_lower": 51, "scalar1_upper": 255}
REFERENCE_PROJECTION_QUOTE = 8
CANDIDATE_F_SELECTED = 24
CANDIDATE_F_MEAN_BILL = {"energy": 1.3402, "vigilance": 1.840}


def _add(a, b):
    return CognitiveWork(*(
        getattr(a, k) + getattr(b, k)
        for k in ("cycles", "simulated_steps", "memory_items", "replays")
    ))


def _delta(after, before):
    return CognitiveWork(*(
        getattr(after, k) - getattr(before, k)
        for k in ("cycles", "simulated_steps", "memory_items", "replays")
    ))


def _clamp(x):
    return 0.0 if x < 0.0 else 100.0 if x > 100.0 else x


class PaidSeparableCachedMind(Mind):
    """Exact #1151 trace cache with the frozen #116? accounting arms."""

    def __init__(self, genome, life_seed, *, accounting_arm):
        if accounting_arm not in ARMS:
            raise ValueError("unknown exact-cache accounting arm")
        super().__init__(genome, life_seed)
        self.cache_accounting_arm = accounting_arm
        self._sep_cache = {}
        self._sep_stats = {
            "project_calls": 0,
            "trace_builds": 0,
            "trace_hits": 0,
            "channel_samples": 0,
            "memory_writes": 0,
            "memory_reads": 0,
            "max_live_entries": 0,
        }

    def cache_stats(self):
        return dict(self._sep_stats)

    def _restore_schedule(self, body, restore):
        if restore is None:
            return (0.0,) * STEPS
        energy, vigilance = float(body[E]), float(body[V])
        schedule = []
        for _ in range(STEPS):
            need_e = max(0.0, self.theta[E] - energy) / restore[0]
            need_v = (
                max(0.0, self.theta[V] - vigilance) / restore[1]
                if restore[1] > 0.0 else 0.0)
            n = min(1.0, max(need_e, need_v))
            energy = _clamp(energy + n * restore[0])
            vigilance = _clamp(vigilance + n * restore[1])
            schedule.append(n)
        return tuple(schedule)

    def _trace_key(self, channel, body, drift, restore):
        if restore is None:
            restoration = None
        else:
            restoration = (
                float(body[E]), float(body[V]),
                float(restore[0]), float(restore[1]), float(restore[2]),
                float(self.theta[E]), float(self.theta[V]),
            )
        if channel in (E, F, V):
            return (
                channel, float(body[channel]), float(drift[channel]),
                restoration, float(self.theta[channel]),
                float(self.p[channel]), float(self.w[channel]),
            )
        return (
            channel, float(body[channel]), float(drift[channel]),
            float(self.theta[channel]), float(self.p[channel]),
            float(self.w[channel]),
        )

    def _build_trace(
            self, channel, body, drift, restore, schedule, budget):
        budget.spend(CognitiveWork(
            simulated_steps=SIM_PER_TRACE[self.cache_accounting_arm],
            memory_items=TRACE_STORE_ITEMS,
        ))

        x = float(body[channel])
        levels = []
        prefixes = [[], [], []]
        sums = [0.0, 0.0, 0.0]
        powers = [1.0, 1.0, 1.0]
        death_step = None
        final_contribution = 0.0

        for step in range(STEPS):
            if channel in (F, W, I):
                x += drift[channel]
            if restore is not None:
                n = schedule[step]
                if channel == E:
                    x += n * restore[0]
                elif channel == F:
                    x += n * restore[2]
                elif channel == V:
                    x += n * restore[1]
            x = _clamp(x)

            z = (self.theta[channel] - x) / self.theta[channel]
            final_contribution = (
                self.w[channel] * (z ** self.p[channel])
                if z > 0.0 else 0.0)

            levels.append(x)
            for k, gamma in enumerate(self.gammas):
                sums[k] += powers[k] * final_contribution
                prefixes[k].append(sums[k])
                powers[k] *= gamma

            if (
                    death_step is None
                    and channel in (F, W, I)
                    and x <= 0.0):
                death_step = step + 1

        self._sep_stats["trace_builds"] += 1
        self._sep_stats["channel_samples"] += STEPS
        self._sep_stats["memory_writes"] += TRACE_STORE_ITEMS
        return {
            "levels": tuple(levels),
            "prefixes": tuple(tuple(row) for row in prefixes),
            "death_step": death_step,
            "final_contribution": final_contribution,
        }

    def _trace(self, channel, body, drift, restore, schedule, budget):
        budget.spend(CognitiveWork(memory_items=TRACE_READ_ITEMS))
        self._sep_stats["memory_reads"] += TRACE_READ_ITEMS
        key = self._trace_key(channel, body, drift, restore)
        trace = self._sep_cache.get(key)
        if trace is None:
            trace = self._build_trace(
                channel, body, drift, restore, schedule, budget)
            self._sep_cache[key] = trace
            self._sep_stats["max_live_entries"] = max(
                self._sep_stats["max_live_entries"],
                len(self._sep_cache))
        else:
            self._sep_stats["trace_hits"] += 1
        return trace

    def project(self, body, drift, budget=None):
        if budget is None:
            raise ValueError("paid exact-cache projection requires CognitiveBudget")
        drift, restore = drift
        self._sep_stats["project_calls"] += 1
        budget.spend(CognitiveWork(cycles=1))
        schedule = self._restore_schedule(body, restore)
        traces = [
            self._trace(c, body, drift, restore, schedule, budget)
            for c in range(5)
        ]

        deaths = [
            traces[c]["death_step"] for c in (F, W, I)
            if traces[c]["death_step"] is not None
        ]
        death = min(deaths) if deaths else None
        end_step = death if death is not None else STEPS

        ret = []
        for k, gamma in enumerate(self.gammas):
            if death is not None:
                alive = death - 1
                before = (
                    sum(t["prefixes"][k][alive - 1] for t in traces)
                    if alive else 0.0)
                value = (
                    -before
                    + (gamma ** alive)
                    * (-self.d_max) / (1.0 - gamma))
            else:
                before = sum(t["prefixes"][k][-1] for t in traces)
                last = sum(t["final_contribution"] for t in traces)
                value = (
                    -before
                    + (gamma ** STEPS)
                    * (-last) / (1.0 - gamma))
            ret.append(value)

        final_body = [
            traces[c]["levels"][end_step - 1]
            for c in range(5)
        ]
        return ret, final_body


def make_mind(arm):
    mind = PaidSeparableCachedMind(midpoint(), 197, accounting_arm=arm)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    if mind.simulation_mode != "reference":
        raise RuntimeError("accounting probe must preserve reference simulation")
    if mind.projection_accounting != "chunk_end":
        raise RuntimeError("accounting probe must preserve reference mode label")
    return mind


def _cache_no_hit_projection_ceiling(arm):
    return CognitiveWork(
        cycles=1,
        simulated_steps=TRACES_PER_PROJECT * SIM_PER_TRACE[arm],
        memory_items=TRACES_PER_PROJECT * (
            TRACE_STORE_ITEMS + TRACE_READ_ITEMS),
    )


def _inner_common_ceiling(model, memory, horizon, arm):
    base = water_one_future_opportunity_work_ceiling(
        model, memory, G.EXPLORE, G.ORDINARY, horizon)
    quote = projection_simulated_steps_ceiling(model)
    if quote != REFERENCE_PROJECTION_QUOTE:
        raise RuntimeError("reference projection quote changed")
    cache = _cache_no_hit_projection_ceiling(arm)
    return CognitiveWork(
        cycles=base.cycles + COMPLETE_PROJECT_CALLS * cache.cycles,
        simulated_steps=(
            base.simulated_steps
            - COMPLETE_PROJECT_CALLS * quote
            + COMPLETE_PROJECT_CALLS * cache.simulated_steps
        ),
        memory_items=(
            base.memory_items
            + COMPLETE_PROJECT_CALLS * cache.memory_items
        ),
        replays=base.replays,
    )


def _total_common_ceiling(recurrence_work, model, memory, horizon, arm):
    return _add(
        recurrence_work,
        _inner_common_ceiling(model, memory, horizon, arm))


def _direct_exactness(arm):
    body = (80., 30., 30., 80., 80.)
    candidate = make_mind(arm)
    cbudget = CognitiveBudget((100.,) * 5, BodyLaws())
    cvalue, cbody = candidate.project(body, candidate._drift, cbudget)

    truth = D.make_mind("per_step")
    tvalue, tbody = truth.project(body, truth._drift)
    return {
        "max_value_error": max(
            abs(a - b) for a, b in zip(cvalue, tvalue)),
        "max_body_error": max(
            abs(a - b) for a, b in zip(cbody, tbody)),
    }


def evaluate_state(arm, body, horizon):
    model = make_mind(arm)
    memory = G.effect_memory()
    recurrence = G.recurrence_2_6_10()
    budget = CognitiveBudget(body, BodyLaws())
    start = budget.work

    try:
        recurrence_result = recurrence.estimate("water", horizon, budget)
        if recurrence_result["status"] == "NO_PERSONAL_RECURRENCE_SUPPORT":
            raise RuntimeError("frozen recurrence unexpectedly lacks support")
        p_future = recurrence_result[
            "future_matching_opportunity_probability"]
        recurrence_work = _delta(budget.work, start)
        ceiling = _total_common_ceiling(
            recurrence_work, model, memory, horizon, arm)

        # Fail the whole state before any information matrix work if the
        # complete no-hit common ceiling cannot be physically prepaid.
        try:
            from ..modules.body import debit_cognition
            debit_cognition(body, BodyLaws(), ceiling)
        except CognitiveFundingError:
            return {
                "status": "UNFUNDED_COMMON_CEILING",
                "body": body,
                "horizon": horizon,
                "common_ceiling": asdict(ceiling),
                "work": asdict(_delta(budget.work, start)),
                "cache": model.cache_stats(),
            }

        result = paid_water_one_future_opportunity_value(
            model, memory, G.EXPLORE, G.ORDINARY, horizon, budget,
            forecast_work=ceiling,
            future_opportunity_probability=p_future)
        total = _delta(budget.work, start)
        within = all(
            getattr(total, key) <= getattr(ceiling, key)
            for key in ("cycles", "simulated_steps", "memory_items", "replays"))
        if not within:
            raise RuntimeError("actual cache work exceeded common ceiling")

        energy, vigilance = cognitive_cost(BodyLaws(), total)
        return {
            "status": "COMPLETE",
            "body": body,
            "horizon": horizon,
            "future_probability": p_future,
            "information_value": result["trial_information_value"],
            "trial_advantage": result["trial_advantage"],
            "target_choices": list(result["target_node_best_choices"]),
            "work": asdict(total),
            "common_ceiling": asdict(ceiling),
            "bill": {"energy": energy, "vigilance": vigilance},
            "cache": model.cache_stats(),
            "actual_within_common_ceiling": within,
        }
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED_ACTUAL_WORK",
            "body": body,
            "horizon": horizon,
            "work": asdict(_delta(budget.work, start)),
            "cache": model.cache_stats(),
        }


def _mean(rows, path):
    vals = []
    for row in rows:
        value = row
        for key in path:
            value = value[key]
        vals.append(value)
    return sum(vals) / len(vals) if vals else None


def _max(rows, path):
    vals = []
    for row in rows:
        value = row
        for key in path:
            value = value[key]
        vals.append(value)
    return max(vals) if vals else None


def evaluate_arm(arm):
    rows = []
    for channel, channel_name in enumerate(G.CHANNEL_NAMES):
        for level in G.LEVELS:
            body = list(G.BASE_BODY)
            body[channel] = level
            body = tuple(body)
            for horizon in G.HORIZONS:
                row = evaluate_state(arm, body, horizon)
                row["channel"] = channel_name
                row["channel_index"] = channel
                row["level"] = level
                rows.append(row)

    complete = [r for r in rows if r["status"] == "COMPLETE"]
    unfunded = [r for r in rows if r["status"] != "COMPLETE"]
    selected = [
        r for r in complete
        if "TRIAL" in r["target_choices"]
        and r["information_value"] is not None
        and r["information_value"] > 1e-12
        and r["trial_advantage"] is not None
        and r["trial_advantage"] > 1e-12
    ]
    declined = [
        r for r in complete
        if r["target_choices"] == ["DECLINE_TRIAL"]
    ]

    work_keys = ("cycles", "simulated_steps", "memory_items", "replays")
    mean_work = {
        k: _mean(complete, ("work", k)) for k in work_keys}
    max_work = {
        k: _max(complete, ("work", k)) for k in work_keys}
    mean_ceiling = {
        k: _mean(rows, ("common_ceiling", k))
        for k in work_keys
        if all("common_ceiling" in r for r in rows)}
    max_ceiling = {
        k: _max(rows, ("common_ceiling", k))
        for k in work_keys
        if all("common_ceiling" in r for r in rows)}

    cache_totals = {
        key: sum(r["cache"][key] for r in rows)
        for key in (
            "project_calls", "trace_builds", "trace_hits",
            "channel_samples", "memory_writes", "memory_reads")
    }
    cache_totals["max_live_entries"] = max(
        r["cache"]["max_live_entries"] for r in rows)
    denom = cache_totals["trace_builds"] + cache_totals["trace_hits"]
    cache_totals["hit_fraction"] = (
        cache_totals["trace_hits"] / denom if denom else 0.0)

    mean_energy = _mean(complete, ("bill", "energy"))
    mean_vigilance = _mean(complete, ("bill", "vigilance"))
    relevance = len(selected) >= CANDIDATE_F_SELECTED
    cheaper = (
        len(complete) == 80
        and mean_energy is not None
        and mean_vigilance is not None
        and mean_energy <= CANDIDATE_F_MEAN_BILL["energy"]
        and mean_vigilance <= CANDIDATE_F_MEAN_BILL["vigilance"]
    )

    return rows, {
        "evaluated": len(rows),
        "complete": len(complete),
        "unfunded": len(unfunded),
        "unfunded_states": [
            {
                "channel": r["channel"],
                "level": r["level"],
                "horizon": r["horizon"],
                "status": r["status"],
            }
            for r in unfunded
        ],
        "selected_epistemic": len(selected),
        "selected_water_deficit": sum(
            r["channel_index"] == W for r in selected),
        "selected_other_deficit": sum(
            r["channel_index"] != W for r in selected),
        "declined": len(declined),
        "max_information_value": (
            max(r["information_value"] for r in complete)
            if complete else None),
        "best_trial_advantage": (
            max(r["trial_advantage"] for r in complete
                if r["trial_advantage"] is not None)
            if any(r["trial_advantage"] is not None for r in complete)
            else None),
        "worst_trial_advantage": (
            min(r["trial_advantage"] for r in complete
                if r["trial_advantage"] is not None)
            if any(r["trial_advantage"] is not None for r in complete)
            else None),
        "mean_work": mean_work,
        "max_work": max_work,
        "mean_common_ceiling": mean_ceiling,
        "max_common_ceiling": max_ceiling,
        "mean_bill": {
            "energy": mean_energy,
            "vigilance": mean_vigilance,
        },
        "max_bill": {
            "energy": _max(complete, ("bill", "energy")),
            "vigilance": _max(complete, ("bill", "vigilance")),
        },
        "cache": cache_totals,
        "actual_work_ceiling_violations": sum(
            not r.get("actual_within_common_ceiling", True)
            for r in complete),
        "decision_relevance_retained": relevance,
        "cheaper_than_candidate_f_mean_bill": cheaper,
    }


def run(out_path):
    exact = {arm: _direct_exactness(arm) for arm in ARMS}
    arms = {}
    rows = {}
    for arm in ARMS:
        arm_rows, summary = evaluate_arm(arm)
        rows[arm] = arm_rows
        arms[arm] = summary

    if arms["scalar1_upper"]["complete"] == 80:
        classification = "CACHE_ACCOUNTING_ROBUSTLY_FUNDED"
    elif arms["bundle5_lower"]["complete"] < 80:
        classification = "CACHE_ACCOUNTING_UNFUNDED_EVEN_LOWER_BOUND"
    else:
        classification = "CACHE_ACCOUNTING_SENSITIVE"

    conservative_runtime_authorized = (
        classification == "CACHE_ACCOUNTING_ROBUSTLY_FUNDED"
        and arms["scalar1_upper"]["decision_relevance_retained"]
        and arms["scalar1_upper"]["cheaper_than_candidate_f_mean_bill"]
        and exact["scalar1_upper"]["max_value_error"] <= 1e-10
        and exact["scalar1_upper"]["max_body_error"] <= 1e-10
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_SEPARABLE_CACHE_ACCOUNTING.md",
        "world_access": False,
        "lives": 0,
        "arms": arms,
        "rows": rows,
        "direct_exactness": exact,
        "frozen_baselines": {
            "reference": {
                "selected_epistemic": 1,
                "mean_work": {
                    "cycles": 18, "simulated_steps": 53,
                    "memory_items": 201, "replays": 0},
                "mean_bill": {"energy": 0.5062, "vigilance": 1.006},
            },
            "candidate_f": {
                "selected_epistemic": 24,
                "mean_work": {
                    "cycles": 18, "simulated_steps": 470,
                    "memory_items": 201, "replays": 0},
                "mean_bill": dict(CANDIDATE_F_MEAN_BILL),
            },
            "per_step": {
                "selected_epistemic": 32,
                "mean_work": {
                    "cycles": 18, "simulated_steps": 1288,
                    "memory_items": 201, "replays": 0},
                "mean_bill": {"energy": 2.9762, "vigilance": 3.476},
            },
        },
        "accounting": {
            "trace_store_items": TRACE_STORE_ITEMS,
            "trace_read_items": TRACE_READ_ITEMS,
            "trace_key_items": TRACE_KEY_ITEMS,
            "simulated_steps_per_trace": dict(SIM_PER_TRACE),
            "complete_project_calls_ceiling": COMPLETE_PROJECT_CALLS,
            "traces_per_project": TRACES_PER_PROJECT,
            "forecast_assumes_cache_hits": False,
        },
        "classification": classification,
        "conservative_runtime_candidate_authorized":
            conservative_runtime_authorized,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print(json.dumps({
        "classification": rep["classification"],
        "conservative_runtime_candidate_authorized":
            rep["conservative_runtime_candidate_authorized"],
        "direct_exactness": rep["direct_exactness"],
        "arms": rep["arms"],
    }, indent=1, sort_keys=True))
