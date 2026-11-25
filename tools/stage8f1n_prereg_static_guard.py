"""F1N preexposure ONLY: verify literal grid and preregistered scientific promises.

Engine-free Python stdlib. This module must NEVER create worlds, instantiate a
Mind, perform World.step or dispatch any experiment. A Git source pin and this
validator are not exposure permission; live remote no-bypass and one-shot gates
will require a separate transport and an explicit owner authorization.
"""
from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/research/studies/stage8f1-paid-microdecision"
GRID = STUDY / "STAGE8F1N_OWNED_MARGIN_NEXT_DECISION_PREEXPOSURE_GRID_2026-11-25.json"
PROTOCOL = STUDY / "STAGE8F1N_OWNED_MARGIN_NEXT_DECISION_PREEXPOSURE_2026-11-25.md"
GRID_BLOB = "c522d092cb7c1777ebb0f56c4162f61948b35653"
PROTOCOL_BLOB = "ff07a8db807bee15277052ea71e1e76321286ab9"
BASE_MAIN = "1f2566ef803a43f1904c555b865e81318506a6fb"
SCHEMA = "i3-stage8f1n-preregistered-owned-threshold-margin-next-decision-T60/v0"
CONSUMED_REF = "refs/heads/i3-stage8-f1n-heldout-consumed-once"
SEEDS = tuple(range(202611259801, 202611259849))
ROOT_IDS = tuple("N%02d" % i for i in range(1, 49))
BODY_TEMPLATES = [
    [60, 70, 36, 93, 95], [61, 69, 37, 92.5, 94.5],
    [62, 68, 38, 92, 94], [63, 67, 39, 91.5, 93.5],
    [64, 66, 40, 91, 93], [65, 65, 41, 90.5, 92.5],
]
ENGINE_PINS = {
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
}
HISTORICAL_PINS = {
    "docs/research/studies/stage8f1-paid-microdecision/"
    "STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_GRID_2026-11-23.json":
        "659b72c2c5894a0ba89995a23419d66b61436465",
    "docs/research/studies/stage8f1-paid-microdecision/"
    "STAGE8F1M_PH1_POSTHOC_THRESHOLD_COMPETITION_2026-11-24.md":
        "6d2592663058b829d0a7965ab812bafdb4fce3e4",
}
PARTS = [
    "source_t1_t4", "self_paid_t5", "self_paid_t5_sham",
    "margin_t6_t60", "margin_t6_t60_sham",
    "masked_t6_t60", "masked_t6_t60_sham",
]


def demand(ok, message):
    if not ok:
        raise ValueError("F1N PREEXPOSURE LOCK: " + message)


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def exact_blob(path: Path, required: str) -> None:
    demand(path.is_file() and git_blob(path.read_bytes()) == required,
           "frozen Git blob differs: " + str(path.relative_to(ROOT)))


def verify_grid(g: dict) -> None:
    demand(type(g) is dict and g.get("schema") == SCHEMA,
           "wrong F1N schema")
    demand(g.get("phase") == "PREEXPOSURE_ONLY_NO_F1N_WORLD_STEP"
           and g.get("preregistration_date") == "2026-11-25"
           and g.get("source_baseline_main") == BASE_MAIN
           and g.get("source_genome") ==
               "midpoint() (one fixed genotype, NOT 48 independent genotypes)",
           "incorrect preexposure source or cohort identity")
    demand(g.get("reference_engine_git_blobs") == ENGINE_PINS,
           "reference F1J/P1.3 world/body/genome drift")
    demand(g.get("historical_science_reference", {}).get("f1m_consumed_commit")
           == "f6e213ca197c432b03907c3d8999ddf10bcac809"
           and g["historical_science_reference"]["f1m_grid_git_blob"]
           == "659b72c2c5894a0ba89995a23419d66b61436465"
           and g["historical_science_reference"]["f1m_ph1_json_sha256"]
           == "ed4adcbef9b93527c74f87de67de412e1e377bae2933ad910f03148bd455ff23",
           "F1M/PH1 historical precedence altered")
    demand(g.get("world") == {"width":3, "height":3, "spawn":[1,1],
                              "laws":"BodyLaws() i3-body-laws-v2", "changes":[]}
           and g.get("body_order") ==
               ["energy", "food", "water", "integrity", "vigilance"],
           "world or body protocol altered")
    demand(g.get("body_templates") == BODY_TEMPLATES,
           "literal six bodily templates changed")
    ecologies = g.get("ecologies")
    demand(type(ecologies) is list and len(ecologies) == 8
           and len({e["id"] for e in ecologies}) == 8,
           "must have exactly eight fixed literal ecologies")
    expected_factors = {
        (distance, renewal, nutrition)
        for distance in ("adjacent", "diagonal")
        for renewal in ("finite", "renewing")
        for nutrition in ("safe", "bitter")
    }
    factors = set()
    for e in ecologies:
        f = e["factors"]
        combo = (f["water_access"], f["water_renewal"], f["food_integrity"])
        factors.add(combo)
        distance, renewal, nutrition = combo
        demand(e["id"] == "n_water_%s_%s_food_%s" % combo
               and e["f1m_precedent_ecology"] ==
                   "m_water_%s_%s_food_%s" % combo
               and e["token"] == "f1n-%s-%s-%s" % combo,
               "ecology/token/source link drift")
        demand(e["water"] == ([1, 0] if distance == "adjacent" else [2, 0])
               and e["food"] == [0, 2]
               and e["water_gain"] == 22
               and e["water_stock"] == 2
               and e["water_max_stock"] == 2
               and e["water_restock_every"] == (0 if renewal == "finite" else 7)
               and e["food_quantity"] == 2
               and e["food_max_quantity"] == 2
               and e["food_restock_every"] == 0
               and e["food_gain"] == (22 if nutrition == "safe" else 28)
               and e["integrity_delta"] == (1 if nutrition == "safe" else -1),
               "literal native ecology law parameters changed")
    demand(factors == expected_factors,
           "factorial ecologies missing or duplicated")
    origins = g.get("origins")
    demand(type(origins) is list and len(origins) == 48
           and g.get("roots_declared") == 48
           and tuple(o["id"] for o in origins) == ROOT_IDS
           and tuple(o["seed"] for o in origins) == SEEDS,
           "scientific source identities/seeds/order changed")
    demand(all(o == {"id":ROOT_IDS[i], "ecology":ecologies[i//6]["id"],
                     "seed":SEEDS[i], "body":BODY_TEMPLATES[i%6]}
               for i, o in enumerate(origins)),
           "preallocated exact world/body/seed crossing changed")
    forbidden = set(range(202611229501, 202611229609))
    forbidden |= set(range(202611239601, 202611239619))
    forbidden |= set(range(202611239701, 202611239733))
    demand(not (set(SEEDS) & forbidden),
           "collision with known previous scientific or DEV allocation")
    demand(g.get("ecological_family", {}).get("no_posthoc_reallocation") is True,
           "posthoc ecology allocation allowed")
    m = g.get("paid_self_confidence_margin")
    demand(type(m) is dict
           and m["recording_tick"] == 5 and m["replay_tick"] == 6
           and m["record_after_actual_native_T5_motor_and_paid_learning"] is True
           and m["record_after_actual_paid_f1j_final_round"] is True
           and m["real_record_cost"]["memory_items"] == 1
           and m["real_read_cost_T6"]["memory_items"] == 1
           and m["intervention_gain_kappa"] == 0.5
           and m["only_tick_6_readout"] is True
           and m["final_relative_surplus_formula"] ==
               "s(o)=(A5(o)-theta5(o))/theta5(o)"
           and m["confidence_formula"] ==
               "q=clip(s(winner)-max_other_s,0.0,1.0) iff winner actually crosses theta AND action admitted/executed; else q=0.0"
           and m["actual_threshold_T6"] ==
               "theta_margin(o)=theta_base(o)*(1-0.5*q) iff o==own T5 winner key and key scored at T6; otherwise theta_base(o)",
           "funded own threshold-margin memory formula or readout changed")
    demand(g.get("arms") == ["margin", "masked"]
           and g.get("sham_arms") == ["margin_sham", "masked_sham"]
           and g.get("native_original_parts_per_root") == PARTS
           and g.get("objective_end_tick") == 60,
           "cohort branches or original receipts changed")
    motor = g.get("primary_motor", {})
    survival = g.get("adaptive_survival", {})
    body = g.get("secondary_body", {})
    demand(motor.get("success_threshold") ==
               {"min_distinct_origins":8, "min_ecologies":3}
           and motor.get("positive_verdict") ==
               "REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT"
           and survival.get("success_threshold") ==
               {"min_positive_origins":8, "min_ecologies":3,
                "max_negative_pairs":0}
           and survival.get("positive_verdict") ==
               "LOCAL_T60_OWN_MARGIN_SURVIVAL_ADAPTIVE_ADVANTAGE"
           and survival.get("independent_of_motor_success") is True
           and body.get("positive_body_only_threshold") ==
               {"min_strict_pareto_roots":12, "min_ecologies":3,
                "max_reverse_dominance":0}
           and body.get("forbidden_to_promote_to_survival") is True,
           "registered motor/survival/body decision threshold changed")
    integrity = g.get("scientific_integrity", {})
    demand(integrity.get("exact_consumed_ref") == CONSUMED_REF
           and integrity.get("at_least_two_dev_disjoint_same_source_tree_rehearsals") is True
           and integrity.get("all_48_sources_eligible_and_paid_required") is True
           and integrity.get("all_48_t6_cost_pairs_equal_required") is True
           and integrity.get("all_48_t5_shams_and_96_followup_shams_neutral_required") is True
           and integrity.get("exactly_336_original_gzip_parts_if_complete") is True
           and integrity.get("owner_explicit_new_F1N_exposure_permission_required") is True,
           "one-shot remote protections/funding gates changed")
    demand(g.get("design_exposure_state") == {
        "scientific_exposure_authorized": False,
        "scientific_workflow_dispatch_allowed": False,
        "producer_implemented": False,
        "birth_steps_performed": 0,
        "consumed_ref_must_be_absent": True,
        "results_available": False,
    }, "no-scientific-exposure hold silently removed")


def check_files() -> None:
    exact_blob(GRID, GRID_BLOB)
    exact_blob(PROTOCOL, PROTOCOL_BLOB)
    for path, expected in {**ENGINE_PINS, **HISTORICAL_PINS}.items():
        exact_blob(ROOT / path, expected)
    verify_grid(json.loads(GRID.read_bytes()))


def main() -> None:
    check_files()
    print(json.dumps({
        "status": "F1N_PREREG_STATIC_PASS_NO_EXPOSURE",
        "source_baseline_main": BASE_MAIN,
        "grid_git_blob": GRID_BLOB,
        "protocol_git_blob": PROTOCOL_BLOB,
        "independent_origins": 48,
        "literal_ecologies": 8,
        "preallocated_one_to_one_t6_contrasts": 48,
        "native_science_births_created": 0,
        "native_science_world_steps": 0,
        "scientific_exposure_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
