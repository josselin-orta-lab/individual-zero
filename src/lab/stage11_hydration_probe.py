"""Stage-11 public-world hydration decision-funnel diagnostic.

DEVELOPMENT ONLY. This module never accesses sealed worlds/seeds, oracle truth
or scientific acceptances, and never injects a hypothesis or causal test.
It compares ordinary agent trajectories on the same publicly declared
Stage-9 positive-hydration fixtures. Not a Stage-9 retrospective rerun.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from collections import Counter
from math import isfinite
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


PROTOCOL_VERSION = "stage11-public-hydration-funnel-dev-v5"
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
    # Read-only evidence funnel. A physical command is not automatically a
    # published AgencyComparator comparison or a causal intervention.
    stage11_test_comparison_events: int
    stage11_test_comparison_classes: tuple[tuple[str, str, str, int], ...]
    stage11_comparison_water_values: tuple[tuple[int, int, float, float, float, str], ...]
    stage11_physical_comparator_join_candidates: int
    stage11_causal_action_memory_closed: int
    stage11_published_test_agency_reports: int
    stage11_pending_test_actions: int
    stage11_causal_intervention_stagings: int
    stage11_exploration_visits: int
    stage11_exploration_stagnant_visits: int
    stage11_prospective_prediction_count: int
    stage11_prospective_source_count: int
    prospective_prediction_enabled: bool
    exploration_policy_version: str
    exploration_visit_ceiling: int
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
    enable_lived_prediction: bool = False,
    exploration_policy: str = "reference",
) -> PublicHydrationFunnel:
    if (type(seed) is not int or seed < 0 or type(steps) is not int
        or steps < 6 or world not in POSITIVE_HYDRATION_VARIANTS
        or type(enable_lived_prediction) is not bool
        or type(exploration_policy) is not str
        or exploration_policy not in {"reference", "three_visit_window"}):
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

    baseline = build_stage11_reference_runtime(
        enable_lived_prediction=enable_lived_prediction,
    )
    # Public development opportunity probe: permit exactly one additional
    # real attempt AFTER the two-visit reference's habituation ceiling.
    # Not a scientific P-48 calibration and never a hidden-world search.
    exploration_cfg = baseline._stage11_config.exploration
    if exploration_policy == "three_visit_window":
        exploration_cfg = replace(
            exploration_cfg, version="p48-three-visit-window-dev-v1",
            stagnant_visit_limit=3,
        )
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
        config=replace(
            baseline._stage11_config, stage9=stage9_config,
            exploration=exploration_cfg,
        ),
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
    exploration_questions = vnext.exploration.export_causal_state()["questions"]
    exploration_visits = sum(row["visits"] for _, row in exploration_questions)
    exploration_stagnant = sum(row["stagnant"] for _, row in exploration_questions)
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
        if isinstance(row.get("option_ref"), str)
        and row["option_ref"].startswith(TEST_PREFIX)
    ]
    assessments = [
        event["data"]
        for event in events
        if event.get("kind") == "stage11_intrinsic_evaluation"
        and isinstance(event.get("data"), Mapping)
        and event["data"]["option_ref"].startswith(TEST_PREFIX)
    ]
    # A descriptive forecast must exist BEFORE sending its particular
    # physical action. Its source references may be checked by the lab but
    # are never counted as additional causal interventions.
    prospective = [
        event["data"] for event in events
        if event.get("kind") == "stage11_prospective_prediction_frozen"
        and isinstance(event.get("data"), Mapping)
    ]
    for row in prospective:
        steps_before = row.get("source_steps")
        transitions = row.get("source_transition_refs")
        episodes = row.get("source_episode_refs")
        if (
            row.get("prediction_source") != "prior_closed_lived_observation"
            or row.get("causal_validation") is not False
            or not isinstance(steps_before, list)
            or not isinstance(transitions, list)
            or not isinstance(episodes, list)
            or not steps_before
            or not (len(steps_before) == len(transitions) == len(episodes))
            or len(set(steps_before)) != len(steps_before)
            or len(set(transitions)) != len(transitions)
            or len(set(episodes)) != len(episodes)
            or any(type(step) is not int or step >= row["sent_t_monde"]
                   for step in steps_before)
        ):
            raise AssertionError("prospective forecast has invalid prior witnesses")
    # The P-47 report is produced from the actual next-step capture, not
    # merely from the selected command. Count independently stored statuses
    # without guessing the cause of a missing or uncredited intervention.
    comparisons = [
        event["data"] for event in events
        if event.get("kind") == "agency_comparison"
        and isinstance(event.get("data"), Mapping)
        and isinstance(event["data"].get("option_ref"), str)
        and event["data"]["option_ref"].startswith(TEST_PREFIX)
    ]
    comparator_classes = Counter()
    comparison_water_values: list[tuple[int, int, float, float, float, str]] = []
    for report in comparisons:
        # The real AgencyComparator's effects are *dictionaries*, not
        # tuple pairs. Earlier diagnostic versions displayed "unreported"
        # even when P-47 had checked an accessible water value.
        effect = next(
            (value for value in report.get("effects", ())
             if isinstance(value, Mapping) and value.get("variable") == "water"),
            None,
        )
        effect_status = (
            "missing_water_effect" if effect is None
            else str(effect.get("status", "unknown"))
        )
        if report.get("status") == "conforming" and effect_status != "conforming":
            raise AssertionError("conforming P-47 hydration report lacks conforming water")
        if effect is not None:
            values = tuple(effect.get(k) for k in (
                "predicted", "observed", "precision",
            ))
            if all(type(v) in (float, int) and isfinite(v) for v in values):
                comparison_water_values.append((
                    report["sent_t_monde"], report["observed_t_monde"],
                    *map(float, values), effect_status,
                ))
        comparator_classes[(
            str(report.get("status", "unknown")),
            str(report.get("attribution", "unknown")),
            effect_status,
        )] += 1
    comparator_keys = {
        (report["option_ref"], report["sent_t_monde"],
         report["observed_t_monde"])
        for report in published_comparisons
    }
    joined_candidates = sum(
        row.get("physical_episode_ref") is not None
        and (row["option_ref"], row["sent_t_monde"],
             row["observed_t_monde"]) in comparator_keys
        for row in state["lived_causal_actions"]
        if isinstance(row.get("option_ref"), str)
        and row["option_ref"].startswith(TEST_PREFIX)
    )
    comparison_classes = tuple(
        (status, attribution, water_effect, count)
        for (status, attribution, water_effect), count
        in sorted(comparator_classes.items())
    )
    memory_closed = sum(
        event.get("kind") == "causal_applied_action_memory_verified"
        and isinstance(event.get("data"), Mapping)
        and isinstance(event["data"].get("option_ref"), str)
        and event["data"]["option_ref"].startswith(TEST_PREFIX)
        for event in events
    )
    published_agency = sum(
        isinstance(row.get("option_ref"), str)
        and row["option_ref"].startswith(TEST_PREFIX)
        for row in state["agency_evidence"]
    )
    pending_test_action_count = sum(
        isinstance(row.get("option_ref"), str)
        and row["option_ref"].startswith(TEST_PREFIX)
        for row in state["lived_causal_actions"]
    )
    staged_interventions = sum(
        event.get("kind") == "causal_lived_intervention_staged"
        and isinstance(event.get("data"), Mapping)
        and event["data"].get("contingency_ref") == "causal:hydration"
        for event in events
    )
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
        stage11_test_comparison_events=len(comparisons),
        stage11_test_comparison_classes=comparison_classes,
        stage11_comparison_water_values=tuple(sorted(comparison_water_values)),
        stage11_physical_comparator_join_candidates=joined_candidates,
        stage11_causal_action_memory_closed=memory_closed,
        stage11_published_test_agency_reports=published_agency,
        stage11_pending_test_actions=pending_test_action_count,
        stage11_causal_intervention_stagings=staged_interventions,
        stage11_exploration_visits=exploration_visits,
        stage11_exploration_stagnant_visits=exploration_stagnant,
        stage11_prospective_prediction_count=len(prospective),
        stage11_prospective_source_count=sum(
            len(row["source_transition_refs"]) for row in prospective
        ),
        prospective_prediction_enabled=enable_lived_prediction,
        exploration_policy_version=exploration_cfg.version,
        exploration_visit_ceiling=exploration_cfg.stagnant_visit_limit,
    )


def main() -> None:
    # One public software diagnostic case; intentionally no sealed holdout.
    print(run_public_hydration_funnel().to_json())


if __name__ == "__main__":
    main()
