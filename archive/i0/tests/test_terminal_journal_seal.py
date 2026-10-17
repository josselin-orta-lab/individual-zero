"""Death seals the individual's internal causal writer, not just its runtime.

External audit still independently detects cryptographically rehashed archives.
"""
from __future__ import annotations

import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.snapshots import SnapshotType
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command


class TerminalJournalSealTests(unittest.TestCase):
    def test_fatal_life_allows_one_closure_then_refuses_any_append(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        sub = individual.stage3.substrate
        individual.world.apply_scenario_event("set_lethal_zone", {
            "position": individual.world.position.as_dict(), "active": True,
        })
        sub.open_step()
        self.assertEqual(sub.execute(Command("attendre")).status, "dead")
        before = individual.journal.canonical_bytes()
        result = audit_export_bytes(before)
        self.assertEqual(result.terminal_deaths, 1)
        self.assertEqual(result.world_steps_closed, 1)
        self.assertTrue(individual.journal.verify())
        with self.assertRaisesRegex(RuntimeError, "terminal journal is sealed"):
            individual.journal.append(
                event_id="forged-postdeath-cognitive",
                causal_event={"kind": "episode_closed", "t_monde": 1},
            )
        with self.assertRaisesRegex(RuntimeError, "terminal journal is sealed"):
            sub.snapshots.take(
                snapshot_type=SnapshotType.COPY,
                individual_id=individual.individual_id,
                t_monde=1, cycle=0, attempt_ref=None,
                owners=(individual.world,), versions={},
            )
        self.assertFalse(sub.snapshots._snapshots)
        self.assertEqual(individual.journal.canonical_bytes(), before)

    def test_terminal_closure_only_after_matching_death_attempt(self):
        j = HashChainedJournal()
        j.append(event_id="death", causal_event={
            "kind": "individual_death_confirmed",
            "t_monde": 2, "attempt_ref": "attempt:2",
        })
        original = j.canonical_bytes()
        with self.assertRaisesRegex(RuntimeError, "unique technical closure"):
            j.append(event_id="unlawful", causal_event={
                "kind": "td_update_published", "t_monde": 2,
                "attempt_ref": "attempt:2",
            })
        with self.assertRaisesRegex(RuntimeError, "unique technical closure"):
            j.append(event_id="mismatched", causal_event={
                "kind": "step_closed", "t_monde": 2, "attempt_ref": "wrong",
                "data": {"outcome": "dead",
                         "applied_command_count": 1, "world_advance_count": 1},
            })
        self.assertEqual(j.canonical_bytes(), original)
        j.append(event_id="closure", causal_event={
            "kind": "step_closed", "t_monde": 2, "attempt_ref": "attempt:2",
            "data": {"outcome": "dead",
                     "applied_command_count": 1, "world_advance_count": 1},
        })
        with self.assertRaisesRegex(RuntimeError, "terminal journal is sealed"):
            j.append(event_id="another-closure", causal_event={
                "kind": "step_closed", "t_monde": 2, "attempt_ref": "attempt:2",
                "data": {"outcome": "dead",
                         "applied_command_count": 1, "world_advance_count": 1},
            })


if __name__ == "__main__":
    unittest.main()
