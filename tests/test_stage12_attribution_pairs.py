"""GA-06 Metacognition: one unique lived pair, next-step receipt, cold image."""
from __future__ import annotations

import unittest

from i0.modules.stage12_attribution_pairs import (
    LivedAttributionPair, Stage12AttributionPairs,
)


def pair(*, step=2, ref="pair:1", intent="intent:1", judgement="judge:1"):
    return LivedAttributionPair(
        pair_ref=ref, life_id="life:1", intent_ref=intent,
        goal_followup_ref=f"goal-outcome:{step}",
        agency_assessment_ref=f"assessment:{step}",
        agency_judgement_ref=judgement,
        observed_world_step=step, outcome="success", agency="self",
    )


class Stage12AttributionPairsTests(unittest.TestCase):
    def test_one_real_step_identity_consumed_only_on_next_step(self):
        ledger = Stage12AttributionPairs()
        first = pair()
        ledger.admit(first)
        self.assertIsNone(ledger.consume(diagnostic_world_step=2))
        self.assertEqual(ledger.consume(diagnostic_world_step=3), first)
        self.assertIsNone(ledger.consume(diagnostic_world_step=3))
        with self.assertRaises(ValueError):
            ledger.admit(first)

    def test_late_diagnostic_does_not_backfill_retroactively(self):
        ledger = Stage12AttributionPairs()
        ledger.admit(pair())
        self.assertIsNone(ledger.consume(diagnostic_world_step=4))
        self.assertIsNone(ledger.pending)
        self.assertIsNone(ledger.consume(diagnostic_world_step=5))

    def test_disjoint_identifiers_and_unique_original_observations(self):
        ledger = Stage12AttributionPairs()
        ledger.admit(pair())
        first_state = ledger.export_causal_state()
        for kwargs in (
            {"step": 3, "ref": "pair:2", "intent": "intent:2", "judgement": "judge:2"},
            {"step": 3, "ref": "pair:1", "intent": "intent:2", "judgement": "judge:2"},
        ):
            with self.assertRaises(ValueError):
                ledger.admit(pair(**kwargs))
            self.assertEqual(ledger.export_causal_state(), first_state)
        ledger.consume(diagnostic_world_step=3)
        for kwargs in (
            {"step": 3, "ref": "pair:1", "intent": "intent:2", "judgement": "judge:2"},
            {"step": 3, "ref": "pair:2", "intent": "intent:1", "judgement": "judge:2"},
            {"step": 3, "ref": "pair:2", "intent": "intent:2", "judgement": "judge:1"},
        ):
            with self.assertRaises(ValueError):
                ledger.admit(pair(**kwargs))

    def test_missing_agency_or_goal_outcome_cannot_be_pair(self):
        for field, value in (
            ("agency", "unknown"), ("agency", "self_compatible"),
            ("outcome", "unknown"), ("outcome", "conforming"),
            ("life_id", ""), ("observed_world_step", 1),
        ):
            with self.subTest(field=field):
                data = pair().as_dict()
                data[field] = value
                with self.assertRaises(ValueError):
                    Stage12AttributionPairs().admit(LivedAttributionPair(**data))

    def test_authentic_current_cold_install_is_not_historical_rollback(self):
        source = Stage12AttributionPairs()
        source.admit(pair())
        image = source.export_causal_state()
        cold = Stage12AttributionPairs()
        cold.restore_causal_state(image)
        self.assertEqual(cold.export_causal_state(), image)
        with self.assertRaises(ValueError):
            cold.restore_causal_state(image)
        self.assertEqual(cold.consume(diagnostic_world_step=3), pair())

    def test_duplicate_or_missing_restore_sources_fail_atomically(self):
        source = Stage12AttributionPairs()
        source.admit(pair())
        before = Stage12AttributionPairs().export_causal_state()
        invalid = source.export_causal_state()
        invalid["seen_judgements"] = ["judge:1", "judge:1"]
        cold = Stage12AttributionPairs()
        with self.assertRaises(ValueError):
            cold.restore_causal_state(invalid)
        self.assertEqual(cold.export_causal_state(), before)


if __name__ == "__main__":
    unittest.main()
