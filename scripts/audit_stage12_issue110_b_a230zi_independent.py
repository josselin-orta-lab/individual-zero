"""A2.30-ZI: independent archive-only first-person alternative-food audit.

The model-facing input is ONLY first-person SimulationState, recorded before
each physical action. Scores are recomputed from sealed original archives,
WITHOUT importing the Z producer runner, WorldBody, Stage6Planner, Equipment,
Oracle, or any production runtime. No new physical worlds or I0 lives.

An archive-only reviewer does not independently prove WorldBody.apply happened;
that needs a separate physical replay (if commissioned).
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

SOURCE_RUN = 38760713470
SOURCE_SHA = "0d9fd7cd511640103498f037b84cae915169356e"
DIGESTS = {
    "a230z-physical-worlds.json":
        "09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d",
    "a230z-summary.json":
        "170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c",
}
STATE_KEYS = {
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
}
BODY_KEYS = {"energy","food","water","integrity"}
LAYOUTS = (
    "A_ONLY","B_LOCAL","B_EAST_BLOCKED",
    "B_EAST_ADJACENT","B_EAST_TWO_STEPS",
)
PROTOCOLS=("OBSERVED_ONLY","SINGLE_EAST_PROBE")
A_CAUSES={"benign","toxin_7","toxin_30","toxin_100","gain_zero"}
B_CAUSES={"benign","toxin_7","toxin_100","gain_zero"}
FOODS=(35.0,45.0)
POSITIONS=((5,5),(7,7))
PRIM={"direction":"east"}
B={"target":"berry_b"}
MOVE={"primitive":"se_deplacer","parameters":PRIM}
COLLECT={"primitive":"collecter","parameters":B}
EAT={"primitive":"manger","parameters":B}
EXPECT = {
    ("A_ONLY","OBSERVED_ONLY"):(20,0),
    ("A_ONLY","SINGLE_EAST_PROBE"):(20,20),
    ("B_LOCAL","OBSERVED_ONLY"):(16,32),
    ("B_LOCAL","SINGLE_EAST_PROBE"):(16,32),
    ("B_EAST_BLOCKED","OBSERVED_ONLY"):(16,0),
    ("B_EAST_BLOCKED","SINGLE_EAST_PROBE"):(16,0),
    ("B_EAST_ADJACENT","OBSERVED_ONLY"):(16,48),
    ("B_EAST_ADJACENT","SINGLE_EAST_PROBE"):(16,48),
    ("B_EAST_TWO_STEPS","OBSERVED_ONLY"):(16,0),
    ("B_EAST_TWO_STEPS","SINGLE_EAST_PROBE"):(16,64),
}


def hash_obj(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def read_sealed(root):
    result={}
    for filename,required in DIGESTS.items():
        hits=list(Path(root).rglob(filename))
        if len(hits)!=1:
            raise ValueError("ambiguous or missing sealed original: "+filename)
        raw=hits[0].read_bytes()
        if sha256(raw).hexdigest()!=required:
            raise ValueError("sealed original byte digest mismatch: "+filename)
        result[filename]=raw
    return result


def require_accessible(observation):
    if (type(observation) is not dict or set(observation)!=STATE_KEYS
        or type(observation["body"]) is not dict
        or set(observation["body"])!=BODY_KEYS
        or type(observation["adjacent"]) is not list
        or {n.get("direction") for n in observation["adjacent"]}
            != {"north","south","east","west"}):
        raise ValueError("hidden, future or incomplete first-person features")
    for n in observation["adjacent"]:
        if set(n)!={"direction","x","y","passable","water_source","resources","creature"}:
            raise ValueError("latent information in adjacent perceptual cell")


def independent_action(state,protocol,previous):
    """Written independently of the producer; consults NO lab cause labels."""
    require_accessible(state)
    if protocol not in PROTOCOLS:
        raise ValueError("unregistered policy")
    if EAT in previous:
        return None,"already_consumed_one_berry_b"
    if state["inventory"].get("berry_b",0)>0:
        return EAT,"held_berry_b_accessible"
    if "berry_b" in state["current_resources"]:
        return COLLECT,"local_berry_b_visible"
    east=next(x for x in state["adjacent"] if x["direction"]=="east")
    if "berry_b" in east["resources"]:
        return (MOVE,"eastern_berry_b_visible_passable") if east["passable"] else (
            None,"eastern_berry_b_visible_but_blocked"
        )
    if protocol=="SINGLE_EAST_PROBE" and not previous and east["passable"]:
        return MOVE,"one_blind_eastern_probe"
    return None,"no_visible_accessible_berry_b_abstain"


def observable_root_candidates(state):
    """Independent source-inspecting reimplementation of Stage6 candidates.

    All candidate exact SHA digests are calculated from accessible state
    and command dictionaries. No invocation of the actual planner here.
    """
    cmds=[]
    for n in state["adjacent"]:
        if n["passable"]:
            cmds.append({
                "primitive":"se_deplacer",
                "parameters":{"direction":n["direction"]},
            })
    for kind in set(state["current_resources"]):
        cmds.append({"primitive":"collecter","parameters":{"target":kind}})
    for fruit in ("berry_a","berry_b"):
        if state["inventory"].get(fruit,0)>0:
            cmds.append({"primitive":"manger","parameters":{"target":fruit}})
    if state["current_water_source"]:
        cmds.append({"primitive":"boire","parameters":{}})
    if state["inventory"].get("stone",0)>0:
        cmds.append({"primitive":"poser_une_pierre","parameters":{}})
    if state["inventory"].get("wood",0)>0 and state["inventory"].get("stone",0)>0:
        cmds.append({"primitive":"fabriquer_outil","parameters":{}})
    cmds += [
        {"primitive":"dormir","parameters":{}},
        {"primitive":"attendre","parameters":{}},
    ]
    return cmds


def _check_shadow(row,preingestion_idx):
    sh=row["stage6_shadow"]
    receipts=row["physical_steps_external"]
    if sh is None or receipts[preingestion_idx]["command"]!=EAT:
        raise ValueError("missing prospective Stage6 shadow on B ingestion")
    past=[r["physical_example"] for r in receipts[:preingestion_idx]]
    before=receipts[preingestion_idx]["state_before"]
    if not past or any(ex["terminal"] for ex in past):
        raise ValueError("Stage6 own history contains unexperienced future/death")
    if (sh["own_physical_examples"]!=past
        or sh["actual_own_history_step_count"]!=len(past)
        or sh["actual_own_history_step_indices"]!=list(
            range(1,preingestion_idx+1))
        or sh["input_first_person"]!=before
        or sh["input_first_person_sha256"]!=hash_obj(before)
        or sh["t_monde"]!=preingestion_idx+1
        or sh["model_kind"]!="own_prior_experience_only_exact_shadow"
        or sh["not_a_lived_I0_memory"] is not True
        or sh["oracle_fed_to_shadow"] is not False
        or sh["no_shadow_command_dispatched"] is not True
        or sh["true_I0_UC_used"] is not None
        or sh["r_eff"]!=1 or sh["max_depth"]!=3
        or abs(float(sh["target_food"])-(float(before["body"]["food"])+5.0))>1e-8):
        raise ValueError("Stage6 first-person timeline/model provenance contaminated")
    version=f"z-own-past-{row['world_id']}-t{preingestion_idx+1}"
    if sh["history_corpus_sha256"]!=hash_obj({
        "version":version,"examples":past
    }):
        raise ValueError("Stage6 physical history SHA altered")
    inputkeys={
        hash_obj({"state":x["state"],"command":x["command"]}) for x in past
    }
    candidates=observable_root_candidates(before)
    match_count=sum(
        hash_obj({"state":before,"command":c}) in inputkeys
        for c in candidates
    )
    diag=sh["stage6_diagnostic"]
    if (sh["stage6_root_candidate_edges"]!=len(candidates)
        or sh["stage6_root_available_edges"]!=match_count
        or sh["stage6_root_unavailable_edges"]!=len(candidates)-match_count
        or diag.get("root_candidate_edges")!=len(candidates)
        or diag.get("root_available_edges")!=match_count
        or diag.get("root_unavailable_edges")!=len(candidates)-match_count):
        raise ValueError("Stage6 exact root coverage falsified")
    if match_count==0:
        if (sh["stage6_status"]!="incomplete_model"
            or diag.get("status")!="incomplete_model"
            or diag.get("root_model_diagnostic")!="no_predictable_first_step"
            or sh["stage6_candidate_commands_only"]):
            raise ValueError("Stage6 invented food plan from unknown root")
    # No true UC ledger. This counts a *search invocation*, not UC consumed.
    return match_count


def independently_check_world(row):
    arm=row["layout_external_only"]
    mode=row["protocol_precommitted"]
    hidden=row["latent_berry_effect_external_only"]
    food=row["initial_food"]
    pos=tuple(row["initial_position"])
    if (arm not in LAYOUTS or mode not in PROTOCOLS
        or food not in FOODS or pos not in POSITIONS
        or hidden not in (A_CAUSES if arm=="A_ONLY" else B_CAUSES)):
        raise ValueError("physical source outside preregistered matrix")
    identifier=f"a230z:{arm}:{mode}:{hidden}:food{int(food)}:x{pos[0]}y{pos[1]}"
    if row["world_id"]!=identifier:
        raise ValueError("physical world identity/provenance mismatched")
    if not all(isinstance(row[x],str) and len(row[x])==64
               for x in ("config_sha256_external_only","layout_sha256_external_only")):
        raise ValueError("missing physical configuration provenance")
    if (row["no_oracle_information_in_policy"] is not True
        or row["no_stage6_shadow_action_dispatched"] is not True
        or row["no_i0_birth_or_autonomous_step"] is not True
        or row["actual_I0_UC_cost"] is not None
        or row["lived_postterminal_capture"] is not None
        or row["certifies_food_safety"] is not False):
        raise ValueError("false safety/I0 cognition or postmortem-as-lived claim")
    obs=row["initial_first_person"]
    require_accessible(obs)
    if (hash_obj(obs)!=row["initial_first_person_sha256"]
        or obs["x"]!=pos[0] or obs["y"]!=pos[1]
        or obs["body"]["food"]!=food):
        raise ValueError("false initially accessible body/sensory input")
    east=next(x for x in obs["adjacent"] if x["direction"]=="east")
    if "berry_a" not in obs["current_resources"]:
        raise ValueError("pre-registered visible A missing")
    if arm=="B_LOCAL" and "berry_b" not in obs["current_resources"]:
        raise ValueError("positive accessible local berry_b control missing")
    if arm=="B_EAST_ADJACENT" and (
        "berry_b" not in east["resources"] or not east["passable"]):
        raise ValueError("accessible adjacent berry_b positive cue absent")
    if arm=="B_EAST_BLOCKED" and (
        "berry_b" not in east["resources"] or east["passable"]):
        raise ValueError("blocked adjacent berry_b negative cue fabricated")
    if arm in ("A_ONLY","B_EAST_TWO_STEPS") and (
        "berry_b" in obs["current_resources"] or
        "berry_b" in east["resources"]):
        raise ValueError("remote or absent berry_b leaked into initial capture")

    receipts=row["physical_steps_external"]
    choices=row["perceptual_policy_choices"]
    lived=row["lived_states_while_alive"]
    if (not choices or not lived
        or row["physical_step_count"]!=len(receipts)
        or len(receipts)>4 or lived[0] != {"t_monde":1,"state":obs}):
        raise ValueError("invalid physical and first-person evidence lengths")
    if len(choices)!=(len(receipts) if receipts and receipts[-1][
        "terminal_external_only"] else len(receipts)+1):
        raise ValueError("postterminal or unrecorded policy choice")

    history=[]
    total_step_data=[]
    for idx, choice in enumerate(choices):
        tick=idx+1
        perceived=choice["input_accessible_state"]
        require_accessible(perceived)
        expected_before=obs if idx==0 else receipts[idx-1][
            "physical_after_external_only"]
        if (perceived!=expected_before or choice["t_monde"]!=tick
            or choice["input_sha256"]!=hash_obj(perceived)
            or choice["previous_actually_executed_commands"]!=history
            or choice["external_hidden_configuration_not_used"] is not True
            or choice["certifies_safe"] is not False):
            raise ValueError("future/latent information selected physical action")
        proposal, reason=independent_action(perceived,mode,history)
        if (choice["command"]!=proposal or
            choice["decision_reason_from_observation_only"]!=reason):
            raise ValueError("policy bypassed visible resource/blocked constraint")
        if idx>=len(receipts):
            if choice["command"] is not None:
                raise ValueError("unapplied physical action offered after stop")
            break
        rec=receipts[idx]
        ex=rec["physical_example"]
        if (rec["t_monde"]!=tick or rec["command"]!=proposal
            or rec["state_before"]!=perceived
            or rec["physical_after_external_only"]!=ex["observed_next_state"]
            or rec["terminal_external_only"] is not ex["terminal"]
            or ex["state"]!=perceived or ex["command"]!=proposal
            or ex["family"]!="a230z_physically_executed_alternative"
            or rec["physical_example_sha256"]!=hash_obj(ex)
            or rec["not_dispatched_by_shadow"] is not True):
            raise ValueError("physical transition receipt invalid")
        if rec["terminal_external_only"] and idx!=len(receipts)-1:
            raise ValueError("physical action after terminal transition")
        total_step_data.append(ex)
        history.append(proposal)
    survivor_steps=[
        {"t_monde":idx+2,"state":rec["physical_after_external_only"]}
        for idx,rec in enumerate(receipts)
        if not rec["terminal_external_only"]
    ]
    if lived!=[{"t_monde":1,"state":obs},*survivor_steps]:
        raise ValueError("subjective postmortem observation or lived chain falsified")
    last_terminal=(bool(receipts) and receipts[-1]["terminal_external_only"])
    terminal=len(receipts) if last_terminal else None
    if row["physical_terminal_step_external_only"]!=terminal:
        raise ValueError("external terminal chronology changed")
    eating=[i for i,x in enumerate(receipts) if x["command"]==EAT]
    if len(eating)>1:
        raise ValueError("repeated berry_b ingestion outside preregistration")
    ate=bool(eating)
    if ate!=row["ingested_berry_b_external"]:
        raise ValueError("unphysical ingestion label")
    if ate:
        index=eating[0]
        earlier=receipts[index]["state_before"]
        after=receipts[index]["physical_after_external_only"]
        if (row["pre_ingestion_lived_state"]!=earlier
            or row["post_ingestion_external_only"]!=after):
            raise ValueError("post-exposure outcome mislabeled first-person")
        shadow_root_known=_check_shadow(row,index)
        gain=float(after["body"]["food"])-float(earlier["body"]["food"])
        achieved=(terminal is None and gain>=5.0)
        insufficient=(terminal is None and not achieved)
    else:
        if (row["pre_ingestion_lived_state"] is not None
            or row["post_ingestion_external_only"] is not None
            or row["stage6_shadow"] is not None):
            raise ValueError("invented consumed food or shadow plan")
        shadow_root_known=None
        achieved=False
        insufficient=False
    if (row["food_success_with_survival_external"] is not achieved
        or row["insufficient_food_with_survival_external"] is not insufficient):
        raise ValueError("food achievement falsely attributed from physics")
    finalbody=(receipts[-1]["physical_after_external_only"]["body"]
               if receipts else obs["body"])
    measured={
        v:round(float(finalbody[v])-float(obs["body"][v]),8)
        for v in BODY_KEYS
    }
    if row["physical_body_delta_external"]!=measured:
        raise ValueError("physical resource cost was falsified")
    if ate and (
        (terminal is not None) != (hidden=="toxin_100") or
        achieved != (hidden in ("benign","toxin_7")) or
        insufficient != (hidden=="gain_zero")
    ):
        raise ValueError("source hidden B effect disagrees with physical result")

    preexposure_choice_inputs=[]
    for c in choices:
        preexposure_choice_inputs.append(c["input_accessible_state"])
        if c["command"]==EAT:
            break
    return {
        "id":identifier,"arm":arm,"policy":mode,"food":food,"position":pos,
        "hidden":hidden,"initial":obs,
        "preexposure_perceptual_history":preexposure_choice_inputs,
        "physical_steps":len(receipts),"ingested":ate,
        "terminal":terminal is not None,"food_success":achieved,
        "insufficient":insufficient,"shadow_root_known":shadow_root_known,
        "shadow_queried":shadow_root_known is not None,
        "delta":measured,
    }


def independent_reanalysis(worlds,source_summary):
    if (source_summary.get("schema")!="a230z-accessible-alternative-food-physical-v1"
        or source_summary.get("analysis_code_sha")!=SOURCE_SHA
        or source_summary.get("original_physical_worlds")!=168
        or source_summary.get("original_physical_actions")!=244
        or source_summary.get("new_living_I0_births")!=0
        or source_summary.get("oracle_to_i0_feedback") is not False
        or source_summary.get("food_safety_proven") is not False):
        raise ValueError("original preregistered Z source integrity mismatched")
    if len(worlds)!=168 or source_summary.get("world_data_sha256")!=hash_obj(worlds):
        raise ValueError("physical world count or checksum mismatched")
    verified=[]
    seen=set()
    for item in worlds:
        x=independently_check_world(item)
        if x["id"] in seen:
            raise ValueError("duplicated physical world")
        seen.add(x["id"])
        verified.append(x)
    per=defaultdict(Counter)
    for x in verified:
        v=per[(x["arm"],x["policy"])]
        v["worlds"]+=1
        v["physical_steps"]+=x["physical_steps"]
        v["ingestions"]+=x["ingested"]
        v["terminals"]+=x["terminal"]
        v["food_successes"]+=x["food_success"]
        v["insufficient"]+=x["insufficient"]
        v["abstained_from_food"]+=not x["ingested"]
    for name,expected in EXPECT.items():
        counts=per[name]
        if (counts["worlds"],counts["physical_steps"])!=expected:
            raise ValueError("physical science matrix not reproduced")

    alias=defaultdict(list)
    for x in verified:
        alias[(x["arm"],x["policy"],x["food"],x["position"])].append(x)
    if len(alias)!=40:
        raise ValueError("not 40 independently cross-checked hidden-context groups")
    risky_contexts=0
    for (arm,mode,food,pos),group in alias.items():
        expected=A_CAUSES if arm=="A_ONLY" else B_CAUSES
        if len(group)!=len(expected) or {x["hidden"] for x in group}!=expected:
            raise ValueError("latent physical branches were selectively omitted")
        if (any(x["initial"]!=group[0]["initial"] for x in group[1:])
            or any(x["preexposure_perceptual_history"]!=group[0][
                "preexposure_perceptual_history"] for x in group[1:])):
            raise ValueError("hidden causes changed the pre-exposure history")
        if arm!="A_ONLY" and group[0]["ingested"]:
            if (sum(x["terminal"] for x in group)!=1 or
                sum(x["food_success"] for x in group)!=2 or
                sum(x["insufficient"] for x in group)!=1):
                raise ValueError("risky alternative's hidden mortality suppressed")
            risky_contexts+=1
    remote_unseen=0
    remote_revealed=0
    for policy,food,pos in product(PROTOCOLS,FOODS,POSITIONS):
        old=alias[("A_ONLY",policy,food,pos)][0]
        distant=alias[("B_EAST_TWO_STEPS",policy,food,pos)][0]
        if old["initial"]!=distant["initial"]:
            raise ValueError("remote food known before exploration")
        remote_unseen+=1
        if policy=="SINGLE_EAST_PROBE":
            old_pre=old["preexposure_perceptual_history"]
            remote_pre=distant["preexposure_perceptual_history"]
            if (len(old_pre)<2 or len(remote_pre)<2
                or old_pre[1]==remote_pre[1]):
                raise ValueError("physically acquired distant-food cue absent")
            remote_revealed+=1
    observations={
        "worlds":len(verified),
        "physical_steps":sum(x["physical_steps"] for x in verified),
        "ingestions":sum(x["ingested"] for x in verified),
        "terminals":sum(x["terminal"] for x in verified),
        "success":sum(x["food_success"] for x in verified),
        "insufficient":sum(x["insufficient"] for x in verified),
        "no_ingestion":sum(not x["ingested"] for x in verified),
        "shadow_queries":sum(x["shadow_queried"] for x in verified),
        "shadow_roots_with_first_known_step":sum(
            x["shadow_root_known"]>0 for x in verified if x["shadow_queried"]
        ),
    }
    expected_obs={
        "worlds":168,"physical_steps":244,"ingestions":80,"terminals":20,
        "success":40,"insufficient":20,"no_ingestion":88,
        "shadow_queries":80,"shadow_roots_with_first_known_step":0,
    }
    if observations!=expected_obs:
        raise ValueError("independent world/action/success/root counters changed")
    compare={
        "original_physical_worlds":observations["worlds"],
        "original_physical_actions":observations["physical_steps"],
        "ingestions_of_berry_b":observations["ingestions"],
        "terminal_physical_ingestions":observations["terminals"],
        "surviving_food_gain_at_least_5":observations["success"],
        "surviving_food_gain_insufficient":observations["insufficient"],
        "abstentions_from_berry_b_ingestion":observations["no_ingestion"],
        "shadow_queries_actual_Stage6_algorithm":observations["shadow_queries"],
        "known_alternative_with_hidden_lethal_possibility_groups":risky_contexts,
        "unique_initial_firstperson_hidden_groups":len(alias),
        "remote_B_truly_unseen_initial_paired_groups":remote_unseen,
    }
    for name,value in compare.items():
        if source_summary.get(name)!=value:
            raise ValueError("original Z aggregate was incorrectly scored: "+name)
    actual_per={
        f"{arm}/{mode}":dict(counter) for (arm,mode),counter in sorted(per.items())
    }
    if source_summary.get("per_arm")!=actual_per:
        raise ValueError("independent physical arms do not match original score")
    return {
        "schema":"a230zi-independent-archived-firstperson-v1",
        "source_original_run":SOURCE_RUN,"original_source_code":SOURCE_SHA,
        "original_detached_worlds_checked":168,
        "original_physical_receipts_checked":244,
        "original_B_ingestions_recomputed":80,
        "original_physical_terminals_recomputed":20,
        "surviving_food_goals_recomputed":40,
        "surviving_insufficient_goals_recomputed":20,
        "original_no_ingestions":88,
        "latent_group_count":40,
        "risk_ambiguous_success_vs_death_groups":risky_contexts,
        "initially_unseen_remote_resource_pair_groups":remote_unseen,
        "remotely_discovered_by_actual_scout_pair_groups":remote_revealed,
        "actual_stage6_algorithm_shadow_searches_checked":80,
        "zero_known_first_edges_independently_recomputed":80,
        "new_worlds":0,"new_physical_steps":0,"new_i0_births":0,
        "source_physics_independently_proven_from_json":False,
        "stage6_production_plan_success_proven":False,
        "safe_food_option_certified":False,
        "lab_physical_food_feasibility_witnessed":True,
        "true_i0_uc_cost_evaluated":False,
        "oracle_injected_into_cognition":False,
        "stage12":"PARTIAL","issue110":"OPEN",
        "per_arm":actual_per,
    }


def run(source_a:Path,source_b:Path,output:Path):
    files_a=read_sealed(source_a)
    files_b=read_sealed(source_b)
    if files_a!=files_b:
        raise ValueError("original 3.11 and 3.12 scientific JSON differ")
    cert=independent_reanalysis(
        json.loads(files_a["a230z-physical-worlds.json"]),
        json.loads(files_a["a230z-summary.json"]),
    )
    cert.update({
        "source_json_sha256":DIGESTS,
        "original_python_311_312_outputs_equal_bytes":True,
        "analysis_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230zi-independent-certificate.json").write_text(
        json.dumps(cert,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZI_SUMMARY "+json.dumps({
        k:v for k,v in cert.items() if k not in (
            "source_json_sha256","per_arm"
        )
    },sort_keys=True),flush=True)
    return cert


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-311",required=True,type=Path)
    ap.add_argument("--source-312",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    args=ap.parse_args()
    run(args.source_311,args.source_312,args.output_dir)


if __name__=="__main__":
    main()
