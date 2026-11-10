"""Stage-2.1 synthetic-only host-operation coverage and equal-compute control.

Never opens a World. Audits the historical *unchanged* compact paid
engineering path and demonstrates why equal CognitiveWork != equal host CPU.
The new balanced readout helper is for future prospectively designed
ENGINEERING work only, NOT retroactive changes to completed sources.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite
from time import perf_counter_ns
import tracemalloc
from unittest.mock import patch

from ..modules.body import BodyLaws, CognitiveBudget, cognitive_cost
from ..modules import stage2_replay_content_selection as selection
from .stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, work_envelope)
from .stage2_compact_shadow_cost_audit import BODY, SIZES, EXTRA_STATES, fixture
from .stage2_compact_paid_first_person_engineering import (
    MODES, _source_seal)
from .stage2_repeated_paid_distress_prequential_engineering import (
    RepeatedPaidWitness)

SCHEMA = "i3-stage2.1-compact-host-operation-coverage-engineering/v1"
SEED = 980041
K = 3


def balanced_refit_forecast(*, head, memory, indices, body, mode):
    """Same inference and replay count across TD, HMAC and paid-discard.

    Always compute the post-training forecast, including the paid-discard
    arm, where its value is intentionally NOT used. No World, action
    authority or future outcome is available to this helper.
    """
    if mode not in MODES:
        raise ValueError("original three forecast control modes required")
    if type(head) is not CompactPersonalDistressHead:
        raise TypeError("separately detached, compact personal head required")
    if head.training_updates:
        raise ValueError("only fresh personal snapshot refits allowed")
    pre = head.predict(body)
    head.apply(memory, indices)
    post = head.predict(body)  # deliberately executed even for discard
    selected = pre if mode == "discard" else post
    if any(not isfinite(v) for v in (pre, post, selected)):
        raise RuntimeError("nonfinite personal forecast")
    return {
        "forecast": selected,
        "pretraining_forecast": pre,
        "posttraining_forecast_computed": True,
        "updates": head.training_updates,
    }


def _selected(memory, seed, ordinal):
    n = len(memory)
    priority_calls = 0

    def priority_key(i):
        nonlocal priority_calls
        priority_calls += 1
        return -memory[i][0]

    priority = tuple(sorted(range(n), key=priority_key)[:K])
    hmac_calls = 0
    message_bytes = 0
    actual_hmac_new = selection.hmac.new

    def hmac_spy(key, message, digestmod):
        nonlocal hmac_calls, message_bytes
        hmac_calls += 1
        message_bytes += len(message)
        return actual_hmac_new(key, message, digestmod)

    with patch.object(selection.hmac, "new", hmac_spy):
        random = selection.random_content_indices(
            eligible=n, count=K, life_seed=seed, sleep_ordinal=ordinal)
    # The unpatched helper must return exactly the same genuine HMAC ranking.
    if random != selection.random_content_indices(
            eligible=n, count=K, life_seed=seed, sleep_ordinal=ordinal):
        raise RuntimeError("HMAC spy perturbed authentic memory identity")
    if priority_calls != n or hmac_calls != n:
        raise RuntimeError("selector scan coverage differs from actual n memories")
    return {
        "priority_indices": priority,
        "random_indices": random,
        "priority_key_visits": priority_calls,
        "hmac_identity_messages": hmac_calls,
        "hmac_message_payload_bytes": message_bytes,
        "hmac_digest_output_bytes": 32 * hmac_calls,
    }


def _legacy_paid_admission(source, mode):
    """Observe actual historical first-person precharge path, NO World step."""
    old_seal = _source_seal(source)
    budget = CognitiveBudget(BODY, BodyLaws())
    observer = RepeatedPaidWitness(mode=mode, seed=SEED)
    original_predict = CompactPersonalDistressHead.predict
    calls = 0

    def spy(head, body):
        nonlocal calls
        calls += 1
        return original_predict(head, body)

    with patch.object(CompactPersonalDistressHead, "predict", spy):
        observer.after_choice(source, {"body": BODY},
                              budget, "attendre", None, budget.work)
    if (_source_seal(source) != old_seal or observer.pending is None
            or observer.slots[0]["status"] != "PAID_FROZEN_AWAITING_OUTCOME"):
        raise RuntimeError("historical computational spy was not pure or funded")
    event = observer.slots[0]
    ticket = work_envelope(len(source.buffer), K)
    if budget.work != ticket:
        raise RuntimeError("original native allowance price changed")
    return {
        "predict_calls": calls,
        "actually_executed_updates": observer._head.training_updates,
        "native_model_work": asdict(budget.work),
        "native_model_energy_authorized": event["energy_paid"],
        "native_model_vigilance_authorized": event["vigilance_paid"],
        "actual_frozen_forecast": observer.pending[0]["forecast"],
        "learned_weights": list(observer._head.weights),
    }


def _balanced_software_refit(source, mode, selectors):
    original = _source_seal(source)
    memory = tuple(source.buffer)
    old_predict = CompactPersonalDistressHead.predict
    calls = 0

    def spy(head, body):
        nonlocal calls
        calls += 1
        return old_predict(head, body)

    with patch.object(CompactPersonalDistressHead, "predict", spy):
        head = CompactPersonalDistressHead(source)
        indices = (selectors["priority_indices"] if mode == "priority"
                   else selectors["random_indices"])
        result = balanced_refit_forecast(
            head=head, memory=memory, indices=indices, body=BODY,
            mode=mode)
    if _source_seal(source) != original:
        raise RuntimeError("balanced forecast modified live source")
    return {
        "predict_calls": calls,
        "actually_executed_updates": head.training_updates,
        "forecast": result["forecast"],
        "learned_weights": list(head.weights),
        "posttraining_inference_always_executed":
            result["posttraining_forecast_computed"],
    }


def _provenance_host_measure(source):
    """ONLY laboratory integrity hash, purposely not part of i3's bill."""
    tracemalloc.start()
    try:
        t0 = perf_counter_ns()
        receipt = _source_seal(source)
        elapsed = perf_counter_ns() - t0
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if len(receipt) != 64:
        raise RuntimeError("laboratory source digest malformed")
    return {"host_elapsed_ns": elapsed, "peak_traced_bytes": peak}


def audit():
    rows = []
    for n in SIZES:
        for unrelated in EXTRA_STATES:
            source = fixture(n, unrelated)
            selectors = _selected(tuple(source.buffer), SEED, 1)
            old = {mode: _legacy_paid_admission(source, mode)
                   for mode in MODES}
            balanced = {
                mode: _balanced_software_refit(source, mode, selectors)
                for mode in MODES}
            bill = work_envelope(n, K)
            energy, vigilance = cognitive_cost(BodyLaws(), bill)
            if any(old[mode]["native_model_work"] != asdict(bill)
                   for mode in MODES):
                raise RuntimeError("prior equal native work ticket changed")
            if any(old[mode]["actual_frozen_forecast"]
                   != balanced[mode]["forecast"]
                   or old[mode]["learned_weights"]
                   != balanced[mode]["learned_weights"]
                   for mode in MODES):
                raise RuntimeError("balanced proposed control changed original forecast")
            if any(x["predict_calls"] != K + 2 for x in balanced.values()):
                raise RuntimeError("proposed computational balancing failed")
            if ([old[m]["predict_calls"] for m in MODES]
                    != [K + 2, K + 2, K + 1]):
                raise RuntimeError("historical computed-readout disparity falsified")
            rows.append({
                "personal_memory_records": n,
                "unrelated_map_effect_entries": unrelated,
                "native_price": asdict(bill),
                "native_model_energy_authorized": energy,
                "native_model_vigilance_authorized": vigilance,
                "selector_coverage": {
                    "priority_key_visits": selectors["priority_key_visits"],
                    "hmac_identity_messages": selectors["hmac_identity_messages"],
                    "hmac_message_payload_bytes":
                        selectors["hmac_message_payload_bytes"],
                    "hmac_digest_output_bytes":
                        selectors["hmac_digest_output_bytes"],
                },
                "historical_predict_calls": {
                    mode: old[mode]["predict_calls"] for mode in MODES},
                "balanced_predict_calls": {
                    mode: balanced[mode]["predict_calls"] for mode in MODES},
                "all_three_training_updates": {
                    mode: old[mode]["actually_executed_updates"]
                    for mode in MODES},
                "balanced_forecasts_exact_original": True,
                "external_only_provenance_host_measure":
                    _provenance_host_measure(source),
            })
    return {
        "schema": SCHEMA,
        "status": "HISTORICAL_PAID_HOST_WORK_DISPARITY_CONFIRMED",
        "synthetic_fixture_cells": len(rows),
        "historical_discard_inference_shortfall_per_event": 1,
        "native_model_price_equal_but_host_readout_counts_unequal": True,
        "proposed_balanced_forecast_and_weights_exact": True,
        "proposed_balanced_inference_call_counts_equal": True,
        "hmac_identity_messages_equal_eligible_memory_count": True,
        "unmapped_host_operation_coverage_includes":
            ("hmac_sha256", "priority_and_random_ordering",
             "source_snapshot_allocations",
             "laboratory_provenance_and_sha_receipts"),
        "native_model_tariff_is_full_host_cpu_calibration": False,
        "no_historical_originals_rewritten": True,
        "worlds_opened": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_activation": False,
        "rows": rows,
    }


if __name__ == "__main__":
    print("I3_COMPACT_HOST_OPERATION_COVERAGE_RESULT="+json.dumps(
        audit(), sort_keys=True))
