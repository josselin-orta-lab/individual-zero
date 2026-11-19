"""Stage8-E2 gamma-horizon BLOCK causal comparison: pure, UNVERIFIED summaries.

This module neither creates nor reads a life. Synthetic correctness tests
cannot certify a future prospective experiment. Future science must FIRST
rehash original archive and check all cohort, seed, genotype and World pins.
"""
from __future__ import annotations

import math

SCHEMA = "i3-stage8e-gamma-block-causal-did-design/v0"
POPULATIONS = 64
LIVES_G2_PER_ARM_AND_POPULATION = 144
HORIZON = 400
ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
ALPHA_TWO_SIDED = 0.025
T_CRITICAL_DF63 = 2.2962367715148795


def _numeric(v: object, *, lower: float = 0., upper: float = 400.) -> float:
    if type(v) not in (int,float) or not math.isfinite(v) or not lower <= v <= upper:
        raise ValueError("missing/foreign/nonfinite G2 bodily observation")
    return float(v)


def analyze_design_only(rows: list[dict]) -> dict:
    """Compute the single prospective DID, NEVER declare a scientific verdict.

    T[p] = (S_sham - M_sham) - (S_swap - M_swap), G2 lived-steps
    Four cells per population, each 24 v4 genomes x six paired F0 Worlds.
    Does NOT validate any source or life and MUST NOT be called as a
    scientific reducer before original-level audit and preregistration.
    """
    if (type(rows) is not list or len(rows) != POPULATIONS or
            any(type(r) is not dict or r.get("population") != p
                for p,r in enumerate(rows))):
        raise ValueError("exactly 64 uniquely indexed populations required")
    contrasts = []
    for r in rows:
        if (set(r) != {"population","mean_G2_steps","original_lives_by_arm"}
                or type(r["mean_G2_steps"]) is not dict
                or set(r["mean_G2_steps"]) != set(ARMS)
                or type(r["original_lives_by_arm"]) is not dict
                or set(r["original_lives_by_arm"]) != set(ARMS)
                or any(type(r["original_lives_by_arm"][arm]) is not int
                       or r["original_lives_by_arm"][arm] !=
                       LIVES_G2_PER_ARM_AND_POPULATION for arm in ARMS)):
            raise ValueError("four exact original-lived G2 arms required")
        a = {arm:_numeric(r["mean_G2_steps"][arm]) for arm in ARMS}
        contrasts.append(
            (a["S_sham"] - a["M_sham"]) -
            (a["S_swap"] - a["M_swap"]))
    avg = math.fsum(contrasts)/POPULATIONS
    sd = math.sqrt(math.fsum((z-avg)**2 for z in contrasts)/(POPULATIONS-1))
    margin = T_CRITICAL_DF63 * sd/math.sqrt(POPULATIONS)
    signal = sd > 0 and abs(avg) > margin
    return {
        "schema": SCHEMA,
        "status": "PURE_DESIGN_CALCULATION_NO_SCIENTIFIC_VERDICT",
        "population_units": POPULATIONS,
        "new_worlds": 0,
        "new_lives": 0,
        "g2_native_original_lives_required": 4*POPULATIONS*LIVES_G2_PER_ARM_AND_POPULATION,
        "primary_gamma_block_did_mean_steps": avg,
        "primary_gamma_block_did_population_sd_steps": sd,
        "primary_gamma_block_did_t_statistic":
            avg/(sd/math.sqrt(POPULATIONS)) if sd>0 else None,
        "two_sided_97_5_percent_interval_steps": [avg-margin,avg+margin],
        "design_threshold_two_sided_alpha": ALPHA_TWO_SIDED,
        "design_t_critical_df63": T_CRITICAL_DF63,
        "nominal_design_only_nonzero_compatible": bool(signal),
        "all_64_population_did": contrasts,
        "scientific_claim_authorized": False,
        "limits": ("NO_ORIGINAL_GZIP_CHECK_NO_PREEXPOSURE_CUSTODY;"
                   "NO_NEW_COHORT_OR_NATIVE_WORLD;"
                   "NULL_VARIANCE_NEVER_COUNTS_AS_SUCCESS;"
                   "GENE_BLOCK_NOT_GAMMA3_ONLY"),
    }
