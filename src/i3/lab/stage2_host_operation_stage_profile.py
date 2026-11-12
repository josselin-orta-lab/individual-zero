"""No-World, stage-specific host-operation profiler for issue #1283.

Prospectively scoped in STAGE2_HOST_OPERATION_STAGE_PROFILE_PREFLIGHT_2026-11-12.
Times and traced allocations are volatile host diagnostics, never an organism
energy price. Native CognitiveBudget preauthorizes every optional operation,
but no World.step debit or born life is executed.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from statistics import median
from time import perf_counter_ns
import tracemalloc
from unittest.mock import patch

from ..modules import stage2_replay_content_selection as selection
from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from .stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, preauthorize, work_envelope)
from .stage2_compact_host_operator_coverage import balanced_refit_forecast
from .stage2_compact_paid_first_person_engineering import MODES, _source_seal
from .stage2_compact_shadow_cost_audit import BODY, SIZES, EXTRA_STATES, fixture

SCHEMA = "i3-stage2-host-operation-stage-profile-engineering/v1"
K = 3
SEED = 980041
REPEATS = 2
ACTION = "attendre"
STAGES = ("personal_head_copy", "memory_snapshot", "both_real_selectors",
          "three_updates_two_outer_predictions")


def _sha(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _measure(operator):
    """Isolate each synchronous stage's host clock and Python allocations."""
    tracemalloc.start()
    try:
        started = perf_counter_ns()
        answer = operator()
        elapsed = perf_counter_ns() - started
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if elapsed < 0 or peak < 0:
        raise RuntimeError("invalid host diagnostic counter")
    return answer, {"elapsed_ns": elapsed, "peak_traced_bytes": peak}


def _both_selectors(memory):
    n = len(memory)
    calls = 0
    hmac_calls = 0
    payload_bytes = 0

    def priority_key(i):
        nonlocal calls
        calls += 1
        return -memory[i][0]

    priority = tuple(sorted(range(n), key=priority_key)[:K])
    real_hmac_new = selection.hmac.new

    def spy_hmac(key, message, digestmod):
        nonlocal hmac_calls, payload_bytes
        hmac_calls += 1
        payload_bytes += len(message)
        return real_hmac_new(key, message, digestmod)

    with patch.object(selection.hmac, "new", spy_hmac):
        random = selection.random_content_indices(
            eligible=n, count=K, life_seed=SEED, sleep_ordinal=1)
    if calls != n or hmac_calls != n:
        raise RuntimeError("actual selector work did not cover each memory")
    return {
        "priority": priority, "random": random,
        "priority_key_visits": calls, "hmac_identity_messages": hmac_calls,
        "hmac_payload_bytes": payload_bytes,
    }


def profile_once(n, extras, mode, *, body=BODY):
    """One engineering trial; insufficient model funding fails before work."""
    if n not in SIZES or type(n) is not int:
        raise ValueError("memory count outside frozen grid")
    if extras not in EXTRA_STATES or type(extras) is not int:
        raise ValueError("unrelated-state count outside frozen grid")
    if type(mode) is not str or mode not in MODES:
        raise ValueError("unknown frozen control mode")
    # Fixture creation is laboratory setup, not an optional cognitive head.
    source = fixture(n, extras)
    budget = CognitiveBudget(body, BodyLaws())
    prior = budget.work
    if not preauthorize(budget, n=n, k=K, action=ACTION):
        if budget.work != prior or budget.work != CognitiveWork():
            raise RuntimeError("denied model admission leaked a charge")
        return {
            "status": "REFUSED_NOT_EXECUTED", "mode": mode, "memories": n,
            "unrelated_entries": extras, "native_model_work": asdict(budget.work),
            "optional_host_stages_executed": 0, "worlds": 0, "lives": 0,
        }

    expected = work_envelope(n, K)
    if budget.work != expected:
        raise RuntimeError("native modeled ticket changed")
    source_before = _source_seal(source)  # unpriced laboratory custody ONLY
    head, head_diag = _measure(lambda: CompactPersonalDistressHead(source))
    memory, snapshot_diag = _measure(lambda: tuple(source.buffer))
    selectors, selector_diag = _measure(lambda: _both_selectors(memory))
    if tuple(head._eligible_records) != memory:
        raise RuntimeError("snapshot and personal copied data differ")
    indices = (selectors["priority"] if mode == "priority"
               else selectors["random"])
    predict_calls = 0
    actual_predict = CompactPersonalDistressHead.predict

    def spy_predict(instance, before_body):
        nonlocal predict_calls
        predict_calls += 1
        return actual_predict(instance, before_body)

    with patch.object(CompactPersonalDistressHead, "predict", spy_predict):
        result, readout_diag = _measure(
            lambda: balanced_refit_forecast(
                head=head, memory=memory, indices=indices,
                body=body, mode=mode))
    if (predict_calls != K + 2 or head.training_updates != K
            or result["updates"] != K
            or not result["posttraining_forecast_computed"]):
        raise RuntimeError("unequal actual inference/training work")
    if _source_seal(source) != source_before:
        raise RuntimeError("optional head mutated personal source or RNG")
    energy, vigilance = cognitive_cost(budget.laws, budget.work)
    return {
        "status": "MODEL_AUTHORIZED_HOST_OPERATORS_EXECUTED",
        "mode": mode, "memories": n, "unrelated_entries": extras,
        "native_model_work": asdict(budget.work),
        "native_model_energy": energy, "native_model_vigilance": vigilance,
        "counts": {
            "head_records_copied": len(head._eligible_records),
            "snapshot_items_read": len(memory),
            "priority_key_visits": selectors["priority_key_visits"],
            "hmac_identity_messages": selectors["hmac_identity_messages"],
            "hmac_payload_bytes": selectors["hmac_payload_bytes"],
            "learning_updates": head.training_updates,
            "forecast_calls": predict_calls,
        },
        "selector_indices": {
            "priority": list(selectors["priority"]),
            "random": list(selectors["random"]),
            "used": list(indices),
        },
        "pretraining_forecast": result["pretraining_forecast"],
        "selected_forecast": result["forecast"],
        "trained_weights": list(head.weights),
        "stage_diagnostics": {
            "personal_head_copy": head_diag,
            "memory_snapshot": snapshot_diag,
            "both_real_selectors": selector_diag,
            "three_updates_two_outer_predictions": readout_diag,
        },
        "optional_host_stages_executed": len(STAGES),
        "source_and_rng_unchanged": True,
        "native_World_debit_occurred": False,
        "worlds": 0, "lives": 0,
    }


def audit():
    rows = []
    canonical = []
    for n in SIZES:
        for extras in EXTRA_STATES:
            arms = {}
            for mode in MODES:
                trials = [profile_once(n, extras, mode)
                          for _ in range(REPEATS)]
                a = [{k: v for k, v in trial.items()
                      if k != "stage_diagnostics"} for trial in trials]
                if a[0] != a[1]:
                    raise RuntimeError("nondeterministic structural host work")
                if any(t["status"] !=
                       "MODEL_AUTHORIZED_HOST_OPERATORS_EXECUTED" for t in trials):
                    raise RuntimeError("fixed funding fixture unexpectedly denied")
                merged = dict(a[0])
                merged["stage_diagnostics"] = {
                    stage: {
                        "median_elapsed_ns": int(median(
                            t["stage_diagnostics"][stage]["elapsed_ns"]
                            for t in trials)),
                        "median_peak_traced_bytes": int(median(
                            t["stage_diagnostics"][stage]["peak_traced_bytes"]
                            for t in trials)),
                    } for stage in STAGES
                }
                arms[mode] = merged
                canonical.append(a[0])
                rows.append(merged)
            for mode in MODES:
                a = arms[mode]
                if (a["counts"] != arms["priority"]["counts"]
                        or a["native_model_work"] != arms["priority"]["native_model_work"]
                        or a["selector_indices"]["priority"] !=
                           arms["priority"]["selector_indices"]["priority"]
                        or a["selector_indices"]["random"] !=
                           arms["priority"]["selector_indices"]["random"]):
                    raise RuntimeError("operator or work parity defect")
            if (arms["discard"]["trained_weights"] !=
                    arms["random"]["trained_weights"]
                    or arms["discard"]["selected_forecast"] !=
                    arms["random"]["pretraining_forecast"]):
                raise RuntimeError("discard is not a fully computed random control")

    no_energy = profile_once(6, 0, "priority",
                             body=(0.2, 60., 50., 90., 80.))
    no_vigilance = profile_once(6, 0, "random",
                                body=(70., 60., 50., 90., 0.1))
    if any(x["status"] != "REFUSED_NOT_EXECUTED"
           or x["optional_host_stages_executed"] != 0
           for x in (no_energy, no_vigilance)):
        raise RuntimeError("negative funding controls failed")
    return {
        "schema": SCHEMA,
        "status": "STAGE_PROFILE_PARITY_PASS",
        "source_kind": "SYNTHETIC_MIND_FIXTURES_ONLY",
        "predeclared_cells": len(SIZES) * len(EXTRA_STATES),
        "modeled_arms": list(MODES),
        "repeats_per_arm": REPEATS,
        "stage_names": list(STAGES),
        "fixed_denied_funding_controls": [no_energy, no_vigilance],
        "deterministic_structural_sha256": _sha(canonical),
        "stage_metrics_are_host_diagnostics_not_physical_currency": True,
        "host_cpu_joules_calibrated": False,
        "native_World_debits_observed": 0,
        "worlds_opened": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "rows": rows,
    }


if __name__ == "__main__":
    print("I3_HOST_OPERATION_STAGE_PROFILE="+json.dumps(audit(), sort_keys=True))
