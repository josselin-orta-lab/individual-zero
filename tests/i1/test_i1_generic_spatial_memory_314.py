"""Deterministic generic I1 spatial-memory tests with no third-party packages."""
import unittest
from types import SimpleNamespace
from dataclasses import replace

from i1.modules.spatial_memory import (
    PlaceMemory, find_spatial_return,
)
from i1.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from i1.modules.observed_frontier_routing import ObservedSurvey


def capture(t, x, y, entities=()):
    directions = (("north", 0, -1), ("east", 1, 0),
                  ("south", 0, 1), ("west", -1, 0))
    return SimpleNamespace(
        t_monde=t, x=x, y=y, current_water_source=False,
        adjacent=tuple(SimpleNamespace(direction=d, x=x+dx, y=y+dy,
                                      passable=True, creature=False)
                       for d, dx, dy in directions),
        visible_entities=tuple(SimpleNamespace(entity_id=entity_id,
            entity_type=kind, x=px, y=py) for entity_id, kind, px, py in entities),
    )


def owner():
    return GeographicExploration(GeographicExplorationConfig(
        version="test-entity-general", novelty_weight=0.15,
        max_distinct_sites=64, max_targets_per_cycle=1,
        observe_routes=True, refresh_surveys=True, remember_entities=True,
    ))


def sample(entity_id="berry_a:1:0", kind="berry_a", step=1):
    return PlaceMemory(
        observer_id="i1:sample", entity_id=entity_id, entity_type=kind,
        position=(1, 0), observed_from=(0, 0),
        first_seen_step=step, last_seen_step=step,
        reached_step=None, contradiction_step=None, contradictions=0,
        confidence=0.65,
    )


class GenericSpatialMemoryTests(unittest.TestCase):
    def test_same_owner_remembers_multiple_types_and_ids(self):
        geo = owner()
        seen = capture(1, 0, 0, (
            ("water_source:0", "water_source", 0, 1),
            ("berry_a:1:0", "berry_a", 1, 0),
            ("creature:0", "creature", -1, 0),
        ))
        geo.observe_capture(seen)
        rows = geo.observe_entities(seen, observer_id="i1:sample")
        self.assertEqual(len(rows), 3)
        self.assertEqual({v.entity_type for v in rows},
                         {"water_source", "berry_a", "creature"})
        self.assertEqual(len(geo.observe_entities(
            seen, observer_id="i1:sample")), 0)

    def test_absence_weakens_only_locally_visible_history(self):
        geo = owner()
        seen = capture(1, 0, 0, (("berry_a:1:0", "berry_a", 1, 0),))
        geo.observe_capture(seen)
        geo.observe_entities(seen, observer_id="i1:sample")
        before = geo.place_memories[0]
        away = capture(2, 0, 2)
        geo.observe_capture(away)
        geo.observe_entities(away, observer_id="i1:sample")
        self.assertEqual(geo.place_memories[0], before)
        nearby = capture(3, 0, 0)
        geo.observe_capture(nearby)
        geo.observe_entities(nearby, observer_id="i1:sample")
        self.assertEqual(geo.place_memories[0].contradictions, 1)
        self.assertLess(geo.place_memories[0].confidence, before.confidence)

    def test_seen_entity_moves_without_original_position_oracle(self):
        geo = owner()
        first = capture(1, 0, 0, (("creature:0", "creature", 1, 0),))
        geo.observe_capture(first)
        geo.observe_entities(first, observer_id="i1:sample")
        moved = capture(2, 0, 0, (("creature:0", "creature", 0, 1),))
        geo.observe_capture(moved)
        geo.observe_entities(moved, observer_id="i1:sample")
        self.assertEqual(geo.place_memories[0].position, (0, 1))

    def test_route_for_food_water_or_unnamed_type(self):
        surveys=(ObservedSurvey(
            position=(1, 0), world_step=2,
            free_neighbors=((0, 0), (2, 0)),
        ),)
        for entity_id, kind in (
            ("water_source:0", "water_source"),
            ("berry_a:1:0", "berry_a"),
            ("artifact:1", "undiscovered_type"),
        ):
            place=sample(entity_id, kind)
            got=find_spatial_return(
                origin=(2, 0),
                visits=frozenset(((0, 0), (1, 0), (2, 0))),
                surveys=surveys, places=(place,),
                current_free_neighbors=frozenset(((1, 0),)),
                current_world_step=4,
            )
            self.assertIsNotNone(got)
            self.assertEqual(got.entity_id, entity_id)
            self.assertEqual(got.destination, (1, 0))

    def test_unobserved_edge_never_made_up(self):
        got=find_spatial_return(
            origin=(2, 0), visits=frozenset(((0, 0), (2, 0))),
            surveys=(), places=(sample(),),
            current_free_neighbors=frozenset(), current_world_step=4,
        )
        self.assertIsNone(got)

    def test_future_and_duplicate_entity_ids_are_rejected(self):
        kwargs=dict(origin=(2, 0), visits=frozenset(((2, 0),)),
                    surveys=(), current_free_neighbors=frozenset(((1, 0),)),
                    current_world_step=4)
        with self.assertRaises(ValueError):
            find_spatial_return(places=(sample(step=5),), **kwargs)
        with self.assertRaises(ValueError):
            find_spatial_return(places=(sample(), sample()), **kwargs)

    def test_owner_snapshot_roundtrip_is_independent(self):
        geo=owner()
        seen=capture(1, 0, 0, (("berry_a:1:0", "berry_a", 1, 0),))
        geo.observe_capture(seen)
        geo.observe_entities(seen, observer_id="i1:sample")
        state=geo.export_causal_state()
        cold=owner()
        cold.restore_causal_state(state)
        self.assertEqual(cold.place_memories, geo.place_memories)
        tampered=dict(state, entity_places=[dict(state["entity_places"][0],
                                                last_seen_step=999)])
        with self.assertRaises(ValueError):
            cold.restore_causal_state(tampered)
        self.assertEqual(cold.place_memories, geo.place_memories)
