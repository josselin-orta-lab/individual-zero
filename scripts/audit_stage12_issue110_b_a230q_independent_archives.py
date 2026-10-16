"""A2.30-Q: standalone reconstruction of the original P frozen archives.

Reads JSON only. No import of the joint prototype, runner, WorldBody,
Simulator, Oracle, Bench or any I0 life. This cross-checks integrity of
written causal examples and independent recomputation of every forecast.
It CANNOT independently prove WorldBody.apply happened from JSON alone.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

P_RUN = 38730415503
P_SHA = "3ab03a90b38d6c968cddcd9ed699c3f089d0544c"
EXPECTED_SHA = {
    "a230p-training-manifest.json":
        "f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e",
    "a230p-heldout-physical-results.json":
        "570713d9a44c55a13482dba3d5e9b2f8095df8ba8f487f22d5aa917db8bc3514",
    "a230p-summary.json":
        "45167e3bd7be3827f2839208aa8bfe2e316e6b4f110106b94d68bf32a3fea0e0",
}
DIMS=("dx","dy",*(f"body.{p}" for p in ("energy","food","water","integrity")),
      *(f"inventory.{p}" for p in ("berry_a","berry_b","wood","stone","tool")))
GROUPS=("MOV","EAT","WAIT")
STRATA = {
    "train":(48,132),
    "heldout_ID":(48,132),
    "heldout_hidden_OOD":(24,64),
    "heldout_unknown_context":(8,24),
}


def digest(x):
    return sha256_hex(canonical_causal_bytes(x))


def context(initial,commands):
    """Alternative observer-feature projection, authored without importing P."""
    if len(commands)!=3:
        raise ValueError("expected three preregistered prefix commands")
    first=commands[0]
    primitive=first["primitive"]
    parameters=first["parameters"]
    visible={"primitive":primitive, "parameters":parameters,
             "is_night":bool(initial["is_night"])}
    if primitive=="se_deplacer":
        by_direction={n["direction"]:n for n in initial["adjacent"]}
        n=by_direction.get(parameters.get("direction"))
        visible["visible_neighbor"]=(
            {"present":False} if n is None else
            {"present":True,"passable":bool(n["passable"]),
             "creature":bool(n["creature"])}
        )
    elif primitive=="collecter":
        visible["resource_visible_here"]=(
            parameters.get("target") in initial["current_resources"]
        )
        visible["tool_present"]=initial["inventory"].get("tool",0)>0
    elif primitive=="manger":
        visible["held_food_available"]=(
            initial["inventory"].get(parameters.get("target"),0)>0
        )
    elif primitive=="boire":
        visible["water_source_here"]=initial["current_water_source"]
    elif primitive in ("attendre","dormir"):
        visible["known_shelter_here"]=initial["known_shelter_here"]
    else:
        visible["unsupported_feature_policy"]=True
    return digest({"initial_observable_context":visible,
                   "exact_committed_prefix":commands})


def independently_cumulative(a,b):
    out={"dx":float(b["x"]-a["x"]),"dy":float(b["y"]-a["y"])}
    for variable in ("energy","food","water","integrity"):
        out["body."+variable]=float(b["body"][variable]-a["body"][variable])
    for variable in ("berry_a","berry_b","wood","stone","tool"):
        out["inventory."+variable]=float(
            b["inventory"].get(variable,0)-a["inventory"].get(variable,0)
        )
    return out


def signature(steps):
    # Exact preregistered 1e-8 tolerance for floating representation only.
    return digest([{
        "terminal":step["terminal"],
        "cumulative_delta":{
            k:round(float(step["cumulative_delta"][k]),8) for k in DIMS
        },
    } for step in steps])


def _recompute_one(witness, physical, expected_stage):
    """Independent physical ARCHIVE CONSISTENCY, not an oracle of nature."""
    name=witness["world_id"]
    if (not name.startswith("a230p:"+expected_stage+":")
        or physical["world_id"]!=name or physical["stage"]!=expected_stage
        or physical["family"] not in GROUPS
        or physical["initial_food"] not in (
            (30.0,40.0) if expected_stage=="train" else (35.0,45.0)
        )
        or tuple(physical["initial_position"]) not in (
            ((2,2),(4,4)) if expected_stage=="train" else ((5,5),(7,7))
        )
    ):
        raise ValueError("invalid/contaminated cohort identity or stratum")
    if (physical["terminal_step"]!=witness["first_terminal_step"]
        or physical["applied_steps"]!=len(witness["steps"])
        or not physical["physical_applications_evidenced_by_runner"]
        or physical["oracle_feedback_to_i0"] is not False):
        raise ValueError("mismatched original physical-world receipt")
    if (not isinstance(physical["physical_config_sha256"],str)
        or len(physical["physical_config_sha256"])!=64
        or len(physical["physical_layout_sha256"])!=64):
        raise ValueError("missing original physical physics/layout provenance")
    examples=physical["observed_physical_examples"]
    if len(examples)!=len(witness["steps"]):
        raise ValueError("different world-step counts")
    if len(witness["commands"])!=3:
        raise ValueError("prefix secretly shortened")
    if not(1<=len(examples)<=3):
        raise ValueError("wrong physical trajectory length")
    previous=None
    actual_deltas=[]
    terminal=[]
    before0=witness["initial"]
    for i,(row,recorded_step) in enumerate(zip(examples,witness["steps"]),start=1):
        e=row["physical_example"]
        if (row["t_monde"]!=i
            or digest(e)!=row["physical_example_sha256"]
            or e["command"]!=witness["commands"][i-1]
            or e["family"]!="physical_a230p_"+physical["family"]):
            raise ValueError("physical example tampered (step/command/hash)")
        if e["state"]!=(before0 if i==1 else previous):
            raise ValueError("noncontiguous physical state chain")
        measured=independently_cumulative(before0,e["observed_next_state"])
        if set(recorded_step["cumulative_delta"])!=set(DIMS):
            raise ValueError("missing an observable bodily dimension")
        if any(abs(measured[k]-recorded_step["cumulative_delta"][k])>1e-8
               for k in DIMS):
            raise ValueError("recorded cumulative physical delta was altered")
        if recorded_step["terminal"]!=e["terminal"]:
            raise ValueError("physical terminal mismatch at step")
        if e["terminal"] and i!=len(examples):
            raise ValueError("physical transition executed after death")
        terminal.append(bool(e["terminal"]))
        previous=e["observed_next_state"]
        actual_deltas.append(measured)
    first_terminal=(len(terminal) if terminal[-1] else None)
    if (
        sum(terminal)>1
        or (first_terminal is None and len(examples)!=3)
        or first_terminal!=witness["first_terminal_step"]
    ):
        raise ValueError("false or truncated physical mortality")
    actually_harmful=first_terminal is not None or any(
        s["body.integrity"] < -1e-8 for s in actual_deltas
    )
    if actually_harmful!=witness["had_observed_harm"]:
        raise ValueError("false harm/witness status")
    key=context(before0,witness["commands"])
    if key!=witness["group_key"]:
        raise ValueError("hidden physical intervention leaked into context")
    return {
        "world_id":name,
        "stage":expected_stage,
        "family":physical["family"],
        "hidden_variant":physical["hidden_variant_for_lab_only"],
        "initial":before0,
        "commands":witness["commands"],
        "group_key":key,
        "steps":witness["steps"],
        "step_count":len(examples),
        "fingerprint":signature(witness["steps"]),
        "first_terminal_step":first_terminal,
        "harm":actually_harmful,
    }


def _training_catalogue(witnesses):
    groups=defaultdict(list)
    for item in witnesses:
        groups[item["group_key"]].append(item)
    catalog={}
    for key,rows in groups.items():
        fingerprint=defaultdict(list)
        for row in rows:
            fingerprint[row["fingerprint"]].append(row)
        branches={}
        for k,items in fingerprint.items():
            first=items[0]
            branches[k]={
                "fingerprint":k,
                "first_terminal_step":first["first_terminal_step"],
                "physical_training_worlds":len(items),
                "observed_steps":[{
                    "terminal":step["terminal"],
                    "cumulative_delta":{
                        d:round(step["cumulative_delta"][d],8) for d in DIMS
                    },
                } for step in first["steps"]],
            }
        terminal_times=sorted({
            x["first_terminal_step"] for x in rows
            if x["first_terminal_step"] is not None
        })
        label=("observed_terminal_possible" if terminal_times
               else "observed_harm_possible" if any(
                   x["harm"] for x in rows
               ) else "unknown_hidden_risk")
        catalog[key]={
            "branches":branches,
            "terminal_steps":terminal_times,
            "risk_label":label,
            "physical_training_worlds":len(rows),
            "first_step_terminal":any(
                row["first_terminal_step"]==1 for row in rows
            ),
        }
    return catalog


def _compare_forecast(measurement, observed, catalogue):
    out=measurement["model"]
    result=measurement["result"]
    if (out["context_key"]!=observed["group_key"]
        or out["certifies_safe"] is not False
        or out["unseen_hidden_hazard_not_excluded"] is not True
        or measurement["physical_steps"]!=observed["step_count"]
        or measurement["no_i0_command_was_executed"] is not True
        or measurement["family"]!=observed["family"]
        or measurement["stage"]!=observed["stage"]
        or measurement["hidden_variant_for_lab_only"]!=observed["hidden_variant"]):
        raise ValueError("forecast declared fake certainty or changed source")
    trained=catalogue.get(observed["group_key"])
    if trained is None:
        if out!={
            "status":"abstain_unknown_context",
            "context_key":observed["group_key"],
            "risk_label":"unavailable",
            "supported_physical_worlds":0,
            "empirical_branches":[],
            "observed_terminal_steps":[],
            "single_step_baseline_witnessed_terminal":False,
            "certifies_safe":False,
            "unseen_hidden_hazard_not_excluded":True,
        }:
            raise ValueError("unseen context fabricated a known branch")
        expected_result={
            "covered":False, "joint_branch_witnessed":None,
            "first_terminal_step":observed["first_terminal_step"],
            "terminal_step_in_empirical_set":None,
            "novel_joint_branch":None,
            "observed_possible_late_terminal":False,
        }
    else:
        if (
            out["status"]!="observed_joint_branches"
            or out["supported_physical_worlds"]!=trained["physical_training_worlds"]
            or out["risk_label"]!=trained["risk_label"]
            or out["observed_terminal_steps"]!=trained["terminal_steps"]
            or out["single_step_baseline_witnessed_terminal"]!=
                trained["first_step_terminal"]
            or len(out["empirical_branches"])!=len(trained["branches"])
        ):
            raise ValueError("frozen predictor coverage/risk/branch count falsified")
        published={row["fingerprint"]:row for row in out["empirical_branches"]}
        if published!=trained["branches"]:
            raise ValueError("published branches do not match frozen physical train")
        matched=observed["fingerprint"] in trained["branches"]
        terminal_step=observed["first_terminal_step"]
        valid_terminal=(
            terminal_step in trained["terminal_steps"]
            if terminal_step is not None else
            any(x["first_terminal_step"] is None
                for x in trained["branches"].values())
        )
        expected_result={
            "covered":True,
            "joint_branch_witnessed":matched,
            "first_terminal_step":terminal_step,
            "terminal_step_in_empirical_set":valid_terminal,
            "novel_joint_branch":not matched,
            "observed_possible_late_terminal":any(
                step>1 for step in trained["terminal_steps"]
            ),
        }
    if result!=expected_result:
        raise ValueError("test truth manipulated joint-branch results")
    return {
        "stage":observed["stage"],
        "world_id":observed["world_id"],
        "step_count":observed["step_count"],
        "covered":expected_result["covered"],
        "joint_matched":expected_result["joint_branch_witnessed"] is True,
        "novel_branch":expected_result["novel_joint_branch"] is True,
        "abstained":not expected_result["covered"],
        "terminal":observed["first_terminal_step"] is not None,
        "late_terminal":(
            observed["first_terminal_step"] is not None
            and observed["first_terminal_step"]>1
        ),
        "unwitnessed_late_terminal_first_step":(
            observed["first_terminal_step"] is not None
            and observed["first_terminal_step"]>1
            and (not out["single_step_baseline_witnessed_terminal"])
            and expected_result["covered"]
        ),
        "terminal_step_outside_empirical_set":(
            expected_result["covered"]
            and expected_result["terminal_step_in_empirical_set"] is False
            and observed["first_terminal_step"] is not None
        ),
    }


def independently_audit(training,tests,summary):
    if (
        summary.get("schema")!="a230p-physical-joint-trajectories-v1"
        or summary.get("code_sha")!=P_SHA
        or summary.get("new_i0_births")!=0
        or summary.get("new_autonomous_i0_steps")!=0
        or summary.get("deployable_to_i0") is not False
        or summary.get("certifies_any_action_safe") is not False
    ):
        raise ValueError("wrong historical research version/source")
    if (
        training.get("schema")!="a230p-detached-physical-training-v1"
        or training.get("training_witness_corpus_sha256")!=digest(
            training["training_witnesses"]
        )
        or summary["training_witness_corpus_sha256"]!=training[
            "training_witness_corpus_sha256"
        ]
    ):
        raise ValueError("original training witness corpus SHA invalid")
    witnesses=training["training_witnesses"]
    sources=training["source_lab_physics"]
    if len(witnesses)!=48 or len(sources)!=48 or len(tests)!=80:
        raise ValueError("expected exact physical train/test world counts")
    receipts=[]
    IDs=set()
    steps_train=0
    for w,p in zip(witnesses,sources):
        verified=_recompute_one(w,p,"train")
        if verified["world_id"] in IDs:
            raise ValueError("same physical training world recorded twice")
        IDs.add(verified["world_id"])
        steps_train+=verified["step_count"]
        receipts.append(verified)
    if steps_train!=132 or len({
        receipt["group_key"] for receipt in receipts
    })!=3:
        raise ValueError("training physical corpus has wrong steps/context")
    # An unseen hidden intervention must not create a distinct *input* key.
    aliased=defaultdict(list)
    for row in receipts:
        aliased[(row["family"],row["initial"]["body"]["food"],
                 row["initial"]["x"],row["initial"]["y"])].append(row["initial"])
    if any(len(group)!=4 or any(x!=group[0] for x in group[1:])
           for group in aliased.values()):
        raise ValueError("hidden physics was perceptible in training inputs")
    model=_training_catalogue(receipts)
    if any(
        len(group["branches"])!=4 or
        group["physical_training_worlds"]!=16 or
        group["risk_label"]!="observed_terminal_possible"
        for group in model.values()
    ):
        raise ValueError("not three four-branch independent physical contexts")
    expected_training_counts={
        "MOV":40, "EAT":44, "WAIT":48,
    }
    for family,count in expected_training_counts.items():
        if sum(x["step_count"] for x in receipts if x["family"]==family)!=count:
            raise ValueError("training physical terminal chronology disagrees")
    audit_rows=[]
    for row in tests:
        observed=_recompute_one(
            row["witness"],row["source_lab_physics"],row["stage"]
        )
        if (observed["world_id"] in IDs or
            row["world_id"]!=observed["world_id"]):
            raise ValueError("reused or mismatched training/test world")
        IDs.add(observed["world_id"])
        audit_rows.append(_compare_forecast(row,observed,model))
    if len(IDs)!=128:
        raise ValueError("expected 128 disjoint laboratory worlds")
    computed={}
    for stage in STRATA:
        subset=[x for x in audit_rows if x["stage"]==stage]
        if stage=="train":
            continue
        item={
            "worlds":len(subset),
            "physical_steps":sum(x["step_count"] for x in subset),
            "available":sum(x["covered"] for x in subset),
            "abstained":sum(x["abstained"] for x in subset),
            "joint_matches":sum(x["joint_matched"] for x in subset),
            "novel_branches":sum(x["novel_branch"] for x in subset),
            "terminal_worlds":sum(x["terminal"] for x in subset),
            "late_terminal_worlds":sum(x["late_terminal"] for x in subset),
            "late_terminal_absent_from_first_step_witness":sum(
                x["unwitnessed_late_terminal_first_step"] for x in subset
            ),
            "terminal_step_outside_empirical_set":sum(
                x["terminal_step_outside_empirical_set"] for x in subset
            ),
        }
        if (item["worlds"],item["physical_steps"])!=STRATA[stage]:
            raise ValueError("test stage independent world/step count mismatch")
        if item!=summary["strata"][stage]:
            raise ValueError("independent strata metrics mismatch: "+stage)
        computed[stage]=item
    if (summary["training_physical_worlds"],
        summary["training_physical_steps"],
        summary["heldout_physical_worlds"],
        summary["heldout_physical_steps"],
        summary["physical_worlds_total"],
        summary["physical_steps_total"])!=(48,132,80,220,128,352):
        raise ValueError("all physical world counts were misreported")
    return {
        "schema":"stage12-a230q-independent-offline-witness-v1",
        "source_original_run":P_RUN,
        "source_original_sha":P_SHA,
        "new_i0_lives":0,
        "new_physical_worlds":0,
        "new_physical_steps":0,
        "original_worlds_checked":128,
        "original_steps_checked":352,
        "independently_scored_holdout_worlds":80,
        "model_groups_rebuilt_from_train":len(model),
        "id_joint_matches":computed["heldout_ID"]["joint_matches"],
        "ood_novel_joint_branches":computed[
            "heldout_hidden_OOD"]["novel_branches"],
        "unknown_context_abstentions":computed[
            "heldout_unknown_context"]["abstained"],
        "late_deaths_without_first_step_terminal_example":computed[
            "heldout_ID"]["late_terminal_absent_from_first_step_witness"],
        "ood_terminal_step_misses":computed[
            "heldout_hidden_OOD"]["terminal_step_outside_empirical_set"],
        "prototype_imported":False,
        "physical_worldbody_apply_independently_proven_from_json":False,
        "safe_model_deployment_proven":False,
        "stage12":"PARTIAL",
        "strata":computed,
    }


def sealed_source(folder:Path)->dict[str,bytes]:
    out={}
    for name,expected in EXPECTED_SHA.items():
        files=list(folder.rglob(name))
        if len(files)!=1:
            raise ValueError("missing or ambiguous sealed source: "+name)
        data=files[0].read_bytes()
        if sha256(data).hexdigest()!=expected:
            raise ValueError("source artifact original bytes changed: "+name)
        out[name]=data
    return out


def execute(a:Path,b:Path,output:Path):
    sourceA=sealed_source(a)
    sourceB=sealed_source(b)
    if sourceA!=sourceB:
        raise ValueError("original Python 3.11 and 3.12 archives differ")
    computed=independently_audit(
        json.loads(sourceA["a230p-training-manifest.json"]),
        json.loads(sourceA["a230p-heldout-physical-results.json"]),
        json.loads(sourceA["a230p-summary.json"]),
    )
    computed.update({
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "source_artifact_sha256":EXPECTED_SHA,
        "python_artifacts_identical_bytes":True,
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230q-summary.json").write_text(
        json.dumps(computed,sort_keys=True,indent=2)+"\n"
    )
    print("A230Q_SUMMARY "+json.dumps({
        k:v for k,v in computed.items() if k!="strata"
    },sort_keys=True),flush=True)
    return computed


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-311",type=Path,required=True)
    ap.add_argument("--source-312",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    execute(args.source_311,args.source_312,args.output_dir)


if __name__=="__main__":
    main()
