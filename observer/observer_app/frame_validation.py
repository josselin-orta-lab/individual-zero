"""Structural checks for proposed 2D frame exports.

No Core imports. Successful parsing is NOT independent causal attestation.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

MAX_FRAME_BYTES = 16 * 1024 * 1024
MAX_FRAMES = 100_000
MAX_ENTITIES = 10_000


def validate_frames(path: Path) -> dict[str, Any]:
    result = {"structurally_valid": False, "independently_verified": False,
              "map_authorized": False, "frame_count": 0, "errors": []}
    def reject(reason: str) -> dict[str, Any]:
        result["errors"].append(reason)
        return result
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_FRAME_BYTES + 1)
        if len(data) > MAX_FRAME_BYTES:
            return reject("archive_too_large")
        def reject_duplicate_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate JSON key")
                result[key] = value
            return result
        document = json.loads(data, object_pairs_hook=reject_duplicate_keys,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON value")))
    except (OSError, ValueError, UnicodeError):
        return reject("unreadable_json")
    def json_values_safe(value: Any) -> bool:
        if value is None or type(value) in (str, bool, int):
            return True
        if type(value) is float:
            return math.isfinite(value)
        if isinstance(value, list):
            return all(json_values_safe(item) for item in value)
        if isinstance(value, dict):
            return all(isinstance(key, str) and json_values_safe(item) for key, item in value.items())
        return False
    if not json_values_safe(document):
        return reject("nonfinite_or_unsupported_json")
    if not isinstance(document, dict) or set(document) != {"schema", "identity", "geometry", "frames", "attestation"}:
        return reject("invalid_root")
    if document["schema"] != "observer-world-frames-v1":
        return reject("unknown_schema")
    identity = document["identity"]
    if not isinstance(identity, dict) or set(identity) != {"individual_id", "life_generation", "attempt_ref"}:
        return reject("invalid_identity")
    if not all(isinstance(identity[k], str) and 0 < len(identity[k]) <= 128 for k in ("individual_id", "attempt_ref")) or type(identity["life_generation"]) is not int or identity["life_generation"] < 0:
        return reject("invalid_identity_values")
    geometry = document["geometry"]
    if not isinstance(geometry, dict) or set(geometry) != {"coordinate_system", "width", "height"}:
        return reject("invalid_geometry")
    width, height = geometry["width"], geometry["height"]
    if geometry["coordinate_system"] != "grid-xy-top-left" or type(width) is not int or type(height) is not int or not 1 <= width <= 10000 or not 1 <= height <= 10000:
        return reject("invalid_dimensions")
    attestation = document["attestation"]
    required = {"journal_head_sha256", "journal_event_count", "verifier", "verified_at", "source_sha256"}
    if not isinstance(attestation, dict) or set(attestation) != required:
        return reject("invalid_attestation")
    def digest(x: Any) -> bool:
        return isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x)
    if not digest(attestation["journal_head_sha256"]) or not digest(attestation["source_sha256"]) or type(attestation["journal_event_count"]) is not int or attestation["journal_event_count"] < 1 or not all(isinstance(attestation[k], str) and bool(attestation[k]) for k in ("verifier", "verified_at")):
        return reject("invalid_attestation_values")
    frames = document["frames"]
    if not isinstance(frames, list) or len(frames) > MAX_FRAMES:
        return reject("invalid_frames")
    def position(p: Any) -> bool:
        return isinstance(p, dict) and set(p) == {"x", "y"} and type(p["x"]) is int and type(p["y"]) is int and 0 <= p["x"] < width and 0 <= p["y"] < height
    previous = -1
    for frame in frames:
        if not isinstance(frame, dict) or set(frame) != {"t_monde", "step_boundary", "individual_pose", "entities"}:
            return reject("invalid_frame")
        step = frame["t_monde"]
        if type(step) is not int or step <= previous or frame["step_boundary"] != "committed":
            return reject("unordered_or_uncommitted_step")
        previous = step
        if not position(frame["individual_pose"]):
            return reject("invalid_individual_position")
        entities = frame["entities"]
        if not isinstance(entities, list) or len(entities) > MAX_ENTITIES:
            return reject("invalid_entities")
        ids = set()
        for entity in entities:
            if not isinstance(entity, dict) or set(entity) != {"id", "kind", "position"}:
                return reject("invalid_entity")
            eid, kind = entity["id"], entity["kind"]
            if not isinstance(eid, str) or not 0 < len(eid) <= 128 or eid in ids or not isinstance(kind, str) or not 0 < len(kind) <= 128 or not position(entity["position"]):
                return reject("duplicate_or_invalid_entity")
            ids.add(eid)
    result["frame_count"] = len(frames)
    result["structurally_valid"] = True
    return result
