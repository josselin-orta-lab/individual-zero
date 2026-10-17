"""Operator-only durable physical frame receipts, separate from I0 cognition.

Append-before-ack JSONL; never replay into a live world. The caller owns the
birth-time exclusive path and the matching causal journal WAL.
"""
from __future__ import annotations

import os
import json
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

    @staticmethod
    def export_world_frames(
        receipts_path: str, destination: str, *,
        individual_id: str, life_generation: int,
        journal_path: str | None = None,
    ) -> None:
        """Produce a bounded, explicitly unverified Observer import document.

        This export is not an independent scientific attestation. Receipt
        continuity and journal custody require separate offline checks.
        """
        import hashlib
        from datetime import datetime, timezone

        source = Path(receipts_path)
        target = Path(destination)
        if not source.is_absolute() or not target.is_absolute():
            raise ValueError("archive paths must be absolute")
        if type(life_generation) is not int or life_generation < 0:
            raise ValueError("invalid life generation")
        if source.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("oversized frame receipts")
        with source.open("rb") as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024 or not raw or not raw.endswith(b"\n"):
            raise ValueError("missing, oversized or torn frame receipts")
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate operator receipt key")
                result[key] = value
            return result

        receipts = []
        for line in raw.splitlines():
            receipt = json.loads(line, object_pairs_hook=unique_keys,
                                 parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite receipt")))
            if canonical_causal_bytes(receipt) != line:
                raise ValueError("noncanonical operator receipt")
            receipts.append(receipt)
        for receipt in receipts:
            if (type(receipt) is not dict
                    or type(receipt.get("frame")) is not dict
                    or receipt["frame"].get("step_boundary") != "committed"
                    or type(receipt.get("attempt_ref")) is not str
                    or not receipt["attempt_ref"]
                    or type(receipt.get("journal_event_count")) is not int
                    or receipt["journal_event_count"] < 1
                    or type(receipt.get("journal_head_sha256")) is not str
                    or len(receipt["journal_head_sha256"]) != 64
                    or any(c not in "0123456789abcdef" for c in receipt["journal_head_sha256"])
                    or ("journal_closure_hash" in receipt and (
                        type(receipt["journal_closure_hash"]) is not str
                        or len(receipt["journal_closure_hash"]) != 64
                        or any(c not in "0123456789abcdef" for c in receipt["journal_closure_hash"])))):
                raise ValueError("invalid operator receipt")
        steps = [r["frame"]["t_monde"] for r in receipts]
        if any(type(step) is not int or step < 1 for step in steps):
            raise ValueError("invalid recorded world step")
        if steps != list(range(1, len(steps) + 1)):
            raise ValueError("incomplete or unordered world frames")
        counts = [r["journal_event_count"] for r in receipts]
        if any(a >= b for a, b in zip(counts, counts[1:])):
            raise ValueError("nonmonotonic journal event counts")
        if journal_path is not None:
            journal = Path(journal_path)
            if not journal.is_absolute():
                raise ValueError("journal path must be absolute")
            with journal.open("rb") as stream:
                journal_raw = stream.read(32 * 1024 * 1024 + 1)
            if (len(journal_raw) > 32 * 1024 * 1024 or not journal_raw
                    or journal_raw.startswith(b"\n") or journal_raw.endswith(b"\n")):
                raise ValueError("invalid or oversized canonical journal")
            previous = "00" * 32
            closures = {}
            rows = journal_raw.split(b"\n")
            for index, line in enumerate(rows):
                record = json.loads(line, object_pairs_hook=unique_keys)
                if canonical_causal_bytes(record) != line or record.get("index") != index:
                    raise ValueError("noncanonical journal entry")
                if record.get("previous_hash") != previous:
                    raise ValueError("broken journal chain")
                payload = canonical_causal_bytes({
                    "event_id": record["event_id"], "causal_event": record["causal_event"]})
                digest = hashlib.sha256(bytes.fromhex(previous) + payload).hexdigest()
                if digest != record.get("event_hash"):
                    raise ValueError("invalid journal event hash")
                previous = digest
                event = record["causal_event"]
                if event.get("kind") == "step_closed":
                    step = event["t_monde"]
                    if step in closures:
                        raise ValueError("duplicate journal closure")
                    closures[step] = (event["attempt_ref"], digest, index + 1)
            if len(closures) != len(receipts):
                raise ValueError("missing operator frame for journal closure")
            for receipt in receipts:
                step = receipt["frame"]["t_monde"]
                expected = closures.get(step)
                if (expected is None or
                        (receipt["attempt_ref"], receipt.get("journal_closure_hash"),
                         receipt["journal_event_count"]) != expected or
                        receipt["journal_head_sha256"] != expected[1]):
                    raise ValueError("operator receipt does not match journal closure")
            if receipts[-1]["journal_event_count"] > len(rows):
                raise ValueError("receipt references missing journal events")
        geometry = receipts[0]["geometry"]
        if any(r["geometry"] != geometry for r in receipts):
            raise ValueError("geometry changed within archive")
        last = receipts[-1]
        document = {
            "schema": "observer-world-frames-v1",
            "identity": {"individual_id": individual_id,
                         "life_generation": life_generation,
                         },
            "geometry": geometry,
            "frames": [{**r["frame"], "attempt_ref": r["attempt_ref"]}
                       for r in receipts],
            "attestation": {
                "journal_head_sha256": last["journal_head_sha256"],
                "journal_event_count": last["journal_event_count"],
                "verifier": "engine-receipt-export-unverified",
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
            },
        }
        output = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(target, flags, 0o600)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            parent = os.open(str(target.parent), os.O_RDONLY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        except BaseException:
            target.unlink(missing_ok=True)
            raise
