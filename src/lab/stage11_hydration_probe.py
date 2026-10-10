"""Stage-11 public-world hydration decision-funnel diagnostic.

DEVELOPMENT ONLY. This module never accesses sealed worlds/seeds, oracle truth
or scientific acceptances, and never injects a hypothesis or causal test.
It compares ordinary agent trajectories on the same publicly declared
Stage-9 positive-hydration fixtures. Not a Stage-9 retrospective rerun.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping
import json

from i0.modules.causal_model import CausalModelConfig

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import InjectedScenario
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .stage9_positive_hydration_benchmark import (
    POSITIVE_HYDRATION_VARIANTS,
    PROTOCOL_VERSION as STAGE9_PUBLIC_PROTOCOL,
    run_positive_hydration_diagnostic,
)
from .stage9_random_reward_benchmark import preregistered_food_rewards


PROTOCOL_VERSION = "stage11-public-hydration-funnel-dev-v2"
TEST_PREFIX = "option:causal-test:"


@dataclass(frozen=True)
class PublicHydrationFunnel:
    protocol_version: str
    classification: str
    world: str
    seed: int
    steps: int
    schedule_sha256: str
    stage9_journal_sha256: str
    stage11_journal_sha256: str
    stage9_causal_status: str
    stage11_causal_status: str
    stage9_test_proposals: int
    stage11_test_proposals: int
    stage9_unscored_evaluations: int
    stage11_unscored_evaluations: int
    stage11_scored_intrinsic_evaluations: int
    stage11_scored_distinct_options: int
    stage11_unpredicted_proposals: int
    stage11_prediction_unavailability: tuple[tuple[str, int], ...]
    stage11_lived_causal_actions_pending: int
    stage11_lived_actions_physically_closed: int
    stage11_published_agency_reports_for_tests: int
    stage11_first_hypothesis_step: int | None
    stage11_executed_test_commands: int
    stage11_verified_interventions: int
    stage9_executed_test_commands: int
    stage9_verified_interventions: int
    stage11_modulation_transitions: int
    scientific_verdict: None = None
    golden_stage9_frozen: bool = False

    def as_dict(self) -> dict[str, object]:
        from dataclasses import asdict
        result = asdict(self)
        result["evidence_sha256"] = sha256_hex(canonical_causal_bytes(result))
        return result

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, indent=2, ensure_ascii=False)


def run_public_hydration_funnel(
    *, seed: int = 41, world: str = "small_water_gain", steps: int = 18,
) -> PublicHydrationFunnel:
    if (type(seed) is not int or seed < 0 or type(steps) is not int
        or steps < 6 or world not in POSITIVE_HYDRATION_VARIANTS):
        raise ValueError("only explicitly public Stage-9 development settings are allowed")
    gain, decay = POSITIVE_HYDRATION_VARIANTS[world]
    rewards = preregistered_food_rewards(campaign_seed=seed, steps=steps)
    schedule_digest = sha256_hex(canonical_causal_bytes(
        [event.as_dict() for event in rewards]
    ))

    # The Stage-9 control is run through its existing diagnostic unchanged.
    control = run_positive_hydration_diagnostic(
        campaign_seed=seed, world_variant=world, steps=steps,
    )
    if schedule_digest != control.schedule_sha256:
        raise AssertionError("development controls did not share physical schedule")

    baseline = build_stage11_reference_runtime()
    stage9_config = replace(
        baseline._stage11_config.stage9,
        version=STAGE9_PUBLIC_PROTOCOL + ":runtime",
        causal=CausalModelConfig(
            version=STAGE9_PUBLIC_PROTOCOL + ":causal",
            n1=2, n2=2, n_sec=2, m_sec=2,
            causal_predicates=("hydration_effect",),
            safe_test_actions=(("hydration_effect", "water", "boire"),),
        ),
    )
    vnext = Stage11Runtime(
        world_config=replace(
            baseline.world.config,
            version=STAGE9_PUBLIC_PROTOCOL + ":" + world,
            drink_water_gain=gain, water_decay_per_step=decay,
        ),
        layout=baseline.world._layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=replace(baseline._stage11_config, stage9=stage9_config),
        equipment=baseline.equipment,
    )
    vnext.stage3.substrate.scenario = InjectedScenario(
        scenario_id="stage9-positive-hydration-food-control",
        version=STAGE9_PUBLIC_PROTOCOL,
        events=rewards,
        journal=vnext.journal,
    )

    first_hypothesis = None
    applied_tests = 0
    for t in range(1, steps + 1):
        outcome = vnext.run_step()
        if (outcome.execution_status == "applied"
            and outcome.option_ref is not None
            and outcome.option_ref.startswith(TEST_PREFIX)
            and outcome.command_primitive == "boire"):
            applied_tests += 1
        record = vnext.causal_model.get("causal:hydration")
        if (first_hypothesis is None and record is not None
            and record.causal_status in {
                "hypothese_causale", "testee_par_intervention", "etablie"
            }):
            first_hypothesis = t

    if not vnext.journal.verify():
        raise AssertionError("stage11 software diagnostic has invalid journal")
    state = vnext.causal_model.export_causal_state()
    record = vnext.causal_model.get("causal:hydration")
    events = tuple(entry.causal_event for entry in vnext.journal.entries)
    proposals = {
        event["data"]["option_ref"]
        for event in events
        if event.get("kind") == "causal_test_option_proposed"
        and isinstance(event.get("data"), Mapping)
    }
    missing_predictions: dict[str, int] = {}
    for event in events:
        if event.get("kind") != "causal_test_option_proposed":
            continue
        data = event.get("data")
        if not isinstance(data, Mapping):
            continue
        if data.get("simulation_status") == "unavailable":
            reason = data.get("simulation_reason")
            if not isinstance(reason, str) or not reason:
                raise AssertionError("unpredicted causal option needs an explicit reason")
            missing_predictions[reason] = missing_predictions.get(reason, 0) + 1
    pending_actions = [
        row for row in state["lived_causal_actions"]
        if row["contingency_ref"] == "causal:hydration"
    ]
    published_comparisons = [
        row for row in state["agency_evidence"]
        if row.get("option_ref", "").startswith(TEST_PREFIX)
    ]
    assessments = [
        event["data"]
        for event in events
        if event.get("kind") == "stage11_intrinsic_evaluation"
        and isinstance(event.get("data"), Mapping)
        and event["data"]["option_ref"].startswith(TEST_PREFIX)
    ]
    evaluation_count = len(assessments)
    scored = [
        row for row in assessments
        if row["status"] == "evaluated" and row["intrinsic_value"] is not None
    ]
    if any(
        row["status"] == "evaluated" and row["intrinsic_value"] is None
        for row in assessments
    ):
        raise AssertionError("scored causal test missing P-48 motivation")
    # An accepted plan is not a physical intervention. Only the canonical
    # Causal Model's independent, Memory-closed evidence counts here.
    physical_trials = {
        trial["identifier"]
        for trial in state["causal_interventions"]
        if trial["contingency_ref"] == "causal:hydration"
    }
    return PublicHydrationFunnel(
        protocol_version=PROTOCOL_VERSION,
        classification="development_only_not_heldout",
        world=world, seed=seed, steps=steps,
        schedule_sha256=schedule_digest,
        stage9_journal_sha256=control.journal_sha256,
        stage11_journal_sha256=vnext.journal.head_hash,
        stage9_causal_status=control.published_hydration_status,
        stage11_causal_status=("aucun" if record is None else record.causal_status),
        stage9_test_proposals=control.causal_test_proposal_events,
        stage11_test_proposals=sum(
            event.get("kind") == "causal_test_option_proposed"
            for event in events
        ),
        stage9_unscored_evaluations=control.unscored_causal_test_evaluations,
        stage11_unscored_evaluations=evaluation_count - len(scored),
        stage11_scored_intrinsic_evaluations=len(scored),
        stage11_scored_distinct_options=len({
            row["option_ref"] for row in scored
        }),
        stage11_unpredicted_proposals=sum(missing_predictions.values()),
        stage11_prediction_unavailability=tuple(sorted(missing_predictions.items())),
        stage11_lived_causal_actions_pending=len(pending_actions),
        stage11_lived_actions_physically_closed=sum(
            row.get("physical_episode_ref") is not None
            for row in pending_actions
        ),
        stage11_published_agency_reports_for_tests=len(published_comparisons),
        stage11_first_hypothesis_step=first_hypothesis,
        stage11_executed_test_commands=applied_tests,
        stage11_verified_interventions=len(physical_trials),
        stage9_executed_test_commands=control.applied_causal_test_drinks,
        stage9_verified_interventions=control.published_physical_interventions,
        stage11_modulation_transitions=sum(
            event.get("kind") == "stage11_modulation_transition"
            for event in events
        ),
    )


def main() -> None:
    # One public software diagnostic case; intentionally no sealed holdout.
    print(run_public_hydration_funnel().to_json())


if __name__ == "__main__":
    main()
