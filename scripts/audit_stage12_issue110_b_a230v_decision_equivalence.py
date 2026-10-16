"""A2.30-V: sealed, read-only identifiability audit across S/T sources.

This is a DERIVED logical certificate about ONE experimentally fixed action
choice (commit to berry_a collect/eat vs abstain). It is NOT a new test-world
campaign, a general I0 policy, an estimator of real-world fatality frequency
or a claim that alternative plans are physically impossible.

The equivalence classes are determined SOLELY from the full accessible
predecision SimulationState. Latent names and outcomes enter ONLY the
external retrospective scoring, never the decision input.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess

HASHES = {
    "observable": {
        "a230s-summary.json": "b60935224306279f3b2ac74ddf88407dd95b56aeb1760cdc36c992e488464d57",
        "a230s-worlds.json": "8631839f8c9e253601b1b9f203d2fabf55672eefd2b7b17f330b1a5b5f8802bf",
        "a230s-pairs.json": "8331090bed8c56d8c3a7e6b85f76bbf99a9c11380a1b882f37dae06c7d95370b",
    },
    "food": {
        "a230t-summary.json": "37885824412243b9186d51a29e2e82799c481e8b20d4eab1b5381a3966534f62",
        "a230t-worlds.json": "c418b9aef5b86d67e599520ea1e1620c2a0970f11d9253b75429b38c91eacada",
        "a230t-paired.json": "58c042d323e82e6772f53f58cbc8af5631250f03e155ccdacd94d46fd81b6dde",
    },
    "causal": {
        "a230s-summary.json": "969de41c916df3210f8c9e0c1f033edc769bd49536f7fd20b14eaee03deee048",
        "a230s-acted-worlds.json": "b905535a67c72b912e0b384dbc7e189e8446ee4954631e559928bd922edd0e36",
        "a230s-passive-worlds.json": "2863bb4e4d820cb3cc9b7492a0264e23f888e6b12e6225313f3c40766f8c27e6",
    },
}
EXPECTED_VARIANTS = {"benign", "toxin_7", "toxin_30", "toxin_100", "gain_zero"}
EXPECTED_SOURCE_RUNS = {
    "observable": 38740205272, "food": 38741620906,
    "causal": 38740664255,
}


def state_bytes(state):
    """Data-only canonicalization; explicit no oracle/hidden features."""
    allowed = {
        "adjacent", "body", "current_resources", "current_water_source",
        "inventory", "is_night", "known_shelter_here", "schema_version",
        "x", "y",
    }
    if type(state) is not dict or set(state) != allowed:
        raise ValueError("observation contains missing, future or hidden fields")
    if set(state["body"]) != {"energy", "food", "water", "integrity"}:
        raise ValueError("not a complete first-person bodily state")
    return json.dumps(state, sort_keys=True, separators=(",", ":"))


def read_sealed_files(root, category):
    loaded = {}
    for filename, digest in HASHES[category].items():
        files = list(Path(root).rglob(filename))
        if len(files) != 1:
            raise ValueError("sealed archive source missing or ambiguous: " + filename)
        raw = files[0].read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError("sealed source SHA-256 mismatch: " + filename)
        loaded[filename] = raw
    return loaded


def load_pair(category, py311, py312):
    left = read_sealed_files(py311, category)
    right = read_sealed_files(py312, category)
    if left != right:
        raise ValueError("original Python 3.11 and 3.12 archives differ")
    return {key: json.loads(value) for key, value in left.items()}


def audit_food(worlds, pairs, summary):
    if (len(worlds) != 40 or len(pairs) != 20
        or summary.get("schema") != "a230t-shadow-food-planning-v1"
        or summary.get("new_independent_lab_worlds") != 40
        or summary.get("new_lab_physical_steps") != 132
        or summary.get("shadow_safety_certificates") != 0
        or summary.get("new_i0_births") != 0
        or summary.get("new_autonomous_i0_steps") != 0
        or summary.get("shadow_does_not_command_physics") is not True):
        raise ValueError("invalid historical food physical/cohort protocol")
    classes = defaultdict(list)
    indexed = {}
    for row in worlds:
        identity = row["id"]
        if identity in indexed:
            raise ValueError("duplicated physical world identifier")
        indexed[identity] = row
        arm = row["arm"]
        latent = row["latent_external_only"]
        if arm not in ("no_wait", "wait_first") or latent not in EXPECTED_VARIANTS:
            raise ValueError("unexpected physical context or hidden variant")
        if row["starting_food"] not in (35.0, 45.0):
            raise ValueError("unexpected food initial condition")
        if tuple(row["starting_position"]) not in ((5, 5), (7, 7)):
            raise ValueError("unexpected initial physical position")
        expected_id = (
            f"a230t:{arm}:{latent}:food{int(row['starting_food'])}:"
            f"x{row['starting_position'][0]}y{row['starting_position'][1]}"
        )
        if identity != expected_id:
            raise ValueError("physical world identity does not match its fixture")
        snapshot = state_bytes(row["decision_stage3_state"])
        initial = state_bytes(row["preprobe_stage3_state"])
        forecast = row["shadow_forecast_precommitted"]
        if (state_bytes(forecast["input_stage3_state"]) != snapshot
            or forecast["forecast_time_t_monde"] !=
                (1 if arm == "no_wait" else 2)
            or forecast["certifies_safe"] is not False
            or forecast["optimistic_goal_exists"] is not True
            or forecast["all_observed_branches_survive_and_meet_goal"] is not False
            or forecast["risk_label"] != "observed_terminal_possible"
            or forecast["shadow_risk_veto"] is not True
            or row["no_command_emitted_to_i0"] is not True
            or not isinstance(row["physical_operations_not_chosen_by_shadow"], list)
            or row["no_subj_agency_claim"] is not True):
            raise ValueError("future leakage, false safety or uncommitted shadow")
        if arm == "no_wait" and snapshot != initial:
            raise ValueError("no-wait predecision state changed without intervention")
        if row["decision_food"] != row["decision_stage3_state"]["body"]["food"]:
            raise ValueError("food decision body mismatches physical capture")
        if row["physical_food_goal_with_survival_external"] is not (
            row["physically_alive_after_ingestion"] and
            row["actual_food_gain_after_ingestion_external"] >= 5.0
        ):
            raise ValueError("food goal mislabeled after physical consequence")
        if not row["physically_alive_after_ingestion"]:
            if (row["potential_lived_post_ingestion_if_survivor"] is not None
                or row["terminal_step_external_only"] is None):
                raise ValueError("terminal result converted to subjective living memory")
        elif row["terminal_step_external_only"] is not None:
            raise ValueError("nonterminal world has a fabricated death")
        operations = row["physical_operations_not_chosen_by_shadow"]
        if (len(operations) != row["real_physical_steps"]
            or len(operations) not in (2, 3, 4)
            or [op["t_monde"] for op in operations] != list(
                range(1, len(operations) + 1)
            )
            or operations[0]["command"]["primitive"] != (
                "collecter" if arm == "no_wait" else "attendre"
            )
            or (arm == "wait_first" and
                operations[1]["command"]["primitive"] != "collecter")
            or operations[-1]["terminal_external_only"] is not (
                not row["physically_alive_after_ingestion"]
            )
            or any(op["terminal_external_only"] for op in operations[:-1])
            or operations[-1]["physical_after"] is None):
            raise ValueError("laboratory physical commands or terminal chain altered")
        if not isinstance(row["physical_config_sha256"], str) or len(
            row["physical_config_sha256"]) != 64:
            raise ValueError("physical configuration provenance missing")
        # This is the ONLY policy feature. Do NOT include latent labels,
        # physical consequence, model's after-state or lab configuration.
        classes[(arm, snapshot)].append(row)

    if len(classes) != 8 or any(len(v) != 5 for v in classes.values()):
        raise ValueError("incorrect observational equivalence partition")
    if len({k[1] for k in classes}) != 8:
        raise ValueError("different arms are wrongly treated as one visible input")
    group_rows = []
    for (arm, snapshot), rows in sorted(classes.items()):
        variants = {r["latent_external_only"] for r in rows}
        if variants != EXPECTED_VARIANTS:
            raise ValueError("latent variant missing or duplicated inside class")
        deaths = sum(not r["physically_alive_after_ingestion"] for r in rows)
        successes = sum(r["physical_food_goal_with_survival_external"] for r in rows)
        insufficient = len(rows) - deaths - successes
        if (deaths, successes, insufficient) != (1, 3, 1):
            raise ValueError("observational class lacks expected conflicting outcomes")
        # The factual outcomes are SCORING LABELS at the bench, not features.
        group_rows.append({
            "arm": arm,
            "visible_state_sha256": sha256(snapshot.encode()).hexdigest(),
            "observable_worlds": len(rows),
            "latent_external_variants_only_for_bench": sorted(variants),
            "lab_terminal_worlds_if_commit": deaths,
            "lab_food_goal_with_survival_if_commit": successes,
            "lab_insufficient_if_commit": insufficient,
            "deterministic_policy_decision_cannot_distinguish_variants": True,
            "at_least_one_benign_and_one_terminal_outcome": True,
            "uc_cost_measured": False,
        })

    observed_pairs = set()
    total_extra_physical = {"energy": 0.0, "food": 0.0, "water": 0.0}
    for pair in pairs:
        key = (pair["latent_external_only"],pair["food"],tuple(pair["coords"]))
        if key in observed_pairs:
            raise ValueError("duplicated OFF/ON experimental pair")
        observed_pairs.add(key)
        a = indexed.get(pair["no_wait_id"])
        b = indexed.get(pair["wait_first_id"])
        if (a is None or b is None or a["arm"] != "no_wait"
            or b["arm"] != "wait_first"
            or a["latent_external_only"] != b["latent_external_only"]
            or a["starting_food"] != b["starting_food"]
            or a["starting_position"] != b["starting_position"]
            or pair["terminal_in_both_arms"] is not (
                not a["physically_alive_after_ingestion"]
                and not b["physically_alive_after_ingestion"]
            )
            or pair["same_initial_perception"] is not True
            or pair["same_observed_branch_risk"] is not True
            or pair["physical_food_goal_no_wait"] is not
                a["physical_food_goal_with_survival_external"]
            or pair["physical_food_goal_wait_first"] is not
                b["physical_food_goal_with_survival_external"]):
            raise ValueError("OFF/ON shadow comparison corrupted")
        physical_cost = {
            k: (b["decision_stage3_state"]["body"][k] -
                a["decision_stage3_state"]["body"][k])
            for k in total_extra_physical
        }
        if (abs(physical_cost["energy"] + 0.5) > 1e-8 or
            abs(physical_cost["food"] + 0.5) > 1e-8 or
            abs(physical_cost["water"] + 0.2) > 1e-8 or
            abs(pair["food_cost_waiting_extra"] + 0.5) > 1e-8):
            raise ValueError("time-cost of observation probe misstated")
        for k, value in physical_cost.items():
            total_extra_physical[k] += value
    if len(observed_pairs) != 20:
        raise ValueError("not 20 independent paired interventions")
    total_steps = sum(r["real_physical_steps"] for r in worlds)
    if total_steps != 132:
        raise ValueError("wrong physical action count in original study")

    # Exhaustively enumerate ALL policies on eight observation classes.
    # Choices are only commit fixed food prefix (1) or abstain (0).
    policies = []
    for choices in product((False, True), repeat=len(group_rows)):
        committed = [row for choose,row in zip(choices,group_rows) if choose]
        policies.append({
            "committed_observable_classes": len(committed),
            "terminal_worlds_if_commit": sum(
                c["lab_terminal_worlds_if_commit"] for c in committed
            ),
            "goal_worlds_if_commit": sum(
                c["lab_food_goal_with_survival_if_commit"] for c in committed
            ),
            "insufficient_worlds_if_commit": sum(
                c["lab_insufficient_if_commit"] for c in committed
            ),
        })
    zero_terminal = [p for p in policies if p["terminal_worlds_if_commit"] == 0]
    with_success = [
        p for p in zero_terminal if p["goal_worlds_if_commit"] > 0
    ]
    if (len(policies) != 256 or len(zero_terminal) != 1
        or with_success or max(p["goal_worlds_if_commit"] for p in policies) != 24):
        raise ValueError("finite conditional safety tradeoff contradiction")
    counts = Counter((p["committed_observable_classes"],
                      p["terminal_worlds_if_commit"],
                      p["goal_worlds_if_commit"]) for p in policies)
    frontier = [{
        "committed_classes":k[0], "terminal_worlds":k[1],
        "successful_food_worlds":k[2], "deterministic_policies":v,
    } for k,v in sorted(counts.items())]
    return {
        "original_physical_worlds":40,
        "original_physical_steps":total_steps,
        "observational_equivalence_classes":len(group_rows),
        "worlds_per_class":5,
        "contradictory_success_and_terminal_classes":sum(
            x["at_least_one_benign_and_one_terminal_outcome"]
            for x in group_rows),
        "tested_deterministic_policies":len(policies),
        "policies_with_zero_terminal_worlds":len(zero_terminal),
        "policies_with_zero_terminal_and_positive_food_goal":len(with_success),
        "max_food_goal_worlds_if_zero_terminal":0,
        "max_food_goal_worlds_if_all_classes_committed":24,
        "terminal_worlds_if_all_classes_committed":8,
        "insufficient_worlds_if_all_classes_committed":8,
        "group_details":group_rows,
        "conditional_decision_frontier":frontier,
        "wait_predecision_total_physical_cost_across_20_pairs":
            {k:round(v,8) for k,v in total_extra_physical.items()},
        "preexposure_wait_separated_hidden_food_variants":False,
        "latent_physics_ever_used_in_decision_features":False,
        "calibrated_death_probability":None,
        "all_other_policies_or_food_resources_excluded_from_claim":True,
        "any_i0_command_or_autonomous_step_executed_by_audit":False,
    }


def audit_observable(worlds,pairs,summary):
    if (len(worlds)!=36 or len(pairs)!=36
        or summary.get("schema")!="a230s-accessible-probes-physical-v1"
        or summary.get("independent_lab_worlds")!=36
        or summary.get("physical_lab_steps")!=104
        or summary.get("external_terminals")!=8
        or summary.get("paired_comparisons")!=36
        or summary.get("jointly_lived_differences")!=20
        or summary.get("jointly_lived_nonidentifications")!=16
        or summary.get("food_preexposure_distinctions")!=0
        or summary.get("move_preexposure_distinctions")!=0
        or summary.get("terminal_postcapture_considered_lived") is not False
        or summary.get("uc_cost_evaluated") is not False):
        raise ValueError("independent S-observable source changed")
    index={}
    for w in worlds:
        if w["id"] in index or w["postterminal_lived_capture_count"]!=0:
            raise ValueError("duplicate world or terminal wrongly experienced")
        index[w["id"]]=w
    family_counts=Counter()
    seen_pairs=set()
    lived_count=0
    for p in pairs:
        name=p["family"]
        family_counts[name]+=1
        if name not in ("FOOD","MOVE","DECAY") or len(p["worlds"])!=2:
            raise ValueError("unpreregistered first-person pair")
        pair_key=tuple(sorted(p["worlds"]))
        if pair_key in seen_pairs or any(v not in index for v in pair_key):
            raise ValueError("duplicate/missing pair source")
        seen_pairs.add(pair_key)
        if p["discrimination_before_exposure"] is not False:
            raise ValueError("sensory exposure was moved backward in time")
        if p["first_mutually_lived_difference"] is not None:
            lived_count+=1
    if family_counts!={"FOOD":12,"MOVE":12,"DECAY":12} or lived_count!=20:
        raise ValueError("S-observable pair groups differ")
    return {
        "original_worlds":36,
        "original_physical_steps":104,
        "external_terminals":8,
        "paired_accessible_histories":36,
        "jointly_lived_distinguishable_pairs":20,
        "jointly_lived_nonidentifications":16,
        "food_and_movement_preexposure_known_distinctions":0,
        "uc_measured":False,
    }


def audit_causal(worlds,passive,summary):
    if (len(worlds)!=64 or len(passive)!=8
        or summary.get("schema")!="a230s-firstperson-controlled-information-v1"
        or summary.get("acted_detached_worlds")!=64
        or summary.get("passive_observation_only_worlds")!=8
        or summary.get("actual_lab_physical_steps")!=196
        or summary.get("physically_terminal_worlds")!={"food":8,"movement":16}
        or summary.get("shadow_stage6_queries")!=56
        or summary.get("shadow_first_step_known")!=0
        or summary.get("shadow_no_predictable_first_step")!=56
        or summary.get("new_I0_births")!=0
        or summary.get("new_I0_autonomous_steps")!=0):
        raise ValueError("independent S-causal source changed")
    seen=set()
    roots=0
    steps=0
    for world in worlds:
        if world["id"] in seen:
            raise ValueError("duplicated causal world identifier")
        seen.add(world["id"])
        steps+=world["physical_step_count"]
        if world["oracle_information_in_cognitive_search"]:
            raise ValueError("oracle state leaked into a shadow query")
        for query in world["shadow_food"]:
            root=query["stage6_diagnostic"]
            if (root["status"]!="incomplete_model"
                or root["root_available_edges"]!=0
                or root["root_model_diagnostic"]!="no_predictable_first_step"
                or query["no_shadow_command_dispatched"] is not True):
                raise ValueError("known first step or dispatched shadow command")
            roots+=1
    if roots!=56 or steps!=196:
        raise ValueError("S-causal per-world physical/search receipts disagree")
    return {
        "independent_protocol_acted_worlds":64,
        "passive_observations_only_worlds":8,
        "independent_protocol_physical_steps":196,
        "real_stage6_shadow_queries_without_predictable_root":roots,
        "causal_confounded_first_ingestion_pairs_from_source":
            summary["comparison"]["paired_food_after_ingestion_identical_accessible_output"],
        "causal_identification_of_food_harm_by_i0_established":False,
    }


def audit_all(sobs,food,causal):
    food_result=audit_food(
        food["a230t-worlds.json"],food["a230t-paired.json"],
        food["a230t-summary.json"],
    )
    observable_result=audit_observable(
        sobs["a230s-worlds.json"],sobs["a230s-pairs.json"],
        sobs["a230s-summary.json"],
    )
    causal_result=audit_causal(
        causal["a230s-acted-worlds.json"],causal["a230s-passive-worlds.json"],
        causal["a230s-summary.json"],
    )
    return {
        "schema":"a230v-bounded-observation-equivalence-certificate-v1",
        "evidence_is_known_posthoc_not_preregistered_new_cohort":True,
        "new_physical_worlds":0,
        "new_physical_steps":0,
        "new_i0_births":0,
        "new_i0_autonomous_steps":0,
        "policy_domain":"commit_experimental_food_prefix_vs_abstain_only",
        "food_decision":food_result,
        "observable_probes_separate_original_study":observable_result,
        "causal_shadow_separate_original_study":causal_result,
        "sources_are_three_disjoint_protocols_not_replications":True,
        "oracle_or_bench_feedback_to_i0":False,
        "uc_policy_inference_supported":False,
        "safety_of_alternative_food_plans_proven":False,
        "stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
        "cognitive_deployment":"NO-GO",
    }


def execute(observable_a,observable_b,food_a,food_b,causal_a,causal_b,output):
    sobs=load_pair("observable",observable_a,observable_b)
    food=load_pair("food",food_a,food_b)
    causal=load_pair("causal",causal_a,causal_b)
    summary=audit_all(sobs,food,causal)
    summary.update({
        "run_ids_known_before_audit":EXPECTED_SOURCE_RUNS,
        "original_json_digests":HASHES,
        "both_python_source_archives_equal_per_protocol":True,
        "analysis_git_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230v-certificate.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",
    )
    print("A230V_CERTIFICATE "+json.dumps({
        "eight_visible_classes":summary["food_decision"]["observational_equivalence_classes"],
        "tested_policies":summary["food_decision"]["tested_deterministic_policies"],
        "safe_and_success_policies":
            summary["food_decision"]["policies_with_zero_terminal_and_positive_food_goal"],
        "wait_cost":
            summary["food_decision"]["wait_predecision_total_physical_cost_across_20_pairs"],
        "s_observable_preexposure_distinctions":
            summary["observable_probes_separate_original_study"]["food_and_movement_preexposure_known_distinctions"],
        "stage6_unknown_roots":
            summary["causal_shadow_separate_original_study"]["real_stage6_shadow_queries_without_predictable_root"],
        "new_scientific_worlds":0,
        "cognitive_deployment":"NO-GO",
    },sort_keys=True),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser()
    for name in ("observable_311","observable_312","food_311","food_312",
                 "causal_311","causal_312"):
        parser.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    execute(
        args.observable_311,args.observable_312,
        args.food_311,args.food_312,
        args.causal_311,args.causal_312,args.output_dir,
    )


if __name__=="__main__":
    main()
