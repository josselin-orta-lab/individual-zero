"""Stage11 hidden world-danger changes under strict UC, public unit-only.

This does not fabricate learned danger knowledge. Truth comparisons are made
only by the test harness; the individual receives ordinary local Perception.
"""
from copy import deepcopy
from unittest import TestCase

from lab.injected_scenario import ScenarioEvent
from lab.snapshots import SnapshotType
from lab.stage11_routed_junction_probe import build_public_route_runtime


BUDGETS = ((0, 0), (1, 4), (4, 4))
DANGER_POS = {"x": 3, "y": 2}


def build(*, planning_uc: int, exploration_uc: int, dangerous: bool):
    return build_public_route_runtime(
        layout_variant="junction_open",
        planning_uc=planning_uc,
        exploration_uc=exploration_uc,
        survey_refresh=True,
        scenario_events=(ScenarioEvent(
            t_monde=3, sequence=0, operation="set_danger_zone",
            payload={"position": dict(DANGER_POS), "active": dangerous},
        ),),
    )


def entries(runtime, kind):
    return [
        entry.causal_event for entry in runtime.journal.entries
        if entry.causal_event.get("kind") == kind
    ]


def owner_states(runtime):
    return {
        o.owner_id: deepcopy(o.export_causal_state())
        for o in runtime.causal_owners
    }


def action(row):
    return (
        row.source, row.execution_status,
        row.command_primitive, row.option_ref,
    )


def run_three(*, planning_uc, exploration_uc, dangerous):
    runtime = build(
        planning_uc=planning_uc, exploration_uc=exploration_uc,
        dangerous=dangerous,
    )
    self_actions = []
    for step in (1, 2, 3):
        if step == 3:
            if runtime._canonical_safety.zone_status(
                x=3, y=2,
            ) != "unknown":
                raise AssertionError("hidden physical hazard was known prematurely")
        self_actions.append(action(runtime.run_step()))
    if not runtime.journal.verify():
        raise AssertionError("invalid hash-chained journal")
    return runtime, tuple(self_actions)


class Stage11HiddenDangerStrictUCTests(TestCase):
    def test_external_hidden_danger_does_not_enter_decision_before_observation(self):
        for planning_uc, exploration_uc in BUDGETS:
            with self.subTest(
                planning_uc=planning_uc, exploration_uc=exploration_uc,
            ):
                control, control_actions = run_three(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    dangerous=False,
                )
                danger, danger_actions = run_three(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    dangerous=True,
                )

                # The dangerous world-input happens before step-3 Perception
                # but its hidden label is not present in local capture. Damage
                # can legitimately change later decisions, never prior ones.
                self.assertEqual(control_actions, danger_actions)
                self.assertEqual(
                    [row["data"] for row in entries(
                        control, "perceptual_capture",
                    )],
                    [row["data"] for row in entries(
                        danger, "perceptual_capture",
                    )],
                )
                for owner, expected_active in (
                    (control, False), (danger, True),
                ):
                    received = entries(owner, "external_input_received")
                    applied = entries(owner, "external_input_applied")
                    self.assertEqual(len(received), 1)
                    self.assertEqual(len(applied), 1)
                    self.assertEqual(received[0]["t_monde"], 3)
                    self.assertEqual(applied[0]["t_monde"], 3)
                    self.assertEqual(
                        received[0]["operation"], "set_danger_zone",
                    )
                    self.assertEqual(
                        received[0]["payload"]["position"], DANGER_POS,
                    )
                    self.assertIs(
                        received[0]["payload"]["active"], expected_active,
                    )
                    self.assertFalse(entries(owner, "external_input_rejected"))

                    visited = {
                        tuple(row[:2]) for row in
                        owner.exploration.geographic.export_causal_state()["visits"]
                    }
                    perceived = {
                        (row["data"]["position"]["x"],
                         row["data"]["position"]["y"])
                        for row in entries(owner, "perceptual_capture")
                    }
                    self.assertEqual(visited, perceived)
                    charges = [
                        row["data"] for row in entries(owner, "compute_charge")
                    ]
                    if planning_uc == 0:
                        self.assertFalse(any(
                            c.get("module") == "planning"
                            and c.get("accepted") is True for c in charges
                        ))
                    if exploration_uc == 0:
                        self.assertFalse(any(
                            c.get("module") == "exploration"
                            and c.get("operation") == "exploration_observe"
                            and c.get("accepted") is True for c in charges
                        ))
                    self.assertTrue(all(
                        row["data"].get("safety_decision") is None
                        for row in entries(
                            owner, "stage11_geographic_budget_deferred",
                        )
                    ))
                    self.assertTrue(owner.journal.verify())

                self.assertEqual(
                    control.world.export_causal_state()["danger_zones"], [],
                )
                self.assertEqual(
                    danger.world.export_causal_state()["danger_zones"],
                    [DANGER_POS],
                )

    def test_hidden_danger_after_step_boundary_snapshot_restores_every_owner(self):
        for planning_uc, exploration_uc in ((0, 0), (4, 4)):
            with self.subTest(
                planning_uc=planning_uc, exploration_uc=exploration_uc,
            ):
                runtime, _ = run_three(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    dangerous=True,
                )
                owners = runtime.causal_owners
                frozen = owner_states(runtime)
                manager = runtime.stage3.substrate.snapshots
                record = manager.take(
                    snapshot_type=SnapshotType.PERIODIC,
                    individual_id=runtime.individual_id,
                    t_monde=3, cycle=0, attempt_ref=None,
                    owners=owners,
                    versions={"stage11": runtime._stage11_config.version},
                )
                self.assertTrue(manager.verify(record.id))
                runtime.run_step()
                manager.restore(record.id, owners=owners)
                self.assertEqual(owner_states(runtime), frozen)
                self.assertEqual(
                    runtime.world.export_causal_state()["danger_zones"],
                    [DANGER_POS],
                )
                self.assertTrue(manager.verify(record.id))
                self.assertTrue(runtime.journal.verify())

    def test_same_versioned_inputs_independently_replay(self):
        for planning_uc, exploration_uc in BUDGETS:
            with self.subTest(
                planning_uc=planning_uc, exploration_uc=exploration_uc,
            ):
                a, actions_a = run_three(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    dangerous=True,
                )
                b, actions_b = run_three(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    dangerous=True,
                )
                self.assertEqual(actions_a, actions_b)
                self.assertEqual(a.journal.canonical_bytes(),
                                 b.journal.canonical_bytes())
                self.assertEqual(owner_states(a), owner_states(b))


if __name__ == "__main__":
    import unittest
    unittest.main()
