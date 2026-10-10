"""No-follow read-only file opener for Stage-9 raw scientific artifacts.

The path check and the actual descriptor open must not form a symlink
time-of-check/time-of-use gap. This is local technical integrity only:
the operator still needs independent physical custody and runtime witnesses.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import stat
from typing import BinaryIO, Iterator


@contextmanager
def open_regular_no_follow(path: Path) -> Iterator[BinaryIO]:
    """Open a regular file via no-follow directory descriptors, fail closed.

    Walk each directory relative to its already-open parent. The final inode
    and its on-disk path must still agree, and must not be mutated during the
    read. Filesystem integrity does not independently attest authenticity.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("raw artifact custody requires no-follow file opens")
    absolute = path.absolute()
    if len(absolute.parts) < 2:
        raise ValueError("raw artifact must identify a regular file")
    directory_flags = (
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = (
        os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    directory_fd: int | None = None
    file_fd: int | None = None
    try:
        directory_fd = os.open(absolute.parts[0], directory_flags)
        for part in absolute.parts[1:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        file_fd = os.open(absolute.parts[-1], file_flags, dir_fd=directory_fd)
        opened = os.fstat(file_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("raw artifact is not a regular file")
        current = absolute.lstat()
        if (
            not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino)
            != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("raw artifact changed during descriptor open")
        if any(part.is_symlink() for part in (absolute, *absolute.parents)):
            raise ValueError("raw artifact path changed to a symlink")
        with os.fdopen(file_fd, "rb") as stream:
            file_fd = None
            yield stream
            after = os.fstat(stream.fileno())
            if (
                (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns)
                !=
                (opened.st_dev, opened.st_ino, opened.st_size,
                 opened.st_mtime_ns, opened.st_ctime_ns)
            ):
                raise ValueError("raw artifact changed during descriptor read")
    except OSError as exc:
        raise ValueError(
            "raw artifact path changed or traversed a symlink during open"
        ) from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)
