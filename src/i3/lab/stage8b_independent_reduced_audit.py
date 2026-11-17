"""Independent read-only Stage8-B omnibus verification from sealed result JSON.

Does NOT import stage8b_ecology_interaction, stage8a_mean_persistence,
motor, World, mutation, nor score selection. This verifies the published
32x3 per-population ecological contrasts, their frozen primary Hotelling
T-squared/F(2,30) statistic and the source-bound scientific final record.

IMPORTANT LIMIT: revalidates the SEALED REDUCED ROWS and plan, not each
gzip original; record_sha_verified=1 is not original_lives_rehashed=23040.
A full original-level rehash audit must follow before claiming that.
"""
from __future__ import annotations

from hashlib import sha256
import argparse
import json
import math
from pathlib import Path

SOURCE_HEAD = "9f94d1c2c4170fd923ea0de68761bed2ac3d8377"
SCHEMA_PLAN = "i3-stage8b-ecology-interaction-science/v1"
SCHEMA_RESULT = "i3-stage8b-internal-ecology-omnibus-result/v1"
SCHEMA_FINAL = "i3-stage8b-scientific-original/v1"
SCHEMA_PRIMARY = "i3-stage8b-population-cluster-omnibus-result/v1"
PASS = "STAGE8B_SELECTION_BY_ECOLOGY_INTERACTION_F0"
NO = "STAGE8B_NO_INTERACTION_DEMONSTRATED_F0"
FAMILIES = ("stable", "depletion", "pulse")
N = 32
ALPHA = .025


def canonical(item: object) -> bytes:
    return json.dumps(item, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def hash_bytes(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _float_close(observed, expected) -> bool:
    return (type(observed) in (int, float) and
            math.isfinite(observed) and
            math.isclose(observed, expected, abs_tol=1e-10, rel_tol=0))


def reduce_omnibus(family_effects: list[dict]) -> dict:
    """Recompute two-dimensional population-cluster Hotelling from scratch."""
    if (type(family_effects) is not list or len(family_effects) != N or
            any(type(row) is not dict or set(row) != set(FAMILIES) or
                any(type(v) not in (int, float) or not math.isfinite(v)
                    for v in row.values()) for row in family_effects)):
        raise ValueError("exactly 32 complete finite ecological population profiles required")
    rows = [{f: float(row[f]) for f in FAMILIES} for row in family_effects]
    x = [r["depletion"] - r["stable"] for r in rows]
    y = [r["pulse"] - r["stable"] for r in rows]
    mx, my = math.fsum(x)/N, math.fsum(y)/N
    sxx = math.fsum((v-mx)**2 for v in x)/(N-1)
    syy = math.fsum((v-my)**2 for v in y)/(N-1)
    sxy = math.fsum((a-mx)*(b-my) for a,b in zip(x,y))/(N-1)
    determinant = sxx*syy - sxy*sxy
    valid = sxx > 0 and syy > 0 and determinant > max(sxx*syy*1e-12,1e-15)
    if valid:
        t2 = max(0., N*(syy*mx*mx-2*sxy*mx*my+sxx*my*my)/determinant)
        f = (N-2)*t2/(2*(N-1))
        p = (1+2*f/(N-2))**(-(N-2)/2)
    else:
        t2, f, p = None, None, 1.
    passed = valid and p < ALPHA
    return {
        "status": PASS if passed else NO,
        "primary_success": passed,
        "covariance_identifiable": valid,
        "hotelling_t_squared": t2,
        "f_df2_30": f,
        "p_value_two_sided_omnibus": p,
        "family_means": {family: math.fsum(r[family] for r in rows)/N
                         for family in FAMILIES},
        "positive_counts": {family: sum(r[family]>0 for r in rows)
                            for family in FAMILIES},
        "pair_contrast_means": [mx,my],
        "sample_covariance": [[sxx,sxy],[sxy,syy]],
        "effects_per_population": rows,
    }


def _verify_primary(primary: dict, independently: dict):
    if (type(primary) is not dict or
            primary.get("schema") != SCHEMA_PRIMARY or
            primary.get("n_populations") != 32 or
            primary.get("alpha_fixed") != ALPHA or
            primary.get("status") != independently["status"] or
            primary.get("primary_success") is not independently["primary_success"] or
            primary.get("covariance_identifiable") is not independently["covariance_identifiable"]):
        raise ValueError("frozen statistical decision differs from sealed 32 population contrasts")
    for k in ("hotelling_t_squared", "f_df2_30", "p_value_two_sided_omnibus"):
        want = independently[k]
        got = primary.get(k)
        if not (got is None and want is None or _float_close(got,want)):
            raise ValueError("published ecological omnibus statistic differs: "+k)
    for label,k in (
        ("family_mean_selection_advantage_steps","family_means"),
        ("family_positive_population_counts","positive_counts"),
    ):
        value = primary.get(label)
        if type(value) is not dict or set(value) != set(FAMILIES):
            raise ValueError("missing reported ecology family values")
        for family in FAMILIES:
            if (value[family] != independently[k][family] if k == "positive_counts"
                else not _float_close(value[family], independently[k][family])):
                raise ValueError("one ecological family measure mismatches originals summary")
    pairs = primary.get("two_family_contrasts_means", {})
    if (not _float_close(pairs.get("depletion_minus_stable"),
                          independently["pair_contrast_means"][0]) or
            not _float_close(pairs.get("pulse_minus_stable"),
                             independently["pair_contrast_means"][1])):
        raise ValueError("two-dimensional ecological primary vector changed")
    matrix = primary.get("sample_covariance_2_by_2")
    if (type(matrix) is not list or len(matrix) != 2 or
            any(type(row) is not list or len(row) != 2 for row in matrix) or
            any(not _float_close(matrix[i][j], independently["sample_covariance"][i][j])
                for i in range(2) for j in range(2))):
        raise ValueError("published population covariance differs")


def verify_reduced_science(plan_file: str, archive_root: str, result_file: str) -> dict:
    """Audit published JSON; all input files read only, no World ever opened."""
    plan = json.loads(Path(plan_file).read_bytes())
    observed_sha = plan.get("allocation_sha256")
    if (type(plan) is not dict or plan.get("schema") != SCHEMA_PLAN or
            plan.get("scientific_admission") is not True or
            plan.get("source_git_head") != SOURCE_HEAD or
            plan.get("planned_lives") != 23040 or
            plan.get("planned_worlds") != 576 or
            plan.get("planned_g2_holdout_worlds") != 192 or
            plan.get("preexposure_scientific_verdict") != "NOT_ISSUED" or
            hash_bytes(canonical({k:v for k,v in plan.items()
                                  if k!="allocation_sha256"})) != observed_sha):
        raise ValueError("prospective scientific plan is absent, foreign, or altered")
    method = plan.get("frozen_method", {})
    if (method.get("alpha_omnibus") != ALPHA or
            method.get("n_population_units") != N or
            method.get("df1") != 2 or method.get("df2") != 30 or
            method.get("primary") != "two_dimensional_population_level_Hotelling_T_squared" or
            method.get("G2_worlds_precommitted_and_blind_to_parent_fitness") is not True):
        raise ValueError("ecological primary test or heldout condition was altered")
    holdout = plan.get("g2_holdout_reserved_worlds")
    if (type(holdout) is not list or len(holdout) != 192 or
            hash_bytes(canonical(holdout)) != plan.get("g2_holdout_worlds_sha256") or
            {(r["population"],r["family"],r["repeat"]) for r in holdout} !=
            {(p,f,r) for p in range(N) for f in FAMILIES for r in (0,1)}):
        raise ValueError("the 192 precommitted G2 heldout coordinates were modified")
    root=Path(archive_root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("missing extracted immutable scientific originals")
    claim=json.loads((root/"CLAIM.json").read_bytes())
    if (claim.get("allocation_sha256")!=observed_sha or
            claim.get("source_sha")!=SOURCE_HEAD or
            claim.get("science") is not True or
            claim.get("status")!="CLAIMED_NO_RETRY_EVEN_IF_PARTIAL" or
            (root/"FAILURE.json").exists()):
        raise ValueError("scientific custody was never exclusively claimed or failed")
    final_bytes=(root/"SCIENCE_FINAL.json").read_bytes()
    final=json.loads(final_bytes)
    report=json.loads(Path(result_file).read_bytes())
    if (final.get("schema")!=SCHEMA_FINAL or
            final.get("plan_sha256")!=observed_sha or
            final.get("source_git_head")!=SOURCE_HEAD or
            final.get("frozen_method")!=method or
            final.get("original_native_lives")!=23040 or
            final.get("g2_holdout_worlds_sha256")!=plan["g2_holdout_worlds_sha256"] or
            report.get("schema")!=SCHEMA_RESULT or
            report.get("science_plan_sha256")!=observed_sha or
            report.get("source_git_head")!=SOURCE_HEAD or
            report.get("science_original_sha256")!=hash_bytes(final_bytes) or
            report.get("population_units")!=32 or
            report.get("original_native_lives")!=23040 or
            report.get("status")!=final.get("analysis",{}).get("status") or
            report.get("primary")!=final["analysis"]["primary"] or
            report.get("all_population_statistics")!=
            final["analysis"]["all_32_population_observed_statistics"]):
        raise ValueError("final scientific outcome is not source/plan/digest bound")
    population_rows=report["all_population_statistics"]
    if (type(population_rows) is not list or len(population_rows)!=32 or
            {row.get("population") for row in population_rows}!=set(range(32))):
        raise ValueError("not exactly 32 unique complete population summaries")
    rows=[]
    for p,row in enumerate(sorted(population_rows,key=lambda r:r["population"])):
        f=row.get("G2_families_descriptive",{})
        if type(f) is not dict or set(f)!=set(FAMILIES):
            raise ValueError("one F0 family was omitted")
        effects={family:f[family]["selected_minus_random_mean_steps"]
                 for family in FAMILIES}
        if not _float_close(math.fsum(effects.values())/3,
                            row["G2_selected_minus_random_steps"]):
            raise ValueError("reported family effects fail to sum to population G2 result")
        rows.append(effects)
    independent=reduce_omnibus(rows)
    _verify_primary(report["primary"],independent)
    if (report["status"]!=independent["status"] or
            final["analysis"]["status"]!=independent["status"] or
            report["primary"].get("effects_per_population")!=independent["effects_per_population"]):
        raise ValueError("published ecological interaction decision disagrees with reduced rows")
    return {
        "schema":"i3-stage8b-independent-readonly-published-population-audit/v1",
        "status":"READ_ONLY_REDUCED_ROWS_REPRODUCED",
        "scientific_status":independent["status"],
        "source_git_head":SOURCE_HEAD,
        "science_plan_sha256":observed_sha,
        "plan_and_final_original_sha_verified":True,
        "populations_reduced":32,
        "G2_holdout_world_coordinates_verified":192,
        "independent_omnibus_p":independent["p_value_two_sided_omnibus"],
        "family_means":independent["family_means"],
        "family_positive_counts":independent["positive_counts"],
        "original_lives_rehashed":0,
        "new_worlds":0,"new_lives":0,
        "limit":"REDUCED_ROWS_ONLY; NOT_23_040_INDEPENDENT_GZIP_REHASH",
    }


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("science_plan")
    ap.add_argument("scientific_original_root")
    ap.add_argument("science_result")
    args=ap.parse_args()
    print(json.dumps(verify_reduced_science(
        args.science_plan,args.scientific_original_root,args.science_result),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
