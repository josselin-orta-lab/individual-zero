"""Deterministic generic I1 spatial-memory tests with no third-party packages."""
import unittest
from types import SimpleNamespace
from dataclasses import replace

# Source-only tests: avoid importing i0's historical Lab namespace and do
# not write __pycache__ into src/, which would break the I0/I1 tree guard.
import importlib.util
from pathlib import Path
import sys
import types

_MODULES = Path(__file__).resolve().parents[2] / "src/i1/modules"
_NS = "_i1_spatial_314"
_PACKAGE = types.ModuleType(_NS)
_PACKAGE.__path__ = [str(_MODULES)]
sys.modules[_NS] = _PACKAGE
_prior_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    for _name in ("observed_frontier_routing", "spatial_memory",
                  "geographic_exploration"):
        _spec = importlib.util.spec_from_file_location(
            f"{_NS}.{_name}", _MODULES / f"{_name}.py")
        _module = importlib.util.module_from_spec(_spec)
        sys.modules[_spec.name] = _module
        _spec.loader.exec_module(_module)
finally:
    sys.dont_write_bytecode = _prior_bytecode
Spatial = sys.modules[f"{_NS}.spatial_memory"]
Geography = sys.modules[f"{_NS}.geographic_exploration"]
ObservedSurvey = sys.modules[f"{_NS}.observed_frontier_routing"].ObservedSurvey
PlaceMemory, find_spatial_return = Spatial.PlaceMemory, Spatial.find_spatial_return
find_spatial_returns = Spatial.find_spatial_returns
GeographicExploration = Geography.GeographicExploration
GeographicExplorationConfig = Geography.GeographicExplorationConfig


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
        max_place_candidates=3,
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
        self.assertEqual({m.position for m in geo.place_memories}, {(1, 0), (0, 1)})
        self.assertTrue(any(m.contradictions == 1 for m in geo.place_memories))

    def test_reused_sensor_label_does_not_merge_distinct_water_sites(self):
        geo = owner()
        first = capture(1, 0, 0, (("water_source:0", "water_source", 1, 0),))
        geo.observe_capture(first)
        geo.observe_entities(first, observer_id="i1:sample")
        second = capture(2, 0, 2, (("water_source:0", "water_source", 1, 2),))
        geo.observe_capture(second)
        geo.observe_entities(second, observer_id="i1:sample")
        self.assertEqual(len(geo.place_memories), 2)
        self.assertEqual({m.position for m in geo.place_memories}, {(1, 0), (1, 2)})

    def test_mobility_diagnosis_requires_consecutive_unique_sightings(self):
        geo = owner()
        for t, pos in ((1, (1, 0)), (2, (1, 0)), (3, (1, 0)),
                       (4, (0, 1))):
            c = capture(t, 0, 0, (("creature:0", "creature", *pos),))
            geo.observe_capture(c)
            geo.observe_entities(c, observer_id="i1:sample")
        motion = geo.motion_diagnoses[0]
        self.assertEqual(motion.diagnosis, "mobile_probable")
        self.assertEqual(motion.observed_moves, 1)
        self.assertEqual(motion.identity_certainty, "tentative")
        cold = owner()
        cold.restore_causal_state(geo.export_causal_state())
        self.assertEqual(cold.motion_diagnoses, geo.motion_diagnoses)

    def test_stable_observation_is_only_apparent_immobility(self):
        geo = owner()
        for t in (1, 2, 3):
            c = capture(t, 0, 0, (("object", "unknown_kind", 1, 0),))
            geo.observe_capture(c)
            geo.observe_entities(c, observer_id="i1:sample")
        self.assertEqual(geo.motion_diagnoses[0].diagnosis, "immobile_apparente")
        self.assertEqual(geo.motion_diagnoses[0].identity_certainty, "tentative")

    def test_multiple_indistinguishable_entities_break_identity_link(self):
        geo = owner()
        first = capture(1, 0, 0, (("creature:0", "creature", 1, 0),))
        geo.observe_capture(first)
        geo.observe_entities(first, observer_id="i1:sample")
        ambiguous = capture(2, 0, 0, (
            ("creature:0", "creature", 1, 0),
            ("creature:1", "creature", 0, 1),
        ))
        geo.observe_capture(ambiguous)
        geo.observe_entities(ambiguous, observer_id="i1:sample")
        self.assertEqual(geo.motion_diagnoses, ())
        after = capture(3, 0, 0, (("creature:1", "creature", 0, 1),))
        geo.observe_capture(after)
        geo.observe_entities(after, observer_id="i1:sample")
        self.assertEqual(geo.motion_diagnoses[0].diagnosis, "indetermine")

    def test_gap_prevents_false_motion_or_stationarity(self):
        geo = owner()
        for t, entities in (
            (1, (("creature:0", "creature", 1, 0),)),
            (2, ()),
            (3, (("creature:0", "creature", 0, 1),)),
        ):
            c = capture(t, 0, 0, entities)
            geo.observe_capture(c)
            geo.observe_entities(c, observer_id="i1:sample")
        self.assertEqual(geo.motion_diagnoses[0].observations, 1)
        self.assertEqual(geo.motion_diagnoses[0].diagnosis, "indetermine")

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


    def test_retrieval_returns_distinct_alternatives(self):
        water = sample("water_source:0", "water_source")
        berry = replace(sample("berry_a:1:0", "berry_a"),
                        position=(0, 1), observed_from=(0, 0))
        found = find_spatial_returns(
            origin=(0, 0), visits=frozenset(((0, 0),)),
            surveys=(), places=(water, berry),
            current_free_neighbors=frozenset(((1, 0), (0, 1))),
            current_world_step=2, max_candidates=2,
        )
        self.assertEqual({t.entity_type for t in found}, {"water_source", "berry_a"})
        self.assertEqual(len(found), 2)

    def test_owner_can_freeze_two_real_spatial_alternatives(self):
        geo = owner()
        observed = capture(1, 0, 0, (
            ("berry_a:1:0", "berry_a", 1, 0),
            ("water_source:0", "water_source", 0, 1),
        ))
        geo.observe_capture(observed)
        geo.observe_entities(observed, observer_id="i1:sample")
        second = capture(2, 0, 0, (
            ("berry_a:1:0", "berry_a", 1, 0),
            ("water_source:0", "water_source", 0, 1),
        ))
        geo.observe_capture(second)
        candidates = find_spatial_returns(
            origin=(0, 0), visits=frozenset(((0, 0),)),
            surveys=(), places=geo.place_memories,
            current_free_neighbors=frozenset(((1, 0), (0, 1))),
            current_world_step=2, max_candidates=3)
        self.assertEqual(len(candidates), 2)
        geo.freeze_places(candidates)
        self.assertEqual(len(geo._place_offered), 2)
        cold = owner()
        cold.restore_causal_state(geo.export_causal_state())
        self.assertEqual(cold._place_offered, geo._place_offered)

    def test_stale_offer_contradiction_is_withdrawn_without_exception(self):
        geo = owner()
        first = capture(1, 0, 0, (("berry_a:1:0", "berry_a", 1, 0),))
        geo.observe_capture(first)
        geo.observe_entities(first, observer_id="i1:sample")
        at2 = capture(2, 0, 0)
        geo.observe_capture(at2)
        # Freeze Phase-0 belief, as Planning does before Phase-1 observation.
        original = geo.place_memories
        target = find_spatial_return(
            origin=(0, 0), visits=frozenset(((0, 0),)),
            surveys=(), places=original,
            current_free_neighbors=frozenset(((1, 0),)),
            current_world_step=2,
        )
        self.assertIsNotNone(target)
        geo.observe_entities(at2, observer_id="i1:sample")
        self.assertLess(geo.place_memories[0].confidence, target.confidence)
        geo.freeze_place(target)
        self.assertEqual(geo._place_offered, ())

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
