"""Frozen characterization of the exact separable decision-local cache.

Protocol: docs/STAGE1_SEPARABLE_PROJECTION_CACHE.md.
Software only: no World, life, study index, runtime projection mode or adoption.

The cache changes no projected state law. It only factorizes the 255-step
per-step diagnostic projection into channel traces and reuses an exact trace
when the represented inputs match inside one option batch.
"""
from __future__ import annotations

from itertools import combinations
import json
import math
import sys

from ..modules.body import BodyLaws, CognitiveBudget, E, F, W, I, V
from ..modules.genome import midpoint
from ..modules.mind import Mind
from . import projection_consistency_characterization as P
from . import stage1_affordable_projection_probes as A

SCHEMA = "i3-stage1-separable-projection-cache/v1"
STEPS = 255
BIAS_LIMIT = 1e-3
INVARIANT_LIMIT = 1e-3
BODY_LIMIT = 1e-10


def _clamp(x):
    return 0.0 if x < 0.0 else 100.0 if x > 100.0 else x


class SeparableCachedMind(Mind):
    """Lab-only exact channel factorization of the per-step projection."""

    def __init__(self, genome, life_seed, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        self._sep_cache = {}
        self._sep_stats = {
            "project_calls": 0,
            "channel_trace_builds": 0,
            "channel_trace_hits": 0,
            "channel_samples": 0,
            "scalar_cache_writes": 0,
            "scalar_cache_reads": 0,
            "max_live_cache_entries": 0,
        }

    def cache_stats(self):
        out = dict(self._sep_stats)
        out["uncached_per_step_full_endpoints"] = (
            out["project_calls"] * STEPS)
        out["lower_bound_equivalent_full_endpoints_not_a_bill"] = (
            math.ceil(out["channel_samples"] / 5.0))
        return out

    def _restore_schedule(self, b, restore):
        if restore is None:
            return (0.0,) * STEPS
        e, v = float(b[E]), float(b[V])
        out = []
        for _ in range(STEPS):
            need_e = max(0.0, self.theta[E] - e) / restore[0]
            need_v = (
                max(0.0, self.theta[V] - v) / restore[1]
                if restore[1] > 0.0 else 0.0)
            n = min(1.0, max(need_e, need_v))
            e = _clamp(e + n * restore[0])
            v = _clamp(v + n * restore[1])
            out.append(n)
        return tuple(out)

    def _trace_key(self, channel, b, drift, restore):
        if restore is None:
            schedule_key = None
        else:
            schedule_key = (
                float(b[E]), float(b[V]),
                float(restore[0]), float(restore[1]), float(restore[2]),
                float(self.theta[E]), float(self.theta[V]),
            )
        if channel in (E, F, V):
            return (
                channel, float(b[channel]), float(drift[channel]),
                schedule_key, float(self.theta[channel]),
                float(self.p[channel]), float(self.w[channel]),
            )
        return (
            channel, float(b[channel]), float(drift[channel]),
            float(self.theta[channel]), float(self.p[channel]),
            float(self.w[channel]),
        )

    def _build_trace(self, channel, b, drift, restore, schedule):
        x = float(b[channel])
        levels = []
        contributions = []
        prefixes = [[], [], []]
        sums = [0.0, 0.0, 0.0]
        powers = [1.0, 1.0, 1.0]
        death = None

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
            contribution = (
                self.w[channel] * (z ** self.p[channel])
                if z > 0.0 else 0.0)

            levels.append(x)
            contributions.append(contribution)
            for k, gamma in enumerate(self.gammas):
                sums[k] += powers[k] * contribution
                prefixes[k].append(sums[k])
                powers[k] *= gamma

            if (
                    death is None
                    and channel in (F, W, I)
                    and x <= 0.0):
                death = step + 1

        self._sep_stats["channel_trace_builds"] += 1
        self._sep_stats["channel_samples"] += STEPS
        # endpoint + contribution + three discounted prefixes per step
        self._sep_stats["scalar_cache_writes"] += 5 * STEPS
        return {
            "levels": tuple(levels),
            "contributions": tuple(contributions),
            "prefixes": tuple(tuple(x) for x in prefixes),
            "death_step": death,
        }

    def _trace(self, channel, b, drift, restore, schedule):
        key = self._trace_key(channel, b, drift, restore)
        trace = self._sep_cache.get(key)
        if trace is None:
            trace = self._build_trace(
                channel, b, drift, restore, schedule)
            self._sep_cache[key] = trace
            self._sep_stats["max_live_cache_entries"] = max(
                self._sep_stats["max_live_cache_entries"],
                len(self._sep_cache))
        else:
            self._sep_stats["channel_trace_hits"] += 1
        # level + contribution + three prefix values for the query boundary
        self._sep_stats["scalar_cache_reads"] += 5
        return trace

    def project(self, b, drift, budget=None):
        """Exact per-step semantics assembled from decision-local channel traces.

        No candidate CognitiveWork price is charged in this structural slice.
        Explicit plan simulation remains ordinarily funded by Mind.simulate.
        """
        drift, restore = drift
        self._sep_stats["project_calls"] += 1
        schedule = self._restore_schedule(b, restore)
        traces = [
            self._trace(c, b, drift, restore, schedule)
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
                last = sum(t["contributions"][-1] for t in traces)
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


def make_mind(genome, life_seed=97, *, sleep_learned=True,
              projection_equivalent=False):
    mind = SeparableCachedMind(genome, life_seed)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    if projection_equivalent:
        mind.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    else:
        mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    if sleep_learned:
        mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def _candidate_values(genome, body, **fixture):
    mind = make_mind(genome, **fixture)
    out = {}
    for name, plan in P.PLANS.items():
        out[name] = mind.simulate(
            body, plan, P.HORIZON,
            CognitiveBudget(body, BodyLaws()))[0]
    return out, mind.cache_stats()


def _truth_values(genome, body, **fixture):
    return P.values(genome, body, "per_step", **fixture)


def _pairwise_bias(candidate, truth):
    worst = 0.0
    pair = None
    for a, b in combinations(candidate, 2):
        err = abs(
            (candidate[a] - candidate[b])
            - (truth[a] - truth[b]))
        if err > worst:
            worst, pair = err, (a, b)
    return worst, pair


def _direct_body_error(genome, body, **fixture):
    candidate = make_mind(genome, **fixture)
    truth = P.configure(
        P.make_mind(genome, **fixture), "per_step")
    cb = candidate.project(body, candidate._drift)[1]
    tb = truth.project(body, truth._drift)[1]
    errs = [abs(a - b) for a, b in zip(cb, tb)]
    return max(errs), errs.index(max(errs)), cb, tb


def _merge_work(total, stats):
    for key in (
            "project_calls", "channel_trace_builds", "channel_trace_hits",
            "channel_samples", "scalar_cache_writes",
            "scalar_cache_reads"):
        total[key] += stats[key]
    total["max_live_cache_entries"] = max(
        total["max_live_cache_entries"],
        stats["max_live_cache_entries"])


def _new_work():
    return {
        "project_calls": 0,
        "channel_trace_builds": 0,
        "channel_trace_hits": 0,
        "channel_samples": 0,
        "scalar_cache_writes": 0,
        "scalar_cache_reads": 0,
        "max_live_cache_entries": 0,
    }


def characterize_projection_grid():
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    max_value_error = 0.0
    max_bias = 0.0
    max_body_error = 0.0
    invariant = 0.0
    worst_value = None
    worst_bias = None
    worst_body = None
    work = _new_work()
    cases = 0

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                candidate, stats = _candidate_values(
                    genome, body, **fixture)
                truth = _truth_values(genome, body, **fixture)
                _merge_work(work, stats)

                for name in candidate:
                    err = abs(candidate[name] - truth[name])
                    if err > max_value_error:
                        max_value_error = err
                        worst_value = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "option": name,
                            "candidate": candidate[name],
                            "truth": truth[name],
                            "abs_error": err,
                        }

                bias, pair = _pairwise_bias(candidate, truth)
                if bias > max_bias:
                    max_bias = bias
                    worst_bias = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "pair": list(pair) if pair else None,
                        "abs_bias": bias,
                    }

                if fixture_name == "projection_equivalent":
                    prefix = candidate["prefix"]
                    invariant = max(
                        invariant,
                        abs(candidate["plus_1_wait"] - prefix),
                        abs(candidate["plus_3_waits"] - prefix))

                body_error, channel, cb, tb = _direct_body_error(
                    genome, body, **fixture)
                if body_error > max_body_error:
                    max_body_error = body_error
                    worst_body = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": channel,
                        "candidate_final_body": list(cb),
                        "truth_final_body": list(tb),
                        "abs_error": body_error,
                    }

    work["uncached_per_step_full_endpoints"] = (
        work["project_calls"] * STEPS)
    work["lower_bound_equivalent_full_endpoints_not_a_bill"] = (
        math.ceil(work["channel_samples"] / 5.0))
    return {
        "cases": cases,
        "max_abs_option_value_error": max_value_error,
        "max_pairwise_decision_bias": max_bias,
        "projection_equivalent_invariant_max_gap": invariant,
        "max_final_body_channel_error": max_body_error,
        "worst": {
            "option_value": worst_value,
            "decision_bias": worst_bias,
            "final_body": worst_body,
        },
        "work": work,
    }


def _apply_plan(body, plan):
    b = list(body)
    for delta in plan:
        for c in range(5):
            b[c] = _clamp(b[c] + delta[c])
    return tuple(b)


def _probe_values(mind, body):
    return {
        name: A.plan_value(
            mind, body, plan,
            lambda b, _length: mind.project(
                b, mind._drift)[0])
        for name, plan in A.PLANS.items()
    }


def characterize_nonlinear_set():
    max_value_error = 0.0
    max_bias = 0.0
    max_body_error = 0.0
    worst_value = None
    worst_bias = None
    worst_body = None
    work = _new_work()

    for body in A.BODIES:
        candidate_mind = make_mind(
            midpoint(), 197, sleep_learned=True)
        candidate = _probe_values(candidate_mind, body)
        _merge_work(work, candidate_mind.cache_stats())

        truth = {}
        for name, plan in A.PLANS.items():
            truth_mind = P.configure(
                P.make_mind(midpoint()), "per_step")
            truth[name] = A.plan_value(
                truth_mind, body, plan,
                lambda b, _length, m=truth_mind:
                    m.project(b, m._drift)[0])

        for name in candidate:
            err = abs(candidate[name] - truth[name])
            if err > max_value_error:
                max_value_error = err
                worst_value = {
                    "body": list(body),
                    "option": name,
                    "candidate": candidate[name],
                    "truth": truth[name],
                    "abs_error": err,
                }

        bias, pair = _pairwise_bias(candidate, truth)
        if bias > max_bias:
            max_bias = bias
            worst_bias = {
                "body": list(body),
                "pair": list(pair) if pair else None,
                "abs_bias": bias,
            }

        for name, plan in A.PLANS.items():
            end = _apply_plan(body, plan)
            cm = make_mind(midpoint(), 197)
            tm = P.configure(P.make_mind(midpoint()), "per_step")
            cb = cm.project(end, cm._drift)[1]
            tb = tm.project(end, tm._drift)[1]
            errs = [abs(a - b) for a, b in zip(cb, tb)]
            err = max(errs)
            if err > max_body_error:
                max_body_error = err
                worst_body = {
                    "body": list(body),
                    "option": name,
                    "project_start": list(end),
                    "channel": errs.index(err),
                    "candidate_final_body": list(cb),
                    "truth_final_body": list(tb),
                    "abs_error": err,
                }

    work["uncached_per_step_full_endpoints"] = (
        work["project_calls"] * STEPS)
    work["lower_bound_equivalent_full_endpoints_not_a_bill"] = (
        math.ceil(work["channel_samples"] / 5.0))
    return {
        "bodies": len(A.BODIES),
        "plans_per_body": len(A.PLANS),
        "max_abs_option_value_error": max_value_error,
        "max_pairwise_decision_bias": max_bias,
        "max_final_body_channel_error": max_body_error,
        "worst": {
            "option_value": worst_value,
            "decision_bias": worst_bias,
            "final_body": worst_body,
        },
        "work": work,
    }


def run(out_path):
    a = characterize_projection_grid()
    b = characterize_nonlinear_set()

    max_bias = max(
        a["max_pairwise_decision_bias"],
        b["max_pairwise_decision_bias"])
    max_body = max(
        a["max_final_body_channel_error"],
        b["max_final_body_channel_error"])
    hit_a = a["work"]["channel_trace_hits"] > 0
    hit_b = b["work"]["channel_trace_hits"] > 0
    reuse_a = (
        a["work"]["channel_samples"]
        < 5 * a["work"]["uncached_per_step_full_endpoints"])
    reuse_b = (
        b["work"]["channel_samples"]
        < 5 * b["work"]["uncached_per_step_full_endpoints"])

    rules = {
        "R0_decision_bias_le_1e_3": max_bias <= BIAS_LIMIT,
        "R1_projection_equivalent_gap_le_1e_3":
            a["projection_equivalent_invariant_max_gap"]
            <= INVARIANT_LIMIT,
        "R2_final_body_error_le_1e_10": max_body <= BODY_LIMIT,
        "R3_cache_hit_in_projection_grid": hit_a,
        "R4_cache_hit_in_nonlinear_set": hit_b,
        "R5_actual_trace_reuse_projection_grid": reuse_a,
        "R6_actual_trace_reuse_nonlinear_set": reuse_b,
    }
    passed = all(rules.values())

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_SEPARABLE_PROJECTION_CACHE.md",
        "world_access": False,
        "lives": 0,
        "candidate": "separable_exact_cache_v1",
        "truth": "reference_float_per_step_chunk_end",
        "projection_grid": a,
        "nonlinear_option_set": b,
        "limits": {
            "decision_bias": BIAS_LIMIT,
            "projection_equivalent_invariant": INVARIANT_LIMIT,
            "final_body": BODY_LIMIT,
        },
        "rules": rules,
        "verdict": (
            "SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_PASS"
            if passed else
            "SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_FAIL"),
        "physical_affordability_claim_authorized": False,
        "runtime_integration_authorized": False,
        "next_paid_accounting_slice_authorized": passed,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print(json.dumps({
        "verdict": rep["verdict"],
        "rules": rep["rules"],
        "projection_grid": {
            k: rep["projection_grid"][k]
            for k in (
                "max_abs_option_value_error",
                "max_pairwise_decision_bias",
                "projection_equivalent_invariant_max_gap",
                "max_final_body_channel_error",
                "work")
        },
        "nonlinear_option_set": {
            k: rep["nonlinear_option_set"][k]
            for k in (
                "max_abs_option_value_error",
                "max_pairwise_decision_bias",
                "max_final_body_channel_error",
                "work")
        },
    }, indent=1, sort_keys=True))
