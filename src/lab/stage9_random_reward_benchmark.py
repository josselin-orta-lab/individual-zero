"""Stage-9 experimental negative control for spurious causal rules.

EN MVP v1.2.1 §§9.6, 13.2, 17.6, 19.3-19.5, Stage 9 (§20.3).

A preregistered, seed-shuffled schedule alters body food *externally* via the
Stage-2 InjectedScenario contract. The individual receives ordinary Perception
only. A *bench-seeded* false hypothesis ('drinking increases water') is an
optional challenge, explicitly distinguished from autonomously learned beliefs.

This is a diagnostic software experiment, NOT a successful Stage-9 scientific
gate: the full random-reward campaign, natural false-rule opportunities, and
a frozen superstition acceptance threshold remain to be registered.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from i0.modules.causal_lifecycle import CausalObservation, CausalHypothesisReview
from i0.modules.causal_model import CausalModelConfig
from lab.determinism import RandomStreamRegistry, sha256_hex, canonical_causal_bytes
from lab.injected_scenario import InjectedScenario, ScenarioEvent
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage9_runtime import Stage9Runtime

_PROTOCOL_VERSION = "stage9-random-food-negative-control-v1"
_SCENARIO_ID = "stage9-exogenous-food-reward"
_FALSE_HYPOTHESIS_REF = "causal:hydration"


@dataclass(frozen=True, slots=True)
class RandomRewardControl:
    protocol_version: str
    seed: int
    steps: int
    schedule_sha256: str
    physical_reward_steps: tuple[int, ...]
    logged_inputs: int
    applied_commands: int
    drinking_commands: int
    agency_comparisons: int
    causal_interventions: int
    established_false_rule: bool
    bench_seeded_false_hypothesis: bool
    journal_sha256: str
    # Controlled compatibility/negative-control readout is NOT a campaign
    # estimate of superstition under genuinely learned random associations.
    scientific_superstition_rate: float | None
    scientific_gate: bool | None


def preregistered_food_rewards(
    *, campaign_seed: int, steps: int,
) -> tuple[ScenarioEvent, ...]:
    """Counterbalanced, independent reward assignments fixed before action.

    The first step is left intact so the existing reference equipment can
    select a physically grounded drinking command. From step 2 onward the
    reward sequence is generated without consulting actions or world outcomes.
    """
    if type(campaign_seed) is not int or campaign_seed < 0:
        raise ValueError("the benchmark requires an explicit nonnegative seed")
    if type(steps) is not int or steps < 6:
        raise ValueError("the benchmark requires at least six physical steps")
    count = steps - 1
    switches = [1] * (count // 2) + [0] * (count - count // 2)
    stream = RandomStreamRegistry(campaign_seed=campaign_seed).stream(
        _PROTOCOL_VERSION + ":exogenous-food",
    )
    stream.shuffle(switches)
    return tuple(
        ScenarioEvent(
            t_monde=step,
            sequence=0,
            operation="set_body",
            payload={"food": float(70 if switches[step - 2] else 60)},
        )
        for step in range(2, steps + 1)
    )


def _seed_false_hypothesis_for_control(runtime: Stage9Runtime) -> None:
    """Bench injection. It is intentionally NOT autonomous evidence.

    This challenge tests refusal to establish a known false cause even
    when an unearned hypothesis exists. It must never be used to claim
    that the individual learned a superstitious belief from lived data.
    """
    model = runtime.causal_model
    for i, present, effect in (
        (1, True, True), (2, True, True),
        (3, False, False), (4, False, False),
    ):
        model.integrate_causal_observation(CausalObservation(
            identifier=f"control-observation:{i}",
            contingency_ref=_FALSE_HYPOTHESIS_REF,
            predicate="hydration_effect",
            subject_ref="water",
            application_context="water_source",
            observation_context="water_source",
            episode_ref=f"bench-episode:{i}",
            observation_ref=f"bench-transition:{i}",
            observed_step=i,
            cause_present=present,
            effect_present=effect,
            controlled_variables=(("environment", "source"),),
        ))
    changes = model.publish_causal_inference()
    if len(changes) != 1 or changes[0].after != "correlation_observee":
        raise AssertionError("controlled hypothesis fixture failed at correlation")
    model.integrate_hypothesis_review(CausalHypothesisReview(
        identifier="bench-review:water",
        contingency_ref=_FALSE_HYPOTHESIS_REF,
        alternatives=("no_drink",),
        contrasting_pairs=(
            ("control-observation:1", "control-observation:3"),
        ),
    ))
    changes = model.publish_causal_inference()
    if len(changes) != 1 or changes[0].after != "hypothese_causale":
        raise AssertionError("controlled hypothesis fixture failed at review")


def run_random_reward_negative_control(
    *, campaign_seed: int, steps: int = 14,
    bench_seed_false_hypothesis: bool = True,
) -> RandomRewardControl:
    """Exercise the *real* Stage-9 runtime with an exogenous reward schedule.

    Never inject oracle truth into memory or an individual module. The
    benchmark alone knows that drinking cannot increase water in this
    deliberately modified physical world. That truth is checked against
    actually executed and journaled actions after the life fragment.
    """
    if type(bench_seed_false_hypothesis) is not bool:
        raise ValueError("bench seed flag must be Boolean")
    events = preregistered_food_rewards(
        campaign_seed=campaign_seed, steps=steps,
    )
    source = build_stage9_reference_runtime()
    config = replace(
        source._stage9_config,
        version=_PROTOCOL_VERSION,
        causal=CausalModelConfig(
            version="p35-stage9-random-reward-control-v1",
            n1=2, n2=2, n_sec=2, m_sec=2,
            causal_predicates=("hydration_effect",),
            safe_test_actions=(("hydration_effect", "water", "boire"),),
        ),
    )
    # The physical truth is known only to the bench. The same preexisting
    # equipment still expects the original, positive drinking consequence.
    physical = replace(
        source.world.config,
        version=_PROTOCOL_VERSION + ":physics",
        drink_water_gain=0.0,
    )
    runtime = Stage9Runtime(
        world_config=physical,
        layout=source.world._layout,
        safety_config=source.stage3.substrate.safety._config,
        safety_facts=source._canonical_safety._innate,
        protected_integrity_threshold=(
            source.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=source.equipment,
    )
    runtime.stage3.substrate.scenario = InjectedScenario(
        scenario_id=_SCENARIO_ID,
        version=_PROTOCOL_VERSION,
        events=events,
        journal=runtime.journal,
    )
    if bench_seed_false_hypothesis:
        _seed_false_hypothesis_for_control(runtime)
    actions = tuple(runtime.run_step() for _ in range(steps))
    if not runtime.journal.verify():
        raise AssertionError("Stage-9 random reward causal journal is invalid")

    received = [
        row.causal_event
        for row in runtime.journal.entries
        if row.causal_event.get("kind") == "external_input_received"
        and row.causal_event.get("scenario_id") == _SCENARIO_ID
    ]
    applied = [
        row.causal_event
        for row in runtime.journal.entries
        if row.causal_event.get("kind") == "external_input_applied"
        and row.causal_event.get("scenario_id") == _SCENARIO_ID
    ]
    expected = [event.as_dict() for event in events]
    observed = [
        {
            "t_monde": item["t_monde"],
            "sequence": item["sequence"],
            "operation": item["operation"],
            "payload": item["payload"],
        }
        for item in received
    ]
    if observed != expected or len(applied) != len(events):
        raise AssertionError("random reward inputs lack journaled provenance")
    if any(
        item["t_monde"] != event.t_monde
        or item["sequence"] != event.sequence
        for item, event in zip(applied, events)
    ):
        raise AssertionError("random reward was not applied as preregistered")

    drinking = [a for a in actions if a.command_primitive == "boire"
                and a.execution_status == "applied"]
    if not drinking:
        raise AssertionError("negative-control world produced no lived test action")

    # Ground truth is evaluated externally, NEVER delivered to the individual.
    if physical.drink_water_gain != 0.0:
        raise AssertionError("the negative control has no verified false cause")
    statuses = {row.ref: row.causal_status
                for row in runtime.causal_model.contingencies()}
    false_established = statuses.get(_FALSE_HYPOTHESIS_REF) == "etablie"
    return RandomRewardControl(
        protocol_version=_PROTOCOL_VERSION,
        seed=campaign_seed, steps=steps,
        schedule_sha256=sha256_hex(canonical_causal_bytes(expected)),
        physical_reward_steps=tuple(
            event.t_monde for event in events
            if event.payload["food"] == 70.0
        ),
        logged_inputs=len(received),
        applied_commands=sum(a.execution_status == "applied" for a in actions),
        drinking_commands=len(drinking),
        agency_comparisons=len(runtime.causal_model.published_agency_evidence()),
        causal_interventions=len(
            runtime.causal_model.export_causal_state()["causal_interventions"]
        ),
        established_false_rule=false_established,
        bench_seeded_false_hypothesis=bench_seed_false_hypothesis,
        journal_sha256=runtime.journal.head_hash,
        scientific_superstition_rate=None,
        scientific_gate=None,
    )
