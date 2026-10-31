"""G2 operator-controlled durable witness challenge ledger, not a M11 owner.

Private append-only log + cooperative OS flock. The log is a transport
anti-replay aid, NEVER the cognitive SQLite transaction owner or a trusted
independent witness. Restoring/replacing the entire directory defeats it.
"""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import secrets
import stat
from typing import Callable

_CHARS = frozenset("0123456789abcdef")
_FLAGS = getattr(os, "O_NOFOLLOW", 0)
_MAX_RECORDS = 4096
_LINE_SIZE = 65


class ChallengeCustodyError(ValueError):
    """Fail-closed challenge custody error; not a recovery instruction."""


def _valid_challenge(value: object) -> bool:
    return type(value) is str and len(value) == 64 and set(value) <= _CHARS


class DurableChallengeSource:
    """Reserve before handing a challenge to the read-only witness transport.

    Protects cooperating processes using the *same unchanged private
    directory*. A process crash before transport leaves the nonce burned.
    Failure and partial writes fail closed rather than guessing whether a
    remote attestation happened. This does not attest the directory itself.
    """

    def __init__(
        self, *, directory: Path,
        candidate_source: Callable[[], str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        if candidate_source is not None and (
            isinstance(candidate_source, type) or not callable(candidate_source)
        ):
            raise ValueError("challenge supplier must be callable")
        # Default CSPRNG; supplier injection is for controlled G2 tests and
        # does NOT establish production entropy or independence.
        self._candidate_source = (
            candidate_source if candidate_source is not None
            else lambda: secrets.token_hex(32)
        )
        # Pin the inode for this instance so a swapped directory is not
        # silently treated as the original custody domain.
        self._directory_inode: tuple[int, int] | None = None
        self._check_directory()

    def _check_directory(self) -> None:
        try:
            st = self.directory.lstat()
        except OSError as exc:
            raise ChallengeCustodyError("challenge directory unavailable") from exc
        if (not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid()
                or stat.S_IMODE(st.st_mode) & 0o077):
            raise ChallengeCustodyError("challenge directory must be private")
        identity = (st.st_dev, st.st_ino)
        if self._directory_inode is None:
            self._directory_inode = identity
        elif identity != self._directory_inode:
            raise ChallengeCustodyError("challenge custody directory was replaced")

    @staticmethod
    def _check_file(fd: int) -> None:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1
                or st.st_uid != os.getuid()
                or stat.S_IMODE(st.st_mode) & 0o077):
            raise ChallengeCustodyError("unsafe challenge custody file")

    def _check_named_file(self, name: str, fd: int) -> None:
        """Require the locked/open descriptor to remain the named inode.

        Cooperative flock on a detached lock inode would not serialize
        another process that opened its replacement. Also reject a log
        replaced after we opened its descriptor, before releasing a nonce.
        """
        self._check_file(fd)
        try:
            named = os.stat(self.directory / name, follow_symlinks=False)
        except OSError as exc:
            raise ChallengeCustodyError("challenge custody file disappeared") from exc
        held = os.fstat(fd)
        if (not stat.S_ISREG(named.st_mode) or
                (named.st_dev, named.st_ino) != (held.st_dev, held.st_ino)):
            raise ChallengeCustodyError("challenge custody file was replaced")

    def _sync_directory(self) -> None:
        fd = os.open(
            self.directory,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | _FLAGS,
        )
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def _inspect_log(data: bytes) -> set[bytes]:
        if data and not data.endswith(b"\n"):
            raise ChallengeCustodyError("torn challenge log")
        seen: set[bytes] = set()
        if data:
            for value in data.split(b"\n")[:-1]:
                try:
                    challenge = value.decode("ascii")
                except UnicodeDecodeError as exc:
                    raise ChallengeCustodyError("invalid challenge log bytes") from exc
                if not _valid_challenge(challenge) or value in seen:
                    raise ChallengeCustodyError("noncanonical or repeated challenge log")
                seen.add(value)
        return seen

    def next_challenge(self) -> str:
        challenge = self._candidate_source()
        if not _valid_challenge(challenge):
            raise ChallengeCustodyError("invalid 256-bit challenge")
        self._check_directory()

        # Separate stable lock inode serializes cooperating readers/writers.
        # Both lock and log live in this non-shared mutable operator domain.
        # Bootstrap only if both custody files are genuinely new. If a
        # previously initialized log or lock disappears, refuse rather than
        # silently creating an empty ledger and admitting an old challenge.
        # Deleting/rolling back BOTH files is still outside local detection.
        fresh_lock = False
        try:
            try:
                lock_fd = os.open(
                    self.directory / ".challenge.lock",
                    os.O_CREAT | os.O_EXCL | os.O_RDWR | _FLAGS, 0o600,
                )
                fresh_lock = True
            except FileExistsError:
                lock_fd = os.open(
                    self.directory / ".challenge.lock",
                    os.O_RDWR | _FLAGS,
                )
        except OSError as exc:
            raise ChallengeCustodyError("challenge lock unavailable") from exc
        try:
            self._check_file(lock_fd)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            self._check_directory()
            self._check_named_file(".challenge.lock", lock_fd)
            try:
                # New lock must pair with a new log. Existing locks MUST
                # reopen an existing nonempty log, never recreate one.
                open_flags = os.O_RDWR | os.O_APPEND | _FLAGS
                if fresh_lock:
                    open_flags |= os.O_CREAT | os.O_EXCL
                log_fd = os.open(
                    self.directory / "challenges.log", open_flags, 0o600,
                )
            except OSError as exc:
                raise ChallengeCustodyError("challenge log unavailable") from exc
            try:
                self._check_named_file("challenges.log", log_fd)
                os.lseek(log_fd, 0, os.SEEK_SET)
                with os.fdopen(os.dup(log_fd), "rb") as stream:
                    data = stream.read(_MAX_RECORDS * _LINE_SIZE + 1)
                if len(data) > _MAX_RECORDS * _LINE_SIZE:
                    raise ChallengeCustodyError("challenge log capacity exhausted")
                if not fresh_lock and not data:
                    raise ChallengeCustodyError("empty existing challenge log")
                seen = self._inspect_log(data)
                if len(seen) >= _MAX_RECORDS:
                    raise ChallengeCustodyError("challenge log capacity exhausted")
                encoded = challenge.encode("ascii")
                if encoded in seen:
                    raise ChallengeCustodyError("persisted challenge already used")
                # A short/torn append causes subsequent scans to fail closed.
                if os.write(log_fd, encoded + b"\n") != _LINE_SIZE:
                    raise ChallengeCustodyError("short challenge reservation write")
                os.fsync(log_fd)
                self._sync_directory()
                # Catch replacement of either path while the ledger was
                # inspected/appended. No claim against hostile same-UID
                # processes, global filesystem rollback or power-loss lies.
                self._check_directory()
                self._check_named_file(".challenge.lock", lock_fd)
                self._check_named_file("challenges.log", log_fd)
            finally:
                os.close(log_fd)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
        # Only after fsync may the caller contact an external transport.
        return challenge
