"""Independent Stage-10 transaction contract regression; not semantic passes."""
import json
import unittest
from copy import deepcopy
from i0.modules.consolidation_transaction import (
    PASSES, ConsolidationCut, ConsolidationSlot,
    ConsolidationTransaction, ConsolidationCommitReceipt,
)


def transaction():
    return ConsolidationTransaction(
        consolidation_id="consolidation:1",
        cut=ConsolidationCut(4, 17, "event:17", "af" * 32, "h:0"),
        episode_refs=("ep:1", "ep:2"),
        episode_payloads={
            "ep:1": {"id": "ep:1", "end_t_monde": 1, "event_refs": ["e:1"]},
            "ep:2": {"id": "ep:2", "end_t_monde": 3, "event_refs": ["e:2"]},
        },
        history_candidate={"passes": []},
    )


def advance(tx):
    name = PASSES[tx.cursor]
    tx.run_pass(
        name=name,
        executor=lambda state, batch, cut: {"passes": state["passes"] + [name]},
        validator=lambda state: isinstance(state, dict) and isinstance(state.get("passes"), list),
    )


def finish(tx):
    while tx.cursor < len(PASSES):
        advance(tx)


def receipt(tx, **changes):
    data = {
        "consolidation_id": tx.id, "source_history_version": "h:0",
        "new_history_version": "h:1", "candidate_digest": tx.candidate_digest,
        "journal_commit_index": 18, "journal_commit_event_id": "commit:18",
    }
    data.update(changes)
    return ConsolidationCommitReceipt(**data)


class ConsolidationTransactionTests(unittest.TestCase):
    def test_frozen_episode_values_are_private(self):
        tx = transaction()
        copy = tx.frozen_episodes_copy()
        copy["ep:1"]["event_refs"].append("forged")
        self.assertEqual(tx.frozen_episodes_copy()["ep:1"]["event_refs"], ["e:1"])

    def test_batch_digest_stable_and_tamper_rejected(self):
        a, b = transaction(), transaction()
        self.assertEqual(a.batch_digest, b.batch_digest)
        state = a.export_causal_state()
        state["frozen_episodes"]["ep:1"]["event_refs"].append("fake")
        with self.assertRaises(ValueError):
            ConsolidationTransaction.restore(state)

    def test_post_cut_episode_rejected(self):
        state = transaction().export_causal_state()
        state["frozen_episodes"]["ep:2"]["end_t_monde"] = 4
        with self.assertRaises(ValueError):
            ConsolidationTransaction.restore(state)

    def test_bad_cut_and_invalid_workspace_rejected(self):
        with self.assertRaises(ValueError):
            ConsolidationCut(0, 1, "e", "af" * 32, "h:0").validate()
        with self.assertRaises(ValueError):
            ConsolidationCut(4, 1, "e", "xx" * 32, "h:0").validate()
        with self.assertRaises(ValueError):
            ConsolidationTransaction(
                consolidation_id="id",
                cut=ConsolidationCut(4, 1, "e", "af" * 32, "h:0"),
                episode_refs=(), episode_payloads={}, history_candidate={"bad": float("nan")},
            )

    def test_checkpoint_chain_rejects_mutation(self):
        tx = transaction()
        finish(tx)
        state = tx.export_causal_state()
        state["checkpoints"][1]["candidate"]["passes"].append("bad")
        with self.assertRaises(ValueError):
            ConsolidationTransaction.restore(state)

    def test_replay_identical_across_every_interruption(self):
        expected = transaction()
        finish(expected)
        for n in range(len(PASSES) + 1):
            tx = transaction()
            for _ in range(n):
                advance(tx)
            tx.interrupt()
            restored = ConsolidationTransaction.restore(json.loads(json.dumps(tx.export_causal_state())))
            restored.resume()
            finish(restored)
            self.assertEqual(restored.export_causal_state(), expected.export_causal_state())

    def test_failed_pass_leaves_last_point_unchanged(self):
        tx = transaction()
        advance(tx)
        previous = tx.export_causal_state()
        def interrupted(working, batch, cut):
            working["passes"].append("bad")
            raise RuntimeError("interrupted")
        with self.assertRaises(RuntimeError):
            tx.run_pass(name=PASSES[1], executor=interrupted, validator=lambda _: True)
        self.assertEqual(tx.export_causal_state(), previous)

    def test_validator_cannot_modify_private_candidate(self):
        tx = transaction()
        def validator(candidate):
            candidate["passes"].append("bad")
            return True
        tx.run_pass(name=PASSES[0], executor=lambda c, b, cut: c, validator=validator)
        self.assertEqual(tx.candidate_copy(), {"passes": []})

    def test_second_transaction_rejected_during_suspension(self):
        slot = ConsolidationSlot()
        tx = transaction()
        slot.begin(tx)
        advance(tx)
        tx.interrupt()
        with self.assertRaises(ValueError):
            slot.begin(transaction())
        self.assertIs(slot.resume(), tx)
        self.assertEqual(tx.cursor, 1)

    def test_receipt_cannot_clear_wrong_or_incomplete_transaction(self):
        slot = ConsolidationSlot()
        tx = transaction()
        slot.begin(tx)
        with self.assertRaises(ValueError):
            slot.acknowledge_coordinated_commit(receipt(tx))
        finish(tx)
        for variation in (
            {"consolidation_id": "other"}, {"candidate_digest": "0" * 64},
            {"journal_commit_index": 17}, {"source_history_version": "h:old"},
            {"new_history_version": "h:0"},
        ):
            with self.assertRaises(ValueError):
                slot.acknowledge_coordinated_commit(receipt(tx, **variation))
        self.assertIs(slot.current, tx)
        slot.acknowledge_coordinated_commit(receipt(tx))
        self.assertIsNone(slot.current)

    def test_slot_snapshot_restore_atomic(self):
        slot = ConsolidationSlot()
        tx = transaction()
        slot.begin(tx)
        advance(tx)
        tx.interrupt()
        before = slot.export_causal_state()
        forged = deepcopy(before)
        forged["current"]["candidate"] = {"passes": ["bad"]}
        with self.assertRaises(ValueError):
            slot.restore_causal_state(forged)
        self.assertEqual(slot.export_causal_state(), before)
        copied = ConsolidationSlot()
        copied.restore_causal_state(json.loads(json.dumps(before)))
        self.assertEqual(copied.export_causal_state(), before)


if __name__ == "__main__":
    unittest.main()
