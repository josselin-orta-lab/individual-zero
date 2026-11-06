"""Read-only Stage-0 funding receipts and eight-block descriptive comparisons.

No runner, selection, allocation, tariff or Mind changes. Hash checks establish
internal consistency, NOT authenticated custody or independent populations.
Callers must supply their prospectively fixed expected cases and source pins.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from hashlib import sha256
import json
from math import isclose, isfinite

from i3.modules.body import ACTIONS, BodyLaws, CognitiveWork, debit_cognition, validate_laws

SCHEMA = "i3-stage0-energy/v1"
PHASES = ("decision", "learning")
CHANNELS = ("energy", "vigilance")
WORK = ("cycles", "simulated_steps", "memory_items", "replays")
ARMS = ("reference", "candidate")
POPULATIONS = 8
TOL = 1e-8  # Absolute accounting roundoff only; never a statistical tie rule.
RECORD_FIELDS = ("t", "action", "param", "option", "body", "pos", "dead")


def _digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _count(value, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("invalid nonnegative integer: " + name)
    return value


def _number(value, name: str) -> float:
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError("invalid finite nonnegative number: " + name)
    return value


def _equal(observed, expected, name: str) -> None:
    _number(observed, name)
    if not isclose(observed, expected, rel_tol=0.0, abs_tol=TOL):
        raise ValueError("inconsistent " + name)


def _body(value) -> tuple:
    if not isinstance(value, (list, tuple)) or len(value) != 5:
        raise ValueError("five-channel body required")
    for item in value:
        if _number(item, "body") > 100:
            raise ValueError("body outside physical bounds")
    return tuple(value)


def _bill(observed: dict, expected: dict) -> None:
    if set(observed) != set(CHANNELS):
        raise ValueError("invalid cost channels")
    for channel in CHANNELS:
        if set(observed[channel]) != {"requested", "paid", "unpaid"}:
            raise ValueError("invalid bill fields")
        for key in ("requested", "paid", "unpaid"):
            _equal(observed[channel][key], expected[channel][key], channel + ":" + key)


def energy_receipt(life: dict, *, expected_protocol: str,
                   expected_source_sha256: str) -> dict:
    """Verify a complete runtime trace and reduce its genuinely declared funding.

This checks original evidence chains, cost functions and physical debits, not
CPU instructions, motor costs, authenticity or the truth of a re-signed history.
Zero-step physical death is retained with undefined per-lived-step rates.
"""
    try:
        return _energy_receipt(life, expected_protocol, expected_source_sha256)
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError("missing or invalid funded life receipt") from exc


def _energy_receipt(life, protocol, source_pin):
    if not isinstance(protocol, str) or not protocol.strip():
        raise ValueError("explicit protocol required")
    if (type(source_pin) is not str or len(source_pin) != 64 or
            any(c not in "0123456789abcdef" for c in source_pin)):
        raise ValueError("explicit source SHA-256 required")
    m, account, rows = life["manifest"], life["cognitive_accounting"], life["trace"]
    if (m["schema"] != "i3-life-manifest/v2" or m["execution_model"] != "i3-funded-v2" or
            m["protocol"] != protocol or m["source"]["sha256"] != source_pin or
            _digest(m["source"]["files"]) != source_pin or
            _digest(m["world"]) != m["world_sha256"] or _digest(m) != life["manifest_id"]):
        raise ValueError("manifest or source lock mismatch")
    genome_hash = sha256(json.dumps(m["genome"], sort_keys=True,
                                   separators=(",", ":"), allow_nan=False).encode("ascii")).hexdigest()
    if genome_hash != life["genome"] or m["world"]["name"] != life["world"]:
        raise ValueError("genome or world identity mismatch")
    horizon = _count(life["horizon"], "horizon")
    steps = _count(life["steps_lived"], "steps")
    if (horizon < 1 or type(m["horizon"]) is not int or horizon != m["horizon"] or
            type(m["life_seed"]) is not int or steps > horizon or len(rows) != steps or
            type(life["life_seed"]) is not int or life["life_seed"] != m["life_seed"]):
        raise ValueError("incomplete life or execution context")
    if life["terminal"] not in ("dead", "censored"):
        raise ValueError("crashed or unfinished life is not a physical death")
    if (life["terminal"] == "censored") != (steps == horizon and not life["death_causes"]):
        raise ValueError("invalid censoring")
    if life["terminal"] == "dead" and not life["death_causes"]:
        raise ValueError("physical death requires a cause")
    if account["schema"] != "i3-cognitive-funding/v2" or account["status"] != "SETTLED_FOR_DECLARED_WORK":
        raise ValueError("unsettled accounting")
    for key in ("shortfall_steps", "pending_replays"):
        if _count(account[key], key) != 0:
            raise ValueError("unsettled " + key)
    for key in ("pending_energy", "pending_vigilance"):
        _equal(account[key], 0.0, key)
    laws = BodyLaws(**m["world"]["laws"])
    validate_laws(laws)
    paid = {phase: {ch: 0.0 for ch in CHANNELS} for phase in PHASES}
    work = {phase: {key: 0 for key in WORK} for phase in PHASES}
    totals = {ch: {key: 0.0 for key in ("requested", "paid", "unpaid")} for ch in CHANNELS}
    previous_body = _body(m["world"]["body"])
    evidence = life["manifest_id"]
    trace_head = sha256(json.dumps([genome_hash, life["world"], life["life_seed"], horizon],
                                   separators=(",", ":")).encode()).hexdigest()
    actions = Counter()
    for i, row in enumerate(rows, 1):
        if type(row["t"]) is not int or row["t"] != i or (row["dead"] and i != steps):
            raise ValueError("nonsequential or postmortem trace")
        if any(previous_body[k] <= 0 for k in (1, 2, 3)):
            raise ValueError("work after physical death")
        phases = row["funding_phases"]
        if set(phases) != set(PHASES):
            raise ValueError("unknown funding phase")
        if _body(phases["decision"]["body_before"]) != previous_body:
            raise ValueError("discontinuous pre-decision body")
        summed_work = {key: 0 for key in WORK}
        summed_bill = {ch: {key: 0.0 for key in totals[ch]} for ch in CHANNELS}
        for phase in PHASES:
            part = phases[phase]
            if set(part["work"]) != set(WORK):
                raise ValueError("invalid work vector")
            counters = CognitiveWork(**part["work"])
            before = _body(part["body_before"])
            after, bill = debit_cognition(before, laws, counters)
            recorded_after = _body(part["body_after_debit"])
            for actual, expected in zip(recorded_after, after):
                _equal(actual, expected, "phase body debit")
            _bill(part["accounting"], bill)
            if phase == "learning" and row["dead"] and any(part["work"].values()):
                raise ValueError("postmortem learning")
            for key in WORK:
                work[phase][key] += part["work"][key]
                summed_work[key] += part["work"][key]
            for ch in CHANNELS:
                paid[phase][ch] += bill[ch]["paid"]
                for key in totals[ch]:
                    summed_bill[ch][key] += bill[ch][key]
        if (set(row["cognitive_work"]) != set(WORK) or
                any(type(row["cognitive_work"][k]) is not int for k in WORK) or
                row["cognitive_work"] != summed_work):
            raise ValueError("step and phase work disagree")
        _bill(row["cognitive_accounting"], summed_bill)
        for ch in CHANNELS:
            for key in totals[ch]:
                totals[ch][key] += summed_bill[ch][key]
        previous_body = _body(row["body"])
        if previous_body != _body(phases["learning"]["body_after_debit"]):
            raise ValueError("final step body differs from paid learning body")
        causes = [name for name, k in (("zero_food", 1), ("zero_water", 2),
                                       ("zero_integrity", 3)) if previous_body[k] <= 0]
        if row["dead"] != causes:
            raise ValueError("physical terminal cause disagrees with body")
        if row["action"] is not None and row["action"] not in ACTIONS:
            raise ValueError("unknown physical action")
        actions[row["action"] if row["action"] is not None else "physical_inactivity"] += 1
        record = {key: row[key] for key in RECORD_FIELDS}
        trace_head = sha256((trace_head + json.dumps(record, sort_keys=True,
                                                    separators=(",", ":"))).encode()).hexdigest()
        evidence = _digest({"previous": evidence, "record": record,
                            "work": row["cognitive_work"],
                            "accounting": row["cognitive_accounting"], "funding_phases": phases})
    causes = [name for name, k in (("zero_food", 1), ("zero_water", 2),
                                   ("zero_integrity", 3)) if previous_body[k] <= 0]
    if life["death_causes"] != causes or (steps == 0 and not causes):
        raise ValueError("invalid final physical death")
    if life["final_body"] != [round(x, 6) for x in previous_body]:
        raise ValueError("final body summary mismatch")
    if life["actions"] != dict(sorted(actions.items())):
        raise ValueError("physical action counts mismatch")
    if _count(account["inactive_steps"], "inactive steps") != actions["physical_inactivity"]:
        raise ValueError("physical inactivity is not chosen waiting")
    if _count(account["replays_executed"], "replays") != work["learning"]["replays"]:
        raise ValueError("replay count mismatch")
    _bill(account["totals"], totals)
    evidence = _digest({"previous": evidence, "terminal": life["terminal"], "accounting": account})
    if trace_head != life["trace_head"] or evidence != life["evidence_head"]:
        raise ValueError("original evidence chain mismatch")
    return {"schema": SCHEMA, "protocol": protocol, "source_sha256": source_pin,
            "manifest_id": life["manifest_id"], "evidence_head": evidence,
            "trace_head": trace_head, "world_sha256": m["world_sha256"],
            "genome_sha256": genome_hash, "life_seed": life["life_seed"],
            "horizon": horizon, "steps_lived": steps, "terminal": life["terminal"],
            "death_causes": list(causes), "inactive_steps": actions["physical_inactivity"],
            "chosen_wait_steps": actions["attendre"], "sleep_steps": actions["dormir"],
            "phase_work": work, "phase_paid": paid,
            "paid": {ch: totals[ch]["paid"] for ch in CHANNELS}}


def _aggregate(rows: list[dict]) -> dict:
    steps = sum(r["steps_lived"] for r in rows)
    inactive = sum(r["inactive_steps"] for r in rows)
    paid = {ch: sum(r["paid"][ch] for r in rows) for ch in CHANNELS}
    return {"lives": len(rows), "censored": sum(r["terminal"] == "censored" for r in rows),
            "dead": sum(r["terminal"] == "dead" for r in rows),
            "zero_step_lives": sum(r["steps_lived"] == 0 for r in rows),
            "steps_lived": steps, "inactive_steps": inactive,
            "inactive_fraction": inactive / steps if steps else None,
            "chosen_wait_steps": sum(r["chosen_wait_steps"] for r in rows),
            "sleep_steps": sum(r["sleep_steps"] for r in rows),
            "phase_work": {p: {k: sum(r["phase_work"][p][k] for r in rows) for k in WORK} for p in PHASES},
            "phase_paid": {p: {ch: sum(r["phase_paid"][p][ch] for r in rows) for ch in CHANNELS} for p in PHASES},
            "paid": paid, "paid_per_lived_step": {ch: paid[ch] / steps if steps else None for ch in CHANNELS},
            "rate_denominator": "sum_of_all_lived_steps_including_deaths_NOT_mean_of_life_rates"}


def population_energy(pairs: Iterable[Mapping], *, expected_cases: Mapping,
                      expected_protocol: str, source_pins: Mapping) -> dict:
    """Reduce complete declared pairs into eight blocks, never life-level inference.

Each row has population, case_id, reference and candidate (full runtime lives).
Expected cases must be fixed independently of outcomes. Same world/seed/horizon
is required within pairs; sources and selected genomes may differ between arms.
No shared world across populations or repeated life identity within one arm.
The caller still owns allocation, ancestry, intervention and source-lock custody.
"""
    if (not isinstance(expected_cases, Mapping) or
            any(type(p) is not int for p in expected_cases) or
            set(expected_cases) != set(range(POPULATIONS)) or set(source_pins) != set(ARMS)):
        raise ValueError("eight identified blocks and two source pins required")
    expected = set()
    for p, ids in expected_cases.items():
        if not isinstance(ids, (list, tuple)) or not ids or len(set(ids)) != len(ids):
            raise ValueError("nonempty unique predeclared case lists required")
        for name in ids:
            if type(name) is not str or not name.strip():
                raise ValueError("case identifiers must be nonempty strings")
            expected.add((p, name))
    inputs, seen = list(pairs), set()
    for pair in inputs:
        if not isinstance(pair, Mapping) or set(pair) != {"population", "case_id", *ARMS}:
            raise ValueError("invalid paired input fields")
        p, name = pair["population"], pair["case_id"]
        if type(p) is not int or type(name) is not str or (p, name) not in expected or (p, name) in seen:
            raise ValueError("duplicate or foreign paired case")
        seen.add((p, name))
    if seen != expected:
        raise ValueError("incomplete panel; never discard missing/crashed/early-death lives")
    groups = {p: {a: [] for a in ARMS} for p in range(POPULATIONS)}
    identities = {a: set() for a in ARMS}
    world_owners, horizon = {}, None
    for pair in sorted(inputs, key=lambda x: (x["population"], x["case_id"])):
        p = pair["population"]
        receipts = {a: energy_receipt(pair[a], expected_protocol=expected_protocol,
                                     expected_source_sha256=source_pins[a]) for a in ARMS}
        a, b = (receipts[arm] for arm in ARMS)
        for key in ("world_sha256", "life_seed", "horizon"):
            if a[key] != b[key]:
                raise ValueError("unequal paired physical opportunities: " + key)
        if horizon is None:
            horizon = a["horizon"]
        if a["horizon"] != horizon:
            raise ValueError("mixed panel horizons")
        world = a["world_sha256"]
        if world in world_owners and world_owners[world] != p:
            raise ValueError("shared ecology does not form independent population blocks")
        world_owners[world] = p
        for arm, receipt in receipts.items():
            identity = tuple(receipt[k] for k in ("genome_sha256", "world_sha256", "life_seed", "horizon"))
            if identity in identities[arm]:
                raise ValueError("same life counted twice in one arm")
            identities[arm].add(identity)
            groups[p][arm].append(receipt)
    blocks = [{"population": p, **{a: _aggregate(groups[p][a]) for a in ARMS}}
              for p in range(POPULATIONS)]
    contrasts = []
    for block in blocks:
        a, b = block["reference"], block["candidate"]
        contrasts.append({"population": block["population"],
                          "censored_fraction_difference": (b["censored"] - a["censored"]) / a["lives"],
                          "lived_steps_difference": b["steps_lived"] - a["steps_lived"],
                          "paid_difference": {ch: b["paid"][ch] - a["paid"][ch] for ch in CHANNELS},
                          "inactive_fraction_difference": (b["inactive_fraction"] - a["inactive_fraction"]
                              if a["steps_lived"] and b["steps_lived"] else None)})
    return {"schema": SCHEMA, "status": "DESCRIPTIVE_NOT_CAUSAL_MEDIATION_OR_GO",
            "analysis_unit": "eight_declared_population_ecology_blocks",
            "independence_authenticated": False, "realized_cost_parity_assumed": False,
            "contrast_direction": "candidate_minus_reference", "horizon": horizon,
            "populations": blocks, "paired_differences": contrasts,
            "life_receipts": [{"population": p, "arm": a, "receipts": groups[p][a]}
                              for p in range(POPULATIONS) for a in ARMS]}
