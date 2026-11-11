"""I3-only engineering birth-slot reservation, NOT a life journal or M11.

The local SQLite transaction prevents one workspace from reusing a reserved
engineering slot. It does not authenticate external originals, support born
state recovery, claim globally unique identities, or admit scientific Worlds.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

SCHEMA = "i3-engineering-birth-reservation/v1"
APP_ID = 0x49334252  # 'I3BR'; reject I1/other SQLite databases
DB_NAME = "i3_birth_reservations.sqlite3"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True, slots=True)
class Reservation:
    birth_index: int
    life_seed: int
    source_sha256: str
    world_sha256: str
    genome_sha256: str
    identity_sha256: str
    scope: str = "I3_ENGINEERING_ONLY_NOT_BORN"

    def payload(self) -> dict:
        return {"schema": SCHEMA, "birth_index": self.birth_index,
                "life_seed": self.life_seed, "source_sha256": self.source_sha256,
                "world_sha256": self.world_sha256,
                "genome_sha256": self.genome_sha256,
                "scope": self.scope}


def make_reservation(*, birth_index: int, life_seed: int,
                     source_sha256: str, world_sha256: str,
                     genome_sha256: str) -> Reservation:
    """Validate identifiers without constructing World, Mind or a life."""
    for value, name, maximum in ((birth_index, "birth_index", 2**63 - 1),
                                 (life_seed, "life_seed", 2**64 - 1)):
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(name + " must be a bounded nonnegative int")
    for value, name in ((source_sha256, "source_sha256"),
                        (world_sha256, "world_sha256"),
                        (genome_sha256, "genome_sha256")):
        if not isinstance(value, str) or SHA256.fullmatch(value) is None:
            raise ValueError(name + " must be a lowercase SHA-256")
    partial = Reservation(birth_index, life_seed, source_sha256,
                          world_sha256, genome_sha256, "")
    identity = sha256(json.dumps(partial.payload(), sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return Reservation(birth_index, life_seed, source_sha256,
                       world_sha256, genome_sha256, identity)


def _path(directory: Path) -> Path:
    if directory.is_symlink() or not directory.is_dir():
        raise PermissionError("existing non-symlink I3 engineering directory required")
    db = directory / DB_NAME
    if db.is_symlink() or (db.exists() and not db.is_file()):
        raise PermissionError("non-symlink regular database required")
    return db


def _check_database(conn: sqlite3.Connection, *, create: bool) -> None:
    app = conn.execute("PRAGMA application_id").fetchone()[0]
    if app not in (0, APP_ID) or (not create and app != APP_ID):
        raise PermissionError("foreign/unsigned I3 engineering database")
    existing = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    if existing - {"reservations"} or (app == 0 and existing):
        raise PermissionError("database has foreign or unauthenticated tables")
    if create and app == 0:
        conn.execute(f"PRAGMA application_id={APP_ID}")
        conn.execute("CREATE TABLE reservations ("
                     "birth_index INTEGER PRIMARY KEY, "
                     "payload TEXT NOT NULL, identity_sha256 TEXT NOT NULL)")
    if app == APP_ID and "reservations" not in existing:
        raise PermissionError("I3 reservation table missing")


def reserve(directory: Path, reservation: Reservation) -> dict:
    """Consume one slot in a real SQLite IMMEDIATE transaction, never birth."""
    if type(reservation) is not Reservation or make_reservation(
            birth_index=reservation.birth_index, life_seed=reservation.life_seed,
            source_sha256=reservation.source_sha256,
            world_sha256=reservation.world_sha256,
            genome_sha256=reservation.genome_sha256) != reservation:
        raise ValueError("reservation identity/content mismatch")
    db = _path(Path(directory))
    try:
        with sqlite3.connect(db, isolation_level=None, timeout=5) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                _check_database(conn, create=True)
                conn.execute("INSERT INTO reservations VALUES (?, ?, ?)",
                             (reservation.birth_index,
                              json.dumps(reservation.payload(), sort_keys=True,
                                         separators=(",", ":")),
                              reservation.identity_sha256))
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
    except sqlite3.IntegrityError as exc:
        raise PermissionError("I3 engineering birth slot already consumed") from exc
    except sqlite3.DatabaseError as exc:
        raise PermissionError("I3 engineering reservation storage failure") from exc
    return {**reservation.payload(), "identity_sha256": reservation.identity_sha256,
            "status": "RESERVED_NOT_BORN", "durable_m11": False,
            "scientific_world_authorized": False}


def inspect(directory: Path, birth_index: int) -> dict:
    """Read an existing reservation; refuse corruption and never create DB."""
    if type(birth_index) is not int or birth_index < 0:
        raise ValueError("birth_index must be a nonnegative int")
    db = _path(Path(directory))
    if not db.is_file():
        raise PermissionError("no reservation database")
    try:
        with sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True) as conn:
            _check_database(conn, create=False)
            row = conn.execute("SELECT payload, identity_sha256 FROM reservations "
                               "WHERE birth_index=?", (birth_index,)).fetchone()
            if row is None:
                raise PermissionError("unreserved I3 engineering birth slot")
            data = json.loads(row[0])
            if (type(data) is not dict or data.get("schema") != SCHEMA
                    or data.get("scope") != "I3_ENGINEERING_ONLY_NOT_BORN"
                    or data.get("birth_index") != birth_index):
                raise PermissionError("invalid I3 reservation record")
            verified = make_reservation(
                birth_index=data["birth_index"], life_seed=data["life_seed"],
                source_sha256=data["source_sha256"],
                world_sha256=data["world_sha256"],
                genome_sha256=data["genome_sha256"])
            if verified.payload() != data or verified.identity_sha256 != row[1]:
                raise PermissionError("I3 reservation digest mismatch")
            return {**data, "identity_sha256": row[1],
                    "status": "RESERVED_NOT_BORN", "durable_m11": False,
                    "scientific_world_authorized": False}
    except (sqlite3.DatabaseError, KeyError, ValueError, TypeError) as exc:
        raise PermissionError("I3 engineering reservation invalid/corrupt") from exc
