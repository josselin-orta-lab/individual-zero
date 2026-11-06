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


def development_diagnostic() -> dict:
    """Small engineering-only smoke check; never opens selection or reserve."""
    from i3.modules.genome import generation_zero
    result = {"protocol": PROTOCOL, "cohorts": ["development"],
              "world_protocol": p2_ecologies.partition_manifest(), "cases": []}
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
            result["cases"].append(case)
    return result


if __name__ == "__main__":
    print(json.dumps(development_diagnostic(), indent=2, sort_keys=True))
