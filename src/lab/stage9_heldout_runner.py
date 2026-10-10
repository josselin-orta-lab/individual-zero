"""Independent-operator Stage-9 held-out executor and evidence packager.

This runs the real Stage9Runtime on prospectively registered worlds and seeds.
It NEVER generates scientific ground-truth labels, approves GO, self-certifies
independence, claims INV-25 or freezes a Golden. All hidden inputs and output
artefacts belong in a separately controlled operator checkout.

EN normative MVP v1.2.1 sections 9.6, 13.2, 19.5, 20.3; INV-25/33/44/53.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping as MappingABC
from dataclasses import asdict, fields, is_dataclass
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints, Union

from i0.equipment import EquipmentArtifact, ExactTransitionRecord, FrozenTableEquipment
from i0.modules.action_control import StaticSafetyFacts
from i0.modules.stage6_evaluator import Stage6EvaluationConfig
from i0.modules.stage6_planning import Stage6PlanningConfig
from i0.modules.simulator import SimulatorConfig
from i0.equipment import SimulationState, PredictedEffect
from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import ScenarioEvent
from .safety_protocol import SafetyProtocolConfig
from .stage9_frozen_worktree import verify_frozen_worktree
from .stage9_heldout_artifact_custody import audit_heldout_raw_artifacts
from .stage9_memory_custody import audit_archived_closed_memory_sources
from .stage9_canonical_journal_audit import audit_raw_causal_journal
from .stage9_registered_manifest_custody import (
    _file_without_aliases, _root_without_aliases,
    audit_registered_manifest_files, load_manifest_index,
)
from .stage9_registration_chronology import (
    _check_commit, _file_in_repo, _git, _require_ancestor,
    _verify_frozen_source_tree, _verify_frozen_normative_specification,
    reject_git_repository_overrides,
)
from .stage9_runtime import Stage9Config, Stage9Runtime
from .stage9_scientific_assessment import assess_heldout_campaign
from .stage9_scientific_preregistration import (
    _unique_pairs, _reject_nonfinite_registration_constant,
    load_registration, validate_registration,
)
from .stage9_secure_file_read import read_text_no_follow, open_regular_no_follow
from .world import (
    WorldPhysicsConfig, WorldLayout, Position,
)
from .world_generation import (
    WorldGenerationConfig, generate_world, apply_generated_berry_effects,
)

RUN_VERSION = "stage9-heldout-operator-run-index-v1"
PARAMETER_VERSION = "stage9-heldout-parameters-v1"
EQUIPMENT_VERSION = "stage9-heldout-equipment-v1"
GENERATOR_VERSION = "stage9-heldout-world-generator-v1"
WORLD_VERSION = "stage9-heldout-physical-world-v1"
ANNOTATIONS_VERSION = "stage9-heldout-independent-annotations-v1"
RELEASE_VERSION = "stage9-heldout-operator-release-record-v1"
RAW_INDEX_VERSION = "stage9-heldout-raw-artifact-index-v4"
EVIDENCE_VERSION = "stage9-heldout-evidence-v2"


def _json_bytes(source: bytes) -> dict[str, object]:
    """Interpret precisely the already hashed input byte image."""
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for name, value in items:
            if name in out:
                raise ValueError("duplicate Stage-9 operator JSON key")
            out[name] = value
        return out

    def reject(value: str) -> None:
        raise ValueError("nonfinite Stage-9 operator JSON constant: " + value)

    document = json.loads(
        source.decode("utf-8"),
        object_pairs_hook=pairs, parse_constant=reject,
    )
    if not isinstance(document, dict):
        raise ValueError("Stage-9 operator input must be a JSON object")
    canonical_causal_bytes(document)  # Also rejects overflowing numeric JSON.
    return document


def _json_file(path: Path) -> dict[str, object]:
    """Strict input through a no-follow guarded descriptor."""
    return _json_bytes(read_text_no_follow(path).encode("utf-8"))


def _exact(obj: object, names: set[str], role: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != names:
        raise ValueError(role + " fields are missing or unexpected")
    return obj


def _typed(typ: object, value: object) -> object:
    """Decode registered dataclass parameters without eval or arbitrary imports."""
    origin = get_origin(typ)
    args = get_args(typ)
    if typ is Any or typ is object:
        canonical_causal_bytes(value)
        return value
    if typ is str:
        if not isinstance(value, str):
            raise ValueError("expected parameter string")
        return value
    if typ is bool:
        if type(value) is not bool:
            raise ValueError("expected parameter boolean")
        return value
    if typ is int:
        if type(value) is not int:
            raise ValueError("expected parameter integer")
        return value
    if typ is float:
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("expected finite parameter number")
        return float(value)
    if origin in (Union, UnionType):
        for candidate in args:
            if candidate is type(None) and value is None:
                return None
            try:
                return _typed(candidate, value)
            except (TypeError, ValueError):
                pass
        raise ValueError("parameter union has no valid alternative")
    if isinstance(typ, type) and is_dataclass(typ):
        valid = {field.name for field in fields(typ)}
        item = _exact(value, valid, typ.__name__)
        hints = get_type_hints(typ)
        decoded = {
            name: _typed(hints[name], item[name])
            for name in valid
        }
        result = typ(**decoded)
        if callable(getattr(result, "validate", None)):
            result.validate()
        return result
    if origin in (dict, MappingABC):
        if not isinstance(value, dict):
            raise ValueError("expected parameter mapping")
        key_t, val_t = args
        return {
            _typed(key_t, key): _typed(val_t, item)
            for key, item in value.items()
        }
    if origin in (tuple, list):
        if not isinstance(value, list):
            raise ValueError("expected parameter array")
        if len(args) == 2 and args[1] is Ellipsis:
            result = [_typed(args[0], part) for part in value]
        else:
            if len(value) != len(args):
                raise ValueError("wrong tuple parameter arity")
            result = [_typed(t, part) for t, part in zip(args, value)]
        return tuple(result) if origin is tuple else result
    if origin is frozenset:
        if not isinstance(value, list):
            raise ValueError("expected parameter set array")
        members = [_typed(args[0], item) for item in value]
        if len(set(members)) != len(members):
            raise ValueError("duplicate parameter set member")
        return frozenset(members)
    raise ValueError("unsupported frozen parameter type: " + str(typ))


def _world_layout(data: object) -> WorldLayout:
    item = _exact(data, {
        "obstacles", "water_sources", "resources", "creatures",
        "danger_zones", "lethal_zones", "oracle_canary",
    }, "WorldLayout")
    if item["oracle_canary"]:
        raise ValueError("operator world cannot inject an oracle canary into cognition")
    def positions(name: str) -> frozenset[Position]:
        if not isinstance(item[name], list):
            raise ValueError("invalid world position array")
        result = [_typed(Position, position) for position in item[name]]
        if len(set(result)) != len(result):
            raise ValueError("duplicate world position")
        return frozenset(result)

    if not isinstance(item["resources"], list):
        raise ValueError("invalid world resources")
    resources = []
    for resource in item["resources"]:
        row = _exact(resource, {"position", "kind", "quantity"}, "resource")
        resources.append((
            _typed(Position, row["position"]),
            _typed(str, row["kind"]),
            _typed(int, row["quantity"]),
        ))
    return WorldLayout(
        obstacles=positions("obstacles"),
        water_sources=positions("water_sources"),
        resources=tuple(resources),
        creatures=positions("creatures"),
        danger_zones=positions("danger_zones"),
        lethal_zones=positions("lethal_zones"),
        oracle_canary="",
    )


def _json_safe(value: object) -> object:
    """Explicit exporter for already calibrated/frozen config value objects."""
    if is_dataclass(value):
        return {field.name: _json_safe(getattr(value, field.name))
                for field in fields(value)}
    if isinstance(value, MappingABC):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [_json_safe(item) for item in sorted(value)]
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    canonical_causal_bytes(value)
    return value


def export_frozen_stage9_assets(
    runtime: Stage9Runtime,
) -> tuple[dict[str, object], dict[str, object]]:
    """Serialize an *operator-selected* trained Stage-9 runtime for custody.

    This does NOT calibrate, approve or freeze scientific parameters. The
    research owner must provide an independently calibrated runtime, and
    independently inspect both outputs before preregistering their bytes.
    Reference fixtures are software examples, not scientific calibration.
    """
    if not isinstance(runtime, Stage9Runtime):
        raise ValueError("only a Stage-9 cognitive runtime can be exported")
    if not isinstance(runtime.equipment, FrozenTableEquipment):
        raise ValueError("only the frozen exact-transition Equipment model is supported")
    innate = runtime.stage3.control._facts._innate
    if not isinstance(innate, StaticSafetyFacts):
        raise ValueError("cannot attest a nonstandard innate safety policy")
    parameters = {
        "protocol_version": PARAMETER_VERSION,
        "stage9_config": _json_safe(runtime._stage9_config),
        "safety_config": _json_safe(runtime.stage3.substrate.safety._config),
        "protected_integrity_threshold":
            runtime.stage3.control._config.protected_integrity_threshold,
        "innate_safety_facts": _json_safe(innate),
    }
    equipment = {
        "protocol_version": EQUIPMENT_VERSION,
        "artifact": _json_safe(runtime.equipment._artifact),
        "records": [
            _json_safe(row)
            for _, row in sorted(runtime.equipment._records.items())
        ],
    }
    # Round-trip the exact exported content; no runtime recalibration.
    _frozen_parameters(parameters)
    decoded = _frozen_equipment(equipment)
    if decoded.artifact_digest != runtime.equipment.artifact_digest:
        raise ValueError("frozen equipment export changed its provenance digest")
    return parameters, equipment


def _frozen_parameters(document: dict) -> tuple[Stage9Config, SafetyProtocolConfig, float, StaticSafetyFacts]:
    raw = _exact(document, {
        "protocol_version", "stage9_config", "safety_config",
        "protected_integrity_threshold", "innate_safety_facts",
    }, "parameter manifest")
    if raw["protocol_version"] != PARAMETER_VERSION:
        raise ValueError("parameter schema version mismatch")
    stage9 = _typed(Stage9Config, raw["stage9_config"])
    safety = _typed(SafetyProtocolConfig, raw["safety_config"])
    if safety.mode != "campaign":
        raise ValueError("held-out safety must use campaign mode")
    threshold = _typed(float, raw["protected_integrity_threshold"])
    if not 0 < threshold < 100:
        raise ValueError("invalid protected integrity threshold")
    facts = _typed(StaticSafetyFacts, raw["innate_safety_facts"])
    return stage9, safety, threshold, facts


def _frozen_equipment(document: dict) -> FrozenTableEquipment:
    data = _exact(document, {"protocol_version", "artifact", "records"}, "equipment")
    if data["protocol_version"] != EQUIPMENT_VERSION:
        raise ValueError("equipment schema version mismatch")
    artifact = _typed(EquipmentArtifact, data["artifact"])
    if not isinstance(data["records"], list):
        raise ValueError("equipment records must be a list")
    rows: dict[str, ExactTransitionRecord] = {}
    for raw in data["records"]:
        record = _typed(ExactTransitionRecord, raw)
        digest = record.input_sha256
        if len(digest) != 64 or any(x not in "0123456789abcdef" for x in digest):
            raise ValueError("invalid equipment input digest")
        if digest in rows:
            raise ValueError("duplicate frozen equipment input")
        record.next_state.validate()
        for effect in record.effects:
            effect.validate()
        rows[digest] = record
    model = artifact.model_payload
    if (
        model.get("record_count") != len(rows)
        or model.get("input_hashes") != sorted(rows)
    ):
        raise ValueError("frozen equipment differs from trained artifact index")
    return FrozenTableEquipment(artifact=artifact, records=rows)


def _scenario(data: object, steps: int) -> tuple[str, str, tuple[ScenarioEvent, ...]]:
    item = _exact(data, {"id", "version", "events"}, "world scenario")
    scenario_id, version = item["id"], item["version"]
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ValueError("scenario id missing")
    if not isinstance(version, str) or not version:
        raise ValueError("scenario version missing")
    if not isinstance(item["events"], list):
        raise ValueError("scenario events must be a list")
    events = tuple(_typed(ScenarioEvent, event) for event in item["events"])
    if any(
        type(event.t_monde) is not int or not 1 <= event.t_monde <= steps
        or type(event.sequence) is not int or event.sequence < 0
        or event.operation not in {
            "set_danger_zone", "set_lethal_zone", "place_creature",
            "remove_creature", "place_resource", "set_body",
        }
        for event in events
    ):
        raise ValueError("invalid or out-of-range registered scenario event")
    keys = [(event.t_monde, event.sequence) for event in events]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate scenario schedule entry")
    return scenario_id, version, events


def _world(document: dict, *, world_id: str, steps: int):
    raw = _exact(document, {
        "protocol_version", "world_id", "physics", "scenario",
    }, "physical world manifest")
    if raw["protocol_version"] != WORLD_VERSION or raw["world_id"] != world_id:
        raise ValueError("world manifest does not identify its registered world")
    physics = _typed(WorldPhysicsConfig, raw["physics"])
    scenario = _scenario(raw["scenario"], steps)
    return physics, scenario


def _write_new(path: Path, content: bytes) -> None:
    """Never overwrite or reassign an experimental path, even after failure."""
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("output path contains a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)


def _file_sha(path: Path) -> str:
    with open_regular_no_follow(path) as stream:
        return sha256_hex(stream.read())


def _external_release(release: dict, registration: dict, registration_commit: str) -> None:
    item = _exact(release, {
        "protocol_version", "registration_digest", "frozen_implementation_commit",
        "registration_commit", "authorization", "research_owner",
        "custodian", "operator", "independent_evaluator",
        "approval_evidence_ref", "independent_timestamp_ref",
    }, "external release record")
    if (
        item["protocol_version"] != RELEASE_VERSION
        or item["authorization"] != "GO"
        or item["registration_digest"] != validate_registration(registration)
        or item["frozen_implementation_commit"]
            != registration["frozen_implementation_commit"]
        or item["registration_commit"] != registration_commit
        or any(
            not isinstance(item[key], str) or not item[key].strip()
            for key in (
                "research_owner", "custodian", "operator",
                "independent_evaluator", "approval_evidence_ref",
                "independent_timestamp_ref",
            )
        )
    ):
        raise ValueError("absent, incomplete or conflicting human GO record")
    # These are self-reported references, not cryptographically verified
    # signatures. The independent reviewer must inspect the originals.


def _check_preregistration(
    *, repository: Path, registration_path: Path, registration_commit: str,
    registration: dict,
) -> dict:
    reject_git_repository_overrides()
    root = repository.resolve()
    if _git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise ValueError("operator seal requires complete unshallowed Git history")
    _check_commit(root, registration_commit)
    freeze = registration["frozen_implementation_commit"]
    _check_commit(root, freeze)
    _require_ancestor(root, freeze, registration_commit)
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    if head != registration_commit:
        # A preregistration commit is the entire initial operator checkout:
        # later source commits, even reverted ones, must not be executable.
        raise ValueError("execution checkout must be at preregistration commit")
    physical, name = _file_in_repo(root, registration_path)
    with open_regular_no_follow(physical) as stream:
        original = stream.read()
    sealed = _git(root, "show", registration_commit + ":" + name)
    if sealed != original:
        raise ValueError("preregistration bytes differ from Git-sealed original")
    # Bind the earlier parsed registration object to exactly the immutable
    # Git bytes, not an independently replaceable physical parse result.
    committed = json.loads(
        sealed.decode("utf-8"), object_pairs_hook=_unique_pairs,
        parse_constant=_reject_nonfinite_registration_constant,
    )
    if canonical_causal_bytes(committed) != canonical_causal_bytes(registration):
        raise ValueError("operator registration parse differs from sealed Git bytes")
    frozen_tree, frozen_package, source_commits = _verify_frozen_source_tree(
        root, freeze, registration_commit,
    )
    frozen_spec, specification_commits = _verify_frozen_normative_specification(
        root, freeze, registration_commit,
        registration["normative_specification_sha256"],
    )
    checked = verify_frozen_worktree(
        repository=root, frozen_implementation_commit=freeze,
    )
    if (
        checked["source_tree_sha"] != frozen_tree
        or checked["pyproject_blob_sha"] != frozen_package
        or checked["normative_specification_blob_sha"] != frozen_spec
    ):
        raise ValueError("operator source checkout and ancestry disagree")
    return {
        **checked,
        "source_ancestry_commits_verified": source_commits,
        "normative_specification_ancestry_commits_verified": specification_commits,
    }


def _cell_run(
    *, world_id: str, seed: int, steps: int,
    physics: WorldPhysicsConfig, generator: WorldGenerationConfig,
    scenario: tuple[str, str, tuple[ScenarioEvent, ...]],
    config: Stage9Config, safety: SafetyProtocolConfig, threshold: float,
    innate: StaticSafetyFacts, equipment: FrozenTableEquipment,
) -> tuple[bytes, bytes, bytes, bytes, dict]:
    # Each seed procedurally changes *real* world layout and berry identity.
    # All oracle-relevant choices remain on the bench side.
    generated = generate_world(physics=physics, generation=generator, seed=seed)
    runtime_physics = apply_generated_berry_effects(
        physics=physics, generation=generator, generated=generated,
    )
    layout = generated.layout
    layout.validate(runtime_physics)
    def build() -> Stage9Runtime:
        return Stage9Runtime(
            world_config=runtime_physics, layout=layout,
            safety_config=safety, safety_facts=innate,
            protected_integrity_threshold=threshold,
            config=config, equipment=equipment,
            scenario_id=scenario[0], scenario_version=scenario[1],
            scenario_events=scenario[2],
        )

    def execute() -> tuple[bytes, bytes, dict]:
        individual = build()
        before_truth = individual.world.ground_truth()
        for step in range(steps):
            outcome = individual.run_step()
            if outcome.execution_status != "applied":
                raise ValueError(
                    "registered cell did not complete every applied physical step "
                    + str(step + 1) + "/" + str(steps)
                )
        if not individual.journal.verify():
            raise ValueError("held-out execution journal hash chain failed")
        owners = {owner.owner_id: owner.export_causal_state()
                  for owner in individual.causal_owners}
        if len(owners) != len(individual.causal_owners):
            raise ValueError("duplicate held-out canonical causal owner")
        return (
            individual.journal.canonical_bytes(),
            canonical_causal_bytes(owners),
            {"before_world_truth": before_truth,
             "after_world_truth": individual.world.ground_truth()},
        )

    original_journal, original_state, truth = execute()
    replay_journal, replay_state, _ = execute()
    if original_journal != replay_journal or original_state != replay_state:
        raise ValueError("held-out cell does not replay byte-identically")
    truth["world_id"] = world_id
    truth["seed"] = seed
    truth["realized_world_physics"] = runtime_physics.as_dict()
    truth["realized_world_layout"] = layout.as_dict()
    truth["scenario_id"] = scenario[0]
    truth["scenario_version"] = scenario[1]
    truth["generated_toxic_berry_bench_only"] = generated.toxic_berry
    truth["generated_nutritious_berry_bench_only"] = generated.nutritious_berry
    return original_journal, original_state, replay_journal, replay_state, truth


def execute_campaign(
    *, repository: Path, registration_path: Path, registration_commit: str,
    manifest_index_path: Path, manifest_root: Path, release_path: Path,
    output_root: Path,
) -> dict:
    """Execute only after all local guards and an external reported GO.

    This does not authenticate the approval or prove human independence.
    """
    registration = load_registration(registration_path)
    digest = validate_registration(registration)
    source_receipt = _check_preregistration(
        repository=repository, registration_path=registration_path,
        registration_commit=registration_commit, registration=registration,
    )
    _external_release(
        _json_file(release_path), registration, registration_commit,
    )
    index = load_manifest_index(manifest_index_path)
    custody = audit_registered_manifest_files(
        registration=registration, index=index, artifact_root=manifest_root,
    )
    if custody["registration_digest"] != digest:
        raise ValueError("manifest custody disagrees with sealed registration")
    root = _root_without_aliases(manifest_root)
    def manifest(path: str, expected_digest: str) -> dict:
        physical = _file_without_aliases(root, path)
        with open_regular_no_follow(physical) as stream:
            raw = stream.read()
        if sha256_hex(raw) != expected_digest:
            raise ValueError("operator-decoded manifest differs from registered original bytes")
        return _json_bytes(raw)

    frozen = index["frozen_manifests"]
    parameter = _frozen_parameters(manifest(
        frozen["parameter_registry"], registration["parameter_registry_sha256"],
    ))
    equipment = _frozen_equipment(manifest(
        frozen["equipment"], registration["equipment_sha256"],
    ))
    generator_doc = _exact(
        manifest(frozen["world_generator"], registration["world_generator_sha256"]),
        {"protocol_version", "generation"}, "world generator manifest",
    )
    if generator_doc["protocol_version"] != GENERATOR_VERSION:
        raise ValueError("world generator manifest version mismatch")
    generator = _typed(WorldGenerationConfig, generator_doc["generation"])
    if generator.version != registration["world_generator_version"]:
        raise ValueError("world generator version differs from preregistration")
    # The ontology file is registered/custodied. Its semantics are frozen by
    # code and must be separately checked by the independent reviewer.
    ontology = manifest(frozen["ontology"], registration["ontology_sha256"])
    if ontology.get("protocol_version") != "stage9-heldout-ontology-v1":
        raise ValueError("unrecognized frozen ontology manifest")
    if output_root.exists():
        raise ValueError("operator output directory already exists; no overwrite")
    if any(part.is_symlink() for part in (output_root.absolute(), *output_root.absolute().parents)):
        raise ValueError("operator output root must not traverse symlinks")

    worlds = {}
    for world_id in registration["holdout_world_ids"]:
        worlds[world_id] = _world(
            manifest(
                index["holdout_worlds"][world_id],
                registration["holdout_world_sha256"][world_id],
            ),
            world_id=world_id, steps=registration["steps_per_run"],
        )
    # No selected subset: execute the entire registered Cartesian product.
    rows = []
    for world_number, world_id in enumerate(registration["holdout_world_ids"]):
        physics, scenario = worlds[world_id]
        for seed_number, seed in enumerate(registration["holdout_seeds"]):
            cell = f"cell-{world_number:03d}-{seed_number:03d}"
            journal, state, replay_journal, replay_state, bench_truth = _cell_run(
                world_id=world_id, seed=seed,
                steps=registration["steps_per_run"], physics=physics,
                generator=generator, scenario=scenario,
                config=parameter[0], safety=parameter[1],
                threshold=parameter[2], innate=parameter[3],
                equipment=equipment,
            )
            files = {
                "journal_path": cell + "/journal.jsonl",
                "replay_journal_path": cell + "/replay-journal.jsonl",
                "causal_state_path": cell + "/causal-state.json",
                "replay_causal_state_path": cell + "/replay-causal-state.json",
            }
            for field, content in (
                ("journal_path", journal),
                ("replay_journal_path", replay_journal),
                ("causal_state_path", state),
                ("replay_causal_state_path", replay_state),
            ):
                _write_new(output_root / files[field], content)
            _write_new(
                output_root / cell / "bench-only-world-truth.json",
                canonical_causal_bytes(bench_truth),
            )
            rows.append({
                "world_id": world_id, "seed": seed,
                "world_sha256": registration["holdout_world_sha256"][world_id],
                **files,
                "journal_sha256": sha256_hex(journal),
                "causal_state_sha256": sha256_hex(state),
                "bench_truth_sha256": sha256_hex(canonical_causal_bytes(bench_truth)),
            })
    result = {
        "protocol_version": RUN_VERSION,
        "registration_digest": digest,
        "frozen_implementation_commit": registration["frozen_implementation_commit"],
        "registration_commit": registration_commit,
        "runs": rows,
        "local_preflight": source_receipt,
        "manifest_custody": custody["manifest_custody_status"],
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "external_independence_attested_by_runner": False,
    }
    _write_new(output_root / "operator-run-index.json",
               json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return {
        "status": "operator_execution_archived_requires_external_annotation",
        "run_count": len(rows), "registration_digest": digest,
        "scientific_verdict": None, "golden_stage9_frozen": False,
        "external_approval_authenticated": False,
        "independent_execution_attested": False,
    }


def package_evidence(
    *, registration_path: Path, runs_root: Path, annotations_path: Path,
    evidence_path: Path, raw_index_path: Path,
) -> dict:
    """Join separately sourced bench annotations to actual archived attempts.

    Labels are supplied by the independent bench. No annotation, no credited
    evidence. This is a retrospective machine envelope, not a verdict.
    """
    registration = load_registration(registration_path)
    digest = validate_registration(registration)
    archive = _json_file(runs_root / "operator-run-index.json")
    if (
        archive.get("protocol_version") != RUN_VERSION
        or archive.get("registration_digest") != digest
        or archive.get("frozen_implementation_commit")
            != registration["frozen_implementation_commit"]
        or not isinstance(archive.get("runs"), list)
    ):
        raise ValueError("operator archive differs from registered experiment")
    annotation = _exact(
        _json_file(annotations_path),
        {"protocol_version", "registration_digest", "runs"},
        "bench annotations",
    )
    if (
        annotation["protocol_version"] != ANNOTATIONS_VERSION
        or annotation["registration_digest"] != digest
        or not isinstance(annotation["runs"], list)
    ):
        raise ValueError("bench annotation schema or digest mismatch")
    lookup = {}
    for row in annotation["runs"]:
        row = _exact(
            row, {"world_id", "seed", "known_cause_cases",
                  "naturally_acquired_false_candidates"},
            "bench annotation run",
        )
        key = (row["world_id"], row["seed"])
        if key in lookup:
            raise ValueError("duplicate bench annotation cell")
        lookup[key] = row
    wanted = {(w, s) for w in registration["holdout_world_ids"]
              for s in registration["holdout_seeds"]}
    if set(lookup) != wanted:
        raise ValueError("bench annotations omit or add preregistered cells")
    archive_lookup = {}
    for row in archive["runs"]:
        key = (row["world_id"], row["seed"])
        if key in archive_lookup:
            raise ValueError("duplicate operator execution cell")
        archive_lookup[key] = row
    if set(archive_lookup) != wanted:
        raise ValueError("operator archive coverage is not complete")

    evidence_runs, raw_rows = [], []
    for world_id, seed in sorted(wanted):
        operator = archive_lookup[world_id, seed]
        source = lookup[world_id, seed]
        refs = {}
        for name, suffix in (
            ("journal_path", "journal_sha256"),
            ("replay_journal_path", "journal_sha256"),
            ("causal_state_path", "causal_state_sha256"),
            ("replay_causal_state_path", "causal_state_sha256"),
        ):
            path = _file_without_aliases(
                _root_without_aliases(runs_root), operator[name],
            )
            if _file_sha(path) != operator[suffix]:
                raise ValueError("operator raw artifact changed after execution")
            refs[name] = operator[name]
        journal_path = runs_root / refs["journal_path"]
        state_path = runs_root / refs["causal_state_path"]
        claims = [
            *source["known_cause_cases"],
            *source["naturally_acquired_false_candidates"],
        ]
        physical_refs = {entry["observation_ref"] for entry in claims}
        audit = audit_raw_causal_journal(
            journal_path, physical_observation_refs=physical_refs,
        )
        episodes = {entry["observation_ref"]: entry["episode_ref"]
                    for entry in claims}
        if len(episodes) != len(claims):
            raise ValueError("bench annotations reuse a physical observation")
        audit_archived_closed_memory_sources(
            state_path, claimed_episodes=episodes,
            physical_source_provenance=audit["physical_source_provenance"],
        )
        evidence_runs.append({
            "world_id": world_id, "seed": seed,
            "world_sha256": registration["holdout_world_sha256"][world_id],
            "journal_sha256": operator["journal_sha256"],
            "replay_journal_sha256": operator["journal_sha256"],
            "causal_state_sha256": operator["causal_state_sha256"],
            "replay_causal_state_sha256": operator["causal_state_sha256"],
            "known_cause_cases": source["known_cause_cases"],
            "naturally_acquired_false_candidates": source[
                "naturally_acquired_false_candidates"
            ],
        })
        raw_rows.append({"world_id": world_id, "seed": seed, **refs})

    payload = {
        "protocol_version": EVIDENCE_VERSION,
        "registration_digest": digest,
        "frozen_implementation_commit": registration["frozen_implementation_commit"],
        "runs": evidence_runs,
    }
    evidence = {
        **payload, "evidence_sha256": sha256_hex(canonical_causal_bytes(payload)),
    }
    metrics = assess_heldout_campaign(registration, evidence)
    raw_index = {
        "protocol_version": RAW_INDEX_VERSION,
        "registration_digest": digest,
        "evidence_sha256": evidence["evidence_sha256"],
        "runs": raw_rows,
    }
    audit_heldout_raw_artifacts(
        registration=registration, evidence=evidence,
        index=raw_index, artifact_root=runs_root,
    )
    if evidence_path.exists() or raw_index_path.exists():
        raise ValueError("evidence or custody-index path exists; no overwrite")
    _write_new(evidence_path, json.dumps(
        evidence, sort_keys=True, indent=2,
    ).encode("utf-8") + b"\n")
    _write_new(raw_index_path, json.dumps(
        raw_index, sort_keys=True, indent=2,
    ).encode("utf-8") + b"\n")
    return {
        "status": "provisional_evidence_packaged_requires_independent_review",
        "assessment": metrics["assessment"],
        "registration_digest": digest,
        "evidence_sha256": evidence["evidence_sha256"],
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-9 isolated held-out operator: never a Golden"
    )
    sub = parser.add_subparsers(dest="operation", required=True)
    run = sub.add_parser("run", help="Execute all sealed world/seed cells")
    run.add_argument("--repo", type=Path, default=Path("."))
    run.add_argument("--registration", type=Path, required=True)
    run.add_argument("--registration-commit", required=True)
    run.add_argument("--manifest-index", type=Path, required=True)
    run.add_argument("--manifest-root", type=Path, required=True)
    run.add_argument("--external-go-record", type=Path, required=True)
    run.add_argument("--output-root", type=Path, required=True)
    seal = sub.add_parser("package", help="Build evidence from independent bench labels")
    seal.add_argument("--registration", type=Path, required=True)
    seal.add_argument("--runs-root", type=Path, required=True)
    seal.add_argument("--annotations", type=Path, required=True)
    seal.add_argument("--evidence", type=Path, required=True)
    seal.add_argument("--raw-index", type=Path, required=True)
    args = parser.parse_args()
    if args.operation == "run":
        report = execute_campaign(
            repository=args.repo, registration_path=args.registration,
            registration_commit=args.registration_commit,
            manifest_index_path=args.manifest_index,
            manifest_root=args.manifest_root,
            release_path=args.external_go_record, output_root=args.output_root,
        )
    else:
        report = package_evidence(
            registration_path=args.registration,
            runs_root=args.runs_root,
            annotations_path=args.annotations,
            evidence_path=args.evidence, raw_index_path=args.raw_index,
        )
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
