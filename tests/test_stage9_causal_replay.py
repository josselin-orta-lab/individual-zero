"""Stage-9 exact re-execution and interval replay of a physical causal test.

The hypothesis is a controlled test input prepared by the bench using the
existing typed Stage-9 test fixture. It does NOT claim autonomous formation
of that hypothesis. The drinking command, perception, DC-09 Memory closure,
P-47 attribution, and canonical intervention are produced by the real runtime.

Normative: EN MVP v1.2.1 §§9.6, 13.2, 17.1-17.3, 20.3 Stage 9; INV-03, INV-25, INV-33.
"""
from __future__ import annotations

import unittest

from lab.determinism import sha256_hex
from lab.replay import verify_reexecution, compare_causal_state
from lab.snapshots import SnapshotType
from test_stage9_causal_test_pipeline import configured_runtime
from test_stage9_causal_test_targets import hypothesis


def _reference_runtime():
    runtime = configured_runtime()
    hypothesis(runtime.causal_model)
    return runtime


def _advance(runtime, count):
    outcomes = []
    for _ in range(count):
        step = runtime.run_step()
        outcomes.append((
            step.source, step.execution_status,
            step.command_primitive, step.option_ref,
        ))
    assert runtime.journal.verify()
    return tuple(outcomes)


def _causal_replay_payload(runtime):
    """Read-only full owner states plus the exact normalized causal journal."""
    return {
        "owners": {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
        },
        "journal_sha256": sha256_hex(runtime.journal.canonical_bytes()),
        "agency_evidence_refs": [
            report.identifier
            for report in runtime.causal_model.published_agency_evidence()
        ],
    }


class Stage9CausalReplayTests(unittest.TestCase):
    def test_independent_lives_reexecute_identically_with_lived_intervention(self):
        def execute():
            runtime = _reference_runtime()
            outcomes = _advance(runtime, 11)
            state = runtime.causal_model.export_causal_state()
            self.assertEqual(
                runtime.causal_model.get("causal:hydration").causal_status,
                "testee_par_intervention",
            )
            self.assertEqual(len(state["causal_interventions"]), 1)
            self.assertEqual(len(state["causal_action_witnesses"]), 1)
            self.assertGreater(len(state["agency_evidence"]), 0)
            self.assertEqual(outcomes[0][2], "boire")
            trial = state["causal_interventions"][0]
            self.assertEqual(
                trial["observed_step"], trial["emitted_step"] + 1,
            )
            self.assertIn(
                trial["comparator_ref"],
                {item["identifier"] for item in state["agency_evidence"]},
            )
            self.assertIn(
                trial["observation_ref"],
                {
                    ref for episode in runtime.memory.episodes
                    for ref in episode.event_refs
                },
            )
            return {
                "outcomes": outcomes,
                **_causal_replay_payload(runtime),
            }

        comparison = verify_reexecution(
            execute_reference=execute,
            execute_replay=execute,
        )
        comparison.require_identical()

    def test_periodic_snapshot_restores_pending_causal_state_and_exact_suffix(self):
        original, replay = _reference_runtime(), _reference_runtime()
        self.assertEqual(_advance(original, 1), _advance(replay, 1))
        self.assertEqual(
            len(original.causal_model.export_causal_state()[
                "lived_causal_actions"
            ]), 1,
        )
        records = []
        for runtime in (original, replay):
            manager = runtime.stage3.substrate.snapshots
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id=runtime.individual_id,
                t_monde=runtime.scheduler.t_monde,
                cycle=0,
                attempt_ref=None,
                owners=runtime.causal_owners,
                versions={"causal_protocol": runtime.causal_model.config.version},
            )
            self.assertTrue(manager.verify(record.id))
            records.append(record)
        self.assertEqual(records[0].id, records[1].id)
        self.assertEqual(records[0].sha256, records[1].sha256)

        # Perturb only the replay copy's canonical state. The checkpoint
        # restoration must recover its pre-observation pending action, not
        # substitute any future answer from the first run.
        replay.causal_model.publish_causal_inference()
        self.assertNotEqual(
            original.causal_model.export_causal_state(),
            replay.causal_model.export_causal_state(),
        )
        for runtime, record in zip((original, replay), records):
            runtime.stage3.substrate.snapshots.restore(
                record.id, owners=runtime.causal_owners,
            )
        self.assertEqual(
            _causal_replay_payload(original),
            _causal_replay_payload(replay),
        )

        expected_suffix = _advance(original, 10)
        replayed_suffix = _advance(replay, 10)
        self.assertEqual(expected_suffix, replayed_suffix)
        equality = compare_causal_state(
            _causal_replay_payload(original),
            _causal_replay_payload(replay),
        )
        equality.require_identical()
        self.assertEqual(
            original.journal.canonical_bytes(),
            replay.journal.canonical_bytes(),
        )
        state = replay.causal_model.export_causal_state()
        self.assertEqual(len(state["causal_interventions"]), 1)
        self.assertEqual(len(state["causal_action_witnesses"]), 1)
        self.assertEqual(
            replay.causal_model.get("causal:hydration").causal_status,
            "testee_par_intervention",
        )

    def test_reference_without_hypothesis_does_not_infer_from_p47_alone(self):
        from lab.stage9_reference_fixture import build_stage9_reference_runtime

        def execute():
            runtime = build_stage9_reference_runtime()
            _advance(runtime, 11)
            self.assertGreater(
                len(runtime.causal_model.published_agency_evidence()), 0,
            )
            self.assertEqual(
                runtime.causal_model.export_causal_state()[
                    "causal_interventions"
                ], [],
            )
            return _causal_replay_payload(runtime)

        verify_reexecution(
            execute_reference=execute,
            execute_replay=execute,
        ).require_identical()


if __name__ == "__main__":
    unittest.main()
