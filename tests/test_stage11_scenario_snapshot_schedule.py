"""Stage11 external scenario snapshot integrity, synthetic unit-only."""
from copy import deepcopy
from unittest import TestCase

from lab.injected_scenario import InjectedScenario, ScenarioEvent
from lab.journal import HashChainedJournal
from lab.snapshots import SnapshotType
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.world import Position


SCHEDULE = (
    ScenarioEvent(
        t_monde=2, sequence=1, operation="set_position",
        payload={"position": {"x": 4, "y": 2}},
    ),
    ScenarioEvent(
        t_monde=3, sequence=1, operation="set_danger_zone",
        payload={"position": {"x": 3, "y": 2}, "active": True},
    ),
)


def scenario(journal):
    return InjectedScenario(
        scenario_id="stage11-public-world-scenario-unit",
        version="external-position-known-hazards-v1",
        events=SCHEDULE,
        journal=journal,
    )


class Stage11ScenarioSnapshotScheduleTests(TestCase):
    def test_unjournalable_external_input_rejected_before_world_step(self):
        # An unencodable causal input cannot be received into a valid
        # hash-chained journal and must fail before any Scheduler tick.
        bad = (
            ScenarioEvent(0, 0, "set_position", {"position": {"x": 4, "y": 2}}),
            ScenarioEvent(True, 0, "set_position", {"position": {"x": 4, "y": 2}}),
            ScenarioEvent(1, -1, "set_position", {"position": {"x": 4, "y": 2}}),
            ScenarioEvent(1, False, "set_position", {"position": {"x": 4, "y": 2}}),
            ScenarioEvent(1, 0, "  ", {"position": {"x": 4, "y": 2}}),
            ScenarioEvent(1, 0, "set_position", None),
            ScenarioEvent(1, 0, "set_danger_zone", {"active": float("nan")}),
            ScenarioEvent(1, 0, "set_danger_zone", {"active": float("inf")}),
            ScenarioEvent(1, 0, "set_danger_zone", {"extra": {1, 2}}),
            ScenarioEvent(1, 0, "set_danger_zone", {3: "invalid_key"}),
        )
        for index, bad_event in enumerate(bad):
            journal = HashChainedJournal()
            with self.subTest(case=index), self.assertRaisesRegex(
                ValueError,
                "malformed external scenario event schema|not canonically encodable",
            ):
                InjectedScenario(
                    scenario_id="stage11-input-schema-unit",
                    version="canonical-v1",
                    events=(bad_event,),
                    journal=journal,
                )
            self.assertEqual(journal.entries, ())
            self.assertTrue(journal.verify())

        # A semantically invalid but canonically representable physical
        # destination is a runtime rejection, never a registration error.
        journal = HashChainedJournal()
        admitted = InjectedScenario(
            scenario_id="stage11-input-schema-unit",
            version="canonical-v1",
            events=(ScenarioEvent(
                1, 0, "set_position", {"position": {"x": 0, "y": 2}},
            ),),
            journal=journal,
        )
        self.assertEqual(admitted.export_causal_state()["next_index"], 0)
        self.assertEqual(journal.entries, ())

    def test_restores_only_the_exact_original_external_event_program(self):
        journal = HashChainedJournal()
        runner = build_public_route_runtime(
            layout_variant="junction_open", survey_refresh=True,
        )
        before = runner.world.export_causal_state()
        instance = scenario(journal)
        self.assertEqual(len(instance.apply_for_step(
            t_monde=2, world=runner.world,
        )), 1)
        self.assertNotEqual(runner.world.export_causal_state(), before)
        self.assertEqual(runner.world.position, Position(4, 2))

        checkpoint = instance.export_causal_state()
        self.assertEqual(checkpoint["next_index"], 1)
        world_state = deepcopy(runner.world.export_causal_state())
        journal_bytes = journal.canonical_bytes()
        self.assertTrue(journal.verify())

        cases = []
        changed_position = deepcopy(checkpoint)
        changed_position["events"][0]["payload"]["position"]["x"] = 3
        cases.append(("different external target", changed_position,
                      "scenario event schedule mismatch"))
        changed_operation = deepcopy(checkpoint)
        changed_operation["events"][1]["operation"] = "set_lethal_zone"
        cases.append(("different hazard operation", changed_operation,
                      "scenario event schedule mismatch"))
        missing_events = deepcopy(checkpoint)
        missing_events.pop("events")
        cases.append(("missing schedule", missing_events,
                      "scenario event schedule mismatch"))
        changed_order = deepcopy(checkpoint)
        changed_order["events"].reverse()
        cases.append(("different future event order", changed_order,
                      "scenario event schedule mismatch"))
        bad_cursor = deepcopy(checkpoint)
        bad_cursor["next_index"] = True
        cases.append(("Boolean cursor", bad_cursor, "invalid scenario next_index"))
        out_of_range = deepcopy(checkpoint)
        out_of_range["next_index"] = 10
        cases.append(("out of range cursor", out_of_range,
                      "invalid scenario next_index"))

        for case_name, corrupted, error in cases:
            with self.subTest(case=case_name):
                with self.assertRaisesRegex(ValueError, error):
                    instance.restore_causal_state(corrupted)
                self.assertEqual(instance.export_causal_state(), checkpoint)
                self.assertEqual(runner.world.export_causal_state(), world_state)
                self.assertEqual(journal.canonical_bytes(), journal_bytes)

        independently_instantiated = scenario(HashChainedJournal())
        independently_instantiated.restore_causal_state(deepcopy(checkpoint))
        self.assertEqual(
            independently_instantiated.export_causal_state(), checkpoint,
        )
        self.assertTrue(journal.verify())


    def test_runtime_full_owner_restore_rejects_different_scenario_atomically(self):
        # Both runtimes use the same public world and scenario id/version,
        # but different *external physical event* programs. A snapshot of
        # the first must not partially overwrite the second one's life.
        first = build_public_route_runtime(
            scenario_events=SCHEDULE, survey_refresh=True,
        )
        alternative = (
            ScenarioEvent(
                t_monde=2, sequence=1, operation="set_position",
                payload={"position": {"x": 3, "y": 2}},
            ),
            SCHEDULE[1],
        )
        second = build_public_route_runtime(
            scenario_events=alternative, survey_refresh=True,
        )
        first.run_step()
        snapshots = first.stage3.substrate.snapshots
        saved = snapshots.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id=first.individual_id,
            t_monde=1, cycle=0, attempt_ref=None,
            owners=first.causal_owners,
            versions={"stage11": first._stage11_config.version},
        )
        second.run_step()
        second.run_step()
        before = {
            owner.owner_id: deepcopy(owner.export_causal_state())
            for owner in second.causal_owners
        }
        first_journal = first.journal.canonical_bytes()
        second_journal = second.journal.canonical_bytes()
        self.assertIn("scenario", before)
        self.assertNotEqual(
            before["scenario"]["events"], snapshots.export_payload(
                saved.id,
            )["owner_states"]["scenario"]["events"],
        )
        with self.assertRaisesRegex(
            ValueError, "scenario event schedule mismatch",
        ):
            snapshots.restore(saved.id, owners=second.causal_owners)
        self.assertEqual(
            {
                owner.owner_id: owner.export_causal_state()
                for owner in second.causal_owners
            },
            before,
        )
        self.assertEqual(first.journal.canonical_bytes(), first_journal)
        self.assertEqual(second.journal.canonical_bytes(), second_journal)
        self.assertTrue(snapshots.verify(saved.id))
        self.assertTrue(first.journal.verify())
        self.assertTrue(second.journal.verify())


if __name__ == "__main__":
    import unittest
    unittest.main()
