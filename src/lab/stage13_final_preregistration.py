"""Stage-13 preregistration PREFLIGHT only: never launch a campaign.

MVP v1.3.1 §7 postpones definitive science until the complete project's
independent module-by-module campaign. This validator freezes the proposal
*before* any held-out life and refuses missing protocols or parameter values.
It cannot establish prospective Git chronology, scientific success, operator
acceptance, or independent world truth. No I0, Oracle or Bench constructed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path
import re
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex

SPEC_PATH = "docs/architecture/reference/en/mvp-specification-v1.3.1.md"
REGISTRATION_SCHEMA = "stage13-final-independent-preregistration-v1"
REQUIRED_PARAMETERS = frozenset(f"P-{i:02d}" for i in range(1, 59))
REQUIRED_STAGE_PROTOCOLS = frozenset(f"stage{i:02d}" for i in range(1, 13))
REQUIRED_HYPOTHESES = frozenset(f"H{i}" for i in range(1, 7))
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
ROOT_FIELDS = frozenset({
    "registration_schema", "registration_id", "normative_specification",
    "normative_specification_sha256", "implementation_commit",
    "parameter_values", "parameter_registry_sha256",
    "world_manifest_sha256", "equipment_manifest_sha256",
    "development_seeds", "calibration_seeds", "holdout_seeds",
    "calibration_world_ids", "holdout_world_ids",
    "module_protocols", "hypotheses", "familywise_error_control",
    "early_stop_rule", "exclusion_rule", "reporting_rule",
})
MODULE_FIELDS = frozenset({
    "module_id", "stage", "hypothesis", "independent_observation_source",
    "measurable_claim", "metric", "baseline", "negative_control",
    "minimum_independent_runs", "success_direction", "success_threshold",
    "failure_reporting",
})


def _string(value, name):
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be an explicit nonempty string")


def _digest(value, name):
    if type(value) is not str or not _HEX64.fullmatch(value):
        raise ValueError(f"{name} must be a complete lowercase SHA-256 digest")


def _distinct_strings(items, name):
    if (type(items) is not list or not items
            or any(type(x) is not str or not x.strip() for x in items)
            or len(items) != len(set(items))):
        raise ValueError(f"{name} must contain unique nonempty identifiers")
    return set(items)


def _seeds(items, name):
    if (type(items) is not list or not items
            or any(type(x) is not int or x < 0 for x in items)
            or len(items) != len(set(items))):
        raise ValueError(f"{name} must be nonempty unique nonnegative seeds")
    return set(items)


def normative_digest():
    path = Path(__file__).resolve().parents[2] / SPEC_PATH
    if path.is_symlink() or not path.is_file():
        raise ValueError("normative English specification unavailable or symlinked")
    return sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class Stage13DraftReceipt:
    schema: str
    digest: str
    module_protocol_count: int
    parameter_count: int
    stage_coverage: tuple[str, ...]
    operator_approval_required: bool = True
    scientific_verdict: None = None
    campaign_started: bool = False


def preregistration_preflight(plan: object) -> Stage13DraftReceipt:
    """Validate only a PROSPECTIVE DRAFT, never infer scientific verification.

    An operator must separately verify source ancestry, calibrations,
    independent held-out world hashes, and chronological registration before
    considering campaign launch. No run method exists in this module.
    """
    if type(plan) is not dict or set(plan) != ROOT_FIELDS:
        raise ValueError("Stage13 plan requires the exact preregistration fields")
    if plan["registration_schema"] != REGISTRATION_SCHEMA:
        raise ValueError("unsupported Stage13 preregistration schema")
    _string(plan["registration_id"], "registration_id")
    if plan["normative_specification"] != SPEC_PATH:
        raise ValueError("Stage13 registration must use normative EN v1.3.1")
    _digest(plan["normative_specification_sha256"], "normative_specification_sha256")
    if plan["normative_specification_sha256"] != normative_digest():
        raise ValueError("normative specification bytes changed before registration")
    if (type(plan["implementation_commit"]) is not str
            or not _HEX40.fullmatch(plan["implementation_commit"])):
        raise ValueError("immutable full implementation commit required")
    for field in (
        "parameter_registry_sha256", "world_manifest_sha256",
        "equipment_manifest_sha256",
    ):
        _digest(plan[field], field)
    for field in (
        "familywise_error_control", "early_stop_rule", "exclusion_rule",
        "reporting_rule",
    ):
        _string(plan[field], field)
    # Fixed before birth. No absent calibration parameter can silently fall
    # back to a convenient software default after seeing held-out evidence.
    params = plan["parameter_values"]
    if type(params) is not dict or set(params) != REQUIRED_PARAMETERS:
        raise ValueError("all 58 normative P-xx parameters must be frozen")
    for name, value in params.items():
        if (type(value) is not dict or set(value) != {"version", "value"}
                or type(value["version"]) is not str
                or not value["version"].strip()
                or value["value"] is None):
            raise ValueError(f"{name} needs an explicit version and nonnull value")
        canonical_causal_bytes(value)
    training = _seeds(plan["development_seeds"], "development_seeds")
    calibration = _seeds(plan["calibration_seeds"], "calibration_seeds")
    holdout = _seeds(plan["holdout_seeds"], "holdout_seeds")
    if training & calibration or training & holdout or calibration & holdout:
        raise ValueError("development, calibration and holdout seeds overlap")
    calibration_worlds = _distinct_strings(
        plan["calibration_world_ids"], "calibration_world_ids",
    )
    holdout_worlds = _distinct_strings(
        plan["holdout_world_ids"], "holdout_world_ids",
    )
    if calibration_worlds & holdout_worlds:
        raise ValueError("calibration world reused as holdout")
    hypotheses = plan["hypotheses"]
    if type(hypotheses) is not dict or set(hypotheses) != REQUIRED_HYPOTHESES:
        raise ValueError("all H1-H6 hypotheses must be prospectively specified")
    for identifier, claim in hypotheses.items():
        _string(claim, f"hypothesis {identifier}")
    modules = plan["module_protocols"]
    if type(modules) is not list or len(modules) < 12:
        raise ValueError("final evidence needs individually registered module protocols")
    ids: set[str] = set()
    covered: set[str] = set()
    for protocol in modules:
        if type(protocol) is not dict or set(protocol) != MODULE_FIELDS:
            raise ValueError("module protocol is missing its independent validation fields")
        ident, stage = protocol["module_id"], protocol["stage"]
        _string(ident, "module_id")
        if ident in ids or stage not in REQUIRED_STAGE_PROTOCOLS:
            raise ValueError("module protocols need unique identities and valid stages")
        ids.add(ident)
        covered.add(stage)
        if protocol["hypothesis"] not in REQUIRED_HYPOTHESES:
            raise ValueError("module must declare a preregistered hypothesis")
        for field in (
            "independent_observation_source", "measurable_claim", "metric",
            "baseline", "negative_control", "failure_reporting",
        ):
            _string(protocol[field], field)
        if protocol["independent_observation_source"] in {
            "I0_private_inference", "Oracle_as_I0_input",
        }:
            raise ValueError("independent verification cannot come from I0's private guess")
        if (type(protocol["minimum_independent_runs"]) is not int
                or protocol["minimum_independent_runs"] < 1):
            raise ValueError("minimum independent run count must be declared")
        if protocol["success_direction"] not in {"at_least", "at_most"}:
            raise ValueError("unknown success direction")
        threshold = protocol["success_threshold"]
        if type(threshold) not in (int, float) or not isfinite(threshold):
            raise ValueError("scientific acceptance threshold must be explicit and finite")
    if covered != REQUIRED_STAGE_PROTOCOLS:
        raise ValueError("every Stage 1-12 needs an independent component evidence plan")
    digest = sha256_hex(canonical_causal_bytes(plan))
    return Stage13DraftReceipt(
        schema=REGISTRATION_SCHEMA, digest=digest,
        module_protocol_count=len(modules), parameter_count=len(params),
        stage_coverage=tuple(sorted(covered)),
    )
