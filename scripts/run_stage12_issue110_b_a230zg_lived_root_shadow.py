"""A2.30-ZG: real I0 birth-root matched Stage6 shadow model-coverage ablation.

PREREGISTERED before code at 533a2afac13d6dd4228a3f0ddbd635413ce6b808.
Source: original 12 autonomous ZB births (run 38767643472), read-only.
Six NEW standalone physical DEMONSTRATION worlds, exactly fourteen real
WorldBody.apply transitions, NONE involving berry_b ingestion. No new
Stage12 I0 birth, no autonomous I0 step, no Oracle/Bench feedback.
24 genuinely executed Stage6 SEARCHES are shadow and never dispatch actions.

The B demonstrators are other laboratory worlds, NOT I0's own memory.
Never interpret a predicted substep as a safe meal or agency judgement.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any

from i0.equipment import (
    EquipmentCorpus, FrozenTableEquipment, SimulationNeighbor,
    SimulationState, train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout

ORIGINAL_RUN = 38767643472
ORIGINAL_SOURCE_SHA = "2a19742df22f27752635203304097134a3009c45"
ORIGINAL_SUMMARY_HASHES = {
    "3.11": "ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b",
    "3.12": "ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362",
}
PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST")
HIDDEN_VARIANTS=("benign","toxic_lethal")
SOURCE_TRAIN_WORLDS=6
SOURCE_A_STEPS=8
SOURCE_B_STEPS=6
PHYSICAL_STEPS=14
HISTORICAL_BIRTHS=12
SHADOW_SEARCHES=24
MOVE_N=PrimitiveCommand("se_deplacer",{"direction":"north"})
MOVE_E=PrimitiveCommand("se_deplacer",{"direction":"east"})
COLLECT_A=PrimitiveCommand("collecter",{"target":"berry_a"})
EAT_A=PrimitiveCommand("manger",{"target":"berry_a"})
COLLECT_B=PrimitiveCommand("collecter",{"target":"berry_b"})
EAT_B=PrimitiveCommand("manger",{"target":"berry_b"})
VALID_ACCESSIBLE={
    "schema_version","x","y","body","inventory","current_water_source",
    "current_resources","adjacent","known_shelter_here","is_night",
}


def digest(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def first_person(world,t=1):
    capture=SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    state=state_from_capture(capture=capture,is_night=world.is_night(t))
    state.validate()
    return state


def decode_state(value):
    if type(value) is not dict or set(value)!=VALID_ACCESSIBLE:
        raise ValueError("hidden/future or missing first-person state feature")
    s=SimulationState(
        schema_version=value["schema_version"],x=value["x"],y=value["y"],
        body=value["body"],inventory=value["inventory"],
        current_water_source=value["current_water_source"],
        current_resources=tuple(value["current_resources"]),
        adjacent=tuple(SimulationNeighbor(
            direction=n["direction"],x=n["x"],y=n["y"],
            passable=n["passable"],water_source=n["water_source"],
            resources=tuple(n["resources"]),creature=n["creature"],
        ) for n in value["adjacent"]),
        known_shelter_here=value["known_shelter_here"],
        is_night=value["is_night"],
    )
    if s.as_dict()!=value:
        raise ValueError("accessible historical input is not canonical")
    return s


def read_original_summary(path, interpreter):
    if interpreter not in ORIGINAL_SUMMARY_HASHES:
        raise ValueError("original version is not preregistered")
    files=list(Path(path).rglob("a230zb-summary.json"))
    if len(files)!=1:
        raise ValueError("original archived summary absent or ambiguous")
    raw=files[0].read_bytes()
    if sha256(raw).hexdigest()!=ORIGINAL_SUMMARY_HASHES[interpreter]:
        raise ValueError("original historical ZB source JSON SHA mismatch")
    j=json.loads(raw)
    if (j.get("schema")!="a230zb-autonomous-alternative-lived-v1"
        or j.get("git_sha")!=ORIGINAL_SOURCE_SHA
        or j.get("independent_new_I0_births")!=HISTORICAL_BIRTHS
        or j.get("actual_autonomous_world_steps")!=384
        or j.get("B_collections_executed")!=0
        or j.get("B_ingestions_physically_confirmed")!=0
        or len(j.get("lives",()))!=12):
        raise ValueError("not original sealed autonomous birth cohort")
    return j


def verify_original_birth_sources(a,b):
    """Pythons differ in internal ULP receipts; root/birth must still agree."""
    l,r=read_original_summary(a,"3.11"),read_original_summary(b,"3.12")
    by_311={x["birth_id"]:x for x in l["lives"]}
    by_312={x["birth_id"]:x for x in r["lives"]}
    if len(by_311)!=12 or set(by_311)!=set(by_312):
        raise ValueError("autonomous birth identifiers are missing or duplicated")
    for identity,life in by_311.items():
        other=by_312[identity]
        for key in (
            "initial_accessible_projection","equipment_sha256_A_only",
            "profile","layout","hidden_B_external_only","world_steps",
            "mortal_status","executed_motor_commands",
        ):
            if life[key]!=other[key]:
                raise ValueError(
                    "original interpreters disagree about first-person evidence: "
                    + identity + ":" + key
                )
        if (life["world_steps"]!=32
            or life["mortal_status"]!="experiment_stopped"
            or life["experienced_B_commands_with_motives"]
            or life["confirmed_B_ingestions"]
            or not life["independent_WAL_P48_dual_agency_audits"]):
            raise ValueError("historical life source is unsupported")
        decode_state(life["initial_accessible_projection"])
    return [by_311[k] for k in sorted(by_311)]


def reference_birth_world(profile):
    """Rebuild only the PHYSICAL original fixture; no Stage12 I0 is born."""
    if profile not in PROFILES:
        raise ValueError("unknown historical profile")
    s11=build_stage11_reference_runtime(
        enable_geography=True,autonomous_mortal=True,
    )
    ref=s11.world.config
    config=replace(
        ref,version="stage12-issue110-food-world-v1",
        initial_body=replace(ref.initial_body,water=70.0,food=35.0),
        berry_effects={
            **ref.berry_effects,
            "berry_a":replace(
                ref.berry_effects["berry_a"],
                food_gain=30.0,integrity_delta=0.0,
            ),
        },
    )
    at=Position(3,1)
    layout=replace(
        s11.world._layout,
        water_sources=frozenset({Position(2,2)}),
        resources=((at,"berry_a",2),),
        obstacles=frozenset(),
    )
    settings={
        "restored":(35.0,30.0,0.0,12),
        "sustained":(24.0,6.0,0.7,12),
    }
    initial_food,gain,decay,n=settings[profile]
    config=replace(
        config,
        version=config.version+"-calibration-"+profile+"-v1",
        initial_body=replace(config.initial_body,food=initial_food),
        food_decay_per_step=decay,
        berry_effects={
            **config.berry_effects,
            "berry_a":replace(
                config.berry_effects["berry_a"],food_gain=gain,
            ),
        },
    )
    layout=replace(layout,resources=((at,"berry_a",n),))
    config.validate()
    layout.validate(config)
    return config,layout


def benign_B_fixture(config,layout,which):
    """Only worlds used to OBSERVE NONINGESTIVE B transitions are benign."""
    if which not in ("B_LOCAL","B_EAST"):
        raise ValueError("unknown preregistered B demonstrator")
    if any(name=="berry_b" for _,name,_ in layout.resources):
        raise AssertionError("original A source already contains B")
    effect=replace(
        config.berry_effects["berry_b"],
        food_gain=30.0,integrity_delta=0.0,
    )
    changed_config=replace(
        config,version=config.version+"-a230zb-benign-v1",
        berry_effects={**config.berry_effects,"berry_b":effect},
    )
    pos=(config.initial_position if which=="B_LOCAL" else
         config.initial_position.moved("east"))
    changed_layout=replace(
        layout,
        resources=tuple(layout.resources)+((pos,"berry_b",2),),
    )
    changed_config.validate()
    changed_layout.validate(changed_config)
    return changed_config,changed_layout


def physically_demonstrate(*,name,config,layout,commands,
                           corpus_version):
    """Real detached physics, never a cognitive demonstration injected into I0."""
    world=WorldBody(config=config,layout=layout)
    recorder=EquipmentCorpusRecorder(corpus_version=corpus_version)
    root=first_person(world,1)
    examples=[]
    for time,command in enumerate(commands,1):
        now=first_person(world,time)
        if command==COLLECT_B and "berry_b" not in now.current_resources:
            raise AssertionError("collect(B) physical source lacks visible B")
        if command==MOVE_E and not next(
            v for v in now.adjacent if v.direction=="east"
        ).passable:
            raise AssertionError("physically demonstrated movement into obstacle")
        if command==EAT_B or (command.primitive=="manger" and
                            command!=EAT_A):
            raise AssertionError("B ingestion is prohibited in ZG corpus")
        example=recorder.record_transition(
            world=world,t_monde=time,
            family=("movement_free" if command in (MOVE_N,MOVE_E)
                    and name.startswith("A_REFERENCE") else
                    "collection_without_tool" if command==COLLECT_A else
                    "resource_consumption" if command==EAT_A else
                    "a230zg_B_non_ingestive_"+command.primitive),
            command=command,
        )
        if example.state!=now:
            raise AssertionError("sensor and physical recorder do not agree")
        if example.terminal:
            raise AssertionError("physical demonstrator became terminal")
        examples.append(example)
    if any(e.command==EAT_B for e in examples):
        raise AssertionError("B ingestion slipped into corpus")
    return {
        "source_world_id":name,
        "root_first_person":root.as_dict(),
        "physics_config_sha256_external_only":config.digest(),
        "physics_layout_sha256_external_only":digest(layout.as_dict()),
        "physical_step_count":len(examples),
        "physical_examples":[e.as_dict() for e in examples],
        "physical_example_sha256":[digest(e.as_dict()) for e in examples],
        "all_actions_physical_nonterminal":True,
        "not_an_I0_birth":True,
        "no_B_ingestion":True,
    },tuple(examples)


def build_frozen_profiles():
    """Build all SIX physical demonstrators and freeze FOUR exact tables."""
    sources=[]
    models={}
    source_roots={}
    for profile in PROFILES:
        config,layout=reference_birth_world(profile)
        a_source,a_examples=physically_demonstrate(
            name=f"A_REFERENCE-{profile}",config=config,layout=layout,
            commands=(MOVE_N,MOVE_E,COLLECT_A,EAT_A),
            corpus_version="issue110-lived-north-east-food-physical-v1",
        )
        sources.append(a_source)
        a_corpus=EquipmentCorpus(
            version="issue110-lived-north-east-food-physical-v1",
            examples=a_examples,
        )
        a_model=train_exact_transition_table(
            corpus=a_corpus,
            equipment_version="E-stage12-issue110-lived-state-food-physical-v1",
        )
        b_examples=[]
        for which in ("B_LOCAL","B_EAST"):
            b_config,b_layout=benign_B_fixture(config,layout,which)
            commands=((COLLECT_B,) if which=="B_LOCAL"
                      else (MOVE_E,COLLECT_B))
            demo,records=physically_demonstrate(
                name=f"B_DEMONSTRATOR-{profile}-{which}",
                config=b_config,layout=b_layout,commands=commands,
                corpus_version=f"a230zg-B-{profile}-{which}-v1",
            )
            sources.append(demo)
            b_examples.extend(records)
            source_roots[(profile,which)]=demo["root_first_person"]
        if len(a_examples)!=4 or len(b_examples)!=3:
            raise AssertionError("frozen original A and new B corpora not as registered")
        expanded=EquipmentCorpus(
            version=f"a230zg-physical-A+B-{profile}-v1",
            examples=tuple(a_examples)+tuple(b_examples),
        )
        enriched=train_exact_transition_table(
            corpus=expanded,
            equipment_version=f"E-a230zg-shadow-noningestive-{profile}-v1",
        )
        for source in b_examples:
            if source.command.primitive=="manger":
                raise AssertionError("model got a B ingestion training example")
        models[profile]=(a_model,enriched)
    if len(sources)!=SOURCE_TRAIN_WORLDS or sum(
        item["physical_step_count"] for item in sources
    )!=PHYSICAL_STEPS or sum(
        item["physical_step_count"] for item in sources
        if item["source_world_id"].startswith("B_DEMONSTRATOR")
    )!=SOURCE_B_STEPS:
        raise AssertionError("source physical cohort deviated from preregistration")
    return sources,models,source_roots


def stage6_shadow(state,equipment,tag):
    """Same search implementation as production; no result ever dispatched."""
    target=float(state.body["food"])+5.0
    simulator=Simulator(
        config=SimulatorConfig(
            version="stage12-a230zg-readonly-h3-r1-v1",
            h_max=3,r_max=1,
        ),
        equipment=equipment,
    )
    planner=SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="stage12-a230zg-readonly-firstperson-v1",
            option_ttl_steps=5,max_depth=3,revision_delta=0.0,
            setpoints={
                "energy":65.0,"food":target,
                "water":65.0,"integrity":65.0,
            },
            progressive_subgoals=True,
            progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
        ),
        simulator=simulator,
    )
    result=planner.search(
        initial_state=state,
        target=lambda s:float(s.body["food"])>=target,
        progress_measure="food",
    )
    diagnostics=planner.last_search_diagnostic
    if diagnostics is None:
        raise AssertionError("real planner returned no root diagnostics")
    if result.root_candidate_edges!=len(
        SimulatorPlanner.candidate_commands(state)
    ):
        raise AssertionError("planner root candidates disagree with accessible state")
    if any(p.command.primitive=="manger" and
           p.command.parameters.get("target")=="berry_b"
           for p in result.predictions):
        raise AssertionError("model claimed unobserved berry B ingestion")
    return {
        "arm":tag,
        "status":result.status,
        "commands":[c.as_dict() for c in result.commands],
        "predicted_commands":[p.command.as_dict() for p in result.predictions],
        "partial_progress":result.partial_progress,
        "root_candidate_edges":result.root_candidate_edges,
        "root_available_edges":result.root_available_edges,
        "root_unavailable_edges":result.root_unavailable_edges,
        "unavailable_edges_total":result.unavailable_edges,
        "expanded_states":result.expanded_states,
        "last_search_diagnostic":diagnostics,
        "target_food":target,
        "no_shadow_action_dispatched":True,
        "berry_b_safety_certified":False,
        "actual_i0_uc_measured":False,
    }


def score_root(life,models,source_roots):
    """Test root comes ONLY from archive; no physical act in original life."""
    profile=life["profile"]
    layout=life["layout"]
    hidden=life["hidden_B_external_only"]
    if (profile not in PROFILES or layout not in LAYOUTS
        or hidden not in HIDDEN_VARIANTS):
        raise ValueError("original birth factor cell unknown")
    state=decode_state(life["initial_accessible_projection"])
    if state.x!=2 or state.y!=2:
        raise AssertionError("unexpected archived real-birth geometry")
    if float(state.body["food"])!={
        "restored":35.0,"sustained":24.0,
    }[profile]:
        raise AssertionError("wrong archived first-person profile food")
    local=("berry_b" in state.current_resources)
    east=next(n for n in state.adjacent if n.direction=="east")
    if (
        local!=(layout=="B_LOCAL")
        or ("berry_b" in east.resources)!=(layout=="B_EAST")
        or (layout=="B_EAST" and not east.passable)
    ):
        raise ValueError("fake berry B perceptual availability")
    command=(COLLECT_B if layout=="B_LOCAL" else
             MOVE_E if layout=="B_EAST" else None)
    candidates=SimulatorPlanner.candidate_commands(state)
    if (command is not None and command not in candidates
        or layout=="B_NONE" and COLLECT_B in candidates):
        raise AssertionError("eligible first B step not derived from true sensation")
    if layout!="B_NONE" and (
        state.as_dict()!=source_roots[(profile,layout)]
    ):
        raise AssertionError("DETACHED physical source does not match actual I0 birth")
    baseline,enriched=models[profile]
    if baseline.artifact_digest!=life["equipment_sha256_A_only"]:
        raise AssertionError("reconstructed physical A model differs from I0 birth")
    if any(p["primitive"]=="manger" and p["parameters"].get("target")=="berry_b"
           for p in (c.as_dict() for c in candidates)):
        raise AssertionError("I0 born holding a fabricated berry B")
    b_root_old=None
    b_root_new=None
    first_effect=None
    if command is not None:
        try:
            baseline.predict(state=state,command=command)
        except LookupError:
            b_root_old=False
        else:
            b_root_old=True
        try:
            p=enriched.predict(state=state,command=command)
        except LookupError:
            b_root_new=False
        else:
            b_root_new=True
            if p.terminal or p.command.primitive=="manger":
                raise AssertionError("shadow physical B noningestive transition is unsafe")
            first_effect=p.next_state.as_dict()
        if b_root_old or not b_root_new:
            raise AssertionError("real root did not acquire exact physical B first edge")
    else:
        try:
            enriched.predict(state=state,command=COLLECT_B)
        except LookupError:
            pass
        else:
            raise AssertionError("model predicts nonexistent B in absent resource cell")
    first=stage6_shadow(state,baseline,"A_ONLY")
    second=stage6_shadow(state,enriched,"A_PLUS_B_NON_INGESTIVE")
    return {
        "original_birth_id":life["birth_id"],
        "profile":profile,
        "layout":layout,
        "hidden_effect_for_external_stratification_only":hidden,
        "historical_world_steps_no_new_actions":life["world_steps"],
        "first_person_root_state":state.as_dict(),
        "first_person_sha256":digest(state.as_dict()),
        "external_physical_source_world_id":(
            f"B_DEMONSTRATOR-{profile}-{layout}"
            if layout!="B_NONE" else None
        ),
        "eligible_B_first_step":None if command is None else command.as_dict(),
        "eligible_B_first_step_in_candidate_commands":command in candidates
           if command is not None else False,
        "B_first_step_known_in_historical_A":b_root_old,
        "B_first_step_known_in_augmented_shadow":b_root_new,
        "physically_witnessed_B_first_step_next_state":first_effect,
        "A_only_equipment_sha256":baseline.artifact_digest,
        "augmented_exact_equipment_sha256":enriched.artifact_digest,
        "baseline_stage6":first,
        "enriched_stage6":second,
        "training_transition_from_other_world_not_lived_by_i0":True,
        "stage6_prediction_not_actually_dispatched":True,
        "no_lived_uc_or_agency_implied":True,
        "B_ingestion_safety_proven":False,
    }


def verify_result(rows):
    if len(rows)!=HISTORICAL_BIRTHS or len({
        row["original_birth_id"] for row in rows
    })!=HISTORICAL_BIRTHS:
        raise AssertionError("not 12 independent archived subjects")
    indexed={(x["profile"],x["layout"],x[
        "hidden_effect_for_external_stratification_only"]):x
        for x in rows}
    if len(indexed)!=12:
        raise ValueError("not full preregistered 2×3×2 factors")
    for p in PROFILES:
        for layout in LAYOUTS:
            a=indexed[(p,layout,"benign")]
            b=indexed[(p,layout,"toxic_lethal")]
            for key in (
                "first_person_root_state","first_person_sha256",
                "eligible_B_first_step","A_only_equipment_sha256",
                "augmented_exact_equipment_sha256",
                "baseline_stage6","enriched_stage6",
            ):
                if a[key]!=b[key]:
                    raise ValueError(
                        "hidden hazard changed prospective physical shadow: "+key
                    )
    if any(x["B_ingestion_safety_proven"] for x in rows):
        raise AssertionError("false safety claim")
    return {
        "historical_I0_birth_roots_scored":12,
        "original_ZB_autonomous_steps_reused_read_only":384,
        "new_autonomous_I0_births":0,
        "new_autonomous_I0_steps":0,
        "original_roots_B_visible":sum(x["layout"]!="B_NONE" for x in rows),
        "exact_B_demonstrations_match_visible_roots":sum(
            x["B_first_step_known_in_augmented_shadow"] is True for x in rows
        ),
        "historical_A_B_root_unknown":sum(
            x["B_first_step_known_in_historical_A"] is False for x in rows
        ),
        "actual_shadow_searches":len(rows)*2,
        "baseline_root_known_count":sum(
            x["baseline_stage6"]["root_available_edges"]>0 for x in rows
        ),
        "enriched_root_known_count":sum(
            x["enriched_stage6"]["root_available_edges"]>0 for x in rows
        ),
        "baseline_statuses":dict(Counter(
            x["baseline_stage6"]["status"] for x in rows
        )),
        "enriched_statuses":dict(Counter(
            x["enriched_stage6"]["status"] for x in rows
        )),
        "B_visible_partial_progress":sum(
            x["layout"]!="B_NONE" and
            x["enriched_stage6"]["status"]=="partial_progress"
            for x in rows
        ),
        "B_first_action_selected_in_shadow":sum(
            x["layout"]!="B_NONE" and
            bool(x["enriched_stage6"]["commands"]) and
            x["enriched_stage6"]["commands"][0]==x[
                "eligible_B_first_step"]
            for x in rows
        ),
        "model_predicted_B_ingestion_count":sum(
            any(c.get("primitive")=="manger" and
                c.get("parameters",{}).get("target")=="berry_b"
                for c in x["enriched_stage6"]["predicted_commands"])
            for x in rows
        ),
        "hidden_effect_parity_pairs":6,
        "actual_I0_UC_in_shadow":None,
        "actual_I0_berry_B_food_gain_proven":False,
        "actual_I0_berry_B_food_safety_proven":False,
        "model_was_installed_in_real_I0":False,
        "stage12":"PARTIAL","issue110":"OPEN",
    }


def experiment(output_dir,source_311,source_312):
    output_dir.mkdir(parents=True,exist_ok=False)
    source_worlds,models,source_roots=build_frozen_profiles()
    if len(source_worlds)!=6 or sum(
        w["physical_step_count"] for w in source_worlds
    )!=14:
        raise AssertionError("prespecified physical sources missing")
    # The original already-born ZB lives remain READ-ONLY. Source worlds were
    # physically completed and model frozen BEFORE any shadow search.
    lives=verify_original_birth_sources(source_311,source_312)
    rows=[score_root(life,models,source_roots) for life in lives]
    stats=verify_result(rows)
    manifest={
        "schema":"a230zg-separate-detached-physical-training-v1",
        "original_ZB_run":ORIGINAL_RUN,
        "original_ZB_source_SHA":ORIGINAL_SOURCE_SHA,
        "original_source_summary_sha256":ORIGINAL_SUMMARY_HASHES,
        "physical_demo_worlds":len(source_worlds),
        "real_physical_demonstration_steps":14,
        "A_reference_physical_steps":8,
        "B_non_ingestive_physical_steps":6,
        "separate_original_births_read_only":12,
        "all_physical_demonstrations":source_worlds,
        "original_A_model_sha256_by_profile":{
            p:models[p][0].artifact_digest for p in PROFILES
        },
        "augmented_shadow_model_sha256_by_profile":{
            p:models[p][1].artifact_digest for p in PROFILES
        },
        "demo_hashes_are_external_not_cognitive":True,
        "model_trained_before_test_root_queries":True,
        "no_ingestion_B_demonstrated":True,
    }
    (output_dir/"a230zg-physical-demonstrations.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",
    )
    (output_dir/"a230zg-lived-birth-shadow.json").write_text(
        json.dumps(rows,indent=2,sort_keys=True)+"\n",
    )
    report={
        **stats,
        "schema":"a230zg-firstperson-lived-root-exact-model-shadow-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "separate_detached_physical_worlds":len(source_worlds),
        "physical_A_reference_actions":8,
        "physical_B_non_ingestive_actions":6,
        "total_new_physical_training_steps":14,
        "original_B_exposure_or_danger_learned":False,
        "no_act_executed_from_shadow":True,
        "laboratory_only_nonlived_model_addition":True,
        "normative_spec_or_runtime_modified":False,
        "all_evidence_individually_provenanced":True,
        "original_source_run":ORIGINAL_RUN,
        "artifact_sha256":{
            "physical_demonstration_corpus":digest(source_worlds),
            "twelve_lived_birth_shadow":digest(rows),
        },
    }
    (output_dir/"a230zg-summary.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",
    )
    print("A230ZG_SUMMARY "+json.dumps({
        key:value for key,value in report.items() if key!="artifact_sha256"
    },sort_keys=True),flush=True)
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-zb-311",type=Path,required=True)
    ap.add_argument("--original-zb-312",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    experiment(args.output_dir,args.original_zb_311,args.original_zb_312)


if __name__=="__main__":
    main()
