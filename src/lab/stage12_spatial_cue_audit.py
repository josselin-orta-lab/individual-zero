"""Independent GA-SPATIAL-01 audit of legal local perceptual cue receipts.

Read-only canonical journal analysis: does NOT prove underlying physical truth,
agency, or a bias. No I0 cognition, WorldBody, Oracle, Bench imports.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .independent_journal_audit import audit_export_bytes

OFFSETS = {
    "north": (0, -1), "south": (0, 1),
    "east": (1, 0), "west": (-1, 0),
}
_CAPTURE_SCHEMA = "stage12-first-person-cue-v1"


@dataclass(frozen=True, slots=True)
class Stage12SpatialCueReceiptAudit:
    head_hash: str
    occurrences: int
    legal_adjacent_receipts: int
    passable_cells: int
    nonpassable_cells: int

    def as_dict(self):
        return {
            "schema": "stage12-spatial-visible-cue-receipt-audit-v1",
            **vars(self),
            "objective_physical_causation_proven": False,
            "first_person_world_judgement_proven": False,
        }


def audit_spatial_visible_cues(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12SpatialCueReceiptAudit:
    anchor = dict(expected_head=expected_head, expected_count=expected_count)
    verified = audit_export_bytes(content, **anchor)
    rows = [json.loads(line) for line in content.splitlines()]
    samples = passable = blocked = 0
    seen: set[tuple[int, str]] = set()
    for row in rows:
        event = row["causal_event"]
        if event.get("kind") != "perceptual_capture":
            continue
        data = event.get("data")
        if not isinstance(data, dict) or "agency_visible_adjacent" not in data:
            if isinstance(data, dict) and data.get("agency_capture_schema") == _CAPTURE_SCHEMA:
                raise ValueError("first-person capture missing adjacent cue provenance")
            continue
        if (event.get("emitter") != "stage3-runtime"
                or data.get("agency_capture_schema") != _CAPTURE_SCHEMA
                or data.get("capture_t_monde") != event.get("t_monde")
                or type(event.get("t_monde")) is not int
                or type(event.get("attempt_ref")) is not str
                or not event["attempt_ref"]
                or type(data.get("position")) is not dict):
            raise ValueError("spatial cue receipt lacks authorized perception")
        pos = data["position"]
        if (set(pos) != {"x", "y"}
                or type(pos["x"]) is not int or type(pos["y"]) is not int):
            raise ValueError("invalid perceived source position")
        key = (event["t_monde"], event["attempt_ref"])
        if key in seen:
            raise ValueError("duplicated perceptual source in one physical step")
        seen.add(key)
        cells = data["agency_visible_adjacent"]
        if not isinstance(cells, list) or len(cells) != 4:
            raise ValueError("spatial cue requires four observed cardinal cells")
        found = set()
        for c in cells:
            if type(c) is not dict or set(c) != {
                "direction", "x", "y", "passable", "water_source", "resources",
            }:
                raise ValueError("malformed spatial first-person cell witness")
            direction = c["direction"]
            if direction not in OFFSETS or direction in found:
                raise ValueError("duplicate or unknown spatial direction")
            found.add(direction)
            dx, dy = OFFSETS[direction]
            if (type(c["x"]) is not int or type(c["y"]) is not int
                    or (c["x"], c["y"]) != (pos["x"]+dx, pos["y"]+dy)
                    or type(c["passable"]) is not bool
                    or type(c["water_source"]) is not bool
                    or type(c["resources"]) is not list
                    or any(type(k) is not str or not k for k in c["resources"])
                    or sorted(set(c["resources"])) != c["resources"]):
                raise ValueError("spatial witness incompatible with perceived cell")
            passable += int(c["passable"])
            blocked += int(not c["passable"])
        samples += 1
    return Stage12SpatialCueReceiptAudit(
        head_hash=verified.head_hash, occurrences=verified.occurrences,
        legal_adjacent_receipts=samples,
        passable_cells=passable, nonpassable_cells=blocked,
    )
