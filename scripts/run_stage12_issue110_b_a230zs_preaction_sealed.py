"""A2.30-ZS: actually prospective pre-action durable forecast receipts, 120 worlds.

PREREGISTERED BEFORE CODE/PHYSICS at e642e7f240909c906cc2bb9d045623f4c4afbf35.
Unlike retrospective ZO scoring, every heldout partial forecast is:
  (a) computed from the current accessible capture + frozen TRAIN-only model,
  (b) appended to the SHA-linked ledger, flushed and os.fsync-ed,
  (c) ONLY THEN followed by WorldBody.apply via physical corpus recorder,
  (d) joined to a subsequent external physical outcome receipt and fsynced.
No Stage12 I0 birth, subject, Oracle, UC, postdeath subjectivity or food eating.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

from i0.equipment import EquipmentCorpus, train_exact_transition_table
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import WorldBody

from run_stage12_issue110_b_a230zo_factorized_heldout import (
    COMMAND, TRAIN_N, NOMINAL_N, HIDDEN_N, BOUNDARY_N, DELTA_KEYS,
    registered_recipes, physical_fixture, first_person, check_action_eligible,
    apply_one, fit_partial_empirical, partial_forecast, compare_forecast,
    review_results, digest, visible_only,
)

PRE_REGISTERED_SHA="e642e7f240909c906cc2bb9d045623f4c4afbf35"
ZO_MODEL_FINGERPRINT="d837d17d285c20ac53a55f3f78818d4f2abfa7cd387b6232e3c105bd9ac25171"
MODEL_FREEZE_FILE="a230zs-frozen-training-model.json"
LEDGER_FILE="a230zs-preaction-forecast-chain.jsonl"
STUDY_SCHEMA="a230zs-durable-preaction-heldout-v1"
GENESIS="0"*64
PREDICT="prediction_committed"
OUTCOME="outcome_sealed"
LEDGER_RECORDS=208
HELDOUT_COUNT=104
TRAIN_COUNT=16
ALL_WORLDS=120


def zs_recipe(recipe):
    """New independent physical world identities, never the historical ZO worlds."""
    if not recipe["world_id"].startswith("a230zo:"):
        raise ValueError("not an independently renamed preregistered recipe")
    return {**recipe,"world_id":"a230zs:"+recipe["world_id"][len("a230zo:"):]}


def write_fsync(path, data):
    """Create a sealed UTF-8 file and fsync its contents and directory metadata."""
    path=Path(path)
    if path.exists():
        raise ValueError("will not rewrite already-frozen source evidence")
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    # fsync directory so the file's name is also durably published.
    dirfd=os.open(str(path.parent),os.O_RDONLY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)
    return sha256(data).hexdigest()


def immutable_json_file(path,obj):
    return write_fsync(
        path,(json.dumps(obj,sort_keys=True,indent=2)+"\n").encode("utf-8")
    )


class DurableForecastLedger:
    """Append-only SHA-chain with one real fsync per event. No overwrites."""
    def __init__(self,path):
        self.path=Path(path)
        self.head=GENESIS
        self.count=0
        with self.path.open("xb") as f:
            f.flush()
            os.fsync(f.fileno())
        dirfd=os.open(str(self.path.parent),os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)

    def append(self,kind,payload):
        if kind not in (PREDICT,OUTCOME):
            raise ValueError("illegal durable temporal event")
        if (self.count%2==0)!=(kind==PREDICT):
            raise ValueError("prediction/outcome must strictly alternate")
        envelope={
            "seq":self.count+1,
            "prev_sha256":self.head,
            "kind":kind,
            "payload":payload,
        }
        checksum=digest(envelope)
        event={**envelope,"event_sha256":checksum}
        encoded=(json.dumps(
            event,sort_keys=True,separators=(",",":"),allow_nan=False
        )+"\n").encode("utf-8")
        # append bytes AND fsync before control can continue to WorldBody.apply
        with self.path.open("ab") as f:
            f.write(encoded)
            f.flush()
            os.fsync(f.fileno())
        self.head=checksum
        self.count+=1
        return checksum


def prepare_training(folder,registered):
    """16 real physics actions; froze immutable model BEFORE any heldout WorldBody."""
    training_pairs=[apply_one(zs_recipe(row)) for row in registered]
    source=[row for row,_ in training_pairs]
    if len(source)!=TRAIN_COUNT or len({r["world_id"] for r in source})!=TRAIN_COUNT:
        raise AssertionError("not 16 independent ZS physical training worlds")
    physical=tuple(ex for _,ex in training_pairs)
    corpus=EquipmentCorpus(
        version="a230zs-training-external-worlds-v1",
        examples=physical,
    )
    exact=train_exact_transition_table(
        corpus=corpus,equipment_version="E-a230zs-exact-control-v1",
    )
    partial=fit_partial_empirical(source)
    model_sha=digest(partial)
    # The original ZO model is derived only from accessible physics; the
    # strictly prospective replication must preserve its empirical deltas.
    if model_sha!=ZO_MODEL_FINGERPRINT:
        raise AssertionError("physical training model diverged from preregistered ZO")
    training_sha=immutable_json_file(
        folder/"a230zs-physical-training.json",source
    )
    freeze={
        "schema":"a230zs-locked-before-heldout-v1",
        "preregistered_protocol_sha":PRE_REGISTERED_SHA,
        "model":partial,
        "model_sha256":model_sha,
        "exact_equipment_source_sha256":exact.artifact_digest,
        "training_physical_source_sha256":digest(source),
        "training_file_sha256":training_sha,
        "training_worlds":TRAIN_COUNT,
        "training_examples_per_command":{"MOVE_E":8,"COLLECT_B":8},
        "unknown_dimensions":[
            "integrity","terminal","next_adjacency","safe"
        ],
        "contains_no_heldout_worlds":True,
        "no_production_i0_model_contract":True,
    }
    freeze_bytes_sha=immutable_json_file(folder/MODEL_FREEZE_FILE,freeze)
    # A fresh read of the synced file disallows in-process unstaged data.
    if sha256((folder/MODEL_FREEZE_FILE).read_bytes()).hexdigest()!=freeze_bytes_sha:
        raise AssertionError("model was not durably frozen")
    return source,partial,exact,freeze,freeze_bytes_sha


def prospective_one(recipe,index,model,exact,freeze,freeze_file_sha,ledger):
    """Commit the first-person forecast BEFORE applying one external action."""
    if not 1<=index<=HELDOUT_COUNT or ledger.count!=(index-1)*2:
        raise AssertionError("unregistered prediction-vs-physics order")
    config,layout=physical_fixture(recipe)
    world=WorldBody(config=config,layout=layout)
    command=COMMAND[recipe["action"]]
    t=recipe["t_monde"]
    if recipe["intervention"]=="hidden_forced_action_failure":
        # External contingent failure exists at birth, not in visible state.
        world.apply_scenario_event(
            "set_action_failure_schedule",
            {"primitive":command.primitive,"schedule":[True]},
        )
    before=first_person(world,t)
    firstperson=visible_only(before.as_dict())
    actual_command=check_action_eligible(firstperson,recipe["action"])
    if actual_command!=command or actual_command.primitive=="manger":
        raise AssertionError("no legitimate visible noningestive primitive")

    # All cognitive-like model inputs are in these two arguments, plus a
    # training-only immutable model. No hidden_B, intervention or outcome.
    model_sha=digest(model)
    if model_sha!=freeze["model_sha256"] or model_sha!=ZO_MODEL_FINGERPRINT:
        raise AssertionError("trained source model changed after freeze")
    prediction=partial_forecast(model,firstperson,recipe["action"])
    if set(prediction)!={"status","estimated","integrity",
                        "terminal","next_adjacency","safe"} or any(
        prediction[key] is not None for key in (
            "integrity","terminal","next_adjacency","safe"
        )
    ):
        raise AssertionError("unknown hazard was falsely certified")
    opaque=f"a230zs-heldout-{index:03d}"
    first={
        "world_token":opaque,
        "t_monde":t,
        "source_training_model_sha256":model_sha,
        "source_training_file_sha256":freeze_file_sha,
        "preaction_accessible_state":firstperson,
        "preaction_accessible_sha256":digest(firstperson),
        "firstperson_eligible_command":command.as_dict(),
        "command_label":recipe["action"],
        "frozen_partial_forecast":prediction,
        "no_hidden_world_parameters_in_forecast":True,
        "no_oracle_or_i0_uc_receipt":True,
        "no_action_yet_executed_for_this_world":True,
    }
    if any(x in json.dumps(first) for x in (
        "hidden_lethal","hidden_danger","forced_action_failure",
        "toxic_lethal","latent_berry","integrity_delta_external"
    )):
        raise AssertionError("hidden external treatment leaked into prediction")
    prediction_sha=ledger.append(PREDICT,first)
    if (ledger.count!=2*index-1 or ledger.head!=prediction_sha
        or not ledger.path.is_file()):
        raise AssertionError("preaction prediction was not durably committed")
    # The filesystem receipt was flushed and os.fsync-ed by Ledger.append.
    # Crucial causal-order guarantee: ONLY NOW do we invoke physical apply.
    recorder=EquipmentCorpusRecorder(
        corpus_version="a230zs-"+opaque,
    )
    example=recorder.record_transition(
        world=world,t_monde=t,
        family="a230zs-independent-noningestive-"+recipe["action"],
        command=command,
    )
    if example.state!=before:
        raise AssertionError("physics used a different preaction visible state")
    if example.terminal:
        world.freeze_terminal_state()
    after=example.observed_next_state.as_dict()
    example_dict=example.as_dict()
    second={
        "world_token":opaque,
        "world_id_external_only":recipe["world_id"],
        "cohort_external_only":recipe["cohort"],
        "latent_B_external_only":recipe["hidden_B"],
        "intervention_external_only":recipe["intervention"],
        "linked_preaction_event_sha256":prediction_sha,
        "linked_preaction_accessible_sha256":digest(firstperson),
        "source_training_model_sha256":model_sha,
        "action_physically_applied":command.as_dict(),
        "physical_example":example_dict,
        "physical_example_sha256":digest(example_dict),
        "physical_terminal_external_only":example.terminal,
        "postaction_external_only":after,
        "world_terminal_frozen":bool(example.terminal),
        "postterminal_lived_capture":None,
        "no_i0_birth_or_autonomous_step":True,
    }
    outcome_sha=ledger.append(OUTCOME,second)
    if ledger.count!=2*index:
        raise AssertionError("failed to seal physical outcome after first-person forecast")
    row={
        "world_id":recipe["world_id"],
        "preregistered_cohort":recipe["cohort"],
        "source_or_heldout":"previously_unseen_heldout",
        "position_factor_external":list(recipe["position"]),
        "body_factor_external":list(recipe["body"]),
        "phase_factor_external":t,
        "command_label":recipe["action"],
        "latent_berry_effect_external_only":recipe["hidden_B"],
        "hidden_intervention_external_only":recipe["intervention"],
        "physical_config_sha256_external_only":config.digest(),
        "physical_layout_sha256_external_only":digest(layout.as_dict()),
        "preaction_first_person":firstperson,
        "preaction_sha256":digest(firstperson),
        "action_physically_applied":command.as_dict(),
        "physical_example":example_dict,
        "physical_example_sha256":digest(example_dict),
        "postaction_external_only":after,
        "physically_terminal_external_only":example.terminal,
        "postdeath_lived_capture":None,
        "world_sealed_on_terminal":bool(example.terminal),
        "no_i0_birth_or_autonomous_step":True,
        "no_berry_ingestion":True,
        "actual_i0_uc_measured":None,
        "no_oracle_or_hidden_input_to_prediction":True,
        "safety_certificate":None,
        "forecast_preaction_event_sha256":prediction_sha,
        "outcome_external_event_sha256":outcome_sha,
    }
    return row,first,second


def parse_chain(raw):
    """Parse AND strictly verify cryptographic temporal sequence and schemas."""
    lines=raw.splitlines()
    if len(lines)!=LEDGER_RECORDS:
        raise ValueError("preaction/outcome durable chain missing or duplicated event")
    entries=[]
    previous=GENESIS
    for index,line in enumerate(lines):
        if not line or b"\x00" in line:
            raise ValueError("truncated or malformed durable event")
        try:
            row=json.loads(line)
        except (ValueError,UnicodeDecodeError) as err:
            raise ValueError("invalid JSON forecast/outcome receipt") from err
        if type(row) is not dict or set(row)!={
            "seq","prev_sha256","kind","payload","event_sha256"
        }:
            raise ValueError("invalid receipt envelope schema")
        if (row["seq"]!=index+1 or row["prev_sha256"]!=previous
            or row["kind"]!=(PREDICT if index%2==0 else OUTCOME)):
            raise ValueError("forecast was not durably committed before action")
        checksum=digest({k:row[k] for k in (
            "seq","prev_sha256","kind","payload"
        )})
        if row["event_sha256"]!=checksum:
            raise ValueError("broken SHA-256 chain or forged physical receipt")
        entries.append(row)
        previous=checksum
    return entries


def audit_chain(raw,training,freeze,heldout,model_sha,freeze_file_sha):
    """Offline, independently replayable audit; cannot falsify the runner order."""
    entries=parse_chain(raw)
    if (len(heldout)!=HELDOUT_COUNT
        or len(training)!=TRAIN_COUNT
        or freeze["model_sha256"]!=model_sha
        or freeze["model_sha256"]!=digest(freeze["model"])
        or freeze["model"]!=fit_partial_empirical(training)
        or freeze["training_physical_source_sha256"]!=digest(training)
        or freeze["training_worlds"]!=TRAIN_COUNT
        or freeze["training_examples_per_command"]!={
            "MOVE_E":8,"COLLECT_B":8
        }
        or freeze["contains_no_heldout_worlds"] is not True
        or freeze["no_production_i0_model_contract"] is not True
        or freeze["unknown_dimensions"]!=[
            "integrity","terminal","next_adjacency","safe"
        ]):
        raise ValueError("frozen training-only source was replaced")
    nominal_pair={}
    counts=Counter()
    for i,row in enumerate(heldout):
        a=entries[i*2]
        z=entries[i*2+1]
        pre=a["payload"]
        after=z["payload"]
        opaque=f"a230zs-heldout-{i+1:03d}"
        if (type(pre) is not dict or set(pre)!={
            "world_token","t_monde","source_training_model_sha256",
            "source_training_file_sha256","preaction_accessible_state",
            "preaction_accessible_sha256","firstperson_eligible_command",
            "command_label","frozen_partial_forecast",
            "no_hidden_world_parameters_in_forecast",
            "no_oracle_or_i0_uc_receipt",
            "no_action_yet_executed_for_this_world"
        } or type(after) is not dict or set(after)!={
            "world_token","world_id_external_only","cohort_external_only",
            "latent_B_external_only","intervention_external_only",
            "linked_preaction_event_sha256",
            "linked_preaction_accessible_sha256",
            "source_training_model_sha256","action_physically_applied",
            "physical_example","physical_example_sha256",
            "physical_terminal_external_only","postaction_external_only",
            "world_terminal_frozen","postterminal_lived_capture",
            "no_i0_birth_or_autonomous_step"
        }):
            raise ValueError("unexpected fields or hidden truth in preaction model")
        p=pre["frozen_partial_forecast"]
        if (pre["world_token"]!=opaque or after["world_token"]!=opaque
            or pre["t_monde"]!=row["phase_factor_external"]
            or pre["source_training_model_sha256"]!=model_sha
            or pre["source_training_file_sha256"]!=freeze_file_sha
            or pre["preaction_accessible_sha256"]!=digest(pre["preaction_accessible_state"])
            or pre["preaction_accessible_state"]!=row["preaction_first_person"]
            or pre["firstperson_eligible_command"]!=row["action_physically_applied"]
            or pre["command_label"]!=row["command_label"]
            or pre["no_hidden_world_parameters_in_forecast"] is not True
            or pre["no_oracle_or_i0_uc_receipt"] is not True
            or pre["no_action_yet_executed_for_this_world"] is not True
            or type(p) is not dict or set(p)!={
                "status","estimated","integrity","terminal",
                "next_adjacency","safe"
            } or any(p[k] is not None for k in (
                "integrity","terminal","next_adjacency","safe"
            ))):
            raise ValueError("forecast never frozen on the correct accessible input")
        # Independent recalculation is a DETECTOR of a forged preaction
        # event, never a substitute for the already-fsynced original event.
        if p!=partial_forecast(
            freeze["model"],pre["preaction_accessible_state"],
            pre["command_label"],
        ):
            raise ValueError("preaction forecast differs from frozen training model")
        if (
            not row["preaction_sha256"]==digest(row["preaction_first_person"])
            or row["physical_example_sha256"]!=digest(row["physical_example"])
            or row["physical_example"]["state"]!=row["preaction_first_person"]
            or row["physical_example"]["observed_next_state"]!=
                row["postaction_external_only"]
            or row["physical_example"]["terminal"]!=
                row["physically_terminal_external_only"]
            or row["physical_example"]["command"]!=row["action_physically_applied"]
            or row["no_i0_birth_or_autonomous_step"] is not True
            or row["no_berry_ingestion"] is not True
            or row["actual_i0_uc_measured"] is not None
            or row["postdeath_lived_capture"] is not None
            or row["safety_certificate"] is not None
        ):
            raise ValueError("postaction physical example or UC was forged")
        if (after["world_id_external_only"]!=row["world_id"]
            or after["cohort_external_only"]!=row["preregistered_cohort"]
            or after["latent_B_external_only"]!=row["latent_berry_effect_external_only"]
            or after["intervention_external_only"]!=row["hidden_intervention_external_only"]
            or after["linked_preaction_event_sha256"]!=a["event_sha256"]
            or after["linked_preaction_accessible_sha256"]!=
                pre["preaction_accessible_sha256"]
            or after["source_training_model_sha256"]!=model_sha
            or after["action_physically_applied"]!=row["action_physically_applied"]
            or after["physical_example"]!=row["physical_example"]
            or after["physical_example_sha256"]!=digest(row["physical_example"])
            or after["physical_terminal_external_only"]!=row["physically_terminal_external_only"]
            or after["postaction_external_only"]!=row["postaction_external_only"]
            or after["world_terminal_frozen"]!=row["physically_terminal_external_only"]
            or after["postterminal_lived_capture"] is not None
            or after["no_i0_birth_or_autonomous_step"] is not True
            or row["forecast_preaction_event_sha256"]!=a["event_sha256"]
            or row["outcome_external_event_sha256"]!=z["event_sha256"]):
            raise ValueError("external physical receipt cannot be joined after prediction")
        if not row["world_id"].startswith("a230zs:"):
            raise ValueError("retrospective source identity used as new ZS world")
        if p["status"]=="empirical_partial_not_certified":
            counts["estimates"]+=1
        if p["status"]=="abstain_clamp":
            counts["abstentions"]+=1
        if row["physically_terminal_external_only"]:
            counts["terminal_worlds"]+=1
        counts["source_provenance_pairs"]+=1
    if (counts["source_provenance_pairs"]!=104
        or counts["estimates"]!=88
        or counts["abstentions"]!=16
        or counts["terminal_worlds"]!=4):
        raise ValueError("precommitted forecast denominators or mortal outcomes changed")
    return {
        "valid_durable_events":len(entries),
        "preaction_fsync_receipts":len(entries)//2,
        "postaction_fsync_receipts":len(entries)//2,
        "all_model_hashes_same_original_source":True,
        "preaction_vs_outcome_links_valid":True,
        "chain_head_sha256":entries[-1]["event_sha256"],
        "numerical_forecast_receipts":counts["estimates"],
        "clamp_abstention_receipts":counts["abstentions"],
        "fatal_outcome_receipts_external":counts["terminal_worlds"],
        "no_postdeath_subjective_receipts":True,
        "no_hidden_hazard_fields_in_prediction_receipts":True,
    }


def experiment(folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=False)
    src_train,src_nominal,src_hidden,src_boundary=registered_recipes()
    training,model,exact,freeze,freeze_file_sha=prepare_training(
        folder,src_train
    )
    ledger=DurableForecastLedger(folder/LEDGER_FILE)
    heldout=[]
    actual_prediction_receipts=[]
    for idx,original in enumerate(
        src_nominal+src_hidden+src_boundary,1
    ):
        row,pre,after=prospective_one(
            zs_recipe(original),idx,model,exact,freeze,
            freeze_file_sha,ledger,
        )
        heldout.append(row)
        actual_prediction_receipts.append(pre)
    if ledger.count!=LEDGER_RECORDS:
        raise AssertionError("prospective fsync commit pair count mismatch")
    chain_bytes=(folder/LEDGER_FILE).read_bytes()
    chron=audit_chain(
        chain_bytes,training,freeze,heldout,
        digest(model),freeze_file_sha,
    )
    # Compare only AFTER every preaction prediction was already committed.
    scores=[]
    for row,committed in zip(heldout,actual_prediction_receipts):
        shadow_score=compare_forecast(row,model,exact)
        if shadow_score["frozen_empirical_prediction"]!=committed[
            "frozen_partial_forecast"
        ]:
            raise AssertionError("retrospective scoring mutated preaction forecast")
        scores.append(shadow_score)
    base=review_results(training,heldout,model,scores)
    if base["nominal_six_component_physically_exact"]!=64:
        raise AssertionError("prospective nominal heldout numerical predictions failed")
    if digest(model)!=ZO_MODEL_FINGERPRINT:
        raise AssertionError("changed model after heldout physics")
    summary={
        **base,
        **chron,
        "schema":STUDY_SCHEMA,
        "original_ZO_preregistered_matrix_reused_with_new_world_id":True,
        "ZS_preregistered_before_code_sha":PRE_REGISTERED_SHA,
        "actual_total_independent_new_physical_worlds":ALL_WORLDS,
        "train_physical_before_frozen_model":TRAIN_COUNT,
        "new_heldout_physical_worlds":HELDOUT_COUNT,
        "actual_physical_actions":ALL_WORLDS,
        "original_ZO_heldout_forecast_timestamp_gap_resolved_in_ZS":True,
        "per_heldout_prediction_receipt_before_apply_in_runner":True,
        "full_independent_external_timing_attestation":False,
        "ledger_durable_flush_fsync_called_before_each_physical_apply":True,
        "durable_model_sha256":digest(model),
        "durable_model_file_sha256":freeze_file_sha,
        "heldout_source_data_sha256":digest(heldout),
        "heldout_numeric_scores_sha256":digest(scores),
        "ledger_raw_file_sha256":sha256(chain_bytes).hexdigest(),
        "original_code_head":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "I0_external_memory_transferred":False,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "I0_UC_measured":False,
        "no_hidden_B_ingestion_physics":True,
        "unknown_hidden_motor_safety":True,
        "normative_MVP_or_cognition_changed":False,
        "Stage12":"PARTIAL",
        "a230":"PARTIELLE",
        "issue110_administrative_status":"CLOSED",
        "operator_deployment":"NO-GO",
    }
    immutable_json_file(
        folder/"a230zs-heldout-worlds.json",heldout
    )
    immutable_json_file(
        folder/"a230zs-postaction-scoring.json",scores
    )
    immutable_json_file(
        folder/"a230zs-summary.json",summary
    )
    print("A230ZS_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("by_cohort","durable_model_sha256",
                     "ledger_raw_file_sha256","heldout_source_data_sha256",
                     "heldout_numeric_scores_sha256")
    },sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    experiment(args.output_dir)


if __name__=="__main__":
    main()
