"""Prospective P5c heldout action-readout allocation; pure metadata only.

Opening *any* validation world requires separately merged preregistration.
The four original genetic populations are the independent units, not
the 1152 dependent lives. No P3/P4/P5a or reserve world reused.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import p2_ecologies, p3_schedule, p4a_schedule, p4b_schedule, p5a_schedule, p5b_schedule

PROTOCOL = "i3-p5c-paid-score-addends-heldout-v1"
SCHEMA = "i3-p5c-new-score-addend-allocation-v1"
MODES = ("normal", "discard_curiosity_bonus",
         "discard_risk_penalty", "discard_both_bonus_terms")
POPULATIONS = p3_schedule.POPULATIONS
ARMS = p3_schedule.ARMS
GENOTYPES = p3_schedule.GENOTYPES
FAMILIES = p2_ecologies.FAMILIES
REPEATS = p3_schedule.REPEATS
HORIZON = p2_ecologies.HORIZON
WORLD_OFFSET = 96
LIFE_SEED_BASE = 760_000
LIVES = POPULATIONS * len(ARMS) * GENOTYPES * len(FAMILIES) * REPEATS * len(MODES)
MECHANISTIC_WINDOW = 12


def world_index(population: int, family: str, repeat: int) -> int:
    if (type(population) is not int or
        not 0 <= population < POPULATIONS or family not in FAMILIES or
        type(repeat) is not int or not 0 <= repeat < REPEATS):
        raise ValueError("unregistered P5c validation key")
    return WORLD_OFFSET + p3_schedule.validation_world_index(population, family, repeat)


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
    if (len(allocation) != 24 or
        {row["index"] for row in allocation} != set(range(96, 120)) or
        len({row["world_seed"] for row in allocation}) != 24):
        raise RuntimeError("overlap or incomplete P5c study worlds")
    data = {
        "schema": SCHEMA, "protocol": PROTOCOL,
        "score_addend_modes": list(MODES), "families": list(FAMILIES),
        "genetic_arms": list(ARMS), "genotypes_per_arm": GENOTYPES,
        "populations": POPULATIONS, "repeats": REPEATS,
        "horizon": HORIZON, "lives": LIVES,
        "mechanistic_window": MECHANISTIC_WINDOW,
        "analysis_unit": "four_independent_P3_genetic_populations",
        "primary_endpoint": "fraction_censored_at_step_400",
        "mechanistic_secondary": "first_pre_action_change_in_shared_paid_candidate_score_and_bonus_components_with_matched_body_within_12_steps",
        "multiplicity": "three_predeclared_comparisons_Holm_exploratory",
        "sign_flip_floor": 0.125,
        "p5b_schedule_sha256": p5b_schedule.manifest()["sha256"],
        "p5a_schedule_sha256": p5a_schedule.manifest()["sha256"],
        "p4b_schedule_sha256": p4b_schedule.manifest()["sha256"],
        "p4a_schedule_sha256": p4a_schedule.schedule_manifest()["sha256"],
        "frozen_g2_file_sha256": p4a_schedule.G2_FILE_SHA256,
        "frozen_g2_canonical_sha256": p4a_schedule.G2_CANONICAL_SHA256,
        "exposure": allocation,
        "p3_p4a_p4b_p5a": "NEVER_OPEN",
        "reserve": "NEVER_OPEN",
        "work_parity": "IDENTICAL_INITIAL_PRICES_NOT_REALIZED_WORK_EQUALITY",
        "score_control": "FULL_PREDICTION_AND_BOTH_ADDENDS_COMPUTED_AND_PAID_THEN_ONE_OR_BOTH_MASKED",
        "scientific_status": "EXPLORATORY_NO_AUTOMATIC_GO",
    }
    data["sha256"] = sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data
