"""Posthoc read-only Stage8-A independent reduction of all 23,040 native gzip lives.

This is NOT an additional experiment and does not import the Stage8 runner,
create WorldSpecs, evaluate genomes, or call run_life. Its fixed 17-Nov-2026
source/plan pins are for the already-closed ONE-SHOT run #43950098410.
No source-independent attestation, physical action replay, or proof of
statistical population independence is claimed.

Reuse only the separately authored Stage7 *original record* SHA/body scanner.
The Stage8-A mean, 32 contrasts, Student bound and scientific verdict are
recomputed here independently of the Stage8-A scientific reducer.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import re
import sys

from i3.lab import stage7_persistence_independent_audit as A

SOURCE_HEAD = "ac353a9c4206ee3ecfd90bb101e26d092103958b"
SCIENCE_PLAN_SHA = "dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660"
RUN_ID = 43950098410
SOURCE_SCHEMA = "i3-stage8a-mean-persistence-science-plan/v1"
PANEL_SCHEMA = "i3-stage7-heritable-persistence-engineering-plan/v1"
RESULT_SCHEMA = "i3-stage8a-mean-persistence-internal-result/v1"
FINAL_SCHEMA = "i3-stage8a-mean-science-original/v1"
PANEL_SUCCESS = "PERSISTENCE_FULL_GSR_ENGINEERING_SEALED_NO_SCIENCE"
POSITIVE = "STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0"
NEGATIVE = "STAGE8A_MEAN_ADVANTAGE_NOT_DEMONSTRATED_F0"
TCRIT = 2.0395134463964077
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
POP = 32
PANEL_POP = 16
LIVES_TOTAL = 23040


def _eq_float(actual, expected):
    return type(actual) in (float, int) and math.isfinite(actual) and math.isclose(
        actual, expected, rel_tol=0, abs_tol=1e-10)


def _digest_and_assert(p: dict):
    if type(p) is not dict or not SHA_RE.fullmatch(str(p.get("allocation_sha256", ""))):
        raise ValueError("missing immutable plan hash")
    if A.digest(A.canonical({k:v for k,v in p.items()
                             if k!="allocation_sha256"})) != p["allocation_sha256"]:
        raise ValueError("mutated originally-published plan")
    return p


def _verify_panel_plan(panel: object, source: dict, expected_path: str, seen_seed: set) -> dict:
    panel=_digest_and_assert(panel)
    if (panel.get("schema") != PANEL_SCHEMA or
            panel.get("scientific_admission") is not False or
            panel.get("source_git_head") != SOURCE_HEAD or
            panel.get("source_files_sha256") != source["source_files_sha256"] or
            panel.get("planned_lives") != 11520 or
            panel.get("planned_worlds") != 288 or
            panel.get("lives_per_generation") != [2304,4608,4608] or
            panel.get("archive_root") != expected_path or
            panel.get("reference") != "P1.3 funded-v2" or
            panel.get("decision_policy") != "reference"):
        raise ValueError("wrong full native 16-population technical panel")
    worlds=panel.get("worlds")
    founders=panel.get("founders")
    draws=panel.get("draws")
    if (type(worlds) is not list or len(worlds)!=288 or
            type(founders) is not list or len(founders)!=384 or
            type(draws) is not list or len(draws)!=1536):
        raise ValueError("incomplete World/founder/descendant allocation")
    keys=set()
    lookup={}
    for w in worlds:
        key=(w["population"],w["generation"],w["family"],w["repeat"])
        if (key in keys or type(key[0]) is not int or not 0<=key[0]<16
                or key[1] not in (0,1,2) or key[2] not in A.FAMILIES
                or key[3] not in (0,1)):
            raise ValueError("duplicate or missing independent F0 opportunity")
        keys.add(key)
        lookup[key]=w
    expected={(p,g,f,r) for p in range(16) for g in range(3)
              for f in A.FAMILIES for r in (0,1)}
    if keys!=expected:
        raise ValueError("incomplete 288 original World plan coordinates")
    all_seeds=[v[k] for v in worlds
               for k in ("world_index","world_seed","life_seed")]
    all_seeds += [v["genome_seed"] for v in founders]
    all_seeds += [v[k] for v in draws
                  for k in ("parent_draw_seed","mutation_seed")]
    if (any(type(s) is not int for s in all_seeds) or
            len(all_seeds)!=len(set(all_seeds)) or
            any(s in seen_seed for s in all_seeds)):
        raise ValueError("reused seeds across panel or root")
    seen_seed.update(all_seeds)
    return lookup


def _verify_phases_and_cores(folder: Path, plan: dict, final: dict, i: int):
    phases=(folder/"PHASES.jsonl").read_bytes().splitlines()
    if len(phases)!=len(A.PHASES):
        raise ValueError("not nine complete phases in technical subpanel")
    previous=None
    for n,raw in enumerate(phases):
        row=json.loads(raw)
        phase=A.PHASES[n]
        if (row.get("ordinal")!=n or row.get("phase")!=phase or
                row.get("previous_sha256")!=previous):
            raise ValueError("broken G/S/R phase chronology")
        recorded=row.get("chain_sha256")
        expected=A.digest(A.canonical({k:v for k,v in row.items()
                                       if k!="chain_sha256"}))
        if recorded!=expected:
            raise ValueError("altered phase chain hash")
        if phase in ("G0","G1","G2"):
            file=folder/phase/"MANIFEST.json"
        elif phase.startswith("SEAL_"):
            file=folder/phase[5:]/"MANIFEST.json"
        elif phase.startswith("SELECT_"):
            file=folder/(phase+".json")
        else:
            file=folder/"R_FINAL_PERSISTENCE_ENGINEERING.json"
        if A.digest(file.read_bytes())!=row.get("payload_sha256"):
            raise ValueError("phase chain not bound to original payload")
        previous=recorded
    claim=A.read_json(folder/"CLAIM.json")
    core=A.read_json(folder.parent/f"PANEL_{i}_CORE.json")
    original=A.read_json(folder/"R_FINAL_PERSISTENCE_ENGINEERING.json")
    expected_core=final.get("panel_cores", [])[i]
    if (claim.get("plan_sha256") != plan["allocation_sha256"] or
            claim.get("scientific") is not False or
            claim.get("status")!="CLAIMED_NO_RETRY_EVEN_IF_PARTIAL" or
            (folder/"FAILURE.json").exists() or
            core!=expected_core or
            core.get("source_git_head")!=SOURCE_HEAD or
            core.get("plan_sha256")!=plan["allocation_sha256"] or
            core.get("status")!=PANEL_SUCCESS or
            core.get("scientific_admission") is not False or
            core.get("original_lives")!=11520 or
            core.get("phase_chain_sha256")!=previous or
            original.get("status")!=PANEL_SUCCESS or
            original.get("original_lives")!=11520 or
            original.get("scientific_admission") is not False or
            original.get("scientific_result_disclosed") is not False):
        raise ValueError("missing complete source-exact sealed technical panel receipt")
    seals=original.get("generation_seals")
    if (not isinstance(seals,list) or len(seals)!=3 or
            [r.get("generation") for r in seals]!=[0,1,2] or
            [r.get("lives") for r in seals]!=[2304,4608,4608]):
        raise ValueError("three native generations not sealed in engineering panel")
    for g,receipt in enumerate(seals):
        if A.digest((folder/f"G{g}"/"MANIFEST.json").read_bytes())!=receipt["manifest_sha256"]:
            raise ValueError("one generational original SHA receipt changed")
    return previous


def _mean_primary(values: list[float]) -> dict:
    """Independently recompute the already-frozen 32-population one-sided test."""
    if (type(values) is not list or len(values)!=32
            or any(type(v) not in (float,int) or not math.isfinite(v)
                   for v in values)):
        raise ValueError("exactly 32 finite population G2 contrasts required")
    x=[float(z) for z in values]
    mean=math.fsum(x)/32
    sd=math.sqrt(math.fsum((v-mean)**2 for v in x)/31)
    se=sd/math.sqrt(32)
    lower=mean-TCRIT*se
    passed=sd>0 and mean>0 and lower>0
    return {
        "status": POSITIVE if passed else NEGATIVE,
        "mean":mean,"sd":sd,"se":se,"lower":lower,
        "positive":sum(v>0 for v in x),
        "negative":sum(v<0 for v in x),
        "zero":sum(v==0 for v in x),
        "contrasts":x,
        "positive_lower_bound":passed,
    }


def _assert_original_reducer_match(final: dict, report: dict, observed: dict):
    if (final.get("schema")!=FINAL_SCHEMA or
            final.get("source_git_head")!=SOURCE_HEAD or
            final.get("result",{}).get("status")!=observed["status"] or
            report.get("schema")!=RESULT_SCHEMA or
            report.get("status")!=observed["status"] or
            report.get("source_git_head")!=SOURCE_HEAD or
            report.get("population_units")!=32 or
            report.get("original_native_lives")!=23040 or
            report.get("primary")!=final["result"]["primary"] or
            report.get("all_population_statistics")!=final["result"]["all_population_statistics"]):
        raise ValueError("original result report diverges from sealed science R")
    primary=report["primary"]
    for key,expect in (
        ("mean_difference_steps",observed["mean"]),
        ("sample_sd_between_populations",observed["sd"]),
        ("standard_error",observed["se"]),
        ("one_sided_97_5_percent_lower_bound_steps",observed["lower"])):
        if not _eq_float(primary.get(key),expect):
            raise ValueError("frozen Student primary statistic not rederived")
    if (primary.get("status")!=observed["status"] or
            primary.get("n_populations")!=32 or
            primary.get("positive")!=observed["positive"] or
            primary.get("negative")!=observed["negative"] or
            primary.get("zero")!=observed["zero"] or
            primary.get("primary_success") is not observed["positive_lower_bound"] or
            primary.get("t_critical_df31_one_sided_975")!=TCRIT or
            not isinstance(primary.get("population_contrasts_steps"),list) or
            len(primary["population_contrasts_steps"])!=32 or
            any(not _eq_float(a,b) for a,b in zip(
                primary["population_contrasts_steps"],observed["contrasts"]))):
        raise ValueError("one or more primary population contrasts altered")
    return True


def audit_full(plan_file: str, original_root: str, result_file: str) -> dict:
    """Read-only scan 23,040 compressed original life records and recompute mean."""
    plan=_digest_and_assert(A.read_json(Path(plan_file)))
    if (plan.get("schema")!=SOURCE_SCHEMA or
            plan["allocation_sha256"]!=SCIENCE_PLAN_SHA or
            plan.get("source_git_head")!=SOURCE_HEAD or
            plan.get("scientific_admission") is not True or
            plan.get("planned_original_lives")!=23040 or
            plan.get("planned_worlds")!=576 or
            plan.get("scientific_verdict_before_exposure")!="NOT_ISSUED" or
            plan.get("Stage6_and_Stage7_originals_not_reused") is not True):
        raise ValueError("not the original Stage8-A preexposure scientific plan")
    method=plan.get("frozen_method",{})
    if (method.get("population_units")!=32 or
            method.get("t_critical_df31")!=TCRIT or
            method.get("alpha_one_sided")!=0.025 or
            method.get("primary") !=
            "mean_over_32_populations_of_G2_selected_minus_random_mean_lived_steps"):
        raise ValueError("original mean method changed after exposure")
    root=Path(original_root).resolve()
    if not root.is_dir() or Path(original_root).is_symlink():
        raise ValueError("no untouched extracted scientific originals available")
    claim=A.read_json(root/"CLAIM.json")
    if (claim.get("allocation_sha256")!=plan["allocation_sha256"] or
            claim.get("source_git_head")!=SOURCE_HEAD or
            claim.get("scientific") is not True or
            claim.get("status")!="CLAIMED_NO_RETRY_EVEN_IF_PARTIAL" or
            (root/"FAILURE.json").exists()):
        raise ValueError("science custody claim absent, failed or wrong")
    final_bytes=(root/"SCIENCE_FINAL.json").read_bytes()
    final=json.loads(final_bytes)
    report=A.read_json(Path(result_file))
    if (report.get("science_plan_sha256")!=plan["allocation_sha256"] or
            report.get("science_original_sha256")!=A.digest(final_bytes) or
            final.get("plan_sha256")!=plan["allocation_sha256"] or
            final.get("source_files_sha256")!=plan["source_files_sha256"] or
            final.get("original_native_lives")!=23040 or
            report.get("provenance")!="INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED" or
            final.get("provenance")!="INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"):
        raise ValueError("final published report not digest-bound to original science")
    subplans=plan.get("panels")
    if type(subplans) is not list or len(subplans)!=2:
        raise ValueError("two independent original scientific panels required")
    seeds=set()
    counts={}
    chain=[]
    for i,panel in enumerate(subplans):
        folder=root/f"PANEL_{i}"
        if (folder.is_symlink() or not folder.is_dir() or
                A.read_json(root/f"PANEL_{i}_PLAN.json")!=panel):
            raise ValueError("mismatched embedded physical panel")
        lookups=_verify_panel_plan(
            panel,plan,str(Path(plan["archive_root"])/f"PANEL_{i}"),seeds)
        panel_count={
            g: A.scan_sealed_generation(folder,g,panel,lookups)
            for g in (0,1,2)
        }
        for g,by_arm in panel_count.items():
            for (p,arm),row in by_arm.items():
                key=(i*16+p,g,arm)
                if key in counts:
                    raise ValueError("duplicate population across panels")
                counts[key]=row
        chain.append(_verify_phases_and_cores(folder,panel,final,i))
    if (len(counts)!=16*2*(1+2+2) or
            len(set(chain))!=2):
        raise ValueError("one panel/generation/arm audit is incomplete or duplicated")
    differences=[]
    pop_rows=report.get("all_population_statistics",[])
    if (not isinstance(pop_rows,list) or len(pop_rows)!=32
            or {row.get("population") for row in pop_rows}!=set(range(32))):
        raise ValueError("not all 32 population summaries publicly retained")
    bypop={row["population"]:row for row in pop_rows}
    for p in range(32):
        g0=counts[p,0,"shared"]
        s1=counts[p,1,"selected"];r1=counts[p,1,"random_parent"]
        s2=counts[p,2,"selected"];r2=counts[p,2,"random_parent"]
        delta=(s2["steps"]-r2["steps"])/144
        differences.append(delta)
        published=bypop[p]
        expected=[
            ("G0_mean_steps",g0["steps"]/144),
            ("G1_selected_mean_steps",s1["steps"]/144),
            ("G1_random_mean_steps",r1["steps"]/144),
            ("G2_selected_mean_steps",s2["steps"]/144),
            ("G2_random_mean_steps",r2["steps"]/144),
            ("G1_selected_minus_random_steps",(s1["steps"]-r1["steps"])/144),
            ("G2_selected_minus_random_steps",delta),
            ("G2_selected_horizon_survival",s2["censored"]/144),
            ("G2_random_horizon_survival",r2["censored"]/144)
        ]
        if (published.get("panel")!=p//16 or
                any(not _eq_float(published.get(field),number)
                    for field,number in expected)):
            raise ValueError("one reported G0/G1/G2 outcome contradicts original lives")
    independently=_mean_primary(differences)
    _assert_original_reducer_match(final,report,independently)
    return {
        "schema":"i3-stage8a-independent-readonly-original-mean-audit/v1",
        "status":"READ_ONLY_REPRODUCTION_OK",
        "science_status":independently["status"],
        "source_git_head":SOURCE_HEAD,
        "plan_sha256":SCIENCE_PLAN_SHA,
        "run_id":RUN_ID,
        "original_lives_rehashed":23040,
        "populations_reduced":32,
        "panel_phase_chain_sha256":chain,
        "independent_mean_difference_steps":independently["mean"],
        "independent_lower_bound_steps":independently["lower"],
        "positive":independently["positive"],
        "negative":independently["negative"],
        "zero":independently["zero"],
        "population_G2_differences_steps":independently["contrasts"],
        "new_worlds":0,"new_lives":0,
        "limits":"NO_MOTOR_REPLAY_NO_OFF_HOST_ATTESTATION_NO_POPULATION_INDEPENDENCE_PROOF"
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("science_plan")
    parser.add_argument("science_originals")
    parser.add_argument("science_result")
    a=parser.parse_args()
    print(json.dumps(audit_full(a.science_plan,a.science_originals,
                                a.science_result),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
