"""Stage-9 positive-water contrast for naturally selected causal evidence.

EN MVP v1.2.1 §§9.6, 13.2, 19.3-19.5, Stage 9 (§20.3).

Same seeded exogenous FOOD schedule as the null-water negative control, but
the physical drinking effect is positive. No hypothesis, observation, option,
or test is injected. Only the individual's real actions and independently
closed DC-09 episodes can reach the canonical CausalModel. The laboratory
alone observes the world configuration and computes the diagnostics.

This is a contrastive SOFTWARE diagnostic, not a scientific acceptance gate.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from i0.modules.causal_model import CausalModelConfig

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import InjectedScenario
from .stage9_random_reward_benchmark import (
    preregistered_food_rewards,
)
from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage9_runtime import Stage9Runtime

PROTOCOL_VERSION = "stage9-positive-hydration-diagnostic-v1"

# Fixed, explicitly test-only physical configurations. Food rewards depend
# on the campaign seed; the variant controls only the water physics.
POSITIVE_HYDRATION_VARIANTS = {
    "small_water_gain": (12.0, 0.0),
    "recurrent_water_need": (35.0, 1.5),
}


@dataclass(frozen=True, slots=True)
class PositiveHydrationDiagnostic:
    protocol_version: str
    world_variant: str
    seed: int
    steps: int
    drink_water_gain: float
    water_decay_per_step: float
    schedule_sha256: str
    journal_sha256: str
    applied_drink_commands: int
    applied_wait_commands: int
    closed_hydration_observations: int
    independent_closed_episodes: int
    closed_drink_observations: int
    positive_drink_observations: int
    closed_wait_controls: int
    positive_drinks_with_matched_controls: int
    observed_hydration_refs: tuple[str, ...]
    published_hydration_status: str
    qualifying_n1: bool
    missing_evidence: str
    scientific_gate: None = None


def run_positive_hydration_diagnostic(
    *,
    campaign_seed: int,
    world_variant: str = "small_water_gain",
    steps: int = 24,
) -> PositiveHydrationDiagnostic:
    if type(campaign_seed) is not int or campaign_seed < 0:
        raise ValueError("a nonnegative integer campaign seed is required")
    if type(steps) is not int or steps < 6:
        raise ValueError("at least six world steps are required")
    if world_variant not in POSITIVE_HYDRATION_VARIANTS:
        raise ValueError("unsupported positive hydration world variant")

    drink_gain, water_decay = POSITIVE_HYDRATION_VARIANTS[world_variant]
    rewards = preregistered_food_rewards(
        campaign_seed=campaign_seed, steps=steps,
    )
    reference = build_stage9_reference_runtime()
    causal = CausalModelConfig(
        version=PROTOCOL_VERSION + ":causal",
        n1=2, n2=2, n_sec=2, m_sec=2,
        causal_predicates=("hydration_effect",),
        safe_test_actions=(("hydration_effect", "water", "boire"),),
    )
    stage9 = replace(
        reference._stage9_config,
        version=PROTOCOL_VERSION + ":runtime",
        causal=causal,
    )
    physical = replace(
        reference.world.config,
        version=PROTOCOL_VERSION + ":" + world_variant,
        drink_water_gain=drink_gain,
        water_decay_per_step=water_decay,
    )
    runtime = Stage9Runtime(
        world_config=physical,
        layout=reference.world._layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=reference._canonical_safety._innate,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=stage9,
        equipment=reference.equipment,
    )
    runtime.stage3.substrate.scenario = InjectedScenario(
        scenario_id="stage9-positive-hydration-food-control",
        version=PROTOCOL_VERSION,
        events=rewards,
        journal=runtime.journal,
    )

    outcomes = tuple(runtime.run_step() for _ in range(steps))
    if not runtime.journal.verify():
        raise AssertionError("positive hydration journal is not intact")
    state = runtime.causal_model.export_causal_state()
    witnesses = {
        ref: (command_ref, transition_ref)
        for ref, command_ref, transition_ref
        in state["hydration_observation_witnesses"]
    }
    if len(witnesses) != len(state["hydration_observation_witnesses"]):
        raise AssertionError("duplicated canonical hydration witness")

    episode_by_ref = {
        episode.id: set(episode.event_refs)
        for episode in runtime.memory.episodes
    }
    observations = [
        obs for obs in state["causal_observations"]
        if obs["identifier"] in witnesses
        and obs["contingency_ref"] == "causal:hydration"
        and obs["predicate"] == "hydration_effect"
    ]
    if len(observations) != len(witnesses):
        raise AssertionError("orphan canonical hydration witness")
    for obs in observations:
        command_ref, transition_ref = witnesses[obs["identifier"]]
        if (
            obs["observation_ref"] != transition_ref
            or not {command_ref, transition_ref}.issubset(
                episode_by_ref.get(obs["episode_ref"], set())
            )
        ):
            raise AssertionError("hydration evidence is not in its closed episode")

    if len({row["episode_ref"] for row in observations}) != len(observations):
        raise AssertionError("multiple causal observations credited to one episode")

    drinks = tuple(row for row in observations if row["cause_present"])
    positive_drinks = tuple(row for row in drinks if row["effect_present"])
    controls = tuple(row for row in observations if not row["cause_present"])

    def context(row):
        return tuple(tuple(pair) for pair in row["controlled_variables"])

    matched_positive = {
        row["identifier"]
        for row in positive_drinks for control in controls
        if row["episode_ref"] != control["episode_ref"]
        and row["observation_context"] == control["observation_context"]
        and context(row) == context(control)
    }
    if not drinks:
        missing = "no_closed_drinking_observations"
    elif not positive_drinks:
        missing = "no_observed_positive_drinking_effect"
    elif len(positive_drinks) < causal.n1:
        missing = "fewer_than_n1_positive_drinking_episodes"
    elif not matched_positive:
        missing = "no_independent_matched_wait_control"
    elif len(matched_positive) < causal.n1:
        missing = "fewer_than_n1_matched_positive_episodes"
    else:
        missing = "eligible_for_contextual_base_rate_check"

    record = runtime.causal_model.get("causal:hydration")
    status = "absent" if record is None else record.causal_status
    return PositiveHydrationDiagnostic(
        protocol_version=PROTOCOL_VERSION,
        world_variant=world_variant,
        seed=campaign_seed,
        steps=steps,
        drink_water_gain=drink_gain,
        water_decay_per_step=water_decay,
        schedule_sha256=sha256_hex(canonical_causal_bytes(
            [event.as_dict() for event in rewards]
        )),
        journal_sha256=runtime.journal.head_hash,
        applied_drink_commands=sum(
            item.execution_status == "applied"
            and item.command_primitive == "boire"
            for item in outcomes
        ),
        applied_wait_commands=sum(
            item.execution_status == "applied"
            and item.command_primitive == "attendre"
            for item in outcomes
        ),
        closed_hydration_observations=len(observations),
        independent_closed_episodes=len({
            row["episode_ref"] for row in observations
        }),
        closed_drink_observations=len(drinks),
        positive_drink_observations=len(positive_drinks),
        closed_wait_controls=len(controls),
        positive_drinks_with_matched_controls=len(matched_positive),
        observed_hydration_refs=tuple(sorted(witnesses)),
        published_hydration_status=status,
        qualifying_n1=(
            len(matched_positive) >= causal.n1
        ),
        missing_evidence=missing,
        scientific_gate=None,
    )
