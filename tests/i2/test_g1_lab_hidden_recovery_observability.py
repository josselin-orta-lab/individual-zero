"""ADR-0006 falsifier: hidden environmental change must not leak to cognition.

Uses the already frozen G1-LAB adverse/recovery worlds and unchanged policies.
This is an observational-equivalence regression, NOT a new animal/social or
physiological experiment, an H2 success claim, or approval for living I2.

For byte-exact counterfactual journal comparison, both disposable SQLite
sandboxes intentionally carry the SAME mock subject/genesis identifiers.
They are alternative test worlds for one hypothetical history, not two
independently born lives; independent identity/M11 is not tested here.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.lab.integrated_loop import (  # noqa: E402
    EAT, IntegratedLab, REGIMES,
)


class HiddenRecoveryIdentifiabilityTests(unittest.TestCase):
    """Contrasting hidden physics must not become unearned subjective evidence."""

    def run_counterfactual(self, *, regime: str, revisit: bool, count: int):
        with tempfile.TemporaryDirectory(prefix="g1-lab-adr6-") as temp:
            path = Path(temp) / "one-disposable-owner.sqlite"
            lab = IntegratedLab.create(
                path,
                life_ref="lab:counterfactual:one-controlled-identity",
                genesis_ref="lab:counterfactual:one-controlled-genesis",
                learning=True,
                revisit=revisit,
                deltas=REGIMES[regime],
                initial_energy=24,
                initial_uc=60,
            )
            trace = []
            for _ in range(count):
                step = lab.step()
                trace.append(asdict(step))
                if step.terminal:
                    break
            audit = lab.audit()
            with sqlite3.connect(path) as db:
                events = tuple(
                    (event_json, event_hash)
                    for event_json, event_hash in db.execute(
                        "SELECT event_json,event_hash FROM events ORDER BY seq"
                    )
                )
                hidden_schedule = db.execute(
                    "SELECT deltas_json FROM g1_lab_meta WHERE id=1"
                ).fetchone()[0]
            return trace, events, hidden_schedule, audit

    def test_unobserved_payoff_recovery_is_indistinguishable_from_adversity(self):
        adverse = self.run_counterfactual(
            regime="adverse", revisit=False, count=8
        )
        recovered = self.run_counterfactual(
            regime="recovery", revisit=False, count=8
        )
        a_trace, a_events, a_hidden, a_audit = adverse
        r_trace, r_events, r_hidden, r_audit = recovered

        # Only the external toy world schedule differs. The personal history
        # and even the complete local cognitive chain are identical.
        self.assertNotEqual(a_hidden, r_hidden)
        self.assertEqual(a_trace, r_trace)
        self.assertEqual(a_events, r_events)
        self.assertEqual(len(a_trace), 8)
        self.assertEqual(
            [step["chosen"] for step in a_trace],
            [
                "affordance:collect:berry_a", EAT,
                "affordance:collect:berry_a",
                "affordance:collect:berry_a",
                "affordance:collect:berry_a",
                "affordance:collect:berry_a",
                "affordance:collect:berry_a",
                "affordance:collect:berry_a",
            ],
        )
        self.assertTrue(a_trace[-1]["terminal"])
        self.assertEqual([s["energy"] for s in a_trace],
                         [22, 12, 10, 8, 6, 4, 2, 0])
        self.assertEqual(a_audit["actual_synthetic_uc_spent"], 38)
        self.assertEqual(r_audit["actual_synthetic_uc_spent"], 38)
        self.assertFalse(a_audit["m11_authenticated"])
        self.assertEqual(a_audit["motor_authority"], "NONE")

        for event_json, _ in a_events:
            data = json.loads(event_json)
            # Available first-person facts are fixed-goal affordances and
            # prior chosen consequences, not the hidden future food payoff.
            self.assertEqual(data["claim"]["capture"]["goal_ref"], "goal:food")
            self.assertNotIn("hidden_payoff", data["claim"]["capture"])

    def test_existing_revisit_reveals_change_only_after_same_chosen_action(self):
        # This is a POSITIVE INFORMATION CONTROL, not a policy endorsement.
        # Existing researcher-injected +9 revisit causes EAT at capture 5.
        adverse = self.run_counterfactual(
            regime="adverse", revisit=True, count=5
        )
        recovered = self.run_counterfactual(
            regime="recovery", revisit=True, count=5
        )
        a_trace, a_events, _, a_audit = adverse
        r_trace, r_events, _, r_audit = recovered
        self.assertEqual(a_trace[:4], r_trace[:4])
        self.assertEqual(len(a_trace), 5)
        self.assertEqual(len(r_trace), 5)
        self.assertEqual(a_trace[4]["chosen"], EAT)
        self.assertEqual(r_trace[4]["chosen"], EAT)
        self.assertEqual(a_trace[4]["visible"], r_trace[4]["visible"])
        self.assertEqual(a_trace[4]["control_status"],
                         r_trace[4]["control_status"])
        self.assertEqual(a_trace[4]["uc_spent"], r_trace[4]["uc_spent"])
        # Cognitive COMMIT advice at capture 5 is sealed before the physical
        # consequence. Thus even at that capture the journals must match.
        self.assertEqual(a_events, r_events)
        self.assertEqual(a_trace[4]["result_net"], -8)
        self.assertEqual(r_trace[4]["result_net"], 6)
        self.assertTrue(a_trace[4]["terminal"])
        self.assertFalse(r_trace[4]["terminal"])
        self.assertEqual(a_audit["actual_synthetic_uc_spent"],
                         r_audit["actual_synthetic_uc_spent"])
        self.assertFalse(r_audit["birth_authorized"])


if __name__ == "__main__":
    unittest.main()
