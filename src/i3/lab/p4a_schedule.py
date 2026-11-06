"""P4a prospective held-out allocation (pure; never constructs worlds).

This schedule must be independently SHA-locked before the first validation
life. It does not read selection outcomes or reserve-world conditions.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import p2_ecologies, p3_schedule

SCHEMA = "i3-p4a-heldout-schedule-v1"
PROTOCOL = "i3-p4a-g2-heldout-v1"
G2_FILE_SHA256 = "6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419"
G2_CANONICAL_SHA256 = "4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b"
P3_SELECTION_ORIGINAL_SHA256 = "e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e"
ARMS = p3_schedule.ARMS
FAMILIES = p2_ecologies.FAMILIES
POPULATIONS = p3_schedule.POPULATIONS
GENOTYPES = p3_schedule.GENOTYPES
REPEATS = p3_schedule.REPEATS
HORIZON = p2_ecologies.HORIZON
NEW_VALIDATION_LIFE_SEED_BASE = 160_000
LIVES = POPULATIONS * len(ARMS) * GENOTYPES * len(FAMILIES) * REPEATS


def validation_life_seed(population: int, family: str, repeat: int) -> int:
    index = p3_schedule.validation_world_index(population, family, repeat)
    return NEW_VALIDATION_LIFE_SEED_BASE + index


def schedule_manifest() -> dict:
    allocation = []
    for population in range(POPULATIONS):
        for family in FAMILIES:
            for repeat in range(REPEATS):
                index = p3_schedule.validation_world_index(population, family, repeat)
                allocation.append({
                    "population": population, "family": family, "repeat": repeat,
                    "cohort": "validation", "world_index": index,
                    "world_seed": p2_ecologies.COHORTS["validation"][index],
                    "life_seed": validation_life_seed(population, family, repeat),
                })
    assert len(allocation) == POPULATIONS * len(FAMILIES) * REPEATS == 24
    data = {
        "schema": SCHEMA, "protocol": PROTOCOL,
        "ecology_protocol": p2_ecologies.PROTOCOL,
        "p3_schedule_sha256": p3_schedule.schedule_manifest()["sha256"],
        "frozen_g2_file_sha256": G2_FILE_SHA256,
        "frozen_g2_canonical_sha256": G2_CANONICAL_SHA256,
        "original_p3_selection_sha256": P3_SELECTION_ORIGINAL_SHA256,
        "arms": list(ARMS), "populations": POPULATIONS,
        "genotypes_per_arm_population": GENOTYPES,
        "families": list(FAMILIES), "repeats": REPEATS,
        "horizon": HORIZON, "total_lives": LIVES,
        "allocation": allocation,
        "validation_only": True,
        "selection_cohort": "FORBIDDEN",
        "reserve_cohort": "FORBIDDEN",
        "analysis_unit": "independent_population",
        "primary_outcome": "G2_censored_fraction_selected_minus_random_parent",
        "allocation_policy": "all_48_previously_frozen_genomes_no_selection_or_mutation",
    }
    data["sha256"] = sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data
