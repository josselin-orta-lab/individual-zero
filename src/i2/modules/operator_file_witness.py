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
        # In-process pins detect renamed custody paths; they are NOT
        # independent anti-rollback checkpoints across new processes.
        self._directory_inode = None
        self._lock_inode = None
        self._log_inode = None
        self._check_directory()

    def _check_directory(self) -> None:
        try:
            s = self.directory.lstat()
        except OSError as exc:
            raise WitnessStoreError("operator witness directory unavailable") from exc
        if (not stat.S_ISDIR(s.st_mode) or s.st_uid != os.getuid()
                or stat.S_IMODE(s.st_mode) & 0o077):
            raise WitnessStoreError("operator witness directory must be private")
        identity = (s.st_dev, s.st_ino)
        if self._directory_inode is None:
            self._directory_inode = identity
        elif identity != self._directory_inode:
            raise WitnessStoreError("operator witness directory was replaced")

    def _check_named_file(self, name: str, fd: int) -> None:
        """Require the locked/open inode to remain its named custody path.

        Checks cooperative local swaps, not malicious same-UID operations
        after the final check or coherent rollback across new instances.
        """
        if name not in (".writer.lock", "heads.jsonl"):
            raise ValueError("unknown operator witness custody path")
        held = os.fstat(fd)
        try:
            named = os.stat(self.directory / name, follow_symlinks=False)
        except OSError as exc:
            raise WitnessStoreError("operator witness custody path disappeared") from exc
        identity = (held.st_dev, held.st_ino)
        # An unlinked fd already has nlink=0. Classify a changed named
        # file as a path replacement before the generic unsafe-fd error.
        if (not stat.S_ISREG(named.st_mode)
                or (named.st_dev, named.st_ino) != identity):
            raise WitnessStoreError("operator witness custody path was replaced")
        if (not stat.S_ISREG(held.st_mode) or held.st_nlink != 1
                or held.st_uid != os.getuid()
                or stat.S_IMODE(held.st_mode) & 0o077):
            raise WitnessStoreError("unsafe operator witness file")
        attribute = "_lock_inode" if name == ".writer.lock" else "_log_inode"
        pinned = getattr(self, attribute)
        if pinned is None:
            setattr(self, attribute, identity)
        elif pinned != identity:
            raise WitnessStoreError("operator witness custody inode changed")

    @contextmanager
    def _locked(self) -> Iterator[bool]:
        self._check_directory()
        lock_path = self.directory / ".writer.lock"
        fresh_lock = False
        try:
            try:
                fd = os.open(lock_path, os.O_RDWR | _FLAGS)
            except FileNotFoundError:
                # A missing lock beside an existing journal cannot safely
                # serialize concurrent writers. Do not bootstrap a new lock.
                if (self._lock_inode is not None
                        or (self.directory / "heads.jsonl").exists()):
                    raise WitnessStoreError("operator witness lock disappeared")
                try:
                    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR | _FLAGS, 0o600)
                    fresh_lock = True
                except FileExistsError:
                    # Another cooperative process created the lock first.
                    fd = os.open(lock_path, os.O_RDWR | _FLAGS)
        except OSError as exc:
            raise WitnessStoreError("operator witness lock unavailable") from exc
        try:
            self._check_named_file(".writer.lock", fd)
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                self._check_directory()
                self._check_named_file(".writer.lock", fd)
                try:
                    yield fresh_lock
                finally:
                    # Detect an orphaned lock inode before claiming success.
                    self._check_directory()
                    self._check_named_file(".writer.lock", fd)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def _open(self, *, create: bool, append: bool = False) -> int:
        # A genesis may create exactly ONE new log, guarded by a newly
        # created lock. Existing logs are opened without O_CREAT; a removed
        # journal must not be silently reset to an empty valid genesis.
        flags = (os.O_RDWR | os.O_APPEND if append else os.O_RDONLY) | _FLAGS
        if create:
            if not append:
                raise ValueError("genesis journal requires append mode")
            flags |= os.O_CREAT | os.O_EXCL
        try:
            fd = os.open(self.directory / "heads.jsonl", flags, 0o600)
        except FileNotFoundError as exc:
            raise WitnessStoreError("no witnessed genesis") from exc
        except OSError as exc:
            raise WitnessStoreError("operator witness log unavailable") from exc
        try:
            self._check_named_file("heads.jsonl", fd)
        except BaseException:
            os.close(fd)
            raise
        return fd

    def _scan(self, fd: int) -> tuple[dict[str, LatestWitness], str | None]:
        os.lseek(fd, 0, os.SEEK_SET)
        with os.fdopen(os.dup(fd), "rb") as stream:
            data = stream.read()
        if data and not data.endswith(b"\n"):
            raise WitnessStoreError("torn operator witness log")
        latest: dict[str, LatestWitness] = {}
        previous: str | None = None
        # Preserve exact bytes, including CRLF. splitlines() erases line
        # endings and json.loads() silently accepts duplicate JSON keys.
        # The recorded representation must be unique, not merely a parsed
        # object that produces the same HMAC under re-serialization.
        for line in data.split(b"\n")[:-1]:
            try:
                row = json.loads(line)
                if _canonical(row) != line:
                    raise ValueError("noncanonical operator witness bytes")
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
        self._check_directory()
        # Do not create an empty lock during a failed pre-genesis read;
        # a subsequent legitimate first stage must own a fresh lock.
        if not (self.directory / "heads.jsonl").exists():
            raise WitnessStoreError("no witnessed genesis")
        with self._locked():
            fd = self._open(create=False)
            try:
                latest, _ = self._scan(fd)
                self._check_directory()
                self._check_named_file("heads.jsonl", fd)
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
        with self._locked() as fresh_lock:
            fd = self._open(create=fresh_lock, append=True)
            try:
                latest, previous = self._scan(fd)
                if not fresh_lock and previous is None:
                    raise WitnessStoreError("empty existing witness history")
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
                if fresh_lock:
                    dfd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(dfd)
                    finally:
                        os.close(dfd)
                self._check_directory()
                self._check_named_file("heads.jsonl", fd)
                return LatestWitness(**raw, proof_ref="hmac-sha256:" + mac)
            finally:
                os.close(fd)
