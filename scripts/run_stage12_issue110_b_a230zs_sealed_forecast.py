"""A2.30-ZS: truly preaction-sealed partial forecasts, two CI jobs.

PRE-REGISTERED before implementation at 8ae4f26650bdb5f47f474051763bd8c91aba7afd.

--seal: exactly 16 physical TRAIN WorldBody.apply and ZERO heldout steps;
        freeze 104 first-person forecast receipts to three fsync'ed immutable
        files plus SHA manifest, then process terminates.
--realize: another process in a distinct dependent CI job verifies ALL sealed
           records against fresh unacted WorldBody perceptions BEFORE any
           heldout step; only then physically acts in 104 fresh research
           worlds, scores the PREEXISTING predictions without reissuing one.

No Stage12 I0 subject is born, no B is ingested, no UC is charged to I0,
no Oracle is consulted and no full-state or safety forecast is licensed.
ZO's existing model formula and controlled physical recipes are reused as
preregistered, but source world IDs and physical executions are NEW.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from typing import Any

from i0.equipment import (
    EquipmentCorpus, EquipmentCorpusExample, train_exact_transition_table,
)
from lab.world import WorldBody
from lab.equipment_corpus import EquipmentCorpusRecorder

import run_stage12_issue110_b_a230zo_factorized_heldout as zo
from run_stage12_issue110_b_a230zg_lived_root_shadow import (
    first_person, decode_state,
)

PREREG_SHA="8ae4f26650bdb5f47f474051763bd8c91aba7afd"
SOURCE_PR="210"
EXPECTED_TRAIN=16
EXPECTED_HELDOUT=104
EXPECTED_NOMINAL=64
EXPECTED_HIDDEN=24
EXPECTED_BOUNDARY=16
SEAL_STAGE="SEALED_BEFORE_HELDOUT"
FILES={
    "training":"a230zs-training-physical.json",
    "model":"a230zs-frozen-model.json",
    "forecasts":"a230zs-preaction-forecast-receipts.json",
    "seal":"a230zs-source-seal.json",
}
EXPECTED_SOURCE_KEYS={"training","model","forecasts"}


def digest(payload:Any)->str:
    return zo.digest(payload)


def present_commit():
    return subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True
    ).strip()


def original_recipes():
    train,nominal,hidden,boundary=zo.registered_recipes()
    # A different physical WorldBody life in this ZS experiment. All
    # prespecified positions, interventions, motor primitives remain same.
    groups=tuple(tuple({
        **x,"world_id":x["world_id"].replace("a230zo:","a230zs:",1)
    } for x in family) for family in (train,nominal,hidden,boundary))
    if [len(family) for family in groups] != [16,64,24,16]:
        raise AssertionError("frozen ZO recipe factorial was changed")
    all_rows=sum((list(x) for x in groups),[])
    if len({r["world_id"] for r in all_rows})!=120 or any(
        not r["world_id"].startswith("a230zs:") for r in all_rows
    ):
        raise AssertionError("ZS physical birth IDs reused ZO")
    return groups


def json_bytes(payload):
    return (json.dumps(payload,sort_keys=True,indent=2,
                       ensure_ascii=True)+"\n").encode("utf-8")


def write_once_fsynced(path:Path,contents:bytes):
    # O_EXCL refuses silently overwriting a prior sealed source file.
    with path.open("xb") as file:
        file.write(contents)
        file.flush()
        os.fsync(file.fileno())
    return sha256(contents).hexdigest()


def ensure_source_dir_empty(output_dir:Path):
    output_dir.mkdir(parents=True,exist_ok=False)


def sealed_prediction(model,firstperson,action):
    """The only input to the model is explicitly accessible I0 state + action."""
    state=zo.visible_only(firstperson)
    if action not in zo.ACTIONS:
        raise ValueError("unregistered motor action")
    prediction=zo.partial_forecast(model,state,action)
    if (set(prediction)!={"status","estimated","integrity","terminal",
                          "next_adjacency","safe"} or
        any(prediction[x] is not None for x in (
            "integrity","terminal","next_adjacency","safe"
        ))):
        raise ValueError("full future, terminality or food safety falsely predicted")
    return prediction


def preaction_sensor(recipe):
    """Construct a HELDOUT world but DO NOT call .apply or .record_transition."""
    config,layout=zo.physical_fixture(recipe)
    world=WorldBody(config=config,layout=layout)
    if recipe["intervention"]=="hidden_forced_action_failure":
        # Schedule is set only in the hidden WORLD, before sensory capture.
        world.apply_scenario_event(
            "set_action_failure_schedule",
            {"primitive":zo.COMMAND[recipe["action"]].primitive,
             "schedule":[True]},
        )
    sensed=first_person(world,recipe["t_monde"]).as_dict()
    zo.check_action_eligible(sensed,recipe["action"])
    if any(k not in zo.VISIBLE_KEYS for k in sensed):
        raise ValueError("non-first-person hidden model field")
    return sensed


def expected_heldout_recipes():
    _,nominal,hidden,boundary=original_recipes()
    return tuple(nominal)+tuple(hidden)+tuple(boundary)


def preflight_source_payloads(training,model,receipts):
    if len(training)!=EXPECTED_TRAIN or len(receipts)!=EXPECTED_HELDOUT:
        raise ValueError("source cohort changed during preaction sealing")
    model_sha=digest(model)
    if len({r["world_id"] for r in receipts})!=104:
        raise ValueError("sealed prediction identities collide")
    if model!=zo.fit_partial_empirical(training):
        raise ValueError("source model was not trained only on 16 physical sources")
    for item,recipe in zip(receipts,expected_heldout_recipes()):
        if (set(item)!={
            "world_id","cohort","preaction_first_person",
            "preaction_first_person_sha256","command","prediction",
            "prediction_sha256","source_model_sha256",
            "training_example_count","had_no_heldout_action_when_sealed",
            "no_hidden_fields_sent_to_predictor","safety_certified",
        }
        or item["world_id"]!=recipe["world_id"]
        or item["cohort"]!=recipe["cohort"]
        or item["command"]!=zo.COMMAND[recipe["action"]].as_dict()
        or item["source_model_sha256"]!=model_sha
        or item["training_example_count"]!=EXPECTED_TRAIN
        or item["had_no_heldout_action_when_sealed"] is not True
        or item["no_hidden_fields_sent_to_predictor"] is not True
        or item["safety_certified"] is not False):
            raise ValueError("commit file contains forged physical outcome or label")
        input_state=zo.visible_only(item["preaction_first_person"])
        if (item["preaction_first_person_sha256"]!=digest(input_state)
            or item["prediction_sha256"]!=digest(item["prediction"])
            or item["prediction"]!=sealed_prediction(
                model,input_state,recipe["action"]
            )):
            raise ValueError("prediction was changed after being issued")
    return model_sha


def seal_before_heldout(output_dir:Path):
    ensure_source_dir_empty(output_dir)
    train,_,_,_=original_recipes()
    # Physically apply the ONLY source transitions in this job.
    physical_train=[zo.apply_one(recipe)[0] for recipe in train]
    for row in physical_train:
        if (row["preregistered_cohort"]!="TRAIN"
            or row["source_or_heldout"]!="external_train"
            or row["physical_example"]["terminal"] is not False):
            raise AssertionError("heldout or terminal example entered training")
    model=zo.fit_partial_empirical(physical_train)
    train_corpus=EquipmentCorpus(
        version="a230zs-external-training-16-v1",
        examples=tuple(
            EquipmentCorpusExample(
                family=row["physical_example"]["family"],
                state=decode_state(row["physical_example"]["state"]),
                command=zo.COMMAND[row["command_label"]],
                observed_next_state=decode_state(
                    row["physical_example"]["observed_next_state"]
                ),
                terminal=row["physical_example"]["terminal"],
            )
            for row in physical_train
        ),
    )
    exact=train_exact_transition_table(
        corpus=train_corpus,
        equipment_version="E-a230zs-external-exact-control-v1",
    )
    model_sha=digest(model)
    # All 104 sources are UNACTED. Capturing first-person state is allowed,
    # as in every physical trial; no heldout WorldBody.apply is possible here.
    receipts=[]
    for recipe in expected_heldout_recipes():
        first=preaction_sensor(recipe)
        prediction=sealed_prediction(model,first,recipe["action"])
        receipts.append({
            "world_id":recipe["world_id"],
            "cohort":recipe["cohort"],
            "preaction_first_person":first,
            "preaction_first_person_sha256":digest(first),
            "command":zo.COMMAND[recipe["action"]].as_dict(),
            "prediction":prediction,
            "prediction_sha256":digest(prediction),
            "source_model_sha256":model_sha,
            "training_example_count":EXPECTED_TRAIN,
            "had_no_heldout_action_when_sealed":True,
            "no_hidden_fields_sent_to_predictor":True,
            "safety_certified":False,
        })
    preflight_source_payloads(physical_train,model,receipts)
    model_payload={
        "schema":"a230zs-before-physical-model-v1",
        "model":model,"model_sha256":model_sha,
        "exact_training_equipment_sha256":exact.artifact_digest,
        "no_production_i0_installation":True,
        "unresolved_integrity_termination_and_safety":True,
    }
    source={
        "training":physical_train,
        "model":model_payload,
        "forecasts":receipts,
    }
    sha_bytes={}
    for key,payload in source.items():
        sha_bytes[key]=write_once_fsynced(
            output_dir/FILES[key],json_bytes(payload),
        )
    seal={
        "schema":"a230zs-sealed-source-prediction-commit-v1",
        "state":SEAL_STAGE,
        "preregistered_before_code_sha":PREREG_SHA,
        "git_source_sha":present_commit(),
        "physical_train_worlds_applied":EXPECTED_TRAIN,
        "physical_heldout_worlds_created_unacted":EXPECTED_HELDOUT,
        "physical_heldout_actions_performed_before_seal":0,
        "preaction_model_sha256":model_sha,
        "preaction_training_structural_sha256":digest(physical_train),
        "preaction_104_forecast_structural_sha256":digest(receipts),
        "source_file_sha256":sha_bytes,
        "no_oracle_to_i0_or_fullstate_model":True,
        "realizing_process_has_not_run":True,
        "stage12":"PARTIAL","issue110_administratively_closed":True,
    }
    seal_hash=write_once_fsynced(
        output_dir/FILES["seal"],json_bytes(seal),
    )
    # Every source file has been fsynced. Journal the durable digest.
    print("A230ZS_PREACTION_SEAL "+json.dumps({
        "seal_file_sha256":seal_hash,
        "source_file_sha256":sha_bytes,
        "model_sha256":model_sha,
        "locked_predictions":len(receipts),
        "physically_applied_training_actions":EXPECTED_TRAIN,
        "physically_applied_heldout_actions":0,
        "code_sha":present_commit(),
    },sort_keys=True),flush=True)
    return seal


def read_existing_sealed_source(folder:Path):
    root=Path(folder)
    raw_seal=(root/FILES["seal"]).read_bytes()
    seal=json.loads(raw_seal)
    if (set(seal["source_file_sha256"])!=EXPECTED_SOURCE_KEYS
        or seal.get("schema")!="a230zs-sealed-source-prediction-commit-v1"
        or seal.get("state")!=SEAL_STAGE
        or seal.get("preregistered_before_code_sha")!=PREREG_SHA
        or seal.get("git_source_sha")!=present_commit()
        or seal.get("physical_train_worlds_applied")!=16
        or seal.get("physical_heldout_worlds_created_unacted")!=104
        or seal.get("physical_heldout_actions_performed_before_seal")!=0
        or seal.get("realizing_process_has_not_run") is not True
        or seal.get("no_oracle_to_i0_or_fullstate_model") is not True):
        raise ValueError("tampered or cross-commit preaction seal")
    blocks={}
    for key in ("training","model","forecasts"):
        raw=(root/FILES[key]).read_bytes()
        if sha256(raw).hexdigest()!=seal["source_file_sha256"][key]:
            raise ValueError("sealed source SHA-256 mismatch for "+key)
        blocks[key]=json.loads(raw)
    train=blocks["training"]
    model_block=blocks["model"]
    receipts=blocks["forecasts"]
    model=model_block["model"]
    if (model_block["schema"]!="a230zs-before-physical-model-v1"
        or model_block["no_production_i0_installation"] is not True
        or model_block["unresolved_integrity_termination_and_safety"] is not True
        or model_block["model_sha256"]!=seal["preaction_model_sha256"]
        or seal["preaction_training_structural_sha256"]!=digest(train)
        or seal["preaction_104_forecast_structural_sha256"]!=digest(receipts)
        or model_block["model_sha256"]!=preflight_source_payloads(
            train,model,receipts,
        )):
        raise ValueError("sealed source model or future prediction integrity broken")
    return seal,train,model_block,receipts


def physically_realize_after_seal(source_dir:Path,output_dir:Path):
    # CRITICAL: complete all receipt SHA checks and compare all newly built
    # first-person states BEFORE taking the FIRST heldout world step.
    seal,training,model_block,receipts=read_existing_sealed_source(source_dir)
    original_source_shas=dict(seal["source_file_sha256"])
    preflight=[]
    for rec,recipe in zip(receipts,expected_heldout_recipes()):
        before=preaction_sensor(recipe)
        if (before!=rec["preaction_first_person"]
            or digest(before)!=rec["preaction_first_person_sha256"]
            or rec["world_id"]!=recipe["world_id"]
            or rec["command"]!=zo.COMMAND[recipe["action"]].as_dict()
            or rec["prediction"]!=sealed_prediction(
                model_block["model"],before,recipe["action"]
            )):
            raise ValueError(
                "heldout preaction first-person world differs from sealed forecast"
            )
        preflight.append(rec["preaction_first_person_sha256"])
    if len(preflight)!=104:
        raise ValueError("partial preflight of sealed unexposed worlds")
    if not all(
        rec["prediction"]["safe"] is None
        and rec["prediction"]["terminal"] is None
        and rec["prediction"]["integrity"] is None
        for rec in receipts
    ):
        raise ValueError("preaction forecast incorrectly guaranteed safety")
    output_dir.mkdir(parents=True,exist_ok=False)
    realized=[]
    scored=[]
    # No forecast is CREATED here. All predictions are read from the prior
    # separate GitHub job and are never replaced with observed outcomes.
    source_exact_corps=EquipmentCorpus(
        version="a230zs-external-training-16-v1",
        examples=tuple(
            EquipmentCorpusExample(
                family=x["physical_example"]["family"],
                state=decode_state(x["physical_example"]["state"]),
                command=zo.COMMAND[x["command_label"]],
                observed_next_state=decode_state(
                    x["physical_example"]["observed_next_state"]
                ),
                terminal=x["physical_example"]["terminal"],
            ) for x in training
        ),
    )
    exact=train_exact_transition_table(
        corpus=source_exact_corps,
        equipment_version="E-a230zs-external-exact-control-v1",
    )
    if exact.artifact_digest!=model_block["exact_training_equipment_sha256"]:
        raise ValueError("historical exact source model mutated in second process")
    for recipe,receipt in zip(expected_heldout_recipes(),receipts):
        physical,_=zo.apply_one(recipe)
        if (physical["preaction_first_person"]!=receipt["preaction_first_person"]
            or physical["action_physically_applied"]!=receipt["command"]
            or physical["world_id"]!=receipt["world_id"]
            or digest(receipt["prediction"])!=receipt["prediction_sha256"]):
            raise ValueError("physical receipt cannot join sealed preaction forecast")
        original_preaction=zo.visible_only(receipt["preaction_first_person"])
        actual=zo.visible_only(physical["postaction_external_only"])
        command=zo.COMMAND[recipe["action"]]
        try:
            exact.predict(state=decode_state(original_preaction),command=command)
        except LookupError:
            key_known=False
        else:
            key_known=True
        if key_known:
            raise AssertionError("heldout world was already in exact source Equipment")
        target={
            "x":actual["x"],"y":actual["y"],
            "energy":actual["body"]["energy"],
            "food":actual["body"]["food"],
            "water":actual["body"]["water"],
            "inventory_berry_b":actual["inventory"]["berry_b"],
        }
        pred=receipt["prediction"]
        match={}
        if pred["estimated"] is not None:
            match={
                key:abs(float(pred["estimated"][key])-float(target[key]))<1e-8
                for key in target
            }
        sc={
            "original_train_model_firstperson_exact_key_known":False,
            "frozen_empirical_prediction":pred, # SHA-pinned in earlier CI job
            "actual_partial_target_external_only":target,
            "component_match_external_scoring_only":match,
            "all_six_components_match_external_only":(
                all(match.values()) if match else None
            ),
            "physical_terminal_external_only":physical[
                "physically_terminal_external_only"
            ],
            "physical_integrity_delta_external_only":round(
                float(actual["body"]["integrity"])-
                float(original_preaction["body"]["integrity"]),8
            ),
            "hidden_cause_never_in_firstperson_prediction":True,
            "no_hazard_or_safe_inferred":True,
        }
        realized.append(physical)
        scored.append(sc)
    outcome=zo.review_results(
        training,realized,model_block["model"],scored
    )
    # Prove the files downloaded from prior job remain byte-identical even
    # after all physically hazardous worlds have been observed.
    final_seal,_,_,final_predictions=read_existing_sealed_source(source_dir)
    if (final_seal!=seal or final_predictions!=receipts
        or final_seal["source_file_sha256"]!=original_source_shas):
        raise ValueError("preaction commitments were modified during scoring")
    status_counts=dict(Counter(
        rec["prediction"]["status"] for rec in receipts
    ))
    summary={
        **outcome,
        "schema":"a230zs-genuinely-preaction-sealed-physical-heldout-v1",
        "source_prediction_seal_sha256":sha256(
            (Path(source_dir)/FILES["seal"]).read_bytes()
        ).hexdigest(),
        "source_prediction_files_sha256":original_source_shas,
        "preaction_heldout_forecast_count":len(receipts),
        "preaction_receipts_verified_before_first_heldout_apply":True,
        "source_model_trained_on_physical_worlds_before_heldout":16,
        "realized_physical_heldout_worlds_after_seal":len(realized),
        "physically_applied_new_total_worlds":16+len(realized),
        "ci_seal_job_required_before_realize_job":True,
        "new_process_and_job_for_realization":True,
        "source_source_files_unchanged_after_scoring":True,
        "sealed_preaction_statuses":status_counts,
        "true_heldout_forecast_receipt_timing":"BEFORE_APPLY_DIFFERENT_CI_JOB",
        "source_model_sha256":model_block["model_sha256"],
        "postrealization_physical_receipts_sha256":digest(realized),
        "postrealization_score_sha256":digest(scored),
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "no_oracle_feedback":True,
        "berry_B_ingestions":0,
        "subjective_I0_agency_proven":False,
        "stage12":"PARTIAL","a230":"PARTIELLE",
        "cognitive_deployment":"NO-GO",
        "git_code_sha":present_commit(),
    }
    (output_dir/"a230zs-realized-physical-worlds.json").write_bytes(
        json_bytes(realized)
    )
    (output_dir/"a230zs-sealed-predictions-scored.json").write_bytes(
        json_bytes(scored)
    )
    (output_dir/"a230zs-summary.json").write_bytes(json_bytes(summary))
    print("A230ZS_POSTSEAL_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("by_cohort","source_prediction_files_sha256")
    },sort_keys=True),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--seal",action="store_true")
    modes.add_argument("--realize",action="store_true")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--source-dir",type=Path)
    args=parser.parse_args()
    if args.seal:
        if args.source_dir is not None:
            parser.error("source-dir not allowed in seal phase")
        seal_before_heldout(args.output_dir)
    else:
        if args.source_dir is None:
            parser.error("realize phase requires sealed source-dir")
        physically_realize_after_seal(args.source_dir,args.output_dir)


if __name__=="__main__":
    main()
