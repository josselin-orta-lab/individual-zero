"""Private physical candidate parity for the not-yet-activated M-11 seam."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalWorldBoundary
from lab.sqlite_life_store import SQLiteLifeLedger
from lab.sqlite_staged_world import prepare_mortal_world_effect
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command, WorldBody, WorldLayout


class SQLitePrivatePhysicalPreparationTests(unittest.TestCase):
    def test_private_candidate_preserves_current_world_and_exact_physics(self):
        fixture = build_stage4_reference_runtime(autonomous_mortal=True)
        world = fixture.world
        original = world.export_causal_state()
        self.assertIsNotNone(world._mortal_dispatch_key)
        command = Command("attendre")
        candidate = prepare_mortal_world_effect(world, command, world_step=1)
        baseline = WorldBody(config=world.config, layout=world._layout)
        reference = baseline.apply(command, t_monde=1)
        self.assertEqual(
            canonical_causal_bytes(candidate.transition.as_dict()),
            canonical_causal_bytes(reference.as_dict()),
        )
        self.assertEqual(
            canonical_causal_bytes(candidate.proposed_state),
            canonical_causal_bytes(baseline.export_causal_state()),
        )
        self.assertEqual(world.export_causal_state(), original)
        self.assertNotEqual(
            canonical_causal_bytes(candidate.proposed_state),
            canonical_causal_bytes(original),
        )

    def test_lethal_candidate_is_not_public_death_before_commit(self):
        seed = build_stage4_reference_runtime(autonomous_mortal=True)
        home = seed.world.config.initial_position
        layout = WorldLayout(lethal_zones=frozenset({home}))
        world = WorldBody(config=seed.world.config, layout=layout)
        boundary = MortalWorldBoundary(world=world)
        original = world.export_causal_state()
        prepared = prepare_mortal_world_effect(
            world, Command("attendre"), world_step=1,
        )
        self.assertTrue(prepared.lethal)
        self.assertIn("lethal_zone", prepared.transition.lethal_reasons)
        self.assertEqual(world.export_causal_state(), original)
        self.assertEqual(boundary.status.value, "active")
        # The proposal has no publish() method. It must not terminate a real
        # identity until a later coordinator commits the final state/receipts.
        self.assertFalse(hasattr(prepared, "publish"))

    def test_sqlite_can_commit_exact_private_world_candidate_without_publishing(self):
        fixture = build_stage4_reference_runtime(autonomous_mortal=True)
        world = fixture.world
        before = world.export_causal_state()
        prepared = prepare_mortal_world_effect(
            world, Command("attendre"), world_step=1,
        )
        identity = "i0:staged:world"
        def state(physical):
            return {
                "individual_id": identity,
                "world": physical,
                "scheduler": {"t_monde": 1 if physical is prepared.proposed_state else 0},
                "owners": {"metacognition_health": {"cycle": 0}},
            }
        journal = HashChainedJournal()
        events = [
            journal.append(
                event_id="prepared:transition:1",
                causal_event={"kind": "world_transition_experienced", "t_monde": 1},
            ).as_dict(),
            journal.append(
                event_id="prepared:close:1",
                causal_event={
                    "kind": "step_closed", "t_monde": 1,
                    "data": {"outcome": "applied"},
                },
            ).as_dict(),
        ]
        with TemporaryDirectory() as tmp:
            with SQLiteLifeLedger.birth(
                path=str(Path(tmp) / "i0-staged.db"),
                individual_id=identity, initial_state=state(before),
            ) as ledger:
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                receipt = ledger.commit_generation(
                    expected_generation=0, expected_head="00" * 32,
                    intent_ref="step:1",
                    current_state=state(prepared.proposed_state),
                    events=events,
                )
                self.assertEqual(receipt.status, "active")
                self.assertEqual(receipt.journal_head, journal.head_hash)
                self.assertEqual(ledger.export_canonical_journal(), journal.canonical_bytes())
                # Publication is a separate, NOT YET implemented atomic step.
                self.assertEqual(world.export_causal_state(), before)


if __name__ == "__main__":
    unittest.main()
