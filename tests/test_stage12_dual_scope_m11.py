"""Actual SQLite M11 born-enabled dual-scope identity and cold continuity."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from lab.m11_transactional_mortal import M11TransactionalMortal, RecoveryBlocked
from lab.sqlite_life_store import SQLiteLifeLedger
from test_stage12_dual_scope_runtime import born


class DualScopeM11Tests(unittest.TestCase):
    def test_atomic_current_generation_cold_resume(self):
        with TemporaryDirectory() as d:
            db=str(Path(d)/"individual.sqlite")
            who="dual:m11:one"
            mk=lambda:born(Path(d)/"unused",m11=True,life_id=who)
            with M11TransactionalMortal.birth(db_path=db,runtime=mk(),
                                               individual_id=who) as owner:
                self.assertEqual(owner.run_step().generation,1)
            ledger=SQLiteLifeLedger.audit_read_only(
                path=db,expected_individual_id=who)
            self.assertEqual(ledger.generation,1)
            with M11TransactionalMortal.cold_recover(
                    db_path=db,individual_id=who,runtime_factory=mk) as owner:
                self.assertEqual(owner.run_step().generation,2)
            ledger=SQLiteLifeLedger.audit_read_only(
                path=db,expected_individual_id=who)
            self.assertEqual(ledger.generation,2)
            with SQLiteLifeLedger.open_existing(path=db,
                    expected_individual_id=who) as sqlite:
                rows=[json.loads(x) for x in sqlite.export_canonical_journal().splitlines()]
            self.assertEqual(len(rows),ledger.journal_count)
            self.assertEqual(rows[-1]["event_hash"],ledger.journal_head)

    def test_opposite_birth_contract_rejected_at_cold_recovery(self):
        with TemporaryDirectory() as d:
            db=str(Path(d)/"individual.sqlite")
            who="dual:m11:two"
            with M11TransactionalMortal.birth(db_path=db,
                    runtime=born(Path(d)/"unused",m11=True,life_id=who),
                    individual_id=who) as owner:
                owner.run_step()
            with self.assertRaises((RecoveryBlocked,ValueError)):
                with M11TransactionalMortal.cold_recover(
                        db_path=db,individual_id=who,
                        runtime_factory=lambda:born(Path(d)/"none",m11=True,
                                                     dual=False,life_id=who)):
                    pass


if __name__=="__main__":
    unittest.main()
