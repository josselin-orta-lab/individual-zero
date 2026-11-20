"""Stage8-E3B: independent read-only native funding gate diagnostic.

No native generation. Reopens exactly 36,864 Stage8-E2 G2 original gzip with
the Stage8-E3A original SHA and complete first-person/body/cognition proof;
classifies every physical None by the *archived* first-person info.funding,
not by inferred or counterfactual actions. No new scientific hypothesis test.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import tarfile

from tools import stage8e3a_readonly_motor_cost_audit as A

SCHEMA = "i3-stage8e3b-posthoc-funded-decision-gates-readonly/v0"
SOURCE_E3A_SHA = "16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b"
SOURCE_E3A_SECOND_SHA = "16040d0da069ac25bb3be014729a129f1202d2f7812b13c688466013f45be027"
CATEGORIES = ("FUNDED", "NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE", "NO_FUNDED_MOTOR")
FAILURES = CATEGORIES[1:]
EARLY_TICK = 20
N = 36864


def read_known_e3a(older_full, older_second):
    paths = (Path(older_full), Path(older_second))
    if any(x.is_symlink() or not x.is_file() for x in paths):
        raise PermissionError("historical Stage8-E3A original-level and independent receipts missing")
    raw = paths[0].read_bytes()
    second_raw = paths[1].read_bytes()
    if (sha256(raw).hexdigest() != SOURCE_E3A_SHA
            or sha256(second_raw).hexdigest() != SOURCE_E3A_SECOND_SHA):
        raise PermissionError("Stage8-E3A original-level reference report changed")
    full, second = json.loads(raw), json.loads(second_raw)
    if (full.get("status") != "READONLY_36864_ORIGINAL_G2_MOTOR_COST_AUDIT_COMPLETE_POSTHOC"
            or full.get("native_lives_generated") != 0
            or full.get("original_g2_gzip_full_compressed_and_raw_sha256_rechecked") != N
            or full.get("published_g2_manifest_sha256") != A.G2_MANIFEST_SHA
            or len(full.get("population_rows", [])) != 64
            or second.get("status") != "ALL_64_POPULATION_EXPLORATORY_MOTOR_AND_COST_CONTRASTS_INDEPENDENTLY_RECOMPUTED"
            or second.get("source_readonly_report_sha256") != SOURCE_E3A_SHA
            or second.get("population_unit_count") != 64):
        raise PermissionError("historical Stage8-E3A source was not an all-original audit")
    return full


def _make():
    return {"lives":0, "steps":0, "early_steps":0, "funding":Counter(),
            "early_funding":Counter(), "start_energy_by_funding":Counter(),
            "start_vigilance_by_funding":Counter(),
            "under10_energy_by_funding":Counter(),
            "under10_vigilance_by_funding":Counter()}


def classify_one(life):
    """Precondition: original life separately SHA/trace verified by E3A."""
    trace=life["trace"]
    out=_make()
    out["lives"]=1
    out["steps"]=len(trace)
    for i,step in enumerate(trace):
        if type(step) is not dict or type(step.get("info")) is not dict:
            raise ValueError("missing original first-person decision info")
        info=step["info"]
        category=info.get("funding")
        if category not in CATEGORIES:
            raise ValueError("unknown native funding explanation")
        action=step["action"]
        if (action is None) == (category == "FUNDED"):
            raise ValueError("null action incompatible with native funding gate")
        if info.get("option") != step.get("option"):
            raise ValueError("native decision option no longer matches original trace")
        phases=step.get("funding_phases")
        if type(phases) is not dict or type(phases.get("decision")) is not dict:
            raise ValueError("missing charged original decision phase")
        decision=phases["decision"]
        b=decision.get("body_before")
        if type(b) is not list or len(b)!=5 or any(
                type(x) not in (int,float) or not math.isfinite(x)
                or not 0 <= x <= 100 for x in b):
            raise ValueError("missing real decision-time energy or vigilance")
        if category=="NO_PROCESSING_BUDGET":
            work=decision.get("work")
            if (type(work) is not dict or set(work)!=set(A.WORK)
                or any(work[k]!=0 for k in A.WORK)):
                raise ValueError("unfunded processing request cannot be reported as paid work")
        out["funding"][category]+=1
        if i < EARLY_TICK:
            out["early_funding"][category]+=1
            out["early_steps"]+=1
        out["start_energy_by_funding"][category]+=b[0]
        out["start_vigilance_by_funding"][category]+=b[4]
        out["under10_energy_by_funding"][category]+=int(b[0] < 10)
        out["under10_vigilance_by_funding"][category]+=int(b[4] < 10)
    if (sum(out["funding"].values()) != out["steps"]
            or sum(out["early_funding"].values()) != out["early_steps"]
            or out["funding"]["FUNDED"] != sum(
                life["actions"].get(a,0) for a in A.ACTIONS if a!="physical_inactivity")
            or sum(out["funding"][reason] for reason in FAILURES) !=
                   life["actions"].get("physical_inactivity",0)):
        raise ValueError("native original motor and funding reason conservation failed")
    return out


def add(group, one):
    for k in ("lives","steps","early_steps"):
        group[k]+=one[k]
    for k in ("funding","early_funding","start_energy_by_funding",
              "start_vigilance_by_funding","under10_energy_by_funding",
              "under10_vigilance_by_funding"):
        group[k].update(one[k])


def summarize_group(group, old):
    lives, steps, first=group["lives"],group["steps"],group["early_steps"]
    if lives != A.ARM_LIVES or not steps or not first:
        raise ValueError("incomplete population/arm G2 original life exposure")
    if (steps!=old["lived_steps"]
            or not A.close(old["action_physical_inactivity_per_step"],
                  sum(group["funding"][name] for name in FAILURES)/steps)
            or not A.close(old["early20_action_physical_inactivity_per_step"],
                  sum(group["early_funding"][name] for name in FAILURES)/first)):
        raise ValueError("new motive classification cannot reconstruct published Stage8-E3A inactivity")
    d={"original_lives":lives,"lived_steps":steps,"first20_observed_steps":first}
    for name in CATEGORIES:
        n=group["funding"][name]; early=group["early_funding"][name]
        d["original_count_"+name]=n
        d["per_lived_step_"+name]=n/steps
        d["early20_per_observed_step_"+name]=early/first
        d["predecision_energy_mean_"+name]=(group["start_energy_by_funding"][name]/n if n else None)
        d["predecision_vigilance_mean_"+name]=(group["start_vigilance_by_funding"][name]/n if n else None)
        d["predecision_energy_under10_fraction_"+name]=(group["under10_energy_by_funding"][name]/n if n else None)
        d["predecision_vigilance_under10_fraction_"+name]=(group["under10_vigilance_by_funding"][name]/n if n else None)
    if not A.close(sum(d["per_lived_step_"+name] for name in CATEGORIES),1.):
        raise ValueError("not all first-person decision outcomes counted")
    return d


def analyse(metadata_tar, g2_tar, science_final, cold_audit, independent_statistics, old_full, old_second):
    cases=A.read_manifest(metadata_tar)
    A.verify_prior_science(science_final,cold_audit,independent_statistics)
    old=read_known_e3a(old_full,old_second)
    acc={(p,arm):_make() for p in range(64) for arm in A.ARMS}
    seen=set()
    packed_bytes=raw_bytes=0
    archive=Path(g2_tar)
    if archive.is_symlink() or not archive.is_file():
        raise PermissionError("original complete G2 archive missing")
    with tarfile.open(archive,"r|") as tar:
        for item in tar:
            name=item.name.lstrip("./")
            if not name.startswith("PHYSICAL_G2/G2/life-"):
                continue
            rel=name.removeprefix("PHYSICAL_G2/G2/")
            if rel not in cases or rel in seen or not item.isfile() or item.size>A.MAX_PACKED:
                raise ValueError("unexpected / duplicated G2 original")
            packed=tar.extractfile(item).read()
            if len(packed)!=item.size or sha256(packed).hexdigest()!=cases[rel]["sha256"]:
                raise ValueError("tampered original compressed bytes")
            raw=A.unpack_gzip(packed)
            if sha256(raw).hexdigest()!=cases[rel]["uncompressed_sha256"]:
                raise ValueError("tampered original uncompressed bytes")
            body=json.loads(raw)
            if type(body) is not dict or set(body)!={"identity","life"} or body["identity"] != cases[rel]["identity"]:
                raise ValueError("foreign native first-person identity")
            idn=body["identity"];life=body["life"]
            # E3A independent of the engine recomputes both chained histories,
            # confirms original physics, funding and motor counts for this life.
            A.summarize_one(idn,life)
            one=classify_one(life)
            add(acc[idn["population"],idn["arm"]],one)
            seen.add(rel)
            packed_bytes+=len(packed);raw_bytes+=len(raw)
    if seen != set(cases):
        raise ValueError("originals missing; no partial result may be reduced")
    rows=[]
    for p in range(64):
        by_arm={}
        for arm in A.ARMS:
            group=summarize_group(acc[p,arm],old["population_rows"][p]["by_arm"][arm])
            by_arm[arm]=group
        rows.append({"population":p,"by_arm":by_arm})
    descriptions=[]
    for part in ("per_lived_step", "early20_per_observed_step"):
        for reason in CATEGORIES:
            key=part+"_"+reason
            vals=[]
            for row in rows:
                a=row["by_arm"];v={arm:a[arm][key] for arm in A.ARMS}
                vals.append(v["S_sham"]-v["M_sham"]-v["S_swap"]+v["M_swap"])
            descriptions.append({
                "metric":key,"population_units":64,
                "arm_means_equal_population_weight":{
                    arm:math.fsum(row["by_arm"][arm][key] for row in rows)/64
                    for arm in A.ARMS},
                "exploratory_did_population_mean":math.fsum(vals)/64,
                "positive_negative_zero_population_counts":[
                    sum(x>0 for x in vals),sum(x<0 for x in vals),sum(x==0 for x in vals)],
                "all_64_population_descriptive_did":vals,
            })
    return {
        "schema":SCHEMA,
        "status":"READONLY_ALL_36864_ORIGINAL_FUNDING_REASONS_IDENTIFIED_POSTHOC",
        "original_science_result_sha256":A.SCIENCE_RESULT_SHA,
        "original_g2_manifest_sha256":A.G2_MANIFEST_SHA,
        "original_stage8e3a_full_sha256":SOURCE_E3A_SHA,
        "original_stage8e3a_second_sha256":SOURCE_E3A_SECOND_SHA,
        "native_originals_rehashed":len(seen),
        "originals_body_and_funding_chains_verified":len(seen),
        "original_gzip_bytes":packed_bytes,"original_json_bytes":raw_bytes,
        "populations":64,"four_arms":list(A.ARMS),
        "lives_per_population_arm":A.ARM_LIVES,
        "native_lives_generated":0,
        "closed_stage8e2_primary":"STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0",
        "per_population_arm":rows,
        "funding_reason_descriptions":descriptions,
        "exploratory_only":True,
        "not_identifiable":["NO_MEDIATION_CAUSALITY","NO_SPECIFIC_GAMMA_GENE_EFFECT",
                            "NO_INFERENTIAL_SIGNIFICANCE","NO_SELECTION_FREE_SURVIVAL_NORMALIZATION",
                            "NO_SUBREASON_OF_MOTOR_CONTROL_REJECTION_WITHOUT_OPT_IN_OBSERVER"],
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("metadata-tar","g2-tar","science-final","cold-audit",
                 "independent-statistics","old-e3a-full","old-e3a-second","output"):
        p.add_argument("--"+name,required=True)
    a=vars(p.parse_args())
    result=analyse(*(a[k] for k in (
        "metadata_tar","g2_tar","science_final","cold_audit",
        "independent_statistics","old_e3a_full","old_e3a_second")))
    data=A.canonical(result)
    output=Path(a["output"])
    with output.open("xb") as f:
        f.write(data)
    print(json.dumps({"status":result["status"],
                      "verified_originals":result["native_originals_rehashed"],
                      "source_sha256":sha256(data).hexdigest(),
                      "new_lives":result["native_lives_generated"]},sort_keys=True))


if __name__=="__main__":
    main()
