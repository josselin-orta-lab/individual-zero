"""Read-only independent Stage8-E2 scientific Student-statistic verification.

Deliberately does NOT import the Stage8-E2 prospective envelope, the Stage8-E
design-only t-test helper, or the native data generator. Recomputes from the
64 complete published population G2 means AFTER the separately successful
cold 64512-original audit. Source Git and published outer plan are rechecked.
This is a statistical second check, not a second original gzip audit.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sys

SCHEMA = "i3-stage8e2-second-independent-population-primary-reduction/v0"
ENGINE_HEAD = "03faff4b9c194a5288b92e394f6a75cbe62cd095"
ENGINE_SHA = "e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6"
ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
N_POP = 64
LIVES_G2 = 36864
LIVES_TOTAL = 64512
CRIT = 2.2962367715148795
PASS = "STAGE8E2_CAUSAL_GAMMA_BLOCK_MODULATION_F0"
NO = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
SCIENCE_SCHEMA = "i3-stage8e2-new-prospective-science-over-frozen-technical-source/v0"
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def verify(plan_path: str, plan_sha_path: str, science_path: str) -> dict:
    """Recompute unweighted 64-population DID, not 36864-life pseudo-replication."""
    outer_raw = Path(plan_path).read_bytes()
    outer_sha = sha256(outer_raw).hexdigest()
    if (not HEX.fullmatch(outer_sha)
            or outer_sha != Path(plan_sha_path).read_text().strip()):
        raise ValueError("prospective science plan published digest is missing or altered")
    plan = json.loads(outer_raw)
    if (type(plan) is not dict or plan.get("schema") != SCIENCE_SCHEMA
            or _canonical(plan) != outer_raw
            or plan.get("scientific_admission") is not True
            or plan.get("preexposure_scientific_verdict") != "NOT_ISSUED"
            or plan.get("source_engine_head") != ENGINE_HEAD
            or plan.get("source_engine_sha256") != ENGINE_SHA
            or plan.get("planned_original_lives") != LIVES_TOTAL
            or plan.get("planned_g2_original_lives") != LIVES_G2
            or plan.get("population_units") != N_POP
            or plan.get("no_retry") is not True
            or plan.get("allocation_sha256") != sha256(_canonical({
                k: v for k, v in plan.items() if k != "allocation_sha256"
            })).hexdigest()):
        raise ValueError("not the frozen complete third-root scientific allocation")
    primary = plan.get("primary")
    if (type(primary) is not dict
            or primary.get("population_units") != 64
            or primary.get("four_arms") != list(ARMS)
            or primary.get("G2_lives_per_arm_population") != 144
            or primary.get("two_sided_alpha") != 0.025
            or primary.get("t_critical_df63") != CRIT
            or primary.get("primary_estimand") !=
               "(S_sham-M_sham)-(S_swap-M_swap)"
            or primary.get("no_retry") is not True
            or sha256(_canonical(primary)).hexdigest() != plan["primary_sha256"]):
        raise ValueError("primary changed from prospectively frozen test")
    result_bytes = Path(science_path).read_bytes()
    result = json.loads(result_bytes)
    if (type(result) is not dict
            or result.get("schema") != SCIENCE_SCHEMA + "/from-cold-originals"
            or result.get("status") not in (PASS, NO)
            or result.get("scientific_admission") is not True
            or result.get("science_plan_file_sha256") != outer_sha
            or result.get("science_allocation_sha256") != plan["allocation_sha256"]
            or result.get("source_engine_head") != ENGINE_HEAD
            or result.get("source_protocol_head") != plan["source_protocol_head"]
            or result.get("frozen_primary_sha256") != plan["primary_sha256"]
            or result.get("technical_evidence_sha256") !=
               plan["technical_evidence_sha256"]
            or result.get("original_native_lives_rehashed") != LIVES_TOTAL
            or result.get("G2_original_lives_scored") != LIVES_G2
            or result.get("native_mutations_reconstructed") != 6144
            or result.get("population_units") != N_POP
            or result.get("F0_only") is not True
            or result.get("joint_block_not_gamma3_alone") is not True
            or result.get("external_attestation") is not False
            or result.get("previous_technical_lives_excluded") is not True):
        raise ValueError("foreign scientific original-level population report")
    cold = result.get("cold_audit")
    if (type(cold) is not dict
            or cold.get("status") != "ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE"
            or cold.get("original_lives_rehashed") != 64512
            or cold.get("source_git_head") != ENGINE_HEAD
            or cold.get("source_files_sha256") != ENGINE_SHA
            or cold.get("allocation_sha256") !=
               plan["native_generator_plan"]["allocation_sha256"]
            or sha256(_canonical(cold)).hexdigest() != result["cold_originals_sha256"]):
        raise ValueError("original-level cold audit receipt absent or detached")
    rows = result.get("original_population_means")
    if type(rows) is not list or len(rows) != 64:
        raise ValueError("no 64 independent complete population observations")
    contrasts = []
    for p, row in enumerate(rows):
        if (type(row) is not dict or set(row) != {
                "population", "mean_G2_steps", "original_lives_by_arm"}
                or row["population"] != p
                or type(row["mean_G2_steps"]) is not dict
                or set(row["mean_G2_steps"]) != set(ARMS)
                or type(row["original_lives_by_arm"]) is not dict
                or set(row["original_lives_by_arm"]) != set(ARMS)):
            raise ValueError("not all G2 arms are present for each population")
        mean = row["mean_G2_steps"]
        if any(type(mean[a]) not in (int, float) or
               not math.isfinite(mean[a]) or
               not 1.0 <= mean[a] <= 400.0 for a in ARMS):
            raise ValueError("nonphysical or nonfinite independent population mean")
        if any(type(row["original_lives_by_arm"][a]) is not int or
               row["original_lives_by_arm"][a] != 144 for a in ARMS):
            raise ValueError("incorrect G2 original count or pseudo-replication")
        contrasts.append(float(mean["S_sham"] - mean["M_sham"] -
                               mean["S_swap"] + mean["M_swap"]))
    m = math.fsum(contrasts) / N_POP
    sd = math.sqrt(math.fsum((v-m)*(v-m) for v in contrasts)/(N_POP-1))
    if sd <= 0 or not math.isfinite(sd):
        raise ValueError("zero/nonfinite population variance: no scientific verdict")
    se = sd / math.sqrt(N_POP)
    lower = m - CRIT*se
    upper = m + CRIT*se
    t = m / se
    significant = lower > 0 or upper < 0
    expected_status = PASS if significant else NO
    published = result.get("primary")
    if (type(published) is not dict or published.get("population_units") != 64
            or published.get("design_threshold_two_sided_alpha") != 0.025
            or published.get("design_t_critical_df63") != CRIT
            or published.get("nominal_design_only_nonzero_compatible") is not significant
            or published.get("scientific_claim_authorized") is not False
            or type(published.get("all_64_population_did")) is not list
            or len(published["all_64_population_did"]) != 64):
        raise ValueError("calculation used another threshold or hidden population")
    numbers = (
        (m, published.get("primary_gamma_block_did_mean_steps")),
        (sd, published.get("primary_gamma_block_did_population_sd_steps")),
        (t, published.get("primary_gamma_block_did_t_statistic")),
        (lower, published.get("two_sided_97_5_percent_interval_steps", [None,None])[0]),
        (upper, published.get("two_sided_97_5_percent_interval_steps", [None,None])[1]),
    )
    if any(type(target) not in (float, int)
           or not math.isfinite(target)
           or not math.isclose(value, target, rel_tol=0, abs_tol=1e-10)
           for value, target in numbers):
        raise ValueError("Student statistic cannot be reconstructed from populations")
    if any(type(expected) not in (int, float) or not math.isclose(
              value, expected, abs_tol=1e-10, rel_tol=0)
           for value, expected in zip(contrasts, published["all_64_population_did"])):
        raise ValueError("published 64 contrasts differ from independent recomputation")
    if (result["status"] != expected_status or
            result.get("positive_population_DID") != sum(v > 0 for v in contrasts)
            or result.get("negative_population_DID") != sum(v < 0 for v in contrasts)
            or result.get("zero_population_DID") != sum(v == 0 for v in contrasts)):
        raise ValueError("scientific verdict or adverse population count was changed")
    return {
        "schema": SCHEMA,
        "status": "SCIENTIFIC_64_POPULATION_PRIMARY_INDEPENDENTLY_REPRODUCED",
        "scientific_status": expected_status,
        "source_engine_head": ENGINE_HEAD,
        "science_plan_file_sha256": outer_sha,
        "science_result_file_sha256": sha256(result_bytes).hexdigest(),
        "original_lives_independently_rehashed_prior_job": LIVES_TOTAL,
        "primary_population_units": N_POP,
        "primary_mean_steps": m,
        "primary_population_sd_steps": sd,
        "primary_t_statistic": t,
        "two_sided_97_5_percent_interval_steps": [lower, upper],
        "positive_population_units": sum(v > 0 for v in contrasts),
        "negative_population_units": sum(v < 0 for v in contrasts),
        "zero_population_units": sum(v == 0 for v in contrasts),
        "gamma3_alone_not_identified": True,
        "science_stage2_verdict_unchanged": "NOT_ISSUED",
    }


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: SCIENCE_PLAN.json SCIENCE_PLAN.sha256 SCIENCE_FINAL.json OUT_RECEIPT.json")
    _, plan, pin, result, output = sys.argv
    receipt = verify(plan, pin, result)
    with Path(output).open("xb") as fh:
        fh.write(_canonical(receipt))
    print(json.dumps({
        "status": receipt["status"],
        "scientific_status": receipt["scientific_status"],
        "primary_population_units": 64,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
