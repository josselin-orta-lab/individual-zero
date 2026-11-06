"""P2 development-only panel: quantify model-charge mismatch before P3.

No mutation, fitness, survivor selection, validation or reserved-world access.
The observer receives full work receipts; neither individual nor reference
policy sees the other side's actions or private state. Compute time is separate.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json

from i3.lab import p2_ecologies as ecologies
from i3.lab import p2_validation as validation
from i3.modules.body import CognitiveWork, cognitive_cost
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

PROTOCOL = "i3-p2-development-charge-panel-v1"
# Explicitly disjoint from indices (0, 1) used for static calibration.
INDICES = (2, 3, 4, 5)
GENOME_SEEDS = (6000, 6001, 6002)
LIFE_SEED_BASE = 51_000
HORIZON = ecologies.HORIZON


def _totals(laws, blocks):
    energy = vigilance = 0.0
    for block in blocks:
        e, v = cognitive_cost(laws, block)
        energy += e
        vigilance += v
    return {"energy": energy, "vigilance": vigilance}


def _relative_difference(actual, reference):
    if reference == 0:
        return 0.0 if actual == 0 else None
    return (actual - reference) / reference


def _rounded(channels):
    return {name: round(value, 8) for name, value in channels.items()}


def run_panel() -> dict:
    """Cost observations only. Does NOT certify comparator parity or P3 GO."""
    profile = validation.calibrate_fixed_tariff()
    decision = CognitiveWork(**profile["tariff"]["decision"])
    learning = CognitiveWork(**profile["tariff"]["learning"])
    rows = []
    for family in ecologies.FAMILIES:
        for index in INDICES:
            spec = ecologies.world_for(family, "development", index)
            world_id = ecologies.fingerprint(spec)
            static_reference = validation.run_fixed_tariff_probe(
                spec, HORIZON, profile, probe="reference")
            static_oracle = validation.run_fixed_tariff_probe(
                spec, HORIZON, profile, probe="oracle")
            for genome_seed in GENOME_SEEDS:
                life = run_life(generation_zero(genome_seed), spec,
                                LIFE_SEED_BASE + genome_seed, HORIZON,
                                keep_trace=True, protocol=PROTOCOL)
                witness = validation.work_witness(life)
                flat = [work for phases in witness for work in phases]
                actual = _totals(spec.laws, flat)
                static = _totals(spec.laws, [decision, learning] * len(witness))
                vector_exact = sum(pair == (decision, learning) for pair in witness)
                phase_counts = {"decision": Counter(), "learning": Counter()}
                for d, l in witness:
                    for phase, block in (("decision", d), ("learning", l)):
                        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
                            phase_counts[phase][key] += getattr(block, key)
                rows.append({
                    "family": family, "development_index": index,
                    "genome_seed": genome_seed, "world_sha256": world_id,
                    "individual_manifest_id": life["manifest_id"],
                    "individual_evidence_head": life["evidence_head"],
                    "individual_terminal": life["terminal"],
                    "individual_steps": life["steps_lived"],
                    "individual_inactive_steps": life["cognitive_accounting"]["inactive_steps"],
                    "individual_shortfall_steps": life["cognitive_accounting"]["shortfall_steps"],
                    "individual_pending_replays": life["cognitive_accounting"]["pending_replays"],
                    "individual_paid": _rounded(actual),
                    "static_tariff_for_same_prefix": _rounded(static),
                    "relative_gap": {k: (None if _relative_difference(actual[k], static[k])
                                        is None else round(_relative_difference(actual[k], static[k]), 6))
                                     for k in actual},
                    "individual_work_exact_vectors": vector_exact,
                    "individual_work_ticks": len(witness),
                    "individual_work_totals": {p: dict(v) for p, v in phase_counts.items()},
                    "reference": static_reference,
                    "oracle": static_oracle,
                })
    statuses = Counter(row["individual_terminal"] for row in rows)
    summary = {
        "cases": len(rows), "ecological_families": len(ecologies.FAMILIES),
        "worlds": len(ecologies.FAMILIES) * len(INDICES),
        "individual_deaths": statuses["dead"],
        "individual_censored": statuses["censored"],
        "paid_shortfalls": sum(r["individual_shortfall_steps"] for r in rows),
        "pending_replays": sum(r["individual_pending_replays"] for r in rows),
        "individual_inactive_steps": sum(r["individual_inactive_steps"] for r in rows),
        "individual_steps": sum(r["individual_steps"] for r in rows),
        "individual_exact_tariff_ticks": sum(r["individual_work_exact_vectors"] for r in rows),
        "reference_fully_funded_worlds": sum(r["reference"]["fully_funded"] for r in rows[::len(GENOME_SEEDS)]),
        "oracle_fully_funded_worlds": sum(r["oracle"]["fully_funded"] for r in rows[::len(GENOME_SEEDS)]),
    }
    out = {
        "schema": PROTOCOL,
        "scope": "development-only-diagnostic-not-selection-or-P3",
        "calibration_indices": [0, 1],
        "audit_indices": list(INDICES),
        "genome_seeds": list(GENOME_SEEDS),
        "horizon": HORIZON,
        "fixed_tariff_sha256": profile["sha256"],
        "fixed_work": profile["tariff"],
        "summary": summary,
        "rows": rows,
    }
    out["sha256"] = sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return out


if __name__ == "__main__":
    result = run_panel()
    print(json.dumps({
        "schema": result["schema"],
        "sha256": result["sha256"],
        "profile_sha256": result["fixed_tariff_sha256"],
        "summary": result["summary"],
        "by_family": {
            family: {
                "deaths": sum(r["individual_terminal"] == "dead" for r in result["rows"]
                              if r["family"] == family),
                "mean_relative_energy_gap": round(
                    sum(r["relative_gap"]["energy"] for r in result["rows"]
                        if r["family"] == family) / len(INDICES) / len(GENOME_SEEDS), 5),
                "mean_relative_vigilance_gap": round(
                    sum(r["relative_gap"]["vigilance"] for r in result["rows"]
                        if r["family"] == family) / len(INDICES) / len(GENOME_SEEDS), 5),
            } for family in ecologies.FAMILIES
        },
    }, indent=2, sort_keys=True))
