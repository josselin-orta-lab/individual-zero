"""Prospective scientific preregistration preflight for Stage 9.

Normative: EN MVP v1.2.1 §§13.2, 19.5, 20.3 Stage 9; INV-25.
This validates a protocol draft, NOT that it predates any held-out results.
A separate Git ancestry review, witnessed campaign and exact replay are
necessary before a scientific or Golden decision can be made.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import re
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex


SPEC_PATH = "docs/architecture/reference/en/mvp-specification-v1.2.1.md"
REGISTRATION_VERSION = "stage9-preregistration-schema-v2"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED_FIELDS = frozenset({
    "protocol_version", "registration_id", "author",
    "normative_specification", "normative_specification_sha256",
    "frozen_implementation_commit", "world_generator_version",
    "world_generator_sha256", "equipment_sha256",
    "parameter_registry_sha256", "ontology_sha256",
    "calibration_world_sha256", "holdout_world_sha256",
    "calibration_world_ids", "holdout_world_ids", "positive_world_ids",
    "negative_world_ids", "calibration_seeds", "holdout_seeds",
    "steps_per_run", "minimum_naturally_acquired_candidates",
    "maximum_superstitious_rule_rate", "minimum_known_cause_accuracy",
    "confidence_method", "candidate_definition", "ground_truth_definition",
    "independent_episode_definition", "exclusion_rule", "stop_rule",
    "replay_rule",
})


def normative_specification_digest() -> str:
    root = Path(__file__).resolve().parents[2]
    return sha256((root / SPEC_PATH).read_bytes()).hexdigest()


def _ids(rows: object, minimum: int = 1) -> set[str]:
    if (
        not isinstance(rows, list) or len(rows) < minimum
        or any(not isinstance(x, str) or not x.strip() for x in rows)
        or len(set(rows)) != len(rows)
    ):
        raise ValueError("world IDs must be unique nonempty strings")
    return set(rows)


def _world_hashes(value: object, names: set[str]) -> set[str]:
    """Require explicit immutable world physics+layout+scenario digests.

    This catches simple world relabelling; the independent bench must still
    inspect the underlying physical manifests and their real provenance.
    """
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError("physical world digests must cover exactly the world IDs")
    if any(
        not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
        for digest in value.values()
    ):
        raise ValueError("invalid physical world SHA-256 digest")
    values = set(value.values())
    if len(values) != len(value):
        raise ValueError("duplicate physical world under different identifiers")
    return values


def _seeds(rows: object, minimum: int = 1) -> set[int]:
    if (
        not isinstance(rows, list) or len(rows) < minimum
        or any(type(x) is not int or x < 0 for x in rows)
        or len(set(rows)) != len(rows)
    ):
        raise ValueError("seeds must be distinct nonnegative integers")
    return set(rows)


def _rate(value: object, name: str) -> None:
    if (
        type(value) not in (int, float)
        or not isfinite(value)
        or not 0 <= value <= 1
    ):
        raise ValueError(f"{name} must be a finite fraction in [0,1]")


def validate_registration(data: Mapping[str, object]) -> str:
    """Return a draft content hash; never claim prospective Git chronology."""
    if not isinstance(data, dict) or set(data) != REQUIRED_FIELDS:
        raise ValueError("registration requires exact mandatory fields")
    if data["protocol_version"] != REGISTRATION_VERSION:
        raise ValueError("registration schema mismatch")
    if data["normative_specification"] != SPEC_PATH:
        raise ValueError("English MVP v1.2.1 must be the normative reference")
    digest = data["normative_specification_sha256"]
    if (
        not isinstance(digest, str)
        or not SHA256_RE.fullmatch(digest)
        or digest != normative_specification_digest()
    ):
        raise ValueError("normative specification digest mismatch")
    commit = data["frozen_implementation_commit"]
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise ValueError("full immutable implementation commit required")
    for name in (
        "registration_id", "author", "world_generator_version",
        "confidence_method", "candidate_definition",
        "ground_truth_definition", "independent_episode_definition",
        "exclusion_rule", "stop_rule", "replay_rule",
    ):
        v = data[name]
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"registration field {name} must be nonempty")
    worlds = _ids(data["holdout_world_ids"], 2)
    calibration_worlds = _ids(data["calibration_world_ids"])
    positive = _ids(data["positive_world_ids"])
    negative = _ids(data["negative_world_ids"])
    if (
        worlds & calibration_worlds
        or positive & negative
        or positive | negative != worlds
    ):
        raise ValueError("holdout world/control groups must be disjoint")
    for name in (
        "world_generator_sha256", "equipment_sha256",
        "parameter_registry_sha256", "ontology_sha256",
    ):
        digest = data[name]
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ValueError(f"invalid frozen manifest digest: {name}")
    physical_calibration = _world_hashes(
        data["calibration_world_sha256"], calibration_worlds,
    )
    physical_holdout = _world_hashes(data["holdout_world_sha256"], worlds)
    if physical_calibration & physical_holdout:
        raise ValueError("holdout duplicates calibration physical world")
    if _seeds(data["holdout_seeds"], 2) & _seeds(data["calibration_seeds"]):
        raise ValueError("holdout and calibration seeds must be disjoint")
    for key in ("steps_per_run", "minimum_naturally_acquired_candidates"):
        val = data[key]
        if type(val) is not int or val < 1:
            raise ValueError(f"{key} must be a positive integer")
    for key in ("maximum_superstitious_rule_rate", "minimum_known_cause_accuracy"):
        _rate(data[key], key)
    return sha256_hex(canonical_causal_bytes(data))


def _unique_pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in items:
        if name in result:
            raise ValueError(f"duplicate registration JSON key: {name}")
        result[name] = value
    return result


def load_registration(path: Path) -> dict[str, object]:
    data = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs,
    )
    validate_registration(data)
    return data


def preflight(data: Mapping[str, object] | None = None) -> dict[str, object]:
    """Fail closed even if a user-supplied draft contains passing thresholds."""
    digest = None if data is None else validate_registration(data)
    return {
        "registration_status": (
            "unregistered" if data is None
            else "draft_requires_independent_git_seal"
        ),
        "registration_digest": digest,
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "author-approved thresholds and heldout design" if data is None
            else "independent prospective Git ancestry verification",
            "physically distinct holdout worlds and independent lived candidates",
            "external truth isolation, complete raw journals and exact replay",
            "preregistered rate/accuracy assessment and INV-25 review",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-9 registration preflight; never a Golden gate"
    )
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()
    data = load_registration(args.manifest) if args.manifest else None
    print(json.dumps(preflight(data), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
