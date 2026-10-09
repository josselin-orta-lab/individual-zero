"""Multi-seed, multi-variant diagnostic of spontaneous Stage-9 false rules.

This intentionally does not count an opportunity that cannot form a causal
candidate as a scientific success. The Stage-9 default has no autonomous
hydration observations, so this control exposes that coverage gap rather
than reporting a falsely reassuring superstition rate.
"""
from __future__ import annotations

from dataclasses import dataclass

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
    natural_false_rule_rate: float | None
    evaluation_status: str
    digest: str


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
        natural_false_rule_rate=diagnostic_rate,
        evaluation_status="not_evaluable" if opportunities == 0 else "diagnostic_only",
        digest=sha256_hex(canonical_causal_bytes(payload)),
    )
