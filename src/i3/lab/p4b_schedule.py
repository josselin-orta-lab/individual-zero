"""P4b: independent prospective learning intervention with all 48 frozen G2.

This module lists keys only. No simulation, allocation reuse, world creation,
genome mutation or P4 reserve exposure is performed on import or preflight.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import p2_ecologies, p3_schedule, p4a_schedule

PROTOCOL = "i3-p4b-outcome-learning-v1"
SCHEMA = "i3-p4b-fresh-learning-allocation-v1"
MODES = ("normal", "shadow_discard")
ARMS = p3_schedule.ARMS
FAMILIES = p2_ecologies.FAMILIES
POPULATIONS = p3_schedule.POPULATIONS
GENOTYPES = p3_schedule.GENOTYPES
REPEATS = p3_schedule.REPEATS
HORIZON = p2_ecologies.HORIZON
INDEX_OFFSET = 24
LIFE_SEED_BASE = 260_000
LIVES = POPULATIONS * len(ARMS) * GENOTYPES * len(FAMILIES) * REPEATS * len(MODES)


def world_index(population: int, family: str, repeat: int) -> int:
    return INDEX_OFFSET + p3_schedule.validation_world_index(population, family, repeat)


def life_seed(population: int, family: str, repeat: int) -> int:
    return LIFE_SEED_BASE + world_index(population, family, repeat)


def manifest() -> dict:
    allocation = []
    for population in range(POPULATIONS):
        for family in FAMILIES:
            for repeat in range(REPEATS):
                index = world_index(population, family, repeat)
                allocation.append({
                    "population": population, "family": family, "repeat": repeat,
                    "cohort": "validation", "index": index,
                    "world_seed": p2_ecologies.COHORTS["validation"][index],
                    "life_seed": life_seed(population, family, repeat),
                })
    if len(allocation) != 24 or any(x["index"] < 24 or x["index"] >= 48
                                    for x in allocation):
        raise RuntimeError("P4b worlds overlap P4a or escape registered bounds")
    data = {
        "schema": SCHEMA, "protocol": PROTOCOL, "modes": list(MODES),
        "arms": list(ARMS), "ecologies": list(FAMILIES),
        "population_count": POPULATIONS, "genotypes_per_arm": GENOTYPES,
        "repeats": REPEATS, "horizon": HORIZON, "total_lives": LIVES,
        "p4a_schedule_sha256": p4a_schedule.schedule_manifest()["sha256"],
        "frozen_g2_file_sha256": p4a_schedule.G2_FILE_SHA256,
        "allocation": allocation,
        "physical_pricing": "same_i3_funded_v2_laws_both_modes",
        "intervention": "prepaid_shadow_outcome_computation_discard_learned_updates",
        "preserved": ["first_person_perception", "position_bookkeeping",
                      "map_and_place_beliefs", "innate_projection", "body_physics"],
        "not_equalized": ["realized_cognitive_costs", "memory_capacity_occupancy"],
        "individuality": "same_fixed_genome_distinct_world_and_life_seed_replicates",
        "selection_worlds": "NEVER_OPEN", "p4a_worlds": "NEVER_REOPEN",
        "p4_reserve": "NEVER_OPEN",
    }
    data["sha256"] = sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data
