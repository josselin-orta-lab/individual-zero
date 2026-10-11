"""Stage 11 public guarded lethal checkpoint and physically grounded rollback.

One world step, no oracle reads, no promotion of lethal WorldBody truth into
the individual. This is software regression, not held-out science.
"""
from dataclasses import replace
from unittest import TestCase

from lab.determinism import canonical_causal_bytes
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import Position


class Stage11GuardedLethalRollbackTests(TestCase):
    def test_real_unknown_lethal_east_and_complete_guarded_rollback(self):
        def independent():
            original = build_public_route_runtime(
                layout_variant="junction_open",
                planning_uc=4,
                exploration_uc=4,
                survey_refresh=True,
                cycle_occurrence_guard=True,
            )
            cfg = replace(
                original._stage11_config,
                version=(
                    original._stage11_config.version
                    + "+guarded-lethal-physical-dev-v1"
                ),
            )
            runner = Stage11Runtime(
                world_config=original.world.config,
                layout=replace(
                    original.world._layout,
                    lethal_zones=frozenset({Position(3, 2)}),
                ),
                safety_config=original.stage3.substrate.safety._config,
                safety_facts=original._canonical_safety._innate,
                protected_integrity_threshold=(
                    original.stage3.control._config.protected_integrity_threshold
                ),
                config=cfg,
                equipment=original.equipment,
            )
            self.assertTrue(
                runner._config.compute_budget.cycle_occurrence_guard,
            )
            self.assertEqual(
                runner._canonical_safety.zone_status(x=3, y=2),
                "unknown",
            )
            result = runner.run_step()
            self.assertEqual(runner.bench.metrics.lethal_transitions, 1)
            self.assertEqual(runner.bench.metrics.lethal_rollbacks, 1)
            self.assertIn(
                result.execution_status, {"applied", "safety_block"},
            )
            self.assertNotEqual(runner.world.position, Position(3, 2))
            self.assertEqual(runner.world.position, Position(2, 2))
            self.assertEqual(
                runner._canonical_safety.zone_status(x=3, y=2),
                "unknown",
            )
            self.assertTrue(runner.journal.verify())

            ev = [entry.causal_event for entry in runner.journal.entries]
            kinds = [entry["kind"] for entry in ev]
            self.assertEqual(kinds.count("lethal_transition_detected"), 1)
            self.assertEqual(kinds.count("lethal_rollback_completed"), 1)
            self.assertGreaterEqual(kinds.count("snapshot_restored"), 1)
            boundary = kinds.index("lethal_rollback_completed")
            before = [
                event for index, event in enumerate(ev)
                if event["kind"] == "cycle_opened" and index < boundary
            ]
            after = [
                event for index, event in enumerate(ev)
                if event["kind"] == "cycle_opened" and index > boundary
            ]
            self.assertTrue(before)
            self.assertTrue(after)
            self.assertEqual(before[-1]["t_monde"], 1)
            self.assertEqual(after[0]["t_monde"], 1)
            self.assertNotEqual(
                before[-1]["attempt_ref"], after[0]["attempt_ref"],
            )
            self.assertGreater(after[0]["cycle"], before[-1]["cycle"])
            owner = runner.compute_budget.export_causal_state()
            self.assertEqual(
                owner["active_occurrence"],
                {
                    "t_monde": after[-1]["t_monde"],
                    "attempt_ref": after[-1]["attempt_ref"],
                    "cycle": after[-1]["cycle"],
                },
            )
            self.assertGreater(owner["consumed_cycle_uc"], 0)
            self.assertLessEqual(
                owner["consumed_cycle_uc"],
                runner._config.compute_budget.cycle_ceiling,
            )

            autobiography = runner.stage3.substrate.autobiographical_view()
            # The rolled-back movement into (3,2) must not become personal
            # history or a learned canonical danger.
            autobiographical_commands = [
                row["primitive"] for row in autobiography
                if "primitive" in row
            ]
            self.assertNotIn("se_deplacer", autobiographical_commands)
            self.assertTrue(all(
                row.get("t_monde") == 1 for row in autobiography
            ))
            if result.execution_status == "applied":
                self.assertIn("attendre", autobiographical_commands)
                self.assertEqual(runner.scheduler.t_monde, 1)
            self.assertEqual(
                len([
                    event for event in ev
                    if event["kind"] == "world_transition_experienced"
                ]),
                1 if result.execution_status == "applied" else 0,
            )

            owners = {
                item.owner_id: item.export_causal_state()
                for item in runner.causal_owners
            }
            return (
                result, owner, runner.bench.metrics.lethal_transitions,
                runner.bench.metrics.lethal_rollbacks,
                tuple((v["kind"], v["attempt_ref"]) for v in ev),
                canonical_causal_bytes(owners),
                runner.journal.canonical_bytes(),
                runner.journal.head_hash,
            )

        self.assertEqual(independent(), independent())
