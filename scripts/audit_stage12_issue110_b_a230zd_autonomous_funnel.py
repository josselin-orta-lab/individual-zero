"""A2.30-ZD: independent read-only attrition and determinism audit of ZB WAL.

Preregistered *after* known ZB outcomes and *before this auditor*, at
c64a01acb396152534f8592229c880788a05d586.

NO new I0 life, no physics, no Oracle, no Stage6 search, no prescribed motor
command. Reads only the twelve unaltered historical ZB worlds and their two
original Python-version artifacts. False-safe extrapolation is prohibited.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i0.equipment import SimulationNeighbor, SimulationState
from i0.interfaces import PrimitiveCommand
from i0.modules.stage6_planning import SimulatorPlanner
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

HISTORICAL_RUN = 38767643472
HISTORICAL_SHA = "2a19742df22f27752635203304097134a3009c45"
ORIGINAL_SUMMARY_BYTES_SHA256 = {
    "3.11": "ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b",
    "3.12": "ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362",
}
PROFILES = ("restored", "sustained")
LAYOUTS = ("B_NONE", "B_LOCAL", "B_EAST")
VARIANTS = ("benign", "toxic_lethal")
STEPS_PER_LIFE = 32
SEARCH_STATUSES = frozenset({
    "plan_found", "partial_progress",
    "incomplete_model", "not_found_within_horizon",
})
ALLOWED_CROSS_PY_NUMERICAL_EVENT_KINDS = frozenset({
    "stage8_option_evaluation", "competition_cycle", "td_update_published",
})
PERCEPTIBLE_ROOT_KEYS = frozenset({
    "schema_version", "x", "y", "body", "inventory", "current_resources",
    "current_water_source", "adjacent", "known_shelter_here", "is_night",
})


def hexfloat(value):
    if type(value) is dict and set(value) == {"$f64"}:
        return float.fromhex(value["$f64"])
    if type(value) in (int, float):
        return float(value)
    raise ValueError("unexpected physical/learned number schema")


def candidate_root(state_dict, layout):
    """Evaluate *candidate eligibility*, not model prediction or priority."""
    if type(state_dict) is not dict or set(state_dict) != PERCEPTIBLE_ROOT_KEYS:
        raise ValueError("initial sensory root contains hidden or omitted fields")
    if set(state_dict["body"]) != {"energy","food","water","integrity"}:
        raise ValueError("incomplete accessible bodily input")
    fields = tuple(SimulationNeighbor(
        direction=n["direction"], x=n["x"], y=n["y"],
        passable=n["passable"], water_source=n["water_source"],
        resources=tuple(n["resources"]), creature=n["creature"],
    ) for n in state_dict["adjacent"])
    obj = SimulationState(
        schema_version=state_dict["schema_version"],
        x=state_dict["x"], y=state_dict["y"],
        body=state_dict["body"], inventory=state_dict["inventory"],
        current_water_source=state_dict["current_water_source"],
        current_resources=tuple(state_dict["current_resources"]),
        adjacent=fields, known_shelter_here=state_dict["known_shelter_here"],
        is_night=state_dict["is_night"],
    )
    if obj.as_dict() != state_dict:
        raise ValueError("accessible state not canonically reconstructible")
    east = next((n for n in fields if n.direction=="east"), None)
    if east is None:
        raise ValueError("unobservable eastern neighbor")
    local = "berry_b" in obj.current_resources
    nextdoor = "berry_b" in east.resources
    if (
        (layout=="B_LOCAL" and (not local or nextdoor))
        or (layout=="B_EAST" and (local or not nextdoor or not east.passable))
        or (layout=="B_NONE" and (local or nextdoor))
    ):
        raise ValueError("hidden fruit placement leaked or omitted at initial capture")
    candidates = SimulatorPlanner.candidate_commands(obj)
    gather_b = PrimitiveCommand("collecter",{"target":"berry_b"})
    eat_b = PrimitiveCommand("manger",{"target":"berry_b"})
    move_east = PrimitiveCommand("se_deplacer",{"direction":"east"})
    if (gather_b in candidates) != (layout=="B_LOCAL"):
        raise ValueError("candidate enumeration contradicts first-person berries")
    if eat_b in candidates:
        raise ValueError("prebirth B inventory was fabricated")
    if layout=="B_EAST" and move_east not in candidates:
        raise ValueError("east is physically perceived but not a candidate")
    return {
        "local_B_accessible":local,
        "adjacent_east_B_accessible":bool(nextdoor and east.passable),
        "candidate_collect_B_initial":gather_b in candidates,
        "candidate_eat_B_initial":eat_b in candidates,
        "candidate_east_move_initial":move_east in candidates,
        "candidate_count":len(candidates),
        "model_predictability_of_B_from_candidate_alone":"not_established",
    }


def by_step(events, steps):
    result=defaultdict(list)
    for e in events:
        t=e.get("t_monde")
        if type(t) is int and t>=1:
            if t>steps and e.get("kind") in (
                "command_experienced","world_transition_experienced",
                "perceptual_capture",
            ):
                raise ValueError("out-of-horizon subjectively experienced action/capture")
            result[t].append(e)
    return result


def classify_step(rows, time):
    """Mutually exclusive *evidence* gates. Does NOT assert B intentionality.

    If a generic food proposal lacks its constituent target, no target is
    inferred. Only an actual executed B command can attest B motor output.
    """
    events=defaultdict(list)
    for event in rows: events[event["kind"]].append(event)
    cmd=events["command_experienced"]
    transition=events["world_transition_experienced"]
    if len(cmd)!=1 or len(transition)!=1:
        raise ValueError("one committed command AND physical step required")
    if cmd[0]["attempt_ref"]!=transition[0]["attempt_ref"]:
        raise ValueError("physical command and world consequence unjoined")
    if cmd[0]["t_monde"]!=time or transition[0]["t_monde"]!=time:
        raise ValueError("misordered physical command chronology")
    primitive=cmd[0]["primitive"]
    parameters=cmd[0].get("parameters",{})
    is_B = primitive in ("collecter","manger") and parameters.get("target")=="berry_b"
    receipt=transition[0].get("effects",{})
    physical_B_eat=receipt.get("ate")=="berry_b"
    if physical_B_eat and (not is_B or primitive!="manger"):
        raise ValueError("oracular/fabricated berry B consequence without motor command")
    if is_B and primitive=="manger" and not physical_B_eat:
        # A failed attempt is NOT a successful ingestion.
        if receipt.get("ate") not in ("unavailable", None):
            raise ValueError("B ingestion attempt cannot produce other berry")
    motives=events["stage12_action_motive_attested"]
    if len(motives)>1:
        raise ValueError("conflicting subjective motives for same motor step")
    stage6=events["stage6_planning_result"]
    searches=[]
    proposal_refs=set()
    cached=0
    for e in stage6:
        data=e.get("data",{})
        diagnostic=data.get("progressive_search_diagnostic")
        if isinstance(diagnostic,dict):
            state=diagnostic.get("status")
            if state in SEARCH_STATUSES:
                searches.append(diagnostic)
                if (
                    not all(k in diagnostic for k in (
                        "root_candidate_edges","root_available_edges",
                        "root_unavailable_edges","root_model_diagnostic",
                    )) or
                    diagnostic["root_available_edges"]+
                    diagnostic["root_unavailable_edges"]>
                    diagnostic["root_candidate_edges"]
                ):
                    raise ValueError("impossible native Stage6 root edge accounting")
            elif state=="reused_cached":
                cached+=1
            elif state is not None:
                raise ValueError("unregistered Stage6 search status")
        if data.get("proposal_ref"):
            proposal_refs.add(data["proposal_ref"])
    if not motives:
        reduced=events["stage10_reduced_capture"]
        if len(reduced)!=1 or primitive!="dormir":
            raise ValueError("missing active motive outside reduced sleep")
        return {
            "category":"reduced_sleep",
            "motive_type":None,"active_goal_ref":None,
            "planner_search_statuses":[d["status"] for d in searches],
            "planner_all_proposal_refs":sorted(proposal_refs),
            "staged_food_proposal_target":"not_observable_without_plan_steps",
            "B_motor_executed":is_B,"B_physical_ingestion":physical_B_eat,
            "uc_refusal_operations":uc_refusals(events),
            "selected_option_ref":None,
        }
    motive=motives[0].get("data",{})
    goal_ref=motive.get("active_goal_ref")
    motive_type=motive.get("motive_type")
    selected_option=motive.get("option_ref")
    if selected_option is not None and not isinstance(selected_option,str):
        raise ValueError("motive selected-option provenance not a string")
    if goal_ref is None:
        category="no_attested_active_goal"
    elif motive_type=="active_goal":
        # A selected *goal* does not identify berry species; its physical
        # command, however, is still attested by the joined motor receipt.
        if len(events["stage12_outcome_responsibility_precommitted"])!=1:
            category="goal_selected_without_precommit"
        else:
            category="goal_selected_with_precommit"
    else:
        selected_goal_stage6=[
            e for e in stage6 if e.get("data",{}).get("goal_ref")==goal_ref
        ]
        if not selected_goal_stage6:
            category="insufficient_same_step_planner_evidence"
        else:
            goal_refs={
                e.get("data",{}).get("proposal_ref")
                for e in selected_goal_stage6
                if e.get("data",{}).get("proposal_ref")
            }
            if not goal_refs:
                category="no_planner_proposal"
            else:
                registered={
                    e.get("data",{}).get("option_ref")
                    for e in events["option_registration"]
                    if e.get("data",{}).get("registered") is True
                }
                ready=goal_refs & registered
                if not ready:
                    category="proposed_not_registered"
                else:
                    evaluated={
                        e.get("data",{}).get("option_ref")
                        for e in events["stage8_option_evaluation"]
                    }
                    evaluated_ready=ready & evaluated
                    if not evaluated_ready:
                        category="registered_not_evaluated"
                    else:
                        competition=[
                            trace for e in events["competition_cycle"]
                            for trace in e.get("data",{}).get("traces",[])
                        ]
                        if not competition:
                            category="insufficient_competition_evidence"
                        else:
                            crossed={
                                tr.get("option_ref") for tr in competition
                                if tr.get("crossed") is True
                            } & evaluated_ready
                            if not crossed:
                                category="evaluated_not_crossed"
                            elif selected_option in crossed:
                                category="crossed_and_selected"
                            else:
                                category="crossed_but_not_selected"
    if category=="crossed_and_selected" and selected_option not in proposal_refs:
        raise ValueError("goal option reported chosen without prior proposal")
    if is_B and primitive=="manger" and physical_B_eat and category not in (
        "goal_selected_with_precommit", "goal_selected_without_precommit",
        "crossed_and_selected", "no_attested_active_goal",
        "insufficient_same_step_planner_evidence",
    ):
        # No false self attribution: actual B ingestion may be a permanent
        # option rather than planner-derived goal. It still requires motive.
        raise ValueError("B ingestion attributed to an unselected B option")
    return {
        "category":category,
        "motive_type":motive_type,"active_goal_ref":goal_ref,
        "planner_search_statuses":[d["status"] for d in searches],
        "planner_all_proposal_refs":sorted(proposal_refs),
        "staged_food_proposal_target":"not_observable_without_plan_steps",
        "B_motor_executed":is_B,"B_physical_ingestion":physical_B_eat,
        "uc_refusal_operations":uc_refusals(events),
        "selected_option_ref":selected_option,
    }


def uc_refusals(by_step_events):
    operations=[]
    for e in by_step_events["compute_charge"]:
        data=e.get("data",{})
        if data.get("accepted") is False:
            operations.append(data.get("operation"))
        elif data.get("accepted") is not True:
            raise ValueError("uncategorized real UC charging outcome")
    return sorted(operations)


def audit_life(life,folder):
    """Independent hash-chain and WAL provenance before classifying."""
    expected_id=(f"i0:stage12:b:a230zb:{life['profile']}:"
                 f"{life['layout']}:{life['hidden_B_external_only']}")
    if (life["birth_id"]!=expected_id
        or life["world_steps"]!=STEPS_PER_LIFE
        or life["mortal_status"]!="experiment_stopped"
        or life["no_forced_commands"] is not True
        or life["postterminal_revival"] is not False
        or life["independent_WAL_P48_dual_agency_audits"] is not True):
        raise ValueError("historical ZB birth, mortality, or autonomy misidentified")
    if life["confirmed_B_ingestions"] or life["experienced_B_commands_with_motives"]:
        raise ValueError("historical zero B action contradicted")
    separate=json.loads((folder/"a230zb-life.json").read_text())
    if separate!=life:
        raise ValueError("per-life receipts differ from primary summary")
    raw=(folder/"canonical.jsonl").read_bytes()
    if sha256(raw).hexdigest()!=life["journal_sha256"]:
        raise ValueError("canonical life SHA-256 differs from original receipt")
    anchor={"expected_head":life["journal_head"],
            "expected_count":life["journal_count"]}
    journal=audit_export_bytes(raw,**anchor)
    if journal.world_steps_closed!=STEPS_PER_LIFE:
        raise ValueError("canonical life has a nonclosed physical step")
    wal=HashChainedJournal.audit_durable_wal(str(folder/"life.wal"))
    if (wal["head_hash"]!=anchor["expected_head"]
        or wal["verified_entries"]!=anchor["expected_count"]):
        raise ValueError("mortal durable WAL disagrees with canonical journal")
    p48=audit_stage12_p48_diversity(raw,**anchor)
    if (p48["world_steps"]!=STEPS_PER_LIFE
        or p48["physically_confirmed_eats"]!=life["all_confirmed_ingestions_P48"]
        or p48["net_food_increase_steps_after_first"]!=
            life["physical_food_gain_steps_P48"]):
        raise ValueError("independently scored P48 physical food source mismatch")
    events=[json.loads(s)["causal_event"] for s in raw.splitlines()]
    group=by_step(events,STEPS_PER_LIFE)
    steps=[]
    for t in range(1,STEPS_PER_LIFE+1):
        classification=classify_step(group[t],t)
        cmd=next(e for e in group[t] if e["kind"]=="command_experienced")
        canonical_cmd={"step":t,"primitive":cmd["primitive"],
                       "parameters":cmd.get("parameters",{})}
        if canonical_cmd!=life["executed_motor_commands"][t-1]:
            raise ValueError("reported motor command differs from journal")
        classification.update({
            "t_monde":t,
            "primitive":cmd["primitive"],
            "parameters":cmd.get("parameters",{}),
            "attempt_ref":cmd["attempt_ref"],
        })
        steps.append(classification)
    searches=[e["data"]["progressive_search_diagnostic"]
              for e in events if e["kind"]=="stage6_planning_result"
              and isinstance(e.get("data",{}).get("progressive_search_diagnostic"),dict)
              and e["data"]["progressive_search_diagnostic"].get("status") in SEARCH_STATUSES]
    count=Counter(d["status"] for d in searches)
    root_unknown=sum(d["root_model_diagnostic"]=="no_predictable_first_step" for d in searches)
    root_available=sum(d["root_available_edges"] for d in searches)
    if (len(searches)!=life["stage6_searches"]
        or count!=life["stage6_status_counts"]
        or root_unknown!=life["stage6_no_known_root_searches"]
        or root_available!=life["stage6_available_root_edge_attempts"]
        or count["plan_found"]!=life["stage6_plan_found_searches"]):
        raise ValueError("Stage6 search diagnostics not reconciled with original ZB")
    uc=Counter(op for row in steps for op in row["uc_refusal_operations"])
    if dict(uc)!=life["lived_UC_refusals"]:
        raise ValueError("UC refusal receipts not reconciled with original")
    if any(e.get("kind")=="perceptual_capture" and
           e.get("t_monde",0)>STEPS_PER_LIFE for e in events):
        raise ValueError("postmortem subjective observation cannot be present")
    if sum(e["kind"]=="experiment_stopped" for e in events)!=1:
        raise ValueError("experiment stop is not an irreversible death")
    root=candidate_root(life["initial_accessible_projection"],life["layout"])
    return {
        "birth_id":life["birth_id"],
        "profile":life["profile"],"layout":life["layout"],
        "hidden_effect_for_external_pairing_only":life["hidden_B_external_only"],
        "first_person_root":root,
        "canonical_journal_sha256":life["journal_sha256"],
        "journal_head":life["journal_head"],
        "journal_events":len(events),
        "waking_or_reduced_steps":len(steps),
        "physical_B_eats":p48["physically_confirmed_eats"] -
            (life["all_confirmed_ingestions_P48"]-len(life["confirmed_B_ingestions"])),
        "physical_all_species_eats":p48["physically_confirmed_eats"],
        "actual_searches":len(searches),
        "actual_search_statuses":dict(sorted(count.items())),
        "root_without_predictable_first_step":root_unknown,
        "root_available_edges":root_available,
        "uc_refusals":dict(sorted(uc.items())),
        "exclusive_step_categories":dict(sorted(Counter(
            x["category"] for x in steps).items())),
        "steps":steps,
        "all_motors_verified_by_command_and_world_transition":True,
        "no_causal_explanation_from_hidden_effect_before_exposure":True,
    }


def validate_core_results(lives):
    if len(lives)!=12:
        raise ValueError("not twelve original I0 lives")
    unique=set()
    by_pair=defaultdict(list)
    for life in lives:
        if life["birth_id"] in unique:
            raise ValueError("duplicate original birth identity")
        unique.add(life["birth_id"])
        key=(life["profile"],life["layout"])
        by_pair[key].append(life)
    if len(by_pair)!=6:
        raise ValueError("not six original paired conditions")
    for key,rows in by_pair.items():
        if len(rows)!=2 or {
            x["hidden_effect_for_external_pairing_only"] for x in rows
        }!=set(VARIANTS):
            raise ValueError("missing matched hidden-effect cause")
    categories=Counter()
    statuses=Counter()
    root_unknown=0
    root_edges=0
    rejected=Counter()
    proposal_refs=Counter()
    motor=Counter()
    candidateB=0
    root_east_visible=0
    for life in lives:
        categories.update(life["exclusive_step_categories"])
        statuses.update(life["actual_search_statuses"])
        root_unknown+=life["root_without_predictable_first_step"]
        root_edges+=life["root_available_edges"]
        rejected.update(life["uc_refusals"])
        candidateB+=life["first_person_root"]["candidate_collect_B_initial"]
        root_east_visible+=life["first_person_root"]["adjacent_east_B_accessible"]
        motor.update((row["primitive"],row["parameters"].get("target"))
                     for row in life["steps"])
        for row in life["steps"]:
            proposal_refs.update(row["planner_all_proposal_refs"])
    if (sum(categories.values())!=384
        or sum(statuses.values())!=196
        or statuses["plan_found"]!=10
        or root_unknown!=174 or root_edges!=18
        or candidateB!=4 or root_east_visible!=4
        or any(p in (("collecter","berry_b"),("manger","berry_b")) for p in motor)
    ):
        raise ValueError("original autonomous funnel disobeys recorded evidence")
    return {
        "new_I0_births":0,"new_physical_steps":0,
        "original_born_I0_lives":12,
        "original_autonomous_world_steps":384,
        "original_B_local_candidates_at_birth":candidateB,
        "original_B_east_visible_accessible_at_birth":root_east_visible,
        "verified_berry_b_motors":0,
        "verified_berry_b_eats":0,
        "actual_stage6_searches":sum(statuses.values()),
        "actual_stage6_search_statuses":dict(sorted(statuses.items())),
        "actual_searches_no_predictable_root":root_unknown,
        "actual_root_available_edge_total":root_edges,
        "exclusive_original_step_categories":dict(sorted(categories.items())),
        "real_UC_refused_operations":dict(sorted(rejected.items())),
        "planner_proposal_refs_not_B_species_grounded":dict(sorted(proposal_refs.items())),
        "B_specific_planner_option_count_identifiable_from_receipts":False,
        "UC_refusal_causally_responsible_for_B_absence_established":False,
        "unique_cause_of_B_absence_established":False,
    }


def original_source(folder, py):
    paths=list(folder.rglob("a230zb-summary.json"))
    if len(paths)!=1:
        raise ValueError("historical ZB summary absent/ambiguous")
    summary_path=paths[0]
    root=summary_path.parent
    raw=summary_path.read_bytes()
    if sha256(raw).hexdigest()!=ORIGINAL_SUMMARY_BYTES_SHA256[py]:
        raise ValueError("original GitHub ZB summary byte SHA-256 mismatched")
    summary=json.loads(raw)
    if (
        summary.get("git_sha")!=HISTORICAL_SHA
        or summary.get("schema")!="a230zb-autonomous-alternative-lived-v1"
        or summary.get("independent_new_I0_births")!=12
        or summary.get("actual_autonomous_world_steps")!=384
        or summary.get("B_collections_executed")!=0
        or summary.get("B_eat_attempts_executed")!=0
        or summary.get("B_ingestions_physically_confirmed")!=0
        or summary.get("stage6_searches")!=196
        or summary.get("stage6_no_predictable_first_step")!=174
        or summary.get("stage6_plan_found_searches")!=10
        or summary.get("stage6_root_available_edge_attempts")!=18
        or summary.get("dual_scope_judgements")!=20
        or summary.get("mortal_statuses")!={"experiment_stopped":12}
        or summary.get("no_Oracle_to_I0") is not True
        or summary.get("all_WALs_authenticated") is not True
        or summary.get("all_actions_autonomous") is not True
    ):
        raise ValueError("not sealed original twelve-life ZB source")
    expected_names={
        f"{p}-{layout}-{variant}" for p in PROFILES for layout in LAYOUTS
        for variant in VARIANTS
    }
    actual_names={x.name for x in root.iterdir() if x.is_dir()}
    if actual_names!=expected_names:
        raise ValueError("unexpected missing or extra ZB life directory")
    reports=[]
    for life in summary["lives"]:
        folder_name=(f"{life['profile']}-{life['layout']}-"
                     f"{life['hidden_B_external_only']}")
        if folder_name not in expected_names:
            raise ValueError("out-of-cohort original birth")
        reports.append(audit_life(life,root/folder_name))
    core=validate_core_results(reports)
    return {"py":py, "root":root, "summary":summary,
            "life_reports":reports,"core":core}


def _compare_except_f64(a,b):
    """Ensure differing cognitive events change only canonical float payloads."""
    if type(a)!=type(b):
        raise ValueError("cross-version cognition changed event field types")
    if isinstance(a,dict):
        if set(a)!=set(b):
            raise ValueError("cross-version cognition changed event structure")
        if set(a)=={"$f64"}:
            v=hexfloat(a);w=hexfloat(b)
            delta=abs(v-w)
            if delta>1e-12:
                raise ValueError("cross-version floating difference exceeds ULP-scale bound")
            return delta
        return max((_compare_except_f64(a[k],b[k]) for k in a),
                   default=0.0)
    if isinstance(a,list):
        if len(a)!=len(b):
            raise ValueError("cross-version lists have different length")
        return max((_compare_except_f64(x,y) for x,y in zip(a,b)),
                   default=0.0)
    if a!=b:
        raise ValueError("cross-version change is not a canonical floating value")
    return 0.0


def compare_original_python_versions(a,b):
    first= {x["birth_id"]:x for x in a["life_reports"]}
    second={x["birth_id"]:x for x in b["life_reports"]}
    if first.keys()!=second.keys():
        raise ValueError("different original I0 births between interpreters")
    if a["core"]!=b["core"]:
        raise ValueError("original cross-version aggregate decisions diverged")
    mismatch=[]
    for birth_id in sorted(first):
        lifeA=first[birth_id]
        lifeB=second[birth_id]
        if deepcopy({k:v for k,v in lifeA.items() if k in (
            "first_person_root","exclusive_step_categories","actual_searches",
            "actual_search_statuses","root_without_predictable_first_step",
            "root_available_edges","uc_refusals",
        )})!=deepcopy({k:v for k,v in lifeB.items() if k in (
            "first_person_root","exclusive_step_categories","actual_searches",
            "actual_search_statuses","root_without_predictable_first_step",
            "root_available_edges","uc_refusals",
        )}):
            raise ValueError("real first-person/root or funnel diverged by Python")
        rootA=a["root"] / ":".join(birth_id.split(":")[5:]) # patched by explicit per-life path below
        del rootA
        label="-".join((
            birth_id.split(":")[-3],
            birth_id.split(":")[-2],
            birth_id.split(":")[-1],
        ))
        rawA=(a["root"]/label/"canonical.jsonl").read_bytes()
        rawB=(b["root"]/label/"canonical.jsonl").read_bytes()
        E=[json.loads(s)["causal_event"] for s in rawA.splitlines()]
        F=[json.loads(s)["causal_event"] for s in rawB.splitlines()]
        if len(E)!=len(F):
            raise ValueError("cross-Python same-life journal length changed")
        mismatch_kinds=Counter()
        max_float_delta=0.0
        first_diff=None
        for j,(x,y) in enumerate(zip(E,F)):
            if x==y:
                continue
            if x["kind"]!=y["kind"] or x.get("t_monde")!=y.get("t_monde"):
                raise ValueError("cross-Python reordered cognitive event or time")
            if x["kind"] not in ALLOWED_CROSS_PY_NUMERICAL_EVENT_KINDS:
                raise ValueError("cross-Python differences leaked into motor/physical/sense")
            delta=_compare_except_f64(x,y)
            if not delta:
                raise ValueError("nonfloat/semantic disagreement without measurable float")
            max_float_delta=max(delta,max_float_delta)
            mismatch_kinds[x["kind"]]+=1
            if first_diff is None:
                first_diff={"event_index":j,"world_step":x.get("t_monde"),
                            "kind":x["kind"]}
        if (rawA==rawB)!= (not mismatch_kinds):
            raise ValueError("byte equality and cognitive event mismatch incompatible")
        if mismatch_kinds:
            mismatch.append({
                "birth_id":birth_id,
                "first_cognitive_difference":first_diff,
                "changed_cognitive_event_count":sum(mismatch_kinds.values()),
                "changed_event_kinds":dict(sorted(mismatch_kinds.items())),
                "maximum_absolute_canonical_f64_delta":max_float_delta,
                "motor_and_physics_identical":True,
            })
    if len(mismatch)!=6:
        raise ValueError("unexpected full-life binary reproducibility classification")
    if {x["birth_id"].split(":")[-3] for x in mismatch}!={"sustained"}:
        raise ValueError("cross-Python divergence not limited to sustained")
    if a["core"]["real_UC_refused_operations"] or b["core"]["real_UC_refused_operations"]:
        # A refusal anywhere may matter; still record but never causally
        # attribute it to B unless we have a same-motive link.
        pass
    return {
        "both_versions_original_records_independently_authenticated":True,
        "whole_journals_byte_identical_lives":6,
        "whole_journals_not_byte_identical_lives":len(mismatch),
        "changed_only_floating_point_cognition":True,
        "physical_and_perceptual_events_bit_identical":True,
        "cognitive_float_max_absolute_difference":max(
            x["maximum_absolute_canonical_f64_delta"] for x in mismatch),
        "divergences":mismatch,
        "full_cross_python_cognitive_reproducibility":False,
    }


def run(a_dir:Path,b_dir:Path,out_dir:Path):
    source_a=original_source(a_dir,"3.11")
    source_b=original_source(b_dir,"3.12")
    cross=compare_original_python_versions(source_a,source_b)
    merged={
        "schema":"a230zd-original-12-life-independent-attrition-v1",
        "source_historical_run":HISTORICAL_RUN,
        "source_birth_code_sha":HISTORICAL_SHA,
        "original_python_summary_sha256":ORIGINAL_SUMMARY_BYTES_SHA256,
        "new_I0_lives":0,"new_physical_world_steps":0,
        "separate_preexisting_original_born_lives":12,
        "source_py311_metrics":source_a["core"],
        "source_py312_metrics":source_b["core"],
        "cross_python_integrity":cross,
        "preselection_B_species_planner_intention_identified":False,
        "unobserved_latent_B_toxicity_could_influence_subjective_choice":False,
        "B_food_goal_achieved_by_I0":False,
        "Stage6_model_or_agency_failure_unique_cause_proven":False,
        "cognitive_integration_approved":False,
        "normative_MVP_unchanged":True,
        "issue110":"OPEN","Stage12":"PARTIAL","A2_30":"PARTIELLE",
    }
    out_dir.mkdir(parents=True,exist_ok=False)
    (out_dir/"a230zd-audited-funnel.json").write_text(json.dumps(
        merged,indent=2,sort_keys=True)+"\n")
    trace=[{
        "python":s["py"], "lives":[{
            "birth_id":x["birth_id"],"layout":x["layout"],"profile":x["profile"],
            "first_person_root":x["first_person_root"],
            "exclusive_step_categories":x["exclusive_step_categories"],
            "steps":x["steps"],
        } for x in s["life_reports"]],
    } for s in (source_a,source_b)]
    (out_dir/"a230zd-step-funnel.json").write_text(json.dumps(
        trace,indent=2,sort_keys=True)+"\n")
    print("A230ZD_SUMMARY "+json.dumps({
        "source_run":HISTORICAL_RUN,
        "physical_world_steps":source_a["core"]["original_autonomous_world_steps"],
        "candidate_B_local_at_birth":source_a["core"]["original_B_local_candidates_at_birth"],
        "candidate_B_east_at_birth":source_a["core"]["original_B_east_visible_accessible_at_birth"],
        "step_categories":source_a["core"]["exclusive_original_step_categories"],
        "uc_refusals":source_a["core"]["real_UC_refused_operations"],
        "real_stage6_searches":source_a["core"]["actual_stage6_searches"],
        "cross_python_numerically_different_lives":
            cross["whole_journals_not_byte_identical_lives"],
        "cross_python_max_delta":cross["cognitive_float_max_absolute_difference"],
        "all_motor_and_physical_receipts_equal":
            cross["physical_and_perceptual_events_bit_identical"],
        "new_I0_lives":0,"Stage12":"PARTIAL",
    },sort_keys=True),flush=True)
    return merged


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-py311",type=Path,required=True)
    parser.add_argument("--source-py312",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    run(args.source_py311,args.source_py312,args.output_dir)


if __name__=="__main__":
    main()
