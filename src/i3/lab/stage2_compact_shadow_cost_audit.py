"""Read-only host workload and categorical price for a compact I3 shadow.

Synthetic Mind fixtures ONLY; timing/allocations are host diagnostics, not
evolutionary evidence and NOT joules. No World/life/real cognition debit.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from math import isfinite
import json
from statistics import median
from time import perf_counter_ns
import tracemalloc

from ..modules.body import BodyLaws, cognitive_cost
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.stage2_replay_content_selection import random_content_indices
from .stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, work_envelope)
from .stage2_personal_distress_forecast_shadow import PersonalDistressHead
from . import stage2_replay_predictive_negative_control as NEG

SCHEMA = "i3-stage2.1-compact-distress-operator-cost-audit/v1"
SIZES = (6, 12, 32, 128, 512)
EXTRA_STATES = (0, 256)
REPEATS = 3
MAX_MEMORY_CAPACITY = 512
BODY = (70., 60., 50., 90., 80.)


def fixture(n: int, extras: int):
    if n not in SIZES or extras not in EXTRA_STATES:
        raise ValueError("only declared structural audit fixtures")
    genome = midpoint()
    genome["genes"]["m_max"] = float(MAX_MEMORY_CAPACITY)
    source = Mind(genome, 8780 + n)
    # A deterministic first-person-format history with valid bodily bounds.
    source.buffer = deque(
        (float(1 + i % 9),
         (70., 60., 50., 90., 80.),
         (69. - i % 7, 59., 49. - i % 5, 90., 79.), False)
        for i in range(n))
    for i in range(extras):
        source.hist[(i, 0)] = [1, float(i % 100), {"token": float(i % 17)}]
        source.map[(i, 0)] = (float(i % 100), ("token",))
        source.effects.stats[("manger", f"token-{i}")] = [
            1., [0.]*5, 1]
    return source


def _exercise(head_class, mind):
    memory = tuple(mind.buffer)
    head = head_class(mind)
    selected_priority = tuple(sorted(range(len(memory)),
                                     key=lambda i: -memory[i][0])[:3])
    selected_random = random_content_indices(
        eligible=len(memory), count=3, life_seed=44881,
        sleep_ordinal=2)
    # Both selection methods' traversal and HMAC costs are counted.
    head.apply(memory, selected_priority)
    predicted = head.predict(BODY)
    target = head.target_from_actual_outcome(BODY, False)
    return {
        "trained": head.training_updates,
        "priority_indices": selected_priority,
        "random_indices": selected_random,
        "prediction": predicted,
        "target": target,
    }


def _measure(head_class, mind):
    runtime = []
    peak = []
    output = None
    for _ in range(REPEATS):
        tracemalloc.start()
        try:
            begin = perf_counter_ns()
            actual = _exercise(head_class, mind)
            elapsed = perf_counter_ns() - begin
            _, peak_bytes = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        if output is not None and actual != output:
            raise RuntimeError("non-deterministic repeated shadow readout")
        output = actual
        runtime.append(elapsed)
        peak.append(peak_bytes)
    return {
        "median_elapsed_ns": int(median(runtime)),
        "median_peak_traced_bytes": int(median(peak)),
        "readout": output,
    }


def audit():
    rows = []
    for n in SIZES:
        for extras in EXTRA_STATES:
            mind = fixture(n, extras)
            legacy = _measure(PersonalDistressHead, mind)
            compact = _measure(CompactPersonalDistressHead, mind)
            if legacy["readout"] != compact["readout"]:
                raise RuntimeError("compact shadow broke original distress predictor")
            work = work_envelope(n)
            energy, vigilance = cognitive_cost(BodyLaws(), work)
            if not all(isfinite(x) and x > 0 for x in (energy, vigilance)):
                raise RuntimeError("invalid both-currency operator-category price")
            rows.append({
                "memories": n, "unrelated_spatial_effect_entries": extras,
                "legacy_median_ns": legacy["median_elapsed_ns"],
                "legacy_median_peak_bytes": legacy["median_peak_traced_bytes"],
                "compact_median_ns": compact["median_elapsed_ns"],
                "compact_median_peak_bytes": compact["median_peak_traced_bytes"],
                "same_forecast_training_and_memory_selection": True,
                "compact_declared_work": {
                    "cycles": work.cycles, "simulated_steps": work.simulated_steps,
                    "memory_items": work.memory_items, "replays": work.replays},
                "compact_provisional_energy": energy,
                "compact_provisional_vigilance": vigilance,
            })
    by = {(row["memories"], row["unrelated_spatial_effect_entries"]): row
          for row in rows}
    copy_growth = {
        str(n): by[n, 256]["legacy_median_peak_bytes"]
        > by[n, 0]["legacy_median_peak_bytes"] for n in SIZES}
    return {
        "schema": SCHEMA,
        "status": "SOFTWARE_ONLY_FULL_MIND_COPY_AND_COMPACT_COST_FALSIFIER",
        "repeats_per_cell": REPEATS,
        "fixed_memory_sizes": list(SIZES),
        "unrelated_state_sizes": list(EXTRA_STATES),
        "full_copy_peak_allocations_increase_with_unrelated_state": copy_growth,
        "structural_full_copy_defect_at_12_and_512": (
            copy_growth["12"] and copy_growth["512"]),
        "all_compact_predictions_exact_equal": True,
        "rows": rows,
        "host_timing_is_not_organism_energy": True,
        "tariff_is_operator_category_proposal_not_cpu_calibration": True,
        "worlds_opened": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_approved": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
