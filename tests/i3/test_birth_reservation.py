"""Engineering-only SQLite birth-slot tests; never create a World or Mind."""
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest

from i3.runtime.birth_reservation import (
    make_reservation, reserve, inspect, DB_NAME,
)

A = "a" * 64
B = "b" * 64
C = "c" * 64


class I3EngineeringBirthReservation(unittest.TestCase):
    def item(self, index=1):
        return make_reservation(
            birth_index=index, life_seed=42,
            source_sha256=A, world_sha256=B, genome_sha256=C)

    def test_atomic_one_shot_and_cold_read_without_birth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.item()
            received = reserve(root, item)
            self.assertFalse(received["durable_m11"])
            self.assertFalse(received["scientific_world_authorized"])
            self.assertEqual(received["status"], "RESERVED_NOT_BORN")
            self.assertEqual(received, inspect(root, 1))
            for again in (item, self.item(1)):
                with self.assertRaises(PermissionError):
                    reserve(root, again)
            self.assertEqual(inspect(root, 1), received)
            next_identity = reserve(root, self.item(2))
            self.assertNotEqual(next_identity["identity_sha256"],
                                received["identity_sha256"])

    def test_foreign_invalid_and_rewritten_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(PermissionError):
                inspect(root, 0)
            self.assertFalse((root / DB_NAME).exists())
            original = dict(
                birth_index=1, life_seed=42,
                source_sha256=A, world_sha256=B, genome_sha256=C)
            for edit in (
                {"birth_index": True}, {"birth_index": -1},
                {"birth_index": 2**63}, {"life_seed": False},
                {"life_seed": 2**64}, {"source_sha256": "f" * 63},
                {"world_sha256": "A" * 64},
            ):
                with self.subTest(edit=edit), self.assertRaises(ValueError):
                    make_reservation(**dict(original, **edit))
            with self.assertRaises(ValueError):
                reserve(root, replace(self.item(), source_sha256=B))

    def test_foreign_database_tamper_and_missing_slot_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with sqlite3.connect(root / DB_NAME) as conn:
                conn.execute("CREATE TABLE other (v INTEGER)")
            with self.assertRaises(PermissionError):
                reserve(root, self.item())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reserve(root, self.item())
            with self.assertRaises(PermissionError):
                inspect(root, 2)
            with sqlite3.connect(root / DB_NAME) as conn:
                conn.execute(
                    "UPDATE reservations SET identity_sha256=? "
                    "WHERE birth_index=1", ("0" * 64,))
            with self.assertRaises(PermissionError):
                inspect(root, 1)
            with self.assertRaises(PermissionError):
                reserve(root, self.item())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with sqlite3.connect(root / DB_NAME) as conn:
                conn.execute("PRAGMA application_id=1234")
            with self.assertRaises(PermissionError):
                reserve(root, self.item())

    def test_reservation_has_no_world_birth_or_active_engine_authority(self):
        import inspect as python_inspect
        from i3.runtime import birth_reservation
        code = python_inspect.getsource(birth_reservation)
        for forbidden in (
            "from i3.modules.world", "from i3.modules.mind",
            "run_life(", "World(", "i1lab", "I3_SCIENTIFIC",
        ):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
