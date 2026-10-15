"""A2.30-ZP: independent, read-only audit of five immutable ZO artifacts.

Preregistered in docs/research/stage12-a230zp-independent-sealed-factorized-audit-prereg-2026-10-15.fr.md,
after ZO outcomes but before ZP source. Pure standard-library implementation;
no import of ZO runner, WorldBody, Equipment, I0, Oracle or SimulatorPlanner.

Scope: verify archived receipts and first-person-only predictions. This does
NOT independently re-execute WorldBody.apply or prove prediction receipt was
emitted before an original heldout physical transition.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import unicodedata

SOURCE_RUN = 38792466785
SOURCE_SHA = "50185e2db1dc03188aca372fa0e3b854eaf85915"
PREREG_SHA = "8f4846826394ed34519710d4774ac8c04f691b8a"
FILES = {
    "a230zo-physical-training.json":
        "4ad8489762b32ce21f17809121893a7afd7d96500464124ca28492d87a57d166",
    "a230zo-frozen-partial-model.json":
        "d649d5dd716972824f4190dee4ae3dc5818dc323bb757a1197adffa5232d2dee",
    "a230zo-original-heldout-worlds.json":
        "cc9bd690974c08b831e0ffc0d785040b3fba0a0875b8ce5fd99d8e33043607ef",
    "a230zo-prospective-scores.json":
        "0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354",
    "a230zo-summary.json":
        "d772ebe965238347396da77d40841c39e14573f964bfede50527714601fcd53c",
}
SENSORY_KEYS = frozenset({
    "schema_version", "x", "y", "body", "inventory", "current_resources",
    "current_water_source", "adjacent", "known_shelter_here", "is_night",
})
BODY_KEYS = frozenset(("energy", "food", "water", "integrity"))
INVENTORY_KEYS = frozenset(("berry_a", "berry_b", "stone", "tool", "wood"))
NEIGHBOR_KEYS = frozenset((
    "direction", "x", "y", "passable", "water_source", "resources", "creature",
))
DELTA_KEYS = frozenset(("x", "y", "energy", "food", "water", "inventory_berry_b"))
ACTIONS = {
    "MOVE_E": {"primitive": "se_deplacer", "parameters": {"direction": "east"}},
    "COLLECT_B": {"primitive": "collecter", "parameters": {"target": "berry_b"}},
}
TRAIN_POS = ((5, 5), (7, 7))
TEST_POS = ((9, 9), (11, 11), (13, 13), (15, 15))
TRAIN_FOOD = (35.0, 45.0)
NOMINAL_BODIES = ((35.0, 25.0, 30.0), (70.0, 55.0, 65.0))
BOUNDARY_BODY = (0.5, 0.25, 0.1)
PHASES = (1, 201)
LATENT = ("benign", "toxic_lethal")
INTERVENTIONS = (
    "hidden_lethal_east", "hidden_danger_here", "hidden_forced_action_failure",
)


def normalize(x):
    """Reimplementation of the project causal JSON hashing wire contract."""
    if x is None or isinstance(x, (bool, int)):
        return x
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError("non-finite historical float")
        return {"$f64": (0.0 if x == 0.0 else x).hex().lower()}
    if isinstance(x, str):
        return unicodedata.normalize("NFC", x)
    if isinstance(x, (tuple, list)):
        return [normalize(v) for v in x]
    if isinstance(x, dict):
        output = {}
        for name, value in x.items():
            if not isinstance(name, str):
                raise TypeError("non-string historical key")
            normalized = unicodedata.normalize("NFC", name)
            if normalized in output:
                raise ValueError("normalized historical key collision")
            output[normalized] = normalize(value)
        return output
    raise TypeError("non-canonical historical type")


def digest(x):
    return sha256(json.dumps(
        normalize(x), ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _original_bytes(root, file_name, required_sha):
    found = list(Path(root).rglob(file_name))
    if len(found) != 1:
        raise ValueError("original ZO filename absent or ambiguous: " + file_name)
    raw = found[0].read_bytes()
    if sha256(raw).hexdigest() != required_sha:
        raise ValueError("sealed original ZO SHA-256 changed: " + file_name)
    return raw


def load_archives(archive_311, archive_312):
    one = {name: _original_bytes(archive_311, name, hexdigest)
           for name, hexdigest in FILES.items()}
    two = {name: _original_bytes(archive_312, name, hexdigest)
           for name, hexdigest in FILES.items()}
    if one != two:
        raise ValueError("two original ZO source files are not byte identical")
    return tuple(json.loads(one[key]) for key in FILES)


def visible_state(raw):
    if not isinstance(raw, dict) or set(raw) != SENSORY_KEYS:
        raise ValueError("unperceived hidden/future field or missing first-person field")
    if (set(raw["body"]) != BODY_KEYS or
        set(raw["inventory"]) != INVENTORY_KEYS or
        raw["schema_version"] != "stage6-simulation-state-v1" or
        len(raw["adjacent"]) != 4):
        raise ValueError("corrupt first-person body or neighbor schema")
    neighbors = raw["adjacent"]
    if ({r["direction"] for r in neighbors} != {"north", "south", "east", "west"}
        or any(set(r) != NEIGHBOR_KEYS for r in neighbors)):
        raise ValueError("unperceived neighbor feature")
    for k in BODY_KEYS:
        x = raw["body"][k]
        if type(x) not in (int, float) or not 0 <= x <= 100:
            raise ValueError("impossible first-person body value")
    for n in neighbors:
        dx = {"north": 0, "south": 0, "east": 1, "west": -1}[n["direction"]]
        dy = {"north": -1, "south": 1, "east": 0, "west": 0}[n["direction"]]
        if (n["x"], n["y"]) != (raw["x"]+dx, raw["y"]+dy):
            raise ValueError("forged neighbor geometry")
    if raw["inventory"]["berry_b"] < 0:
        raise ValueError("negative first-person inventory")
    return raw


def command_eligible(obs, label):
    visible_state(obs)
    if label == "MOVE_E":
        return next(n for n in obs["adjacent"] if n["direction"] == "east")["passable"]
    if label == "COLLECT_B":
        return "berry_b" in obs["current_resources"]
    raise ValueError("unregistered action in empirical model")


def deltas(b, a):
    visible_state(b)
    visible_state(a)
    return {
        "x": a["x"]-b["x"],
        "y": a["y"]-b["y"],
        "energy": round(a["body"]["energy"]-b["body"]["energy"], 8),
        "food": round(a["body"]["food"]-b["body"]["food"], 8),
        "water": round(a["body"]["water"]-b["body"]["water"], 8),
        "inventory_berry_b": a["inventory"]["berry_b"]-b["inventory"]["berry_b"],
    }


def _assert_recipe(row, cohort):
    if row["preregistered_cohort"] != cohort:
        raise ValueError("training/heldout cohort crossed")
    pos = tuple(row["position_factor_external"])
    bod = tuple(row["body_factor_external"])
    action = row["command_label"]
    phase = row["phase_factor_external"]
    hidden = row["latent_berry_effect_external_only"]
    intervention = row["hidden_intervention_external_only"]
    if action not in ACTIONS or phase not in PHASES or hidden not in LATENT:
        raise ValueError("unknown factorial action/phase/berry effect")
    if cohort == "TRAIN":
        valid = (pos in TRAIN_POS and bod in {(50.0,x,40.0) for x in TRAIN_FOOD}
                 and hidden == "benign" and intervention == "none")
    elif cohort == "NOMINAL":
        valid = (pos in TEST_POS and bod in NOMINAL_BODIES
                 and intervention == "none")
    elif cohort == "HIDDEN":
        valid = (pos in TEST_POS and bod == NOMINAL_BODIES[0]
                 and phase == 1 and hidden == "benign" and
                 intervention in INTERVENTIONS)
    elif cohort == "BOUNDARY":
        valid = (pos in TEST_POS and bod == BOUNDARY_BODY and
                 hidden == "benign" and intervention == "none")
    else:
        raise ValueError("unexpected experiment cohort")
    if not valid:
        raise ValueError("world outside preregistered factorial matrix")
    expected_id = (f"a230zo:{cohort}:x{pos[0]}y{pos[1]}:"
                   f"e{bod[0]}f{bod[1]}w{bod[2]}:"
                   f"t{phase}:{action}:B{hidden}:{intervention}")
    if row["world_id"] != expected_id:
        raise ValueError("world identity does not match external recipe")
    return pos, bod, action, phase, hidden, intervention


def validate_source_row(row, cohort):
    """Validate one detached world with its physically archived receipts."""
    pos, bod, label, phase, _, _ = _assert_recipe(row, cohort)
    expect_source = "external_train" if cohort == "TRAIN" else "previously_unseen_heldout"
    if (row["source_or_heldout"] != expect_source or
        row["action_physically_applied"] != ACTIONS[label] or
        row["actual_i0_uc_measured"] is not None or
        row["no_i0_birth_or_autonomous_step"] is not True or
        row["no_berry_ingestion"] is not True or
        row["safety_certificate"] is not None or
        row["no_oracle_or_hidden_input_to_prediction"] is not True or
        row["postdeath_lived_capture"] is not None):
        raise ValueError("physical source claimed lived cognition/UC, Oracle or safety")
    b = visible_state(row["preaction_first_person"])
    a = visible_state(row["postaction_external_only"])
    if not command_eligible(b, label):
        raise ValueError("primitive physically selected despite first-person ineligibility")
    if ((b["x"],b["y"])!=pos or
        tuple(b["body"][key] for key in ("energy", "food", "water")) != bod or
        b["body"]["integrity"]!=100.0 or
        b["inventory"]["berry_b"]!=0 or
        "berry_b" not in b["current_resources"] or
        b["is_night"] != (phase==201)):
        raise ValueError("non-first-person initial physical recipe mismatch")
    ex = row["physical_example"]
    if (set(ex)!={"state","command","observed_next_state","terminal","family"}
        or ex["command"]!=ACTIONS[label] or
        ex["state"]!=b or ex["observed_next_state"]!=a or
        ex["terminal"]!=row["physically_terminal_external_only"] or
        row["world_sealed_on_terminal"]!=ex["terminal"] or
        row["preaction_sha256"]!=digest(b) or
        row["physical_example_sha256"]!=digest(ex) or
        ex["family"]!=f"a230zo-externally-controlled-one-step-{label}"):
        raise ValueError("physical example SHA, causality, family or terminal seal falsified")
    return ex


def reconstitute_train(training):
    """Freeze 6 empirical deltas directly from original 16 source receipts."""
    if len(training)!=16:
        raise ValueError("training corpus not 16 source worlds")
    groups=defaultdict(list)
    exact={}
    identities=set()
    keys=set()
    for row in training:
        if row["world_id"] in identities:
            raise ValueError("duplicate original TRAIN world")
        identities.add(row["world_id"])
        ex=validate_source_row(row, "TRAIN")
        if ex["terminal"] is not False:
            raise ValueError("terminal observation falsely added to training")
        act=row["command_label"]
        groups[act].append(deltas(ex["state"],ex["observed_next_state"]))
        key=digest({"state":ex["state"],"command":ex["command"]})
        if key in keys:
            raise ValueError("duplicate physical input in exact model")
        keys.add(key)
        exact[row["world_id"]]=key
    if len(groups)!=2 or {k:len(v) for k,v in groups.items()} != {
        "MOVE_E":8,"COLLECT_B":8}:
        raise ValueError("unbalanced preregistered TRAIN action distribution")
    frozen={}
    for label in ACTIONS:
        observed={}
        for feature in DELTA_KEYS:
            distinct={entry[feature] for entry in groups[label]}
            observed[feature]=next(iter(distinct)) if len(distinct)==1 else None
        frozen[label]={
            "supported_empirical_deltas":observed,
            "physically_observed_training_examples":8,
            "unresolved_integrity":None,
            "unresolved_terminality":None,
            "unresolved_new_adjacency":None,
            "unresolved_food_safety":None,
            "general_safety_claim":False,
        }
    if len(identities)!=16:
        raise ValueError("training worlds miscounted")
    return frozen, keys


def forecast(frozen, obs, label):
    """No WorldBody, oracle, hidden intervention or terminal label arguments."""
    visible_state(obs)
    if label not in ACTIONS or set(frozen)!=set(ACTIONS):
        raise ValueError("unregistered action/model at prospective projection")
    row=frozen[label]
    if (row["general_safety_claim"] is not False or
        any(row[k] is not None for k in (
            "unresolved_integrity","unresolved_terminality",
            "unresolved_new_adjacency","unresolved_food_safety"))):
        raise ValueError("full safety inference attempted from partial model")
    v=row["supported_empirical_deltas"]
    if set(v)!=DELTA_KEYS:
        raise ValueError("non-observable or missing numerical model target")
    status=None
    projected=None
    if not command_eligible(obs,label):
        status="abstain_ineligible"
    elif any(v[k] is None for k in DELTA_KEYS):
        status="abstain_unstable_training"
    elif any(obs["body"][k]+v[k] <0 for k in ("energy","food","water")):
        status="abstain_clamp"
    else:
        status="empirical_partial_not_certified"
        projected={
            "x":obs["x"]+v["x"],
            "y":obs["y"]+v["y"],
            "energy":round(obs["body"]["energy"]+v["energy"],8),
            "food":round(obs["body"]["food"]+v["food"],8),
            "water":round(obs["body"]["water"]+v["water"],8),
            "inventory_berry_b":obs["inventory"]["berry_b"]+v["inventory_berry_b"],
        }
    return {
        "status":status,"estimated":projected,"integrity":None,
        "terminal":None,"next_adjacency":None,"safe":None,
    }


def independently_audit(training, frozen_record, heldout, scores, original_summary):
    """Independent certificate recomputation, no new physical world or I0."""
    frozen, trained_keys = reconstitute_train(training)
    if (set(frozen_record)!={
        "model","model_sha256","historical_firstperson_exact_equipment_sha256",
        "model_has_no_production_equipment_contract"} or
        frozen_record["model"]!=frozen or
        frozen_record["model_sha256"]!=digest(frozen) or
        frozen_record["model_has_no_production_equipment_contract"] is not True):
        raise ValueError("frozen model modified after source training")
    if len(heldout)!=104 or len(scores)!=104:
        raise ValueError("missing/extra independent heldout predictions")
    identities={r["world_id"] for r in training}
    cohorts=defaultdict(list)
    counters=defaultdict(Counter)
    twin=defaultdict(list)
    nominal_lookup={}
    for row, scored in zip(heldout, scores):
        group=row["preregistered_cohort"]
        if group not in ("NOMINAL","HIDDEN","BOUNDARY"):
            raise ValueError("non-heldout source reused as a test")
        if row["world_id"] in identities:
            raise ValueError("duplicate physical world or heldout-train leakage")
        identities.add(row["world_id"])
        source=validate_source_row(row,group)
        cohorts[group].append(row)
        first=source["state"]
        after=source["observed_next_state"]
        label=row["command_label"]
        key=digest({"state":first,"command":ACTIONS[label]})
        if key in trained_keys:
            raise ValueError("heldout exact state-command key was trained")
        p=forecast(frozen,first,label)
        if (scored["frozen_empirical_prediction"]!=p or
            scored["original_train_model_firstperson_exact_key_known"] is not False or
            scored["hidden_cause_never_in_firstperson_prediction"] is not True or
            scored["no_hazard_or_safe_inferred"] is not True):
            raise ValueError("heldout prediction invented hidden future or false safety")
        target={
            "x":after["x"], "y":after["y"],
            "energy":after["body"]["energy"],
            "food":after["body"]["food"],
            "water":after["body"]["water"],
            "inventory_berry_b":after["inventory"]["berry_b"],
        }
        matches=({k:abs(float(p["estimated"][k])-float(target[k]))<1e-8
                  for k in DELTA_KEYS} if p["estimated"] is not None else {})
        exact_status=all(matches.values()) if matches else None
        integrity_delta=round(after["body"]["integrity"]-first["body"]["integrity"],8)
        if (scored["actual_partial_target_external_only"]!=target or
            scored["component_match_external_scoring_only"]!=matches or
            scored["all_six_components_match_external_only"] is not exact_status or
            scored["physical_integrity_delta_external_only"]!=integrity_delta or
            scored["physical_terminal_external_only"] is not source["terminal"]):
            raise ValueError("heldout numeric scorer concealed actual physical error")
        cs=counters[group]
        cs["worlds"]+=1
        cs["physical_steps"]+=1
        cs["predicted"]+=p["status"]=="empirical_partial_not_certified"
        cs["all_numeric_exact"]+=exact_status is True
        cs["numeric_mismatch"]+=exact_status is False
        cs["terminal"]+=source["terminal"]
        cs["injury"]+=integrity_delta<0
        cs["abstain_clamp"]+=p["status"]=="abstain_clamp"
        if group=="NOMINAL":
            pid=(tuple(row["position_factor_external"]),
                 tuple(row["body_factor_external"]),
                 row["phase_factor_external"],label)
            twin[pid].append((row,scored))
            if (row["latent_berry_effect_external_only"]=="benign" and
                pid[1]==NOMINAL_BODIES[0] and pid[2]==1):
                nominal_lookup[(pid[0],label)]=first
        elif group=="HIDDEN":
            intervention=row["hidden_intervention_external_only"]
            hs=counters[intervention]
            hs["worlds"]+=1
            hs["terminal"]+=source["terminal"]
            hs["injury"]+=integrity_delta<0
            hs["numeric_mismatch"]+=exact_status is False
    if len(identities)!=120:
        raise ValueError("original 120-world factorial denominator corrupted")
    if {name:len(cohorts[name]) for name in ("NOMINAL","HIDDEN","BOUNDARY")} != {
        "NOMINAL":64,"HIDDEN":24,"BOUNDARY":16}:
        raise ValueError("heldout cohort factors changed")
    if len(twin)!=32 or any(len(group)!=2 for group in twin.values()):
        raise ValueError("32 latent berry B pairs missing")
    for _, pair in twin.items():
        (a,ac),(b,bc)=pair
        if ({a["latent_berry_effect_external_only"],b["latent_berry_effect_external_only"]}!=set(LATENT)
            or a["preaction_first_person"]!=b["preaction_first_person"]
            or a["postaction_external_only"]!=b["postaction_external_only"]
            or ac["frozen_empirical_prediction"]!=bc["frozen_empirical_prediction"]):
            raise ValueError("latent berry toxicity was disclosed prior to ingestion")
    hidden_matches=0
    for row in cohorts["HIDDEN"]:
        first=row["preaction_first_person"]
        nom=nominal_lookup.get((tuple(row["position_factor_external"]), row["command_label"]))
        if first!=nom:
            raise ValueError("hidden physical intervention leaked into the sensor")
        hidden_matches+=1
    for name,counts in (
        ("NOMINAL",dict(worlds=64,predicted=64,all_numeric_exact=64,terminal=0,injury=0)),
        ("HIDDEN",dict(worlds=24,predicted=24,terminal=4,injury=8,numeric_mismatch=8)),
        ("BOUNDARY",dict(worlds=16,abstain_clamp=16,predicted=0,terminal=0)),
        ("hidden_lethal_east",dict(worlds=8,terminal=4,numeric_mismatch=0)),
        ("hidden_danger_here",dict(worlds=8,injury=8,numeric_mismatch=0)),
        ("hidden_forced_action_failure",dict(worlds=8,numeric_mismatch=8,terminal=0)),
    ):
        for k,v in counts.items():
            if counters[name][k]!=v:
                raise ValueError(f"original {name}.{k} disagrees with physical receipts")
    if original_summary.get("schema") != "a230zo-partial-observable-empirical-heldout-v1":
        raise ValueError("wrong sealed original ZO schema")
    mandatory = {
        "original_physical_worlds":120,"independent_training_worlds":16,
        "nominal_heldout_worlds":64,"hidden_intervention_worlds":24,
        "clamp_boundary_worlds":16,"physical_actions_applied":120,
        "exact_fullstate_heldout_keys_known":0,"nominal_partial_predictions_emitted":64,
        "nominal_six_component_physically_exact":64,
        "hazard_numeric_mismatches":8,"hazard_hidden_motor_deaths":4,
        "hazard_hidden_integrity_injuries":8,"hazard_forced_primitive_failures":8,
        "boundary_abstentions":16,
        "nominal_hidden_berry_twins_with_identical_observations":32,
        "integrity_predictions_emitted":0,"terminality_predictions_emitted":0,
        "next_full_adjacent_state_predictions_emitted":0,
        "safety_certificates_emitted":0,"new_I0_births":0,
        "new_I0_autonomous_steps":0,"I0_UC_measured":False,
        "Stage6_fullstate_equipment_promoted":False,
        "Stage12_operator_ready_proven":False,
        "all_predictions_are_lab_empirical_not_safe":True,
        "preregistered_before_code_sha":PREREG_SHA,
        "runner_commit_sha":SOURCE_SHA,
        "training_external_source_sha256":digest(training),
        "trained_partial_model_sha256":digest(frozen),
        "all_physical_receipts_sha256":digest(training+heldout),
        "heldout_prospective_forecasts_sha256":digest(scores),
        "training_finished_before_heldout_world_creation":True,
        "no_oracle_to_i0":True,"no_mortal_i0_replay":True,
        "issue110_administratively_closed_not_scientifically_certified":True,
    }
    for key,value in mandatory.items():
        if original_summary.get(key)!=value:
            raise ValueError("original aggregate, trained model or hazard claim changed: "+key)
    if original_summary["by_cohort"]!={k:dict(v) for k,v in counters.items()}:
        raise ValueError("original breakdown concealed a cohort-level error")
    # The original runner creates all 104 physical HELDOUT worlds and calls
    # WorldBody.apply before constructing the recorded compare_forecast rows.
    # It does freeze the model before heldout world creation, but does not
    # provide pre-action timestamped per-world prediction receipts.
    return {
        "schema":"a230zp-independent-original-archive-factorized-audit-v1",
        "original_ZO_run":SOURCE_RUN,
        "original_ZO_head_sha":SOURCE_SHA,
        "original_detached_training_worlds":len(training),
        "original_heldout_worlds":len(heldout),
        "independent_total_original_worlds":len(identities),
        "original_one_step_physical_examples_independently_hashed":120,
        "train_examples_per_primitive":8,
        "heldout_exact_fullstate_keys_known":0,
        "nominal_independently_recomputed_exact_six_deltas":counters["NOMINAL"]["all_numeric_exact"],
        "nominal_denominator":counters["NOMINAL"]["worlds"],
        "nominal_latent_pair_parity_groups":len(twin),
        "all_hidden_interventions_match_nominal_preaction_observation":hidden_matches,
        "hidden_lethal_motor_transitions":counters["HIDDEN"]["terminal"],
        "hidden_integrity_damage_transitions":counters["HIDDEN"]["injury"],
        "hidden_forced_action_failures":counters["hidden_forced_action_failure"]["numeric_mismatch"],
        "heldout_body_boundary_abstentions":counters["BOUNDARY"]["abstain_clamp"],
        "heldout_unknown_terminal_forecasts":len(scores),
        "heldout_unknown_integrity_forecasts":len(scores),
        "heldout_unknown_next_adjacency_forecasts":len(scores),
        "heldout_unknown_safety_forecasts":len(scores),
        "frozen_model_sha256_reproduced":digest(frozen),
        "source_only_training_before_heldout_physics_confirmed_by_original_code":True,
        "per_heldout_prediction_receipt_created_before_WorldBody_apply_proven":False,
        "original_ZO_prediction_scoring_executed_after_heldout_physics":True,
        "independent_replay_of_WorldBody_apply":False,
        "new_physical_worlds":0,"new_physical_steps":0,
        "new_autonomous_I0_births":0,"new_autonomous_I0_steps":0,
        "real_I0_UC_measured":False,
        "safety_guaranteed":False,
        "external_model_installed_into_I0":False,
        "issue110_administratively_closed":True,
        "stage12_operator_ready":False,
        "a230_status":"PARTIELLE",
    }


def independently_check_original_runner_chronology(source_path):
    """Read (never import) the checkout's ZO runner to audit timing promises.

    Source checkout must be the pristine ZO parent of the reviewer; using the
    sealed original output hashes separately prevents reruns substituting data.
    """
    source=Path(source_path).read_text(encoding="utf-8")
    module=ast.parse(source)
    funcs=[n for n in module.body if isinstance(n,ast.FunctionDef)
           and n.name=="experiment"]
    if len(funcs)!=1:
        raise ValueError("original experimental order not statically auditable")
    statements={}
    for n in funcs[0].body:
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name):
                    statements[t.id]=n
    needed=("training_pairs","model","heldout","scores")
    if any(name not in statements for name in needed):
        raise ValueError("original experiment blocks absent for chronology check")
    t,m,h,s=(statements[name].lineno for name in needed)
    if not t<m<h<s:
        raise ValueError("unexpected source-only-model/heldout-scoring chronological structure")
    heldout_call=ast.get_source_segment(source,statements["heldout"])
    scores_call=ast.get_source_segment(source,statements["scores"])
    if "apply_one(rec)" not in heldout_call or "compare_forecast(" not in scores_call:
        raise ValueError("physical action/forecast construction not identified")
    return {
        "original_source_model_freeze_before_heldout_physics":True,
        "original_source_scorer_only_after_heldout_physics":True,
        "prephysical_per_world_prediction_receipt_issued":False,
        "methodological_strict_prospective_receipt_criterion_met":False,
    }


def execute(root311,root312,output):
    dataset=load_archives(root311,root312)
    outcome=independently_audit(*dataset)
    chronology=independently_check_original_runner_chronology(
        Path(__file__).resolve().parents[1]/"scripts"/
        "run_stage12_issue110_b_a230zo_factorized_heldout.py"
    )
    outcome.update({**chronology,
        "source_file_sha256":FILES,
        "original_Python_311_312_ZO_5_files_byte_identical":True,
        "not_a_new_physical_cohort":True,
        "not_prospective_independent_discovery":True,
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230zp-independent-original-ZO-audit.json").write_text(
        json.dumps(outcome,sort_keys=True,indent=2)+"\n",encoding="utf-8"
    )
    print("A230ZP_SUMMARY "+json.dumps({
        k:v for k,v in outcome.items() if k!="source_file_sha256"
    },sort_keys=True),flush=True)
    return outcome


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-zo-311",type=Path,required=True)
    p.add_argument("--original-zo-312",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    execute(args.original_zo_311,args.original_zo_312,args.output_dir)

if __name__=="__main__":
    main()
