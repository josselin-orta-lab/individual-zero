"""Adversarial M11 ledger terminal semantics: correctly hashed forgeries must fail.

The low-level SQLite ledger is a trust boundary, not a trusted journal producer.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.journal import HashChainedJournal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked


IDENTITY = "audit:m11:terminal"


def state(n=0):
    return {
        "individual_id": IDENTITY,
        "world": {"physical_step": n},
        "scheduler": {"t_monde": n},
        "owners": {"metacognition_health": {"cycle": n}},
    }


class LedgerOperatorForgeryTests(unittest.TestCase):
    def _attempt(self, *, physical_death, world_rewound, outcome_expected):
        with TemporaryDirectory() as temp:
            path = str(Path(temp) / "life.sqlite")
            events = HashChainedJournal()
            # Deliberately derive valid cryptographic proof from the spoofed
            # event. A journal hash proves integrity, not semantics.
            forged = events.append(event_id="operator:1", causal_event={
                "kind": "experiment_stopped",
                "t_monde": 0,
                "emitter": "operator_console",
                "data": {
                    "reason": "operator_test_complete",
                    "physical_death": physical_death,
                    "world_rewound": world_rewound,
                },
            }).as_dict()
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=state(),
            ) as ledger:
                ledger.begin_intent(expected_generation=0, intent_ref="intent:operator")
                if outcome_expected == "reject":
                    with self.assertRaises((RecoveryBlocked, ValueError, RuntimeError)):
                        ledger.commit_generation(
                            expected_generation=0,
                            expected_head="00" * 32,
                            intent_ref="intent:operator",
                            current_state=state(0),
                            status="experiment_stopped",
                            events=[forged],
                        )
                else:
                    final = ledger.commit_generation(
                        expected_generation=0,
                        expected_head="00" * 32,
                        intent_ref="intent:operator",
                        current_state=state(0),
                        status="experiment_stopped",
                        events=[forged],
                    )
                    self.assertEqual(final.status, "experiment_stopped")
                    self.assertFalse(final.may_recover)

    def test_operator_stop_does_not_claim_physical_death(self):
        self._attempt(physical_death=True, world_rewound=False,
                      outcome_expected="reject")

    def test_operator_stop_does_not_claim_world_rewind(self):
        self._attempt(physical_death=False, world_rewound=True,
                      outcome_expected="reject")

    def test_operator_stop_requires_both_flags_explicit(self):
        self._attempt(physical_death=None, world_rewound=None,
                      outcome_expected="reject")

    def test_valid_terminal_stop_is_allowed_but_not_resumable(self):
        self._attempt(physical_death=False, world_rewound=False,
                      outcome_expected="allow")


if __name__ == "__main__":
    unittest.main()
