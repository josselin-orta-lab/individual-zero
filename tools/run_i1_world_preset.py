#!/usr/bin/env python3
"""Run PREDECLARED physical world presets with the current canonical I1 birth.

Environment facts belong to the Lab/operator, not the individual's belief or
policy. No forced decisions, hidden-hazard oracle, A2.38/H1/H2 cohort or rewind.
Death is final. Technical errors fail the command and are never retried.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
PRESETS = ROOT / "src/i1/lab/world_presets"
SCHEMA = "individual-zero-i1-world-preset/v1"
NAMES = re.compile(r"[a-z][a-z0-9-]{1,39}\Z")
KINDS = {"berry_a", "berry_b", "wood", "stone"}
LAYERS = ("water_sources", "resources", "obstacles", "creatures",
          "danger_zones", "lethal_zones")
BODY = ("energy", "food", "water", "integrity")
MAX_STEPS, MAX_LIVES = 300, 3


def _fields(value, names, label):
    if not isinstance(value, dict) or set(value) != set(names):
        raise ValueError(label + " must contain exactly: " + ", ".join(names))


def _cell(value, label):
    if (not isinstance(value, list) or len(value) != 2
            or any(type(n) is not int or not 1 <= n <= 30 for n in value)):
        raise ValueError(label + ": expected an interior [x,y] cell")
    return tuple(value)


def available(presets_dir=PRESETS):
    result = []
    for path in sorted(Path(presets_dir).glob("*.json")):
        if path.is_symlink():
            raise ValueError("symlinked world preset refused")
        result.append(load_preset(path.stem, presets_dir=presets_dir))
    return result


def load_preset(name, *, presets_dir=PRESETS):
    if type(name) is not str or not NAMES.fullmatch(name):
        raise ValueError("unknown or malformed world preset name")
    path = Path(presets_dir) / (name + ".json")
    if path.is_symlink() or not path.is_file():
        raise ValueError("unregistered or symlinked world preset: " + name)
    raw = path.read_bytes()
    if len(raw) > 16384:
        raise ValueError("world preset too large")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("invalid world preset JSON") from exc
    _fields(data, ("schema", "engine", "id", "description", "spawn",
                   "initial_body", "layout", "recommended_steps"), "preset")
    if (data["schema"] != SCHEMA or data["engine"] != "I1"
            or data["id"] != name or type(data["description"]) is not str
            or not 1 <= len(data["description"]) <= 240):
        raise ValueError("preset identity/description mismatch")
    _cell(data["spawn"], "spawn")
    _fields(data["initial_body"], BODY, "initial_body")
    for k in BODY:
        value = data["initial_body"][k]
        if (type(value) not in (int, float) or
                not math.isfinite(value) or not 0 <= value <= 100):
            raise ValueError("invalid physiological initial state: " + k)
    layout = data["layout"]
    _fields(layout, LAYERS, "layout")
    for key in LAYERS:
        if not isinstance(layout[key], list) or len(layout[key]) > 100:
            raise ValueError("invalid world layer: " + key)
    for layer in LAYERS:
        if layer == "resources":
            continue
        cells = [_cell(item, layer) for item in layout[layer]]
        if len(cells) != len(set(cells)):
            raise ValueError("duplicate world cell in " + layer)
    if tuple(data["spawn"]) in {
        tuple(point) for point in layout["obstacles"]
    }:
        raise ValueError("spawn blocked by obstacle")
    seen_resources = set()
    for item in layout["resources"]:
        _fields(item, ("cell", "kind", "quantity"), "resource")
        cell = _cell(item["cell"], "resource")
        if item["kind"] not in KINDS or type(item["quantity"]) is not int:
            raise ValueError("invalid resource kind or quantity")
        if not 1 <= item["quantity"] <= 100:
            raise ValueError("resource quantity must be in [1,100]")
        key = (cell, item["kind"])
        if key in seen_resources:
            raise ValueError("duplicate resource kind at one cell")
        seen_resources.add(key)
    steps = data["recommended_steps"]
    if type(steps) is not int or not 1 <= steps <= MAX_STEPS:
        raise ValueError("invalid recommended step count")
    return data, sha256(raw).hexdigest()


def _build_physics_and_layout(preset, baseline):
    from i1lab.world import BodyState, Position, WorldBody, WorldLayout

    def position(cell):
        return Position(*cell)

    cfg = replace(
        baseline.world.config,
        version="i1-lab-world-preset-v1:" + preset["id"],
        initial_position=position(preset["spawn"]),
        initial_body=BodyState(**preset["initial_body"]),
    )
    layout_source = preset["layout"]
    layout = WorldLayout(
        water_sources=frozenset(position(c) for c in layout_source["water_sources"]),
        resources=tuple(
            (position(r["cell"]), r["kind"], r["quantity"])
            for r in layout_source["resources"]
        ),
        obstacles=frozenset(position(c) for c in layout_source["obstacles"]),
        creatures=frozenset(position(c) for c in layout_source["creatures"]),
        danger_zones=frozenset(position(c) for c in layout_source["danger_zones"]),
        lethal_zones=frozenset(position(c) for c in layout_source["lethal_zones"]),
        oracle_canary="OPERATOR_ONLY_WORLD_PRESET_HIDDEN:" + preset["id"],
    )
    cfg.validate()
    layout.validate(cfg)
    world = WorldBody(config=cfg, layout=layout)
    local = world.capture_local(t_monde=1).as_dict()
    # No environmental danger map or remote knowledge is injected into I1.
    if any(x in local for x in ("danger_zones", "lethal_zones", "oracle_canary")):
        raise AssertionError("local perception includes privileged world truth")
    if layout.oracle_canary in str(local):
        raise AssertionError("operator canary leaked into perception")
    spawn = preset["spawn"]
    for e in local["visible_entities"]:
        p = e["position"]
        if abs(p["x"] - spawn[0]) + abs(p["y"] - spawn[1]) > 1:
            raise AssertionError("remote entity was observable at birth")
    return cfg, layout, local


def _birth_parameters(preset):
    from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
    from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
    from i1.modules.stage12_detectors import Stage12DetectionPolicy

    base = build_stage11_reference_runtime(autonomous_mortal=True)
    sleep = build_stage10_reference_runtime(autonomous_mortal=True)
    world_config, layout, local = _build_physics_and_layout(preset, base)
    stage10 = replace(
        sleep._stage10_config,
        stage9=base._stage11_config.stage9,
    )
    detector = Stage12DetectionPolicy(
        version="i1-world-preset-diagnostic-v1",
        window=12, stagnation_steps=3, stagnation_tolerance=0.05,
        loop_repetitions=2, loop_max_period=2,
        entropy_min_samples=3, entropy_warning_fraction=0.25,
        bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
    )
    params = dict(
        world_config=world_config, layout=layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold),
        stage11_config=base._stage11_config, stage10_config=stage10,
        equipment=base.equipment, detector_policy=detector,
    )
    return params, local


def _wal_life(*, birth, params, life_id, path, steps):
    from i1lab.journal import HashChainedJournal

    life = birth(life_id=life_id, wal_path=str(path), **params)
    trajectory = []
    for _ in range(steps):
        receipt = life.run_step()
        if receipt.execution_status not in ("applied", "dead", "safety_block"):
            raise RuntimeError("unexpected I1 step outcome")
        trajectory.append({
            "world_step": life.scheduler.t_monde,
            "execution": receipt.execution_status,
            "body": dict(life.world.telemetry()),
            "position": life.world.position.as_dict(),
            "inventory": dict(life.world.inventory()),
            "journal_head": life.journal.head_hash,
        })
        if receipt.execution_status == "dead":
            break
    if not trajectory or not life.journal.verify():
        raise RuntimeError("mortal journal verification failed")
    audit = HashChainedJournal.audit_durable_wal(str(path))
    # Compare the audited count without copying the entire append-only
    # journal into a tuple. The independent WAL audit still checks every
    # occurrence and its cryptographic chain.
    if (audit["head_hash"] != life.journal.head_hash
            or audit["verified_entries"] != life.journal.entry_count):
        raise RuntimeError("durable journal differs from live journal")
    return {
        "lifecycle": life.stage3.substrate.mortal_status.value,
        "steps": trajectory,
        "journal_head": life.journal.head_hash,
        "durable_entries": audit["verified_entries"],
        "custody_file": path.name,
    }


def _m11_life(*, birth, params, life_id, path, steps):
    from i1lab.sqlite_life_store import SQLiteLifeLedger

    trajectory = []
    with birth(db_path=str(path), life_id=life_id, **params) as life:
        for _ in range(steps):
            receipt = life.run_step()
            if receipt.status not in ("active", "dead"):
                raise RuntimeError("uncertain M11 life status")
            trajectory.append({
                "world_step": receipt.world_step,
                "generation": receipt.generation,
                "lifecycle": receipt.status,
                "execution": receipt.outcome,
                "journal_count": receipt.journal_count,
                "journal_head": receipt.journal_head,
            })
            if receipt.status == "dead":
                break
    if not trajectory:
        raise RuntimeError("M11 returned no generation receipt")
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(path), expected_individual_id=life_id)
    if (audit.generation != len(trajectory)
            or audit.journal_head != trajectory[-1]["journal_head"]
            or audit.pending_intent):
        raise RuntimeError("M11 read-only audit disagrees with committed life")
    if audit.status == "dead" and audit.may_recover:
        raise RuntimeError("terminal identity unexpectedly recoverable")
    return {
        "lifecycle": audit.status, "steps": trajectory,
        "journal_head": audit.journal_head,
        "durable_entries": audit.journal_count,
        "may_recover": audit.may_recover,
        "custody_file": path.name,
    }


def execute(*, preset_name, seed, steps, lives, custody, output_dir):
    if (type(seed) is not int or not 0 <= seed <= 2**32 - 1
            or type(steps) is not int or not 1 <= steps <= MAX_STEPS
            or type(lives) is not int or not 1 <= lives <= MAX_LIVES
            or custody not in {"wal", "m11"}):
        raise ValueError("out-of-bounds seed, steps, lives or custody")
    preset, digest = load_preset(preset_name)
    output_dir = Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError("a world run must use a fresh output directory")
    output_dir.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "individual-zero-i1-world-run/v1",
        "engine": "I1",
        "model": "i1lab.i1_natural_runtime.I1Runtime",
        "source": {"preset": preset_name, "sha256": digest,
                   "description": preset["description"]},
        "run": {"seed": seed, "requested_steps": steps,
                "requested_lives": lives, "custody": custody,
                "git_head": None},
        "scientific_gate": "NOT_EVALUATED",
        "old_cohorts_used_as_oracles": False,
        "lives": [],
        "status": "NOT_STARTED",
    }
    try:
        git = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        if git.returncode == 0:
            report["run"]["git_head"] = git.stdout.strip()
        with TemporaryDirectory(prefix="i1-world-preset-build-") as temp:
            sys.path.insert(0, str(ROOT / "src"))
            sys.path.insert(0, str(ROOT / "scripts"))
            from build_i1_fork import generate
            build = Path(temp) / "generated"
            generate(build)
            sys.path.insert(0, str(build))
            from i1lab.i1_birth import birth_i1, birth_i1_m11

            params, initial_local = _birth_parameters(preset)
            report["environment"] = {
                "spawn": preset["spawn"],
                "initial_body": preset["initial_body"],
                "layout": preset["layout"],  # External operator ONLY.
                "world_physics_digest": params["world_config"].digest(),
                "initial_local_perception": initial_local,
                "privileged_environment_not_given_to_policy": True,
            }
            for i in range(lives):
                life_id = "i1:preset:%s:%d:%d" % (preset_name, seed, i)
                suffix = ".sqlite" if custody == "m11" else ".wal"
                path = output_dir / ("life-%02d" % (i + 1) + suffix)
                if path.exists():
                    raise FileExistsError("refusing to overwrite a durable identity")
                if custody == "wal":
                    life = _wal_life(
                        birth=birth_i1, params=params, life_id=life_id,
                        path=path, steps=steps,
                    )
                else:
                    life = _m11_life(
                        birth=birth_i1_m11, params=params, life_id=life_id,
                        path=path, steps=steps,
                    )
                life["individual_id"] = life_id
                report["lives"].append(life)
        report["status"] = "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
    except Exception as exc:
        report["status"] = "TECHNICAL_FAILURE"
        report["technical_error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        (output_dir / "report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="list the checked-in preset worlds, no birth")
    parser.add_argument("--validate-only", action="store_true",
                        help="validate preset data only, no birth")
    parser.add_argument("--preset", help="registered preset id")
    parser.add_argument("--seed", type=int, default=246)
    parser.add_argument("--steps", type=int,
                        help="maximum steps per mortal life, default preset recommendation")
    parser.add_argument("--lives", type=int, default=1)
    parser.add_argument("--custody", choices=("wal", "m11"), default="wal")
    parser.add_argument("--output-dir", type=Path,
                        help="new output directory for reports and durable files")
    args = parser.parse_args()
    try:
        if args.list:
            items = available()
            print(json.dumps({
                "engine": "I1", "schema": SCHEMA,
                "presets": [
                    {"id": p["id"], "description": p["description"],
                     "recommended_steps": p["recommended_steps"]}
                    for p, _digest in items
                ],
            }, indent=2))
            return 0
        if not args.preset:
            raise ValueError("--preset is required for one-world operations")
        preset, digest = load_preset(args.preset)
        if args.validate_only:
            print(json.dumps({"status": "DATA_VALIDATED_NOT_RUN",
                              "preset": preset["id"], "source_sha256": digest,
                              "scientific_gate": "NOT_EVALUATED"}))
            return 0
        if args.output_dir is None:
            raise ValueError("--output-dir is mandatory for an actual world run")
        report = execute(
            preset_name=args.preset, seed=args.seed,
            steps=args.steps if args.steps is not None
            else preset["recommended_steps"],
            lives=args.lives, custody=args.custody,
            output_dir=args.output_dir,
        )
        print(json.dumps({
            "status": report["status"],
            "preset": report["source"]["preset"],
            "seed": report["run"]["seed"],
            "custody": args.custody,
            "lives": [{"id": x["individual_id"],
                       "lifecycle": x["lifecycle"],
                       "world_steps": len(x["steps"])} for x in report["lives"]],
            "report": str(args.output_dir / "report.json"),
            "scientific_gate": "NOT_EVALUATED",
        }, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, AssertionError) as exc:
        print("WORLD_PRESET_RUN_FAILED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
