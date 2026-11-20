"""Independent Stage8-E3C reducer from 64 aggregate population rows only.

No import of native, E3A/B/C streaming reader, no original-life replay.
No inferential statistics, no causal mediation or frozen primary revision.
"""
from __future__ import annotations
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

SCHEMA = "i3-stage8e3c-independent-original-timecourse-population-reduction/v0"
PRIOR = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
SOURCE_B = "c0709ad5ff8491538eab5fcb4f93bd854502d3aec9714878550426a88a179720"
G2_MANIFEST = "61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00"
ARMS = ("S_sham","M_sham","S_swap","M_swap")
WINDOWS = (("t001_020",1,20),("t021_100",21,100),("t101_200",101,200),("t201_400",201,400))
ACTIONS = ("se_deplacer","collecter","manger","boire","dormir","attendre","physical_inactivity")
REASONS = ("FUNDED","NO_PROCESSING_BUDGET","NO_FUNDED_SCORE","NO_FUNDED_MOTOR")
TOL = 2e-7


def near(a, b):
    return type(a) in (int,float) and type(b) in (int,float) and math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,abs_tol=TOL,rel_tol=1e-9)


def frac(n,d):
    return n/d if d else None


def equal_nullable(a,b):
    return a is None and b is None or near(a,b)


def verify_window(w):
    if (type(w) is not dict or type(w.get("observed_steps")) is not int or
            type(w.get("lives_at_risk_at_start")) is not int or
            type(w.get("lives_observed")) is not int or
            type(w.get("first_failures")) is not int or
            min(w["observed_steps"],w["lives_at_risk_at_start"],
                w["lives_observed"],w["first_failures"]) < 0 or
            w["first_failures"]>w["lives_at_risk_at_start"] or
            w["lives_at_risk_at_start"]>w["lives_observed"]):
        raise ValueError("invalid original time-window exposure/at-risk accounting")
    n=w["observed_steps"]
    if (set(w.get("actions",{}))!=set(ACTIONS) or
            set(w.get("reasons",{}))!=set(REASONS) or
            sum(w["actions"].values())!=n or sum(w["reasons"].values())!=n or
            any(type(v) is not int or v<0 for v in
                list(w["actions"].values())+list(w["reasons"].values()))):
        raise ValueError("time-window actions and native funding reasons not conserved")
    actual = {
        "no_processing_per_observed_step":frac(w["reasons"]["NO_PROCESSING_BUDGET"],n),
        "sleep_per_observed_step":frac(w["actions"]["dormir"],n),
        "movement_per_observed_step":frac(w["actions"]["se_deplacer"],n),
        "mean_predecision_energy":frac(w["predecision_energy_sum"],n),
        "mean_postdecision_energy":frac(w["postdecision_energy_sum"],n),
        "mean_water_end_step":frac(w["postdecision_water_sum"],n),
        "mean_food_end_step":frac(w["postdecision_food_sum"],n),
        "cognition_energy_paid_per_step":frac(
            w["decision_energy_paid"]+w["learning_energy_paid"],n),
        "first_failure_fraction_of_lives_reached_start":frac(
            w["first_failures"],w["lives_at_risk_at_start"]),
    }
    if any(not equal_nullable(w.get(k),v) for k,v in actual.items()):
        raise ValueError("time-window rate or cost does not match own original numerator")
    return actual


def check(full, source_sha):
    if (type(full) is not dict or
            full.get("status") != "READONLY_ALL_36864_ORIGINAL_G2_FIRST_ENERGY_GATE_TIME_COURSE_COMPLETE" or
            full.get("original_g2_compressed_and_decoded_sha256_rechecked") != 36864 or
            full.get("original_full_trace_and_funding_chains_rechecked") != 36864 or
            full.get("source_stage8e3b_sha256") != SOURCE_B or
            full.get("source_g2_manifest_sha256") != G2_MANIFEST or
            full.get("stage8e2_frozen_primary") != PRIOR or
            full.get("posthoc_only_no_p_values") is not True or
            full.get("new_native_lives") != 0 or
            full.get("populations") != 64 or
            full.get("arms") != list(ARMS) or
            type(full.get("population_rows")) is not list or
            len(full["population_rows"]) != 64 or
            full.get("windows") != [{"name":n,"first_t":lo,"last_t":hi}
                                   for n,lo,hi in WINDOWS]):
        raise ValueError("foreign, non-exhaustive or reinterpreted original science")
    rows=full["population_rows"]
    totals = {a:{"lives":0,"steps":0,"first_failures":0,"never_failures":0,
                 "recovery_lives":0,"funded_after_failure":0,
                 "death_after_first_failure":0,"censored_after_first_failure":0,
                 "windows":{n:{"steps":0,"first_failures":0,"at_risk":0} for n,_,_ in WINDOWS}}
              for a in ARMS}
    descriptors={}
    def register(name, values):
        if name in descriptors:raise ValueError("duplicate derived descriptor")
        valid=[v for v in values if v is not None]
        descriptors[name]={"population_units_available":len(valid),
                           "population_units_missing":64-len(valid),
                           "mean_equal_population_weight":math.fsum(valid)/len(valid) if valid else None}
    by_arm_values={a:{} for a in ARMS}
    for p,row in enumerate(rows):
        if type(row) is not dict or row.get("population") != p or set(row.get("by_arm",{}))!=set(ARMS):
            raise ValueError("missing or reordered population/arm")
        for a in ARMS:
            g=row["by_arm"][a]
            if (type(g) is not dict or g.get("original_lives")!=144
                    or type(g.get("lived_steps")) is not int
                    or not 144 <= g["lived_steps"] <= 57600):
                raise ValueError("original 144-life cell missing")
            first=g["first_failure_lives"]; never=g["never_failure_lives"]
            if (type(first) is not int or type(never) is not int or
                    first<0 or never<0 or first+never!=144 or
                    g["post_first_failure_recovery_lives"]>first or
                    g["dead_after_first_failure"]+g["censored_after_first_failure"]!=first or
                    not near(g["first_failure_per_life"],first/144) or
                    not equal_nullable(g["mean_first_failure_t_observed_only"],
                                       frac(g["first_failure_t_sum"],first)) or
                    not equal_nullable(g["mean_energy_pre_first_failure"],
                                       frac(g["first_failure_energy_sum"],first)) or
                    not equal_nullable(g["mean_vigilance_pre_first_failure"],
                                       frac(g["first_failure_vigilance_sum"],first)) or
                    g["pre10_observed_steps"]>10*first or
                    g["pre10_observed_steps"] != sum(g["pre10_actions"].values()) or
                    not equal_nullable(g["pre10_sleep_per_observed_step"],
                                       frac(g["pre10_actions"]["dormir"],g["pre10_observed_steps"])) or
                    not equal_nullable(g["pre10_mean_predecision_energy"],
                                       frac(g["pre10_energy_before_first_sum"],g["pre10_observed_steps"]))):
                raise ValueError("first gate existence, prior ten actions or physical allocation drifted")
            for k in ("first_failure_t_min","first_failure_t_max"):
                if not (g[k] is None and first==0 or
                        type(g[k]) is int and first>0 and 1 <= g[k] <= 400):
                    raise ValueError("invalid first-gate observed time support")
            if set(g["windows"])!={n for n,_,_ in WINDOWS}:
                raise ValueError("exposure window selected after observing results")
            totalsteps=totalfirst=0
            actions={x:0 for x in ACTIONS}
            reasons={x:0 for x in REASONS}
            for name,lo,hi in WINDOWS:
                w=g["windows"][name]
                verify_window(w)
                n=w["observed_steps"]
                if n > 144*(hi-lo+1):
                    raise ValueError("temporal window exceeds native life horizon")
                totalsteps+=n
                totalfirst+=w["first_failures"]
                for x in ACTIONS:actions[x]+=w["actions"][x]
                for x in REASONS:reasons[x]+=w["reasons"][x]
                dst=totals[a]["windows"][name]
                dst["steps"]+=n;dst["first_failures"]+=w["first_failures"]
                dst["at_risk"]+=w["lives_at_risk_at_start"]
            if (totalsteps!=g["lived_steps"] or totalfirst!=first or
                    actions!=g["original_motor_counts"] or
                    reasons!=g["original_gate_counts"] or
                    reasons["FUNDED"]+sum(reasons[x] for x in REASONS[1:]) != totalsteps or
                    actions["physical_inactivity"]!=sum(reasons[x] for x in REASONS[1:])):
                raise ValueError("archived life windows not conserved against original E3B gates")
            t=totals[a]
            t["lives"]+=144;t["steps"]+=totalsteps;t["first_failures"]+=first
            t["never_failures"]+=never
            t["recovery_lives"]+=g["post_first_failure_recovery_lives"]
            t["funded_after_failure"]+=g["post_first_failure_funded_action_count"]
            t["death_after_first_failure"]+=g["dead_after_first_failure"]
            t["censored_after_first_failure"]+=g["censored_after_first_failure"]
            metrics={
                "first_failure_per_life":g["first_failure_per_life"],
                "mean_first_failure_t_observed_only":g["mean_first_failure_t_observed_only"],
                "pre10_sleep_per_observed_step":g["pre10_sleep_per_observed_step"],
                "pre10_mean_predecision_energy":g["pre10_mean_predecision_energy"],
                "mean_remaining_observed_steps_after_first_failure":
                     g["mean_remaining_observed_steps_after_first_failure"],
            }
            for n,_,_ in WINDOWS:
                w=g["windows"][n]
                for k in ("no_processing_per_observed_step","sleep_per_observed_step",
                          "movement_per_observed_step","mean_predecision_energy",
                          "mean_water_end_step","cognition_energy_paid_per_step",
                          "first_failure_fraction_of_lives_reached_start"):
                    metrics[n+"__"+k]=w[k]
            for k,v in metrics.items():
                by_arm_values[a].setdefault(k,[]).append(v)
    # Each cohort has one observation per population/arm, never 9 million independent steps.
    for arm,metrics in by_arm_values.items():
        for k,values in metrics.items():
            if len(values)!=64 or any(v is not None and
                                       (type(v) not in (int,float) or not math.isfinite(v))
                                       for v in values):
                raise ValueError("invalid population quantity")
            register(k+"__"+arm,values)
    comparisons={}
    for metric in by_arm_values["S_sham"]:
        observations=[]
        for i in range(64):
            vals=[by_arm_values[a][metric][i] for a in ARMS]
            if any(x is None for x in vals):
                continue
            observations.append(vals[0]-vals[1]-vals[2]+vals[3])
        comparisons[metric]={
            "descriptive_population_units":len(observations),
            "not_available_units":64-len(observations),
            "mean_contrast":math.fsum(observations)/len(observations) if observations else None,
            "positive_negative_zero":[
                sum(x>0 for x in observations),sum(x<0 for x in observations),
                sum(x==0 for x in observations)],
        }
    if sum(totals[a]["lives"] for a in ARMS)!=36864:
        raise ValueError("not all original G2 lives enumerated")
    return {
        "schema":SCHEMA,
        "status":"INDEPENDENT_64_POPULATION_FIRST_GATE_WINDOWS_REPRODUCED_POSTHOC",
        "source_exact_original_report_sha256":source_sha,
        "population_units":64,"original_g2_lives_checked_prior_job":36864,
        "original_stage8e2_negative_primary_unchanged":PRIOR,
        "new_native_lives":0,"pure_descriptive_no_statistical_significance":True,
        "by_arm_original_counts":totals,
        "population_equal_weighted_metrics":descriptors,
        "four_arm_descriptive_interactions":comparisons,
        "limitations":["LATE_WINDOW_SURVIVOR_SELECTION",
                       "FIRST_GATE_CONDITIONAL_ON_OBSERVATION",
                       "POSTHOC_NOT_CAUSAL_MEDIATION","NO_RETRY"],
    }


def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: STAGE8E3C_FULL.json STAGE8E3C_SECOND.json")
    data=Path(sys.argv[1]).read_bytes()
    result=check(json.loads(data),sha256(data).hexdigest())
    with Path(sys.argv[2]).open("xb") as f:
        f.write(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
    print(json.dumps({"status":result["status"],"lives":result["original_g2_lives_checked_prior_job"],
                      "population_units":64,"new_lives":0},sort_keys=True))


if __name__=="__main__":
    main()
