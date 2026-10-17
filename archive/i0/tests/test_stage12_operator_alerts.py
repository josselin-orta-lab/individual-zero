"""Stage12 operator alerts need continuous *physical* evidence, not cycles."""
from __future__ import annotations

from copy import deepcopy
import unittest

from i0.modules.stage12_alerts import (
    ALERT_SIGNALS, Stage12AlertLedger, Stage12AlertPolicy,
)
from i0.modules.stage12_detectors import Stage12DetectionReport


def report(t, *, stagnation=None, loop=None, entropy=None, bias=None):
    return Stage12DetectionReport(
        world_step=t, cycle=1,
        stagnation=stagnation, reasoning_loop=loop,
        low_context_entropy=entropy, attribution_bias=bias,
        verified_successes=0, verified_failures=0, evidence_samples=t,
    )


class Stage12OperatorAlertLedgerTests(unittest.TestCase):
    def ledger(self, steps=3):
        return Stage12AlertLedger(Stage12AlertPolicy(
            version="test-alert-dev-v1", persistence_world_steps=steps,
        ))

    def test_exact_streak_once_then_rearms_after_false(self):
        ledger = self.ledger(3)
        self.assertEqual(ledger.observe(report(1, stagnation=True)), ())
        self.assertEqual(ledger.observe(report(2, stagnation=True)), ())
        alerts = ledger.observe(report(3, stagnation=True))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].signal, "stagnation")
        self.assertEqual(alerts[0].first_world_step, 1)
        self.assertEqual(alerts[0].world_step, 3)
        self.assertEqual(ledger.observe(report(4, stagnation=True)), ())
        self.assertEqual(ledger.observe(report(5, stagnation=False)), ())
        self.assertEqual(ledger.observe(report(6, stagnation=True)), ())
        self.assertEqual(ledger.observe(report(7, stagnation=True)), ())
        rearmed = ledger.observe(report(8, stagnation=True))
        self.assertEqual([a.signal for a in rearmed], ["stagnation"])
        self.assertEqual(rearmed[0].first_world_step, 6)

    def test_unknown_or_missing_physical_step_breaks_streak(self):
        ledger = self.ledger(2)
        self.assertFalse(ledger.observe(report(1, entropy=True)))
        self.assertFalse(ledger.observe(report(3, entropy=True)))
        self.assertFalse(ledger.observe(report(4, entropy=None)))
        self.assertFalse(ledger.observe(report(5, entropy=True)))
        alerts = ledger.observe(report(6, entropy=True))
        self.assertEqual([a.signal for a in alerts], ["low_context_entropy"])
        self.assertFalse(ledger.observe(report(7, entropy=None)))
        self.assertFalse(ledger.observe(report(8, entropy=True)))

    def test_multiple_simultaneous_alerts_have_fixed_canonical_order(self):
        ledger = self.ledger(2)
        self.assertFalse(ledger.observe(report(
            1, stagnation=True, loop=True, entropy=True,
            bias="self_serving_pattern",
        )))
        alerts = ledger.observe(report(
            2, stagnation=True, loop=True, entropy=True,
            bias="self_blame_pattern",
        ))
        self.assertEqual([a.signal for a in alerts], list(ALERT_SIGNALS))
        self.assertTrue(all(a.consecutive_world_steps == 2 for a in alerts))
        self.assertTrue(all(a.as_dict()["operator_only_alert"] for a in alerts))

    def test_inadequate_attribution_evidence_never_triggers(self):
        ledger = self.ledger(2)
        for t in range(1, 7):
            self.assertFalse(ledger.observe(report(
                t, bias=None if t % 2 else "no_detected_pattern",
            )))
        self.assertEqual(ledger.export_causal_state()["streaks"]["attribution_bias"], 0)

    def test_invalid_policy_time_and_state_are_rejected_atomically(self):
        for threshold in (0, 1, -1, True, 2.5):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                Stage12AlertPolicy("test", threshold).validate()
        owner = self.ledger(2)
        owner.observe(report(1, entropy=True))
        current = owner.export_causal_state()
        with self.assertRaises(ValueError):
            owner.observe(report(1, entropy=True))
        with self.assertRaises(ValueError):
            owner.observe(report(0, entropy=True))
        for change in (
            ("last_world_step", 0),
            ("policy_version", "forged"),
        ):
            bad = deepcopy(current)
            bad[change[0]] = change[1]
            with self.subTest(change=change), self.assertRaises(ValueError):
                owner.restore_causal_state(bad)
            self.assertEqual(owner.export_causal_state(), current)
        for name in ALERT_SIGNALS:
            bad = deepcopy(current)
            bad["streaks"][name] = True
            with self.assertRaises(ValueError):
                owner.restore_causal_state(bad)
        owner.restore_causal_state(current)
        newborn = self.ledger(2)
        newborn.restore_causal_state(current)
        self.assertEqual(newborn.export_causal_state(), current)
        self.assertEqual([a.signal for a in newborn.observe(report(2, entropy=True))],
                         ["low_context_entropy"])

    def test_no_double_count_from_additional_cognitive_cycles(self):
        owner = self.ledger(2)
        owner.observe(report(1, entropy=True))
        modified = Stage12DetectionReport(
            world_step=1, cycle=2, stagnation=None,
            reasoning_loop=None, low_context_entropy=True,
            attribution_bias=None, verified_successes=0, verified_failures=0,
            evidence_samples=2,
        )
        with self.assertRaisesRegex(ValueError, "repeat or rewind"):
            owner.observe(modified)
        self.assertEqual(owner.export_causal_state()["streaks"]["low_context_entropy"], 1)


if __name__ == "__main__":
    unittest.main()
