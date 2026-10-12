"""Operator-only durable physical frame receipts, separate from I0 cognition.

Append-before-ack JSONL; never replay into a live world. The caller owns the
birth-time exclusive path and the matching causal journal WAL.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .determinism import canonical_causal_bytes


class OperatorFrameArchive:
    def __init__(self, path: str) -> None:
        target = Path(path)
        if not target.is_absolute():
            raise ValueError("operator frame archive path must be absolute")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        self._fd = os.open(target, flags, 0o600)
        try:
            parent = os.open(str(target.parent), os.O_RDONLY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        except BaseException:
            os.close(self._fd)
            self._fd = -1
            raise
        self._last_step = 0
        self._failed = False

    def append(self, receipt: dict[str, object]) -> None:
        if self._failed or self._fd < 0:
            raise RuntimeError("operator frame archive unavailable")
        frame = receipt.get("frame")
        step = frame.get("t_monde") if isinstance(frame, dict) else None
        if type(step) is not int or step <= self._last_step:
            raise ValueError("operator frames must advance monotonically")
        if frame.get("step_boundary") != "committed":
            raise ValueError("only committed physical frames may be archived")
        raw = canonical_causal_bytes(receipt) + b"\n"
        try:
            offset = 0
            while offset < len(raw):
                count = os.write(self._fd, raw[offset:])
                if count <= 0:
                    raise OSError("short operator archive write")
                offset += count
            os.fsync(self._fd)
        except BaseException:
            self._failed = True
            raise
        self._last_step = step

    def close(self) -> None:
        if self._fd >= 0:
            os.close(self._fd)
            self._fd = -1

    def __enter__(self) -> "OperatorFrameArchive":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
