"""P3 prospective schedule only. This module DOES NOT execute any individual.

Compile the immutable opportunity matrix before P3 selection begins.
Selection and validation populations use distinct P2 cohorts; reserve cannot
be opened by this module. Exposes no world snapshots or outcome-dependent keys.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab.p2_ecologies import COHORTS, FAMILIES, HORIZON, PROTOCOL as ECOLOGY_VERSION

PROTOCOL = "i3-p3-opportunity-schedule-v1"
POPULATIONS = 4
GENOTYPES = 6
GENERATIONS = 3
REPEATS = 2
ARMS = ("selected", "random_parent")
MUTATION_SCALE = 0.1
FITNESS = ("censored_lives", "total_lived_steps", "ascending_slot_tiebreak")


def generation_zero_seed(population: int, slot: int) -> int:
    if not (type(population) is int and 0 <= population < POPULATIONS and
            type(slot) is int and 0 <= slot < GENOTYPES):
        raise ValueError("invalid generation-zero identity")
    # Both arms begin with identical independent genotypes in each population.
    return 100_000 + population * GENOTYPES + slot


def selection_world_index(population: int, generation: int,
                          family: str, repeat: int) -> int:
    if not (type(population) is int and 0 <= population < POPULATIONS and
            type(generation) is int and 0 <= generation < GENERATIONS and
            family in FAMILIES and type(repeat) is int and
            0 <= repeat < REPEATS):
        raise ValueError("invalid prospective selection coordinates")
    return (population * GENERATIONS * len(FAMILIES) * REPEATS +
            generation * len(FAMILIES) * REPEATS +
            FAMILIES.index(family) * REPEATS + repeat)


def validation_world_index(population: int, family: str, repeat: int) -> int:
    if not (type(population) is int and 0 <= population < POPULATIONS and
            family in FAMILIES and type(repeat) is int and 0 <= repeat < REPEATS):
        raise ValueError("invalid prospective validation coordinates")
    return population * len(FAMILIES) * REPEATS + FAMILIES.index(family) * REPEATS + repeat


def life_seed(population: int, generation: int, family: str, repeat: int) -> int:
    return 60_000 + selection_world_index(population, generation, family, repeat)


def mutation_seed(population: int, generation: int, slot: int, arm: str) -> int:
    if not (type(population) is int and 0 <= population < POPULATIONS and
            type(generation) is int and 1 <= generation < GENERATIONS and
            type(slot) is int and 0 <= slot < GENOTYPES and arm in ARMS):
        raise ValueError("invalid mutation identity")
    return (300_000 + population * 10_000 + generation * 100 +
            slot * len(ARMS) + ARMS.index(arm))


def schedule_manifest() -> dict:
    selection = []
    for p in range(POPULATIONS):
        for g in range(GENERATIONS):
            for family in FAMILIES:
                for repeat in range(REPEATS):
                    index = selection_world_index(p, g, family, repeat)
                    selection.append({
                        "population": p, "generation": g,
                        "family": family, "repeat": repeat,
                        "cohort": "selection", "index": index,
                        "seed": COHORTS["selection"][index],
                        "life_seed": life_seed(p, g, family, repeat),
                    })
    validation = []
    for p in range(POPULATIONS):
        for family in FAMILIES:
            for repeat in range(REPEATS):
                index = validation_world_index(p, family, repeat)
                validation.append({
                    "population": p, "family": family, "repeat": repeat,
                    "cohort": "validation", "index": index,
                    "seed": COHORTS["validation"][index],
                })
    g0 = [[generation_zero_seed(p, slot) for slot in range(GENOTYPES)]
          for p in range(POPULATIONS)]
    data = {
        "schema": PROTOCOL, "ecology_version": ECOLOGY_VERSION,
        "generations": GENERATIONS, "populations": POPULATIONS,
        "genotypes_per_population": GENOTYPES,
        "repeats_per_ecology": REPEATS,
        "evolution_families": list(FAMILIES), "horizon": HORIZON,
        "arms": list(ARMS), "mutation_scale": MUTATION_SCALE,
        "fitness": list(FITNESS),
        "generation_zero_seeds": g0,
        "selection_keys": selection, "validation_keys_unopened": validation,
        "selection_cohort_policy": "NO_RUN_BEFORE_PREREGISTRATION",
        "validation_policy": "NEVER_SELECT_OR_RETUNE_FROM_VALIDATION",
        "reserve_policy": "P4_ONLY_NOT_INSTANTIATED",
    }
    data["sha256"] = sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data
