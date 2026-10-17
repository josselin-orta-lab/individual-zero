"""Stage-9 epistemic confounding gate with REAL WorldBody transitions.

These are development-only software regressions, not scientific validation.
The Lab observes the hidden physics for its own assertions, but CausalModel
receives only applied-action provenance and Stage-2 autobiographical views.
"""

from __future__ import annotations

import unittest

from i0.modules.causal_model import CausalModel, CausalModelConfig
from lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command


class Stage9LivedAmbientConfoundTests(unittest.TestCase):
    def exercise_genuine_berry(self, *, hidden_danger: bool):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        world = runtime.world
        sub = runtime.stage3.substrate
        here = world.position.as_dict()
        world.apply_scenario_event(
            "place_resource",
            {"position": here, "kind": "berry_a", "quantity": 1},
        )
        if hidden_danger:
            world.apply_scenario_event(
                "set_danger_zone",
                {"position": here, "active": True},
            )
        model = CausalModel(CausalModelConfig(
            "confounded-berry-development-v1", 2, 2, 2, 2,
        ))
        # Step 1: ordinary resource collection, actually applied in WorldBody.
        sub.open_step()
        collect = sub.execute(Command("collecter", {"target": "berry_a"}))
        self.assertEqual(collect.status, "applied")
        self.assertEqual(world.inventory()["berry_a"], 1)

        # Step 2: one actually applied no-food control on the same site.
        model.record_applied_ambient_integrity_control(
            t_monde=2, option_ref="option:lived-wait",
            position=(world.position.x, world.position.y),
            integrity_before=world.body.integrity,
        )
        sub.open_step()
        wait = sub.execute(Command("attendre"))
        self.assertEqual(wait.status, "applied")
        model.observe_followup_capture(
            t_monde=3, integrity=world.body.integrity,
        )
        before_food = world.body.integrity
        model.record_applied_food_exposure(
            t_monde=3, resource_kind="berry_a",
            option_ref="option:lived-food", motive_ref="goal:food",
            integrity_before=before_food,
            position_before=(world.position.x, world.position.y),
            body_before=dict(world.body.as_dict()),
        )

        # Step 3: berry_a itself is non-toxic in the frozen reference physics.
        sub.open_step()
        meal = sub.execute(Command("manger", {"target": "berry_a"}))
        self.assertEqual(meal.status, "applied")
        model.observe_followup_capture(
            t_monde=4, integrity=world.body.integrity,
        )
        projected = sub.autobiographical_view()
        technical = sub.journal.entries
        self.assertTrue(sub.journal.verify())
        self.assertTrue(any(
            event.causal_event.get("kind") == "world_transition_experienced"
            and event.causal_event.get("t_monde") == 3
            for event in technical
        ))
        # No actual physics-origin damage explanation may enter the I0 memory.
        self.assertNotIn("danger_zone_damage", repr(projected))
        self.assertNotIn("creature_damage", repr(projected))
        self.assertNotIn("oracle_canary", repr(projected))
        rows = {}
        for step in (2, 3):
            events = tuple(
                e for e in projected if e.get("t_monde") == step
                and e.get("kind") in {
                    "command_experienced", "world_transition_experienced",
                }
            )
            self.assertEqual(len(events), 2)
            rows[step] = model.ingest_closed_autobiographical_episode(
                episode_ref=f"episode:{step}",
                event_refs=tuple(e["event_id"] for e in events),
                autobiographical_events=events,
            )
        self.assertEqual(rows[2], ())
        return model, world, technical, rows[3]

    def test_non_toxic_berry_plus_hidden_danger_is_not_safety_proof(self):
        for individual_birth in (1, 2):
            with self.subTest(birth=individual_birth):
                model, world, journal, admitted = self.exercise_genuine_berry(
                    hidden_danger=True,
                )
                self.assertLess(world.body.integrity, 100)
                self.assertTrue(any(
                    e.causal_event.get("kind") == "world_transition_experienced"
                    and e.causal_event.get("effects", {}).get("danger_zone_damage", 0) > 0
                    for e in journal
                ))
                self.assertEqual(admitted, ())
                self.assertEqual(model.pending_causal_observations(), ())
                self.assertEqual(
                    model.export_causal_state()["pending_numeric_witnesses"], [],
                )
                self.assertEqual(model.publish(), ())
                self.assertIsNone(model.get("toxic:berry_a"))

    def test_non_toxic_berry_with_clean_wait_is_still_lived(self):
        model, world, journal, admitted = self.exercise_genuine_berry(
            hidden_danger=False,
        )
        self.assertEqual(world.body.integrity, 100.0)
        self.assertEqual(len(admitted), 1)
        self.assertFalse(admitted[0].harm_observed)
        self.assertEqual(model.publish(), ())
        self.assertEqual(model.get("toxic:berry_a").safety_status, "aucun")
        self.assertTrue(journal)


if __name__ == "__main__":
    unittest.main()
