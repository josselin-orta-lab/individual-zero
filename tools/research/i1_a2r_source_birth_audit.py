"""A2-R source -> pristine birth -> M11 cold owner chain.

Research-only, never launches a confirmatory study. Requires an OUTSIDE
source/tree/preset SHA anchor. A fresh ZERO-STEP technical reference is rebuilt
from the checked-out, independently hashed engine, not from the life report.

This is a *source configuration parity* observation. It cannot attest that
an arbitrary external runner executed the pinned source without a separate
run-identity attestation, nor turn a short technical life into an L3 result.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

from i1_a2r_archive_guard import (
    _identity, SHA40, SHA64, MODES, ROLES, SEEDS,
)

_REQUIRED_SOURCE = (
    "scripts/build_i1_fork.py",
    "src/i1/runtime/m11_transactional_mortal.py",
    "src/i1/runtime/i1_natural_runtime.py",
    "src/i1/runtime/i1_birth_temperament.py",
    "src/i1/runtime/i1_natural_sleep.py",
    "src/i1/runtime/i1_active_value_needs.py",
    "src/i1/lab/matched_temperament_research.py",
    "src/i1/modules/value_needs.py",
    "tools/i1_eco_a1_worlds.py",
    "tools/i1_eco_a2r_birth.py",
    "tools/run_i1_world_preset.py",
    "src/i1/lab/world_presets/oasis.json",
)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(root: Path, *args: str) -> str:
    try:
        run = subprocess.run(
            ["git", "-C", str(root), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=15)
    except (OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        raise ValueError("A2-R git source could not be verified") from exc
    return run.stdout.strip()


def verify_source_checkout(*, root, expected_commit, expected_tree,
                           expected_preset):
    """Verify an EXTERNALLY pinned, unmodified Git source and exact oasis bytes.

    A hash copied from this same workspace is NOT independent attestation.
    A later A2-R runner must obtain commit/tree/preset from the frozen lock,
    and independently bind the GitHub run's actual head SHA and attempt=1.
    """
    if (type(expected_commit) is not str or not SHA40.fullmatch(expected_commit)
            or type(expected_tree) is not str
            or not SHA40.fullmatch(expected_tree)
            or type(expected_preset) is not str
            or not SHA64.fullmatch(expected_preset)):
        raise ValueError("A2-R source lock requires exact lowercase SHA fields")
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("A2-R source tree must be an absolute real directory")
    if _git(root, "rev-parse", "--show-toplevel") != str(root.resolve()):
        raise ValueError("A2-R source path is not checkout root")
    if (_git(root, "rev-parse", "HEAD") != expected_commit or
            _git(root, "rev-parse", "HEAD^{tree}") != expected_tree):
        raise ValueError("source HEAD or tree differs from external origin lock")
    # Both staged and unstaged tracked changes are forbidden; also untracked
    # source/experiment modules. An ignored __pycache__ is not causal source.
    for path in _REQUIRED_SOURCE:
        file = root / path
        if (not file.is_file() or file.is_symlink()
                or file.resolve().is_relative_to((root / ".git").resolve())):
            raise ValueError("source module/preset missing or not a regular file")
        if not _git(root, "ls-files", "--error-unmatch", "--", path):
            raise ValueError("A2-R source not tracked: " + path)
    if _git(root, "status", "--porcelain", "--untracked-files=all", "--",
            "src/i1", "src/i0", "tools", "scripts", "pyproject.toml",
            ".github/workflows"):
        raise ValueError("A2-R engine/research checkout contains dirty source")
    preset = root / "src/i1/lab/world_presets/oasis.json"
    if _digest(preset.read_bytes()) != expected_preset:
        raise ValueError("oasis preset differs from externally pinned bytes")
    # Git tree verifies all tracked bytes; validate critical module bytes a
    # second time against HEAD, including program entrypoints outside src/.
    for path in _REQUIRED_SOURCE:
        tracked = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:" + path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=15).stdout
        if tracked != (root / path).read_bytes():
            raise ValueError("A2-R source blob differs from recorded Git tree")
    return {
        "source_commit": expected_commit, "source_tree": expected_tree,
        "preset_sha256": expected_preset,
        "checkout_clean_and_pinned": True,
        "independent_external_anchor_checked_by_caller": True,
        "runtime_execution_identity_attested": False,
    }


def verify_generated_fork(*, root, generated):
    """Check every generated module against its source and build manifest.

    Manifest is *not* proof of execution. A2-R source audit checks both
    original source and built bytes, including all overlays and no extra py.
    """
    root, generated = Path(root), Path(generated)
    if (not root.is_absolute() or not generated.is_absolute()
            or root.is_symlink() or generated.is_symlink()
            or not generated.is_dir() or generated.resolve().is_relative_to(root.resolve())):
        raise ValueError("generated I1 fork must be disposable, separate from source")
    file = generated / "i1_build_manifest.json"
    if not file.is_file() or file.is_symlink():
        raise ValueError("I1 generated source manifest missing")
    record = json.loads(file.read_bytes())
    if (type(record) is not dict or
            record.get("schema") != "i1-namespaced-source-build-v1" or
            record.get("build_mode") != "independent_i1_and_i1lab_packages" or
            record.get("oracle_or_bench_transferred_into_individual") is not False or
            type(record.get("files")) is not dict or not record["files"]):
        raise ValueError("invalid isolated I1 build provenance")
    files = record["files"]
    actual = {p.relative_to(generated).as_posix() for p in generated.rglob("*.py")}
    if set(files) != actual:
        raise ValueError("I1 generated module roster missing or contains extras")
    for rel, entry in files.items():
        if (type(rel) is not str or type(entry) is not dict
                or set(entry) != {"source_path", "source_sha256", "built_sha256"}
                or type(entry["source_path"]) is not str
                or not SHA64.fullmatch(entry["source_sha256"])
                or not SHA64.fullmatch(entry["built_sha256"])):
            raise ValueError("invalid I1 build manifest entry")
        built = generated / rel
        source = root / "src" / entry["source_path"]
        if (not built.is_file() or built.is_symlink() or not source.is_file()
                or source.is_symlink()
                or not built.resolve().is_relative_to(generated.resolve())
                or not source.resolve().is_relative_to((root / "src").resolve())
                or _digest(source.read_bytes()) != entry["source_sha256"]
                or _digest(built.read_bytes()) != entry["built_sha256"]):
            raise ValueError("generated runtime/source module differs from manifest")
    return {
        "generated_modules_verified": len(files),
        "source_and_built_files_match": True,
        "runtime_execution_identity_attested": False,
    }


def _born_td_config(runtime):
    config = runtime.q_active.config
    f = config.features
    return {
        "version": config.version, "beta": config.beta,
        "eta": config.eta, "lambda_e": config.lambda_e,
        "feature_version": f.version,
        "feature_names": list(f.feature_names),
        "position_scale_x": f.position_scale_x,
        "position_scale_y": f.position_scale_y,
    }


def reconstruct_pristine_birth(*, role, seed, mode, preset_sha256):
    """Create a NEVER-stepped reference, without M11 custody or new WAL.

    This uses a locked source's actual constructor to attest its full M11
    configuration, distinct from the archived study actor and its report.
    """
    if (role not in ROLES or type(seed) is not int or seed not in SEEDS
            or mode not in MODES or type(preset_sha256) is not str
            or not SHA64.fullmatch(preset_sha256)):
        raise ValueError("A2-R birth outside frozen original matrix")
    from i1lab.i1_natural_runtime import I1Runtime
    from i1lab.m11_transactional_mortal import _runtime_contract
    from i1lab.matched_temperament_research import matched_temperament_configuration
    from i1_eco_a2r_birth import (
        a2r_matched_reward_birth, verify_born_reward_owner,
    )
    from i1_eco_a1_worlds import a1_world_parameters
    from run_i1_world_preset import load_preset, _birth_parameters
    from i1lab.world import WorldBody

    identity = _identity(role, seed, mode)
    base, raw_sha = load_preset("oasis")
    if raw_sha != preset_sha256:
        raise ValueError("world preset not equal to externally locked raw bytes")
    params, _ = _birth_parameters(base)
    parameters, initial_view = a1_world_parameters(params, role=role)
    parameters = {**parameters,
                  "diagnostic_sample_cost_uc": 1,
                  "module_occupancy_cost_uc": 1}
    expected = matched_temperament_configuration(
        parameters["stage11_config"], life_id=identity,
        world="eco-a2r-reward", seed=seed)
    intended = expected.temperament_parameters.as_dict()
    with a2r_matched_reward_birth(
            life_id=identity, role=role, seed=seed, mode=mode):
        born = I1Runtime(birth_life_id=identity, autonomous_mortal=True,
                         m11_sqlite_custody=True, wal_path=None, **parameters)
        verify_born_reward_owner(born.value_needs, mode=mode)
    if born.temperament_parameters.as_dict() != intended:
        raise ValueError("actual fresh temperament differs from isolated source")
    if (born.value_needs.config.weights !=
            expected.stage9.stage8.stage7.stage6.stage4.value_needs.weights):
        raise ValueError("born Value/Needs weights differ from source")
    if born.world.capture_local(t_monde=1).as_dict() != initial_view:
        raise ValueError("born visible world differs from preregistered oasis")
    # Stage8 blending parameters must come from the reconstructed frozen
    # source, never from a life report or the experienced M11 reward stream.
    stage8_config = born.stage8_option_evaluator.config
    if (stage8_config != born._stage8_config.evaluation
            or stage8_config != expected.stage9.stage8.evaluation):
        raise ValueError("pristine Stage8 blend differs from source birth")
    stage8_calibration = {
        "version": stage8_config.version, "n0": stage8_config.n0,
        "evidence_scale": stage8_config.evidence_scale,
        "extrinsic_gain": stage8_config.extrinsic_gain,
    }
    return {
        "identity": identity, "role": role, "seed": seed, "mode": mode,
        "runtime_contract": _runtime_contract(born),
        "world_config_sha256": born.world.config.digest(),
        "initial_body": dict(born.world.body.as_dict()),
        "initial_inventory": dict(born.world.inventory()),
        "initial_perception": born.world.capture_local(t_monde=1).as_dict(),
        "born_temperament": intended,
        "value_needs_config_version": born.value_needs.config.version,
        "setpoints": dict(born.value_needs.config.setpoints),
        "weights": dict(born.value_needs.config.weights),
        "scales": dict(born.value_needs.config.normalization_scales),
        "born_td": _born_td_config(born),
        "stage8_evaluation": stage8_calibration,
        "born_td_evidence_scale": born.q_active.config.evidence_scale,
        "stage11_intrinsic_weight": born._stage11_config.intrinsic_weight,
        "world_clock": {
            "day_steps": born.world.config.day_steps,
            "night_steps": born.world.config.night_steps,
            "night_start_step": born.world.config.night_start_step,
        },
        "q_at_birth_empty": born.q_active.export_causal_state()["weights"] == {},
        "scope": "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
    }


def verify_native_birth(*, db_path, role, seed, mode,
                        expected_source_commit, expected_source_tree,
                        expected_preset_sha256, checkout_root,
                        generated_root, allow_incomplete=False):
    """Join external Git lock, generated source, expected birth and M11.

    No effect from original report fields is trusted. Always returns a
    technical comparison, not permission to add a row to A2-R statistics.
    """
    from i1_a2r_m11_cold import inspect_m11
    from i1_a2r_q_replay import cold_replay_m11

    pin = verify_source_checkout(
        root=checkout_root, expected_commit=expected_source_commit,
        expected_tree=expected_source_tree,
        expected_preset=expected_preset_sha256)
    build = verify_generated_fork(root=checkout_root, generated=generated_root)
    reference = reconstruct_pristine_birth(
        role=role, seed=seed, mode=mode,
        preset_sha256=expected_preset_sha256)
    id_ = reference["identity"]
    cold = inspect_m11(path=db_path, identity=id_, mode=mode,
                       allow_incomplete=allow_incomplete)
    if cold["runtime_contract"] != reference["runtime_contract"]:
        raise ValueError("M11 born constructor hash differs from pinned source")
    if (cold["owner"]["owner_config_version"] !=
            reference["value_needs_config_version"] or
            cold["owner"]["td_config_version"] !=
            reference["born_td"]["version"] or
            cold["owner"]["td_feature_version"] !=
            reference["born_td"]["feature_version"]):
        raise ValueError("M11 TD/Value-Needs owner is not from locked birth")
    if (not reference["q_at_birth_empty"] or
            cold["physical_steps"][0]["before"] != reference["initial_body"]):
        raise ValueError("M11 first physiological state not equal to born source")
    replay = cold_replay_m11(
        path=db_path, identity=id_, mode=mode,
        setpoints=reference["setpoints"], weights=reference["weights"],
        born_td=reference["born_td"],
        world_clock=reference["world_clock"],
        allow_incomplete=allow_incomplete)
    if (replay["m11_journal_head"] != cold["receipt"]["journal_head"] or
            replay["m11_state_hash"] != cold["receipt"]["state_hash"] or
            not replay["full_q_replay_verified"]):
        raise ValueError("M11 state moved or Q TD could not be cold reconciled")
    return {
        "scope": "A2R_SOURCE_BIRTH_M11_TECHNICAL_CHAIN_NOT_L3",
        "identity": id_, "mode": mode,
        "source_commit": pin["source_commit"],
        "source_tree": pin["source_tree"],
        "preset_sha256": pin["preset_sha256"],
        "built_modules": build["generated_modules_verified"],
        "reconstructed_birth": reference,
        "m11_runtime_contract_verified": True,
        "m11_owner_source_version_verified": True,
        "m11_original_journal_head": cold["receipt"]["journal_head"],
        "m11_original_state_hash": cold["receipt"]["state_hash"],
        "m11_q_td_full_vector_reconciled": True,
        "technical_incomplete": allow_incomplete,
        "external_run_event_sha_attested": False,
        "external_ci_run_attempt_attested": False,
        "original_archive_sha_bound": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
        "historical_A1C": "NO_GO",
    }
