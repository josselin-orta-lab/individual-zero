"""Controlled Stage-6 reference equipment corpus.

This fixture exists only for software acceptance and equipment benchmarking.
It is not a campaign corpus and does not supply scientific calibration values.

Every required family is represented by an actual controlled WorldBody
transition. Preparation transitions are deliberately excluded from the corpus.

Spec: 12.5, P-46, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import replace

from i0.interfaces import PrimitiveCommand

from .equipment_corpus import (
    EquipmentCorpusRecorder,
    require_corpus_coverage,
)
from .stage4_reference_fixture import build_stage4_reference_runtime
from .world import BodyState, Position, WorldBody, WorldLayout


def reference_corpus_world_config():
    base = build_stage4_reference_runtime().world.config
    costs = dict(base.action_energy_costs)
    costs.update(
        {
            "se_deplacer": 1.0,
            "collecter": 0.5,
            "manger": 0.25,
            "boire": 0.25,
            "poser_une_pierre": 0.5,
            "fabriquer_outil": 1.0,
            "attendre": 0.0,
            "dormir": 0.0,
        }
    )
    return replace(
        base,
        version="stage6-reference-corpus-world-v1",
        initial_body=BodyState(
            energy=40.0,
            food=40.0,
            water=30.0,
            integrity=90.0,
        ),
        action_energy_costs=costs,
        sleep_energy_gain=5.0,
        rest_integrity_gain=1.0,
        drink_water_gain=20.0,
        creature_damage=10.0,
    )


def _world(layout: WorldLayout) -> WorldBody:
    return WorldBody(
        config=reference_corpus_world_config(),
        layout=layout,
    )


def build_stage6_reference_corpus():
    recorder = EquipmentCorpusRecorder(
        corpus_version="stage6-reference-corpus-v1",
    )

    # Free movement.
    recorder.record_transition(
        world=_world(WorldLayout()),
        t_monde=1,
        family="movement_free",
        command=PrimitiveCommand(
            "se_deplacer",
            {"direction": "east"},
        ),
    )

    # Blocked movement, same command with one controlled obstacle.
    recorder.record_transition(
        world=_world(
            WorldLayout(
                obstacles=frozenset({Position(3, 2)}),
            )
        ),
        t_monde=1,
        family="movement_blocked",
        command=PrimitiveCommand(
            "se_deplacer",
            {"direction": "east"},
        ),
    )

    # Collection without a tool.
    recorder.record_transition(
        world=_world(
            WorldLayout(
                resources=((Position(2, 2), "wood", 3),),
            )
        ),
        t_monde=1,
        family="collection_without_tool",
        command=PrimitiveCommand(
            "collecter",
            {"target": "wood"},
        ),
    )

    # Collection with a tool. Preparation is intentionally outside the corpus.
    tool_world = _world(
        WorldLayout(
            resources=(
                (Position(2, 2), "wood", 3),
                (Position(2, 2), "stone", 1),
            ),
        )
    )
    tool_world.apply(
        PrimitiveCommand("collecter", {"target": "wood"}),
        t_monde=1,
    )
    tool_world.apply(
        PrimitiveCommand("collecter", {"target": "stone"}),
        t_monde=2,
    )
    tool_world.apply(
        PrimitiveCommand("fabriquer_outil"),
        t_monde=3,
    )
    recorder.record_transition(
        world=tool_world,
        t_monde=4,
        family="collection_with_tool",
        command=PrimitiveCommand(
            "collecter",
            {"target": "wood"},
        ),
    )

    # Resource consumption.
    eat_world = _world(
        WorldLayout(
            resources=((Position(2, 2), "berry_a", 1),),
        )
    )
    eat_world.apply(
        PrimitiveCommand("collecter", {"target": "berry_a"}),
        t_monde=1,
    )
    recorder.record_transition(
        world=eat_world,
        t_monde=2,
        family="resource_consumption",
        command=PrimitiveCommand("manger", {"target": "berry_a"}),
    )

    # Drinking.
    recorder.record_transition(
        world=_world(
            WorldLayout(
                water_sources=frozenset({Position(2, 2)}),
            )
        ),
        t_monde=1,
        family="drinking",
        command=PrimitiveCommand("boire"),
    )

    # Tool crafting.
    craft_world = _world(
        WorldLayout(
            resources=(
                (Position(2, 2), "wood", 1),
                (Position(2, 2), "stone", 1),
            ),
        )
    )
    craft_world.apply(
        PrimitiveCommand("collecter", {"target": "wood"}),
        t_monde=1,
    )
    craft_world.apply(
        PrimitiveCommand("collecter", {"target": "stone"}),
        t_monde=2,
    )
    recorder.record_transition(
        world=craft_world,
        t_monde=3,
        family="tool_crafting",
        command=PrimitiveCommand("fabriquer_outil"),
    )

    # Ordinary stone placement without forming a shelter.
    stone_world = _world(
        WorldLayout(
            resources=((Position(2, 2), "stone", 1),),
        )
    )
    stone_world.apply(
        PrimitiveCommand("collecter", {"target": "stone"}),
        t_monde=1,
    )
    recorder.record_transition(
        world=stone_world,
        t_monde=2,
        family="stone_placement",
        command=PrimitiveCommand("poser_une_pierre"),
    )

    # Closed-shelter transition: three stones are prepared, the fourth is the
    # recorded contrast that changes known_shelter_here.
    shelter_world = _world(
        WorldLayout(
            resources=((Position(2, 2), "stone", 4),),
        )
    )
    t = 1
    for _ in range(3):
        shelter_world.apply(
            PrimitiveCommand("collecter", {"target": "stone"}),
            t_monde=t,
        )
        t += 1
        shelter_world.apply(
            PrimitiveCommand("poser_une_pierre"),
            t_monde=t,
        )
        t += 1
    shelter_world.apply(
        PrimitiveCommand("collecter", {"target": "stone"}),
        t_monde=t,
    )
    t += 1
    recorder.record_transition(
        world=shelter_world,
        t_monde=t,
        family="shelter_state",
        command=PrimitiveCommand("poser_une_pierre"),
    )

    # Same local creature geometry, contrasted by temporal context.
    creature_layout = WorldLayout(
        creatures=frozenset({Position(3, 2)}),
    )
    recorder.record_transition(
        world=_world(creature_layout),
        t_monde=1,
        family="creature_day",
        command=PrimitiveCommand("attendre"),
    )
    recorder.record_transition(
        world=_world(creature_layout),
        t_monde=200,
        family="creature_night",
        command=PrimitiveCommand("attendre"),
    )

    recorder.record_transition(
        world=_world(WorldLayout()),
        t_monde=1,
        family="sleep",
        command=PrimitiveCommand("dormir"),
    )
    recorder.record_transition(
        world=_world(WorldLayout()),
        t_monde=1,
        family="wait",
        command=PrimitiveCommand("attendre"),
    )

    corpus = recorder.build()
    require_corpus_coverage(corpus)
    return corpus
