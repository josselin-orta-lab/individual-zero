"""Independent contract-level tests, NOT evidence of Stage-10 integration."""
import unittest

from i0.modules.consolidation_transaction import (
    PASSES, ConsolidationCut, ConsolidationSlot, ConsolidationTransaction,
)


def transaction():
    return ConsolidationTransaction(
        consolidation_id="consolidation:test:1",
        cut=ConsolidationCut(3, "event:17", "h:0"),
        episode_refs=("episode:1", "episode:3"),
        history_candidate={"events": []},
    )


def run_next(tx):
    name = PASSES[tx.cursor]
    tx.run_pass(
        name=name,
        executor=lambda candidate, batch, cut: {
            "events": candidate["events"] + [name],
        },
        validator=lambda candidate: isinstance(candidate, dict)
        and isinstance(candidate.get("events"), list),
    )


class ConsolidationTransactionTests(unittest.TestCase):
    def test_suspended_transaction_has_priority_and_keeps_validated_passes(self):
        slot = ConsolidationSlot()
        tx = transaction()
        slot.begin(tx)
        run_next(tx)
        run_next(tx)
        tx.interrupt()
        with self.assertRaises(ValueError):
            slot.begin(transaction())
        self.assertEqual(tx.completed_passes, PASSES[:2])
        self.assertEqual(slot.resume().id, tx.id)
        for _ in PASSES[2:]:
            run_next(tx)
        self.assertEqual(tx.validated_candidate(validator=lambda _: True)["events"], list(PASSES))
        slot.clear_after_coordinated_commit(tx.id)
        self.assertIsNone(slot.current)

    def test_failed_pass_preserves_checkpoint(self):
        tx = transaction()
        run_next(tx)
        before = tx.export_causal_state()
        with self.assertRaises(ValueError):
            tx.run_pass(
                name=PASSES[1],
                executor=lambda candidate, batch, cut: candidate["events"].append("bad"),
                validator=lambda _: False,
            )
        self.assertEqual(tx.export_causal_state(), before)

    def test_private_candidate_and_snapshot_do_not_alias(self):
        tx = transaction()
        snapshot = tx.export_causal_state()
        snapshot["initial"]["events"].append("external")
        self.assertEqual(tx.candidate_copy(), {"events": []})
        for _ in PASSES[:3]:
            run_next(tx)
        tx.interrupt()
        restored = ConsolidationTransaction.restore(tx.export_causal_state())
        self.assertEqual(restored.export_causal_state(), tx.export_causal_state())
        self.assertEqual(restored.id, tx.id)
        restored.resume()
        for _ in PASSES[3:]:
            run_next(restored)
        self.assertEqual(restored.validated_candidate(validator=lambda _: True)["events"], list(PASSES))

    def test_rejects_invalid_pass_order_and_premature_commit(self):
        tx = transaction()
        with self.assertRaises(ValueError):
            tx.run_pass(name=PASSES[1], executor=lambda c, b, cut: c, validator=lambda _: True)
        with self.assertRaises(ValueError):
            tx.validated_candidate(validator=lambda _: True)
        tx.interrupt()
        with self.assertRaises(ValueError):
            run_next(tx)

    def test_corrupt_snapshot_rejected_without_mutating_live_instance(self):
        tx = transaction()
        run_next(tx)
        state = tx.export_causal_state()
        state["candidate"] = {"events": ["forged"]}
        with self.assertRaises(ValueError):
            ConsolidationTransaction.restore(state)
        self.assertEqual(tx.cursor, 1)

    def test_batch_duplicate_and_unstable_clock_rejected(self):
        with self.assertRaises(ValueError):
            ConsolidationTransaction(
                consolidation_id="id",
                cut=ConsolidationCut(1, "e", "h:0"),
                episode_refs=("duplicate", "duplicate"),
                history_candidate={},
            )
        with self.assertRaises(ValueError):
            ConsolidationTransaction(
                consolidation_id="id",
                cut=ConsolidationCut(0, "e", "h:0"),
                episode_refs=(),
                history_candidate={},
            )


if __name__ == "__main__":
    unittest.main()
