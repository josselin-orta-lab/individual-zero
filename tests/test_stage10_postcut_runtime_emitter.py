"""Regression: classify real Stage8/9 online learning events across a causal cut."""
import unittest

from i0.modules.consolidation_transaction import ConsolidationCut
from lab.journal import HashChainedJournal
from lab.consolidation_postcut_journal import Stage10PostCutJournal


class RuntimePostCutPublicationTests(unittest.TestCase):
    def setUp(self):
        self.journal = HashChainedJournal()
        root = self.journal.append(event_id="cut", causal_event={
            "emitter":"scheduler", "kind":"step_opened", "t_monde":9,
        })
        self.cut = ConsolidationCut(
            world_step=9, journal_index=root.index, journal_event_id=root.event_id,
            journal_hash=root.event_hash, history_version="h:0",
        )

    def test_real_stage8_precision_and_stage4_kappa_are_preserved(self):
        self.journal.append(event_id="precision", causal_event={
            "emitter":"perception", "kind":"perceptual_precision_update_published",
            "t_monde":10, "source":"vision", "verification_ref":"physical:10",
            "before":0.6, "after":0.7, "precision_version":1,
        })
        self.journal.append(event_id="kappa", causal_event={
            "emitter":"stage4-runtime", "kind":"kappa_update_published",
            "t_monde":10, "cycle":1,
            "data":{"verification_ref":"physical:10", "confidence":0.8},
        })
        self.journal.append(event_id="causal", causal_event={
            "emitter":"stage4-runtime", "kind":"causal_inference_status_published",
            "t_monde":11, "data":{"contingency_ref":"hyp:1"},
        })
        updates = Stage10PostCutJournal(journal=self.journal).freeze(cut=self.cut)
        self.assertEqual([e.owner_id for e in updates.updates], [
            "perception", "metacognition_health", "causal_model",
        ])
        self.assertEqual(updates.for_owner("perception")[0].payload["after"],0.7)
        self.assertEqual(updates.for_owner("metacognition_health")[0].event_id,"kappa")
        self.assertEqual(updates.for_owner("causal_model")[0].event_id,"causal")
        self.assertTrue(self.journal.verify())

    def test_real_td_update_is_preserved_in_original_order(self):
        self.journal.append(event_id="td", causal_event={
            "emitter":"value_needs", "kind":"td_update_published",
            "t_monde":10, "data":{"delta":1.5, "updated_signatures":["drink"]},
        })
        self.assertEqual(
            Stage10PostCutJournal(journal=self.journal).freeze(cut=self.cut)
            .for_owner("value_needs")[0].payload["delta"],1.5,
        )

    def test_long_td_segment_published_after_cut_keeps_older_decision_t(self):
        self.journal.append(event_id="td:deferred",causal_event={
            "emitter":"value_needs", "kind":"td_update_published",
            "t_monde":2, "cycle":1,
            "data":{"delta":0.25, "updated_signatures":["sleep","drink"]},
        })
        result=Stage10PostCutJournal(journal=self.journal).freeze(cut=self.cut)
        self.assertEqual([r.event_id for r in result.for_owner("value_needs")],
                         ["td:deferred"])
        self.assertLess(result.updates[0].t_monde,result.cut.world_step)

    def test_malformed_real_precision_event_fails_closed(self):
        self.journal.append(event_id="bad", causal_event={
            "emitter":"perception", "kind":"perceptual_precision_update_published",
            "t_monde":10, "source":"vision",
        })
        with self.assertRaises(ValueError):
            Stage10PostCutJournal(journal=self.journal).freeze(cut=self.cut)

    def test_wrong_emitter_must_not_masquerade_as_owner(self):
        self.journal.append(event_id="oracle", causal_event={
            "emitter":"bench", "kind":"kappa_update_published",
            "t_monde":11,"data":{"verification_ref":"fabricated"},
        })
        self.assertEqual(
            Stage10PostCutJournal(journal=self.journal).freeze(cut=self.cut).updates,()
        )

if __name__=="__main__":
    unittest.main()
