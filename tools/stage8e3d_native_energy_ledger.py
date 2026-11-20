"""Stage8-E3D, pure posthoc native ENERGY LEDGER from sealed Stage8-E3C.

Does NOT open any original gzip, import the I3 engine, run World/run_life,
select genomes or issue scientific causal significance. The 36,864 original
G2 gzip were completely cold-audited in E3C, and E3D accepts only exact
SHA-pinned E3C native-ledger and independent second receipts.

Native-body source-frozen energy accounting on each actually lived step:
  E_after - E_before = -paid_decision -paid_learning
                       -executed_non_sleep_motor +realized_sleep_gain

The actually executed native sleep branch does not debit the nominal
ACTION_COSTS['dormir']=0.25; it conditionally restores up to 3 energy.
A fabricated sleep action cost would violate the strict gain upper bound.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

SCHEMA = "i3-stage8e3d-source-exact-observed-energy-balance/v0"
SOURCE_E3C_SHA = "c99011ff4dc2bc7d57eb4edea5e68fa3a273777d984ddae8073777c38e5e4e23"
SOURCE_E3C_SECOND_SHA = "b3ed0a35f4b51d9b77e8d34edb7f48b7d5858de05036018868da237ecffd2fd0"
CLOSED = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
WINDOWS = ("t001_020", "t021_100", "t101_200", "t201_400")
ACTION_COSTS_ACTUALLY_APPLIED = {
    "se_deplacer": 2.0, "collecter": 1.0,
    "manger": 0.5, "boire": 0.5, "attendre": 0.35,
    "dormir": 0.0, "physical_inactivity": 0.0,
}
REASONS = ("FUNDED", "NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE", "NO_FUNDED_MOTOR")
METRICS = (
    "motor_debit_per_observed_step", "cognition_paid_per_observed_step",
    "sleep_energy_gain_per_observed_step", "sleep_energy_gain_per_sleep",
    "net_energy_change_per_observed_step", "movement_per_observed_step",
    "sleep_fraction_observed_steps",
)
TOL = 0.0001


def close(a, b):
    return (type(a) in (int, float) and type(b) in (int, float)
            and math.isfinite(a) and math.isfinite(b)
            and math.isclose(a, b, abs_tol=1e-6, rel_tol=1e-9))


def read_original_reports(full_path, independent_path):
    a, b = Path(full_path), Path(independent_path)
    if any(x.is_symlink() or not x.is_file() for x in (a, b)):
        raise PermissionError("source-exact historical E3C two receipts required")
    raw, second_raw = a.read_bytes(), b.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_E3C_SHA or sha256(second_raw).hexdigest() != SOURCE_E3C_SECOND_SHA:
        raise PermissionError("historical E3C source was modified")
    full, second = json.loads(raw), json.loads(second_raw)
    if (full.get("status") != "READONLY_ALL_36864_ORIGINAL_G2_FIRST_ENERGY_GATE_TIME_COURSE_COMPLETE"
            or full.get("stage8e2_frozen_primary") != CLOSED
            or full.get("original_g2_compressed_and_decoded_sha256_rechecked") != 36864
            or full.get("original_full_trace_and_funding_chains_rechecked") != 36864
            or full.get("new_native_lives") != 0
            or full.get("posthoc_only_no_p_values") is not True
            or full.get("populations") != 64
            or full.get("arms") != list(ARMS)
            or len(full.get("population_rows", [])) != 64
            or second.get("status") != "INDEPENDENT_64_POPULATION_FIRST_GATE_WINDOWS_REPRODUCED_POSTHOC"
            or second.get("original_stage8e2_negative_primary_unchanged") != CLOSED
            or second.get("source_exact_original_report_sha256") != SOURCE_E3C_SHA
            or second.get("original_g2_lives_checked_prior_job") != 36864
            or second.get("new_native_lives") != 0
            or second.get("population_units") != 64
            or second.get("pure_descriptive_no_statistical_significance") is not True):
        raise PermissionError("historical original-gzip and source-independent E3C audits not complete")
    return full


def read_window(window):
    if not isinstance(window, dict):
        raise ValueError("missing physical native window")
    actions = window.get("actions")
    reasons = window.get("reasons")
    steps = window.get("observed_steps")
    if (type(steps) is not int or steps < 0
            or type(actions) is not dict or set(actions) != set(ACTION_COSTS_ACTUALLY_APPLIED)
            or type(reasons) is not dict or set(reasons) != set(REASONS)
            or any(type(v) is not int or v < 0 for v in (*actions.values(), *reasons.values()))
            or sum(actions.values()) != steps or sum(reasons.values()) != steps
            or actions["physical_inactivity"] != sum(reasons[r] for r in REASONS if r != "FUNDED")):
        raise ValueError("original motor/funding count cannot be conserved")

    columns = ("decision_energy_paid", "learning_energy_paid",
               "predecision_energy_sum", "postdecision_energy_sum")
    if any(type(window.get(k)) not in (int, float)
           or not math.isfinite(window[k]) for k in columns):
        raise ValueError("foreign or nonfinite original energy ledger")
    decision = window["decision_energy_paid"]
    learning = window["learning_energy_paid"]
    if decision < 0 or learning < 0:
        raise ValueError("negative paid original cognition")

    motor = math.fsum(actions[a] * cost for a, cost in ACTION_COSTS_ACTUALLY_APPLIED.items())
    paid = decision + learning
    delta = window["postdecision_energy_sum"] - window["predecision_energy_sum"]
    # Pure algebra on actual physical native evidence; no model-specific replay.
    recovered = math.fsum((delta, paid, motor))
    sleep = actions["dormir"]
    if recovered < -TOL or recovered > 3.0 * sleep + TOL:
        raise ValueError("impossible physical energy conservation or fabricated sleep debit")
    if steps == 0 and any(abs(v) > TOL for v in (motor, paid, delta, recovered)):
        raise ValueError("invented physical energy outside observed life exposure")
    if (steps and (not close(paid / steps, window.get("cognition_energy_paid_per_step"))
                   or not close(window["predecision_energy_sum"] / steps,
                                window.get("mean_predecision_energy"))
                   or not close(window["postdecision_energy_sum"] / steps,
                                window.get("mean_postdecision_energy")))):
        raise ValueError("external energy results differ from exact E3C original rows")
    # The physical equation is exact from the source. No .25 energy debit occurs
    # for 'dormir', despite its nominal value in ACTION_COSTS.
    raw = {
        "observed_steps": steps,
        "motor_energy_debit": motor,
        "decision_energy_paid": decision,
        "learning_energy_paid": learning,
        "cognition_energy_paid": paid,
        "realized_sleep_energy_gain": max(0., recovered) if abs(recovered) < TOL else recovered,
        "net_energy_change": delta,
        "sleep_actions": sleep,
        "move_actions": actions["se_deplacer"],
        "no_processing_steps": reasons["NO_PROCESSING_BUDGET"],
        "first_failure_events": window["first_failures"],
        "at_risk_lives_at_start": window["lives_at_risk_at_start"],
    }
    raw.update({
        "motor_debit_per_observed_step": motor / steps if steps else None,
        "cognition_paid_per_observed_step": paid / steps if steps else None,
        "sleep_energy_gain_per_observed_step": recovered / steps if steps else None,
        "sleep_energy_gain_per_sleep": recovered / sleep if sleep else None,
        "net_energy_change_per_observed_step": delta / steps if steps else None,
        "movement_per_observed_step": actions["se_deplacer"] / steps if steps else None,
        "sleep_fraction_observed_steps": sleep / steps if steps else None,
    })
    return raw


def analyse(full, second):
    original = read_original_reports(full, second)
    rows = []
    for pop, row in enumerate(original["population_rows"]):
        if type(row) is not dict or row.get("population") != pop or set(row.get("by_arm",{})) != set(ARMS):
            raise ValueError("altered 64 population units")
        groups = {}
        for arm in ARMS:
            cell = row["by_arm"][arm]
            if cell.get("original_lives") != 144 or set(cell.get("windows",{})) != set(WINDOWS):
                raise ValueError("incomplete original 64-by-four-by-four native ledger")
            groups[arm] = {w:read_window(cell["windows"][w]) for w in WINDOWS}
            if (sum(groups[arm][w]["observed_steps"] for w in WINDOWS) != cell["lived_steps"]
                    or sum(groups[arm][w]["first_failure_events"] for w in WINDOWS)
                       != cell["first_failure_lives"]):
                raise ValueError("physical original exposure not fully represented")
            first = groups[arm]["t001_020"]
            if (first["observed_steps"] != 144 * 20 or first["no_processing_steps"] != 0
                    or first["first_failure_events"] != 0):
                raise ValueError("source early-life 20-step fully observed control failed")
        rows.append({"population": pop, "by_arm": groups})
    descriptions = []
    for window in WINDOWS:
        for metric in METRICS:
            means = {}
            vals = []
            for arm in ARMS:
                seq = [r["by_arm"][arm][window][metric] for r in rows]
                valid = [v for v in seq if v is not None]
                means[arm] = math.fsum(valid)/len(valid) if valid else None
            for r in rows:
                a = r["by_arm"]
                ordered = [a[arm][window][metric] for arm in ARMS]
                if any(v is None for v in ordered):
                    continue
                # Native 64-population 2x2 contrast, posthoc and descriptive ONLY.
                vals.append(ordered[0] - ordered[1] - ordered[2] + ordered[3])
            descriptions.append({
                "window":window, "metric":metric,
                "population_units":len(vals),
                "not_observed_population_units":64-len(vals),
                "four_arm_equal_population_weight_means":means,
                "descriptive_mean_did":math.fsum(vals)/len(vals) if vals else None,
                "positive_negative_zero_populations":[
                    sum(v>0 for v in vals),sum(v<0 for v in vals),sum(v==0 for v in vals)],
                "all_observed_population_did":vals,
            })
    return {
        "schema":SCHEMA,
        "status":"FULL_SOURCE_PINNED_ORIGINAL_G2_WINDOW_ENERGY_CONSERVATION_POSTHOC",
        "source_original_E3C_full_sha256":SOURCE_E3C_SHA,
        "source_independent_E3C_second_sha256":SOURCE_E3C_SECOND_SHA,
        "native_g2_originals_independently_rehashed_in_prior_E3C_job":36864,
        "new_original_gzip_rehashed_in_this_step":0,
        "population_units":64,
        "arms":list(ARMS),
        "windows":list(WINDOWS),
        "population_rows":rows,
        "descriptive_metrics":descriptions,
        "nominal_sleep_action_cost_applied_in_original_transition":False,
        "realized_sleep_gain_physics_limit":3.0,
        "new_native_lives":0,
        "original_stage8e2_causal_primary_unchanged":CLOSED,
        "posthoc_only_no_p_values_or_gamma_mediation":True,
        "limits":["ALREADY_ARCHIVED_E3C_ORIGINAL_SUMMARIES_NOT_NEW_GZIP_REHASH",
                  "LATE_WINDOW_SURVIVOR_SELECTION",
                  "NO_CAUSAL_GAMMA_TO_ENERGY_MEDIATION",
                  "PHYSICAL_ENERGY_IDENTITY_NOT_A_MOTOR_POLICY_COUNTERFACTUAL",
                  "NO_NEW_NATIVE_LIVES"],
    }


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: STAGE8E3C_FULL.json STAGE8E3C_SECOND.json STAGE8E3D_OUT.json")
    result=analyse(sys.argv[1],sys.argv[2])
    payload=json.dumps(result,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
    with Path(sys.argv[3]).open("xb") as f:f.write(payload)
    print(json.dumps({
        "status":result["status"],"population_units":64,
        "source_originals_prior_cold_audit":36864,"new_lives":0,
        "output_sha256":sha256(payload).hexdigest(),
    },sort_keys=True))


if __name__ == "__main__":
    main()
