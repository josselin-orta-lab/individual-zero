"""A2.30-U independent, archive-only audit of S first-person probes and T shadows.

Does not import either experiment runner, P predictor, WorldBody, Simulator,
I0 cognitive runtime or an Oracle. Reconstructs published physical receipt
hashes, accessible comparisons and external versus lived outcomes. It cannot
prove from JSON alone that the archived WorldBody.apply calls took place.

Preregistered AFTER known S/T results, BEFORE this verifier's code.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

S_RUN = 38740205272
T_RUN = 38741620906
S_SHA = "66772ec2281acfbfb6c4c49858c60837feb6b5da"
T_SHA = "c7dbc4f88619c3c96a583ba8741090417d9d0241"
P_TRAIN_SHA = (
    "f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e"
)
P_WITNESS_SHA = "9315d80ce786d044b332283c4e84f60de1e0b446fb3bd0b4d2abc55c1bd45ce0"
S_FILES = ("a230s-worlds.json","a230s-pairs.json","a230s-summary.json")
T_FILES = ("a230t-worlds.json","a230t-paired.json","a230t-summary.json")
FIELDS = (
    "dx","dy",
    *(f"body.{k}" for k in ("energy","food","water","integrity")),
    *(f"inventory.{k}" for k in ("berry_a","berry_b","wood","stone","tool")),
)
EXPECTED_S = {"FOOD":(12,36),"MOVE":(12,32),"DECAY":(12,36)}
LATENT_FOOD = ("benign","toxin_7","toxin_30","toxin_100","gain_zero")


def digest(data):
    return sha256_hex(canonical_causal_bytes(data))


def sealed_files(folder, names):
    out = {}
    for name in names:
        matches = list(folder.rglob(name))
        if len(matches) != 1:
            raise ValueError("ambiguous/missing historical file "+name)
        out[name] = matches[0].read_bytes()
    return out


def read_equal_archive(a,b,names):
    first = sealed_files(a,names)
    second = sealed_files(b,names)
    if first != second:
        raise ValueError("original 3.11 and 3.12 JSON differ byte-for-byte")
    return ({k:json.loads(v) for k,v in first.items()},
            {k:sha256(v).hexdigest() for k,v in first.items()})


def review_S(worlds, pairs, summary):
    if (summary.get("schema")!="a230s-accessible-probes-physical-v1"
        or summary.get("sha")!=S_SHA
        or summary.get("new_i0_births")!=0
        or summary.get("new_i0_autonomous_steps")!=0
        or summary.get("terminal_postcapture_considered_lived") is not False
        or len(worlds)!=36 or len(pairs)!=36):
        raise ValueError("not the original S source experiment")
    lookup = {}
    by_family = defaultdict(list)
    external_terminals = 0
    for row in worlds:
        ident=row["id"]
        if ident in lookup or not ident.startswith("a230s:"):
            raise ValueError("duplicate or invented S laboratory world")
        lookup[ident] = row
        family=row["family"]
        if family not in EXPECTED_S:
            raise ValueError("unknown S family")
        by_family[family].append(row)
        lived=row["possible_lived_captures"]
        physical=row["external_physical_evidence"]
        if (
            not physical or not lived or lived[0]["after_step"]!=0
            or row["initial_capture_digest"]!=digest(lived[0]["state"])
            or row["postterminal_lived_capture_count"]!=0
            or len(physical)!=row["steps_applied"]
            or len(physical)>3
        ):
            raise ValueError("first-person S provenance inconsistent")
        latest=lived[0]["state"]
        last_terminal=None
        index_lived=1
        for index,observation in enumerate(physical,1):
            payload={k:v for k,v in observation.items() if k!="physical_sha256"}
            if observation["physical_sha256"]!=digest(payload):
                raise ValueError("S physical receipt SHA altered")
            if (
                observation["step"]!=index
                or observation["before"]!=latest
                or observation["command"]!=row["external_physical_evidence"][index-1]["command"]
            ):
                raise ValueError("S physical observation/action order corrupted")
            terminal=observation["terminal_for_external_audit_only"]
            if terminal:
                if index!=len(physical):
                    raise ValueError("physical continuation after S death")
                last_terminal=index
            else:
                if index_lived>=len(lived):
                    raise ValueError("missing living observation")
                snap=lived[index_lived]
                if (snap["after_step"]!=index
                    or snap["state"]!=observation["after_for_external_audit_only"]):
                    raise ValueError("S lived capture not physically grounded")
                latest=snap["state"]
                index_lived+=1
        if index_lived!=len(lived):
            raise ValueError("postterminal physical capture counted as lived")
        if row["terminal_step_external_only"]!=last_terminal:
            raise ValueError("terminal physical evidence contradicted")
        if last_terminal is None and len(physical)!=3:
            raise ValueError("nonterminal S world truncated")
        external_terminals += last_terminal is not None
    if external_terminals!=8 or len(lookup)!=36:
        raise ValueError("original S terminal cohort missing")
    for family,(expected_worlds,expected_steps) in EXPECTED_S.items():
        subset=by_family[family]
        if (len(subset)!=expected_worlds or
            sum(x["steps_applied"] for x in subset)!=expected_steps):
            raise ValueError("S physical step counts do not match protocol")
    found_discriminations=0
    found_indistinguishable=0
    seen_pairs=set()
    for pair in pairs:
        names=tuple(pair["worlds"])
        if len(names)!=2 or any(k not in lookup for k in names):
            raise ValueError("invented S comparison world")
        unique=frozenset(names)
        if unique in seen_pairs:
            raise ValueError("duplicated S physical comparison")
        seen_pairs.add(unique)
        a,b=(lookup[k] for k in names)
        if (a["family"]!=b["family"] or a["family"]!=pair["family"]
            or a["food"]!=b["food"]
            or a["position"]!=b["position"]
            or a["initial_capture_digest"]!=b["initial_capture_digest"]):
            raise ValueError("S comparison hidden alias invalid")
        la={x["after_step"]:x["state"] for x in a["possible_lived_captures"]}
        lb={x["after_step"]:x["state"] for x in b["possible_lived_captures"]}
        difference=next(
            (i for i in sorted(la.keys() & lb.keys()) if la[i]!=lb[i]),
            None
        )
        exposure={"FOOD":3,"MOVE":2,"DECAY":1}[pair["family"]]
        if (pair["first_mutually_lived_difference"]!=difference
            or pair["exposure_step"]!=exposure
            or pair["discrimination_before_exposure"]!=(
                difference is not None and difference<exposure
            )
            or difference==0):
            raise ValueError("S discrimination evidence is fabricated")
        found_discriminations += difference is not None
        found_indistinguishable += difference is None
    if (
        found_discriminations!=summary["jointly_lived_differences"]
        or found_indistinguishable!=summary["jointly_lived_nonidentifications"]
        or sum(row["steps_applied"] for row in worlds)!=104
        or len(seen_pairs)!=36
    ):
        raise ValueError("S summary differs from independent first-person audit")
    return {
        "worlds":36,"physical_receipts":104,
        "external_terminals":external_terminals,
        "paired_first_person_contrasts":36,
        "mutually_observable_differences":found_discriminations,
        "undistinguishable_due_to_terminal_branch":found_indistinguishable,
        "new_i0_lives":0,
    }


def independent_P_food_branches(p_training):
    witnesses=p_training["training_witnesses"]
    if (len(witnesses)!=48 or
        digest(witnesses)!=P_WITNESS_SHA or
        p_training["training_witness_corpus_sha256"]!=P_WITNESS_SHA):
        raise ValueError("P food training did not originate in sealed prior cohort")
    food=[x for x in witnesses if ":train:EAT:" in x["world_id"]]
    if len(food)!=16:
        raise ValueError("P food branch training cohort not 16 worlds")
    grouped=defaultdict(list)
    for w in food:
        norm=[{
            "terminal":s["terminal"],
            "cumulative_delta":{
                field:round(float(s["cumulative_delta"][field]),8)
                for field in FIELDS
            }
        } for s in w["steps"]]
        grouped[digest(norm)].append(w)
    if len(grouped)!=4:
        raise ValueError("P original EAT group not four physical branches")
    scores=[]
    for fingerprint,examples in sorted(grouped.items()):
        ref=examples[0]
        if len(examples)!=4:
            raise ValueError("P training support count not by four independent worlds")
        second=ref["steps"][1]
        surviving=ref["first_terminal_step"] is None or (
            ref["first_terminal_step"]>2
        )
        food_gain=float(second["cumulative_delta"]["body.food"])
        scores.append({
            "physical_training_worlds":len(examples),
            "observed_first_terminal_step":ref["first_terminal_step"],
            "predicted_food_gain_after_ingestion":food_gain,
            "surviving_food_goal_possible_in_branch":(
                surviving and food_gain>=5.0
            ),
        })
    if not any(x["observed_first_terminal_step"]==2 for x in scores):
        raise ValueError("P original food mortality branch disappeared")
    return scores


def review_T(worlds,pairs,summary,P_food_scores):
    if (summary.get("schema")!="a230t-shadow-food-planning-v1"
        or summary.get("code_sha")!=T_SHA
        or summary.get("sealed_training_archive_sha256")!=P_TRAIN_SHA
        or summary.get("sealed_training_witness_sha256")!=P_WITNESS_SHA
        or summary.get("new_i0_births")!=0
        or summary.get("new_autonomous_i0_steps")!=0
        or len(worlds)!=40 or len(pairs)!=20):
        raise ValueError("wrong original T shadow cohort")
    ids={}
    per_arm=defaultdict(list)
    for row in worlds:
        ident=row["id"]
        if ident in ids or not ident.startswith("a230t:"):
            raise ValueError("duplicate T shadow laboratory world")
        ids[ident]=row
        arm=row["arm"]
        if arm not in ("no_wait","wait_first") or (
            row["latent_external_only"] not in LATENT_FOOD
        ):
            raise ValueError("unknown T shadow protocol arm/latent")
        per_arm[arm].append(row)
        fc=row["shadow_forecast_precommitted"]
        if fc.get("certifies_safe") is not False:
            raise ValueError("T fabricated certainty about hidden world safety")
        if (fc["input_stage3_state"]!=row["decision_stage3_state"]
            or fc["input_digest_sha256"]!=digest(row["decision_stage3_state"])
            or row["shadow_sha256_before_all_food_actions"]!=digest(fc)):
            raise ValueError("T predicted input or sealed shadow receipt falsified")
        if any(name in fc["input_stage3_state"] for name in (
            "hidden_latent", "berry_effects", "lethal_zones", "terminal"
        )):
            raise ValueError("T oracle latent leaked into prior forecast")
        if (fc["branch_scores"]!=P_food_scores
            or fc["observed_terminal_steps"]!=[2]
            or fc["observed_joint_branches"]!=4
            or fc["risk_label"]!="observed_terminal_possible"
            or fc["training_worlds_in_context"]!=16
            or fc["certifies_safe"] is not False
            or fc["uncertainty_unobserved_causes_not_excluded"] is not True):
            raise ValueError("T invented shadow certainty or P outcomes")
        optimistic=any(x["surviving_food_goal_possible_in_branch"]
                       for x in P_food_scores)
        robust=all(x["surviving_food_goal_possible_in_branch"]
                   for x in P_food_scores)
        if (fc["optimistic_goal_exists"]!=optimistic
            or fc["all_observed_branches_survive_and_meet_goal"]!=robust
            or fc["shadow_risk_veto"] is not True):
            raise ValueError("T optimistic goal or risk veto incorrectly scored")
        actions=row["physical_operations_not_chosen_by_shadow"]
        if not actions or len(actions)!=row["real_physical_steps"]:
            raise ValueError("missing physical T motor events")
        expected=["collecter","manger","attendre"] if arm=="no_wait" else (
            ["attendre","collecter","manger","attendre"]
        )
        if [x["command"]["primitive"] for x in actions]!=expected[:len(actions)]:
            raise ValueError("T physics was chosen by model or changed")
        terminals=[x["t_monde"] for x in actions
                   if x["terminal_external_only"]]
        if (len(terminals)>1 or terminals not in (
                [],[2] if arm=="no_wait" else [3]
        ) or (terminals and terminals[0]!=len(actions))):
            raise ValueError("T postmortem execution or false terminal")
        if (arm=="no_wait" and
            row["preprobe_stage3_state"]!=row["decision_stage3_state"]):
            raise ValueError("no_wait decision state was changed")
        if (arm=="wait_first" and
            actions[0]["physical_after"]!=row["decision_stage3_state"]):
            raise ValueError("T waiting observation fabricated")
        if (fc["forecast_time_t_monde"]!=(
                1 if arm=="no_wait" else 2
            ) or row["decision_food"]!=
            row["decision_stage3_state"]["body"]["food"]):
            raise ValueError("T forecast point/food state falsified")
        after_eat=actions[1 if arm=="no_wait" else 2]["physical_after"]
        living=not bool(terminals)
        success=(
            living and (after_eat["body"]["food"]-
                        row["decision_food"]>=5.0)
        )
        if (
            row["physically_alive_after_ingestion"]!=living
            or row["physical_food_goal_with_survival_external"]!=success
            or abs(row["actual_food_gain_after_ingestion_external"]-
                   (after_eat["body"]["food"]-row["decision_food"]))>1e-8
        ):
            raise ValueError("T external food success or survival falsified")
        post=row["potential_lived_post_ingestion_if_survivor"]
        if post!=(after_eat if living else None):
            raise ValueError("T postterminal technical body falsely counted lived")
        if row["no_command_emitted_to_i0"] is not True:
            raise ValueError("T incorrectly asserted actual I0 execution")
    for arm,rows in per_arm.items():
        if len(rows)!=20:
            raise ValueError("T arm not 20 independent lab worlds")
        aggregate={
            "physical_worlds":len(rows),
            "physical_steps":sum(x["real_physical_steps"] for x in rows),
            "shadow_optimistic_goals":sum(
                x["shadow_forecast_precommitted"]["optimistic_goal_exists"]
                for x in rows
            ),
            "shadow_observed_branch_robust_goals":sum(
                x["shadow_forecast_precommitted"]
                ["all_observed_branches_survive_and_meet_goal"] for x in rows
            ),
            "shadow_risk_veto":sum(
                x["shadow_forecast_precommitted"]["shadow_risk_veto"]
                for x in rows
            ),
            "physical_surviving_food_goal":sum(
                x["physical_food_goal_with_survival_external"] for x in rows
            ),
            "external_terminal_worlds":sum(
                x["terminal_step_external_only"] is not None for x in rows
            ),
            "optimistic_false_food_success_external":sum(
                x["shadow_forecast_precommitted"]["optimistic_goal_exists"]
                and not x["physical_food_goal_with_survival_external"] for x in rows
            ),
        }
        if aggregate!=summary["per_arm"][arm]:
            raise ValueError("T per-arm metrics not independently reproducible")
    compared=set()
    for p in pairs:
        names=(p["no_wait_id"],p["wait_first_id"])
        if names[0] not in ids or names[1] not in ids:
            raise ValueError("T paired invisible world not registered")
        a,b=ids[names[0]],ids[names[1]]
        if a["arm"]!="no_wait" or b["arm"]!="wait_first":
            raise ValueError("T paired incorrectly by arm")
        key=(a["latent_external_only"],a["starting_food"],
             tuple(a["starting_position"]))
        if key in compared:
            raise ValueError("T comparison duplicated")
        compared.add(key)
        if (a["preprobe_stage3_state"]!=b["preprobe_stage3_state"]
            or a["shadow_forecast_precommitted"]["context_group_key"]!=
                b["shadow_forecast_precommitted"]["context_group_key"]
            or a["physical_food_goal_with_survival_external"]!=
                b["physical_food_goal_with_survival_external"]):
            raise ValueError("T waiting wrongly improved latent knowledge or food result")
        last_a=a["physical_operations_not_chosen_by_shadow"][-1]["physical_after"]["body"]
        last_b=b["physical_operations_not_chosen_by_shadow"][-1]["physical_after"]["body"]
        if any(abs(last_b[k]-last_a[k]-diff)>1e-8 for k,diff in
               (("food",-0.5),("energy",-0.5),("water",-0.2))):
            raise ValueError("T real physical waiting cost falsified")
    if len(compared)!=20:
        raise ValueError("T physical paired controls incomplete")
    if summary["new_lab_physical_steps"]!=132 or summary["external_deaths"]!=8:
        raise ValueError("T total physical counts falsified")
    return {
        "worlds":40,
        "physical_receipts":132,
        "paired_wait_control_worlds":20,
        "known_P_food_training_branches":4,
        "actual_surviving_food_goals":sum(
            x["physical_food_goal_with_survival_external"] for x in worlds
        ),
        "optimistic_proxy_false_successes":sum(
            x["shadow_forecast_precommitted"]["optimistic_goal_exists"]
            and not x["physical_food_goal_with_survival_external"] for x in worlds
        ),
        "external_terminals":sum(
            x["terminal_step_external_only"] is not None for x in worlds
        ),
        "shadow_safety_certificates":0,
        "new_i0_births":0,
    }


def execute(s_a,s_b,t_a,t_b,p_path,output):
    s, s_hashes = read_equal_archive(s_a,s_b,S_FILES)
    t, t_hashes = read_equal_archive(t_a,t_b,T_FILES)
    p=sealed_files(p_path,("a230p-training-manifest.json",))
    if sha256(p["a230p-training-manifest.json"]).hexdigest()!=P_TRAIN_SHA:
        raise ValueError("T baseline P training source is not sealed")
    p_source=json.loads(p["a230p-training-manifest.json"])
    food_score=independent_P_food_branches(p_source)
    s_recomputed=review_S(
        s["a230s-worlds.json"],s["a230s-pairs.json"],s["a230s-summary.json"]
    )
    t_recomputed=review_T(
        t["a230t-worlds.json"],t["a230t-paired.json"],
        t["a230t-summary.json"],food_score
    )
    results={
        "schema":"a230u-readonly-independent-reanalysis-v1",
        "source_runs":{"S":S_RUN,"T":T_RUN},
        "source_original_code_shas":{"S":S_SHA,"T":T_SHA},
        "analysis_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "source_P_training_sha256":P_TRAIN_SHA,
        "original_source_json_sha256":{"S":s_hashes,"T":t_hashes},
        "cross_python_original_bytes_identical":True,
        "original_S_recalculated":s_recomputed,
        "original_T_recalculated":t_recomputed,
        "new_physical_worlds":0,
        "new_physical_world_steps":0,
        "new_independent_i0_births":0,
        "raw_WorldBody_physics_independently_proven_by_JSON":False,
        "stage12":"PARTIAL",
        "issue110":"OPEN",
        "model_deployment_authorized":False,
    }
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230u-summary.json").write_text(
        json.dumps(results,sort_keys=True,indent=2)+"\n"
    )
    print("A230U_SUMMARY "+json.dumps(results,sort_keys=True),flush=True)
    return results


def main():
    parser=argparse.ArgumentParser()
    for name in ("s-a","s-b","t-a","t-b","p-source","output-dir"):
        parser.add_argument("--"+name,type=Path,required=True)
    args=parser.parse_args()
    execute(args.s_a,args.s_b,args.t_a,args.t_b,args.p_source,args.output_dir)


if __name__=="__main__":
    main()
