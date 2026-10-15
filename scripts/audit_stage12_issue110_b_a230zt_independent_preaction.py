"""A2.30-ZT: independent archive-only review of genuinely preaction sealed ZS.

Only Python standard library. No imports from ZS/ZO runner, lab, i0,
WorldBody, Stage6, Oracle, Bench, or cognitive runtime. The data are the
ORIGINAL byte-pinned GitHub Actions artifacts from run 38801013480, not
recreated physical trials. Full-file SHA-256 anchors precede this code.

This review can establish consistency of original receipts and in-process
causal order, NOT an independent external wall-clock or safe action proof.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import unicodedata

RUN_ID = 38801013480
RUN_HEAD = "0af1868efe158347992e531c48b182cb5ca91644"
PREREG = "e3ee40e9d79cfd3bcc09598556a941c09a571427"
ZS_PREREG = "e642e7f240909c906cc2bb9d045623f4c4afbf35"
ORIGINAL_DIGESTS = {
    "a230zs-physical-training.json":
        "818fbb1679603323ea8641aa6dfc1684c12757877bd9d570a53aa332d0bd551a",
    "a230zs-frozen-training-model.json":
        "ef52706bf956af484e9c8f6f61d02fab39b35c7db876aa6aa5b9c48d3908f788",
    "a230zs-preaction-forecast-chain.jsonl":
        "3294a763fe6a0091770ed95aaa672978f9ca7f186b4ad02ee1b1ce86d5f73fc4",
    "a230zs-heldout-worlds.json":
        "b44e987ca36e792ac1772eb38d8cf0b0d4c97151874d802d761f485c10339cc3",
    "a230zs-postaction-scoring.json":
        "0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354",
    "a230zs-summary.json":
        "c3f8d36f4653a353332685c8f982d6bcdcdc369207e8ff3ae9996d83c8201a74",
    "a230zs.log":
        "5385244c6d4616542926fc237471550eb46039afa08d1c8d857dc4f855b863b4",
}
PRETRAIN_HASH = "d837d17d285c20ac53a55f3f78818d4f2abfa7cd387b6232e3c105bd9ac25171"
GENESIS = "0"*64
ACTIONS = ("MOVE_E","COLLECT_B")
DELTA_NAMES = ("x","y","energy","food","water","inventory_berry_b")
UNKNOWN_FORECAST = ("integrity","terminal","next_adjacency","safe")
UNKNOWN_MODEL = ("unresolved_integrity","unresolved_terminality",
                 "unresolved_new_adjacency","unresolved_food_safety")
STATE_KEYS = {
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
}
BODY_KEYS = {"energy","food","water","integrity"}
INV_KEYS = {"berry_a","berry_b","wood","stone","tool"}
NEIGHBOR_KEYS = {
    "direction","x","y","passable","resources","water_source","creature",
}
COMMANDS = {
    "MOVE_E":{"primitive":"se_deplacer","parameters":{"direction":"east"}},
    "COLLECT_B":{"primitive":"collecter","parameters":{"target":"berry_b"}},
}
PRE_KEYS = {
    "world_token","t_monde","source_training_model_sha256",
    "source_training_file_sha256","preaction_accessible_state",
    "preaction_accessible_sha256","firstperson_eligible_command",
    "command_label","frozen_partial_forecast",
    "no_hidden_world_parameters_in_forecast",
    "no_oracle_or_i0_uc_receipt","no_action_yet_executed_for_this_world",
}
POST_KEYS = {
    "world_token","world_id_external_only","cohort_external_only",
    "latent_B_external_only","intervention_external_only",
    "linked_preaction_event_sha256","linked_preaction_accessible_sha256",
    "source_training_model_sha256","action_physically_applied",
    "physical_example","physical_example_sha256","physical_terminal_external_only",
    "postaction_external_only","world_terminal_frozen",
    "postterminal_lived_capture","no_i0_birth_or_autonomous_step",
}
HELDOUT_KEYS = {
    "world_id","preregistered_cohort","source_or_heldout",
    "position_factor_external","body_factor_external","phase_factor_external",
    "command_label","latent_berry_effect_external_only",
    "hidden_intervention_external_only","physical_config_sha256_external_only",
    "physical_layout_sha256_external_only","preaction_first_person",
    "preaction_sha256","action_physically_applied","physical_example",
    "physical_example_sha256","postaction_external_only",
    "physically_terminal_external_only","postdeath_lived_capture",
    "world_sealed_on_terminal","no_i0_birth_or_autonomous_step",
    "no_berry_ingestion","actual_i0_uc_measured",
    "no_oracle_or_hidden_input_to_prediction","safety_certificate",
    "forecast_preaction_event_sha256","outcome_external_event_sha256",
}
TRAIN_KEYS = HELDOUT_KEYS - {
    "forecast_preaction_event_sha256","outcome_external_event_sha256",
}
SCORE_KEYS = {
    "original_train_model_firstperson_exact_key_known",
    "frozen_empirical_prediction","actual_partial_target_external_only",
    "component_match_external_scoring_only",
    "all_six_components_match_external_only",
    "physical_terminal_external_only",
    "physical_integrity_delta_external_only",
    "hidden_cause_never_in_firstperson_prediction",
    "no_hazard_or_safe_inferred",
}


def _normalize(value):
    """Independently implement normative canonical UTF-8 + $f64 contract."""
    if value is None or isinstance(value,(bool,int)):
        return value
    if isinstance(value,str):
        return unicodedata.normalize("NFC",value)
    if isinstance(value,float):
        if not math.isfinite(value):
            raise ValueError("nonfinite forensic causal float")
        return {"$f64":(0.0 if value==0.0 else value).hex().lower()}
    if isinstance(value,dict):
        outcome={}
        for key,part in value.items():
            if not isinstance(key,str):
                raise TypeError("causal map key not a string")
            normalized_key=unicodedata.normalize("NFC",key)
            if normalized_key in outcome:
                raise ValueError("NFC causal keys collide")
            outcome[normalized_key]=_normalize(part)
        return outcome
    if isinstance(value,(tuple,list)):
        return [_normalize(p) for p in value]
    raise TypeError("unsupported forensic causal value")


def evidence_sha(value):
    norm=_normalize(value)
    raw=json.dumps(
        norm,ensure_ascii=False,sort_keys=True,
        separators=(",",":"),allow_nan=False,
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def read_original(root,name,expected):
    files=list(Path(root).rglob(name))
    if len(files)!=1:
        raise ValueError("original sealed source file absent or duplicated: "+name)
    content=files[0].read_bytes()
    if sha256(content).hexdigest()!=expected:
        raise ValueError("original sealed source SHA mismatch: "+name)
    return content


def load_two_original_artifacts(root311,root312):
    archives=[]
    for root in (root311,root312):
        archive={
            name:read_original(root,name,full)
            for name,full in ORIGINAL_DIGESTS.items()
        }
        archives.append(archive)
    if archives[0]!=archives[1]:
        raise ValueError("original Python ZS archives differ byte for byte")
    original=archives[0]
    data={
        "training":json.loads(original["a230zs-physical-training.json"]),
        "freeze":json.loads(original["a230zs-frozen-training-model.json"]),
        "events":[json.loads(line) for line in
                  original["a230zs-preaction-forecast-chain.jsonl"].splitlines()],
        "heldout":json.loads(original["a230zs-heldout-worlds.json"]),
        "scores":json.loads(original["a230zs-postaction-scoring.json"]),
        "summary":json.loads(original["a230zs-summary.json"]),
        "log":original["a230zs.log"].decode("utf-8"),
    }
    return data


def valid_state(state):
    if type(state) is not dict or set(state)!=STATE_KEYS:
        raise ValueError("hidden, future or missing first-person field")
    if (set(state["body"])!=BODY_KEYS
        or set(state["inventory"])!=INV_KEYS
        or not isinstance(state["adjacent"],list)
        or len(state["adjacent"])!=4
        or {n["direction"] for n in state["adjacent"]}!=
           {"north","south","east","west"}
        or any(set(n)!=NEIGHBOR_KEYS for n in state["adjacent"])
        or not isinstance(state["current_resources"],list)
        or state["schema_version"]!="stage6-simulation-state-v1"):
        raise ValueError("invalid first-person body/neighbor schema")
    if any(type(state["body"][key]) not in (int,float) for key in BODY_KEYS):
        raise ValueError("unverifiable first-person bodily value")
    if type(state["x"]) is not int or type(state["y"]) is not int:
        raise ValueError("physical geometry falsely presented as first-person input")
    if (type(state["is_night"]) is not bool or
        type(state["known_shelter_here"]) is not bool or
        type(state["current_water_source"]) is not bool):
        raise ValueError("invalid visible flags")
    return state


def check_eligible(firstperson,action):
    valid_state(firstperson)
    if action not in ACTIONS:
        raise ValueError("unknown preregistered source primitive")
    if action=="COLLECT_B" and "berry_b" not in firstperson["current_resources"]:
        raise ValueError("nonvisible berry collection illicitly predicted")
    if action=="MOVE_E":
        east=next(x for x in firstperson["adjacent"] if x["direction"]=="east")
        if not east["passable"]:
            raise ValueError("visibly blocked east command not eligible")
    return COMMANDS[action]


def preregistered_recipes():
    """Closed independent reimplementation of the ZO/ZS matrix."""
    positions_train=((5,5),(7,7))
    positions_hold=((9,9),(11,11),(13,13),(15,15))
    bodies_nominal=((35.0,25.0,30.0),(70.0,55.0,65.0))
    phases=(1,201)
    def recipe(cohort,pos,body,phase,act,hidden="benign",intervention="none"):
        return {
            "world_id":(
                f"a230zs:{cohort}:x{pos[0]}y{pos[1]}:"
                f"e{body[0]}f{body[1]}w{body[2]}:"
                f"t{phase}:{act}:B{hidden}:{intervention}"
            ),
            "preregistered_cohort":cohort,
            "position_factor_external":list(pos),
            "body_factor_external":list(body),
            "phase_factor_external":phase,
            "command_label":act,
            "latent_berry_effect_external_only":hidden,
            "hidden_intervention_external_only":intervention,
        }
    training=[
        recipe("TRAIN",pos,(50.0,float(food),40.0),phase,act)
        for pos,food,phase,act in product(
            positions_train,(35.0,45.0),phases,ACTIONS,
        )
    ]
    nominal=[
        recipe("NOMINAL",pos,body,phase,act,hidden)
        for pos,body,phase,act,hidden in product(
            positions_hold,bodies_nominal,phases,ACTIONS,
            ("benign","toxic_lethal"),
        )
    ]
    hidden=[
        recipe("HIDDEN",pos,bodies_nominal[0],1,act,
               intervention=variant)
        for pos,act,variant in product(
            positions_hold,ACTIONS,
            ("hidden_lethal_east","hidden_danger_here",
             "hidden_forced_action_failure"),
        )
    ]
    boundary=[
        recipe("BOUNDARY",pos,(0.5,0.25,0.1),phase,act)
        for pos,act,phase in product(positions_hold,ACTIONS,phases)
    ]
    assert list(map(len,(training,nominal,hidden,boundary)))==[16,64,24,16]
    return training,nominal+hidden+boundary


def check_physical_row(row,registered,source_type,physical_family=None):
    """Only visible inputs can train; external cause used solely by scorer."""
    keys=TRAIN_KEYS if source_type=="training" else HELDOUT_KEYS
    if type(row) is not dict or set(row)!=keys:
        raise ValueError("unexpected or missing physical receipt field")
    if any(row[k]!=v for k,v in registered.items()):
        raise ValueError("physical world provenance does not match preregistration")
    if row["source_or_heldout"]!=(
        "external_train" if source_type=="training"
        else "previously_unseen_heldout"
    ):
        raise ValueError("training-vs-heldout source contamination")
    pre=valid_state(row["preaction_first_person"])
    example=row["physical_example"]
    if (type(example) is not dict or set(example)!={
        "family","state","command","observed_next_state","terminal"
    } or example["state"]!=pre or
        example["command"]!=check_eligible(pre,row["command_label"]) or
        row["action_physically_applied"]!=example["command"] or
        example["observed_next_state"]!=row["postaction_external_only"] or
        example["terminal"]!=row["physically_terminal_external_only"] or
        row["world_sealed_on_terminal"]!=example["terminal"] or
        row["preaction_sha256"]!=evidence_sha(pre) or
        row["physical_example_sha256"]!=evidence_sha(example)):
        raise ValueError("physical state/action/event checksum inconsistent")
    valid_state(example["observed_next_state"])
    if example["family"]!=(
        "a230zo-externally-controlled-one-step-"+row["command_label"]
        if source_type=="training" else
        "a230zs-independent-noningestive-"+row["command_label"]
    ):
        raise ValueError("physical source family was replaced")
    if (row["no_i0_birth_or_autonomous_step"] is not True or
        row["no_berry_ingestion"] is not True or
        row["no_oracle_or_hidden_input_to_prediction"] is not True or
        row["postdeath_lived_capture"] is not None or
        row["actual_i0_uc_measured"] is not None or
        row["safety_certificate"] is not None):
        raise ValueError("false lived, Oracle, UC, ingestion or safety evidence")
    if (pre["x"],pre["y"])!=tuple(row["position_factor_external"]):
        raise ValueError("world's original position is not its perception")
    if (
        [float(pre["body"][key]) for key in ("energy","food","water")] !=
        row["body_factor_external"]
    ):
        raise ValueError("visible body differs from prespecified physical birth")
    if row["phase_factor_external"] not in (1,201):
        raise ValueError("nonregistered observed t_monde")
    return pre,example["observed_next_state"]


def reconstruct_model(training):
    registered,_=preregistered_recipes()
    if len(training)!=16:
        raise ValueError("training-only cohort count not sixteen")
    seen=set()
    table=defaultdict(list)
    keys=set()
    for row,recipe in zip(training,registered):
        pre,after=check_physical_row(row,recipe,"training")
        if row["world_id"] in seen:
            raise ValueError("training individual world duplicated")
        seen.add(row["world_id"])
        keys.add(evidence_sha({
            "state":pre,"command":row["action_physically_applied"],
        }))
        delta={
            "x":after["x"]-pre["x"],
            "y":after["y"]-pre["y"],
            "energy":round(after["body"]["energy"]-pre["body"]["energy"],8),
            "food":round(after["body"]["food"]-pre["body"]["food"],8),
            "water":round(after["body"]["water"]-pre["body"]["water"],8),
            "inventory_berry_b":after["inventory"]["berry_b"]-
                                 pre["inventory"]["berry_b"],
        }
        table[row["command_label"]].append(delta)
    if set(table)!=set(ACTIONS) or any(len(table[a])!=8 for a in ACTIONS):
        raise ValueError("training per-command distribution corrupted")
    model={}
    for act in ACTIONS:
        empirical={}
        for key in DELTA_NAMES:
            values={x[key] for x in table[act]}
            empirical[key]=next(iter(values)) if len(values)==1 else None
        model[act]={
            "supported_empirical_deltas":empirical,
            "physically_observed_training_examples":len(table[act]),
            "unresolved_integrity":None,
            "unresolved_terminality":None,
            "unresolved_new_adjacency":None,
            "unresolved_food_safety":None,
            "general_safety_claim":False,
        }
    if evidence_sha(model)!=PRETRAIN_HASH:
        raise ValueError("model trained from source deviated from sealed fingerprint")
    return model,keys


def reconstruct_forecast(model,pre,act):
    """Strict source-only numeric forecast; NEVER predicts death or safety."""
    check_eligible(pre,act)
    if set(model)!=set(ACTIONS):
        raise ValueError("source model contains unexpected actions")
    row=model[act]
    if (set(row)!={
        "supported_empirical_deltas","physically_observed_training_examples",
        "unresolved_integrity","unresolved_terminality",
        "unresolved_new_adjacency","unresolved_food_safety",
        "general_safety_claim"
    } or any(row[k] is not None for k in UNKNOWN_MODEL) or
        row["general_safety_claim"] is not False or
        row["physically_observed_training_examples"]!=8):
        raise ValueError("source model contains false safety evidence")
    delta=row["supported_empirical_deltas"]
    if set(delta)!=set(DELTA_NAMES):
        raise ValueError("unknown physical or hidden dimension used for forecast")
    if any(delta[k] is None for k in DELTA_NAMES):
        return {"status":"abstain_unstable_training","estimated":None,
                **{k:None for k in UNKNOWN_FORECAST}}
    if any(pre["body"][name]+delta[name]<0.0 for name in ("energy","food","water")):
        return {"status":"abstain_clamp","estimated":None,
                **{k:None for k in UNKNOWN_FORECAST}}
    estimated={
        "x":int(pre["x"]+delta["x"]),
        "y":int(pre["y"]+delta["y"]),
        "energy":round(pre["body"]["energy"]+delta["energy"],8),
        "food":round(pre["body"]["food"]+delta["food"],8),
        "water":round(pre["body"]["water"]+delta["water"],8),
        "inventory_berry_b":int(pre["inventory"]["berry_b"]+
                                delta["inventory_berry_b"]),
    }
    return {
        "status":"empirical_partial_not_certified",
        "estimated":estimated,
        **{k:None for k in UNKNOWN_FORECAST},
    }


def verify_ledger(events):
    if type(events) is not list or len(events)!=208:
        raise ValueError("missing or duplicated ledger events")
    head=GENESIS
    for idx,ev in enumerate(events):
        if (type(ev) is not dict or
            set(ev)!={"seq","prev_sha256","kind","payload","event_sha256"} or
            type(ev["seq"]) is not int or ev["seq"]!=idx+1 or
            ev["prev_sha256"]!=head or
            ev["kind"]!=(
                "prediction_committed" if idx%2==0 else "outcome_sealed"
            ) or
            type(ev["payload"]) is not dict):
            raise ValueError("durable preaction event order violated")
        expected=evidence_sha({
            k:ev[k] for k in ("seq","prev_sha256","kind","payload")
        })
        if ev["event_sha256"]!=expected:
            raise ValueError("sealed SHA-256 causal ledger was altered")
        head=expected
    return head


def verify_dataset(training,freeze,events,heldout,scores,summary,log,
                   freeze_file_sha=None):
    """Fully independent review; never calls ZS code, simulator or Oracle."""
    model,known_source_keys=reconstruct_model(training)
    if freeze_file_sha is None:
        freeze_file_sha=ORIGINAL_DIGESTS["a230zs-frozen-training-model.json"]
    if (type(freeze) is not dict or set(freeze)!={
        "schema","preregistered_protocol_sha","model","model_sha256",
        "exact_equipment_source_sha256","training_physical_source_sha256",
        "training_file_sha256","training_worlds",
        "training_examples_per_command","unknown_dimensions",
        "contains_no_heldout_worlds","no_production_i0_model_contract"
    } or freeze["schema"]!="a230zs-locked-before-heldout-v1"
        or freeze["preregistered_protocol_sha"]!=ZS_PREREG
        or freeze["model"]!=model
        or freeze["model_sha256"]!=PRETRAIN_HASH
        or freeze["training_physical_source_sha256"]!=evidence_sha(training)
        or freeze["training_file_sha256"]!=
           ORIGINAL_DIGESTS["a230zs-physical-training.json"]
        or freeze["training_examples_per_command"]!={"MOVE_E":8,"COLLECT_B":8}
        or freeze["training_worlds"]!=16
        or freeze["unknown_dimensions"]!=list(UNKNOWN_FORECAST)
        or freeze["contains_no_heldout_worlds"] is not True
        or freeze["no_production_i0_model_contract"] is not True
        or len(freeze["exact_equipment_source_sha256"])!=64):
        raise ValueError("frozen 16-example training-only model was tampered")
    head=verify_ledger(events)
    if (type(heldout) is not list or len(heldout)!=104 or
        type(scores) is not list or len(scores)!=104):
        raise ValueError("heldout prospective physical or scoring cohort incomplete")
    _,recipes=preregistered_recipes()
    seen=set(r["world_id"] for r in training)
    totals=Counter()
    by_cohort=defaultdict(Counter)
    nominal_pairs=defaultdict(list)
    nominal_by_key={}
    for idx,(row,recipe,score) in enumerate(zip(heldout,recipes,scores)):
        pre,after=check_physical_row(row,recipe,"heldout")
        if row["world_id"] in seen:
            raise ValueError("duplicate training or heldout physical identity")
        seen.add(row["world_id"])
        pre_ev,post_ev=events[idx*2:idx*2+2]
        pre_payload=pre_ev["payload"]
        post_payload=post_ev["payload"]
        token=f"a230zs-heldout-{idx+1:03d}"
        if (set(pre_payload)!=PRE_KEYS or set(post_payload)!=POST_KEYS):
            raise ValueError("unknown source, future or hidden field in preaction receipt")
        if (pre_payload["world_token"]!=token or
            post_payload["world_token"]!=token or
            pre_payload["t_monde"]!=row["phase_factor_external"] or
            pre_payload["source_training_model_sha256"]!=PRETRAIN_HASH or
            post_payload["source_training_model_sha256"]!=PRETRAIN_HASH or
            pre_payload["source_training_file_sha256"]!=freeze_file_sha or
            pre_payload["preaction_accessible_state"]!=pre or
            pre_payload["preaction_accessible_sha256"]!=evidence_sha(pre) or
            pre_payload["firstperson_eligible_command"]!=row["action_physically_applied"] or
            pre_payload["command_label"]!=row["command_label"] or
            pre_payload["no_hidden_world_parameters_in_forecast"] is not True or
            pre_payload["no_oracle_or_i0_uc_receipt"] is not True or
            pre_payload["no_action_yet_executed_for_this_world"] is not True):
            raise ValueError("forecast was not committed on the correct first-person state")
        forecast=reconstruct_forecast(model,pre,row["command_label"])
        if (pre_payload["frozen_partial_forecast"]!=forecast or
            set(forecast)!={"status","estimated",*UNKNOWN_FORECAST} or
            any(forecast[k] is not None for k in UNKNOWN_FORECAST)):
            raise ValueError("forecast not identical to sealed model-only calculation")
        if (post_payload["world_id_external_only"]!=row["world_id"] or
            post_payload["cohort_external_only"]!=row["preregistered_cohort"] or
            post_payload["latent_B_external_only"]!=row["latent_berry_effect_external_only"] or
            post_payload["intervention_external_only"]!=row["hidden_intervention_external_only"] or
            post_payload["linked_preaction_event_sha256"]!=pre_ev["event_sha256"] or
            post_payload["linked_preaction_accessible_sha256"]!=evidence_sha(pre) or
            post_payload["action_physically_applied"]!=row["action_physically_applied"] or
            post_payload["physical_example"]!=row["physical_example"] or
            post_payload["physical_example_sha256"]!=row["physical_example_sha256"] or
            post_payload["physical_terminal_external_only"]!=row["physically_terminal_external_only"] or
            post_payload["postaction_external_only"]!=after or
            post_payload["world_terminal_frozen"]!=row["world_sealed_on_terminal"] or
            post_payload["postterminal_lived_capture"] is not None or
            post_payload["no_i0_birth_or_autonomous_step"] is not True or
            row["forecast_preaction_event_sha256"]!=pre_ev["event_sha256"] or
            row["outcome_external_event_sha256"]!=post_ev["event_sha256"]):
            raise ValueError("physical consequence not joined to prior prediction")
        if (row["physical_example"]["terminal"] and
            (row["postdeath_lived_capture"] is not None or
             post_payload["postterminal_lived_capture"] is not None)):
            raise ValueError("invented postmortem first-person experience")
        exact_key=evidence_sha({
            "state":pre,"command":row["action_physically_applied"],
        })
        if exact_key in known_source_keys:
            raise ValueError("heldout example was part of train exact-key corpus")
        target={
            "x":after["x"],"y":after["y"],
            "energy":after["body"]["energy"],
            "food":after["body"]["food"],
            "water":after["body"]["water"],
            "inventory_berry_b":after["inventory"]["berry_b"],
        }
        match=({k:abs(float(forecast["estimated"][k])-float(target[k]))<1e-8
                for k in DELTA_NAMES}
               if forecast["estimated"] is not None else {})
        if (type(score) is not dict or set(score)!=SCORE_KEYS or
            score["original_train_model_firstperson_exact_key_known"] is not False or
            score["frozen_empirical_prediction"]!=forecast or
            score["actual_partial_target_external_only"]!=target or
            score["component_match_external_scoring_only"]!=match or
            score["all_six_components_match_external_only"]!=(
                all(match.values()) if match else None
            ) or score["physical_terminal_external_only"]!=row["physically_terminal_external_only"] or
            score["physical_integrity_delta_external_only"]!=round(
                after["body"]["integrity"]-pre["body"]["integrity"],8
            ) or score["hidden_cause_never_in_firstperson_prediction"] is not True or
            score["no_hazard_or_safe_inferred"] is not True):
            raise ValueError("independent postaction numerical score was falsified")
        cohort=row["preregistered_cohort"]
        by_cohort[cohort]["worlds"]+=1
        by_cohort[cohort]["physical_steps"]+=1
        by_cohort[cohort]["terminal"]+=row["physically_terminal_external_only"]
        by_cohort[cohort]["injury"]+=(
            score["physical_integrity_delta_external_only"]<0
        )
        by_cohort[cohort]["predicted"]+=(
            forecast["status"]=="empirical_partial_not_certified"
        )
        by_cohort[cohort]["abstain_clamp"]+=(
            forecast["status"]=="abstain_clamp"
        )
        by_cohort[cohort]["all_numeric_exact"]+=(
            score["all_six_components_match_external_only"] is True
        )
        by_cohort[cohort]["numeric_mismatch"]+=(
            score["all_six_components_match_external_only"] is False
        )
        if cohort=="NOMINAL":
            key=(
                tuple(row["position_factor_external"]),
                tuple(row["body_factor_external"]),
                row["phase_factor_external"],row["command_label"],
            )
            nominal_pairs[key].append((row,forecast))
            if (row["latent_berry_effect_external_only"]=="benign"
                and tuple(row["body_factor_external"])==(35.0,25.0,30.0)
                and row["phase_factor_external"]==1):
                nominal_by_key[
                    (tuple(row["position_factor_external"]),row["command_label"])
                ]=row["preaction_first_person"]
        if cohort=="HIDDEN":
            intervention=row["hidden_intervention_external_only"]
            by_cohort[intervention]["worlds"]+=1
            by_cohort[intervention]["terminal"]+=row["physically_terminal_external_only"]
            by_cohort[intervention]["injury"]+=(
                score["physical_integrity_delta_external_only"]<0
            )
            by_cohort[intervention]["numeric_mismatch"]+=(
                score["all_six_components_match_external_only"] is False
            )
        totals["verified_pairs"]+=1
        totals["numerical_forecasts"]+=(
            forecast["status"]=="empirical_partial_not_certified"
        )
        totals["abstentions"]+=(forecast["status"]=="abstain_clamp")
    if len(seen)!=120:
        raise ValueError("precommitted distinct physical world count incorrect")
    if len(nominal_pairs)!=32:
        raise ValueError("latent B nominal pair count incorrect")
    for pair,two in nominal_pairs.items():
        if (len(two)!=2 or
            {r["latent_berry_effect_external_only"] for r,_ in two}!=
                {"benign","toxic_lethal"} or
            two[0][0]["preaction_first_person"]!=
                two[1][0]["preaction_first_person"] or
            two[0][0]["postaction_external_only"]!=
                two[1][0]["postaction_external_only"] or
            two[0][1]!=two[1][1]):
            raise ValueError("hidden B toxicity falsely appeared before ingestion")
    for row in heldout:
        if row["preregistered_cohort"]=="HIDDEN":
            key=(tuple(row["position_factor_external"]),row["command_label"])
            if row["preaction_first_person"]!=nominal_by_key.get(key):
                raise ValueError("hidden motor hazard leaked into preaction observation")
    expected={
        "NOMINAL":{"worlds":64,"terminal":0,"injury":0,
                   "predicted":64,"all_numeric_exact":64},
        "HIDDEN":{"worlds":24,"terminal":4,"injury":8,
                  "predicted":24,"numeric_mismatch":8},
        "BOUNDARY":{"worlds":16,"terminal":0,
                    "abstain_clamp":16},
        "hidden_lethal_east":{"worlds":8,"terminal":4},
        "hidden_danger_here":{"worlds":8,"injury":8},
        "hidden_forced_action_failure":{"worlds":8,"numeric_mismatch":8},
    }
    for cohort,claims in expected.items():
        for metric,value in claims.items():
            if by_cohort[cohort][metric]!=value:
                raise ValueError(
                    f"prespecified {cohort} {metric} count differs: "+
                    f"{by_cohort[cohort][metric]} != {value}"
                )
    if (totals["verified_pairs"]!=104 or
        totals["numerical_forecasts"]!=88 or
        totals["abstentions"]!=16):
        raise ValueError("prospectively sealed pair/status totals differ")
    if (type(summary) is not dict or
        summary.get("schema")!="a230zs-durable-preaction-heldout-v1" or
        summary.get("original_code_head")!=RUN_HEAD or
        summary.get("ZS_preregistered_before_code_sha")!=ZS_PREREG or
        summary.get("durable_model_sha256")!=PRETRAIN_HASH or
        summary.get("durable_model_file_sha256")!=freeze_file_sha or
        summary.get("ledger_raw_file_sha256")!=
            ORIGINAL_DIGESTS["a230zs-preaction-forecast-chain.jsonl"] or
        summary.get("heldout_source_data_sha256")!=evidence_sha(heldout) or
        summary.get("heldout_numeric_scores_sha256")!=evidence_sha(scores) or
        summary.get("chain_head_sha256")!=head or
        summary.get("actual_total_independent_new_physical_worlds")!=120 or
        summary.get("new_heldout_physical_worlds")!=104 or
        summary.get("actual_physical_actions")!=120 or
        summary.get("preaction_fsync_receipts")!=104 or
        summary.get("postaction_fsync_receipts")!=104 or
        summary.get("valid_durable_events")!=208 or
        summary.get("numerical_forecast_receipts")!=88 or
        summary.get("clamp_abstention_receipts")!=16 or
        summary.get("fatal_outcome_receipts_external")!=4 or
        summary.get("nominal_six_component_physically_exact")!=64 or
        summary.get("hazard_hidden_motor_deaths")!=4 or
        summary.get("hazard_hidden_integrity_injuries")!=8 or
        summary.get("hazard_forced_primitive_failures")!=8 or
        summary.get("boundary_abstentions")!=16 or
        summary.get("nominal_hidden_berry_twins_with_identical_observations")!=32 or
        summary.get("exact_fullstate_heldout_keys_known")!=0 or
        summary.get("safety_certificates_emitted")!=0 or
        summary.get("terminality_predictions_emitted")!=0 or
        summary.get("integrity_predictions_emitted")!=0 or
        summary.get("next_full_adjacent_state_predictions_emitted")!=0 or
        summary.get("all_predictions_are_lab_empirical_not_safe") is not True or
        summary.get("I0_external_memory_transferred") is not False or
        summary.get("by_cohort")!={k:dict(v) for k,v in sorted(by_cohort.items())} or
        summary.get("I0_UC_measured") is not False or
        summary.get("new_I0_births")!=0 or
        summary.get("new_I0_autonomous_steps")!=0 or
        summary.get("full_independent_external_timing_attestation") is not False or
        summary.get("ledger_durable_flush_fsync_called_before_each_physical_apply") is not True or
        summary.get("operator_deployment")!="NO-GO" or
        summary.get("Stage12")!="PARTIAL" or
        summary.get("a230")!="PARTIELLE"):
        raise ValueError("sealed ZS summary overclaims facts not in source receipts")
    if "A230ZS_SUMMARY " not in log:
        raise ValueError("original runner log has no intact outcome banner")
    return {
        "schema":"a230zt-independent-sealed-preaction-archive-v1",
        "source_ZS_run":RUN_ID,
        "source_ZS_head":RUN_HEAD,
        "original_source_files_verified":len(ORIGINAL_DIGESTS),
        "two_python_source_byte_parity":True,
        "original_independent_physical_worlds":120,
        "training_worlds_verified":len(training),
        "heldout_worlds_verified":len(heldout),
        "original_physical_examples_hashed":len(training)+len(heldout),
        "durable_ledger_events_independently_rehashed":len(events),
        "preaction_outcome_pairs_independently_joined":totals["verified_pairs"],
        "preaction_forecasts_independently_recomputed":len(heldout),
        "numeric_forecasts":totals["numerical_forecasts"],
        "visible_bound_abstentions":totals["abstentions"],
        "nominal_six_feature_exact_count":by_cohort["NOMINAL"]["all_numeric_exact"],
        "hidden_motor_deaths_external_only":by_cohort["HIDDEN"]["terminal"],
        "hidden_injuries_external_only":by_cohort["HIDDEN"]["injury"],
        "hidden_forced_failures_external_only":
            by_cohort["hidden_forced_action_failure"]["numeric_mismatch"],
        "hidden_B_nominal_paired_equalities":len(nominal_pairs),
        "physical_simulator_reexecuted":False,
        "stage6_planner_reexecuted":False,
        "wall_clock_order_thirdparty_attested":False,
        "original_inprocess_preaction_order_supported_by_runner_and_CI":True,
        "no_new_physics":True,"new_i0_births":0,
        "new_i0_autonomous_steps":0,"real_i0_uc_measured":False,
        "any_safety_or_terminal_certification":False,
        "scientific_stage12":"PARTIAL","a230":"PARTIELLE",
        "issue110":"ADMINISTRATIVELY_CLOSED",
        "cognitive_deployment":"NO-GO",
    }


def execute(original311,original312,out):
    data=load_two_original_artifacts(original311,original312)
    result=verify_dataset(**data)
    result.update({
        "source_SHA256_by_file":ORIGINAL_DIGESTS,
        "independent_review_commit":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True,
        ).strip(),
    })
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zt-independent-audit.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",
    )
    print("A230ZT_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k!="source_SHA256_by_file"
    },sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-311",type=Path,required=True)
    ap.add_argument("--original-312",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    execute(args.original_311,args.original_312,args.output_dir)
