"""Operator-only, forward-only historical world capture for Observer replay.

Called solely from an opt-in Lab development runner AFTER one closed physical
step. Reads WorldBody's actual owner state, not perceptions, predictions,
Oracle, Bench or future simulation. Never passes the data to I0.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

from .world import WorldBody


def capture_closed_world(world: WorldBody, *, t_monde: int,
                         closed_event: dict) -> dict:
    if not isinstance(world, WorldBody):
        raise TypeError("capture requires the actual physical WorldBody")
    if (type(t_monde) is not int or t_monde < 1
            or world._mortal_dispatch_active
            or closed_event.get("kind") != "step_closed"
            or closed_event.get("t_monde") != t_monde
            or closed_event.get("data", {}).get("outcome") != "normal"
            or closed_event.get("data", {}).get("world_advance_count") != 1
            or closed_event.get("data", {}).get("applied_command_count") != 1):
        raise ValueError("world capture requires a fully committed live physical step")
    attempt = closed_event.get("attempt_ref")
    if not isinstance(attempt, str) or not attempt or attempt == "no-active-attempt":
        raise ValueError("closed step has no unambiguous attempt reference")
    entities = []
    def add(kind, pos):
        entities.append({
            "id": f"{kind}:{pos.x}:{pos.y}",
            "kind": kind,
            "position": pos.as_dict(),
        })
    for pos in sorted(world._obstacles):
        add("obstacle", pos)
    for pos in sorted(world._water_sources):
        add("water_source", pos)
    for pos in sorted(world._creatures):
        add("creature", pos)
    for pos in sorted(world._danger_zones):
        add("danger_zone", pos)
    for pos in sorted(world._lethal_zones):
        add("lethal_zone", pos)
    for pos in sorted(world._shelters):
        add("shelter", pos)
    for pos, count in sorted(world._placed_stones.items()):
        if count > 0:
            add("placed_stones", pos)
    for (pos, kind), quantity in sorted(
        world._resources.items(), key=lambda x: (x[0][0].x, x[0][0].y, x[0][1])
    ):
        if quantity > 0:
            add("resource_" + kind, pos)
    ids = [entity["id"] for entity in entities]
    if len(ids) != len(set(ids)):
        raise AssertionError("non-unique physical entity identities")
    return {
        "t_monde": t_monde,
        "step_boundary": "committed",
        "attempt_ref": attempt,
        "individual_pose": world.position.as_dict(),
        "entities": entities,
    }


def _write_exclusive(directory: Path, name: str, contents: bytes) -> None:
    path = directory / name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        dirfd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def publish_recorded_world(*, directory: Path, individual_id: str,
                           config, frames: list[dict],
                           canonical_journal: bytes, journal_head: str,
                           journal_count: int, journal_sha256: str) -> None:
    """Publish read-only-replay sources only AFTER complete offline journal audit.

    Both outputs are exclusive, fsynced artifacts. Failure leaves the runner
    unsuccessful; a partial file must never be interpreted as a completed run.
    """
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("capture target must already be a private directory")
    if not isinstance(individual_id, str) or not individual_id or not frames:
        raise ValueError("complete individual identity and recorded frames required")
    if [row["t_monde"] for row in frames] != list(range(1, len(frames) + 1)):
        raise ValueError("only a complete consecutive physical history may be published")
    if not canonical_journal or type(journal_count) is not int or journal_count < 1:
        raise ValueError("missing audited canonical history")
    document = {
        "schema": "observer-world-frames-v1",
        "identity": {"individual_id": individual_id, "life_generation": 0},
        "geometry": {"coordinate_system": "grid-xy-top-left",
                     "width": config.width, "height": config.height},
        "frames": frames,
        "attestation": {"journal_head_sha256": journal_head,
                        "journal_event_count": journal_count,
                        "verifier": "lab.independent_journal_audit (operator-only, same producer)",
                        "verified_at": datetime.now(timezone.utc).isoformat(),
                        "source_sha256": journal_sha256},
    }
    payload = json.dumps(document, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    if b"oracle_canary" in payload or b"oracle_ground_truth" in payload:
        raise AssertionError("privileged source key leaked into world capture")
    if len(payload) > 16 * 1024 * 1024 or len(canonical_journal) > 32 * 1024 * 1024:
        raise ValueError("Observer capture exceeded bounded archive sizes")
    _write_exclusive(directory, "journal.jsonl", canonical_journal)
    _write_exclusive(directory, "world_frames.json", payload)
