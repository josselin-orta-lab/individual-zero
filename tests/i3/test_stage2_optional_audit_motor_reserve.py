"""Motor-reserve funding regression after a previously admitted GATE action.

Historical sources and their frozen originals remain unchanged. These are
pure synthetic funding-state tests; the actual new 24-life engineering smoke
runs separately in GitHub CI with no life outcomes disclosed.
"""
import unittest
from unittest.mock import patch

from i3.modules.body import (ACTION_COSTS, BodyLaws, CognitiveBudget,
                             CognitiveFundingError, CognitiveWork, transition)
from i3.modules.p13_replay_gate_mind import (
    _optional_audit_preserves_funded_motor,
)

from test_p13_replay_gate_mind import BODY, CAP, gate, p13
from i3.lab import stage2_replay_gate_falsifier as F


class OptionalResidualAuditMotorFundingTests(unittest.TestCase):
    def test_optional_audit_never_steals_prepaid_motor_energy(self):
        laws = BodyLaws()
        original = (2.035, 85.0, 85.0, 85.0, 85.0)
        b = CognitiveBudget(original, laws)
        b.spend(CognitiveWork(cycles=1))
        self.assertGreaterEqual(b.remaining[0], ACTION_COSTS["se_deplacer"])
        self.assertFalse(_optional_audit_preserves_funded_motor(b, "se_deplacer"))
        # Demonstrate the actual world/body laws would reject the old
        # decision + post-audit bill. No artificial recovery or refund.
        with self.assertRaises(CognitiveFundingError):
            transition(original, "se_deplacer", laws,
                       CognitiveWork(cycles=2))
        # The same selected action is affordable without that optional cycle.
        after, dead = transition(original, "se_deplacer", laws, b.work)
        self.assertGreaterEqual(after[0], 0)
        self.assertFalse(dead)

    def test_post_audit_can_still_run_with_genuine_motor_reserve(self):
        laws = BodyLaws()
        for action, motor_cost in ACTION_COSTS.items():
            with self.subTest(action=action):
                original = (max(5.0, motor_cost + .1), 80., 80., 80., 80.)
                b = CognitiveBudget(original, laws)
                b.spend(CognitiveWork(cycles=1))
                self.assertTrue(_optional_audit_preserves_funded_motor(b, action))
                self.assertTrue(b.try_spend(CognitiveWork(cycles=1)))
                if action != "dormir":
                    self.assertGreaterEqual(b.remaining[0], motor_cost)
        b = CognitiveBudget((.05, 80., 80., 80., 80.), laws)
        b.spend(CognitiveWork(cycles=1))
        self.assertTrue(_optional_audit_preserves_funded_motor(b, None))
        self.assertTrue(_optional_audit_preserves_funded_motor(b, "dormir"))

    def test_skipped_residual_audit_does_not_modify_existing_motor_competition(self):
        baseline = F._decide(p13(), CAP)
        m = gate()
        with patch("i3.modules.p13_replay_gate_mind._optional_audit_preserves_funded_motor",
                   return_value=False):
            measured = F._decide(m, CAP)
        self.assertEqual((baseline["option"], baseline["action"], baseline["param"]),
                         (measured["option"], measured["action"], measured["param"]))
        self.assertEqual(baseline["scores"], measured["scores"])
        self.assertEqual(baseline["work"], measured["work"])
        self.assertEqual(m.decisions_total, 1)
        self.assertEqual(m.audited_decisions, 0)
        self.assertEqual(m.relevant_decisions, 0)

    def test_unknown_motor_never_treated_as_funded(self):
        b = CognitiveBudget((80.,) * 5, BodyLaws())
        with self.assertRaises(ValueError):
            _optional_audit_preserves_funded_motor(b, "invented_motor")


if __name__ == "__main__":
    unittest.main()
