"""Stage-10 coordinated publication tests: technical properties, not semantic passes."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from i0.modules.consolidation_transaction import (
    ConsolidationCut, ConsolidationSlot, ConsolidationTransaction, PASSES,
)
from lab.journal import HashChainedJournal
from lab.consolidation_publication import SlowHistory, Stage10PublicationCoordinator


class ActiveOwner:
    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.state = {"generation": 0, "postcut_ids": []}
        self.fail_target = False

    def export_causal_state(self):
        return deepcopy(self.state)

    def restore_causal_state(self, state):
        if self.fail_target and state["generation"] != 0:
            self.fail_target = False
            raise RuntimeError("owner restore injected fault")
        self.state = deepcopy(state)


def fixture(*, finish=True):
    journal = HashChainedJournal()
    cut_event = journal.append(event_id="cut:1", causal_event={
        "emitter": "scheduler", "kind": "step_opened", "t_monde": 4})
    cut = ConsolidationCut(
        4, cut_event.index, cut_event.event_id, cut_event.event_hash, "h:0")
    tx = ConsolidationTransaction(
        consolidation_id="c:1", cut=cut,
        episode_refs=("ep:1",),
        episode_payloads={"ep:1": {
            "id":"ep:1", "end_t_monde":2, "event_refs":["physical:2"],
        }}, history_candidate={"forms": {}, "hypotheses": []},
    )
    slot = ConsolidationSlot()
    slot.begin(tx)
    if finish:
        for name in PASSES:
            tx.run_pass(
                name=name, executor=lambda c, refs, cut: c,
                validator=lambda c: True,
            )
    history = SlowHistory(birth_version="h:0", birth_state={"forms": {}})
    owners = {name: ActiveOwner(name) for name in sorted(
        Stage10PublicationCoordinator.REQUIRED
    )}
    coord = Stage10PublicationCoordinator(
        journal=journal, history=history, slot=slot, owners=owners)
    return journal,tx,slot,history,owners,coord


def rebasers():
    def rebase(candidate, old, updates):
        return {
            "generation": 1,
            "postcut_ids": [row.event_id for row in updates],
        }
    return {
        name: rebase
        for name in sorted(Stage10PublicationCoordinator.REQUIRED)
    }


def prepare(coord, tx):
    return coord.prepare(
        transaction=tx,
        technical_validator=lambda c: isinstance(c, dict),
        owner_rebasers=rebasers(),
    )


class CoordinatedPublicationTests(unittest.TestCase):
    def test_prepare_is_private_then_one_coordinated_visibility_point(self):
        journal, tx, slot, history, owners, coord = fixture()
        journal.append(event_id="td:1",causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":4,"data":{"delta":0.5}})
        prior = {name:owner.export_causal_state() for name,owner in owners.items()}
        staged = prepare(coord,tx)
        self.assertEqual(history.current_version,"h:0")
        self.assertEqual(
            {name:owner.export_causal_state() for name,owner in owners.items()},
            prior,
        )
        receipt = coord.publish(
            prepared=staged, transaction=tx, world_step=5,
            scheduler_sync_authorized=True)
        self.assertEqual(history.current_version,receipt.new_history_version)
        self.assertEqual(owners["value_needs"].state["postcut_ids"],["td:1"])
        self.assertEqual(owners["perception"].state["postcut_ids"],[])
        self.assertIsNone(slot.current)
        self.assertEqual(journal.entries[-1].event_id, receipt.journal_commit_event_id)
        self.assertTrue(journal.verify())
        self.assertEqual(
            history.export_causal_state()["lineage"][-1]["source_version"], "h:0")

    def test_future_event_after_private_rebase_blocks_commit(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        journal.append(event_id="td:2",causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":5,"data":{"delta":2}})
        with self.assertRaises(ValueError):
            coord.publish(prepared=staged,transaction=tx,world_step=5,
                          scheduler_sync_authorized=True)
        self.assertEqual(history.current_version,"h:0")
        self.assertIs(slot.current,tx)

    def test_owner_online_update_after_rebase_blocks_commit(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        owners["value_needs"].state["generation"]=2
        with self.assertRaises(ValueError):
            coord.publish(prepared=staged,transaction=tx,world_step=5,
                          scheduler_sync_authorized=True)
        self.assertEqual(history.current_version,"h:0")
        self.assertIs(slot.current,tx)

    def test_restore_failure_rolls_back_all_owners_and_h(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        owners["perception"].fail_target=True
        prior=len(journal.entries)
        with self.assertRaises(RuntimeError):
            coord.publish(prepared=staged,transaction=tx,world_step=5,
                          scheduler_sync_authorized=True)
        self.assertEqual(len(journal.entries),prior)
        self.assertEqual(history.current_version,"h:0")
        self.assertTrue(all(o.state["generation"]==0 for o in owners.values()))
        self.assertIs(slot.current,tx)

    def test_journal_append_failure_rolls_back_all_state(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        with patch.object(journal,"append",side_effect=RuntimeError("disk journal unavailable")):
            with self.assertRaises(RuntimeError):
                coord.publish(prepared=staged,transaction=tx,world_step=5,
                              scheduler_sync_authorized=True)
        self.assertTrue(all(o.state["generation"]==0 for o in owners.values()))
        self.assertEqual(history.current_version,"h:0")
        self.assertIs(slot.current,tx)

    def test_acknowledgement_failure_never_rolls_back_committed_version(self):
        journal, tx, slot, history, owners, coord = fixture()
        staged = prepare(coord, tx)
        with patch.object(
            slot, "acknowledge_coordinated_commit",
            side_effect=RuntimeError("acknowledgement unavailable"),
        ):
            with self.assertRaisesRegex(RuntimeError, "irreversible"):
                coord.publish(
                    prepared=staged, transaction=tx, world_step=5,
                    scheduler_sync_authorized=True,
                )
        self.assertEqual(
            history.current_version, staged.destination_version,
        )
        self.assertTrue(all(o.state["generation"] == 1 for o in owners.values()))
        self.assertEqual(
            journal.entries[-1].causal_event["kind"],
            "stage10_consolidation_version_activated",
        )
        self.assertTrue(journal.verify())

    def test_append_then_raises_cannot_rewind_committed_history(self):
        journal, tx, slot, history, owners, coord = fixture()
        staged = prepare(coord, tx)
        original_append = journal.append

        def persisted_then_raised(**kwargs):
            original_append(**kwargs)
            raise OSError("simulated post-write exception")

        with patch.object(journal, "append", side_effect=persisted_then_raised):
            with self.assertRaisesRegex(RuntimeError, "irreversible"):
                coord.publish(
                    prepared=staged, transaction=tx, world_step=5,
                    scheduler_sync_authorized=True,
                )
        self.assertEqual(
            history.current_version, staged.destination_version,
        )
        self.assertEqual(len(journal.entries), 2)
        self.assertTrue(all(o.state["generation"] == 1 for o in owners.values()))
        self.assertTrue(journal.verify())

    def test_commit_refused_outside_scheduler_sync(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        with self.assertRaises(ValueError):
            coord.publish(prepared=staged,transaction=tx,world_step=5,
                          scheduler_sync_authorized=False)
        self.assertEqual(history.current_version,"h:0")

    def test_incomplete_passes_cannot_publish_or_prepare(self):
        journal,tx,slot,history,owners,coord=fixture(finish=False)
        with self.assertRaises(ValueError):
            prepare(coord,tx)

    def test_technical_candidate_validator_may_refuse(self):
        journal,tx,slot,history,owners,coord=fixture()
        with self.assertRaises(ValueError):
            coord.prepare(transaction=tx,technical_validator=lambda c:False,
                          owner_rebasers=rebasers())
        self.assertEqual(history.current_version,"h:0")

    def test_aliasing_and_missing_owner_rejected(self):
        journal,tx,slot,history,owners,coord=fixture()
        duplicate=dict(owners)
        duplicate["perception"]=owners["causal_model"]
        with self.assertRaises(ValueError):
            Stage10PublicationCoordinator(
                journal=journal,history=history,slot=slot,owners=duplicate)
        removed=dict(owners);del removed["perception"]
        with self.assertRaises(ValueError):
            Stage10PublicationCoordinator(
                journal=journal,history=history,slot=slot,owners=removed)

    def test_publication_snapshot_lineage_roundtrip(self):
        journal,tx,slot,history,owners,coord=fixture()
        staged=prepare(coord,tx)
        receipt=coord.publish(prepared=staged,transaction=tx,world_step=5,
                              scheduler_sync_authorized=True)
        snap=history.export_causal_state()
        restored=SlowHistory(birth_version="temporary",birth_state={})
        restored.restore_causal_state(snap)
        self.assertEqual(restored.export_causal_state(),snap)
        self.assertEqual(restored.current_version,receipt.new_history_version)
        snap["current_state"]["forms"]["injected"]="changed"
        self.assertNotEqual(restored.export_causal_state(),snap)

    def test_owner_preparer_live_mutation_forbidden(self):
        journal,tx,slot,history,owners,coord=fixture()
        def illegal(candidate,original,updates):
            owners["perception"].state["generation"]=99
            return original
        funcs=rebasers();funcs["perception"]=illegal
        with self.assertRaises(ValueError):
            coord.prepare(transaction=tx,
                          technical_validator=lambda c:True,
                          owner_rebasers=funcs)


if __name__=="__main__":
    unittest.main()
