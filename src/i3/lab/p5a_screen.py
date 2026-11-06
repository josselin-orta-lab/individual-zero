"""P5a prospective paid selective-retention screen, no genome selection.

--preflight only examines the allocation and 48 frozen G2 hashes; it NEVER
opens a new validation world. --run refuses to instantiate any study world
unless source HEAD, allocation digest and protocol were frozen in advance.
Keep each life trace transiently to verify and aggregate phase-specific
paid work, but archive compact full-lifetime receipts and evidence hashes.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from math import sqrt
import os
from pathlib import Path
import subprocess
import sys

from i3.lab import p2_ecologies, p4a_validation, p5a_schedule
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot

PROTOCOL = p5a_schedule.PROTOCOL
MODES = p5a_schedule.MODES
CHANNELS = ("energy", "vigilance")
PHASES = ("decision", "learning")
WORK = ("cycles", "simulated_steps", "memory_items", "replays")
TOLERANCE = 1e-7


def _head_sha() -> str:
    root = Path(__file__).resolve().parents[3]
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                          text=True, capture_output=True, check=True,
                          timeout=5).stdout.strip()


def _preflight():
    if _head_sha() != os.environ.get("I3_P5A_SOURCE_SHA", ""):
        raise RuntimeError("P5a exact scientific source was not preregistered")
    schedule = p5a_schedule.manifest()
    if schedule["sha256"] != os.environ.get("I3_P5A_SCHEDULE_SHA", ""):
        raise RuntimeError("P5a allocation SHA was not preregistered")
    if os.environ.get("I3_P5A_APPROVED_PROTOCOL", "") != PROTOCOL:
        raise RuntimeError("P5a protocol not prospectively approved")
    genomes = p4a_validation.verify_frozen_genomes()
    return schedule, genomes


def _receipt(life, *, mode: str, arm: str, slot: int, population: int,
             family: str, repeat: int, index: int, seed: int,
             world_hash: str, genome_sha256: str) -> dict:
    """No missing, unpaid, postmortem or falsely censored work survives."""
    acc, rows = life["cognitive_accounting"], life["trace"]
    steps = life["steps_lived"]
    if (life["learning_intervention"] != mode or
        life["genome"] != genome_sha256 or
        life["manifest"]["world_sha256"] != world_hash or
        life["life_seed"] != seed or life["horizon"] != p5a_schedule.HORIZON or
        not life["manifest_id"] or not life["evidence_head"] or
        not life["trace_head"] or type(steps) is not int or
        not 1 <= steps <= p5a_schedule.HORIZON or len(rows) != steps):
        raise RuntimeError("invalid P5a provenance or incomplete witness")
    if (life["terminal"] not in ("dead", "censored") or
        (life["terminal"] == "censored") !=
        (steps == p5a_schedule.HORIZON and not life["death_causes"]) or
        (life["terminal"] == "dead" and not life["death_causes"])):
        raise RuntimeError("invalid terminal classification")
    if (acc["status"] != "SETTLED_FOR_DECLARED_WORK" or
        acc["shortfall_steps"] != 0 or acc["pending_replays"] != 0 or
        abs(acc["pending_energy"]) > TOLERANCE or
        abs(acc["pending_vigilance"]) > TOLERANCE):
        raise RuntimeError("cognitive accounting was not settled")
    expected_retained = acc["learning_updates"]
    if (life["retained_outcome_learning_updates"] != expected_retained or
        life["shadow_discarded_outcome_updates"] != 0):
        raise RuntimeError("wrong P5a component-retention accounting")
    paid = {phase: {ch: 0.0 for ch in CHANNELS} for phase in PHASES}
    work = {phase: {key: 0 for key in WORK} for phase in PHASES}
    counted_replays = 0
    for i, row in enumerate(rows):
        if row["t"] != i + 1 or (row["dead"] and i + 1 != steps):
            raise RuntimeError("nonsequential or postmortem history")
        phases = row["funding_phases"]
        for phase in PHASES:
            counters = phases[phase]["work"]
            if set(counters) != set(WORK):
                raise RuntimeError("incorrect cognitive work schema")
            for key in WORK:
                if type(counters[key]) is not int or counters[key] < 0:
                    raise RuntimeError("non-integer cognitive work")
                work[phase][key] += counters[key]
            for ch in CHANNELS:
                bill = phases[phase]["accounting"][ch]
                if (bill["unpaid"] > TOLERANCE or
                    abs(bill["requested"] - bill["paid"]) > TOLERANCE or
                    bill["paid"] < -TOLERANCE):
                    raise RuntimeError("unpaid or forged cognitive phase")
                paid[phase][ch] += bill["paid"]
        if row["dead"] and any(phases["learning"]["work"].values()):
            raise RuntimeError("learning after physical death")
        counted_replays += phases["learning"]["work"]["replays"]
    if counted_replays != acc["replays_executed"]:
        raise RuntimeError("declared replays differ from actually paid work")
    for ch in CHANNELS:
        amounts = acc["totals"][ch]
        if (abs(amounts["unpaid"]) > TOLERANCE or
            abs(amounts["requested"] - amounts["paid"]) > TOLERANCE or
            abs(sum(paid[phase][ch] for phase in PHASES) -
                amounts["paid"]) > TOLERANCE):
            raise RuntimeError("life and phase receipts disagree")
    return {
        "population": population, "arm": arm, "slot": slot,
        "family": family, "repeat": repeat, "mode": mode,
        "validation_world_index": index, "life_seed": seed,
        "genome_sha256": genome_sha256,
        "world_sha256": world_hash,
        "source_sha256": life["manifest"]["source"]["sha256"],
        "manifest_id": life["manifest_id"], "evidence_head": life["evidence_head"],
        "trace_head": life["trace_head"],
        "steps_lived": steps, "terminal": life["terminal"],
        "censored": life["terminal"] == "censored",
        "death_causes": life["death_causes"],
        "paid": {ch: acc["totals"][ch]["paid"] for ch in CHANNELS},
        "phase_paid": paid, "phase_work": work,
        "inactive_steps": acc["inactive_steps"],
        "learning_computations": acc["learning_updates"],
        "replays_executed": acc["replays_executed"],
        "outcome_model_sha256": life["outcome_model_sha256"],
        "spatial_beliefs_sha256": life["spatial_beliefs_sha256"],
    }


def run() -> dict:
    schedule, genomes = _preflight()
    receipts = []
    engine_sha = set()
    opportunity_hashes = {}
    for allocation in schedule["allocation"]:
        p, fam, repeat = (allocation["population"], allocation["family"],
                          allocation["repeat"])
        index, seed = allocation["index"], allocation["life_seed"]
        # FIRST world construction happens only after all prereg locks.
        spec = p2_ecologies.world_for(fam, "validation", index)
        world_sha256 = digest(world_snapshot(spec))
        opportunity_hashes[(p, fam, repeat)] = world_sha256
        for arm in p5a_schedule.ARMS:
            for slot in range(p5a_schedule.GENOTYPES):
                genotype = genomes[(p, arm, slot)]
                for mode in MODES:
                    life = run_life(genotype["genome"], spec, seed,
                                    p5a_schedule.HORIZON, keep_trace=True,
                                    protocol=PROTOCOL, learning_mode=mode,
                                    observer_mind_digest=True)
                    receipt = _receipt(life, mode=mode, arm=arm, slot=slot,
                                       population=p, family=fam, repeat=repeat,
                                       index=index, seed=seed,
                                       world_hash=world_sha256,
                                       genome_sha256=genotype["genome_sha256"])
                    engine_sha.add(receipt["source_sha256"])
                    receipts.append(receipt)
    if (len(receipts) != p5a_schedule.LIVES or
        len(opportunity_hashes) != 24 or len(set(opportunity_hashes.values())) != 24 or
        len(engine_sha) != 1):
        raise RuntimeError("missing world exposure, life or engine uniformity")
    raw = {
        "schema": PROTOCOL, "source_sha": _head_sha(),
        "schedule_sha256": schedule["sha256"],
        "frozen_g2_sha256": p5a_schedule.p4a_schedule.G2_CANONICAL_SHA256,
        "status": "P5A_COMPONENT_SCREEN_NO_P4_RESERVE",
        "total_lives": len(receipts), "lives": receipts,
    }
    raw["sha256"] = sha256(
        json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return raw


def _two_sided_sign_flip_p(differences: list[int]) -> float:
    """Exact paired sign-flip reference, n=4, descriptive not a magic test."""
    target = abs(sum(differences))
    extreme = sum(
        abs(sum(s * d for s, d in zip(signs, differences))) >= target
        for signs in product((-1, 1), repeat=len(differences)))
    return extreme / (2 ** len(differences))


def _holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    n = len(p_values)
    ordered = sorted(p_values, key=lambda key: (p_values[key], key))
    out = {}
    previous = 0.0
    for i, key in enumerate(ordered):
        previous = max(previous, min(1.0, (n - i) * p_values[key]))
        out[key] = previous
    return out


def summarize(result: dict) -> dict:
    """Predeclared 3 contrasts, independent genetic population as the unit."""
    people = result["lives"]
    populations = []
    for p in range(p5a_schedule.POPULATIONS):
        groups = {}
        for mode in MODES:
            lives = [x for x in people if x["population"] == p and x["mode"] == mode]
            if len(lives) != 72:
                raise ValueError("incomplete population/mode group")
            groups[mode] = {
                "censored": sum(x["censored"] for x in lives),
                "dead": sum(not x["censored"] for x in lives),
                "lived_steps": sum(x["steps_lived"] for x in lives),
                "inactive_steps": sum(x["inactive_steps"] for x in lives),
                "paid": {ch: round(sum(x["paid"][ch] for x in lives), 7)
                         for ch in CHANNELS},
                "phase_paid": {phase: {
                    ch: round(sum(x["phase_paid"][phase][ch] for x in lives), 7)
                    for ch in CHANNELS} for phase in PHASES},
                "learning_computations": sum(x["learning_computations"] for x in lives),
                "replays_executed": sum(x["replays_executed"] for x in lives),
                "lives_with_replay": sum(x["replays_executed"] > 0 for x in lives),
            }
        populations.append({
            "population": p, "modes": groups,
            "contrasts": {
                mode: groups["normal"]["censored"] - groups[mode]["censored"]
                for mode in MODES[1:]},
        })
    diff = {
        mode: [row["contrasts"][mode] for row in populations]
        for mode in MODES[1:]
    }
    raw_p = {mode: _two_sided_sign_flip_p(d) for mode, d in diff.items()}
    holm = _holm_adjust(raw_p)
    contrasts = {}
    for mode, sample in diff.items():
        n = len(sample)
        mean = sum(sample) / n
        sd = sqrt(sum((d - mean)**2 for d in sample) / (n - 1))
        margin = 3.182446305 * sd / sqrt(n)
        contrasts[mode] = {
            "per_population_difference_in_censored_lives": sample,
            "mean_difference_lives_per_population_of_72": mean,
            "exploratory_95pct_t_interval_lives": [mean-margin, mean+margin],
            "exact_sign_flip_two_sided_p": raw_p[mode],
            "exploratory_holm_adjusted_p": holm[mode],
            "causal_scope": "retention_intervention_with_downstream_cognitive_economy",
        }
    return {
        "schema": PROTOCOL, "source_sha": result["source_sha"],
        "schedule_sha256": result["schedule_sha256"],
        "original_sha256": result["sha256"], "total_lives": result["total_lives"],
        "populations": populations, "contrasts": contrasts,
        "interpretation": "exploratory_n4_no_automatic_scientific_GO",
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        schedule = p5a_schedule.manifest()
        genomes = p4a_validation.verify_frozen_genomes()
        print(json.dumps({
            "status": "NO_P5A_VALIDATION_WORLD_OPENED",
            "protocol": PROTOCOL, "schedule_sha256": schedule["sha256"],
            "world_keys": len(schedule["allocation"]),
            "genomes": len(genomes), "planned_lives": p5a_schedule.LIVES,
            "modes": list(MODES)}, sort_keys=True, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--run":
        destination = Path(sys.argv[2])
        if destination.exists():
            raise FileExistsError("P5a original evidence is immutable")
        outcome = run()
        destination.write_text(json.dumps(outcome, sort_keys=True, indent=2) + "\n")
        print(json.dumps(summarize(outcome), sort_keys=True, indent=2))
    else:
        raise SystemExit("usage: python -m i3.lab.p5a_screen --preflight | --run ORIGINAL.json")
