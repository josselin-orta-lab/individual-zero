"""A2.30-ZQA: independent sealed-archive audit of 24 genuine autonomous I0 lives.

OFFLINE ONLY: no import of ZQ runner, Stage12Runtime, WorldBody, simulator,
Equipment or subjective-judgement implementations. Reads historical immutable
ZB+ZQ CI JSON, durable WAL and canonical journals, re-computes all physical,
motor, first-person, death, UC and dual-scope lineage without issuing commands.

ZR is a POST-HOC audit; its prereg predates this reviewer implementation
but not original known ZQ results, see docs/research/...-a230zqa-...-prereg.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes,sha256_hex
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal

SOURCE_RUN=38796937894
SOURCE_SHA="850256d02cdc9a2fc9be78f7ce1f66ca5dc98347"
ZB_RUN=38767643472
ZB_SHA="2a19742df22f27752635203304097134a3009c45"
ZQ_SUMMARY_SHA={
    "3.11":"fba7f4011aac074ab1106f604fae912fec4170c6f8aa8e9e0012accad7fda650",
    "3.12":"edafcaa281082af05aa7cd0a74ff72ff573485fc2f82a0068b6d315cea367ac6",
}
ZB_SUMMARY_SHA={
    "3.11":"ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b",
    "3.12":"ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362",
}
PAIR_SHA="99643f0a40069be640eaf2c4a02565953288ecb362a4fa00f9ee9c2e4a03c437"
PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST")
B_HIDDEN=("benign","toxic_lethal")
MOTOR=("motor_clear","motor_hidden_lethal")
VALID_STATE_KEYS={
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
}
REAL_SEARCH_STATUSES={
    "plan_found","partial_progress","incomplete_model","not_found_within_horizon",
}


def sha(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def load_one(root,name,expected):
    candidates=list(Path(root).rglob(name))
    if len(candidates)!=1:
        raise ValueError("missing or duplicate immutable CI artifact "+name)
    raw=candidates[0].read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise ValueError("wrong full SHA-256 for immutable CI artifact "+name)
    return json.loads(raw)


def load_sources(root311,root312,zb311,zb312):
    zq={}
    zb={}
    for label,root,original in (
        ("3.11",root311,zb311),("3.12",root312,zb312)
    ):
        zqsummary=load_one(
            root,"a230zq-summary.json",ZQ_SUMMARY_SHA[label]
        )
        pair=load_one(root,"a230zq-pairing.json",PAIR_SHA)
        bz=load_one(
            original,"a230zb-summary.json",ZB_SUMMARY_SHA[label]
        )
        if (zqsummary["schema"]!="a230zq-autonomous-hidden-motor-risk-v1"
            or zqsummary["experiment_code_head"]!=SOURCE_SHA
            or bz["schema"]!="a230zb-autonomous-alternative-lived-v1"
            or bz["git_sha"]!=ZB_SHA):
            raise ValueError("original GitHub Actions source run substituted")
        zq[label]=(zqsummary,pair,Path(root))
        zb[label]=bz
    if zq["3.11"][1]!=zq["3.12"][1]:
        raise ValueError("original causal motor pairing differs across Python")
    return zq,zb


def verify_12_original_birth_roots(zb):
    a={x["birth_id"]:x for x in zb["3.11"]["lives"]}
    b={x["birth_id"]:x for x in zb["3.12"]["lives"]}
    if len(a)!=12 or len(b)!=12 or set(a)!=set(b):
        raise ValueError("ZB original 12 mortal births were changed")
    by_recipe={}
    for identity,row in a.items():
        other=b[identity]
        for name in ("profile","layout","hidden_B_external_only",
                     "initial_accessible_projection","equipment_sha256_A_only"):
            if row[name]!=other[name]:
                raise ValueError("historical first-person root changed across Python")
        key=(row["profile"],row["layout"],row["hidden_B_external_only"])
        if key in by_recipe:
            raise ValueError("same original I0 birth was duplicated")
        by_recipe[key]={
            "root":row["initial_accessible_projection"],
            "equipment_sha256":row["equipment_sha256_A_only"],
            "historical_birth_id":identity,
        }
    if len(by_recipe)!=12:
        raise ValueError("original firstperson factorial roots missing")
    return by_recipe


def validate_visible_state(s):
    if type(s) is not dict or set(s)!=VALID_STATE_KEYS:
        raise ValueError("hidden, future or missing first-person birth field")
    if (set(s["body"])!={"energy","food","water","integrity"}
        or set(s["inventory"])!={"berry_a","berry_b","stone","tool","wood"}
        or len(s["adjacent"])!=4
        or {n["direction"] for n in s["adjacent"]}!={
            "north","south","east","west"}):
        raise ValueError("hidden variable or malformed first-person body/neighbors")
    if not all(set(n)=={"direction","x","y","passable","resources",
                       "water_source","creature"} for n in s["adjacent"]):
        raise ValueError("neighbor field has hidden external cause")
    return s


def visible_from_capture(event):
    """Never invent a capture absent from the original source journal."""
    d=event["data"]
    return {
        "t_monde":event["t_monde"],
        "position":d.get("position"),
        "visible_adjacent":d.get("agency_visible_adjacent",[]),
        "visible_body":d.get("dual_scope_visible_body",{}),
        "visible_inventory":d.get("agency_visible_inventory"),
    }


def verify_original_life(folder,life,prior):
    raw=(folder/"canonical.jsonl").read_bytes()
    wal=folder/"life.wal"
    if (not wal.is_file() or
        sha256(raw).hexdigest()!=life["journal_sha256"]):
        raise ValueError("real original canonical export or WAL is missing/forged")
    verified=audit_export_bytes(
        raw,expected_head=life["journal_head"],
        expected_count=life["journal_count"],
    )
    durable=HashChainedJournal.audit_durable_wal(str(wal))
    if (durable["head_hash"]!=life["journal_head"]
        or durable["verified_entries"]!=life["journal_count"]
        or verified.world_steps_closed!=life["world_steps"]):
        raise ValueError("WAL/physical/P48 closure does not match life summary")
    ev=[json.loads(line)["causal_event"] for line in raw.splitlines()]
    profile,layout,b_hidden,motor=(
        life["profile"],life["layout"],
        life["hidden_B_external_only"],life["ZQ_motor_treatment_external_only"],
    )
    if (profile not in PROFILES or layout not in LAYOUTS
        or b_hidden not in B_HIDDEN or motor not in MOTOR
        or life["zq_schema"]!="a230zq-genuine-autonomous-motor-hazard-life-v1"
        or life["world_steps"]>32
        or life["mortal_status"] not in ("dead","experiment_stopped")
        or life["no_forced_commands"] is not True
        or life["no_oracle_feedback"] is not True
        or life["no_world_truth_or_oracle_data_to_I0"] is not True
        or life["berry_B_safety_certified"] is not False
        or life["motor_commands_from_original_I0_only"] is not True):
        raise ValueError("original autonomous mortal birth contract altered")
    original=prior[(profile,layout,b_hidden)]
    root=validate_visible_state(life["initial_accessible_projection"])
    if (root!=original["root"]
        or life["equipment_sha256_A_only"]!=original["equipment_sha256"]
        or life["birth_id"]==original["historical_birth_id"]
        or root["x"]!=2 or root["y"]!=2
        or life["birth_initial_firstperson_sha256"]!=sha(root)):
        raise ValueError("hidden experimental motor intervention changed cognition at birth")
    if (life["world_birth_configuration_external"].get(
            "lethal_zone_external_only"
        )!=([{"x":3,"y":1}] if motor=="motor_hidden_lethal" else [])
        or life["world_birth_configuration_external"]["at_birth_only"] is not True):
        raise ValueError("unpreregistered hidden physical intervention")
    commands={e["t_monde"]:e for e in ev if e["kind"]=="command_experienced"}
    outcomes={e["t_monde"]:e for e in ev
              if e["kind"]=="world_transition_experienced"}
    deaths=[e for e in ev if e["kind"]=="individual_death_confirmed"]
    if (len(commands)!=life["world_steps"]
        or len(outcomes)!=life["world_steps"]
        or sorted(commands)!=list(range(1,life["world_steps"]+1))
        or sorted(outcomes)!=list(range(1,life["world_steps"]+1))
        or len(deaths)!=(life["mortal_status"]=="dead")
        or verified.terminal_deaths!=len(deaths)):
        raise ValueError("physical step/death event completeness broken")
    captures={(x["t_monde"],x["attempt_ref"]):x
              for x in ev if x["kind"]=="perceptual_capture"}
    motives={(x["t_monde"],x["attempt_ref"]):x
             for x in ev if x["kind"]=="stage12_action_motive_attested"}
    actions=[]
    priorpos={"x":root["x"],"y":root["y"]}
    missing_captures=0
    accepted_uc=0
    denied_uc=0
    for e in ev:
        if e["kind"]=="compute_charge":
            ch=e["data"]
            n=ch.get("requested_uc")
            if type(n) is not int or n<0:
                raise ValueError("actual UC request mutated")
            if ch.get("accepted") is True:
                accepted_uc+=n
            elif ch.get("accepted") is False:
                denied_uc+=n
            else:
                raise ValueError("unknown actual UC acceptance")
    for t in range(1,life["world_steps"]+1):
        c=commands[t]
        w=outcomes[t]
        if c["attempt_ref"]!=w["attempt_ref"]:
            raise ValueError("motor action and physical outcome different attempts")
        command={"primitive":c["primitive"],"parameters":c.get("parameters",{})}
        if sha(command)!=c["command_hash"]:
            raise ValueError("wrong original motor action digest")
        cap=captures.get((t,c["attempt_ref"]))
        firstperson=visible_from_capture(cap) if cap is not None else None
        if firstperson is None:
            missing_captures+=1
        else:
            if firstperson["position"]!=priorpos:
                raise ValueError("firstperson and prior physics location conflict")
            if (len(firstperson["visible_adjacent"])!=4
                or any("lethal" in str(n) or "hidden" in str(n)
                       or "oracle" in str(n) for n in
                       firstperson["visible_adjacent"])):
                raise ValueError("hidden lethal-zone variable leaked into perception")
        motive=motives.get((t,c["attempt_ref"]))
        if motive is not None and motive["data"]["command_hash"]!=c["command_hash"]:
            raise ValueError("chosen action has unrelated motive receipt")
        originally=life["preaction_commands_with_firstperson_receipts"][t-1]
        if (originally["primitive"]!=command["primitive"]
            or originally["parameters"]!=command["parameters"]
            or originally["preaction_firstperson_capture"]!=firstperson
            or originally["preaction_firstperson_sha256"]!=(
                sha(firstperson) if firstperson is not None else None
            )
            or originally["preaction_firstperson_receipt_status"]!=(
                "available" if firstperson is not None else
                "unavailable_in_canonical_journal"
            )
            or originally["verified_physical_position_after"]!=w["position_after"]
            or originally["preaction_position_from_physical_chain_external_only"]!=priorpos
            or originally["lab_chose_or_dispatched_this_primitive"] is not False):
            raise ValueError("motor receipt falsely presented as a subjective sensation")
        if originally["motive_external_journal_receipt"]!=(
            motive["data"] if motive else None
        ):
            raise ValueError("unattested voluntary motive source")
        actions.append({
            "t":t,"command":command,"attempt_ref":c["attempt_ref"],
            "command_hash":c["command_hash"],
            "before_position_external_only":priorpos,
            "after_position_external_only":w["position_after"],
            "after_body_external_only":w["body_after"],
            "preaction_firstperson":firstperson,
            "motive_external_receipt":motive["data"] if motive else None,
        })
        priorpos=w["position_after"]
    if len(actions)!=len(life["preaction_commands_with_firstperson_receipts"]):
        raise ValueError("autonomous source inserted a ghost action")
    if missing_captures!=life["physical_steps_without_same_attempt_firstperson_capture"]:
        raise ValueError("missing firstperson sensory event retroactively fabricated")
    if (accepted_uc!=life["actual_accepted_UC_requests_total"]
        or denied_uc!=life["actual_denied_UC_requests_total"]):
        raise ValueError("reported UC use not supported by compute_charge receipts")
    if deaths:
        d=deaths[0]
        final=actions[-1]
        if (d["t_monde"]!=life["world_steps"]
            or d["attempt_ref"]!=final["attempt_ref"]
            or d["command_hash"]!=final["command_hash"]
            or d["position_after"]!=final["after_position_external_only"]
            or d["body_after"]!=final["after_body_external_only"]
            or any(e.get("t_monde",0)>d["t_monde"] for e in ev)):
            raise ValueError("death event not joined to physical final action, or resurrection")
        if not d.get("reasons") or life["terminal_causes_external_only"]!=d["reasons"]:
            raise ValueError("external death reason suppressed or invented")
    elif life["terminal_causes_external_only"] is not None:
        raise ValueError("nondead life has a fabricated death reason")
    stage6=[]
    for e in ev:
        if e["kind"]!="stage6_planning_result":
            continue
        diag=e.get("data",{}).get("progressive_search_diagnostic")
        if diag and diag.get("status") in REAL_SEARCH_STATUSES:
            stage6.append(diag)
    proximal=[e for e in ev if e["kind"]=="stage12_goal_agency_judgement"]
    distal=[e for e in ev if
            e["kind"]=="stage12_outcome_responsibility_judgement"]
    for judgement in proximal+distal:
        if judgement["t_monde"]>life["world_steps"]:
            raise ValueError("postmortem subjective judgement fabricated")
    actual_self=sum(x["data"].get("subjective_agency")=="self" for x in proximal)
    actual_unknown=sum(x["data"].get("subjective_agency")=="unknown"
                       for x in proximal)
    if (len(stage6)!=life["stage6_searches"]
        or len(distal)!=life["dual_judgements"]
        or actual_self!=life["proximal_self_judgements"]
        or actual_unknown!=life["proximal_unknown_judgements"]):
        raise ValueError("actual planning/agency receipts miscounted or death falsely judged")
    east_count=sum(x["command"]=={
        "primitive":"se_deplacer","parameters":{"direction":"east"}
    } for x in actions)
    collections=sum(
        x["command"]=={"primitive":"collecter","parameters":{"target":"berry_b"}}
        for x in actions
    )
    eats=sum(
        x["command"]=={"primitive":"manger","parameters":{"target":"berry_b"}}
        for x in actions
    )
    if (east_count!=life["physically_east_movements"]
        or collections!=life["physically_collected_B"]
        or eats!=life["physically_eaten_B_commands"]):
        raise ValueError("physical berry B commands falsely counted")
    first_exposure=next((
        a["t"] for a in actions
        if a["before_position_external_only"]=={"x":2,"y":1}
        and a["command"]=={
            "primitive":"se_deplacer","parameters":{"direction":"east"}}
        and a["after_position_external_only"]=={"x":3,"y":1}
    ),None)
    if first_exposure!=life["first_hidden_test_cell_entry_step"]:
        raise ValueError("hidden motor treatment entry was falsified")
    motor_death=bool(
        motor=="motor_hidden_lethal" and
        deaths and first_exposure==life["world_steps"] and
        "lethal_zone" in deaths[0]["reasons"]
    )
    if motor_death!=life["motor_zone_death_observed"]:
        raise ValueError("unearned fatal motor-cause assignment")
    return {
        "birth_id":life["birth_id"],"profile":profile,"layout":layout,
        "B_hidden_external_only":b_hidden,"motor_external_only":motor,
        "body_initial_visible":root,
        "model_sha256_at_birth":life["equipment_sha256_A_only"],
        "world_steps":life["world_steps"],
        "end_status":life["mortal_status"],
        "terminal_reason_external":deaths[0]["reasons"] if deaths else None,
        "motor_death":motor_death,
        "first_motor_hazard_cell_entry":first_exposure,
        "real_actions":actions,
        "firstperson_missing_capture_steps":missing_captures,
        "real_stage6_searches":len(stage6),
        "real_dual_scope_outcomes":len(distal),
        "real_proximal_self":actual_self,
        "real_proximal_unknown":actual_unknown,
        "accepted_UC_requested":accepted_uc,
        "refused_UC_requested":denied_uc,
        "physically_executed_east_moves":east_count,
        "physically_executed_collect_B":collections,
        "physically_executed_eat_B":eats,
        "source_canonical_sha256":sha256(raw).hexdigest(),
        "source_m11_wal_head":durable["head_hash"],
        "mortal_world_step_closure_audited":True,
        "hidden_external_cause_never_transferred_to_sense":True,
    }


def review_source(root,source_summary,source_pairs,original):
    subdirs=[p for p in Path(root).rglob("a230zq-life.json")]
    if len(subdirs)!=24 or len({p.parent for p in subdirs})!=24:
        raise ValueError("not 24 distinct original mortal life archives")
    if (len(list(Path(root).rglob("canonical.jsonl")))!=24
        or len(list(Path(root).rglob("life.wal")))!=24):
        raise ValueError("missing/doubled durable WAL or canonical mortal journals")
    audited=[]
    identities=set()
    keys=set()
    for path in subdirs:
        life=json.loads(path.read_bytes())
        if (life["birth_id"] in identities or
            (life["profile"],life["layout"],life["hidden_B_external_only"],
             life["ZQ_motor_treatment_external_only"]) in keys):
            raise ValueError("mortal I0 birth ID or factorial cell reused")
        identities.add(life["birth_id"])
        keys.add((life["profile"],life["layout"],
                  life["hidden_B_external_only"],
                  life["ZQ_motor_treatment_external_only"]))
        audited.append(verify_original_life(path.parent,life,original))
    if len(keys)!=24 or keys!=set(product(
        PROFILES,LAYOUTS,B_HIDDEN,MOTOR
    )):
        raise ValueError("24 original autonomous physical contexts not factorial")
    by={(x["profile"],x["layout"],x["B_hidden_external_only"],
         x["motor_external_only"]):x for x in audited}
    paired=[]
    for profile,layout,b_hidden in product(PROFILES,LAYOUTS,B_HIDDEN):
        control=by[(profile,layout,b_hidden,"motor_clear")]
        treated=by[(profile,layout,b_hidden,"motor_hidden_lethal")]
        if (control["body_initial_visible"]!=treated["body_initial_visible"]
            or control["model_sha256_at_birth"]!=treated["model_sha256_at_birth"]
            or control["birth_id"]==treated["birth_id"]):
            raise ValueError("paired birth state or cognitive prior was not identical")
        ea=control["real_actions"]
        eb=treated["real_actions"]
        if (len(ea)<2 or len(eb)!=2
            or [x["command"] for x in ea[:2]]!=[
                {"primitive":"se_deplacer","parameters":{"direction":"north"}},
                {"primitive":"se_deplacer","parameters":{"direction":"east"}},
            ]
            or [x["command"] for x in eb]!=[
                {"primitive":"se_deplacer","parameters":{"direction":"north"}},
                {"primitive":"se_deplacer","parameters":{"direction":"east"}},
            ]
            or not all(
                a["preaction_firstperson"] is not None
                and b["preaction_firstperson"] is not None
                and a["preaction_firstperson"]==b["preaction_firstperson"]
                and a["before_position_external_only"]==
                    b["before_position_external_only"]
                and a["after_position_external_only"]==
                    b["after_position_external_only"]
                for a,b in zip(ea[:2],eb[:2])
            )):
            raise ValueError("autonomous north/east preexposure not perceptually matched")
        if (control["world_steps"]!=32
            or treated["world_steps"]!=2
            or control["end_status"]!="experiment_stopped"
            or treated["end_status"]!="dead"
            or control["first_motor_hazard_cell_entry"]!=2
            or treated["first_motor_hazard_cell_entry"]!=2
            or treated["terminal_reason_external"]!=["lethal_zone"]
            or control["terminal_reason_external"] is not None
            or treated["real_dual_scope_outcomes"]!=0
            or treated["real_proximal_self"]!=0
            or treated["real_proximal_unknown"]!=0):
            raise ValueError("actual terminal motor contrast or no-postmortem contract failed")
        # The body can remain intact when hidden terminality alone fires.
        if ea[1]["after_body_external_only"]!=eb[1]["after_body_external_only"]:
            raise ValueError("physical control and terminal hidden hazard differ in visible body")
        if (ea[1]["before_position_external_only"]!={"x":2,"y":1}
            or eb[1]["after_position_external_only"]!={"x":3,"y":1}
            or eb[1]["preaction_firstperson"]["position"]!={"x":2,"y":1}):
            raise ValueError("fatal coordinate was not physically/perceptually reached")
        paired.append({
            "profile":profile,"layout":layout,"hidden_B_external_only":b_hidden,
            "motor_control_birth":control["birth_id"],
            "motor_fatal_birth":treated["birth_id"],
            "both_distinct_autonomous_cognitive_origins":True,
            "command_and_firstperson_parity_through_second_move":True,
            "physically_terminal_only_with_latent_zone":True,
            "terminal_report_external_and_not_lived_after_death":True,
            "no_food_safety_inferred":True,
        })
    derived={
        "births":len(audited),
        "real_autonomous_steps":sum(x["world_steps"] for x in audited),
        "terminal_deaths":sum(x["end_status"]=="dead" for x in audited),
        "firstperson_invisible_motor_deaths":sum(x["motor_death"] for x in audited),
        "paired_hazard_contrasts":len(paired),
        "motor_east_actions":sum(x["physically_executed_east_moves"] for x in audited),
        "B_collections":sum(x["physically_executed_collect_B"] for x in audited),
        "B_eats":sum(x["physically_executed_eat_B"] for x in audited),
        "stage6_actual_searches":sum(x["real_stage6_searches"] for x in audited),
        "accepted_UC_requests":sum(x["accepted_UC_requested"] for x in audited),
        "refused_UC_requests":sum(x["refused_UC_requested"] for x in audited),
        "dual_scope_judgements":sum(x["real_dual_scope_outcomes"] for x in audited),
        "proximal_self":sum(x["real_proximal_self"] for x in audited),
        "proximal_unknown":sum(x["real_proximal_unknown"] for x in audited),
        "genuine_missing_firstperson_capture_steps":sum(
            x["firstperson_missing_capture_steps"] for x in audited
        ),
    }
    expected={
        "births":24,"real_autonomous_steps":408,"terminal_deaths":12,
        "firstperson_invisible_motor_deaths":12,"paired_hazard_contrasts":12,
        "motor_east_actions":274,"B_collections":0,"B_eats":0,
        "stage6_actual_searches":208,"accepted_UC_requests":7954,
        "refused_UC_requests":0,"dual_scope_judgements":20,
        "proximal_self":12,"proximal_unknown":8,
        "genuine_missing_firstperson_capture_steps":46,
    }
    if derived!=expected:
        raise ValueError(
            "known ZQ results not reproduced independently from real events: "
            +repr(derived)
        )
    if (source_summary["real_autonomous_world_steps"]!=derived["real_autonomous_steps"]
        or source_summary["new_independently_born_I0"]!=24
        or source_summary["terminal_individuals"]!=12
        or source_summary["paired_survival_death_contrasts"]!=12
        or source_summary["autonomous_firstperson_motor_east_commands"]!=274
        or source_summary["real_stage6_planner_queries"]!=208
        or source_summary["actual_accepted_UC_requests_total"]!=7954
        or source_summary["actual_denied_UC_requests_total"]!=0
        or source_summary["physically_confirmed_B_ingestions"]!=0
        or source_summary["new_model_transitions_or_I0_cognitive_changes"] is not False
        or source_summary["B_food_safety_proven"] is not False
        or source_summary["subjective_attribution_of_cause_of_death_proven"] is not False):
        raise ValueError("original ZQ scientific aggregation contradicts original journals")
    pairindex={(p["profile"],p["layout"],p["hidden_B_external"]):p
               for p in source_pairs}
    if len(pairindex)!=12:
        raise ValueError("original pairing records duplicated or missing")
    for p in paired:
        historic=pairindex[(p["profile"],p["layout"],
                            p["hidden_B_external_only"])]
        if (historic["clear_birth_id"]!=p["motor_control_birth"]
            or historic["hidden_lethal_birth_id"]!=p["motor_fatal_birth"]
            or historic["commands_parity_until_exposure"] is not True
            or historic["first_person_capture_parity_until_exposure"] is not True
            or historic["physical_survival_contrast_established"] is not True):
            raise ValueError("original ZQ paired cause/fatal claim not reconstructible")
    return derived,audited,paired


def execute(zq311,zq312,zb311,zb312,output):
    source,zb=load_sources(zq311,zq312,zb311,zb312)
    prior=verify_12_original_birth_roots(zb)
    parts={}
    for label in ("3.11","3.12"):
        summary,pairs,root=source[label]
        derived,rows,reconstructed=review_source(
            root,summary,pairs,prior
        )
        parts[label]={
            "aggregate":derived,
            "first_two_commands_per_birth":{
                row["birth_id"]:[
                    r["command"] for r in row["real_actions"][:2]
                ] for row in rows
            },
            "pair_ids":[(
                x["motor_control_birth"],x["motor_fatal_birth"]
            ) for x in reconstructed],
        }
    if (parts["3.11"]["aggregate"]!=parts["3.12"]["aggregate"]
        or parts["3.11"]["first_two_commands_per_birth"]!=
            parts["3.12"]["first_two_commands_per_birth"]
        or parts["3.11"]["pair_ids"]!=parts["3.12"]["pair_ids"]):
        raise ValueError("cross-Python physically verified autonomous controls differ")
    result={
        "schema":"a230zqa-independent-sealed-autonomous-motor-cause-audit-v1",
        "original_ZQ_run":SOURCE_RUN,
        "original_ZQ_code_sha":SOURCE_SHA,
        "source_sha256_by_python":ZQ_SUMMARY_SHA,
        "pairing_sha256_both_python":PAIR_SHA,
        "historical_ZB_source_summary_sha256_by_python":ZB_SUMMARY_SHA,
        "original_24_I0_lives_reaudited":24,
        "original_24_durable_mortal_WAL_reverified":24,
        "original_24_canonical_hash_chains_reverified":24,
        "original_24_physical_P48_closures_recounted":24,
        "original_12_autonomous_mortal_pairs_reconstructed":12,
        "cross_python_same_408_physical_steps_verified":True,
        "motor_hazard_discriminant":"SUPPORTED_BOUNDED",
        "actual_original_executed_evidence":parts["3.11"]["aggregate"],
        "all_12_hidden_lethal_deaths_join_final_motor_east_receipt":True,
        "all_terminal_mortality_external_and_not_subjectively_certified":True,
        "true_I0_UC_requests_recomputed_from_raw_charge_events":True,
        "missing_perceptual_captures_never_fabricated":True,
        "all_hidden_food_and_zone_causes_external_only":True,
        "all_witnessed_prior_models_are_A_only":True,
        "original_I0_births_not_replayed_or_duplicated":True,
        "cross_python_ULP_journal_divergence_preserved":True,
        "worldbody_apply_independently_reexecuted":False,
        "new_I0_births":0,"new_I0_autonomous_steps":0,
        "new_external_physical_worlds":0,
        "new_external_physical_steps":0,
        "proximal_self_does_not_certify_distal_deadly_cause":True,
        "B_food_safety_proven":False,
        "autonomous_safe_exploration_capability_proven":False,
        "stage12":"PARTIAL","a230":"PARTIELLE",
        "issue110_administrative_status":"CLOSED",
        "cognitive_policy_deployment":"NO-GO",
        "audit_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    }
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230zqa-summary.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZQA_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k not in (
            "source_sha256_by_python","historical_ZB_source_summary_sha256_by_python"
        )
    },sort_keys=True),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    for field in ("zq311","zq312","zb311","zb312","output_dir"):
        ap.add_argument("--"+field.replace("_","-"),type=Path,required=True)
    args=ap.parse_args()
    execute(args.zq311,args.zq312,args.zb311,args.zb312,args.output_dir)


if __name__=="__main__":
    main()
