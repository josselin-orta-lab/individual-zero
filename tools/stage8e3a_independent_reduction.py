"""Independent SECOND PASS over Stage8-E3A population-level original reduction.

Never imports the original-life reader or i3. Arithmetic and conservation
checks only; 64 populations remain the units. No new native actions.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

SCHEMA = "i3-stage8e3a-independent-population-motor-cost-reduction/v0"
ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
ACTIONS = ("se_deplacer", "collecter", "manger", "boire", "dormir", "attendre", "physical_inactivity")
PRIOR = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
G2_SHA = "61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00"


def check(source: dict, source_sha: str) -> dict:
    if (type(source) is not dict
            or source.get("status") != "READONLY_36864_ORIGINAL_G2_MOTOR_COST_AUDIT_COMPLETE_POSTHOC"
            or source.get("original_frozen_primary") != PRIOR
            or source.get("published_g2_manifest_sha256") != G2_SHA
            or source.get("source_science_run_id") != 44637950471
            or source.get("original_g2_gzip_full_compressed_and_raw_sha256_rechecked") != 36864
            or source.get("original_step_traces_and_paid_evidence_chains_recomputed") != 36864
            or source.get("native_lives_generated") != 0
            or source.get("scientific_new_cohort") is not False
            or source.get("exploratory_only_no_new_p_values_or_effect_proof") is not True
            or source.get("arms") != list(ARMS)
            or type(source.get("population_rows")) is not list
            or len(source["population_rows"]) != 64
            or type(source.get("exploratory_metric_descriptions")) is not list):
        raise ValueError("foreign/partial Stage8-E3A original-level reduction")
    rows = source["population_rows"]
    expected_metrics = None
    for p, row in enumerate(rows):
        if type(row) is not dict or set(row) != {"population", "by_arm"} or row["population"] != p:
            raise ValueError("population sequence/custody drift")
        arms = row["by_arm"]
        if type(arms) is not dict or set(arms) != set(ARMS):
            raise ValueError("missing sham or gamma-swap source")
        for arm in ARMS:
            a = arms[arm]
            if (type(a) is not dict or a.get("lives") != 144
                    or type(a.get("lived_steps")) is not int
                    or not 144 <= a["lived_steps"] <= 57600):
                raise ValueError("missing original life or impossible denominator")
            metrics = set(a) - {"lives", "lived_steps"}
            if expected_metrics is None:
                expected_metrics = metrics
            if metrics != expected_metrics:
                raise ValueError("arbitrary population-specific metric selection")
            if any(type(x) not in (float, int) or not math.isfinite(x) for k,x in a.items()
                   if k not in ("lives", "lived_steps")):
                raise ValueError("nonfinite original phenotype")
            if not math.isclose(a["mean_steps"], a["lived_steps"]/144, abs_tol=1e-9):
                raise ValueError("altered lived-step mean")
            if not math.isclose(a["dead_fraction"]+a["censored_fraction"],1., abs_tol=1e-9):
                raise ValueError("dead or censored body absent")
            for prefix in ("action_", "early20_action_"):
                total=sum(a[prefix+name+"_per_step"] for name in ACTIONS)
                if not math.isclose(total,1.,abs_tol=1e-9):
                    raise ValueError("native motor choices not normalized to lived exposure")
            for currency in ("energy","vigilance"):
                total = a[f"cognition_{currency}_paid_per_step"]
                phases = (a[f"decision_{currency}_paid_per_step"]+
                          a[f"learning_{currency}_paid_per_step"])
                if not math.isclose(total,phases,abs_tol=1e-8):
                    raise ValueError("cognitive funding phases do not sum")
            for name in ("death_zero_food_per_life", "death_zero_water_per_life",
                         "death_zero_integrity_per_life"):
                if not 0. <= a[name] <= 1.:
                    raise ValueError("nonphysical death-cause fraction")
    reports = source["exploratory_metric_descriptions"]
    if set(r.get("metric") for r in reports) != expected_metrics or len(reports)!=len(expected_metrics):
        raise ValueError("metric table was filtered after reading the results")
    summaries = {}
    for entry in reports:
        name = entry["metric"]
        vals = []
        for p, row in enumerate(rows):
            a = row["by_arm"]
            vals.append((a["S_sham"][name]-a["M_sham"][name])-
                        (a["S_swap"][name]-a["M_swap"][name]))
        mean=math.fsum(vals)/64
        arm_means={arm:math.fsum(row["by_arm"][arm][name] for row in rows)/64
                   for arm in ARMS}
        if (entry.get("population_unit") != 64
                or len(entry.get("all_64_population_descriptive_DID",[]))!=64
                or any(not math.isclose(t,u,abs_tol=1e-9)
                       for t,u in zip(vals,entry["all_64_population_descriptive_DID"]))
                or not math.isclose(mean,entry["mean_exploratory_DID"],abs_tol=1e-9)
                or any(not math.isclose(arm_means[arm],
                                       entry["arm_means_equal_population_weight"][arm],
                                       abs_tol=1e-9) for arm in ARMS)
                or entry["positive_negative_zero_DID_population_count"] != [
                    sum(v>0 for v in vals),sum(v<0 for v in vals),sum(v==0 for v in vals)]):
            raise ValueError("descriptive contrast does not follow 64 population records")
        summaries[name]={"arm_means_equal_population_weight":arm_means,
                          "exploratory_population_mean_DID":mean,
                          "positive_population_count":sum(v>0 for v in vals),
                          "negative_population_count":sum(v<0 for v in vals)}
    primary=summaries["mean_steps"]["exploratory_population_mean_DID"]
    if not math.isclose(primary,source["original_frozen_primary_mean_steps"],abs_tol=1e-9):
        raise ValueError("attempt to change Stage8-E2 negative primary")
    return {
        "schema":SCHEMA,
        "status":"ALL_64_POPULATION_EXPLORATORY_MOTOR_AND_COST_CONTRASTS_INDEPENDENTLY_RECOMPUTED",
        "source_readonly_report_sha256":source_sha,
        "original_g2_lives_verified_in_prior_job":36864,
        "native_lives_generated":0,
        "original_negative_primary_unchanged":PRIOR,
        "mean_primary_steps":primary,
        "population_unit_count":64,
        "metrics_recomputed":len(summaries),
        "motor_and_funding_descriptive_summary": {
            k:summaries[k] for k in (
                "action_se_deplacer_per_step","action_collecter_per_step",
                "action_manger_per_step","action_boire_per_step",
                "action_dormir_per_step","action_attendre_per_step",
                "action_physical_inactivity_per_step",
                "early20_action_se_deplacer_per_step",
                "early20_action_boire_per_step",
                "cognition_energy_paid_per_step",
                "cognition_vigilance_paid_per_step",
                "decision_energy_paid_per_step",
                "learning_energy_paid_per_step",
                "work_cycles_per_step","learning_updates_per_step",
                "body_water_below10_per_step",
                "body_food_below10_per_step",
                "death_zero_water_per_life","death_zero_food_per_life",
                "mean_steps",
            )},
        "posthoc_only_no_causal_mediation":True,
        "stage8e2_no_retry":True,
    }


def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: STAGE8E3A_FULL.json OUTPUT_SECOND_AUDIT.json")
    data=Path(sys.argv[1]).read_bytes()
    result=check(json.loads(data),sha256(data).hexdigest())
    with Path(sys.argv[2]).open("xb") as f:
        f.write(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
    print(json.dumps({"status":result["status"],
                      "population_units":result["population_unit_count"],
                      "original_primary_unchanged":result["original_negative_primary_unchanged"]},
                     sort_keys=True))

if __name__=="__main__":
    main()
