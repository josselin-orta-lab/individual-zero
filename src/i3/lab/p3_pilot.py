"""P3 minimal I3 lineage: mutation only, no inherited lived state.

One bounded prospective, equal-opportunity two-arm experiment. All fitness
comes from each individual's independent lifetime. Never call the validation
or reserve cohorts. No heuristics/oracle are part of parental selection.

Usage:
  PYTHONPATH=src python -m i3.lab.p3_pilot --preflight
  PYTHONPATH=src python -m i3.lab.p3_pilot --run RESULTS.json

The --run command requires an exact protocol SOURCE_SHA and SCHEDULE_SHA in
environment variables as additional launch locks; otherwise it refuses to run.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import subprocess
import sys

from i3.lab import p2_ecologies, p3_schedule
from i3.lab.p2_comparison_contract import compare_equal_opportunity, _settled_life
from i3.modules.genome import digest as genome_digest, generation_zero, mutate, validate
from i3.runtime.life import run_life

PROTOCOL = "i3-p3-mutation-pilot-v1"
ARMS = p3_schedule.ARMS
G0 = p3_schedule.GENOTYPES
HORIZON = p3_schedule.HORIZON
FITNESS_KEYS = ("censored_lives", "total_lived_steps")
MAX_SELECTION_LIVES = (len(ARMS) * p3_schedule.POPULATIONS *
                       p3_schedule.GENERATIONS * G0 * len(p2_ecologies.FAMILIES) *
                       p3_schedule.REPEATS)


def _head_sha() -> str:
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                            capture_output=True, text=True, check=True, timeout=5)
    return result.stdout.strip()


def _verify_launch() -> dict:
    actual = _head_sha()
    expected = os.environ.get("I3_P3_SOURCE_SHA", "")
    if len(expected) != 40 or actual != expected:
        raise RuntimeError("P3 source SHA not prospectively locked to this checkout")
    schedule = p3_schedule.schedule_manifest()
    if schedule["sha256"] != os.environ.get("I3_P3_SCHEDULE_SHA", ""):
        raise RuntimeError("P3 prospective opportunity schedule was not locked")
    if os.environ.get("I3_P3_APPROVED_PROTOCOL") != PROTOCOL:
        raise RuntimeError("P3 study protocol is not explicitly authorized")
    return schedule


def _rank(cohort: list[dict]) -> list[dict]:
    if len(cohort) != G0:
        raise ValueError("exactly six genomes per population required")
    for row in cohort:
        if row.get("fitness") is None:
            raise ValueError("parents require completed lifetime evidence")
    return sorted(cohort, key=lambda row: (
        -row["fitness"][0], -row["fitness"][1], row["slot"]))


def _parent_index(cohort: list[dict], population: int, generation: int,
                  offspring_slot: int, arm: str) -> int:
    """Use only completed persistence scores or uniform random parents."""
    if generation == 0 or arm not in ARMS:
        raise ValueError("generation > 0 and declared arm required")
    ranked = _rank(cohort)
    rng = random.Random(f"i3-p3-parent:{population}:{generation}:{offspring_slot}:{arm}")
    if arm == "random_parent":
        return rng.choice([r["slot"] for r in cohort])
    weights = list(range(len(ranked), 0, -1))
    return rng.choices([r["slot"] for r in ranked], weights=weights, k=1)[0]


def _offspring(cohort: list[dict], population: int,
               generation: int, arm: str) -> list[dict]:
    if len({row["slot"] for row in cohort}) != G0:
        raise ValueError("parent slots must be unique")
    prior = {row["slot"]: row for row in cohort}
    next_gen = []
    for slot in range(G0):
        parent_slot = _parent_index(cohort, population, generation, slot, arm)
        parent = prior[parent_slot]
        # Only closed, generic genome parameters are passed to mutation.
        validate(parent["genome"])
        child = mutate(parent["genome"],
                       p3_schedule.mutation_seed(population, generation, slot, arm),
                       scale=p3_schedule.MUTATION_SCALE)
        validate(child)
        next_gen.append({
            "slot": slot, "genome": child, "genome_sha256": genome_digest(child),
            "parent_slot": parent_slot,
            "parent_genome_sha256": genome_digest(parent["genome"]),
            "mutation_seed": p3_schedule.mutation_seed(population, generation, slot, arm),
            "fitness": None,
        })
    return next_gen


def _newborns(population: int) -> list[dict]:
    cohort = []
    for slot in range(G0):
        seed = p3_schedule.generation_zero_seed(population, slot)
        genome = generation_zero(seed)
        cohort.append({
            "slot": slot, "genome": genome, "genome_sha256": genome_digest(genome),
            "genome_seed": seed, "parent_slot": None, "fitness": None,
        })
    return cohort


def _life_summary(outcome: dict, *, family: str, world_index: int,
                  population: int, generation: int, arm: str, slot: int) -> dict:
    _settled_life(outcome)
    return {
        "population": population, "generation": generation,
        "arm": arm, "slot": slot, "family": family,
        "selection_world_index": world_index,
        "world_sha256": outcome["manifest"]["world_sha256"],
        "source_sha256": outcome["manifest"]["source"]["sha256"],
        "life_seed": outcome["life_seed"],
        "genome_sha256": outcome["genome"],
        "manifest_id": outcome["manifest_id"],
        "evidence_head": outcome["evidence_head"],
        "terminal": outcome["terminal"],
        "death_causes": outcome["death_causes"],
        "steps_lived": outcome["steps_lived"],
        "censored": outcome["terminal"] == "censored",
        "paid": {c: outcome["cognitive_accounting"]["totals"][c]["paid"]
                 for c in ("energy", "vigilance")},
        "inactive_steps": outcome["cognitive_accounting"]["inactive_steps"],
        "learning_updates": outcome["cognitive_accounting"]["learning_updates"],
        "replays_executed": outcome["cognitive_accounting"]["replays_executed"],
    }


def _evaluate_cohort(population: int, generation: int, arm: str,
                     cohort: list[dict], frozen_worlds: list) -> list[dict]:
    """The same physical worlds are reused across all slots in both arms."""
    for individual in cohort:
        outcomes = []
        for family, repeat, index, spec, life_seed in frozen_worlds:
            result = run_life(individual["genome"], spec, life_seed, HORIZON,
                              protocol=PROTOCOL)
            outcomes.append(_life_summary(
                result, family=family, world_index=index, population=population,
                generation=generation, arm=arm, slot=individual["slot"]))
        individual["fitness"] = (
            sum(r["censored"] for r in outcomes),
            sum(r["steps_lived"] for r in outcomes),
        )
        individual["lives"] = outcomes
    return cohort


def run() -> dict:
    schedule = _verify_launch()
    populations = []
    total_lives = 0
    for p in range(p3_schedule.POPULATIONS):
        arms = {arm: _newborns(p) for arm in ARMS}
        generations = []
        for g in range(p3_schedule.GENERATIONS):
            # Expose selection worlds *only* after the exact source/protocol
            # have passed all launch checks.
            frozen = []
            for family in p2_ecologies.FAMILIES:
                for repeat in range(p3_schedule.REPEATS):
                    index = p3_schedule.selection_world_index(p, g, family, repeat)
                    spec = p2_ecologies.world_for(family, "selection", index)
                    frozen.append((
                        family, repeat, index, spec,
                        p3_schedule.life_seed(p, g, family, repeat)))
            evaluated = {}
            for arm in ARMS:
                evaluated[arm] = _evaluate_cohort(p, g, arm, arms[arm], frozen)
                total_lives += sum(len(row["lives"]) for row in evaluated[arm])
            # Explicit pairing of the initial world/seed/body/source between
            # both arms. Actual cognitive spend is recorded, not equalized.
            for slot in range(G0):
                for family, repeat, index, spec, life_seed in frozen:
                    a = evaluated[ARMS[0]][slot]["lives"][
                        p2_ecologies.FAMILIES.index(family) * p3_schedule.REPEATS + repeat]
                    b = evaluated[ARMS[1]][slot]["lives"][
                        p2_ecologies.FAMILIES.index(family) * p3_schedule.REPEATS + repeat]
                    if (a["world_sha256"], a["life_seed"]) != (
                            b["world_sha256"], b["life_seed"]):
                        raise RuntimeError("world/seed opportunity mismatch")
                    if a["source_sha256"] != b["source_sha256"]:
                        raise RuntimeError("source budget equality violated")
            generations.append({
                "generation": g,
                "world_indices": [x[2] for x in frozen],
                "arms": {arm: [
                    {k: v for k, v in row.items() if k != "genome"}
                    for row in evaluated[arm]]
                    for arm in ARMS},
            })
            if g < p3_schedule.GENERATIONS - 1:
                arms = {arm: _offspring(evaluated[arm], p, g + 1, arm)
                        for arm in ARMS}
        populations.append({"population": p, "generations": generations})
    if total_lives != MAX_SELECTION_LIVES:
        raise RuntimeError("a life is missing from the predeclared pilot")
    raw = {
        "schema": PROTOCOL, "source_sha": _head_sha(),
        "schedule_sha256": schedule["sha256"],
        "status": "selection_only_validation_NOT_RUN",
        "total_lives": total_lives,
        "max_selection_ticks": MAX_SELECTION_LIVES * HORIZON,
        "populations": populations,
    }
    raw["sha256"] = sha256(json.dumps(raw, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()
    return raw


def summarize(result: dict) -> dict:
    summary = {"protocol": PROTOCOL, "source_sha": result["source_sha"],
               "schedule_sha256": result["schedule_sha256"],
               "selection_lives": result["total_lives"],
               "population_results": []}
    for pop in result["populations"]:
        lines = []
        for gen in pop["generations"]:
            by_arm = {}
            for arm, individuals in gen["arms"].items():
                lives = [r for individual in individuals for r in individual["lives"]]
                by_arm[arm] = {
                    "survivors": sum(r["censored"] for r in lives),
                    "deaths": sum(not r["censored"] for r in lives),
                    "lived_steps": sum(r["steps_lived"] for r in lives),
                    "paid_energy": round(sum(r["paid"]["energy"] for r in lives), 4),
                    "paid_vigilance": round(sum(r["paid"]["vigilance"] for r in lives), 4),
                    "inactive_steps": sum(r["inactive_steps"] for r in lives),
                }
            lines.append({"generation": gen["generation"], "arms": by_arm})
        summary["population_results"].append({"population": pop["population"],
                                              "generations": lines})
    return summary


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        manifest = p3_schedule.schedule_manifest()
        print(json.dumps({"protocol": PROTOCOL, "status": "NO_SELECTION_RUN",
                          "world_keys": len(manifest["selection_keys"]),
                          "validation_unopened": len(manifest["validation_keys_unopened"]),
                          "manifest_sha256": manifest["sha256"],
                          "maximum_selection_lives": MAX_SELECTION_LIVES}, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--run":
        output = Path(sys.argv[2])
        if output.exists():
            raise FileExistsError("do not overwrite prospective evidence")
        outcome = run()
        output.write_text(json.dumps(outcome, sort_keys=True, indent=2) + "\n")
        print(json.dumps(summarize(outcome), sort_keys=True, indent=2))
    else:
        raise SystemExit("usage: python -m i3.lab.p3_pilot --preflight | --run OUTPUT.json")
