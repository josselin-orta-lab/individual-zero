"""Independent Stage8-B ORIGINAL-LIFE audit; no motor, World or births.

Standalone verification, distinct from the pre-exposure Stage8-B reducer:
- reconstruct all three generations from original SHA-bound gzip life records,
- verify 18 chained phase receipts and all source/World/seed pins,
- independently sum G2 selection effects by heldout F0 family and population,
- recompute the frozen 2-df Hotelling ecological omnibus from those sums,
- compare with published science JSON including negative and null cases.

The scanner reuses the existing Stage7 independent *record-level* verifier,
not the Stage8-A/Stage8-B native GSR generator or scientific reducer.
This is NOT a motor/physics replay, causal mechanism identification,
off-host attestation, or proof of population independence.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import gzip
import json
import math
from pathlib import Path

from i3.lab import stage7_persistence_independent_audit as U
from i3.lab import stage8b_independent_reduced_audit as R

RUN_ID = 44060101150
SOURCE_HEAD = "9f94d1c2c4170fd923ea0de68761bed2ac3d8377"
SCHEMA_SCIENCE = "i3-stage8b-ecology-interaction-science/v1"
SCHEMA_INNER = "i3-stage8a-mean-persistence-engineering-plan/v1"
PANEL_SCHEMA = "i3-stage7-heritable-persistence-engineering-plan/v1"
SCIENCE_FINAL_SCHEMA = "i3-stage8b-scientific-original/v1"
NATIVE_STATUS = "PERSISTENCE_FULL_GSR_ENGINEERING_SEALED_NO_SCIENCE"
TECH_STATUS = "STAGE8A_FULL_NATIVE_ENGINEERING_SEALED_NO_SCIENCE"
ORIGINALS = 23040
FAMILIES = ("stable", "depletion", "pulse")
ARMS = ("selected", "random_parent")
ALPHA = 0.025


def _parse(path: Path) -> dict:
    return json.loads(path.read_bytes())


def _digest_plan(obj: dict) -> str:
    return U.digest(U.canonical({k:v for k,v in obj.items()
                                if k != "allocation_sha256"}))


def _assert_plan(plan: object, schema: str) -> dict:
    if (type(plan) is not dict or plan.get("schema") != schema or
            type(plan.get("allocation_sha256")) is not str or
            not U.HASH_PATTERN.fullmatch(plan["allocation_sha256"]) or
            _digest_plan(plan) != plan["allocation_sha256"]):
        raise ValueError("changed, incomplete or foreign prospective plan")
    return plan


def _validate_panel(panel: dict, source: dict, original_path: Path,
                    reserved: dict, seen_seeds: set) -> dict:
    _assert_plan(panel,PANEL_SCHEMA)
    if (panel.get("source_git_head") != SOURCE_HEAD or
            panel.get("source_files_sha256") != source["source_files_sha256"] or
            panel.get("scientific_admission") is not False or
            panel.get("planned_lives") != 11520 or
            panel.get("planned_worlds") != 288 or
            panel.get("lives_per_generation") != [2304,4608,4608] or
            panel.get("archive_root") != str(original_path) or
            panel.get("reference") != "P1.3 funded-v2" or
            panel.get("decision_policy") != "reference"):
        raise ValueError("foreign 16-population native source or life budget")
    worlds=panel.get("worlds")
    founders=panel.get("founders")
    draws=panel.get("draws")
    if (type(worlds) is not list or len(worlds)!=288 or
            type(founders) is not list or len(founders)!=384 or
            type(draws) is not list or len(draws)!=1536):
        raise ValueError("missing World, founder or parent/mutation allocations")
    lookup={}
    for w in worlds:
        key=(w["population"],w["generation"],w["family"],w["repeat"])
        if (key in lookup or type(key[0]) is not int or
                not 0<=key[0]<16 or key[1] not in (0,1,2) or
                key[2] not in FAMILIES or key[3] not in (0,1)):
            raise ValueError("duplicated, omitted or foreign native World")
        lookup[key]=w
    if set(lookup) != {(p,g,f,r) for p in range(16)
                       for g in (0,1,2) for f in FAMILIES for r in (0,1)}:
        raise ValueError("World plan does not cover 16x3x3x2 opportunities")
    all_seeds = [w[k] for w in worlds
                 for k in ("world_index","world_seed","life_seed")]
    all_seeds += [v["genome_seed"] for v in founders]
    all_seeds += [v[k] for v in draws
                  for k in ("parent_draw_seed","mutation_seed")]
    if (any(type(z) is not int for z in all_seeds) or
            len(all_seeds) != len(set(all_seeds)) or
            any(z in seen_seeds for z in all_seeds)):
        raise ValueError("random seed collision within/between Stage8-B panels")
    seen_seeds.update(all_seeds)
    for w in worlds:
        if w["generation"] != 2:
            continue
        key=(w["population"],w["family"],w["repeat"])
        r=reserved[key]
        if (r["world_index"] != w["world_index"] or
                r["world_seed"] != w["world_seed"] or
                r["life_seed"] != w["life_seed"]):
            raise ValueError("G2 World was not the original preregistered holdout")
    return lookup


def _phase_chain(folder: Path, panel: dict, panel_core: dict) -> str:
    lines=(folder/"PHASES.jsonl").read_bytes().splitlines()
    if len(lines) != len(U.PHASES):
        raise ValueError("G0/G1/G2 native phase chain not complete")
    previous=None
    for n,raw in enumerate(lines):
        row=json.loads(raw)
        phase=U.PHASES[n]
        if (row.get("phase")!=phase or row.get("ordinal")!=n or
                row.get("previous_sha256")!=previous):
            raise ValueError("native phase chronology broken")
        h=row.get("chain_sha256")
        if (not isinstance(h,str) or not U.HASH_PATTERN.fullmatch(h) or
                U.digest(U.canonical({k:v for k,v in row.items()
                                      if k!="chain_sha256"}))!=h):
            raise ValueError("native phase SHA chain invalid")
        if phase in ("G0","G1","G2"):
            path=folder/phase/"MANIFEST.json"
        elif phase.startswith("SEAL_"):
            path=folder/phase[5:]/"MANIFEST.json"
        elif phase.startswith("SELECT_"):
            path=folder/(phase+".json")
        else:
            path=folder/"R_FINAL_PERSISTENCE_ENGINEERING.json"
        if U.digest(path.read_bytes()) != row.get("payload_sha256"):
            raise ValueError("native phase SHA payload mismatch")
        previous=h
    claim=_parse(folder/"CLAIM.json")
    original=_parse(folder/"R_FINAL_PERSISTENCE_ENGINEERING.json")
    seals=original.get("generation_seals")
    if (claim.get("plan_sha256") != panel["allocation_sha256"] or
            claim.get("scientific") is not False or
            claim.get("status") != "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL" or
            (folder/"FAILURE.json").exists() or
            panel_core.get("plan_sha256") != panel["allocation_sha256"] or
            panel_core.get("source_git_head") != SOURCE_HEAD or
            panel_core.get("status") != NATIVE_STATUS or
            panel_core.get("scientific_admission") is not False or
            panel_core.get("original_lives") != 11520 or
            panel_core.get("phase_chain_sha256") != previous or
            original.get("status") != NATIVE_STATUS or
            original.get("original_lives") != 11520 or
            original.get("scientific_admission") is not False or
            original.get("scientific_result_disclosed") is not False or
            type(seals) is not list or len(seals)!=3):
        raise ValueError("original technical panels not source-bound or sealed")
    for g,seal in enumerate(seals):
        if (seal.get("generation") != g or
                seal.get("lives") != (2304 if g==0 else 4608) or
                seal.get("manifest_sha256") !=
                U.digest((folder/f"G{g}"/"MANIFEST.json").read_bytes())):
            raise ValueError("generation seal disagrees with original manifest")
    return previous


def _family_g2_rehash(folder: Path, panel: dict, world_lookup: dict) -> dict:
    """Extra full-original G2 reread for ecological outcomes by family.

    The Stage7 independent scanner checks *all* original G0/G1/G2 SHA
    and complete coordinates first. This second G2 pass makes family
    aggregation independent of the experiment's native reducer.
    """
    g2=folder/"G2"
    raw_manifest=(g2/"MANIFEST.json").read_bytes()
    if U.digest(raw_manifest)!=(g2/"MANIFEST.sha256").read_text().strip():
        raise ValueError("Stage8-B G2 original manifest SHA invalid")
    manifest=json.loads(raw_manifest)
    if (manifest.get("status")!="GENERATED" or
            len(manifest.get("files",[]))!=4608 or
            manifest.get("generated")!=4608 or
            manifest.get("planned")!=4608):
        raise ValueError("G2 original generation incomplete")
    result=defaultdict(lambda: [0,0,0])
    seen=set()
    for i,entry in enumerate(manifest["files"]):
        name=entry.get("file")
        if (type(name) is not str or not U.PATH_PATTERN.fullmatch(name)
                or name!=f"life-{i:03d}.json.gz"):
            raise ValueError("unsafe, duplicate or reordered G2 gzip path")
        identity=entry["identity"]
        p,g,arm,slot,f,r=U._identity_check(identity,2,panel,world_lookup)
        key=(p,g,arm,slot,f,r)
        if key in seen:
            raise ValueError("duplicate original G2 opportunity")
        seen.add(key)
        compressed=(g2/name).read_bytes()
        if U.digest(compressed)!=entry["sha256"]:
            raise ValueError("tampered gzip Stage8-B original")
        raw=gzip.decompress(compressed)
        if U.digest(raw)!=entry["uncompressed_sha256"]:
            raise ValueError("tampered uncompressed Stage8-B original")
        packet=json.loads(raw)
        if packet.get("identity")!=identity:
            raise ValueError("G2 native identity changed")
        steps,censored=U._life_check(packet["life"],identity,panel)
        cell=result[(p,arm,f)]
        cell[0]+=1
        cell[1]+=steps
        cell[2]+=censored
    expected_keys={(p,2,arm,s,f,r)
                   for p in range(16) for arm in ARMS
                   for s in range(24) for f in FAMILIES for r in (0,1)}
    if (seen != expected_keys or
            set(result) != {(p,arm,f) for p in range(16)
                             for arm in ARMS for f in FAMILIES} or
            any(v[0]!=48 for v in result.values())):
        raise ValueError("missing one G2 population-family original")
    return dict(result)


def from_original_counts(counts: dict, families: dict, report_rows: list[dict]):
    """Independent 32x3 reduction, including all adverse/null populations."""
    if (type(report_rows) is not list or len(report_rows)!=32 or
            {r.get("population") for r in report_rows}!=set(range(32))):
        raise ValueError("not all 32 published population profiles")
    bypop={row["population"]:row for row in report_rows}
    vectors=[]
    for p in range(32):
        published=bypop[p]
        if published.get("panel")!=p//16:
            raise ValueError("reindexed population in published scientific result")
        g0=counts[p,0,"shared"]
        s1=counts[p,1,"selected"]
        r1=counts[p,1,"random_parent"]
        s2=counts[p,2,"selected"]
        r2=counts[p,2,"random_parent"]
        expected={
            "G0_mean_steps":g0["steps"]/144,
            "G1_selected_mean_steps":s1["steps"]/144,
            "G1_random_mean_steps":r1["steps"]/144,
            "G2_selected_mean_steps":s2["steps"]/144,
            "G2_random_mean_steps":r2["steps"]/144,
            "G1_selected_minus_random_steps":(s1["steps"]-r1["steps"])/144,
            "G2_selected_minus_random_steps":(s2["steps"]-r2["steps"])/144,
            "G2_selected_horizon_survival":s2["censored"]/144,
            "G2_random_horizon_survival":r2["censored"]/144,
        }
        if any(not R._float_close(published.get(k),v)
               for k,v in expected.items()):
            raise ValueError("G0/G1/G2 published body outcomes do not match original gzip")
        for arm in ARMS:
            frows=[families[p,arm,f] for f in FAMILIES]
            original=counts[p,2,arm]
            if (any(x[0]!=48 for x in frows)
                    or sum(x[1] for x in frows)!=original["steps"]
                    or sum(x[2] for x in frows)!=original["censored"]):
                raise ValueError("family original-life totals fail to exhaust G2 arm")
        row={}
        published_families=published.get("G2_families_descriptive",{})
        if set(published_families)!=set(FAMILIES):
            raise ValueError("published F0 family missing")
        for family in FAMILIES:
            left=families[p,"selected",family]
            right=families[p,"random_parent",family]
            observed=(left[1]-right[1])/48
            row[family]=observed
            expected={
                "selected_minus_random_mean_steps":observed,
                "selected_horizon_fraction":left[2]/48,
                "random_horizon_fraction":right[2]/48,
            }
            if any(not R._float_close(published_families[family].get(k),v)
                   for k,v in expected.items()):
                raise ValueError("one published ecology contrast differs from raw original lives")
        if not R._float_close(math.fsum(row.values())/3,
                              expected_global:=expected_value(
                                  s2["steps"],r2["steps"])):
            raise ValueError("family totals inconsistent with G2 original body steps")
        vectors.append(row)
    return vectors


def expected_value(selected_steps: int, random_steps: int) -> float:
    return (selected_steps-random_steps)/144


def audit_full(plan_path: str, originals_path: str, result_path: str) -> dict:
    """Read-only audit of all 23,040 native records and 32x3 F0 contrasts."""
    reduced=R.verify_reduced_science(plan_path,originals_path,result_path)
    plan=_assert_plan(_parse(Path(plan_path)),SCHEMA_SCIENCE)
    root=Path(originals_path).resolve()
    if not root.is_dir() or Path(originals_path).is_symlink():
        raise ValueError("not a valid extracted Stage8-B science original root")
    source_sha=plan["source_files_sha256"]
    if plan["source_git_head"]!=SOURCE_HEAD or not U.HASH_PATTERN.fullmatch(source_sha):
        raise ValueError("different native source than preregistered Stage8-B")
    native=root/"NATIVE_ORIGINALS"
    inner=_assert_plan(_parse(root/"INNER_PLAN.json"),SCHEMA_INNER)
    if (inner!=plan["inner_native_technical_plan"] or
            inner["allocation_sha256"]!=plan["inner_native_technical_plan_sha256"] or
            inner["scientific_admission"] is not False or
            inner["source_git_head"]!=SOURCE_HEAD or
            inner["source_files_sha256"]!=source_sha or
            inner["planned_original_lives"]!=ORIGINALS or
            inner["planned_worlds"]!=576 or
            inner["archive_root"]!=plan["archive_root"]+"/NATIVE_ORIGINALS" or
            _parse(native/"CLAIM.json").get("allocation_sha256")!=inner["allocation_sha256"] or
            (native/"FAILURE.json").exists()):
        raise ValueError("native engine inner source or custody differs from Stage8-B plan")
    core=_parse(root/"INNER_CORE.json")
    if (core.get("status")!=TECH_STATUS or
            core.get("scientific_admission") is not False or
            core.get("plan_sha256")!=inner["allocation_sha256"] or
            core.get("original_lives")!=ORIGINALS or
            len(core.get("panel_chain_sha256",[]))!=2):
        raise ValueError("native 32-population engineering panels not complete")
    plan_holdout=plan["g2_holdout_reserved_worlds"]
    if (type(plan_holdout) is not list or len(plan_holdout)!=192 or
            U.digest(U.canonical(plan_holdout))!=plan["g2_holdout_worlds_sha256"]):
        raise ValueError("G2 reserved Worlds not bound to science admission")
    seen_seeds=set()
    overall={}
    by_family={}
    phase_chains=[]
    for i in range(2):
        folder=native/f"PANEL_{i}"
        panel=_assert_plan(inner["panels"][i],PANEL_SCHEMA)
        reserved={(r["population"]-16*i,r["family"],r["repeat"]):r
                  for r in plan_holdout if r["panel"]==i}
        if (len(reserved)!=96 or
                set(reserved)!={(p,f,r) for p in range(16)
                                 for f in FAMILIES for r in (0,1)}):
            raise ValueError("missing 96 precommitted G2 Worlds in one panel")
        expected_path=Path(inner["archive_root"])/f"PANEL_{i}"
        worlds=_validate_panel(panel,inner,expected_path,reserved,seen_seeds)
        if (_parse(native/f"PANEL_{i}_PLAN.json")!=panel or
                folder.is_symlink() or not folder.is_dir()):
            raise ValueError("foreign or symlinked native panel")
        panel_core=_parse(native/f"PANEL_{i}_CORE.json")
        sealed=_phase_chain(folder,panel,panel_core)
        if sealed!=core["panel_chain_sha256"][i]:
            raise ValueError("one native panel seal differs from outer original core")
        phase_chains.append(sealed)
        for g in (0,1,2):
            # Independent original-level scanner: SHA and uncompressed payload,
            # all source and genotype identities, life traces and body funding.
            cells=U.scan_sealed_generation(folder,g,panel,worlds)
            for (p,arm),observed in cells.items():
                key=(16*i+p,g,arm)
                if key in overall:
                    raise ValueError("overlapping native populations")
                overall[key]=observed
        for (p,arm,f),observed in _family_g2_rehash(folder,panel,worlds).items():
            key=(16*i+p,arm,f)
            if key in by_family:
                raise ValueError("G2 family population duplicated")
            by_family[key]=observed
    if (len(overall)!=16*2*(1+2+2) or len(by_family)!=32*2*3 or
            len(set(phase_chains))!=2):
        raise ValueError("one G0/G1/G2, population, arm or ecology is missing")
    report=_parse(Path(result_path))
    original_final=_parse(root/"SCIENCE_FINAL.json")
    if (original_final.get("inner_plan_sha256")!=inner["allocation_sha256"]
            or original_final.get("analysis",{}).get("all_native_lives_reverified")!=ORIGINALS
            or original_final.get("analysis",{}).get("parent_draws_reproduced")!=3072
            or original_final.get("analysis",{}).get("mutations_reproduced")!=3072):
        raise ValueError("scientific GSR original envelope does not bind native ancestry")
    observed_rows=from_original_counts(overall,by_family,report["all_population_statistics"])
    calculated=R.reduce_omnibus(observed_rows)
    R._verify_primary(report["primary"],calculated)
    if (report["status"]!=calculated["status"] or
            reduced["scientific_status"]!=calculated["status"] or
            report["primary"].get("effects_per_population")!=calculated["effects_per_population"]):
        raise ValueError("native original G2 ecological effect contradicts published science")
    return {
        "schema":"i3-stage8b-independent-originals-ecology-audit/v1",
        "status":"READ_ONLY_ORIGINALS_REPRODUCED",
        "scientific_status":calculated["status"],
        "run_id":RUN_ID,"source_git_head":SOURCE_HEAD,
        "science_plan_sha256":plan["allocation_sha256"],
        "g2_holdout_worlds_sha256":plan["g2_holdout_worlds_sha256"],
        "populations_verified":32,
        "native_original_lives_rehashed":ORIGINALS,
        "g2_family_lives_rehashed_again":9216,
        "phase_chains_verified":phase_chains,
        "ecology_positive_population_counts":calculated["positive_counts"],
        "ecology_mean_effect_steps":calculated["family_means"],
        "omnibus_p":calculated["p_value_two_sided_omnibus"],
        "omnibus_t_squared":calculated["hotelling_t_squared"],
        "omnibus_f":calculated["f_df2_30"],
        "new_worlds":0,"new_lives":0,
        "limits":"NO_MOTOR_REPLAY_NO_EXTERNAL_ATTESTATION_NO_PROOF_OF_INDEPENDENCE",
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("science_plan")
    parser.add_argument("science_originals")
    parser.add_argument("science_result")
    args=parser.parse_args()
    print(json.dumps(audit_full(
        args.science_plan,args.science_originals,args.science_result),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
