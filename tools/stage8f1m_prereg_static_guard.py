"""F1M frozen preregistration static guard: NO native engine, no heldout births.

This only checks immutable Git blob contents and literal prospective conditions.
It cannot grant exposure authorization, verify remote GitHub rulesets,
or replace an independent cold audit of future original evidence.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha1
import json
from pathlib import Path

DIR = Path("docs/research/studies/stage8f1-paid-microdecision")
GRID = DIR / "STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_GRID_2026-11-23.json"
PROTOCOL = DIR / "STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_PREEXPOSURE_2026-11-23.md"
GRID_BLOB = "659b72c2c5894a0ba89995a23419d66b61436465"
PROTOCOL_BLOB = "342a6794ecd26789da82940c2d1f10e427e3979c"
BASE_MAIN = "9c40f01684f5e69c893d765aa41cad1af1d33532"
SCHEMA = "i3-stage8f1m-preregistered-independent-residual-motor-adaptive-T60/v0"
SEEDS = tuple(range(202611239701, 202611239733))
PREVIOUS_L = set(range(202611229501, 202611229533))
PREVIOUS_DEV_L = set(range(202611229601, 202611229609))
PREVIOUS_DEV_M = set(range(202611239601, 202611239609))
SOURCE_BLOBS = {
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
    "tools/stage8f1h_prospective_native_body_value.py":
        "02c5ece502729e3fa341f17cfa9cdc03e8c50bf4",
    "tools/stage8f1c_paid_postaction_learning.py":
        "c3d00fe078cac0ad9487ac39c2c8c7e081f32313",
    "tools/stage8f1d_next_decision_retention.py":
        "19f10a02b73759b52856e177ac3731f5826281c6",
}
BODY_STATES = [
    [60, 70, 36, 93, 95],
    [61, 69, 37, 92.5, 94.5],
    [62, 68, 38, 92, 94],
    [63, 67, 39, 91.5, 93.5],
]


def blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def require(value, reason):
    if not value:
        raise AssertionError("F1M_PREREG_NO_EXPOSURE: " + reason)


def expected_ecologies():
    out = []
    for access in ("adjacent", "diagonal"):
        for renewal in ("finite", "renewing"):
            for effect in ("safe", "bitter"):
                out.append({
                    "id": f"m_water_{access}_{renewal}_food_{effect}",
                    "factors": {
                        "water_access": access,
                        "water_renewal": renewal,
                        "food_integrity": effect,
                    },
                    "water": [1, 0] if access == "adjacent" else [2, 0],
                    "water_gain": 22,
                    "water_stock": 3,
                    "water_max_stock": 3,
                    "water_restock_every": 0 if renewal == "finite" else 5,
                    "food": [0, 2],
                    "token": f"f1m-{access}-{renewal}-{effect}",
                    "food_gain": 22 if effect == "safe" else 28,
                    "integrity_delta": 1.0 if effect == "safe" else -1.0,
                    "food_quantity": 3,
                    "food_max_quantity": 3,
                    "food_restock_every": 0,
                })
    return out


def validate_grid(data):
    require(data.get("schema") == SCHEMA, "schema drift")
    require(data.get("phase") == "PREEXPOSURE_ONLY_NO_WORLD_STEP" and
            data.get("scientific_exposure_authorized") is False and
            data.get("scientific_workflow_dispatch_allowed") is False and
            data.get("no_scientific_seed_in_dev_or_validation") is True and
            data.get("all_historical_or_development_seeds_forbidden_in_M_science") is True,
            "scientific exposure or seed validation inadvertently permitted")
    require(data.get("source_baseline_main") == BASE_MAIN and
            data.get("source_policy") ==
                "tools.stage8f1j_fixed_round_paid_competition.F1JFixedRoundMind" and
            data.get("source_genome") == "midpoint()" and
            data.get("reference_engine_git_blobs") == SOURCE_BLOBS,
            "reference implementation or genome changed")
    require(data.get("world") == {
            "width": 3, "height": 3, "spawn": [1, 1],
            "laws": "BodyLaws() i3-body-laws-v2", "changes": []},
            "world/birth/physiology changed")
    require(data.get("body_order") ==
            ["energy", "food", "water", "integrity", "vigilance"],
            "body order changed")
    require(data.get("factors") == {
            "water_access": ["adjacent", "diagonal"],
            "water_renewal": ["finite", "renewing"],
            "food_integrity": ["safe", "bitter"],
            "full_factorial": True},
            "science ecology design changed")
    ecologies = expected_ecologies()
    require(data.get("ecologies") == ecologies and
            data.get("ecologies_count") == 8 and
            data.get("origins_per_ecology") == 4, "literal prospective ecologies changed")
    roots = [
        {"id": f"M{index * 4 + j + 1:02d}",
         "ecology": eco["id"],
         "seed": SEEDS[index * 4 + j],
         "body": BODY_STATES[j]}
        for index, eco in enumerate(ecologies)
        for j in range(4)
    ]
    require(data.get("origins") == roots and
            data.get("independent_origins_count") == 32,
            "literal independent science origins changed")
    ids = [r["id"] for r in roots]
    seeds = [r["seed"] for r in roots]
    require(ids == [f"M{i:02d}" for i in range(1, 33)] and
            len(set(ids)) == len(set(seeds)) == 32 and
            not set(seeds) & (PREVIOUS_L | PREVIOUS_DEV_L | PREVIOUS_DEV_M) and
            set(Counter(r["ecology"] for r in roots).values()) == {4},
            "duplicate or recycled root/seed or imbalance")

    require(data.get("personal_history_ticks") == 4 and
            data.get("owned_t1_mean_anchor_tick") == 1 and
            data.get("temporary_content_readout_tick") == 5 and
            data.get("residual_intervention_after_tick") == 5 and
            data.get("residual_intervention_before_tick") == 6 and
            data.get("comparison_tick") == 6 and
            data.get("final_tick") == 60,
            "cognitive intervention/timing changed")
    require(data.get("memory_contents") ==
            ["recent_owned_T4_means", "stale_owned_T1_means"] and
            data.get("mediator_modes") == ["carry_acc", "zero_values_same_acc_keys"] and
            data.get("arms") == ["recent/carry", "recent/zero", "stale/carry", "stale/zero"] and
            data.get("controls") == [
                "recent_full_sham_T5", "sham_each_of_four_native_continuations"] and
            data.get("no_mandated_motor") is True and
            data.get("no_fictitious_work_padding") is True,
            "readout/mediator arms or autonomy changed")

    motor = data.get("motor_estimand", {})
    adaptive = data.get("adaptive_estimand", {})
    pareto = adaptive.get("secondary_body_pareto", {})
    require(motor.get("distinct_origin_min_success") == 6 and
            motor.get("minimum_changed_t6_motor_pairs") == 6 and
            motor.get("distinct_ecology_min_success") == 3 and
            motor.get("score_winner_changed_only_does_not_count") is True and
            motor.get("no_posthoc_subgroup_filtering") is True,
            "motor threshold or motor definition changed")
    require(adaptive.get("positive_survival_distinct_origins_min") == 6 and
            adaptive.get("positive_survival_ecologies_min") == 3 and
            adaptive.get("maximum_negative_survival_pairs") == 0 and
            adaptive.get("same_root_multiple_positive_content_pairs_count_once") is True and
            adaptive.get("no_body_only_claim_of_adaptive_survival") is True,
            "survival threshold/independence changed")
    require(pareto.get("only_when_all_survival_deltas_zero") is True and
            pareto.get("positive_five_channel_dominance_distinct_origins_min") == 8 and
            pareto.get("positive_five_channel_dominance_ecologies_min") == 3 and
            pareto.get("reverse_dominance_pairs_max") == 0 and
            pareto.get("min_abs_channel_improvement") == 1e-9 and
            pareto.get("mixed_tradeoffs_not_success") is True and
            pareto.get("verdict") == "BODY_PARETO_ONLY_NOT_SURVIVAL_ADAPTATION",
            "body-only measure secretly promoted to adaptive")
    require(len(data.get("hard_gates", [])) == 9 and
            data.get("scientific_consumption_ref") ==
            "refs/heads/i3-stage8-f1m-heldout-consumed-once" and
            data.get("science_original_release_tag") ==
            "i3-stage8f1m-t60-raw-heldout-once" and
            data.get("science_cold_release_tag") ==
            "i3-stage8f1m-t60-cold-heldout-once" and
            data.get("historical_results_unchanged", {}).get("F1L") ==
            "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE" and
            data.get("historical_results_unchanged", {}).get("Stage2") ==
            "NOT_ISSUED/HOLD_NO_VERDICT",
            "safety, provenance, or previous verdicts changed")
    return {"status": "F1M_PREREG_STATIC_PASS_NO_EXPOSURE",
            "roots": len(roots), "ecologies": len(ecologies),
            "within_root_pairs": 2 * len(roots),
            "T5_cost_parity_pairs_required": len(roots),
            "T6_cost_parity_pairs_required": 2 * len(roots),
            "all_arm_continuations": 4 * len(roots),
            "all_native_R_shams": 4 * len(roots),
            "motor_distinct_origin_threshold": 6,
            "adaptive_survival_distinct_origin_threshold": 6,
            "science_births_created": 0}


def check_files():
    grid_bytes = GRID.read_bytes()
    protocol_bytes = PROTOCOL.read_bytes()
    require(blob(grid_bytes) == GRID_BLOB and
            blob(protocol_bytes) == PROTOCOL_BLOB,
            "pre-exposure Git grid or protocol blob changed")
    require(GRID_BLOB in protocol_bytes.decode("utf-8"),
            "protocol no longer pins exact grid")
    for name, expected in SOURCE_BLOBS.items():
        require(blob(Path(name).read_bytes()) == expected,
                "reference source SHA changed: " + name)
    data = json.loads(grid_bytes)
    return validate_grid(data)


def main():
    summary = check_files()
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
