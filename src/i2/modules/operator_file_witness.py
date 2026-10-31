"""Operator-side, inert monotone witness *laboratory*, not an I2 authority.

Append-only file custody with process-level flock, HMAC-SHA256, strict CAS,
fsync and cold audit. It is NOT an independent M11 signer: the operator key,
filesystem and process isolation are test-controlled and the entire directory
can be rolled back. A claim is supplied by the operator, not by WorldBody.

No engine, birth, admission, scheduler, recovery or physics imports exist.
The store is an external PROJECTION of synthetic journal heads, never a
second owner of the individual's state.
"""
from __future__ import annotations

from dataclasses import asdict
from contextlib import contextmanager
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
from typing import Iterator

from .lifecycle_external_witness import (
    LatestWitness, LIFECYCLE_SCHEMA, WITNESS_SCHEMA, ZERO_HASH, _ref,
)

STORE_SCHEMA = "i2-operator-file-witness-laboratory-v1"
UNTRUSTED_PROOF = "untrusted:operator-claim"
_FIELDS = frozenset({
    "witness_schema", "life_ref", "genesis_ref", "journal_schema", "committed",
    "last_step", "chain_head", "terminal_ref", "terminal_step",
})
_ROW_FIELDS = frozenset({"schema", "key_id", "claim", "prior_mac", "mac"})
_FLAGS = getattr(os, "O_NOFOLLOW", 0)


class WitnessStoreError(ValueError):
    """Fail-closed custody error, never a life-recovery instruction."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


class OperatorFileWitness:
    """Single-directory test custody; ONLY for offline read-only inspection.

    read_verified_latest and stage are serialized by the same OS file lock.
    This protects cooperative processes using THIS store, not a hostile
    filesystem, cloned directory, compromised signer or external network.
    """

    def __init__(self, *, directory: Path, key_id: str, key: bytes) -> None:
        self.directory = Path(directory)
        self.key_id = _ref(key_id, "operator key id")
        if type(key) is not bytes or len(key) < 32:
            raise ValueError("test custody requires at least 32 key bytes")
        self._key = key
        self._check_directory()

    def _check_directory(self) -> None:
        if self.directory.is_symlink() or not self.directory.is_dir():
            raise WitnessStoreError("unavailable or linked operator witness directory")
        s = self.directory.stat()
        if s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) & 0o077:
            raise WitnessStoreError("operator witness directory must be private")

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self._check_directory()
        fd = os.open(self.directory / ".writer.lock",
                     os.O_CREAT | os.O_RDWR | _FLAGS, 0o600)
        try:
            s = os.fstat(fd)
            if (not stat.S_ISREG(s.st_mode) or s.st_nlink != 1
                    or s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) & 0o077):
                raise WitnessStoreError("unsafe operator witness lock")
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._check_directory()
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def _open(self, *, create: bool) -> int:
        flags = (os.O_RDWR | os.O_APPEND | os.O_CREAT if create
                 else os.O_RDONLY) | _FLAGS
        try:
            fd = os.open(self.directory / "heads.jsonl", flags, 0o600)
        except FileNotFoundError as exc:
            raise WitnessStoreError("no witnessed genesis") from exc
        s = os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or
                s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) & 0o077):
            os.close(fd)
            raise WitnessStoreError("unsafe operator witness log")
        return fd

    def _scan(self, fd: int) -> tuple[dict[str, LatestWitness], str | None]:
        os.lseek(fd, 0, os.SEEK_SET)
        with os.fdopen(os.dup(fd), "rb") as stream:
            data = stream.read()
        if data and not data.endswith(b"\n"):
            raise WitnessStoreError("torn operator witness log")
        latest: dict[str, LatestWitness] = {}
        previous: str | None = None
        for line in data.splitlines():
            try:
                row = json.loads(line)
                if (type(row) is not dict or set(row) != _ROW_FIELDS or
                        row["schema"] != STORE_SCHEMA or
                        row["key_id"] != self.key_id or
                        type(row["claim"]) is not dict or
                        set(row["claim"]) != _FIELDS or
                        row["prior_mac"] != previous or
                        type(row["mac"]) is not str or len(row["mac"]) != 64):
                    raise ValueError("invalid witness row")
                signed = {k: row[k] for k in ("schema", "key_id", "claim", "prior_mac")}
                expected = hmac.new(self._key, _canonical(signed),
                                    hashlib.sha256).hexdigest()
                if not hmac.compare_digest(row["mac"], expected):
                    raise ValueError("witness MAC failed")
                c = row["claim"]
                record = LatestWitness(**c, proof_ref="hmac-sha256:" + row["mac"])
                record.validate()
                older = latest.get(record.life_ref)
                if older is None:
                    if record.committed != 0:
                        raise ValueError("witness missing genesis")
                elif (older.genesis_ref != record.genesis_ref or
                      older.terminal_ref is not None or
                      record.committed != older.committed + 1 or
                      record.last_step <= older.last_step):
                    raise ValueError("witness history fork or terminal append")
                latest[record.life_ref] = record
                previous = row["mac"]
            except (TypeError, ValueError, KeyError, UnicodeError) as exc:
                raise WitnessStoreError("unverifiable operator witness history") from exc
        return latest, previous

    def read_verified_latest(self, *, life_ref: str,
                             genesis_ref: str) -> LatestWitness:
        """Read/verify one monotone view under the SAME process-shared lock."""
        _ref(life_ref, "witness life")
        _ref(genesis_ref, "witness genesis")
        with self._locked():
            fd = self._open(create=False)
            try:
                latest, _ = self._scan(fd)
            finally:
                os.close(fd)
        record = latest.get(life_ref)
        if record is None or record.genesis_ref != genesis_ref:
            raise WitnessStoreError("witness identity not registered")
        return record

    def stage(self, *, claim: LatestWitness,
              expected_proof_ref: str | None = None) -> LatestWitness:
        """CAS-append a caller-claimed synthetic head; never publish a world.

        First claim MUST be genesis-only, with no predecessor proof. Every
        next claim MUST follow exactly one sequence and match the previous
        authenticated proof. An ambiguous/lost acknowledgement must be
        resolved by read_verified_latest, never a physical retry.
        """
        if type(claim) is not LatestWitness or claim.proof_ref != UNTRUSTED_PROOF:
            raise ValueError("only explicit untrusted operator claims are accepted")
        claim.validate()
        with self._locked():
            existed = (self.directory / "heads.jsonl").exists()
            fd = self._open(create=True)
            try:
                latest, previous = self._scan(fd)
                older = latest.get(claim.life_ref)
                if older is None:
                    if expected_proof_ref is not None or claim.committed != 0:
                        raise WitnessStoreError("genesis must start at empty head")
                else:
                    if older.genesis_ref != claim.genesis_ref:
                        raise WitnessStoreError("conflicting genesis for life identity")
                    if older.terminal_ref is not None:
                        raise WitnessStoreError("terminal witness is absorbing")
                    if expected_proof_ref != older.proof_ref:
                        raise WitnessStoreError("stale writer or duplicate acknowledgement")
                    if (claim.committed != older.committed + 1 or
                            claim.last_step <= older.last_step):
                        raise WitnessStoreError("non-monotone or forked proposed head")
                raw = asdict(claim)
                del raw["proof_ref"]
                signed = {"schema": STORE_SCHEMA, "key_id": self.key_id,
                          "claim": raw, "prior_mac": previous}
                mac = hmac.new(self._key, _canonical(signed),
                               hashlib.sha256).hexdigest()
                row = dict(signed, mac=mac)
                line = _canonical(row) + b"\n"
                if os.write(fd, line) != len(line):
                    raise WitnessStoreError("short operator witness write")
                os.fsync(fd)
                if not existed:
                    dfd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(dfd)
                    finally:
                        os.close(dfd)
                return LatestWitness(**raw, proof_ref="hmac-sha256:" + mac)
            finally:
                os.close(fd)
