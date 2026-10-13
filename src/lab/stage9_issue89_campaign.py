"""Issue #89 targeted development campaign for the DC-05 epistemic boundary.

This is a deterministic development probe, not final scientific validation.
Every counted step is an actually applied WorldBody transition. Bench/Oracle
truth is used only by this external lab module to label scenario classes and
score false positives; CausalModel receives only lived autobiographical data
and Perception telemetry.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
from typing import Iterable

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from i0.modules import SymbolicPerception
from i0.modules.causal_model import CausalModel, CausalModelConfig
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage2_runtime import ScriptedStage2Runtime
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import BerryEffect, Command, Position, WorldLayout


@dataclass(frozen=True, slots=True)
class LifeResult:
    seed: int
    scenario: str
    physical_steps: int
    ingestions: int
    injuries: int
    ambiguous: int
    dc05_admissions: int
    promotions: int
    deaths: int
    false_positive_promotions: int
    withheld_true_toxic: int
    contexts: tuple[tuple[int, int], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        }


def _capture(runtime: ScriptedStage2Runtime, t_monde: int):
    return SymbolicPerception().capture(
        local_state=runtime.world.capture_local(t_monde=t_monde).as_dict(),
        telemetry=runtime.world.telemetry(),
    )


def _lived_pair(runtime: ScriptedStage2Runtime, t_monde: int):
    rows = tuple(
        row for row in runtime.autobiographical_view()
        if row.get("t_monde") == t_monde
        and row.get("kind") in {
            "command_experienced", "world_transition_experienced",
        }
    )
    if len(rows) != 2:
        raise AssertionError(f"expected one lived command/transition pair at {t_monde}")
    return rows


def _run_life(seed: int, scenario: str, *, target_steps: int = 75) -> LifeResult:
    if target_steps < 9:
        raise ValueError("campaign life must allow the preregistered probes")
    allowed = {
        "benign_clean", "hidden_static", "hidden_dynamic",
        "visible_creature", "toxic_multicontext",
        "equivalent_toxic", "equivalent_dynamic",
    }
    if scenario not in allowed:
        raise ValueError("unknown issue89 campaign scenario")

    baseline = build_stage4_reference_runtime(autonomous_mortal=True)
    berry_effects = dict(baseline.world.config.berry_effects)
    if scenario in {"toxic_multicontext", "equivalent_toxic"}:
        berry_effects["berry_a"] = BerryEffect(10.0, -10.0)
    else:
        berry_effects["berry_a"] = BerryEffect(10.0, 0.0)
    physics = replace(
        baseline.world.config,
        version=f"issue89-{scenario}-seed-{seed}",
        night_start_step=0,
        creature_damage=10.0,
        danger_zone_damage=10.0,
        berry_effects=berry_effects,
    )
    runtime = ScriptedStage2Runtime(
        config=physics,
        layout=WorldLayout(),
        phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        safety_config=SafetyProtocolConfig(
            version="issue89-campaign-safety-v1",
            lethal_max=2, mode="campaign",
        ),
        autonomous_mortal=True,
    )
    if runtime.bench is not None:
        raise AssertionError("campaign cognition substrate must not attach Bench")
    model = CausalModel(CausalModelConfig(
        f"issue89-campaign-{scenario}-v1", 2, 2, 2, 2,
    ))

    executed = ingestions = injuries = ambiguous = admissions = promotions = 0
    withheld_true = 0
    contexts: list[tuple[int, int]] = []
    last_status = "aucun"

    def apply(command: Command):
        nonlocal executed
        runtime.open_step()
        outcome = runtime.execute(command)
        if outcome.status != "applied":
            raise AssertionError(f"unexpected non-applied command: {outcome.status}")
        executed += 1
        return outcome

    # Toxic learning gets three perceived positions. Dynamic hidden danger is
    # deliberately repeated at one position so it remains within the explicit
    # indistinguishable-within-context guard. Equivalent pair scenarios use a
    # single meal, yielding exactly the same first-person injury history.
    cycles = 3 if scenario in {"hidden_dynamic", "toxic_multicontext"} else 1
    for index in range(cycles):
        if runtime.world.dead:
            break
        if scenario == "toxic_multicontext":
            position = Position(2 + index, 2 + (seed % 2))
        else:
            position = Position(2 + (seed % 3), 2 + ((seed // 3) % 3))
        runtime.world.apply_scenario_event(
            "set_position", {"position": position.as_dict()},
        )
        contexts.append((position.x, position.y))
        runtime.world.apply_scenario_event(
            "set_danger_zone", {"position": position.as_dict(), "active": False},
        )
        runtime.world.apply_scenario_event(
            "place_resource",
            {"position": position.as_dict(), "kind": "berry_a", "quantity": 1},
        )

        collect_step = executed + 1
        apply(Command("collecter", {"target": "berry_a"}))
        wait_step = collect_step + 1

        if scenario == "hidden_static":
            runtime.world.apply_scenario_event(
                "set_danger_zone", {"position": position.as_dict(), "active": True},
            )

        before_wait = _capture(runtime, wait_step)
        model.record_applied_ambient_integrity_control(
            t_monde=wait_step,
            option_ref=f"wait:{seed}:{wait_step}",
            position=(before_wait.x, before_wait.y),
            integrity_before=float(before_wait.body["integrity"]),
        )
        apply(Command("attendre"))
        after_wait = _capture(runtime, wait_step + 1)
        model.observe_followup_capture(
            t_monde=wait_step + 1,
            integrity=float(after_wait.body["integrity"]),
        )
        wait_events = _lived_pair(runtime, wait_step)
        model.ingest_closed_autobiographical_episode(
            episode_ref=f"life:{seed}:wait:{wait_step}",
            event_refs=tuple(row["event_id"] for row in wait_events),
            autobiographical_events=wait_events,
        )

        food_step = wait_step + 1
        if scenario in {"hidden_dynamic", "equivalent_dynamic"}:
            runtime.world.apply_scenario_event(
                "set_danger_zone", {"position": position.as_dict(), "active": True},
            )
        if scenario == "visible_creature":
            creature = Position(position.x + 1, position.y)
            runtime.world.apply_scenario_event(
                "place_creature", {"position": creature.as_dict()},
            )

        before_food = _capture(runtime, food_step)
        model.record_applied_food_exposure(
            t_monde=food_step,
            resource_kind="berry_a",
            option_ref=f"food:{seed}:{food_step}",
            motive_ref="goal:food",
            integrity_before=float(before_food.body["integrity"]),
            position_before=(before_food.x, before_food.y),
            body_before=dict(before_food.body),
            visible_creature_at_exposure=(
                bool(before_food.adjacent_creatures)
                or any(
                    entity.entity_type == "creature"
                    and abs(entity.x - before_food.x)
                    + abs(entity.y - before_food.y) <= 1
                    for entity in before_food.visible_entities
                )
            ),
        )
        apply(Command("manger", {"target": "berry_a"}))
        ingestions += 1
        after_food = _capture(runtime, food_step + 1)
        harmed = float(after_food.body["integrity"]) < float(before_food.body["integrity"])
        injuries += int(harmed)
        model.observe_followup_capture(
            t_monde=food_step + 1,
            integrity=float(after_food.body["integrity"]),
        )
        food_events = _lived_pair(runtime, food_step)
        rows = model.ingest_closed_autobiographical_episode(
            episode_ref=f"life:{seed}:food:{food_step}",
            event_refs=tuple(row["event_id"] for row in food_events),
            autobiographical_events=food_events,
        )
        ambiguous += sum(
            row.epistemic_status == "ambiguous_food_association" for row in rows
        )
        admissions += sum(
            row.epistemic_status == "dc05_admissible" for row in rows
        )
        if scenario in {"toxic_multicontext", "equivalent_toxic"}:
            withheld_true += sum(
                row.harm_observed
                and row.epistemic_status == "ambiguous_food_association"
                for row in rows
            )
        changes = model.publish()
        promotions += sum(
            change.before != "etabli_pour_securite"
            and change.after == "etabli_pour_securite"
            for change in changes
        )
        fact = model.get("toxic:berry_a")
        last_status = "aucun" if fact is None else fact.safety_status

        runtime.world.apply_scenario_event(
            "set_danger_zone", {"position": position.as_dict(), "active": False},
        )
        if scenario == "visible_creature":
            runtime.world.apply_scenario_event(
                "remove_creature", {"position": creature.as_dict()},
            )

    # Count only real applied transitions. If mortality occurs, this loop is
    # skipped and the life stays short rather than receiving fictitious steps.
    while executed < target_steps and not runtime.world.dead:
        apply(Command("attendre"))

    if not runtime.journal.verify():
        raise AssertionError("campaign technical journal failed hash verification")
    false_positive = int(
        scenario in {
            "benign_clean", "hidden_static", "hidden_dynamic",
            "visible_creature", "equivalent_dynamic",
        }
        and last_status == "etabli_pour_securite"
    )
    return LifeResult(
        seed=seed,
        scenario=scenario,
        physical_steps=executed,
        ingestions=ingestions,
        injuries=injuries,
        ambiguous=ambiguous,
        dc05_admissions=admissions,
        promotions=promotions,
        deaths=int(runtime.world.dead),
        false_positive_promotions=false_positive,
        withheld_true_toxic=withheld_true,
        contexts=tuple(contexts),
    )


def run_issue89_campaign(
    *,
    seeds: Iterable[int] = range(41, 49),
    steps_per_life: int = 75,
) -> dict[str, object]:
    seed_rows = tuple(seeds)
    scenarios = (
        "benign_clean",
        "hidden_static",
        "hidden_dynamic",
        "visible_creature",
        "toxic_multicontext",
        "toxic_multicontext",
        "equivalent_toxic",
        "equivalent_dynamic",
    )
    if len(seed_rows) != len(scenarios) or len(set(seed_rows)) != len(seed_rows):
        raise ValueError("issue89 campaign requires eight unique seeds")
    lives = tuple(
        _run_life(seed, scenario, target_steps=steps_per_life)
        for seed, scenario in zip(seed_rows, scenarios)
    )
    total_steps = sum(row.physical_steps for row in lives)
    result = {
        "campaign": "issue89-dc05-epistemic-boundary-v1",
        "seeds": list(seed_rows),
        "lives": len(lives),
        "deaths": sum(row.deaths for row in lives),
        "physical_steps": total_steps,
        "ingestions": sum(row.ingestions for row in lives),
        "injuries": sum(row.injuries for row in lives),
        "ambiguous": sum(row.ambiguous for row in lives),
        "dc05_admissions": sum(row.dc05_admissions for row in lives),
        "promotions": sum(row.promotions for row in lives),
        "false_positive_promotions": sum(
            row.false_positive_promotions for row in lives
        ),
        "withheld_true_toxic": sum(row.withheld_true_toxic for row in lives),
        "rows": [row.as_dict() for row in lives],
    }
    if total_steps < 600:
        raise AssertionError("development hypothesis requires at least 600 real steps")
    return result


def main() -> None:
    print(json.dumps(run_issue89_campaign(), sort_keys=True))


if __name__ == "__main__":
    main()
