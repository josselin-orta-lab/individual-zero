"""P5a prospective mechanism-screen allocation only; NEVER opens study worlds.

A bounded four-mode, same-G2 pilot on a new, disjoint validation slice.
Four original P3 populations remain the independent units; do not claim
larger genetic replication just because this allocates more lives.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import p2_ecologies, p3_schedule, p4a_schedule, p4b_schedule

PROTOCOL = "i3-p5a-paid-component-screen-v1"
SCHEMA = "i3-p5a-fresh-validation-schedule-v1"
MODES = ("normal", "discard_effects", "discard_values", "discard_replay")
ARMS = p3_schedule.ARMS
FAMILIES = p2_ecologies.FAMILIES
POPULATIONS = p3_schedule.POPULATIONS
GENOTYPES = p3_schedule.GENOTYPES
REPEATS = p3_schedule.REPEATS
HORIZON = p2_ecologies.HORIZON
INDEX_OFFSET = 48
LIFE_SEED_BASE = 360_000
LIVES = POPULATIONS * len(ARMS) * GENOTYPES * len(FAMILIES) * REPEATS * len(MODES)


def world_index(population: int, family: str, repeat: int) -> int:
    if (type(population) is not int or
        not 0 <= population < POPULATIONS or
        family not in FAMILIES or
        type(repeat) is not int or
        not 0 <= repeat < REPEATS):
        raise ValueError("invalid P5a prospective world coordinates")
    return INDEX_OFFSET + p3_schedule.validation_world_index(population, family, repeat)


def life_seed(population: int, family: str, repeat: int) -> int:
    return LIFE_SEED_BASE + world_index(population, family, repeat)


def manifest() -> dict:
    allocation = []
    for p in range(POPULATIONS):
        for family in FAMILIES:
            for repeat in range(REPEATS):
                idx = world_index(p, family, repeat)
                allocation.append({
                    "population": p, "family": family, "repeat": repeat,
                    "cohort": "validation", "index": idx,
                    "world_seed": p2_ecologies.COHORTS["validation"][idx],
                    "life_seed": life_seed(p, family, repeat),
                })
    if (len(allocation) != 24 or
        {a["index"] for a in allocation} != set(range(48, 72)) or
        len({a["world_seed"] for a in allocation}) != 24):
        raise RuntimeError("incorrect P5a allocation or cohort overlap")
    out = {
        "schema": SCHEMA, "protocol": PROTOCOL,
        "ecological_generator": p2_ecologies.PROTOCOL,
        "p4a_schedule_sha256": p4a_schedule.schedule_manifest()["sha256"],
        "p4b_schedule_sha256": p4b_schedule.manifest()["sha256"],
        "frozen_g2_file_sha256": p4a_schedule.G2_FILE_SHA256,
        "frozen_g2_canonical_sha256": p4a_schedule.G2_CANONICAL_SHA256,
        "families": list(FAMILIES), "arms": list(ARMS), "modes": list(MODES),
        "population_count": POPULATIONS, "genotypes_per_arm": GENOTYPES,
        "repeats_per_ecology": REPEATS, "horizon": HORIZON,
        "total_lives": LIVES, "allocation": allocation,
        "analysis_unit": "independent_P3_population_n4",
        "comparisons": [
            "normal_minus_discard_effects",
            "normal_minus_discard_values",
            "normal_minus_discard_replay",
        ],
        "confirmatory_power": "NONE_EXPLORATORY_SCREEN_ONLY",
        "multiplicity": "Holm_three_comparisons_exploratory",
        "historical_cohorts": "P3_P4A_P4B_NEVER_REOPEN",
        "reserve_cohort": "NEVER_OPEN",
        "normalization": "DO_NOT_EQUALIZE_REALIZED_COGNITIVE_CHARGES",
    }
    out["sha256"] = sha256(json.dumps(
        out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return out
