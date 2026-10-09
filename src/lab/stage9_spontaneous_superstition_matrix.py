"""Multi-seed, multi-variant diagnostic of spontaneous Stage-9 false rules.

This intentionally does not count an opportunity that cannot form a causal
candidate as a scientific success. The Stage-9 default has no autonomous
hydration observations, so this control exposes that coverage gap rather
than reporting a falsely reassuring superstition rate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_random_reward_benchmark import (
    NULL_WATER_WORLD_VARIANTS, RandomRewardControl,
    run_random_reward_negative_control,
)


@dataclass(frozen=True, slots=True)
class SpontaneousSuperstitionMatrix:
    protocol_version: str
    seeds: tuple[int, ...]
    world_variants: tuple[str, ...]
    runs: tuple[RandomRewardControl, ...]
    spontaneously_observed_candidates: int
    physically_verified_exposures: int
    established_false_rules: int
    total_lived_hydration_observations: int
    lived_drink_observations: int
    lived_wait_control_observations: int
    runs_with_observed_drink_and_wait: int
    natural_false_rule_rate: float | None
    # Opportunity accounting is empirical, not a claim of causation.
    lived_positive_drink_observations: int
    runs_with_independent_positive_drinks: int
    runs_with_matched_controls: int
    correlation_readiness: str
    evaluation_status: str
    digest: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(), ensure_ascii=False, sort_keys=True, indent=2,
        ) + "\n"


def run_spontaneous_superstition_matrix(
    *, seeds: tuple[int, ...] = (41, 42, 43),
    world_variants: tuple[str, ...] = (
        "null_water_reference", "null_water_food_decay",
    ),
    steps: int = 14,
) -> SpontaneousSuperstitionMatrix:
    if (
        not isinstance(seeds, tuple)
        or not seeds
        or len(set(seeds)) != len(seeds)
        or any(type(seed) is not int or seed < 0 for seed in seeds)
        or not isinstance(world_variants, tuple)
        or not world_variants
        or len(set(world_variants)) != len(world_variants)
        or any(name not in NULL_WATER_WORLD_VARIANTS for name in world_variants)
        or type(steps) is not int or steps < 6
    ):
        raise ValueError("invalid fixed Stage-9 diagnostic matrix")
    runs = tuple(
        run_random_reward_negative_control(
            campaign_seed=seed,
            steps=steps,
            world_variant=world_variant,
            bench_seed_false_hypothesis=False,
        )
        for world_variant in world_variants for seed in seeds
    )
    if any(
        run.scientific_gate is not None
        or run.scientific_superstition_rate is not None
        or not run.verified_null_drink_transitions
        or run.bench_seeded_false_hypothesis
        for run in runs
    ):
        raise AssertionError("matrix contains unverified or bench-seeded evidence")
    opportunities = sum(len(run.spontaneous_candidate_refs) for run in runs)
    false_rules = sum(len(run.spontaneous_established_false_refs) for run in runs)
    # This is a per-run fraction of actually occurring candidates, not a
    # population-level scientific rate or an ex-post threshold comparison.
    diagnostic_rate = None if opportunities == 0 else false_rules / opportunities
    payload = {
        "protocol": "stage9-spontaneous-superstition-matrix-v1",
        "seeds": seeds,
        "variants": world_variants,
        "steps": steps,
        "runs": [
            {
                "seed": row.seed,
                "world": row.world_variant,
                "journal": row.journal_sha256,
                "schedule": row.schedule_sha256,
                "witnesses": row.verified_null_drink_transitions,
                "spontaneous": row.spontaneous_candidate_refs,
                "lived_observations": row.lived_hydration_observation_refs,
                "lived_drinks": row.lived_drink_observations,
                "lived_waits": row.lived_wait_control_observations,
                "positive_drinks": row.lived_positive_drink_observations,
                "independent_episodes": row.independent_lived_hydration_episodes,
            }
            for row in runs
        ],
    }
    return SpontaneousSuperstitionMatrix(
        protocol_version=payload["protocol"],
        seeds=seeds,
        world_variants=world_variants,
        runs=runs,
        spontaneously_observed_candidates=opportunities,
        physically_verified_exposures=sum(
            len(run.verified_null_drink_transitions) for run in runs
        ),
        established_false_rules=false_rules,
        total_lived_hydration_observations=sum(
            row.independent_lived_hydration_episodes for row in runs
        ),
        lived_drink_observations=sum(
            row.lived_drink_observations for row in runs
        ),
        lived_wait_control_observations=sum(
            row.lived_wait_control_observations for row in runs
        ),
        runs_with_observed_drink_and_wait=sum(
            bool(row.lived_drink_observations and row.lived_wait_control_observations)
            for row in runs
        ),
        natural_false_rule_rate=diagnostic_rate,
        lived_positive_drink_observations=sum(
            row.lived_positive_drink_observations for row in runs
        ),
        runs_with_independent_positive_drinks=sum(
            row.lived_positive_drink_observations >= 2 for row in runs
        ),
        runs_with_matched_controls=sum(
            row.lived_positive_drink_observations >= 2
            and row.lived_wait_control_observations >= 1
            for row in runs
        ),
        correlation_readiness=(
            "no_matched_positive_exposures"
            if not any(
                row.lived_positive_drink_observations >= 2
                and row.lived_wait_control_observations >= 1
                for row in runs
            ) else "requires_per_run_context_and_base_rate_validation"
        ),
        evaluation_status="not_evaluable" if opportunities == 0 else "diagnostic_only",
        digest=sha256_hex(canonical_causal_bytes(payload)),
    )


def main() -> None:
    print(run_spontaneous_superstition_matrix().to_json(), end="")


if __name__ == "__main__":
    main()
