"""Fatal autonomous WorldBody transitions match original physics byte for byte.

No Oracle, Bench, lethal rollback, hidden safety rescue or retroactive learning.
These scripted Stage2 controls cover actual v1.3.1 world hazards; they do not
claim that hunger/thirst alone inflict damage in the unchanged physical model.
"""
from __future__ import annotations

from dataclasses import replace
import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.mortal_execution import MortalStatus
from lab.stage2_runtime import ScriptedStage2Runtime
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import BodyState, Command, Position, WorldBody, WorldLayout


class MortalLethalPhysicsMatrixTests(unittest.TestCase):
    def test_five_distinct_fatal_hazards_preserve_baseline_physics_and_final_archive(self):
        seed = build_stage4_reference_runtime(autonomous_mortal=True)
        cfg = seed.world.config
        safety_cfg = seed.stage3.substrate.safety._config
        home = cfg.initial_position
        near = Position(home.x + 1, home.y)
        cases = (
            ("unknown_lethal_cell", cfg,
             WorldLayout(lethal_zones=frozenset({home})),
             (Command("attendre"),), "lethal_zone"),
            ("lethal_toxic_berry", cfg,
             WorldLayout(resources=((home, "berry_b", 1),)),
             (Command("collecter", {"target": "berry_b"}),
              Command("manger", {"target": "berry_b"})), "zero_integrity"),
            ("night_creature", replace(cfg, night_start_step=0,
             initial_body=BodyState(50.0, 60.0, 60.0, 5.0)),
             WorldLayout(creatures=frozenset({near})),
             (Command("attendre"),), "zero_integrity"),
            ("danger_exhaustion", replace(cfg,
             initial_body=BodyState(50.0, 60.0, 60.0, 10.0)),
             WorldLayout(danger_zones=frozenset({home})),
             (Command("attendre"),), "zero_integrity"),
            ("creature_plus_danger", replace(cfg, night_start_step=0,
             initial_body=BodyState(50.0, 60.0, 60.0, 20.0)),
             WorldLayout(creatures=frozenset({near}),
                         danger_zones=frozenset({home})),
             (Command("attendre"),), "zero_integrity"),
        )

        for case, physics, layout, commands, expected_reason in cases:
            with self.subTest(hazard=case):
                actual = ScriptedStage2Runtime(
                    config=physics, layout=layout,
                    phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
                    safety_config=safety_cfg, autonomous_mortal=True,
                )
                baseline = WorldBody(config=physics, layout=layout)
                self.assertIsNone(actual.bench)
                self.assertIsNone(actual.evaluation_trace)
                for world_step, command in enumerate(commands, start=1):
                    actual.open_step()
                    execution = actual.execute(command)
                    original_physics = baseline.apply(command, t_monde=world_step)
                    self.assertEqual(
                        canonical_causal_bytes(execution.transition.as_dict()),
                        canonical_causal_bytes(original_physics.as_dict()),
                    )
                    self.assertEqual(
                        execution.status,
                        "dead" if world_step == len(commands) else "applied",
                    )
                self.assertIn(expected_reason, execution.transition.lethal_reasons)
                self.assertEqual(actual.mortal_status, MortalStatus.DEAD)
                self.assertEqual(actual.world.export_causal_state(),
                                 baseline.export_causal_state())
                self.assertEqual(actual.scheduler.t_monde, len(commands))
                self.assertEqual(actual.snapshots._snapshots, {})
                events = [e.causal_event["kind"] for e in actual.journal.entries]
                self.assertEqual(events.count("individual_death_confirmed"), 1)
                self.assertEqual(events.count("world_transition_experienced"),
                                 len(commands))
                self.assertNotIn("lethal_rollback_completed", events)
                self.assertTrue(actual.journal.verify())
                audited = audit_export_bytes(
                    actual.journal.canonical_bytes(),
                    expected_head=actual.journal.head_hash,
                    expected_count=len(actual.journal.entries),
                )
                self.assertEqual(audited.world_steps_closed, len(commands))
                self.assertEqual(audited.terminal_deaths, 1)
                self.assertEqual(audited.autobiographical_commits,
                                 len(commands) - 1)
                frozen_world = actual.world.export_causal_state()
                with self.assertRaisesRegex(RuntimeError, "dead or halted"):
                    actual.open_step()
                self.assertEqual(actual.world.export_causal_state(), frozen_world)


if __name__ == "__main__":
    unittest.main()
