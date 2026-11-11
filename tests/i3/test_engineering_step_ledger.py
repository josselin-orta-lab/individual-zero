"""I3 engineering-only ledger validation: no World, Mind or scientific birth."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest

from i3.runtime.birth_reservation import make_reservation, reserve
from i3.runtime.engineering_step_ledger import (
    DB_NAME, INTENT_SCHEMA, RECEIPT_SCHEMA, initialize, inspect, prepare, seal,
)


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.claim = make_reservation(
            birth_index=11, life_seed=2303,
            source_sha256="a"*64, world_sha256="b"*64,
            genome_sha256="c"*64,
        )
        reserve(self.root, self.claim)
        self.initial = [95., 85., 75., 65., 55.]
        self.start = initialize(self.root, self.claim,
                                horizon=2, initial_body=self.initial)

    def intent(self, step=1, before=None, action="attendre"):
        return {"schema": INTENT_SCHEMA, "tick_before": step-1,
                "body_before": list(self.initial if before is None else before),
                "action": action, "param": None,
                "decision_work": {"cycles": 3, "simulated_steps": 5,
                                  "memory_items": 14, "replays": 0}}

    def receipt(self, step=1, body=None, action="attendre", deaths=None):
        body = list(body or [90., 84., 74., 65., 54.])
        if deaths and "zero_water" in deaths:
            body[2] = 0.0
        learning_paid = ({"energy": 0.0, "vigilance": 0.0} if deaths else
                         {"energy": 0.02, "vigilance": 0.05})
        after_motor = list(body)
        after_motor[0] += learning_paid["energy"]
        after_motor[4] += learning_paid["vigilance"]
        return {"schema": RECEIPT_SCHEMA, "phase": "POST_PAID_LEARNING",
                "tick": step, "action": action, "param": None,
                "body_after_motor": after_motor,
                "body_after_paid_learning": body,
                "decision_paid": {"energy": 0.15, "vigilance": 0.16},
                "learning_paid": learning_paid,
                "death_causes": deaths or [],
                "world_state_sha256": "d"*64,
                "mind_state_sha256": "e"*64}

    def prepared(self, step=1, body=None, action="attendre"):
        current = self.start if step == 1 else inspect(self.root, self.claim)
        return prepare(self.root, self.claim,
                       expected_head=current["head_sha256"],
                       intent=self.intent(step, body, action))

    def seal(self, prepared, receipt):
        return seal(self.root, self.claim,
                    expected_head=prepared["prior_head_sha256"],
                    seal_token=prepared["seal_token"], receipt=receipt)

    def test_prepared_is_fail_closed_and_commit_then_cold_inspection(self):
        prepared = self.prepared()
        self.assertFalse(prepared["recoverable"])
        with self.assertRaisesRegex(PermissionError, "uncertain prepared motor"):
            inspect(self.root, self.claim)
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim,
                    expected_head=self.start["head_sha256"], intent=self.intent())
        with self.assertRaises(PermissionError):
            seal(self.root, self.claim,
                 expected_head=prepared["prior_head_sha256"],
                 seal_token="0"*64, receipt=self.receipt())
        committed = self.seal(prepared, self.receipt())
        recovered = inspect(self.root, self.claim)
        self.assertEqual(committed["head_sha256"], recovered["head_sha256"])
        self.assertEqual(recovered["sequence"], 1)
        self.assertEqual(recovered["terminal"], "OPEN")
        self.assertFalse(recovered["durable_m11"])
        self.assertEqual(recovered["last_body"], self.receipt()["body_after_paid_learning"])
        self.assertIsNone(recovered["prepared"])
        self.assertNotIn("seal_token", str(recovered))
        with closing(sqlite3.connect(self.root / DB_NAME)) as con:
            self.assertIsNone(con.execute("SELECT seal_token_hash FROM steps").fetchone()[0])

    def test_reject_stale_writer_wrong_body_and_stop_at_horizon(self):
        p = self.prepared()
        sealed = self.seal(p, self.receipt())
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim, expected_head=self.start["head_sha256"],
                    intent=self.intent(step=2, before=self.receipt()["body_after_paid_learning"]))
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim, expected_head=sealed["head_sha256"],
                    intent=self.intent(step=2, before=self.initial))
        p2 = self.prepared(2, self.receipt()["body_after_paid_learning"])
        final = self.seal(p2, self.receipt(step=2, body=[88.,83.,73.,64.,52.]))
        self.assertEqual(final["terminal"], "CENSORED")
        self.assertEqual(inspect(self.root, self.claim)["sequence"], 2)
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim, expected_head=final["head_sha256"],
                    intent=self.intent(step=3))
        with self.assertRaises(PermissionError):
            self.seal(p2, self.receipt(step=2))

    def test_death_is_terminal_even_if_horizon_is_not_reached(self):
        p = self.prepared()
        outcome = self.receipt(deaths=["zero_water"])
        dead = self.seal(p, outcome)
        self.assertEqual(dead["terminal"], "DEAD")
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim, expected_head=dead["head_sha256"],
                    intent=self.intent(step=2, before=outcome["body_after_paid_learning"]))

    def test_fail_bad_receipts_and_unauthenticated_claim(self):
        p = self.prepared()
        bads = [
            {"phase": "PRE_MOTOR"}, {"tick": 2}, {"action": "boire"},
            {"decision_paid": {"energy": -1, "vigilance": 0}},
            {"decision_paid": {"energy": float("nan"), "vigilance": 0}},
            {"death_causes": ["unknown"]}, {"body_after_paid_learning": [101,0,0,0,0]},
            {"world_state_sha256": "X"*64},
        ]
        for edit in bads:
            with self.subTest(edit=str(edit)), self.assertRaises(PermissionError):
                self.seal(p, dict(self.receipt(), **edit))
        with self.assertRaises(PermissionError):
            inspect(self.root, replace(self.claim, life_seed=99))
        self.seal(p, self.receipt())

    def test_payment_body_and_mortality_must_be_mutually_consistent(self):
        p = self.prepared()
        baseline = self.receipt()
        cases = [
            {"learning_paid": {"energy": 0.07, "vigilance": 0.05}},
            {"body_after_paid_learning": [90., 0., 74., 65., 54.]},
            {"death_causes": ["zero_water"]},
            {"body_after_motor": [90., 84., 74., 65., 54.]},
            {"body_after_paid_learning": [90., 84., 74., 0., 54.]},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(PermissionError):
                self.seal(p, dict(baseline, **changes))
        self.seal(p, baseline)

    def test_tampering_missing_and_foreign_database_rejected(self):
        with closing(sqlite3.connect(self.root / DB_NAME)) as con:
            con.execute("UPDATE session SET head=?", ("0"*64,))
            con.commit()
        with self.assertRaises(PermissionError):
            inspect(self.root, self.claim)
        with closing(sqlite3.connect(self.root / DB_NAME)) as con:
            con.execute("UPDATE session SET head=?", (self.start["head_sha256"],))
            con.commit()
        with closing(sqlite3.connect(self.root / DB_NAME)) as con:
            con.execute("CREATE TABLE foreign_table (id INTEGER)")
            con.commit()
        with self.assertRaises(PermissionError):
            inspect(self.root, self.claim)

    def test_gap_reordered_and_corrupted_seal_rejected(self):
        p = self.prepared()
        self.seal(p, self.receipt())
        with closing(sqlite3.connect(self.root / DB_NAME)) as con:
            con.execute("UPDATE steps SET receipt_json=? WHERE seq=1", ('{"fake":1}',))
            con.commit()
        with self.assertRaises(PermissionError):
            inspect(self.root, self.claim)

    def test_concurrent_prepared_intent_only_one_writer_wins(self):
        def attempt(_):
            try:
                return prepare(self.root, self.claim,
                               expected_head=self.start["head_sha256"],
                               intent=self.intent())
            except PermissionError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (0, 1)))
        self.assertEqual(sum(result is not None for result in results), 1)
        with self.assertRaises(PermissionError):
            inspect(self.root, self.claim)
        accepted = next(result for result in results if result is not None)
        self.seal(accepted, self.receipt())
        self.assertEqual(inspect(self.root, self.claim)["sequence"], 1)

    def test_reject_noninteger_tick_and_foreign_schema(self):
        with self.assertRaises(PermissionError):
            prepare(self.root, self.claim,
                    expected_head=self.start["head_sha256"],
                    intent=dict(self.intent(), tick_before=False))
        p = self.prepared()
        with self.assertRaises(PermissionError):
            self.seal(p, dict(self.receipt(), tick=True))
        self.seal(p, self.receipt())

    def test_no_world_identity_or_registration_implicitly_executed(self):
        from i3.runtime import engineering_step_ledger
        import inspect as pyinspect
        source = pyinspect.getsource(engineering_step_ledger)
        for forbidden in ("World(", "Mind(", "run_life(", "i1lab", "pickle."):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
