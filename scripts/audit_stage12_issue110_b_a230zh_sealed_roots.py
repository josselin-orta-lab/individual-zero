"""A2.30-ZH: independent offline verification of the sealed ZG root study.

No import of the original ZG runner, WorldBody, Equipment, SimulatorPlanner,
Oracle, or a Stage12Runtime. The 12 true I0 birth roots come independently
from their original ZB CI run, not from the experimental learner's report.
Reconstruct exact state-command keyed evidence, every root-edge count, and
the bounded first actions from physical-example JSON only.

This is an ARCHIVE INTEGRITY audit, not another physical reproduction.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

ZG_RUN=38777542232
ZB_RUN=38767643472
ZG_SHA="f416424292501671eda7f9ed65accb7a2712f9ef"
ZB_SHA="2a19742df22f27752635203304097134a3009c45"
ZG_FILES={
    "a230zg-physical-demonstrations.json":
        "53f0363f09df2e23984d75bcdddb98550adeb1f35b015810a1b8ad5d37c91625",
    "a230zg-lived-birth-shadow.json":
        "fdfafde49f92f2feb26b41b42e71106766b5f30f3c33fb191ef53866705a9875",
    "a230zg-summary.json":
        "6af19338b42d9d3f17d26e9c3f1fe051e55f47e1fc3e04e7b66ccd5301b78617",
}
ZB_FILES={
    "3.11":"ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b",
    "3.12":"ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362",
}
PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST")
HIDDEN=("benign","toxic_lethal")
STATE_KEYS={
    "schema_version","x","y","body","inventory","current_water_source",
    "current_resources","adjacent","known_shelter_here","is_night",
}
B_COLLECT={"primitive":"collecter","parameters":{"target":"berry_b"}}
B_EAT={"primitive":"manger","parameters":{"target":"berry_b"}}
MOVE_E={"primitive":"se_deplacer","parameters":{"direction":"east"}}
MOVE_N={"primitive":"se_deplacer","parameters":{"direction":"north"}}
A_COLLECT={"primitive":"collecter","parameters":{"target":"berry_a"}}
A_EAT={"primitive":"manger","parameters":{"target":"berry_a"}}


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def read_one(root,name,expected):
    hits=list(Path(root).rglob(name))
    if len(hits)!=1:
        raise ValueError("ambiguous or missing original artifact: "+name)
    raw=hits[0].read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise ValueError("original artifact SHA-256 mismatch: "+name)
    return raw


def load_sources(zg311,zg312,zb311,zb312):
    a={name:read_one(zg311,name,h) for name,h in ZG_FILES.items()}
    b={name:read_one(zg312,name,h) for name,h in ZG_FILES.items()}
    if a!=b:
        raise ValueError("original ZG 3.11 and 3.12 outputs are not byte-equal")
    zb_a=json.loads(read_one(zb311,"a230zb-summary.json",ZB_FILES["3.11"]))
    zb_b=json.loads(read_one(zb312,"a230zb-summary.json",ZB_FILES["3.12"]))
    return (
        json.loads(a["a230zg-physical-demonstrations.json"]),
        json.loads(a["a230zg-lived-birth-shadow.json"]),
        json.loads(a["a230zg-summary.json"]),
        zb_a,zb_b,
    )


def check_state(s):
    if type(s) is not dict or set(s)!=STATE_KEYS:
        raise ValueError("nonperceptual, hidden or future variable in root")
    if (set(s["body"])!={"energy","food","water","integrity"}
        or set(s["inventory"])!={"berry_a","berry_b","wood","stone","tool"}
        or len(s["adjacent"])!=4
        or {n["direction"] for n in s["adjacent"]}!=
            {"north","south","east","west"}):
        raise ValueError("incomplete observable body/neighbor state")
    if not all(set(n)=={
        "direction","x","y","passable","water_source","resources","creature"
    } for n in s["adjacent"]):
        raise ValueError("hidden information in neighbor perception")
    if any(k in s for k in ("latent_B","safe","oracle","world_config")):
        raise ValueError("latent/Oracle model feature was injected")
    return s


def command_key(s,command):
    return digest({"state":check_state(s),"command":command})


def candidates(s):
    """Standalone reimplementation of Stage6 candidate generation."""
    check_state(s)
    commands=[]
    for n in s["adjacent"]:
        if n["passable"]:
            commands.append({
                "primitive":"se_deplacer",
                "parameters":{"direction":n["direction"]},
            })
    for item in sorted(set(s["current_resources"])):
        commands.append({
            "primitive":"collecter","parameters":{"target":item},
        })
    for item in ("berry_a","berry_b"):
        if s["inventory"].get(item,0)>0:
            commands.append({
                "primitive":"manger","parameters":{"target":item},
            })
    if s["current_water_source"]:
        commands.append({"primitive":"boire","parameters":{}})
    if s["inventory"].get("stone",0)>0:
        commands.append({
            "primitive":"poser_une_pierre","parameters":{},
        })
    if (s["inventory"].get("wood",0)>0
        and s["inventory"].get("stone",0)>0):
        commands.append({"primitive":"fabriquer_outil","parameters":{}})
    commands.extend((
        {"primitive":"dormir","parameters":{}},
        {"primitive":"attendre","parameters":{}},
    ))
    return commands


def check_original_births(zb311,zb312):
    if (zb311["schema"]!="a230zb-autonomous-alternative-lived-v1"
        or zb312["schema"]!="a230zb-autonomous-alternative-lived-v1"
        or zb311["git_sha"]!=ZB_SHA or zb312["git_sha"]!=ZB_SHA
        or len(zb311["lives"])!=12 or len(zb312["lives"])!=12
        or zb311["B_collections_executed"]!=0
        or zb311["B_ingestions_physically_confirmed"]!=0
        or zb311["actual_autonomous_world_steps"]!=384):
        raise ValueError("incorrect historical ZB birth cohort")
    births={}
    for original in (zb311,zb312):
        local={}
        for life in original["lives"]:
            ident=life["birth_id"]
            if ident in local:
                raise ValueError("duplicate original I0 mortal birth identifier")
            if (life["world_steps"]!=32 or
                life["mortal_status"]!="experiment_stopped" or
                life["confirmed_B_ingestions"] or
                life["experienced_B_commands_with_motives"] or
                len(life["equipment_sha256_A_only"])!=64):
                raise ValueError("original I0 life contains unrecognized B experience")
            check_state(life["initial_accessible_projection"])
            local[ident]=life
        if not births:
            births=local
        elif set(births)!=set(local):
            raise ValueError("cross Python original I0 identities differ")
        else:
            for identity,row in births.items():
                other=local[identity]
                for k in (
                    "initial_accessible_projection",
                    "equipment_sha256_A_only","profile","layout",
                    "hidden_B_external_only","world_steps",
                    "executed_motor_commands","mortal_status",
                ):
                    if row[k]!=other[k]:
                        raise ValueError("birth-firstperson cross Python discrepancy")
    if len(births)!=12:
        raise ValueError("not 12 original autonomous roots")
    return births


def check_detached_sources(manifest):
    if (manifest.get("schema")!="a230zg-separate-detached-physical-training-v1"
        or manifest.get("original_ZB_run")!=ZB_RUN
        or manifest.get("original_ZB_source_SHA")!=ZB_SHA
        or manifest.get("original_source_summary_sha256")!=ZB_FILES
        or manifest.get("physical_demo_worlds")!=6
        or manifest.get("real_physical_demonstration_steps")!=14
        or manifest.get("A_reference_physical_steps")!=8
        or manifest.get("B_non_ingestive_physical_steps")!=6
        or manifest.get("demo_hashes_are_external_not_cognitive") is not True
        or manifest.get("model_trained_before_test_root_queries") is not True
        or manifest.get("no_ingestion_B_demonstrated") is not True):
        raise ValueError("training manifest misreports physical custody")
    demos=manifest["all_physical_demonstrations"]
    if len(demos)!=6 or len({d["source_world_id"] for d in demos})!=6:
        raise ValueError("missing or duplicated detached physical source")
    source_index={}
    training={}
    for p in PROFILES:
        training[p]={"A_ONLY":{},"A_PLUS_B_NON_INGESTIVE":{}}
    step_count=0
    for d in demos:
        ident=d["source_world_id"]
        if (not ident.startswith(("A_REFERENCE-","B_DEMONSTRATOR-"))
            or d["not_an_I0_birth"] is not True
            or d["no_B_ingestion"] is not True
            or d["all_actions_physical_nonterminal"] is not True):
            raise ValueError("illicit physical demonstrator source")
        profile=next((p for p in PROFILES if ident.split("-")[1]==p),None)
        if profile is None:
            raise ValueError("cross-profile or unregistered demonstrator")
        role=("A_ONLY" if ident.startswith("A_REFERENCE") else "B")
        if role=="A_ONLY":
            if ident!=f"A_REFERENCE-{profile}":
                raise ValueError("nonregistered A source identity")
            expected=(MOVE_N,MOVE_E,A_COLLECT,A_EAT)
        else:
            if ident not in (
                f"B_DEMONSTRATOR-{profile}-B_LOCAL",
                f"B_DEMONSTRATOR-{profile}-B_EAST",
            ):
                raise ValueError("nonregistered B source physical geometry")
            expected=((B_COLLECT,) if ident.endswith("B_LOCAL")
                      else (MOVE_E,B_COLLECT))
        examples=d["physical_examples"]
        if (len(examples)!=len(expected) or
            d["physical_step_count"]!=len(expected) or
            len(d["physical_example_sha256"])!=len(examples)
            or examples[0]["state"]!=d["root_first_person"]):
            raise ValueError("detached physical steps/source do not match preregistration")
        check_state(d["root_first_person"])
        previous=None
        for i,(example,command) in enumerate(zip(examples,expected)):
            if (digest(example)!=d["physical_example_sha256"][i]
                or example["command"]!=command
                or example["terminal"] is not False
                or (previous is not None and example["state"]!=previous)):
                raise ValueError("physical example integrity/chronology/terminal mismatch")
            check_state(example["state"])
            check_state(example["observed_next_state"])
            initial=example["state"]
            if command==B_COLLECT and "berry_b" not in initial["current_resources"]:
                raise ValueError("forged physical collection without a visible berry B")
            if command==MOVE_E and not next(n for n in initial["adjacent"]
                    if n["direction"]=="east")["passable"]:
                raise ValueError("forged movement into blocked eastern cell")
            if role=="B" and command["primitive"]=="manger":
                raise ValueError("illegal B ingestion trained before root")
            previous=example["observed_next_state"]
            key=command_key(initial,command)
            target=training[profile]["A_PLUS_B_NON_INGESTIVE"]
            old=target.get(key)
            if old is not None and (
                old["observed_next_state"]!=example["observed_next_state"]
                or old["terminal"]!=example["terminal"]
            ):
                raise ValueError("contradictory physical exact-key outputs")
            target[key]=example
            if role=="A_ONLY":
                training[profile]["A_ONLY"][key]=example
            step_count+=1
        source_index[ident]=d
    if step_count!=14:
        raise ValueError("physical demonstration action count deviates")
    for p in PROFILES:
        if (len(training[p]["A_ONLY"])!=4
            or len(training[p]["A_PLUS_B_NON_INGESTIVE"])!=7):
            raise ValueError("cross-profile or missing exact model facts")
    return source_index,training


def independently_evaluate(manifest,rows,summary,zb311,zb312):
    births=check_original_births(zb311,zb312)
    sources,models=check_detached_sources(manifest)
    if len(rows)!=12 or len({r["original_birth_id"] for r in rows})!=12:
        raise ValueError("duplicate/missing shadow root")
    rows_index={r["original_birth_id"]:r for r in rows}
    if set(rows_index)!=set(births):
        raise ValueError("shadow output swapped original birth identities")
    group=defaultdict(list)
    counters=Counter()
    observed_model_hash={}
    for identity,row in rows_index.items():
        life=births[identity]
        p=life["profile"]
        layout=life["layout"]
        hidden=life["hidden_B_external_only"]
        if (p not in PROFILES or layout not in LAYOUTS or hidden not in HIDDEN
            or row["profile"]!=p or row["layout"]!=layout or
            row["hidden_effect_for_external_stratification_only"]!=hidden):
            raise ValueError("wrong archived root factor profile/layout/latent")
        before=check_state(row["first_person_root_state"])
        if (before!=life["initial_accessible_projection"]
            or row["first_person_sha256"]!=digest(before)
            or row["historical_world_steps_no_new_actions"]!=32
            or row["A_only_equipment_sha256"]!=life["equipment_sha256_A_only"]
            or row["A_only_equipment_sha256"]!=
                manifest["original_A_model_sha256_by_profile"][p]
            or row["augmented_exact_equipment_sha256"]!=
                manifest["augmented_shadow_model_sha256_by_profile"][p]
            or row["training_transition_from_other_world_not_lived_by_i0"] is not True
            or row["stage6_prediction_not_actually_dispatched"] is not True
            or row["no_lived_uc_or_agency_implied"] is not True
            or row["B_ingestion_safety_proven"] is not False):
            raise ValueError("root fingerprint, historical model or safety provenance forged")
        group[(p,layout)].append(row)
        source_name=(f"B_DEMONSTRATOR-{p}-{layout}"
                     if layout!="B_NONE" else None)
        if row["external_physical_source_world_id"]!=source_name:
            raise ValueError("detached physical source identity was spoofed")
        root_commands=candidates(before)
        relevant=(B_COLLECT if layout=="B_LOCAL" else MOVE_E)
        if layout=="B_NONE":
            if (B_COLLECT in root_commands
                or row["eligible_B_first_step"] is not None
                or row["eligible_B_first_step_in_candidate_commands"] is not False
                or row["B_first_step_known_in_historical_A"] is not None
                or row["B_first_step_known_in_augmented_shadow"] is not None
                or row["physically_witnessed_B_first_step_next_state"] is not None):
                raise ValueError("absent B was made physically available")
        else:
            if (row["eligible_B_first_step"]!=relevant
                or row["eligible_B_first_step_in_candidate_commands"] is not True
                or relevant not in root_commands):
                raise ValueError("real first-person B action is not eligible")
            source=sources[source_name]
            if before!=source["root_first_person"]:
                raise ValueError("source was not exact to I0 newborn perception")
            key=command_key(before,relevant)
            if (key in models[p]["A_ONLY"]
                or key not in models[p]["A_PLUS_B_NON_INGESTIVE"]):
                raise ValueError("new B root edge not truly trained from physics")
            example=models[p]["A_PLUS_B_NON_INGESTIVE"][key]
            if (row["physically_witnessed_B_first_step_next_state"]!=
                example["observed_next_state"]
                or row["B_first_step_known_in_historical_A"] is not False
                or row["B_first_step_known_in_augmented_shadow"] is not True):
                raise ValueError("shadow B root has forged physical consequence")
            counters["B_source_roots_known"]+=1
        if (row["baseline_stage6"]["arm"]!="A_ONLY"
            or row["enriched_stage6"]["arm"]!="A_PLUS_B_NON_INGESTIVE"):
            raise ValueError("shadow model arm identity was changed")
        for arm,lookup in (("baseline_stage6",models[p]["A_ONLY"]),
                           ("enriched_stage6",models[p]["A_PLUS_B_NON_INGESTIVE"])):
            out=row[arm]
            available=sum(command_key(before,c) in lookup for c in root_commands)
            count=len(root_commands)
            if (out["root_candidate_edges"]!=count
                or out["root_available_edges"]!=available
                or out["root_unavailable_edges"]!=count-available):
                raise ValueError("Stage6 root availability contradicts physical exact keys")
            dg=out["last_search_diagnostic"]
            expected_diag=(
                "no_predictable_first_step"
                if out["status"]=="incomplete_model" and available==0 and count>0
                else "at_least_one_predictable_first_step"
                if available>0 else "not_classified"
            )
            if (dg["status"]!=out["status"]
                or dg["root_candidate_edges"]!=count
                or dg["root_available_edges"]!=available
                or dg["root_unavailable_edges"]!=count-available
                or dg["root_model_diagnostic"]!=expected_diag
                or dg["partial_progress"]!=out["partial_progress"]
                or out["no_shadow_action_dispatched"] is not True
                or out["berry_b_safety_certified"] is not False
                or out["actual_i0_uc_measured"] is not False
                or out["target_food"]!=float(before["body"]["food"])+5.0):
                raise ValueError("Stage6 diagnostic, safety or UC receipt corrupted")
            if B_EAT in out["predicted_commands"] or B_EAT in out["commands"]:
                raise ValueError("unknown B ingestion falsely included in a plan")
            counters[arm+"_available_root"]+=available>0
            counters[arm+"_"+out["status"]]+=1
        if layout=="B_NONE":
            if (row["baseline_stage6"]!=
                {**row["enriched_stage6"],"arm":"A_ONLY"} or
                row["baseline_stage6"]["commands"][0]!=MOVE_N):
                raise ValueError("B absent control changed A-only plan")
        else:
            base=row["baseline_stage6"]
            added=row["enriched_stage6"]
            expected_first=(B_COLLECT if layout=="B_LOCAL" else MOVE_E)
            expected_full=([B_COLLECT] if layout=="B_LOCAL"
                           else [MOVE_E,B_COLLECT])
            if (base["status"]!="incomplete_model"
                or base["commands"]!=[]
                or base["root_available_edges"]!=0
                or added["status"]!="partial_progress"
                or added["partial_progress"] is not True
                or added["commands"]!=expected_full
                or added["predicted_commands"]!=expected_full
                or added["commands"][0]!=expected_first
                or added["root_available_edges"]!=1):
                raise ValueError("reported B shadow path not supported by corpus")
            counters["B_first_command_selected_in_shadow"]+=1
        if row["first_person_sha256"]!=digest(before):
            raise ValueError("same first-person hash changed during audit")
    if len(group)!=6 or any(
        len(group[(p,l)])!=2 for p in PROFILES for l in LAYOUTS
    ):
        raise ValueError("original six hidden-effect pairs not represented")
    for (p,l),pair in group.items():
        if {x["hidden_effect_for_external_stratification_only"] for x in pair}!=set(HIDDEN):
            raise ValueError("one hidden sibling removed")
        for key in (
            "first_person_root_state","first_person_sha256",
            "A_only_equipment_sha256","augmented_exact_equipment_sha256",
            "baseline_stage6","enriched_stage6",
        ):
            if pair[0][key]!=pair[1][key]:
                raise ValueError("hidden berry toxicity leaked into shadow inputs")
    if (counters["B_source_roots_known"]!=8 or
        counters["B_first_command_selected_in_shadow"]!=8 or
        counters["baseline_stage6_incomplete_model"]!=8 or
        counters["enriched_stage6_partial_progress"]!=12 or
        counters["baseline_stage6_partial_progress"]!=4 or
        counters["baseline_stage6_available_root"]!=4 or
        counters["enriched_stage6_available_root"]!=12):
        raise ValueError("finite branch/negative root coverage not reproduced")
    if (summary.get("schema")!="a230zg-firstperson-lived-root-exact-model-shadow-v1"
        or summary.get("code_sha")!=ZG_SHA
        or summary.get("original_source_run")!=ZB_RUN
        or summary.get("original_roots_B_visible")!=8
        or summary.get("original_ZB_autonomous_steps_reused_read_only")!=384
        or summary.get("separate_detached_physical_worlds")!=6
        or summary.get("physical_A_reference_actions")!=8
        or summary.get("physical_B_non_ingestive_actions")!=6
        or summary.get("actual_shadow_searches")!=24
        or summary.get("B_first_action_selected_in_shadow")!=8
        or summary.get("B_visible_partial_progress")!=8
        or summary.get("exact_B_demonstrations_match_visible_roots")!=8
        or summary.get("model_predicted_B_ingestion_count")!=0
        or summary.get("model_was_installed_in_real_I0") is not False
        or summary.get("no_act_executed_from_shadow") is not True
        or summary.get("new_autonomous_I0_births")!=0
        or summary.get("new_autonomous_I0_steps")!=0
        or summary.get("normative_spec_or_runtime_modified") is not False):
        raise ValueError("original ZG scientific summary silently changed")
    return {
        "schema":"a230zh-archive-only-firstperson-shadow-audit-v1",
        "original_ZG_run":ZG_RUN,
        "original_ZB_run":ZB_RUN,
        "real_original_I0_birth_roots":12,
        "real_original_autonomous_steps_read_only":384,
        "external_physically_applied_train_worlds_from_ZG":6,
        "external_physically_applied_train_steps_from_ZG":14,
        "physical_demonstration_example_hashes_recomputed":14,
        "shadow_stage6_queries_independently_scored":24,
        "visible_B_roots_gain_first_model_edge":counters["B_source_roots_known"],
        "stage6_B_partial_substeps":counters["B_first_command_selected_in_shadow"],
        "baseline_incomplete_with_B_visible":counters[
            "baseline_stage6_incomplete_model"
        ],
        "baseline_A_partial_B_absent":counters[
            "baseline_stage6_partial_progress"
        ],
        "enriched_partial_total":counters[
            "enriched_stage6_partial_progress"
        ],
        "all_hidden_effect_pair_results_identical":True,
        "physical_worldbody_apply_independently_proven_from_archive":False,
        "real_stage6_was_run_in_original_ZG_not_in_ZH":True,
        "new_physical_worlds":0,
        "new_physical_steps":0,
        "new_i0_births":0,
        "new_i0_autonomous_steps":0,
        "no_oracle_or_hidden_B_effect_in_cognitive_input":True,
        "zero_predictions_of_B_ingestion":True,
        "food_safety_proven":False,
        "real_i0_B_food_plan_or_action_proven":False,
        "stage12":"PARTIAL","issue110":"OPEN",
    }


def execute(zg311,zg312,zb311,zb312,out):
    data=load_sources(zg311,zg312,zb311,zb312)
    reviewed=independently_evaluate(*data)
    reviewed.update({
        "original_json_sha256":ZG_FILES,
        "original_ZB_source_json_sha256":ZB_FILES,
        "ZG_python_311_312_output_identical_bytes":True,
        "source_journal_numeric_ulp_divergence_not_suppressed":True,
        "analysis_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    })
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zh-summary.json").write_text(
        json.dumps(reviewed,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZH_SUMMARY "+json.dumps({
        k:v for k,v in reviewed.items()
        if k not in ("original_json_sha256","original_ZB_source_json_sha256")
    },sort_keys=True),flush=True)
    return reviewed


def main():
    ap=argparse.ArgumentParser()
    for p in ("zg311","zg312","zb311","zb312","output_dir"):
        ap.add_argument("--"+p.replace("_","-"),type=Path,required=True)
    a=ap.parse_args()
    execute(a.zg311,a.zg312,a.zb311,a.zb312,a.output_dir)


if __name__=="__main__":
    main()
