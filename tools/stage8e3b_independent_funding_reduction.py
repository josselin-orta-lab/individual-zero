"""Independent Stage8-E3B read-only 64-population native funding-reason audit.

This does not read original gzip, create a World or import the original audit
runner. It mechanically reconstructs all sums from the source rows, checking
every population against the earlier SHA-pinned Stage8-E3A original report.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

SCHEMA = "i3-stage8e3b-independent-original-funding-causes-reduction/v0"
CATEGORIES = ("FUNDED","NO_PROCESSING_BUDGET","NO_FUNDED_SCORE","NO_FUNDED_MOTOR")
FAILURES = CATEGORIES[1:]
ARMS = ("S_sham","M_sham","S_swap","M_swap")
E3A_SHA = "16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b"
E3A_SECOND_SHA = "16040d0da069ac25bb3be014729a129f1202d2f7812b13c688466013f45be027"
PRIMARY = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"


def close(a,b):
    return type(a) in (float,int) and type(b) in (float,int) and math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,abs_tol=1e-9)


def verify(source,old,e3b_sha):
    if (type(source) is not dict
        or source.get("status")!="READONLY_ALL_36864_ORIGINAL_FUNDING_REASONS_IDENTIFIED_POSTHOC"
        or source.get("original_stage8e3a_full_sha256")!=E3A_SHA
        or source.get("original_stage8e3a_second_sha256")!=E3A_SECOND_SHA
        or source.get("closed_stage8e2_primary")!=PRIMARY
        or source.get("native_originals_rehashed")!=36864
        or source.get("originals_body_and_funding_chains_verified")!=36864
        or source.get("native_lives_generated")!=0
        or source.get("exploratory_only") is not True
        or source.get("four_arms")!=list(ARMS)
        or type(source.get("per_population_arm")) is not list
        or len(source["per_population_arm"])!=64
        or len(old.get("population_rows",[]))!=64):
        raise ValueError("partial, foreign or scientific promotion of funding gate audit")
    rows=source["per_population_arm"]
    for p,row in enumerate(rows):
        if type(row) is not dict or set(row)!={"population","by_arm"} or row["population"]!=p:
            raise ValueError("missing original population")
        by=row["by_arm"]
        if type(by) is not dict or set(by)!=set(ARMS):
            raise ValueError("missing sham/swap arm")
        prior=old["population_rows"][p]
        if prior.get("population")!=p:
            raise ValueError("altered reference population order")
        for arm in ARMS:
            x=by[arm];was=prior["by_arm"][arm]
            if (type(x) is not dict or x.get("original_lives")!=144
                or type(x.get("lived_steps")) is not int
                or type(x.get("first20_observed_steps")) is not int
                or not 144<=x["lived_steps"]<=57600
                or not 144<=x["first20_observed_steps"]<=2880
                or x["first20_observed_steps"]>x["lived_steps"]
                or x["lived_steps"]!=was["lived_steps"]):
                raise ValueError("one life/exposure missing from historical original")
            nsteps=x["lived_steps"]
            nfirst=x["first20_observed_steps"]
            fail=0
            early_fail=0
            for name in CATEGORIES:
                count=x.get("original_count_"+name)
                rate=x.get("per_lived_step_"+name)
                early=x.get("early20_per_observed_step_"+name)
                if (type(count) is not int or not 0<=count<=nsteps
                    or not close(rate,count/nsteps)
                    or not close(early,float(early))
                    or not 0<=early<=1):
                    raise ValueError("original gate count/rate mismatch")
                for field in ("energy","vigilance"):
                    avg=x.get("predecision_"+field+"_mean_"+name)
                    low=x.get("predecision_"+field+"_under10_fraction_"+name)
                    if count:
                        if not (close(avg,float(avg)) and 0<=avg<=100 and
                                close(low,float(low)) and 0<=low<=1):
                            raise ValueError("invalid real-time budget observation")
                    elif avg is not None or low is not None:
                        raise ValueError("invented predecision budget for absent gate")
                if name!="FUNDED":
                    fail+=count
                    early_fail+=early*nfirst
            if sum(x["original_count_"+k] for k in CATEGORIES)!=nsteps:
                raise ValueError("not all lived motor decisions assigned to a native gate")
            if not close(fail/nsteps,was["action_physical_inactivity_per_step"]):
                raise ValueError("original idle motor count differs from Stage8-E3A")
            if not close(early_fail/nfirst,was["early20_action_physical_inactivity_per_step"]):
                raise ValueError("early original null motor count was changed")
            if not close(x["per_lived_step_FUNDED"],1-was["action_physical_inactivity_per_step"]):
                raise ValueError("funded motor mismatch")
    result={}
    expected=set()
    for name in CATEGORIES:
        for phase in ("per_lived_step","early20_per_observed_step"):
            metric=phase+"_"+name
            expected.add(metric)
            vals=[]
            for row in rows:
                a=row["by_arm"]
                vals.append(a["S_sham"][metric]-a["M_sham"][metric]-
                            a["S_swap"][metric]+a["M_swap"][metric])
            means={arm:math.fsum(row["by_arm"][arm][metric] for row in rows)/64
                   for arm in ARMS}
            result[metric]={"arm_means_equal_population_weight":means,
                            "DID_population_mean":math.fsum(vals)/64,
                            "S_swap_minus_S_sham":means["S_swap"]-means["S_sham"],
                            "M_swap_minus_M_sham":means["M_swap"]-means["M_sham"],
                            "positive_negative_zero_populations":[sum(v>0 for v in vals),
                                  sum(v<0 for v in vals),sum(v==0 for v in vals)]}
            entry=next((x for x in source.get("funding_reason_descriptions",[]) if x.get("metric")==metric),None)
            if (entry is None or entry.get("population_units")!=64 or
                 not close(entry.get("exploratory_did_population_mean"),result[metric]["DID_population_mean"]) or
                 any(not close(entry["arm_means_equal_population_weight"][a],means[a]) for a in ARMS) or
                 entry.get("positive_negative_zero_population_counts")!=result[metric]["positive_negative_zero_populations"] or
                 len(entry.get("all_64_population_descriptive_did",[]))!=64 or
                 any(not close(a,b) for a,b in zip(vals,entry["all_64_population_descriptive_did"]))):
                raise ValueError("source metric not independently reconstructible")
    if set(x.get("metric") for x in source.get("funding_reason_descriptions",[]))!=expected:
        raise ValueError("source funding metrics partially selected")
    # Fundamental fact: all physical None must be one of the three gates.
    old_did=next(x for x in old["exploratory_metric_descriptions"]
                 if x["metric"]=="action_physical_inactivity_per_step")["mean_exploratory_DID"]
    reason_did=math.fsum(result["per_lived_step_"+x]["DID_population_mean"] for x in FAILURES)
    if not close(reason_did,old_did) or not close(
            result["per_lived_step_FUNDED"]["DID_population_mean"],-reason_did):
        raise ValueError("funding gate decomposition does not exhaust observed inactivity")
    pooled={}
    for arm in ARMS:
        pooled[arm]={}
        for category in CATEGORIES:
            count=sum(row["by_arm"][arm]["original_count_"+category] for row in rows)
            body={}
            for field in ("energy","vigilance"):
                weighted=math.fsum(row["by_arm"][arm]["original_count_"+category]*
                        (row["by_arm"][arm]["predecision_"+field+"_mean_"+category] or 0.)
                        for row in rows)
                body[field]=weighted/count if count else None
            pooled[arm][category]={"total_original_steps":count,
                                    "pooled_predecision_means_descriptive_only":body}
    return {
       "schema":SCHEMA,
       "status":"ALL_64_POPULATIONS_NATIVE_FUNDING_GATE_CAUSES_INDEPENDENTLY_RECONSTRUCTED",
       "source_all_originals_report_sha256":e3b_sha,
       "historical_e3a_report_sha256":E3A_SHA,
       "g2_originals_rehashed_prior_job":36864,
       "population_units":64,
       "native_lives_generated":0,
       "historical_primary_unchanged":PRIMARY,
       "historical_e3a_inactivity_did":old_did,
       "reconstructed_inactivity_did_from_three_funding_causes":reason_did,
       "all_eight_funding_and_early_metrics":result,
       "pooled_predecision_energy_vigilance_by_gate_descriptive":pooled,
       "no_p_value_no_causal_mediation_inference":True,
    }


def main():
    if len(sys.argv)!=4:
        raise SystemExit("usage: E3B_FULL.json ORIGINAL_E3A_FULL.json INDEPENDENT.json")
    raw=Path(sys.argv[1]).read_bytes()
    old_raw=Path(sys.argv[2]).read_bytes()
    if sha256(old_raw).hexdigest()!=E3A_SHA:
        raise ValueError("original E3A report bytes drifted")
    report=verify(json.loads(raw),json.loads(old_raw),sha256(raw).hexdigest())
    with Path(sys.argv[3]).open("xb") as fh:
        fh.write(json.dumps(report,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
    print(json.dumps({"status":report["status"],"reconstructed_idle_DID":report[
        "reconstructed_inactivity_did_from_three_funding_causes"],
        "no_new_lives":report["native_lives_generated"]==0},sort_keys=True))


if __name__=="__main__":
    main()
