"""Independent second E3D energy balance check against pinned E3C evidence.

This reducer deliberately imports neither E3D writer nor native physics.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

SOURCE_FULL = "c99011ff4dc2bc7d57eb4edea5e68fa3a273777d984ddae8073777c38e5e4e23"
SOURCE_SECOND = "b3ed0a35f4b51d9b77e8d34edb7f48b7d5858de05036018868da237ecffd2fd0"
CLOSED = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
ARMS = ("S_sham","M_sham","S_swap","M_swap")
WINDOWS = ("t001_020","t021_100","t101_200","t201_400")
METRICS = ("motor_debit_per_observed_step","cognition_paid_per_observed_step",
           "sleep_energy_gain_per_observed_step","sleep_energy_gain_per_sleep",
           "net_energy_change_per_observed_step","movement_per_observed_step",
           "sleep_fraction_observed_steps")


def near(a,b):
    return (type(a) in (int,float) and type(b) in (int,float)
            and math.isfinite(a) and math.isfinite(b)
            and math.isclose(a,b,abs_tol=1e-5,rel_tol=1e-9))


def nullable(a,b):
    return (a is None and b is None) or near(a,b)


def verify_pair(raw_window, published):
    """Recompute executed non-sleep motor, cognition and sleep gain independently."""
    n=raw_window["observed_steps"]
    actions=raw_window["actions"]
    if (n!=sum(actions.values()) or set(actions)!={
            "se_deplacer","collecter","manger","boire","attendre","dormir",
            "physical_inactivity"} or published["observed_steps"]!=n):
        raise ValueError("original exposure or native action total changed")
    motor=2*actions["se_deplacer"]+actions["collecter"]+(
        actions["manger"]+actions["boire"])/2+0.35*actions["attendre"]
    cognitive=raw_window["decision_energy_paid"]+raw_window["learning_energy_paid"]
    net=raw_window["postdecision_energy_sum"]-raw_window["predecision_energy_sum"]
    sleep_gain=motor+cognitive+net
    if sleep_gain < -0.0001 or sleep_gain>3*actions["dormir"]+0.0001:
        raise ValueError("sleep recovery impossible in native body v2")
    expected={
        "motor_energy_debit":motor,
        "decision_energy_paid":raw_window["decision_energy_paid"],
        "learning_energy_paid":raw_window["learning_energy_paid"],
        "cognition_energy_paid":cognitive,
        "realized_sleep_energy_gain":sleep_gain,
        "net_energy_change":net,
        "sleep_actions":actions["dormir"],
        "move_actions":actions["se_deplacer"],
        "no_processing_steps":raw_window["reasons"]["NO_PROCESSING_BUDGET"],
        "first_failure_events":raw_window["first_failures"],
        "at_risk_lives_at_start":raw_window["lives_at_risk_at_start"],
    }
    if any(not near(published[k],v) for k,v in expected.items()):
        raise ValueError("published energy balance differs from independently derived E3C")
    rates={
        "motor_debit_per_observed_step":motor/n if n else None,
        "cognition_paid_per_observed_step":cognitive/n if n else None,
        "sleep_energy_gain_per_observed_step":sleep_gain/n if n else None,
        "sleep_energy_gain_per_sleep":sleep_gain/actions["dormir"] if actions["dormir"] else None,
        "net_energy_change_per_observed_step":net/n if n else None,
        "movement_per_observed_step":actions["se_deplacer"]/n if n else None,
        "sleep_fraction_observed_steps":actions["dormir"]/n if n else None,
    }
    if any(not nullable(published.get(k),v) for k,v in rates.items()):
        raise ValueError("published rate disagrees with independent E3C numerator")
    return rates


def check(source, source_sha, e3c, second):
    if (type(source) is not dict or
            source.get("status") != "FULL_SOURCE_PINNED_ORIGINAL_G2_WINDOW_ENERGY_CONSERVATION_POSTHOC"
            or source.get("source_original_E3C_full_sha256")!=SOURCE_FULL
            or source.get("source_independent_E3C_second_sha256")!=SOURCE_SECOND
            or source.get("native_g2_originals_independently_rehashed_in_prior_E3C_job")!=36864
            or source.get("new_original_gzip_rehashed_in_this_step")!=0
            or source.get("new_native_lives")!=0
            or source.get("original_stage8e2_causal_primary_unchanged")!=CLOSED
            or source.get("posthoc_only_no_p_values_or_gamma_mediation") is not True
            or source.get("nominal_sleep_action_cost_applied_in_original_transition") is not False
            or source.get("population_units") != 64
            or source.get("arms")!=list(ARMS)
            or source.get("windows")!=list(WINDOWS)
            or len(source.get("population_rows",[]))!=64
            or len(source.get("descriptive_metrics",[]))!=len(WINDOWS)*len(METRICS)
            or e3c.get("stage8e2_frozen_primary")!=CLOSED
            or second.get("source_exact_original_report_sha256")!=SOURCE_FULL
            or second.get("original_stage8e2_negative_primary_unchanged")!=CLOSED):
        raise ValueError("foreign or incomplete E3D original-G2 source")
    rows=source["population_rows"]
    for pop in range(64):
        row, old=rows[pop],e3c["population_rows"][pop]
        if (row.get("population")!=pop or old.get("population")!=pop
                or set(row.get("by_arm",{}))!=set(ARMS)):
            raise ValueError("population unit absent or reordered")
        for arm in ARMS:
            if set(row["by_arm"][arm])!=set(WINDOWS):
                raise ValueError("native E3C window missing")
            for window in WINDOWS:
                verify_pair(old["by_arm"][arm]["windows"][window],
                            row["by_arm"][arm][window])
    seen=set()
    summaries={}
    for desc in source["descriptive_metrics"]:
        key=(desc.get("window"),desc.get("metric"))
        if key in seen or key[0] not in WINDOWS or key[1] not in METRICS:
            raise ValueError("metric selection after publication or duplicate")
        seen.add(key)
        arm_means={}
        nvals={}
        for arm in ARMS:
            v=[rows[p]["by_arm"][arm][key[0]][key[1]] for p in range(64)]
            valid=[x for x in v if x is not None]
            nvals[arm]=len(valid)
            arm_means[arm]=math.fsum(valid)/len(valid) if valid else None
        if any(not nullable(arm_means[arm],
                            desc["four_arm_equal_population_weight_means"][arm]) for arm in ARMS):
            raise ValueError("64 population-weighted mean altered")
        contrasts=[]
        for p in range(64):
            v=[rows[p]["by_arm"][arm][key[0]][key[1]] for arm in ARMS]
            if all(x is not None for x in v):
                contrasts.append(v[0]-v[1]-v[2]+v[3])
        m=math.fsum(contrasts)/len(contrasts) if contrasts else None
        if (desc.get("population_units")!=len(contrasts)
                or desc.get("not_observed_population_units")!=64-len(contrasts)
                or not nullable(m,desc.get("descriptive_mean_did"))
                or desc.get("positive_negative_zero_populations")!=[
                    sum(x>0 for x in contrasts),sum(x<0 for x in contrasts),
                    sum(x==0 for x in contrasts)]
                or len(desc.get("all_observed_population_did",[]))!=len(contrasts)
                or any(not near(x,y) for x,y in zip(
                    contrasts,desc["all_observed_population_did"]))):
            raise ValueError("descriptive factorial contrast was not population-reduced")
        summaries[key[0]+"__"+key[1]]={
            "population_units":len(contrasts),
            "population_contrast_mean":m,
            "four_arm_means":arm_means,
        }
    if len(seen)!=len(WINDOWS)*len(METRICS):
        raise ValueError("not all windows and metric permutations accounted")
    return {
        "schema":"i3-stage8e3d-independent-energy-accounting-reduction/v0",
        "status":"ALL_256_POPULATION_ARM_G2_WINDOWS_PHYSICALLY_BALANCED_INDEPENDENTLY",
        "source_e3d_report_sha256":source_sha,
        "source_e3c_original_sha256":SOURCE_FULL,
        "populations":64,
        "population_arm_windows_checked":64*4*4,
        "prior_original_gzip_verified":36864,
        "new_native_lives":0,
        "historical_stage8e2_negative_unchanged":CLOSED,
        "no_causal_gamma_mediation":True,
        "descriptive_metric_windows_recomputed":len(seen),
        "sums":summaries,
    }


def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: E3D_FULL.json E3C_FULL.json E3C_SECOND.json E3D_SECOND.json")
    data=Path(sys.argv[1]).read_bytes()
    e3c_data=Path(sys.argv[2]).read_bytes()
    ind_data=Path(sys.argv[3]).read_bytes()
    if (sha256(e3c_data).hexdigest()!=SOURCE_FULL or
            sha256(ind_data).hexdigest()!=SOURCE_SECOND):
        raise PermissionError("historical raw source hash changed")
    result=check(json.loads(data),sha256(data).hexdigest(),
                 json.loads(e3c_data),json.loads(ind_data))
    with Path(sys.argv[4]).open("xb") as f:
        f.write(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
    print(json.dumps({"status":result["status"],
                      "cells":result["population_arm_windows_checked"],
                      "new_native_lives":0},sort_keys=True))

if __name__=="__main__":
    main()
