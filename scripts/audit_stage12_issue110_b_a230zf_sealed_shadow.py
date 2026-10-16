"""A2.30-ZF: independent archive-only verifier of prospective ZE Stage6 ablation.

No import of ZE runner or its trainer/planner, no WorldBody, no cognition.
Only immutable old GitHub Actions JSON; recomputes all physical-example
digests, exact-key coverage and 24 frozen shadow verdicts. DOES NOT claim
to independently rerun Stage6 or physically reexecute the source worlds.
Preregistered after known ZE results but before this verifier at 154c2301.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

SOURCE_RUN=38773219305
SOURCE_SHA="e56880e50e278f52640d525ff53916b8fb6ce8de"
SHA_BYTES={
    "a230ze-training-manifest.json":
        "abb45515fa96ac56000527925f68fddfc9693d38dabded8c7941181c81fa1054",
    "a230ze-heldout-shadows.json":
        "2fd30ac9326ae36dd0231ac6807f7992ed7f7a9ee28b95af42d46ac9bb369667",
    "a230ze-summary.json":
        "5ff00641e58303ba72b644a7dadfd5470319a6e0d1f8adc041b9e7cf53b65f19",
}
ACCESSIBLE=frozenset({
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
})
KNOWN_LAYOUTS=frozenset({"B_LOCAL","B_EAST"})
NEGATIVE_LAYOUTS=frozenset({"B_NONE","B_EAST_BLOCKED"})
ARM_KEYS=("baseline_A_only","enriched_demonstrated_prefix")
EAT_B={"primitive":"manger","parameters":{"target":"berry_b"}}
COLLECT_B={"primitive":"collecter","parameters":{"target":"berry_b"}}
COLLECT_A={"primitive":"collecter","parameters":{"target":"berry_a"}}
MOVE_E={"primitive":"se_deplacer","parameters":{"direction":"east"}}


def digest(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def exact_key(state,command):
    valid_perception(state)
    if (type(command) is not dict or
        set(command)!={"primitive","parameters"}):
        raise ValueError("noncanonical first-person command")
    return digest({"state":state,"command":command})


def valid_perception(state):
    if type(state) is not dict or set(state)!=ACCESSIBLE:
        raise ValueError("test or training input contains hidden or future field")
    if set(state["body"])!={"energy","food","water","integrity"}:
        raise ValueError("incomplete bodily first-person input")
    if len(state["adjacent"])!=4:
        raise ValueError("missing visible neighbors")
    if type(state["x"]) is not int or type(state["y"]) is not int:
        raise ValueError("position absent from first person")


def independent_physical_training(training):
    experiments=training["demonstrations"]
    if (
        training.get("schema")!="a230ze-actual-physical-training-v1"
        or len(experiments)!=9
        or training.get("training_worlds")!=9
        or training.get("physical_training_steps")!=13
        or training.get("model_examples_physically_observed")!=13
        or training.get("all_training_commands_non_ingestive") is not True
    ):
        raise ValueError("training source no longer preregistered physical cohort")
    by_id={}
    records=[]
    for demo in experiments:
        name=demo["source_world_id"]
        if name in by_id:
            raise ValueError("duplicate physical demonstration world")
        by_id[name]=demo
        root=demo["root_accessible"]
        valid_perception(root)
        samples=demo["observed_physical_examples"]
        hashes=demo["physical_example_sha256"]
        if (demo["physical_steps"]!=len(samples)
            or len(hashes)!=len(samples)
            or not demo["no_ingestion_in_training"]
            or not demo["no_terminal"]
            or len(demo["physics_config_sha256_external_only"])!=64
            or len(demo["layout_sha256_external_only"])!=64):
            raise ValueError("broken original WorldBody physical provenance")
        expected=(
            [COLLECT_A] if demo["layout_external_only"]=="A_REFERENCE"
            else [COLLECT_B] if demo["layout_external_only"]=="B_LOCAL"
            else [MOVE_E,COLLECT_B] if demo["layout_external_only"]=="B_EAST"
            else None
        )
        if expected is None or len(samples)!=len(expected):
            raise ValueError("world executed unpreregistered physical actions")
        previous=None
        for i,(row,hash_val,expected_command) in enumerate(
            zip(samples,hashes,expected),1
        ):
            input_state=row["state"]
            after=row["observed_next_state"]
            valid_perception(input_state)
            valid_perception(after)
            if (hash_val!=digest(row)
                or row["command"]!=expected_command
                or row["terminal"] is not False
                or (i==1 and input_state!=root)
                or (i>1 and previous!=input_state)):
                raise ValueError("forged or noncontiguous noningestive physical example")
            neighbor=next(n for n in input_state["adjacent"]
                          if n["direction"]=="east")
            if (expected_command==COLLECT_B
                and "berry_b" not in input_state["current_resources"]):
                raise ValueError("collected an invisible or absent B")
            if (expected_command==MOVE_E
                and (not neighbor["passable"] or
                     "berry_b" not in neighbor["resources"])):
                raise ValueError("moved toward blocked or invisible B")
            if (expected_command==COLLECT_B
                and int(after["inventory"].get("berry_b",0)) <=
                    int(input_state["inventory"].get("berry_b",0))):
                raise ValueError("claimed berry collection without inventory gain")
            if expected_command["primitive"]=="manger":
                raise ValueError("hidden toxicity entered the physical training")
            previous=after
            records.append(row)
    if len(records)!=13:
        raise ValueError("missing physical training examples")
    example_shas=[digest(x) for x in records]
    if training["raw_examples_sha256"]!=example_shas:
        raise ValueError("physical example receipt order/hash changed")
    input_shas=[exact_key(x["state"],x["command"]) for x in records]
    if training["training_exact_inputs_sha256"]!=input_shas:
        raise ValueError("raw physical input digest mismatch")
    a_only={}
    expanded={}
    for row in records:
        key=exact_key(row["state"],row["command"])
        out=(row["observed_next_state"],row["terminal"])
        if key in expanded and expanded[key]!=out:
            raise ValueError("same first-person state/command had contradictory training outcomes")
        expanded[key]=out
        if row["family"].endswith("A_REFERENCE"):
            if key in a_only and a_only[key]!=out:
                raise ValueError("ambiguous baseline A physical outcome")
            a_only[key]=out
    if len(a_only)!=1 or len(expanded)!=7:
        raise ValueError("unregistered unique exact-key evidence count")
    if set(a_only)-set(expanded):
        raise ValueError("baseline and enriched tables have changed provenance")
    # Relative proof only: a valid empirical model can forecast these
    # collected/moved transitions. It CANNOT predict unseen ingestion effects.
    return {"source_worlds":by_id,"records":records,
            "baseline":a_only,"enriched":expanded,
            "distinct_physical_worlds":len(by_id),
            "actual_physical_steps":len(records)}


def _allowed_first_command(root):
    if "berry_b" in root["current_resources"]:
        return COLLECT_B
    east=next((n for n in root["adjacent"]
               if n["direction"]=="east"),None)
    if east is not None and east["passable"] and "berry_b" in east["resources"]:
        return MOVE_E
    return None


def recheck_trial(row,physical):
    sources=physical["source_worlds"]
    known=physical["enriched"]
    baseline=physical["baseline"]
    test_id=row["world_id"]
    if (test_id in sources
        or row["physical_steps_executed_in_heldout_world"]!=0
        or row["no_oracle_feedback_to_model"] is not True
        or row["no_B_ingestion_or_test_physics"] is not True
        or row["operator_approved_cognitive_model_installation"] is not False
        or row["hidden_B_effect_still_unidentified"] is not True):
        raise ValueError("test world was secretly trained/acted upon or made cognizant")
    root=row["first_person_state"]
    valid_perception(root)
    east=next((n for n in root["adjacent"] if n["direction"]=="east"),None)
    if east is None:
        raise ValueError("preregistered east neighbor inaccessible to first person")
    visible_local="berry_b" in root["current_resources"]
    visible_east="berry_b" in east["resources"]
    layout=row["layout_external_only"]
    if (
        (layout=="B_LOCAL" and (not visible_local or visible_east))
        or (layout=="B_EAST" and (visible_local or not visible_east or not east["passable"]))
        or (layout=="B_EAST_BLOCKED" and (visible_local or not visible_east or east["passable"]))
        or (layout=="B_NONE" and (visible_local or visible_east))
        or layout not in KNOWN_LAYOUTS | NEGATIVE_LAYOUTS
    ):
        raise ValueError("alternative visible resource/obstacle control falsified")
    if row["hidden_effect_external_only"] not in ("benign","toxic_lethal"):
        raise ValueError("outside preregistered hidden B variants")
    if ([root["x"],root["y"]]!=row["position"]
        or root["body"]["food"]!=row["food_initial"]):
        raise ValueError("test data cannot be reconstructed from first-person state")
    cohort=row["cohort"]
    if cohort not in (
        "same_observable_input","unseen_coordinates","unavailable_or_blocked"
    ):
        raise ValueError("unpreregistered test stratum")
    model_source=row["paired_physical_demonstrator"]
    if cohort=="unavailable_or_blocked":
        if model_source is not None or row[
            "layout_external_only"] not in NEGATIVE_LAYOUTS:
            raise ValueError("negative context claimed a trained paired world")
        if row["position"]!=[5,5]:
            raise ValueError("unknown-layout control not at preregistered location")
    else:
        if model_source not in sources:
            raise ValueError("heldout source world missing")
        src=sources[model_source]
        if src["layout_external_only"]!=row["layout_external_only"]:
            raise ValueError("test source mismatch of accessible local resources")
        if src["hidden_effect_external_only"]==row[
            "hidden_effect_external_only"]:
            raise ValueError("paired holdout did not use opposite latent effect")
        if row["layout_external_only"] not in KNOWN_LAYOUTS:
            raise ValueError("known B source mapped to invalid layout")
        if cohort=="same_observable_input" and src[
            "root_accessible"]!=root:
            raise ValueError("paired source/test observable input differs")
        if cohort=="unseen_coordinates" and (
            row["position"]!=[7,7] or
            src["root_accessible"]["x"]==root["x"]):
            raise ValueError("unseen coordinate is not outside training")
    cmd=_allowed_first_command(root)
    is_known=cohort=="same_observable_input"
    if cmd is None and is_known:
        raise ValueError("demonstrated root lacks the first observable command")
    input_key=(exact_key(root,cmd) if cmd is not None else None)
    a_match=input_key in baseline if input_key else False
    b_match=input_key in known if input_key else False
    if a_match or b_match!=is_known:
        raise ValueError("independently recomputed exact-root coverage differs")
    predicted_first=(cmd if b_match else None)
    expected_partial=is_known
    if is_known:
        before_b=int(root["inventory"].get("berry_b",0))
        current=known[input_key][0]
        if row["layout_external_only"]=="B_EAST":
            after_move=current
            # The second observed action may *only* be treated as known if its
            # full resulting accessible state was a training input.
            second=exact_key(after_move,COLLECT_B)
            if second not in known:
                raise ValueError("east movement known but collection prefix missing")
            current=known[second][0]
        if int(current["inventory"].get("berry_b",0))<=before_b:
            raise ValueError("progress made without demonstrated edible inventory")
        if float(current["body"]["food"]) > float(root["body"]["food"]):
            raise ValueError("collection falsely treated as physical eating")
    for key,should_known in (
        ("baseline_A_only",False),
        ("enriched_demonstrated_prefix",is_known),
    ):
        result=row[key]
        if (
            result["arm"]!=("A_ONLY" if key=="baseline_A_only"
                          else "A_PLUS_B_KNOWN_PREFIX")
            or result["status"]!=("partial_progress" if should_known
                                 else "incomplete_model")
            or result["root_available_edges"]!=int(should_known)
            or result["partial_progress"]!=should_known
            or result["commands"]!=([predicted_first]
                if should_known else [])
            or result["predicted_commands"]!=([predicted_first]
                if should_known else [])
            or result["no_physical_command_dispatched"] is not True
            or result["has_any_ingestion_prediction"] is not False
            or result["guarantees_berry_b_safe"] is not False
            or result["true_I0_UC_measured"] is not None
        ):
            raise ValueError("published Stage6 shadow invented a result or safety")
        if (result["diagnostic"]["status"]!=result["status"]
            or result["diagnostic"]["root_available_edges"]!=
                result["root_available_edges"]
            or result["root_candidate_edges"]<
                result["root_available_edges"]):
            raise ValueError("false/inconsistent actual Stage6 diagnostic receipt")
    return {
        "cohort":cohort,
        "baseline_unavailable":not a_match,
        "known_first_edge":b_match,
        "partial_progress":expected_partial,
        "test_physical_steps":0,
        "no_ingestion_or_certification":True,
    }


def independent_reaudit(training,heldout,summary):
    if (
        summary.get("schema")!="a230ze-independent-exact-coverage-shadow-v1"
        or summary.get("code_sha")!=SOURCE_SHA
        or summary.get("new_I0_births")!=0
        or summary.get("new_I0_autonomous_world_steps")!=0
        or summary.get("detached_worlds_total")!=33
        or summary.get("detached_physical_training_steps")!=13
        or summary.get("heldout_worlds_with_no_physical_actions")!=24
        or summary.get("heldout_physical_actions")!=0
        or summary.get("model_contains_no_B_ingestion") is not True
        or summary.get("model_contains_no_safety_certificate") is not True
        or summary.get("no_commands_dispatched_by_stage6") is not True
        or summary.get("oracle_or_hidden_B_effect_fed_to_model") is not False
        or summary.get("actual_I0_UC_measured") is not False
        or summary.get("actual_I0_food_goal_success_proven") is not False
        or summary.get("Stage6_production_model_accepted") is not False
    ):
        raise ValueError("original physical experiment or no-I0 boundary changed")
    physical=independent_physical_training(training)
    if len(heldout)!=24:
        raise ValueError("unregistered test world count")
    ids=set()
    recomputed=[]
    for row in heldout:
        if row["world_id"] in ids:
            raise ValueError("duplicate heldout world")
        ids.add(row["world_id"])
        recomputed.append(recheck_trial(row,physical))
    strata_sets=defaultdict(set)
    for row in heldout:
        condition=(row["layout_external_only"],row["food_initial"],
                   row["hidden_effect_external_only"])
        if condition in strata_sets[row["cohort"]]:
            raise ValueError("duplicated factorial test condition")
        strata_sets[row["cohort"]].add(condition)
    expected_known={(layout,food,hidden) for layout in KNOWN_LAYOUTS
                    for food in (35.0,45.0) for hidden in ("benign","toxic_lethal")}
    expected_negative={(layout,food,hidden) for layout in NEGATIVE_LAYOUTS
                    for food in (35.0,45.0) for hidden in ("benign","toxic_lethal")}
    if (strata_sets["same_observable_input"]!=expected_known
        or strata_sets["unseen_coordinates"]!=expected_known
        or strata_sets["unavailable_or_blocked"]!=expected_negative):
        raise ValueError("factorial hidden effects or visible contexts incomplete")
    metrics={}
    for cohort,expected in (
        ("same_observable_input",(8,8,0)),
        ("unseen_coordinates",(8,0,8)),
        ("unavailable_or_blocked",(8,0,8)),
    ):
        cases=[x for x in recomputed if x["cohort"]==cohort]
        if len(cases)!=expected[0]:
            raise ValueError("original heldout conditions changed")
        item={
            "test_worlds":len(cases),
            "test_physical_actions":0,
            "baseline_incomplete":sum(x["baseline_unavailable"] for x in cases),
            "enriched_partial_progress":sum(x["partial_progress"] for x in cases),
            "enriched_incomplete":sum(not x["known_first_edge"] for x in cases),
            "enriched_known_root":sum(x["known_first_edge"] for x in cases),
            "false_eat_prediction":0,
        }
        if (item["enriched_partial_progress"],item["enriched_incomplete"]
            )!=(expected[1],expected[2]) or item!=summary["cohorts"][cohort]:
            raise ValueError("stratum Stage6 counters not supported by independent evidence")
        metrics[cohort]=item
    return {
        "schema":"a230zf-archive-only-independent-stage6-coverage-v1",
        "original_run":SOURCE_RUN,"original_SHA":SOURCE_SHA,
        "physical_source_worlds_reaudited":9,
        "physical_source_steps_reaudited":13,
        "heldout_worlds_reaudited":24,
        "heldout_worlds_physically_applied":0,
        "unique_exact_input_keys":len(physical["enriched"]),
        "A_only_exact_input_keys":len(physical["baseline"]),
        "all_input_hashes_and_physical_example_hashes_verified":True,
        "independent_exact_key_coverage_and_B_inventory_progress_recalculated":True,
        "new_I0_births":0,"new_physical_worlds":0,
        "new_physical_steps":0,
        "stage6_reexecuted_by_independent_archive_auditor":False,
        "worldbody_apply_independently_replayed_from_archive":False,
        "hidden_effect_never_observed_in_B_ingestion":True,
        "benign_and_toxic_variants_both_present_in_demonstrations":True,
        "never_a_safe_B_certification":True,
        "cognitive_model_deployment":"NO-GO",
        "stage12":"PARTIAL","issue110":"OPEN",
        "cohorts":metrics,
    }


def read_sealed(folder):
    loaded={}
    for name,expected in SHA_BYTES.items():
        hits=list(folder.rglob(name))
        if len(hits)!=1:
            raise ValueError("original archive file missing or duplicated")
        raw=hits[0].read_bytes()
        if sha256(raw).hexdigest()!=expected:
            raise ValueError("source JSON byte digest no longer matches original")
        loaded[name]=raw
    return loaded


def run(source311:Path,source312:Path,out:Path):
    a=read_sealed(source311)
    b=read_sealed(source312)
    if a!=b:
        raise ValueError("original Python versions do not agree byte for byte")
    summary=independent_reaudit(
        json.loads(a["a230ze-training-manifest.json"]),
        json.loads(a["a230ze-heldout-shadows.json"]),
        json.loads(a["a230ze-summary.json"]),
    )
    summary.update({
        "original_archive_json_shas":SHA_BYTES,
        "python_311_312_source_bytes_equal":True,
        "this_auditor_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    })
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zf-independent-archive-score.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZF_SUMMARY "+json.dumps({
        "original_run":SOURCE_RUN,
        "source_worlds":summary["physical_source_worlds_reaudited"],
        "source_steps":summary["physical_source_steps_reaudited"],
        "heldout":summary["heldout_worlds_reaudited"],
        "exact_unique_keys":summary["unique_exact_input_keys"],
        "baseline_keys":summary["A_only_exact_input_keys"],
        "cohorts":summary["cohorts"],
        "new_I0_births":0,
        "new_physical_steps":0,
        "stage12":"PARTIAL",
    },sort_keys=True),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-311",type=Path,required=True)
    p.add_argument("--source-312",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    run(args.source_311,args.source_312,args.output_dir)


if __name__=="__main__":
    main()
