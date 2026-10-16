"""A2.30-ZL: independent READ-ONLY audit of ZK physically born-analog probes.

Read immutable original ZK physical data and independent original ZB birth
summaries. Reimplement accessible states, candidate commands, exact-key
knowledge, temporal ownership and hidden-mortality contradictions without
importing WorldBody, SimulatorPlanner, Equipment or the original ZK runner.

Pre-registered AFTER original ZK results and BEFORE this audit code,
see stage12-issue110-b-a230zl-ownworld-independent-prereg-2026-10-15.fr.md.
NO NEW PHYSICS. NO NEW I0 INDIVIDUALS. No safety claim is allowed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

ORIGINAL_ZK_RUN=38783733130
ORIGINAL_ZK_SHA="2b01e75caa4b5edac6b971b274a79eb9d8034869"
ORIGINAL_ZB_RUN=38767643472
ORIGINAL_ZB_SHA="2a19742df22f27752635203304097134a3009c45"
ZK_DIGESTS={
    "a230zk-A-physical-source.json":
        "1ca203af3615c1f9dcd6eb84198a571cbb7ee4880d31cc2ab5dcbd0be65f0517",
    "a230zk-ownworld-tests.json":
        "e4824e85d1ce1183617bee75290a5f41772fa43a995a41d78cacffefde9f8b31",
    "a230zk-summary.json":
        "8cc6e967d598daede5d143a2af23b7fd75dafeb58581a39467bfe7a8766a864b",
}
ZB_DIGESTS={
    "3.11":"ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b",
    "3.12":"ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362",
}
PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST","B_EAST_BLOCKED")
VARIANTS=("benign","toxic_lethal")
HAZARDS=("east_clear","east_hidden_lethal")
ARMS=("ABSTAIN","VISIBLE_PROBE")
VISIBLE_KEYS={
    "schema_version","x","y","body","inventory","current_water_source",
    "current_resources","adjacent","known_shelter_here","is_night",
}
NEIGHBOR_KEYS={
    "direction","x","y","passable","water_source","resources","creature",
}
B_COLLECT={"primitive":"collecter","parameters":{"target":"berry_b"}}
B_EAT={"primitive":"manger","parameters":{"target":"berry_b"}}
MOVE_E={"primitive":"se_deplacer","parameters":{"direction":"east"}}
MOVE_N={"primitive":"se_deplacer","parameters":{"direction":"north"}}
A_COLLECT={"primitive":"collecter","parameters":{"target":"berry_a"}}
A_EAT={"primitive":"manger","parameters":{"target":"berry_a"}}


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def sealed_read(root,filename,expected_digest):
    matches=list(Path(root).rglob(filename))
    if len(matches)!=1:
        raise ValueError("archived science source missing or ambiguous: "+filename)
    raw=matches[0].read_bytes()
    if sha256(raw).hexdigest()!=expected_digest:
        raise ValueError("immutable scientific source SHA256 altered: "+filename)
    return raw


def immutable_sources(zk311,zk312,zb311,zb312):
    a={name:sealed_read(zk311,name,h) for name,h in ZK_DIGESTS.items()}
    b={name:sealed_read(zk312,name,h) for name,h in ZK_DIGESTS.items()}
    if a!=b:
        raise ValueError("original physical 3.11/3.12 ZK JSON differ")
    old1=json.loads(sealed_read(
        zb311,"a230zb-summary.json",ZB_DIGESTS["3.11"],
    ))
    old2=json.loads(sealed_read(
        zb312,"a230zb-summary.json",ZB_DIGESTS["3.12"],
    ))
    return (
        json.loads(a["a230zk-A-physical-source.json"]),
        json.loads(a["a230zk-ownworld-tests.json"]),
        json.loads(a["a230zk-summary.json"]),
        old1,old2,
    )


def accessible(state):
    if type(state) is not dict or set(state)!=VISIBLE_KEYS:
        raise ValueError("non-first-person or hidden/future root variable")
    if (set(state["body"])!={"energy","food","water","integrity"}
        or set(state["inventory"])!={"berry_a","berry_b","wood","stone","tool"}
        or len(state["adjacent"])!=4
        or {n["direction"] for n in state["adjacent"]}!=
            {"north","south","east","west"}
        or any(set(n)!=NEIGHBOR_KEYS for n in state["adjacent"])):
        raise ValueError("incomplete cognitive capture or unlicensed neighbor field")
    return state


def key(state,command):
    return digest({"state":accessible(state),"command":command})


def candidates(state):
    """Standalone Stage6 candidate reimplementation, no Stage6 import."""
    accessible(state)
    out=[]
    for n in state["adjacent"]:
        if n["passable"]:
            out.append({"primitive":"se_deplacer",
                        "parameters":{"direction":n["direction"]}})
    for r in sorted(set(state["current_resources"])):
        out.append({"primitive":"collecter","parameters":{"target":r}})
    for r in ("berry_a","berry_b"):
        if state["inventory"].get(r,0)>0:
            out.append({"primitive":"manger","parameters":{"target":r}})
    if state["current_water_source"]:
        out.append({"primitive":"boire","parameters":{}})
    if state["inventory"].get("stone",0)>0:
        out.append({"primitive":"poser_une_pierre","parameters":{}})
    if (state["inventory"].get("stone",0)>0
        and state["inventory"].get("wood",0)>0):
        out.append({"primitive":"fabriquer_outil","parameters":{}})
    out.extend(({"primitive":"dormir","parameters":{}},
                {"primitive":"attendre","parameters":{}}))
    return out


def firstperson_probe(state,arm,prior):
    """Reimplement ZK's preregistered LAB action rule independently."""
    accessible(state)
    if arm not in ARMS:
        raise ValueError("unregistered original action policy")
    if any(c not in (MOVE_E,B_COLLECT) for c in prior):
        raise ValueError("foreign or future action in perceptual policy history")
    if arm=="ABSTAIN":
        return None
    east=next(n for n in state["adjacent"] if n["direction"]=="east")
    if not prior:
        if "berry_b" in state["current_resources"]:
            return B_COLLECT
        if "berry_b" in east["resources"] and east["passable"]:
            return MOVE_E
        return None
    if prior==(MOVE_E,) and "berry_b" in state["current_resources"]:
        return B_COLLECT
    return None


def historical_birth_roots(old1,old2):
    if (old1.get("schema")!="a230zb-autonomous-alternative-lived-v1"
        or old2.get("schema")!="a230zb-autonomous-alternative-lived-v1"
        or old1.get("git_sha")!=ORIGINAL_ZB_SHA
        or old2.get("git_sha")!=ORIGINAL_ZB_SHA
        or old1.get("independent_new_I0_births")!=12
        or old2.get("independent_new_I0_births")!=12
        or old1.get("actual_autonomous_world_steps")!=384
        or old2.get("actual_autonomous_world_steps")!=384
        or len(old1.get("lives",()))!=12
        or len(old2.get("lives",()))!=12):
        raise ValueError("non-authentic original autonomous ZB 12-birth source")
    left={x["birth_id"]:x for x in old1["lives"]}
    right={x["birth_id"]:x for x in old2["lives"]}
    if len(left)!=12 or set(left)!=set(right):
        raise ValueError("duplicated or mismatched original mortal identifiers")
    visible={}
    for ident,row in left.items():
        other=right[ident]
        if (row["world_steps"]!=32 or
            row["confirmed_B_ingestions"] or
            row["experienced_B_commands_with_motives"] or
            len(row["equipment_sha256_A_only"])!=64):
            raise ValueError("original I0 memory erroneously contains B")
        for k in (
            "initial_accessible_projection","equipment_sha256_A_only",
            "profile","layout","hidden_B_external_only",
            "world_steps","executed_motor_commands",
        ):
            if row[k]!=other[k]:
                raise ValueError("ZB 3.11/3.12 first-person source disagrees")
        accessible(row["initial_accessible_projection"])
        p,l,h=row["profile"],row["layout"],row["hidden_B_external_only"]
        if (p not in PROFILES or l not in LAYOUTS[:3]
            or h not in VARIANTS
            or (p,l,h) in visible):
            raise ValueError("not an independent 2x3x2 original birth")
        visible[(p,l,h)]=row
    if len(visible)!=12:
        raise ValueError("12 original birth root cells not complete")
    return visible


def physical_A_reference_models(source,births):
    if (source.get("schema")!="a230zk-physical-reference-models-v1"
        or source.get("all_own_history_examples_are_from_the_same_test_world") is not True
        or source.get("never_trained_on_B_ingestion") is not True
        or source.get("original_births_are_archived_untouched")!=12
        or len(source.get("A_reference_worlds",()))!=2):
        raise ValueError("historical A reference physical source invalid")
    training={}
    for row in source["A_reference_worlds"]:
        identity=row["source_world_id"]
        if not identity.startswith("A_REFERENCE-"):
            raise ValueError("training examples not physically sourced A")
        profile=identity.removeprefix("A_REFERENCE-")
        if profile not in PROFILES or profile in training:
            raise ValueError("duplicate or unknown A reference profile")
        xs=row["physical_examples"]
        if (len(xs)!=4
            or row["physical_step_count"]!=4
            or row["not_an_I0_birth"] is not True
            or row["all_actions_physical_nonterminal"] is not True
            or row["no_B_ingestion"] is not True
            or xs[0]["state"]!=row["root_first_person"]):
            raise ValueError("A prebirth physical model source is corrupted")
        expected=(MOVE_N,MOVE_E,A_COLLECT,A_EAT)
        for i,(ex,cmd) in enumerate(zip(xs,expected)):
            if (row["physical_example_sha256"][i]!=digest(ex)
                or ex["command"]!=cmd or ex["terminal"] is not False
                or i and ex["state"]!=xs[i-1]["observed_next_state"]):
                raise ValueError("A prebirth physical receipt/canonical step altered")
            accessible(ex["state"]);accessible(ex["observed_next_state"])
        training[profile]=xs
    if set(training)!=set(PROFILES):
        raise ValueError("prebirth cohort lacks one body profile")
    for (p,l,h),birth in births.items():
        if source["A_model_digest_by_profile"][p]!=birth["equipment_sha256_A_only"]:
            raise ValueError("reconstructed A model hash does not match real I0 birth")
    return training


def exact_dictionary(examples):
    training={}
    for ex in examples:
        s=accessible(ex["state"]);accessible(ex["observed_next_state"])
        c=ex["command"]
        if c==B_EAT:
            raise ValueError("unwitnessed berry B ingestion in Equipment")
        h=key(s,c)
        if h in training and (
            training[h]["observed_next_state"]!=ex["observed_next_state"]
            or training[h]["terminal"]!=ex["terminal"]
        ):
            raise ValueError("conflicting identical firstperson exact-key outcomes")
        training[h]=ex
    return training


def independent_audit(source,worlds,summary,old1,old2):
    births=historical_birth_roots(old1,old2)
    phys_A=physical_A_reference_models(source,births)
    if len(worlds)!=64 or len({x["world_id"] for x in worlds})!=64:
        raise ValueError("original 64 world factorial missing/duplicated")
    scores=Counter()
    by_arm=defaultdict(Counter)
    partitions=defaultdict(list)
    effect_pairs=defaultdict(list)
    test_seen=set()
    for w in worlds:
        p,l,h,z,arm=(
            w["profile"],w["layout_external_only"],
            w["hidden_B_external_only"],w["hidden_lethal_zone_external_only"],
            w["protocol_frozen_before_physics"],
        )
        cell=(p,l,h,z,arm)
        if (p not in PROFILES or l not in LAYOUTS or
            h not in VARIANTS or z not in HAZARDS or arm not in ARMS
            or cell in test_seen):
            raise ValueError("duplicated, missing or substituted factorial cell")
        test_seen.add(cell)
        if (w["world_id"]!=f"a230zk:{p}:{l}:{h}:{z}:{arm}"
            or w["postterminal_firstperson_capture"] is not None
            or w["no_berry_B_ingestion"] is not True
            or w["berry_B_safety_certified"] is not False
            or w["lived_i0_UC_cost"] is not None
            or w["i0_autonomous_steps"]!=0 or w["i0_births"]!=0
            or w["oracle_feedback_to_cognitive_policy"] is not False
            or w["no_foreign_world_examples_as_own_memory"] is not True
            or w["original_prebirth_A_equipment_sha256"]!=
                births[(p,"B_NONE",h)]["equipment_sha256_A_only"]):
            raise ValueError("world identity, Oracle, cognitive UC or model was fabricated")
        root=accessible(w["firstperson_birth_state"])
        if w["firstperson_birth_sha256"]!=digest(root):
            raise ValueError("initial root digest changed")
        if l!="B_EAST_BLOCKED":
            if root!=births[(p,l,h)]["initial_accessible_projection"]:
                raise ValueError("not exactly the original autonomous firstperson birth")
            scores["archived_original_birth_matches"]+=1
        else:
            east=next(n for n in root["adjacent"] if n["direction"]=="east")
            if not ("berry_b" in east["resources"] and east["passable"] is False):
                raise ValueError("visible obstacle negative control absent")
        for k in ("physics_config_sha256_external","layout_sha256_external"):
            if type(w[k]) is not str or len(w[k])!=64:
                raise ValueError("external physics provenance SHA omitted")
        physical=w["real_physical_lab_receipts"]
        chosen=w["lab_perceptual_choices"]
        sensed=w["firstperson_history_while_alive"]
        queries=w["stage6_shadow_queries"]
        if (w["real_physical_steps"]!=len(physical)
            or len(chosen)!=len(sensed)
            or len(chosen)!=len(queries)
            or len(chosen)==0
            or sensed[0]["state"]!=root):
            raise ValueError("lived/physical/shadow chronology corrupted")
        alive_history=[]
        for idx,(cho,view,query) in enumerate(zip(chosen,sensed,queries),1):
            state=accessible(cho["firstperson_state"])
            if (view["t_monde"]!=idx
                or cho["t_monde"]!=idx
                or state!=view["state"]
                or cho["firstperson_sha256"]!=digest(state)
                or cho["external_world_hidden_effect_used_in_choice"] is not False
                or cho["certifies_safe"] is not False
                or cho["actual_I0_selected_or_authorized_this_command"] is not False):
                raise ValueError("subjective perception and lab authority crossed")
            policy_command=firstperson_probe(
                state,arm,tuple(x["command"] for x in alive_history),
            )
            if cho["preregistered_external_lab_proposal"]!=policy_command:
                raise ValueError("hidden world truth affected laboratory policy")
            if cho["previous_command_receipts"]!=[
                x["command"] for x in alive_history
            ]:
                raise ValueError("future physical command entered firstperson history")
            # Train ONLY on prebirth A and living consequences ALREADY received.
            past=[x["physical_example"] for x in alive_history]
            assert all(x["terminal"] is False for x in past)
            table=exact_dictionary(phys_A[p]+past)
            choices=candidates(state)
            n=sum(key(state,c) in table for c in choices)
            actual=query["planner"]
            diag=actual["last_search_diagnostic"]
            if (query["source_world_id"]!=w["world_id"]
                or query["t_monde"]!=idx
                or query["visible_state_sha256"]!=digest(state)
                or query["own_living_prior_examples"]!=len(past)
                or query["historical_A_examples"]!=4
                or query["lab_next_proposal"]!=policy_command
                or query["lab_next_command_known_in_frozen_exact_model"]
                    !=(key(state,policy_command) in table
                       if policy_command is not None else None)
                or query["no_shadow_dispatch"] is not True
                or query["no_real_I0_UC_measured"] is not True
                or actual["no_shadow_action_dispatched"] is not True
                or actual["berry_b_safety_certified"] is not False
                or actual["actual_i0_uc_measured"] is not False
                or actual["target_food"]!=float(state["body"]["food"])+5.0
                or actual["root_available_edges"]!=n
                or actual["root_candidate_edges"]!=len(choices)
                or actual["root_unavailable_edges"]!=len(choices)-n
                or diag["status"]!=actual["status"]
                or diag["root_available_edges"]!=n
                or diag["root_candidate_edges"]!=len(choices)
                or diag["root_unavailable_edges"]!=len(choices)-n):
                raise ValueError("Stage6 first-step roots or UC/latent observations forged")
            if (any(c==B_EAT for c in actual["predicted_commands"])
                or actual["status"]=="plan_found"):
                raise ValueError("undemonstrated B ingestion or goal fabricated")
            if policy_command is not None:
                if policy_command not in choices or key(state,policy_command) in table:
                    raise ValueError("own future B command was not genuinely novel")
            if actual["root_available_edges"]==0:
                if (actual["status"]!="incomplete_model"
                    or diag["root_model_diagnostic"]!="no_predictable_first_step"):
                    raise ValueError("unpredictable current first action was misclassified")
            else:
                if actual["status"]!="partial_progress":
                    raise ValueError("A-only measurable root progress was not preserved")
            scores["independent_stage6_shadow_roots_verified"]+=1
            scores["living_prior_instances_verified"]+=len(past)
            scores["status_"+actual["status"]]+=1
            if idx==1:
                scores["initial_root_searches"]+=1
            elif idx==2:
                scores["postfirst_surviving_searches"]+=1
            elif idx==3:
                scores["postsecond_surviving_searches"]+=1
            if idx>1 and actual["root_available_edges"]==0:
                scores["current_new_state_unknown_roots"]+=1
            if idx<=len(physical):
                receipt=physical[idx-1]
                ex=receipt["physical_example"]
                if (receipt["world_id"]!=w["world_id"]
                    or receipt["t_monde"]!=idx
                    or receipt["physical_example_sha256"]!=digest(ex)
                    or receipt["command"]!=policy_command
                    or ex["command"]!=policy_command
                    or ex["state"]!=state
                    or receipt["preaction_observable"]!=state
                    or receipt["postaction_external_only"]!=ex["observed_next_state"]
                    or receipt["terminal_external_only"]!=ex["terminal"]
                    or receipt["not_autonomous_I0_or_shadow_dispatched"] is not True):
                    raise ValueError("physical WorldBody event receipt not contiguous")
                accessible(ex["observed_next_state"])
                if ex["terminal"]:
                    if (idx!=len(physical)
                        or w["physically_terminal_step_external_only"]!=idx
                        or w["external_postterminal_state_not_lived"]!=
                            ex["observed_next_state"]
                        or len(queries)!=idx
                        or len(sensed)!=idx):
                        raise ValueError("postmortem physical event became subjective memory")
                    scores["fatal_motor_closures"]+=1
                    continue
                if (idx>=len(sensed)
                    or sensed[idx]["state"]!=ex["observed_next_state"]):
                    raise ValueError("nonterminal physical consequence not perceived later")
                alive_history.append(receipt)
                scores["nonterminal_self_observed_steps"]+=1
                # This exact key enters memory only retrospectively, *after*
                # the action and only if the own world remains alive.
                if key(state,policy_command) in table:
                    raise ValueError("future transition known before physics")
                if key(state,policy_command) not in exact_dictionary(
                    phys_A[p]+[x["physical_example"] for x in alive_history]
                ):
                    raise ValueError("physically observed own edge failed to enter history")
                scores["past_own_edges_acquired_after_survival"]+=1
        if w["own_world_prior_examples_for_final_living_state"]!=len(
            alive_history
        ):
            raise ValueError("postmortem or future own memory count wrong")
        if len(w["past_edges_known_only_retrospectively"])!=len(alive_history):
            raise ValueError("old known-edge hindsight incorrectly attributed")
        for sample in w["past_edges_known_only_retrospectively"]:
            if (sample["past_state_command_now_exactly_known"] is not True
                or sample["current_state_is_different"] is not True
                or sample["not_issued_as_current_firstperson_prediction"] is not True):
                raise ValueError("hindsight relabelled prospective prediction")
        if w["physically_terminal_step_external_only"] is None and any(
            x["terminal_external_only"] for x in physical
        ):
            raise ValueError("terminal outcome omitted from subject boundary")
        if w["physically_terminal_step_external_only"] is not None and (
            not physical or not physical[-1]["terminal_external_only"]
        ):
            raise ValueError("false subjective death terminal label")
        if w["first_action_physically_executed"]!=(len(physical)>0):
            raise ValueError("unreported commanded physics")
        expected=(0 if arm=="ABSTAIN" or l in ("B_NONE","B_EAST_BLOCKED")
                  else 1 if l=="B_LOCAL" or z=="east_hidden_lethal"
                  else 2)
        if len(physical)!=expected:
            raise ValueError("physical action was chosen post hoc")
        if any(e["command"]["primitive"]=="manger" for e in physical):
            raise ValueError("B or other ingestive motor action violated preregistration")
        scores["test_physical_actions"]+=len(physical)
        scores["abstaining_worlds"]+=len(physical)==0
        scores["worlds_with_motor_probe"]+=len(physical)>0
        by_arm[(l,arm)]["worlds"]+=1
        by_arm[(l,arm)]["steps"]+=len(physical)
        by_arm[(l,arm)]["terminals"]+=w["physically_terminal_step_external_only"] is not None
        partitions[(p,l,h,arm)].append(w)
        effect_pairs[(p,l,z,arm)].append(w)
    if len(test_seen)!=64 or len(partitions)!=32 or len(effect_pairs)!=32:
        raise ValueError("full factorial or hidden contrast coverage missing")
    terminal_alias=0
    for (p,l,h,arm),pair in partitions.items():
        if len(pair)!=2 or {
            q["hidden_lethal_zone_external_only"] for q in pair
        }!=set(HAZARDS):
            raise ValueError("hidden motor context not balanced")
        left,right=pair
        if (left["firstperson_birth_state"]!=right["firstperson_birth_state"]
            or left["lab_perceptual_choices"][0][
                "preregistered_external_lab_proposal"]!=right[
                "lab_perceptual_choices"][0]["preregistered_external_lab_proposal"]):
            raise ValueError("latent lethal motor cause shown before exposure")
        if l=="B_EAST" and arm=="VISIBLE_PROBE":
            safe=next(q for q in pair if q["hidden_lethal_zone_external_only"]=="east_clear")
            death=next(q for q in pair if q["hidden_lethal_zone_external_only"]=="east_hidden_lethal")
            ss=safe["real_physical_lab_receipts"][0]
            ds=death["real_physical_lab_receipts"][0]
            if (ss["command"]!=MOVE_E or ds["command"]!=MOVE_E
                or ss["preaction_observable"]!=ds["preaction_observable"]
                or ss["terminal_external_only"] is not False
                or ds["terminal_external_only"] is not True
                or ss["postaction_external_only"]!=ds["postaction_external_only"]
                or death["postterminal_firstperson_capture"] is not None
                or len(death["stage6_shadow_queries"])!=1):
                raise ValueError("aliasing of terminal-only hidden motor consequence falsified")
            terminal_alias+=1
    if terminal_alias!=4:
        raise ValueError("four hidden deadly move twin pairs missing")
    for (p,l,z,arm),pair in effect_pairs.items():
        if len(pair)!=2 or {q["hidden_B_external_only"] for q in pair}!=set(VARIANTS):
            raise ValueError("hidden berry toxicity contrast missing")
        if (pair[0]["firstperson_birth_state"]!=pair[1]["firstperson_birth_state"]
            or [e["command"] for e in pair[0]["real_physical_lab_receipts"]]!=
                [e["command"] for e in pair[1]["real_physical_lab_receipts"]]
            or pair[0]["physically_terminal_step_external_only"]!=
               pair[1]["physically_terminal_step_external_only"]):
            raise ValueError("noningestive policy sees hidden berry effect")
    controls=source["exact_mortal_counterfactual_controls"]
    if len(controls)!=4:
        raise ValueError("one-sided physically unsafe controls missing")
    for c in controls:
        if (c["same_firstperson_input_and_primitive"] is not True
            or c["model_trained_on_one_safe_physical_move_only"] is not True
            or c["nominal_exact_table_confidence"]!=1.0
            or c["predicted_terminal"] is not False
            or c["physically_terminal_external"] is not True
            or c["physical_next_state_equal_despite_terminal_difference"] is not True
            or c["safety_calibration_inferred"] is not False
            or c["not_a_live_I0_prediction_or_command"] is not True):
            raise ValueError("unsafe hidden terminal was disguised as safe inference")
    if (
        scores["test_physical_actions"]!=20
        or scores["fatal_motor_closures"]!=4
        or scores["nonterminal_self_observed_steps"]!=16
        or scores["past_own_edges_acquired_after_survival"]!=16
        or scores["initial_root_searches"]!=64
        or scores["postfirst_surviving_searches"]!=12
        or scores["postsecond_surviving_searches"]!=4
        or scores["independent_stage6_shadow_roots_verified"]!=80
        or scores["status_partial_progress"]!=16
        or scores["status_incomplete_model"]!=64
        or scores["current_new_state_unknown_roots"]!=16
        or scores["abstaining_worlds"]!=48
        or scores["worlds_with_motor_probe"]!=16
    ):
        raise ValueError("preregistered physical or exact-key firstperson totals disagree "
                         +json.dumps(dict(scores),sort_keys=True))
    if (summary.get("schema")!="a230zk-ownworld-motor-bootstrap-physical-v1"
        or summary.get("original_code_sha")!=ORIGINAL_ZK_SHA
        or summary.get("independent_total_worlds")!=66
        or summary.get("actual_A_reference_physical_steps")!=8
        or summary.get("real_test_physical_steps")!=20
        or summary.get("total_new_physical_steps")!=28
        or summary.get("physical_terminal_worlds")!=4
        or summary.get("real_Stage6_shadow_searches")!=80
        or summary.get("new_I0_births")!=0
        or summary.get("new_I0_autonomous_steps")!=0
        or summary.get("berry_B_ingestions")!=0
        or summary.get("I0_UC_measured") is not False
        or summary.get("cognitive_deployment")!="NO-GO"
        or summary.get("exact_one_sided_lethal_prediction_mismatches")!=4
        or summary.get("paired_observationally_identical_hidden_motor_deaths")!=4):
        raise ValueError("ZK original signed scientific summary contradicts archives")
    return {
        "schema":"a230zl-independent-ownworld-archive-audit-v1",
        "original_physical_run":ORIGINAL_ZK_RUN,
        "original_autonomous_birth_run":ORIGINAL_ZB_RUN,
        "original_i0_birth_roots_read_only":12,
        "original_i0_world_steps_not_reexecuted":384,
        "physical_training_worlds_ZK_verified_from_receipts":2,
        "physical_test_worlds_ZK_verified_from_receipts":64,
        "physical_A_reference_steps_ZK":8,
        "physical_test_steps_ZK":scores["test_physical_actions"],
        "physical_fatal_move_worlds_ZK":scores["fatal_motor_closures"],
        "physically_nonterminal_B_probe_steps_ZK":
            scores["nonterminal_self_observed_steps"],
        "former_states_learned_only_retrospectively":
            scores["past_own_edges_acquired_after_survival"],
        "Stage6_original_queries_root_counts_independently_verified":
            scores["independent_stage6_shadow_roots_verified"],
        "Stage6_original_status_histogram":{
            "partial_progress":scores["status_partial_progress"],
            "incomplete_model":scores["status_incomplete_model"],
        },
        "new_current_states_still_unknown_after_probing":
            scores["current_new_state_unknown_roots"],
        "no_hidden_lethal_preexposure_signal":True,
        "identical_visible_postmove_but_different_terminal_outcomes":
            terminal_alias,
        "one_sided_model_falsely_predicts_nonterminal_in_deadly_worlds":4,
        "A_B_berry_ingestions_verified_in_test_worlds":0,
        "I0_UC_measured":False,
        "exact_input_alone_does_not_certify_safety":True,
        "external_death_not_firstperson_lived":True,
        "independent_rerun_of_WorldBody_apply":False,
        "independent_rerun_of_Stage6_search":False,
        "new_physical_worlds":0,"new_physical_steps":0,
        "new_I0_births":0,"new_I0_autonomous_steps":0,
        "alternative_food_safety_certified":False,
        "normative_MVP_or_runtime_modified":False,
        "Stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
        "source_ZK_JSON_sha256":ZK_DIGESTS,
        "original_ZB_JSON_sha256":ZB_DIGESTS,
        "both_ZK_Python_outputs_identical":True,
        "original_ZB_Python_byte_difference_preserved":True,
    }


def execute(zk311,zk312,zb311,zb312,out):
    original=immutable_sources(zk311,zk312,zb311,zb312)
    report=independent_audit(*original)
    report["audit_commit_sha"]=subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True,
    ).strip()
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zl-independent-report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZL_SUMMARY "+json.dumps({
        k:v for k,v in report.items()
        if k not in ("source_ZK_JSON_sha256","original_ZB_JSON_sha256")
    },sort_keys=True),flush=True)
    return report


def main():
    ap=argparse.ArgumentParser()
    for option in ("zk311","zk312","zb311","zb312","output_dir"):
        ap.add_argument("--"+option.replace("_","-"),required=True,type=Path)
    args=ap.parse_args()
    execute(args.zk311,args.zk312,args.zb311,args.zb312,args.output_dir)


if __name__=="__main__":
    main()
