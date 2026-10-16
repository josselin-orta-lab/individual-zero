"""A2.30-ZT independent offline SHA-pinned review of original 2-job ZS.

Retrospective, preregistered AFTER known ZS outcomes but BEFORE this code.
Standard library ONLY, no ZS or ZO runner, physics, Stage6, I0 or Oracle
imports. The 2-job chronological guarantee is established by the original
GitHub Actions needs relationship, NOT from any freely written JSON flag.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import unicodedata

ORIGINAL_RUN=38801117723
ORIGINAL_HEAD="804e2ebb653278f18bd85aa364015acffd3bdb0e"
ORIGINAL_PREREG="8ae4f26650bdb5f47f474051763bd8c91aba7afd"
SEALED={
 "a230zs-training-physical.json":"818fbb1679603323ea8641aa6dfc1684c12757877bd9d570a53aa332d0bd551a",
 "a230zs-frozen-model.json":"3ce61a1fe1e490c56e061d1c2a33e78414cbcdc90e672739014903cf6cfb1a8c",
 "a230zs-preaction-forecast-receipts.json":"ba4f471636534aefb2ff86217c73f23c6b57924566b3459583192e91026a395d",
 "a230zs-source-seal.json":"c5157c83a78ad0a3ce2a071e14d05cd6365aff2e1d74caeefdbf3686363241c5",
}
REALIZED={
 "a230zs-realized-physical-worlds.json":"cb88057fd6f45f22f40afeccc8af38d18d020856838102296e64e08ae1dbc926",
 "a230zs-sealed-predictions-scored.json":"0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354",
 "a230zs-summary.json":"fba0cd5523cbbdf4fb30430239202bd164b27afdd92a52382704ced64d29839a",
}
VISIBLE={"schema_version","x","y","body","inventory","current_resources",
         "current_water_source","adjacent","known_shelter_here","is_night"}
BODY={"energy","food","water","integrity"}
INV={"berry_a","berry_b","wood","stone","tool"}
NEIGHBOR={"direction","x","y","passable","resources","water_source","creature"}
DELTAS=("x","y","energy","food","water","inventory_berry_b")
COMMANDS={
 "MOVE_E":{"primitive":"se_deplacer","parameters":{"direction":"east"}},
 "COLLECT_B":{"primitive":"collecter","parameters":{"target":"berry_b"}},
}
PRED_KEYS={"status","estimated","integrity","terminal","next_adjacency","safe"}
RECEIPT_KEYS={"world_id","cohort","preaction_first_person",
              "preaction_first_person_sha256","command","prediction",
              "prediction_sha256","source_model_sha256","training_example_count",
              "had_no_heldout_action_when_sealed",
              "no_hidden_fields_sent_to_predictor","safety_certified"}


def normalize(value):
    if value is None or isinstance(value,(bool,int)):
        return value
    if isinstance(value,str):
        return unicodedata.normalize("NFC",value)
    if isinstance(value,float):
        if not math.isfinite(value):
            raise ValueError("nonfinite causal data")
        return {"$f64":(0.0 if value==0 else value).hex().lower()}
    if type(value) is dict:
        out={}
        for key,item in value.items():
            if type(key) is not str:
                raise ValueError("nonstring normalized key")
            k=unicodedata.normalize("NFC",key)
            if k in out:
                raise ValueError("colliding normalized key")
            out[k]=normalize(item)
        return out
    if type(value) in (list,tuple):
        return [normalize(v) for v in value]
    raise ValueError("noncausal archive value")


def causal_sha(obj):
    return sha256(json.dumps(normalize(obj),sort_keys=True,
        ensure_ascii=False,separators=(",",":"),allow_nan=False
    ).encode("utf-8")).hexdigest()


def original_file(root,name,expected):
    options=list(Path(root).rglob(name))
    if len(options)!=1:
        raise ValueError("missing or duplicated original source "+name)
    raw=options[0].read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise ValueError("original full SHA-256 mismatch for "+name)
    return raw


def read_archives(seal311,real311,seal312,real312):
    all_raw=[]
    for sdir,rdir in ((seal311,real311),(seal312,real312)):
        source={name:original_file(sdir,name,h) for name,h in SEALED.items()}
        result={name:original_file(rdir,name,h) for name,h in REALIZED.items()}
        all_raw.append((source,result))
    if all_raw[0]!=all_raw[1]:
        raise ValueError("Python 3.11 and 3.12 source bytes differ")
    s,r=all_raw[0]
    return (
      json.loads(s["a230zs-source-seal.json"]),
      json.loads(s["a230zs-training-physical.json"]),
      json.loads(s["a230zs-frozen-model.json"]),
      json.loads(s["a230zs-preaction-forecast-receipts.json"]),
      json.loads(r["a230zs-realized-physical-worlds.json"]),
      json.loads(r["a230zs-sealed-predictions-scored.json"]),
      json.loads(r["a230zs-summary.json"]),
    )


def observe(s):
    if type(s) is not dict or set(s)!=VISIBLE:
        raise ValueError("future or hidden data entered firstperson state")
    if (set(s["body"])!=BODY or set(s["inventory"])!=INV
        or len(s["adjacent"])!=4
        or {n["direction"] for n in s["adjacent"]}!={"north","south","east","west"}
        or any(set(n)!=NEIGHBOR for n in s["adjacent"])):
        raise ValueError("malformed visible body or neighbor dimensions")
    return s


def command_label(c):
    for name,valid in COMMANDS.items():
        if c==valid:
            return name
    raise ValueError("not a preregistered noningestive command")


def difference(a,b):
    observe(a)
    observe(b)
    return {
      "x":int(b["x"]-a["x"]),"y":int(b["y"]-a["y"]),
      "energy":round(float(b["body"]["energy"])-float(a["body"]["energy"]),8),
      "food":round(float(b["body"]["food"])-float(a["body"]["food"]),8),
      "water":round(float(b["body"]["water"])-float(a["body"]["water"]),8),
      "inventory_berry_b":int(b["inventory"]["berry_b"]-a["inventory"]["berry_b"]),
    }


def learn_from_sixteen(training):
    if len(training)!=16 or len({x["world_id"] for x in training})!=16:
        raise ValueError("missing source physical training worlds")
    deltas=defaultdict(list)
    exact=set()
    for row in training:
        p=row["physical_example"]
        before=observe(row["preaction_first_person"])
        after=observe(row["postaction_external_only"])
        arm=command_label(row["action_physically_applied"])
        if (row["preregistered_cohort"]!="TRAIN"
          or row["source_or_heldout"]!="external_train"
          or not row["world_id"].startswith("a230zs:")
          or p["command"]!=row["action_physically_applied"]
          or p["state"]!=before or p["observed_next_state"]!=after
          or p["terminal"] is not False
          or row["physical_example_sha256"]!=causal_sha(p)
          or row["preaction_sha256"]!=causal_sha(before)
          or row["command_label"]!=arm
          or row["no_berry_ingestion"] is not True
          or row["no_i0_birth_or_autonomous_step"] is not True
          or row["actual_i0_uc_measured"] is not None
          or row["safety_certificate"] is not None):
            raise ValueError("source training physical receipt was forged")
        k=causal_sha({"state":before,"command":p["command"]})
        if k in exact:
            raise ValueError("duplicate/contradictory training exact key")
        exact.add(k)
        deltas[arm].append(difference(before,after))
    result={}
    for arm in COMMANDS:
        if len(deltas[arm])!=8:
            raise ValueError("source training distribution not balanced")
        numeric={}
        for k in DELTAS:
            options={row[k] for row in deltas[arm]}
            numeric[k]=next(iter(options)) if len(options)==1 else None
        result[arm]={
          "supported_empirical_deltas":numeric,
          "physically_observed_training_examples":8,
          "unresolved_integrity":None,"unresolved_terminality":None,
          "unresolved_new_adjacency":None,"unresolved_food_safety":None,
          "general_safety_claim":False,
        }
    return result,exact


def empty(status):
    return {"status":status,"estimated":None,"integrity":None,
            "terminal":None,"next_adjacency":None,"safe":None}


def independent_predict(model,state,arm):
    observe(state)
    if arm not in COMMANDS or set(model)!=set(COMMANDS):
        raise ValueError("unsupported source model or motor action")
    branch=model[arm]
    if (set(branch)!={"supported_empirical_deltas",
        "physically_observed_training_examples","unresolved_integrity",
        "unresolved_terminality","unresolved_new_adjacency",
        "unresolved_food_safety","general_safety_claim"}
        or set(branch["supported_empirical_deltas"])!=set(DELTAS)
        or any(branch[k] is not None for k in ("unresolved_integrity",
           "unresolved_terminality","unresolved_new_adjacency",
           "unresolved_food_safety"))
        or branch["general_safety_claim"] is not False):
        raise ValueError("unsafe or unsupported partial model dimension")
    d=branch["supported_empirical_deltas"]
    if arm=="COLLECT_B" and "berry_b" not in state["current_resources"]:
        return empty("abstain_ineligible")
    east=next(n for n in state["adjacent"] if n["direction"]=="east")
    if arm=="MOVE_E" and not east["passable"]:
        return empty("abstain_ineligible")
    if any(v is None for v in d.values()):
        return empty("abstain_unstable_training")
    if any(float(state["body"][k])+float(d[k])<0 for k in
           ("energy","food","water")):
        return empty("abstain_clamp")
    pred={
       "x":int(state["x"]+d["x"]),"y":int(state["y"]+d["y"]),
       "energy":round(float(state["body"]["energy"])+d["energy"],8),
       "food":round(float(state["body"]["food"])+d["food"],8),
       "water":round(float(state["body"]["water"])+d["water"],8),
       "inventory_berry_b":int(state["inventory"]["berry_b"]+
                               d["inventory_berry_b"]),
    }
    return {**empty("empirical_partial_not_certified"),"estimated":pred}


def independent_review(seal,training,model_block,receipts,worlds,scores,summary):
    if (seal["schema"]!="a230zs-sealed-source-prediction-commit-v1"
        or seal["state"]!="SEALED_BEFORE_HELDOUT"
        or seal["git_source_sha"]!=ORIGINAL_HEAD
        or seal["preregistered_before_code_sha"]!=ORIGINAL_PREREG
        or seal["physical_train_worlds_applied"]!=16
        or seal["physical_heldout_worlds_created_unacted"]!=104
        or seal["physical_heldout_actions_performed_before_seal"]!=0
        or seal["realizing_process_has_not_run"] is not True
        or seal["no_oracle_to_i0_or_fullstate_model"] is not True):
        raise ValueError("original preaction seal timeline forged")
    expected={
        "training":SEALED["a230zs-training-physical.json"],
        "model":SEALED["a230zs-frozen-model.json"],
        "forecasts":SEALED["a230zs-preaction-forecast-receipts.json"],
    }
    if (seal["source_file_sha256"]!=expected
        or seal["preaction_training_structural_sha256"]!=causal_sha(training)
        or seal["preaction_104_forecast_structural_sha256"]!=causal_sha(receipts)):
        raise ValueError("sealed source SHA / structural provenance wrong")
    model,source_exact=learn_from_sixteen(training)
    if (model_block["model"]!=model
        or model_block["schema"]!="a230zs-before-physical-model-v1"
        or model_block["no_production_i0_installation"] is not True
        or model_block["unresolved_integrity_termination_and_safety"] is not True
        or model_block["model_sha256"]!=causal_sha(model)
        or seal["preaction_model_sha256"]!=causal_sha(model)):
        raise ValueError("original source-model training not independently reproduced")
    if (len(receipts)!=104 or len(worlds)!=104 or len(scores)!=104
        or len({x["world_id"] for x in receipts})!=104
        or len({x["world_id"] for x in worlds})!=104):
        raise ValueError("104 preaction physical worlds not uniquely paired")
    counts=Counter()
    nominal=defaultdict(list)
    normal={}
    hidden=[]
    for rx,world,score in zip(receipts,worlds,scores):
        if set(rx)!=RECEIPT_KEYS:
            raise ValueError("future outcome or hidden data injected into forecast receipt")
        s=observe(rx["preaction_first_person"])
        arm=command_label(rx["command"])
        expected_pred=independent_predict(model,s,arm)
        if (rx["world_id"]!=world["world_id"]
            or not rx["world_id"].startswith("a230zs:")
            or rx["cohort"]!=world["preregistered_cohort"]
            or rx["training_example_count"]!=16
            or rx["had_no_heldout_action_when_sealed"] is not True
            or rx["no_hidden_fields_sent_to_predictor"] is not True
            or rx["safety_certified"] is not False
            or rx["source_model_sha256"]!=causal_sha(model)
            or rx["preaction_first_person_sha256"]!=causal_sha(s)
            or rx["prediction_sha256"]!=causal_sha(rx["prediction"])
            or rx["prediction"]!=expected_pred
            or set(rx["prediction"])!=PRED_KEYS
            or any(rx["prediction"][k] is not None for k in (
                "integrity","terminal","next_adjacency","safe"))
            or world["preaction_first_person"]!=s
            or world["preaction_sha256"]!=rx["preaction_first_person_sha256"]
            or world["action_physically_applied"]!=rx["command"]
            or world["source_or_heldout"]!="previously_unseen_heldout"
            or world["no_i0_birth_or_autonomous_step"] is not True
            or world["no_berry_ingestion"] is not True
            or world["postdeath_lived_capture"] is not None
            or world["actual_i0_uc_measured"] is not None
            or world["safety_certificate"] is not None):
            raise ValueError("source and physical outcomes mispaired or unsafe forecast")
        if causal_sha({"state":s,"command":rx["command"]}) in source_exact:
            raise ValueError("heldout input leaked into frozen exact training")
        p=world["physical_example"]
        after=observe(world["postaction_external_only"])
        if (p["command"]!=rx["command"] or p["state"]!=s
            or p["observed_next_state"]!=after
            or p["terminal"] is not world["physically_terminal_external_only"]
            or world["world_sealed_on_terminal"] is not p["terminal"]
            or world["physical_example_sha256"]!=causal_sha(p)):
            raise ValueError("physically applied source/terminal receipt forged")
        if arm=="COLLECT_B" and "berry_b" not in s["current_resources"]:
            raise ValueError("physically collected invisible B")
        if arm=="MOVE_E" and not next(n["passable"] for n in s["adjacent"]
                                     if n["direction"]=="east"):
            raise ValueError("physically moved into visible obstacle")
        target={
            "x":after["x"],"y":after["y"],
            "energy":after["body"]["energy"],"food":after["body"]["food"],
            "water":after["body"]["water"],
            "inventory_berry_b":after["inventory"]["berry_b"],
        }
        estimated=rx["prediction"]["estimated"]
        matches={k:abs(float(estimated[k])-float(target[k]))<1e-8
                 for k in DELTAS} if estimated is not None else {}
        all_match=all(matches.values()) if matches else None
        injury=round(float(after["body"]["integrity"])-
                     float(s["body"]["integrity"]),8)
        if (score["frozen_empirical_prediction"]!=rx["prediction"]
            or score["actual_partial_target_external_only"]!=target
            or score["component_match_external_scoring_only"]!=matches
            or score["all_six_components_match_external_only"]!=all_match
            or score["physical_integrity_delta_external_only"]!=injury
            or score["physical_terminal_external_only"] is not p["terminal"]
            or score["original_train_model_firstperson_exact_key_known"] is not False
            or score["hidden_cause_never_in_firstperson_prediction"] is not True
            or score["no_hazard_or_safe_inferred"] is not True):
            raise ValueError("retrospective scoring tampered with sealed preaction result")
        cohort=rx["cohort"]
        counts[cohort]+=1
        counts[cohort+"_success"]+=all_match is True
        counts[cohort+"_abstain"]+=rx["prediction"]["status"]=="abstain_clamp"
        counts[cohort+"_death"]+=p["terminal"] is True
        counts[cohort+"_injury"]+=injury<0
        counts[cohort+"_numeric_error"]+=all_match is False
        if cohort=="NOMINAL":
            key=(tuple(world["position_factor_external"]),
                 tuple(world["body_factor_external"]),
                 world["phase_factor_external"],world["command_label"])
            nominal[key].append((rx,world))
            if (world["latent_berry_effect_external_only"]=="benign"
                and tuple(world["body_factor_external"])==(35.0,25.0,30.0)
                and world["phase_factor_external"]==1):
                normal[(tuple(world["position_factor_external"]),
                        world["command_label"])]=rx
        elif cohort=="HIDDEN":
            hidden.append((rx,world))
            hazard=world["hidden_intervention_external_only"]
            counts[hazard+"_deaths"]+=p["terminal"] is True
            counts[hazard+"_injury"]+=injury<0
            counts[hazard+"_numeric_error"]+=all_match is False
    if len(nominal)!=32 or len(hidden)!=24 or len(normal)!=8:
        raise ValueError("hidden B and intervention pairing incomplete")
    for twins in nominal.values():
        if (len(twins)!=2 or
            {x[1]["latent_berry_effect_external_only"] for x in twins}
              !={"benign","toxic_lethal"}
            or twins[0][0]["preaction_first_person"]!=
               twins[1][0]["preaction_first_person"]
            or twins[0][0]["prediction"]!=twins[1][0]["prediction"]
            or twins[0][1]["postaction_external_only"]!=
               twins[1][1]["postaction_external_only"]):
            raise ValueError("nominal hidden B toxicity contaminated forecast")
    for prediction,world in hidden:
        control=normal.get((tuple(world["position_factor_external"]),
                            world["command_label"]))
        if (control is None or
            prediction["preaction_first_person"]!=
                control["preaction_first_person"]
            or prediction["prediction"]!=control["prediction"]):
            raise ValueError("hidden hazard signal leaked into preaction prediction")
    expected_counts={
        "NOMINAL":64,"NOMINAL_success":64,"HIDDEN":24,
        "HIDDEN_death":4,"HIDDEN_injury":8,"HIDDEN_numeric_error":8,
        "BOUNDARY":16,"BOUNDARY_abstain":16,
        "hidden_lethal_east_deaths":4,
        "hidden_danger_here_injury":8,
        "hidden_forced_action_failure_numeric_error":8,
    }
    for k,v in expected_counts.items():
        if counts[k]!=v:
            raise ValueError("independent expected outcome failed: "+k+"="+str(counts[k]))
    if (summary["schema"]!="a230zs-genuinely-preaction-sealed-physical-heldout-v1"
        or summary["git_code_sha"]!=ORIGINAL_HEAD
        or summary["source_prediction_files_sha256"]!=expected
        or summary["source_prediction_seal_sha256"]!=SEALED["a230zs-source-seal.json"]
        or summary["source_model_sha256"]!=causal_sha(model)
        or summary["preaction_heldout_forecast_count"]!=104
        or summary["physically_applied_new_total_worlds"]!=120
        or summary["realized_physical_heldout_worlds_after_seal"]!=104
        or summary["preaction_receipts_verified_before_first_heldout_apply"] is not True
        or summary["ci_seal_job_required_before_realize_job"] is not True
        or summary["true_heldout_forecast_receipt_timing"]!=
           "BEFORE_APPLY_DIFFERENT_CI_JOB"
        or summary["sealed_preaction_statuses"]!={
           "abstain_clamp":16,"empirical_partial_not_certified":88}
        or summary["nominal_six_component_physically_exact"]!=64
        or summary["hazard_hidden_motor_deaths"]!=4
        or summary["hazard_hidden_integrity_injuries"]!=8
        or summary["hazard_forced_primitive_failures"]!=8
        or summary["boundary_abstentions"]!=16
        or summary["safety_certificates_emitted"]!=0
        or summary["new_I0_births"]!=0
        or summary["new_I0_autonomous_steps"]!=0
        or summary["berry_B_ingestions"]!=0):
        raise ValueError("printed ZS summary differs from independent original receipt count")
    return {
        "schema":"a230zt-sealed-two-job-independent-archive-v1",
        "original_run_id":ORIGINAL_RUN,
        "original_head":ORIGINAL_HEAD,
        "original_preregister_commit":ORIGINAL_PREREG,
        "seven_original_sha256":{**SEALED,**REALIZED},
        "original_py311_py312_seven_JSON_byte_identical":True,
        "training_physical_examples_independently_hashed":16,
        "heldout_physical_examples_independently_hashed":104,
        "locked_preaction_predictions_independently_recomputed":104,
        "original_exact_training_heldout_matches":0,
        "nominal_successful_partial_predictions":counts["NOMINAL_success"],
        "source_ineligible_clamp_abstentions":counts["BOUNDARY_abstain"],
        "original_hidden_fatal_motors":counts["HIDDEN_death"],
        "original_hidden_injuries":counts["HIDDEN_injury"],
        "original_forced_numeric_mismatches":counts[
            "hidden_forced_action_failure_numeric_error"
        ],
        "nominal_unobservable_B_twins_identical":len(nominal),
        "hidden_hazard_matched_preaction_controls":len(hidden),
        "preaction_receipts_signed_in_separate_original_CI_job":104,
        "CI_job_order_provable_from_JSON_alone":False,
        "CI_job_order_requires_original_GitHub_run_and_needs":True,
        "reviewer_reexecuted_physics":False,
        "reviewer_new_worlds":0,
        "reviewer_new_physical_actions":0,
        "new_I0_births":0,
        "real_I0_UC_measured":False,
        "motor_or_food_safety_proven":False,
        "A2_30":"PARTIELLE","Stage12":"PARTIAL",
        "issue110_administrative_status":"CLOSED",
        "operator_deployment":"NO-GO",
    }


def run(a,b,c,d,out):
    items=read_archives(a,b,c,d)
    summary=independent_review(*items)
    summary["reviewer_code_sha"]=subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True
    ).strip()
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zt-summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZT_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="seven_original_sha256"
    },sort_keys=True),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    for x in ("seal311","real311","seal312","real312","output_dir"):
        p.add_argument("--"+x.replace("_","-"),type=Path,required=True)
    q=p.parse_args()
    run(q.seal311,q.real311,q.seal312,q.real312,q.output_dir)


if __name__=="__main__":
    main()
