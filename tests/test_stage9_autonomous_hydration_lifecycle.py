"""Stage-9 spontaneous hydration lifecycle over genuinely applied WorldBody steps.

The bench chooses the test sequence for controlled assertions. CausalModel
only receives individual-accessible next-step Perception and source events
mirroring the closed DC-09 autobiographical projection; no oracle, world
configuration or bench truth enters the canonical causal owner.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.causal_model import CausalModel, CausalModelConfig
from i0.modules.perception import SymbolicPerception
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import WorldBody, WorldLayout


def rig(*, drink_gain: float = 20.0):
    source = build_stage4_reference_runtime()
    world_config = replace(
        source.world.config,
        version="stage9-hydration-lifecycle-physical-v1",
        drink_water_gain=drink_gain,
    )
    world = WorldBody(
        config=world_config,
        layout=WorldLayout(
            water_sources=frozenset({world_config.initial_position}),
        ),
    )
    model = CausalModel(CausalModelConfig(
        version="stage9-hydration-lifecycle-causal-v1",
        n1=2, n2=2, n_sec=2, m_sec=2,
        causal_predicates=("hydration_effect",),
        safe_test_actions=(("hydration_effect", "water", "boire"),),
    ))
    return world, model


def physical_sample(world, model, *, step: int, primitive: str):
    """Actually change world state, then provide only Perception to model."""
    before = SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry(),
    )
    self_position = world.config.initial_position
    admitted = model.record_applied_hydration_observation(
        t_monde=step, primitive=primitive,
        option_ref=f"option:real:{step}:{primitive}",
        current_water_source=True,
        position=(self_position.x, self_position.y),
        water_before=float(before.body["water"]),
    )
    assert admitted
    result = world.apply(PrimitiveCommand(primitive), t_monde=step)
    assert not result.lethal
    perception = SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step + 1).as_dict(),
        telemetry=world.telemetry(),
    )
    model.observe_hydration_followup(
        t_monde=step + 1,
        water=float(perception.body["water"]),
    )
    assert float(perception.body["water"]) == result.body_after.water
    events = (
        {
            "event_id": f"command:{step}",
            "kind": "command_experienced",
            "t_monde": step, "primitive": primitive, "parameters": {},
        },
        {
            "event_id": f"transition:{step}",
            "kind": "world_transition_experienced",
            "t_monde": step,
            "effects": dict(result.effects),
            "body_after": result.body_after.as_dict(),
            "position_after": result.position_after.as_dict(),
        },
    )
    return events


def close(model, *, episode_ref: str, events):
    return model.ingest_closed_hydration_episode(
        episode_ref=episode_ref,
        event_refs=tuple(event["event_id"] for event in events),
        autobiographical_events=events,
    )


class AutonomousHydrationLifecycleTests(unittest.TestCase):
    def test_physical_drinks_and_independent_wait_reach_hypothesis_in_stages(self):
        world, model = rig()
        for step in (1, 2):
            (observation,) = close(
                model, episode_ref=f"episode:{step}",
                events=physical_sample(
                    world, model, step=step, primitive="boire",
                ),
            )
            self.assertTrue(observation.cause_present)
            self.assertTrue(observation.effect_present)
            self.assertEqual(model.publish_causal_inference(), ())
            self.assertEqual(
                model.get("causal:hydration").causal_status, "aucun",
            )
            self.assertEqual(model.proposer_test(), ())

        (control,) = close(
            model, episode_ref="episode:3",
            events=physical_sample(
                world, model, step=3, primitive="attendre",
            ),
        )
        self.assertFalse(control.cause_present)
        self.assertFalse(control.effect_present)
        self.assertEqual(
            [change.after for change in model.publish_causal_inference()],
            ["correlation_observee"],
        )
        self.assertEqual(model.proposer_test(), ())
        self.assertEqual(
            [change.after for change in model.publish_causal_inference()],
            ["hypothese_causale"],
        )
        (target,) = model.proposer_test()
        self.assertEqual(target.primitive, "boire")
        self.assertEqual(target.contingency_ref, "causal:hydration")
        state = model.export_causal_state()
        self.assertEqual(len(state["causal_observations"]), 3)
        self.assertEqual(len(state["hydration_observation_witnesses"]), 3)
        self.assertEqual(len(state["causal_reviews"]), 1)
        self.assertEqual(state["causal_interventions"], [])
        self.assertEqual(model.publish_causal_inference(), ())

        restored = rig()[1]
        restored.restore_causal_state(state)
        self.assertEqual(restored.export_causal_state(), state)
        self.assertEqual(restored.proposer_test(), model.proposer_test())

    def test_same_episode_cannot_fake_two_independent_positive_occurrences(self):
        world, model = rig()
        first = physical_sample(world, model, step=1, primitive="boire")
        second = physical_sample(world, model, step=2, primitive="boire")
        accepted = close(
            model, episode_ref="episode:both",
            events=(*first, *second),
        )
        self.assertEqual(len(accepted), 0)
        model.publish_causal_inference()
        self.assertEqual(
            len(model.export_causal_state()["hydration_observation_witnesses"]),
            0,
        )
        self.assertEqual(len(model.export_causal_state()["causal_observations"]), 0)

        close(
            model, episode_ref="episode:control",
            events=physical_sample(world, model, step=3, primitive="attendre"),
        )
        self.assertEqual(model.publish_causal_inference(), ())
        self.assertEqual(model.get("causal:hydration").causal_status, "aucun")
        self.assertEqual(model.proposer_test(), ())

    def test_null_gain_never_creates_spurious_positive_correlations(self):
        world, model = rig(drink_gain=0.0)
        for step, primitive in ((1, "boire"), (2, "boire"), (3, "attendre")):
            (observation,) = close(
                model, episode_ref=f"episode:{step}",
                events=physical_sample(
                    world, model, step=step, primitive=primitive,
                ),
            )
            self.assertFalse(observation.effect_present)
            self.assertEqual(model.publish_causal_inference(), ())
        self.assertEqual(model.get("causal:hydration").causal_status, "aucun")
        self.assertEqual(model.proposer_test(), ())

    def test_physical_witness_snapshot_cannot_be_orphaned_or_retargeted(self):
        world, model = rig()
        close(
            model, episode_ref="episode:1",
            events=physical_sample(world, model, step=1, primitive="boire"),
        )
        model.publish_causal_inference()
        baseline = model.export_causal_state()
        self.assertEqual(len(baseline["hydration_observation_witnesses"]), 1)

        orphan = deepcopy(baseline)
        orphan["hydration_observation_witnesses"].append(
            ["lived-hydration:unknown", "command:99", "transition:99"]
        )
        swapped = deepcopy(baseline)
        swapped["hydration_observation_witnesses"][0][2] = "transition:99"
        false_predicate = deepcopy(baseline)
        false_predicate["causal_observations"][0]["predicate"] = "unrelated"
        for tampered in (orphan, swapped, false_predicate):
            with self.subTest(tamper=tampered):
                with self.assertRaisesRegex(
                    ValueError, "hydration snapshot witness",
                ):
                    model.restore_causal_state(tampered)
                self.assertEqual(model.export_causal_state(), baseline)

        twin = rig()[1]
        twin.restore_causal_state(baseline)
        self.assertEqual(twin.export_causal_state(), baseline)


if __name__ == "__main__":
    unittest.main()
