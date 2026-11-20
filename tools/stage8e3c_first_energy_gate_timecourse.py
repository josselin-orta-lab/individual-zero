"""Stage8-E3C: first energy-gate time course in EXISTING G2 original lives.

Read-only original gzip SHA, full native trace and paid work chains, pinned
prior E3A/E3B population descriptors. No World, runner, offspring, intervention,
scientific significance or repeat of the CLOSED negative Stage8-E2 primary.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import tarfile

from tools import stage8e3a_readonly_motor_cost_audit as A
from tools import stage8e3b_readonly_funding_gates as B

SCHEMA = "i3-stage8e3c-original-first-energy-gate-time-course-readonly/v0"
SOURCE_E3B_SHA = "c0709ad5ff8491538eab5fcb4f93bd854502d3aec9714878550426a88a179720"
SOURCE_E3B_SECOND_SHA = "9ab20385db8529b2596d54d931a5107edf34b7cfb7287af8a805afda6e7e6f84"
WINDOWS = ((1, 20), (21, 100), (101, 200), (201, 400))
WINDOW_NAMES = ("t001_020", "t021_100", "t101_200", "t201_400")
REASONS = B.CATEGORIES
GATE = "NO_PROCESSING_BUDGET"
PRIOR = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
PRECEDING = 10


def read_previous(first, second):
    files = (Path(first), Path(second))
    if any(not f.is_file() or f.is_symlink() for f in files):
        raise PermissionError("archived Stage8-E3B full & independent evidence required")
    f, s = (file.read_bytes() for file in files)
    if sha256(f).hexdigest() != SOURCE_E3B_SHA or sha256(s).hexdigest() != SOURCE_E3B_SECOND_SHA:
        raise PermissionError("historical Stage8-E3B bytes changed")
    b, independent = json.loads(f), json.loads(s)
    if (b.get("status") != "READONLY_ALL_36864_ORIGINAL_FUNDING_REASONS_IDENTIFIED_POSTHOC"
            or b.get("native_originals_rehashed") != A.ORIGINALS
            or b.get("closed_stage8e2_primary") != PRIOR
            or b.get("native_lives_generated") != 0
            or len(b.get("per_population_arm", [])) != 64
            or independent.get("status") != "ALL_64_POPULATIONS_NATIVE_FUNDING_GATE_CAUSES_INDEPENDENTLY_RECONSTRUCTED"
            or independent.get("source_all_originals_report_sha256") != SOURCE_E3B_SHA
            or independent.get("population_units") != 64
            or independent.get("historical_primary_unchanged") != PRIOR):
        raise PermissionError("historical E3B gate and second audit not admissible")
    return b


def blank_window():
    return {"observed_steps": 0, "lives_observed": 0, "lives_at_risk_at_start": 0,
            "first_failures": 0, "actions": Counter(), "reasons": Counter(),
            "decision_energy_paid": 0., "learning_energy_paid": 0.,
            "decision_vigilance_paid": 0., "learning_vigilance_paid": 0.,
            "predecision_energy_sum": 0., "postdecision_energy_sum": 0.,
            "postdecision_water_sum": 0., "postdecision_food_sum": 0.}


def blank():
    return {"lives": 0, "lived_steps": 0, "reasons": Counter(),
            "actions": Counter(), "windows": {n: blank_window() for n in WINDOW_NAMES},
            "first_failure_lives": 0, "never_failure_lives": 0,
            "first_failure_t_sum": 0, "first_failure_t_min": None, "first_failure_t_max": None,
            "first_failure_energy_sum": 0., "first_failure_vigilance_sum": 0.,
            "pre10_observed_steps": 0, "pre10_actions": Counter(),
            "pre10_cognition_energy_paid": 0., "pre10_cognition_vigilance_paid": 0.,
            "pre10_energy_before_first_sum": 0.,
            "recovery_lives": 0, "funded_actions_after_first_failure": 0,
            "dead_after_first_failure": 0, "censored_after_first_failure": 0,
            "last_step_minus_first_failure_sum": 0}


def _phase_paid(step, phase, currency):
    part = step["funding_phases"][phase]["accounting"][currency]["paid"]
    if not A.num(part) or part < 0:
        raise ValueError("nonphysical original paid cognitive cost")
    return part


def per_life(life):
    """Pure time classification on a previously cryptographically verified life.

    Never infer counterfactual actions or fill post-mortem/nonobserved steps.
    """
    trace = life["trace"]
    steps = life["steps_lived"]
    if type(trace) is not list or type(steps) is not int or len(trace) != steps or not 1 <= steps <= 400:
        raise ValueError("missing real complete native first-person time series")
    first = None
    for idx, step in enumerate(trace):
        if type(step) is not dict or step.get("t") != idx+1:
            raise ValueError("disordered or absent original native time")
        info = step.get("info")
        if type(info) is not dict or info.get("funding") not in REASONS:
            raise ValueError("unknown original decision-funding reason")
        reason = info["funding"]
        if (step.get("action") is None) != (reason != "FUNDED"):
            raise ValueError("original motor status inconsistent with funding")
        if reason == GATE and first is None:
            first = idx+1
    result = blank()
    result["lives"] = 1
    result["lived_steps"] = steps
    if first is None:
        result["never_failure_lives"] = 1
    else:
        result["first_failure_lives"] = 1
        result["first_failure_t_sum"] = first
        result["first_failure_t_min"] = first
        result["first_failure_t_max"] = first
        result["last_step_minus_first_failure_sum"] = steps-first
        result["dead_after_first_failure"] = int(life["terminal"] == "dead")
        result["censored_after_first_failure"] = int(life["terminal"] == "censored")
        body_start = trace[first-1]["funding_phases"]["decision"]["body_before"]
        A._require_body(body_start)
        result["first_failure_energy_sum"] = body_start[0]
        result["first_failure_vigilance_sum"] = body_start[4]
        before = trace[max(0, first-1-PRECEDING):first-1]
        result["pre10_observed_steps"] = len(before)
        if before:
            result["pre10_energy_before_first_sum"] = sum(
                s["funding_phases"]["decision"]["body_before"][0] for s in before)
        for step in before:
            action = step["action"] if step["action"] is not None else "physical_inactivity"
            if action not in A.ACTIONS:
                raise ValueError("invalid preceding original motor choice")
            result["pre10_actions"][action] += 1
            result["pre10_cognition_energy_paid"] += sum(
                _phase_paid(step, ph, "energy") for ph in ("decision", "learning"))
            result["pre10_cognition_vigilance_paid"] += sum(
                _phase_paid(step, ph, "vigilance") for ph in ("decision", "learning"))
        post = trace[first:]
        funded_after = sum(step["info"]["funding"] == "FUNDED" for step in post)
        result["funded_actions_after_first_failure"] = funded_after
        result["recovery_lives"] = int(funded_after > 0)
    for (lo, hi), name in zip(WINDOWS, WINDOW_NAMES):
        if steps < lo:
            continue
        w = result["windows"][name]
        w["lives_observed"] = 1
        # At risk only if observed alive at interval start and not yet failed.
        w["lives_at_risk_at_start"] = int(first is None or first >= lo)
        w["first_failures"] = int(first is not None and lo <= first <= hi)
        for step in trace[lo-1:min(steps, hi)]:
            action = step["action"] if step["action"] is not None else "physical_inactivity"
            reason = step["info"]["funding"]
            if action not in A.ACTIONS or reason not in REASONS:
                raise ValueError("invalid first-person action/reason in fixed time interval")
            start = step["funding_phases"]["decision"]["body_before"]
            end = step["body"]
            A._require_body(start); A._require_body(end)
            w["observed_steps"] += 1
            w["actions"][action] += 1
            w["reasons"][reason] += 1
            w["predecision_energy_sum"] += start[0]
            w["postdecision_energy_sum"] += end[0]
            w["postdecision_water_sum"] += end[2]
            w["postdecision_food_sum"] += end[1]
            w["decision_energy_paid"] += _phase_paid(step, "decision", "energy")
            w["learning_energy_paid"] += _phase_paid(step, "learning", "energy")
            w["decision_vigilance_paid"] += _phase_paid(step, "decision", "vigilance")
            w["learning_vigilance_paid"] += _phase_paid(step, "learning", "vigilance")
        result["lived_steps"] = steps
        result["actions"].update(w["actions"])
        result["reasons"].update(w["reasons"])
    if (sum(result["actions"].values()) != steps or sum(result["reasons"].values()) != steps
            or sum(w["first_failures"] for w in result["windows"].values())
               != result["first_failure_lives"]):
        raise ValueError("native first-failure windows fail to partition observed life")
    return result


def combine(group, row):
    group["lives"] += row["lives"]
    group["lived_steps"] += row["lived_steps"]
    group["reasons"].update(row["reasons"])
    group["actions"].update(row["actions"])
    for name in WINDOW_NAMES:
        a, b = group["windows"][name], row["windows"][name]
        for key in a:
            if key in ("actions", "reasons"):
                a[key].update(b[key])
            else:
                a[key] += b[key]
    for key in ("first_failure_lives", "never_failure_lives", "first_failure_t_sum",
                "first_failure_energy_sum", "first_failure_vigilance_sum",
                "pre10_observed_steps", "pre10_cognition_energy_paid",
                "pre10_cognition_vigilance_paid", "pre10_energy_before_first_sum",
                "recovery_lives", "funded_actions_after_first_failure",
                "dead_after_first_failure", "censored_after_first_failure",
                "last_step_minus_first_failure_sum"):
        group[key] += row[key]
    for key in ("reasons", "actions", "pre10_actions"):
        if key == "pre10_actions":
            group[key].update(row[key])
    if row["first_failure_t_min"] is not None:
        group["first_failure_t_min"] = min(
            v for v in (group["first_failure_t_min"], row["first_failure_t_min"]) if v is not None)
        group["first_failure_t_max"] = max(
            v for v in (group["first_failure_t_max"], row["first_failure_t_max"]) if v is not None)


def _win_values(w):
    n = w["observed_steps"]
    d = {k:v for k,v in w.items() if k not in ("actions","reasons")}
    d["actions"] = {a:w["actions"][a] for a in A.ACTIONS}
    d["reasons"] = {r:w["reasons"][r] for r in REASONS}
    if (n != sum(d["actions"].values()) or n != sum(d["reasons"].values())
            or w["first_failures"] > w["lives_at_risk_at_start"]
            or w["lives_at_risk_at_start"] > w["lives_observed"]):
        raise ValueError("temporal exposure and at-risk denominators inconsistent")
    d["no_processing_per_observed_step"] = w["reasons"][GATE]/n if n else None
    d["sleep_per_observed_step"] = w["actions"]["dormir"]/n if n else None
    d["movement_per_observed_step"] = w["actions"]["se_deplacer"]/n if n else None
    d["mean_predecision_energy"] = w["predecision_energy_sum"]/n if n else None
    d["mean_postdecision_energy"] = w["postdecision_energy_sum"]/n if n else None
    d["mean_water_end_step"] = w["postdecision_water_sum"]/n if n else None
    d["mean_food_end_step"] = w["postdecision_food_sum"]/n if n else None
    d["cognition_energy_paid_per_step"] = (
        w["decision_energy_paid"]+w["learning_energy_paid"])/n if n else None
    d["first_failure_fraction_of_lives_reached_start"] = (
        w["first_failures"]/w["lives_at_risk_at_start"]
        if w["lives_at_risk_at_start"] else None)
    return d


def population_arm(group, old_e3b, old_e3a):
    if group["lives"] != 144 or group["lived_steps"] != old_e3b["lived_steps"]:
        raise ValueError("wrong G2 original life count or total lived steps")
    if group["lives"] != old_e3b["original_lives"]:
        raise ValueError("original population×arm cell missing")
    for r in REASONS:
        if group["reasons"][r] != old_e3b["original_count_"+r]:
            raise ValueError("E3C original native gate count differs from frozen E3B")
    for a in A.ACTIONS:
        rate = group["actions"][a]/group["lived_steps"]
        if not A.close(rate,old_e3a["action_"+a+"_per_step"]):
            raise ValueError("E3C original motor frequency differs from frozen E3A")
    if sum(group["reasons"].values()) != group["lived_steps"]:
        raise ValueError("incomplete original decision gates")
    fail = group["first_failure_lives"]
    if fail + group["never_failure_lives"] != group["lives"]:
        raise ValueError("missing first-gate existence or nonoccurrence")
    if (group["recovery_lives"] > fail or
            group["dead_after_first_failure"]+group["censored_after_first_failure"]!=fail):
        raise ValueError("incorrect first-gate terminal classification")
    w = {n:_win_values(group["windows"][n]) for n in WINDOW_NAMES}
    if (sum(w[n]["observed_steps"] for n in w) != group["lived_steps"]
            or sum(w[n]["first_failures"] for n in w) != fail):
        raise ValueError("first-gate temporal partition does not exhaust original exposure")
    # The first time window MUST reproduce the previously sealed E3A/E3B
    # early-20 independent descriptions, not only full-life totals.
    early=w["t001_020"]
    if not early["observed_steps"]:
        raise ValueError("missing original first twenty observed steps")
    for reason in REASONS:
        if not A.close(early["reasons"][reason]/early["observed_steps"],
                       old_e3b["early20_per_observed_step_"+reason]):
            raise ValueError("first-window funding reasons differ from sealed E3B")
    for action in A.ACTIONS:
        if not A.close(early["actions"][action]/early["observed_steps"],
                       old_e3a["early20_action_"+action+"_per_step"]):
            raise ValueError("first-window motor choices differ from sealed E3A")
    if not A.close(
        sum(w[n]["decision_energy_paid"] for n in w)/group["lived_steps"],
        old_e3a["decision_energy_paid_per_step"]
    ) or not A.close(
        sum(w[n]["learning_energy_paid"] for n in w)/group["lived_steps"],
        old_e3a["learning_energy_paid_per_step"]
    ):
        raise ValueError("E3C cognitive costs not reconstructible from sealed E3A")
    return {
        "original_lives": group["lives"],
        "lived_steps": group["lived_steps"],
        "first_failure_lives": fail, "never_failure_lives":group["never_failure_lives"],
        "first_failure_t_sum": group["first_failure_t_sum"],
        "first_failure_energy_sum": group["first_failure_energy_sum"],
        "first_failure_vigilance_sum": group["first_failure_vigilance_sum"],
        "last_step_minus_first_failure_sum": group["last_step_minus_first_failure_sum"],
        "original_gate_counts": {r:group["reasons"][r] for r in REASONS},
        "original_motor_counts": {a:group["actions"][a] for a in A.ACTIONS},
        "first_failure_per_life": fail/group["lives"],
        "mean_first_failure_t_observed_only": group["first_failure_t_sum"]/fail if fail else None,
        "first_failure_t_min":group["first_failure_t_min"],
        "first_failure_t_max":group["first_failure_t_max"],
        "mean_energy_pre_first_failure": group["first_failure_energy_sum"]/fail if fail else None,
        "mean_vigilance_pre_first_failure":group["first_failure_vigilance_sum"]/fail if fail else None,
        "pre10_observed_steps":group["pre10_observed_steps"],
        "pre10_actions": {a:group["pre10_actions"][a] for a in A.ACTIONS},
        "pre10_cognition_energy_paid":group["pre10_cognition_energy_paid"],
        "pre10_cognition_vigilance_paid":group["pre10_cognition_vigilance_paid"],
        "pre10_energy_before_first_sum":group["pre10_energy_before_first_sum"],
        "pre10_sleep_per_observed_step": (
            group["pre10_actions"]["dormir"]/group["pre10_observed_steps"]
            if group["pre10_observed_steps"] else None),
        "pre10_mean_predecision_energy":(
            group["pre10_energy_before_first_sum"]/group["pre10_observed_steps"]
            if group["pre10_observed_steps"] else None),
        "post_first_failure_funded_action_count":group["funded_actions_after_first_failure"],
        "post_first_failure_recovery_lives":group["recovery_lives"],
        "dead_after_first_failure":group["dead_after_first_failure"],
        "censored_after_first_failure":group["censored_after_first_failure"],
        "mean_remaining_observed_steps_after_first_failure":(
            group["last_step_minus_first_failure_sum"]/fail if fail else None),
        "windows":w,
    }


def analyse(metadata, originals, science, cold, independent, e3a_full, e3a_second, e3b_full, e3b_second):
    cases = A.read_manifest(metadata)
    A.verify_prior_science(science,cold,independent)
    old_a=B.read_known_e3a(e3a_full,e3a_second)
    old_b=read_previous(e3b_full,e3b_second)
    groups={(p,a):blank() for p in range(64) for a in A.ARMS}
    seen=set()
    packed_bytes=raw_bytes=0
    root=Path(originals)
    if not root.is_file() or root.is_symlink():
        raise PermissionError("full original G2 TAR required")
    with tarfile.open(root,"r|") as tar:
        for member in tar:
            name=member.name.lstrip("./")
            if not name.startswith("PHYSICAL_G2/G2/life-"):
                continue
            key=name.removeprefix("PHYSICAL_G2/G2/")
            if key not in cases or key in seen or not member.isfile() or member.size>A.MAX_PACKED:
                raise ValueError("unknown/duplicate original G2 life")
            packed=tar.extractfile(member).read()
            if len(packed)!=member.size or sha256(packed).hexdigest()!=cases[key]["sha256"]:
                raise ValueError("mutated original compressed SHA")
            raw=A.unpack_gzip(packed)
            if sha256(raw).hexdigest()!=cases[key]["uncompressed_sha256"]:
                raise ValueError("mutated original decoded SHA")
            obj=json.loads(raw)
            if (type(obj) is not dict or set(obj)!={"identity","life"}
                    or obj["identity"]!=cases[key]["identity"]):
                raise ValueError("alien original birth identity")
            ident,life=obj["identity"],obj["life"]
            A.summarize_one(ident,life)
            B.classify_one(life)
            row=per_life(life)
            combine(groups[ident["population"],ident["arm"]],row)
            packed_bytes+=len(packed);raw_bytes+=len(raw)
            seen.add(key)
    if len(seen)!=A.ORIGINALS or seen!=set(cases):
        raise ValueError("full original G2 archive incomplete")
    rows=[]
    for p in range(64):
        by_arm={}
        for arm in A.ARMS:
            if old_a["population_rows"][p]["population"]!=p or old_b["per_population_arm"][p]["population"]!=p:
                raise ValueError("historical population order shifted")
            by_arm[arm]=population_arm(
                groups[p,arm],
                old_b["per_population_arm"][p]["by_arm"][arm],
                old_a["population_rows"][p]["by_arm"][arm])
        rows.append({"population":p,"by_arm":by_arm})
    return {
        "schema":SCHEMA,
        "status":"READONLY_ALL_36864_ORIGINAL_G2_FIRST_ENERGY_GATE_TIME_COURSE_COMPLETE",
        "source_engine_head":A.ENGINE_HEAD,
        "source_engine_sha256":A.ENGINE_SHA,
        "science_original_run_id":A.RUN_ID,
        "source_stage8e3a_sha256":B.SOURCE_E3A_SHA,
        "source_stage8e3b_sha256":SOURCE_E3B_SHA,
        "source_g2_manifest_sha256":A.G2_MANIFEST_SHA,
        "source_negative_science_sha256":A.SCIENCE_RESULT_SHA,
        "original_g2_compressed_and_decoded_sha256_rechecked":len(seen),
        "original_full_trace_and_funding_chains_rechecked":len(seen),
        "original_gzip_bytes":packed_bytes,
        "original_decoded_bytes":raw_bytes,
        "populations":64,
        "population_unit_not_steps_or_lives":True,
        "arms":list(A.ARMS),
        "windows":[{"name":name,"first_t":lo,"last_t":hi}
                   for (lo,hi),name in zip(WINDOWS,WINDOW_NAMES)],
        "population_rows":rows,
        "new_native_lives":0,
        "posthoc_only_no_p_values":True,
        "stage8e2_frozen_primary":PRIOR,
        "limits":[
            "SURVIVOR_SELECTION_IN_LATE_WINDOWS",
            "FIRST_GATE_ONSET_OBSERVATIONAL_NOT_RANDOMIZED",
            "NO_GAMMA_SPECIFIC_CAUSAL_MEDIATION",
            "NEVER_OBSERVED_FIRST_FAILURE_IS_RIGHT_CENSORED_AT_DEATH_OR_HORIZON",
            "NO_NEW_LIVES_NO_RETRY",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    for n in ("metadata-tar","g2-tar","science-final","cold-audit","independent-statistics",
              "old-e3a-full","old-e3a-second","old-e3b-full","old-e3b-second","output"):
        p.add_argument("--"+n,required=True)
    v=vars(p.parse_args())
    result=analyse(*(v[k] for k in (
        "metadata_tar","g2_tar","science_final","cold_audit","independent_statistics",
        "old_e3a_full","old_e3a_second","old_e3b_full","old_e3b_second")))
    data=A.canonical(result)
    with Path(v["output"]).open("xb") as f:
        f.write(data)
    print(json.dumps({
        "status":result["status"],"originals":result["original_g2_compressed_and_decoded_sha256_rechecked"],
        "native_new_lives":0,"report_sha256":sha256(data).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
