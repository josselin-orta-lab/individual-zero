"""Diagnostic of natural Stage-9 hydration evidence across matched worlds.

EN MVP v1.2.1: 13.2, 19.5, Stage 9 (§20.3). The laboratory changes physical
water gain, but never injects an option, a causal observation or a hypothesis.
A fixed seeded food schedule is used for both members of each matched pair.

This command is for evidence collection, not a Stage-9 acceptance gate:
    python -m lab.stage9_hydration_contrast_report

The 'recurrent_water_need' scenario is an additional *exploratory* positive
world. It is not a single-variable contrast with the null control, because
its water decay also differs. No scientific threshold or golden is created.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_positive_hydration_benchmark import (
    run_positive_hydration_diagnostic,
)
from .stage9_random_reward_benchmark import (
    run_random_reward_negative_control,
)

PROTOCOL_VERSION = "stage9-hydration-contrast-diagnostic-v1"


@dataclass(frozen=True, slots=True)
class HydrationContrastCase:
    seed: int
    world: str
    comparison_role: str
    schedule_sha256: str
    journal_sha256: str
    applied_drinks: int
    applied_waits: int | None
    closed_memory_episodes: int | None
    closed_hydration_observations: int
    closed_drinks: int
    positive_drinks: int
    wait_controls: int
    matched_positive_drinks: int | None
    pending_hydration_exposures: int | None
    pending_causal_observations: int | None
    causal_status: str
    missing_evidence: str
    scientific_gate: None = None
    first_hypothesis_step: int | None = None
    drinks_after_hypothesis: int | None = None
    unscored_test_evaluations: int | None = None
    published_interventions: int | None = None
    published_self_compatible_water_reports: int | None = None


@dataclass(frozen=True, slots=True)
class HydrationContrastReport:
    protocol_version: str
    experiment_seeds: tuple[int, ...]
    steps: int
    cases: tuple[HydrationContrastCase, ...]
    matched_pairs_checked: int
    acceptance_status: str = "open"
    golden_stage9_frozen: bool = False

    def as_dict(self) -> dict[str, object]:
        data = {
            "protocol_version": self.protocol_version,
            "experiment_seeds": self.experiment_seeds,
            "steps": self.steps,
            "cases": [asdict(row) for row in self.cases],
            "matched_pairs_checked": self.matched_pairs_checked,
            "acceptance_status": self.acceptance_status,
            "golden_stage9_frozen": self.golden_stage9_frozen,
        }
        data["evidence_sha256"] = sha256_hex(canonical_causal_bytes(data))
        return data

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, indent=2) + "\n"


def _positive_gap(
    *,
    closed_drinks: int,
    applied_drinks: int,
    positive_drinks: int,
    wait_controls: int,
    matched_positive_drinks: int,
    n1: int,
    status: str,
    pending_hydration_exposures: int,
    pending_causal_observations: int,
) -> str:
    """Classify the first observable shortfall, never manufacture evidence."""
    if not closed_drinks:
        if applied_drinks:
            return "applied_drinks_without_closed_observation"
        return "no_independently_applied_drink"
    if positive_drinks < n1:
        return "insufficient_positive_closed_episodes"
    if not wait_controls:
        return "no_naturally_selected_wait_controls"
    if matched_positive_drinks < n1:
        return "insufficient_context_matched_control_exposures"
    if status == "aucun":
        return (
            "pending_causal_publication"
            if pending_causal_observations
            else "base_rate_or_evidence_admission"
        )
    if status == "correlation_observee":
        return "observed_alternatives_or_next_publication_required"
    if status == "hypothese_causale":
        return "verified_intervention_required"
    if status == "testee_par_intervention":
        return "independent_n2_intervention_contexts_required"
    if status == "etablie":
        return "established_in_diagnostic_only"
    return "unclassified_causal_status"


def run_hydration_contrast_report(
    *,
    seeds: tuple[int, ...] = (41, 42),
    steps: int = 18,
) -> HydrationContrastReport:
    if (
        not isinstance(seeds, tuple)
        or not seeds
        or len(set(seeds)) != len(seeds)
        or any(type(seed) is not int or seed < 0 for seed in seeds)
        or type(steps) is not int or steps < 6
    ):
        raise ValueError("invalid Stage-9 hydration contrast design")

    rows = []
    for seed in seeds:
        negative = run_random_reward_negative_control(
            campaign_seed=seed, steps=steps,
            bench_seed_false_hypothesis=False,
            world_variant="null_water_reference",
        )
        positive = run_positive_hydration_diagnostic(
            campaign_seed=seed, steps=steps,
            world_variant="small_water_gain",
        )
        exploratory = run_positive_hydration_diagnostic(
            campaign_seed=seed, steps=steps,
            world_variant="recurrent_water_need",
        )
        aligned = run_positive_hydration_diagnostic(
            campaign_seed=seed, steps=steps,
            world_variant="model_aligned_water_gain",
        )
        if (
            negative.schedule_sha256 != positive.schedule_sha256
            or negative.schedule_sha256 != exploratory.schedule_sha256
            or negative.seed != positive.seed
            or positive.schedule_sha256 != aligned.schedule_sha256
            or positive.seed != exploratory.seed
            or positive.seed != aligned.seed
        ):
            raise AssertionError("physical contrast did not preserve reward schedule")
        if (
            negative.lived_positive_drink_observations != 0
            or negative.scientific_gate is not None
            or positive.scientific_gate is not None
            or exploratory.scientific_gate is not None
            or aligned.scientific_gate is not None
        ):
            raise AssertionError("contrast leaked false causal or acceptance evidence")
        rows.append(HydrationContrastCase(
            seed=seed,
            world="null_water_reference",
            comparison_role="matched_null",
            schedule_sha256=negative.schedule_sha256,
            journal_sha256=negative.journal_sha256,
            applied_drinks=negative.drinking_commands,
            applied_waits=None,
            closed_memory_episodes=None,
            closed_hydration_observations=(
                negative.independent_lived_hydration_episodes
            ),
            closed_drinks=negative.lived_drink_observations,
            positive_drinks=negative.lived_positive_drink_observations,
            wait_controls=negative.lived_wait_control_observations,
            matched_positive_drinks=None,
            pending_hydration_exposures=None,
            pending_causal_observations=None,
            causal_status=negative.natural_hydration_status,
            missing_evidence="null_physics_has_no_positive_effect",
        ))
        for item, role in (
            (positive, "matched_positive_water_gain"),
            (exploratory, "exploratory_changed_water_decay"),
            (aligned, "exploratory_model_aligned_prediction"),
        ):
            rows.append(HydrationContrastCase(
                seed=seed,
                world=item.world_variant,
                comparison_role=role,
                schedule_sha256=item.schedule_sha256,
                journal_sha256=item.journal_sha256,
                applied_drinks=item.applied_drink_commands,
                applied_waits=item.applied_wait_commands,
                closed_memory_episodes=item.closed_memory_episodes,
                closed_hydration_observations=item.closed_hydration_observations,
                closed_drinks=item.closed_drink_observations,
                positive_drinks=item.positive_drink_observations,
                wait_controls=item.closed_wait_controls,
                matched_positive_drinks=item.positive_drinks_with_matched_controls,
                pending_hydration_exposures=item.pending_hydration_exposures,
                pending_causal_observations=item.pending_causal_observations,
                causal_status=item.published_hydration_status,
                first_hypothesis_step=item.first_published_hypothesis_step,
                drinks_after_hypothesis=item.applied_drinks_after_hypothesis,
                unscored_test_evaluations=item.unscored_causal_test_evaluations,
                published_interventions=item.published_physical_interventions,
                published_self_compatible_water_reports=(
                    item.published_self_compatible_water_reports
                ),
                missing_evidence=_positive_gap(
                    closed_drinks=item.closed_drink_observations,
                    applied_drinks=item.applied_drink_commands,
                    positive_drinks=item.positive_drink_observations,
                    wait_controls=item.closed_wait_controls,
                    matched_positive_drinks=(
                        item.positive_drinks_with_matched_controls
                    ),
                    n1=2,
                    status=item.published_hydration_status,
                    pending_hydration_exposures=(
                        item.pending_hydration_exposures
                    ),
                    pending_causal_observations=(
                        item.pending_causal_observations
                    ),
                ),
            ))
    return HydrationContrastReport(
        protocol_version=PROTOCOL_VERSION,
        experiment_seeds=seeds,
        steps=steps,
        cases=tuple(rows),
        matched_pairs_checked=len(seeds),
    )


def main() -> None:
    report = run_hydration_contrast_report()
    print("stage9_hydration_contrast=" + json.dumps(
        report.as_dict(), sort_keys=True, separators=(",", ":"),
    ))


if __name__ == "__main__":
    main()
