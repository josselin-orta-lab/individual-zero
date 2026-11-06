"""P2 comparison audit: cost equality is measured, not assumed.

An individual's work trace is an external observer-only tariff. A probe never
receives the individual's map, outcomes, action, or hidden world effects. The
tariff can affect physical affordability, so this is a *diagnostic pairing*,
not a blind prospective P4 experiment; P3 must choose a frozen tariff from
development and never select on validation or held-out results.
"""
from __future__ import annotations

from dataclasses import asdict
import json

from i3.lab import p2_ecologies, probes
from i3.modules.body import CognitiveWork, cognitive_cost
from i3.runtime.life import run_life

PROTOCOL = "i3-p2-cost-witness-v1"
PROBE_NAMES = {"reference": probes.reference_survival, "oracle": probes.oracle_survival}


def work_witness(life: dict) -> tuple[tuple[CognitiveWork, CognitiveWork], ...]:
    """Capture paid decision + post-action work. No hidden world knowledge."""
    if "trace" not in life or len(life["trace"]) != life["steps_lived"]:
        raise ValueError("complete instrumented individual trace required")
    if life["cognitive_accounting"]["shortfall_steps"] != 0:
        raise ValueError("unfunded individual is not a valid tariff witness")
    if life["cognitive_accounting"]["pending_replays"] != 0:
        raise ValueError("unsettled individual work")
    result = []
    for row in life["trace"]:
        phases = row["funding_phases"]
        decision = CognitiveWork(**phases["decision"]["work"])
        learning = CognitiveWork(**phases["learning"]["work"])
        for phase in (phases["decision"], phases["learning"]):
            for channel, requested in phase["accounting"].items():
                if abs(requested["paid"] - requested["requested"]) > 1e-10 or abs(
                        requested["unpaid"]) > 1e-10:
                    raise ValueError("individual did not settle its declared work")
        result.append((decision, learning))
    return tuple(result)


def _charges(laws, work):
    e, v = cognitive_cost(laws, work)
    return {"energy": e, "vigilance": v}


def assess_pair(genome: dict, spec, life_seed: int, horizon: int,
                *, probe: str = "reference") -> dict:
    """A diagnostic paired *prefix*; full matching requires both censored lives.

    A private individual decision is NOT a probe input. The tariff is supplied
    by an external observer, and its identity/hash should be sealed for any
    future prospective use. Oracle uses complete world state, hence can witness
    feasibility only by SUCCESS, never infeasibility by failure.
    """
    if probe not in PROBE_NAMES or type(horizon) is not int or horizon < 1:
        raise ValueError("unknown probe or invalid horizon")
    life = run_life(genome, spec, life_seed, horizon, keep_trace=True,
                    protocol=PROTOCOL)
    schedule = work_witness(life)
    audit = []
    steps = PROBE_NAMES[probe](spec, horizon, work_schedule=schedule, audit=audit)
    if steps != len(audit):
        raise RuntimeError("probe step audit and elapsed time disagree")
    billed = {"energy": 0.0, "vigilance": 0.0}
    observed = {"energy": 0.0, "vigilance": 0.0}
    matched = 0
    for i, row in enumerate(audit):
        request = schedule[i]
        own = (row["paid_decision"], row["paid_learning"])
        for charge in request:
            for key, value in _charges(spec.laws, charge).items():
                billed[key] += value
        for charge in own:
            for key, value in _charges(spec.laws, charge).items():
                observed[key] += value
        exact = (row["status"] == "MATCHED" and own == request)
        if exact:
            matched += 1
    full = (matched == len(audit) == len(schedule) == horizon and
            life["terminal"] == "censored" and steps == horizon)
    return {
        "protocol": PROTOCOL,
        "probe": probe,
        "information": "hidden_full_world" if probe == "oracle" else "capture_only",
        "world_sha256": life["manifest"]["world_sha256"],
        "individual_manifest_id": life["manifest_id"],
        "individual_evidence_head": life["evidence_head"],
        "individual_steps": life["steps_lived"],
        "individual_terminal": life["terminal"],
        "probe_steps": steps,
        "probe_terminal": "censored" if steps == horizon else "dead_or_reference_exhausted",
        "horizon": horizon,
        "compared_ticks": len(audit),
        "exactly_matched_ticks": matched,
        "unmatched_ticks": len(audit) - matched,
        "costs_requested": billed,
        "costs_paid": observed,
        "full_cost_match": full,
        "interpretation": ("full_horizon_comparison" if full else
                           "partial_or_unfunded_not_a_fair_survival_ceiling"),
        "probe_audit": [{
            "t": row["t"],
            "status": row["status"],
            "requested_decision": asdict(row["requested_decision"]),
            "requested_learning": asdict(row["requested_learning"]),
            "paid_decision": asdict(row["paid_decision"]),
            "paid_learning": asdict(row["paid_learning"]),
        } for row in audit],
    }


def calibrate_fixed_tariff() -> dict:
    """Freeze a common v2 profile using DEVELOPMENT worlds only.

    Engineering calibration, never selection fitness or validation tuning.
    One static tariff for all future probe worlds avoids feeding private
    individual action-dependent costs into a reference searcher.
    """
    from hashlib import sha256
    from i3.modules.genome import generation_zero
    total = {"decision": {k: 0 for k in ("cycles", "simulated_steps", "memory_items", "replays")},
             "learning": {k: 0 for k in ("cycles", "simulated_steps", "memory_items", "replays")}}
    n = 0
    sources = []
    for family in p2_ecologies.FAMILIES:
        for index in (0, 1):
            spec = p2_ecologies.world_for(family, "development", index)
            life = run_life(generation_zero(6000), spec, 10_000 + index, 120,
                            keep_trace=True, protocol=PROTOCOL + "-calibration")
            sources.append({"family": family, "index": index,
                            "world_sha256": life["manifest"]["world_sha256"],
                            "manifest_id": life["manifest_id"]})
            for d, l in work_witness(life):
                for k in total["decision"]:
                    total["decision"][k] += getattr(d, k)
                    total["learning"][k] += getattr(l, k)
                n += 1
    if n == 0:
        raise RuntimeError("no development work available for calibration")
    tariff = {phase: {k: (v + n // 2) // n for k, v in counts.items()}
              for phase, counts in total.items()}
    profile = {
        "schema": "i3-p2-static-tariff-v1",
        "cohort": "development",
        "calibration": sources,
        "sampled_ticks": n,
        "tariff": tariff,
        "purpose": "static_common_probe_bill_not_per_instruction_equivalence",
    }
    profile["sha256"] = sha256(
        json.dumps(profile, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return profile


def run_fixed_tariff_probe(spec, horizon: int, profile: dict, *,
                           probe: str = "reference") -> dict:
    """Use a previously frozen profile without looking at any individual's life."""
    from hashlib import sha256
    if probe not in PROBE_NAMES or type(horizon) is not int or horizon < 1:
        raise ValueError("unknown probe or horizon")
    if type(profile) is not dict or profile.get("schema") != "i3-p2-static-tariff-v1" or (
            profile.get("cohort") != "development"):
        raise ValueError("development-only calibrated profile required")
    content = {k: v for k, v in profile.items() if k != "sha256"}
    digest = sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != profile.get("sha256"):
        raise ValueError("static work tariff has been modified since freezing")
    decision = CognitiveWork(**profile["tariff"]["decision"])
    learning = CognitiveWork(**profile["tariff"]["learning"])
    audit = []
    steps = PROBE_NAMES[probe](spec, horizon, work_schedule=((decision, learning),) * horizon,
                              audit=audit)
    exact = sum(row["status"] == "MATCHED" and
                row["paid_decision"] == decision and row["paid_learning"] == learning
                for row in audit)
    totals = {"energy": 0.0, "vigilance": 0.0}
    for row in audit:
        for block in (row["paid_decision"], row["paid_learning"]):
            for k, v in _charges(spec.laws, block).items():
                totals[k] += v
    return {
        "schema": "i3-p2-probe-with-static-tariff-v1",
        "profile_sha256": profile["sha256"],
        "probe": probe,
        "information": "hidden_full_world" if probe == "oracle" else "capture_only",
        "world_sha256": p2_ecologies.fingerprint(spec),
        "steps": steps, "horizon": horizon, "matched_ticks": exact,
        "unmatched_ticks": len(audit) - exact,
        "fully_funded": exact == len(audit) == horizon,
        "paid": totals,
        "terminal": "censored" if steps == horizon else "dead_or_unfunded",
        "scope": "frozen_mean_work_tariff_not_exact_individual_work",
    }


def development_diagnostic() -> dict:
    """Small engineering-only smoke check; never opens selection or reserve."""
    from i3.modules.genome import generation_zero
    result = {"protocol": PROTOCOL, "cohorts": ["development"],
              "world_protocol": p2_ecologies.partition_manifest(), "cases": [],
              "frozen_tariff": calibrate_fixed_tariff()}
    for family in p2_ecologies.FAMILIES:
        for index in (0, 1):
            spec = p2_ecologies.world_for(family, "development", index)
            case = {"family": family, "index": index,
                    "world_sha256": p2_ecologies.fingerprint(spec),
                    "probes": []}
            for name in ("reference", "oracle"):
                audited = assess_pair(generation_zero(6000), spec, 10_000 + index,
                                      120, probe=name)
                case["probes"].append({k: v for k, v in audited.items()
                                       if k != "probe_audit"})
            case["static_tariff_reference"] = run_fixed_tariff_probe(
                spec, 120, result["frozen_tariff"])
            result["cases"].append(case)
    return result


if __name__ == "__main__":
    print(json.dumps(development_diagnostic(), indent=2, sort_keys=True))
