"""Post-cut provenance tests against real append-only technical journal."""
from copy import deepcopy
import unittest

from lab.journal import HashChainedJournal
from lab.consolidation_postcut_journal import Stage10PostCutJournal
from i0.modules.consolidation_transaction import ConsolidationCut


def scenario():
    journal = HashChainedJournal()
    a = journal.append(event_id="start", causal_event={
        "emitter":"scheduler","kind":"step_opened","t_monde":3})
    cut = ConsolidationCut(
        world_step=3, journal_index=a.index,
        journal_event_id=a.event_id, journal_hash=a.event_hash,
        history_version="h:0")
    return journal, cut


class PostCutJournalTests(unittest.TestCase):
    def test_verified_real_technical_journal_respects_append_order(self):
        journal, cut = scenario()
        journal.append(event_id="td:1", causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":3,"data":{"delta":0.5}})
        journal.append(event_id="diagnostic:1", causal_event={
            "emitter":"bench","kind":"diagnostic","t_monde":4,
            "data":{"oracle":True}})
        journal.append(event_id="kappa:1", causal_event={
            "emitter":"metacognition_health","kind":"kappa_update_published",
            "t_monde":4,"data":{"verification_id":"v1"}})
        frozen = Stage10PostCutJournal(journal=journal).freeze(cut=cut)
        self.assertEqual([r.event_id for r in frozen.updates], ["td:1", "kappa:1"])
        self.assertEqual([r.journal_index for r in frozen.updates], [1,3])
        self.assertEqual(len(frozen.for_owner("perception")), 0)
        self.assertEqual(frozen.for_owner("value_needs")[0].detached_payload()["delta"],0.5)
        self.assertEqual(frozen.end_hash,journal.head_hash)

    def test_future_postcut_online_update_requires_rebase_restart(self):
        journal, cut = scenario()
        bound = Stage10PostCutJournal(journal=journal)
        frozen = bound.freeze(cut=cut)
        journal.append(event_id="td:later", causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":4,"data":{"delta":1}})
        with self.assertRaises(ValueError):
            bound.validate_no_intervening_updates(frozen=frozen)
        second = bound.freeze(cut=cut)
        self.assertEqual(len(second.updates),1)
        bound.validate_no_intervening_updates(frozen=second)

    def test_not_the_real_journal_rejected(self):
        with self.assertRaises(TypeError):
            Stage10PostCutJournal(journal=[])

    def test_forged_cut_identity_rejected(self):
        journal, cut = scenario()
        altered = ConsolidationCut(
            cut.world_step,cut.journal_index,"fake",cut.journal_hash,
            cut.history_version)
        with self.assertRaises(ValueError):
            Stage10PostCutJournal(journal=journal).freeze(cut=altered)

    def test_forged_cut_hash_rejected(self):
        journal,cut=scenario()
        forged=ConsolidationCut(
            cut.world_step,cut.journal_index,cut.journal_event_id,
            "a"*64,cut.history_version)
        with self.assertRaises(ValueError):
            Stage10PostCutJournal(journal=journal).freeze(cut=forged)

    def test_missing_cut_index_rejected(self):
        journal,cut=scenario()
        invalid=ConsolidationCut(
            cut.world_step,99,cut.journal_event_id,cut.journal_hash,
            cut.history_version)
        with self.assertRaises(ValueError):
            Stage10PostCutJournal(journal=journal).freeze(cut=invalid)

    def test_malformed_online_event_cannot_pass(self):
        journal,cut=scenario()
        journal.append(event_id="bad:1",causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":4,"data":["not","mapping"]})
        with self.assertRaises(ValueError):
            Stage10PostCutJournal(journal=journal).freeze(cut=cut)

    def test_lab_oracle_diagnostic_never_appears_as_online_update(self):
        journal,cut=scenario()
        journal.append(event_id="oracle:1",causal_event={
            "emitter":"bench","kind":"td_update_published",
            "t_monde":4,"data":{"delta":9999}})
        frozen=Stage10PostCutJournal(journal=journal).freeze(cut=cut)
        self.assertEqual(frozen.updates,())

    def test_detached_payload_does_not_mutate_history(self):
        journal,cut=scenario()
        journal.append(event_id="td:1",causal_event={
            "emitter":"value_needs","kind":"td_update_published",
            "t_monde":4,"data":{"n":[1]}})
        bound=Stage10PostCutJournal(journal=journal)
        frozen=bound.freeze(cut=cut)
        copy=frozen.for_owner("value_needs")[0].detached_payload()
        copy["n"].append(100)
        self.assertEqual(frozen.updates[0].detached_payload(),{"n":[1]})
        bound.validate_no_intervening_updates(frozen=frozen)
