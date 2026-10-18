#!/usr/bin/env python3
"""Run isolated mortal I1 movement/need investigations with matched world draws.

Environment facts belong to the Lab/operator, not the individual's belief or
policy. No forced decisions, hidden-hazard oracle, A2.38/H1/H2 cohort or rewind.
Death is final. Technical errors fail the command and are never retried.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import random
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
MAX_STEPS, MAX_LIVES = 1600, 3
RESEARCH_WEIGHTS = (0.0, 0.2, 0.65)
GEOGRAPHIC_NOVELTY_WEIGHTS = (0.15, 0.3, 0.6, 0.9)
GEO_POLICY = "i1-geographic-novelty-sensitivity-v1"


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



def _vary_preset_layout(preset, base_digest, variant):
    """Prebirth seeded environment draw; never disclose operator layout to I1.

    variant=0 is the unmodified registered world. For a positive variant,
    water and resource positions are independently jittered within three
    Manhattan cells; starting body, spawn and preset's obstacles/hazards
    stay fixed. This defines independently sampled resource layouts, not
    independent physics or new unknown categories.
    """
    if type(variant) is not int or not 0 <= variant <= 1_000_000:
        raise ValueError("invalid environment variation index")
    if variant == 0:
        return preset, base_digest
    changed = deepcopy(preset)
    rng = random.Random(int.from_bytes(
        sha256(f"i1-longlife-layout-v1:{base_digest}:{variant}".encode()).digest(),
        "big",
    ))
    layout = changed["layout"]
    forbidden = {tuple(p) for layer in
                 ("obstacles", "creatures", "danger_zones", "lethal_zones")
                 for p in layout[layer]}
    def candidate(cell, seen, *, preserve=False):
        initial = tuple(cell)
        if preserve:
            seen.add(initial)
            return list(initial)
        choices = [(initial[0] + dx, initial[1] + dy)
                   for dx in range(-3, 4) for dy in range(-3, 4)
                   if 0 < abs(dx) + abs(dy) <= 3]
        rng.shuffle(choices)
        for p in choices:
            if (1 <= p[0] <= 30 and 1 <= p[1] <= 30
                    and p not in forbidden and p not in seen):
                seen.add(p)
                return list(p)
        if initial not in seen and initial not in forbidden:
            seen.add(initial)
            return list(initial)
        raise ValueError("no safe, unique resource perturbation")
    spawn = tuple(changed["spawn"])
    placed = set()
    varied_water = []
    for cell in layout["water_sources"]:
        keep_birth_water = (preset["id"] == "oasis" and tuple(cell) == spawn)
        varied_water.append(candidate(cell, placed, preserve=keep_birth_water))
    layout["water_sources"] = varied_water
    # Uniqueness is per (kind, cell), consistent with the registered schema.
    per_kind = {}
    for resource in layout["resources"]:
        seen = per_kind.setdefault(resource["kind"], set())
        preserve_birth_food = (
            preset["id"] == "oasis" and tuple(resource["cell"]) == spawn
        )
        resource["cell"] = candidate(
            resource["cell"], seen, preserve=preserve_birth_food,
        )
    digest = sha256(json.dumps(
        changed, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    return changed, digest


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


def _research_geographic_birth(params, novelty_weight):
    """Reproduce canonical I1 geography prebirth; change ONLY novelty weight.

    The natural constructor installs exactly these five Stage11 settings when
    .geographic is None. Preinstalling them with .geographic non-None prevents
    that default branch from running twice. At novelty=0.15 this MUST be
    configuration-equivalent to canonical birth; other arms carry version IDs.
    No map, outcome, prior reward, safety fact, or motor command is supplied.
    """
    from i1.modules.geographic_exploration import GeographicExplorationConfig

    if novelty_weight not in GEOGRAPHIC_NOVELTY_WEIGHTS:
        raise ValueError("unknown preregistered novelty sensitivity")
    cfg = params["stage11_config"]
    if cfg.geographic is not None:
        raise ValueError("expected unmodified reference fixture geography")
    standard_version = "i1-firstperson-frontier-v1"
    arm = ("" if novelty_weight == 0.15 else
           "+" + GEO_POLICY + "-w" + str(novelty_weight).replace(".", "p"))
    geography = GeographicExplorationConfig(
        version=standard_version + arm, novelty_weight=novelty_weight,
        max_distinct_sites=1024, max_targets_per_cycle=1,
        observe_routes=False, refresh_surveys=False,
    )
    upgraded = replace(
        cfg, version=cfg.version + "+" + standard_version + arm,
        geographic=geography,
        intrinsic_weight=min(cfg.intrinsic_weight, 0.35),
        local_threat_alerts=True,
        geographic_capacity_guard_enabled=True,
    )
    upgraded.validate()
    return {**params, "stage11_config": upgraded}


def _observer_owner_hashes(life):
    """Operator-only hashes of existing published owner state; no writes."""
    from i1lab.determinism import canonical_causal_bytes, sha256_hex

    owners = {
        "value_needs": life.value_needs,
        "causal_model": life._i1_active_owner_views["causal_model"],
        "perception": life._i1_active_owner_views["perception"],
        "metacognition_health": life._i1_active_owner_views["metacognition_health"],
        "slow_history": life.slow_history,
    }
    return {
        name: sha256_hex(canonical_causal_bytes(owner.export_causal_state()))
        for name, owner in sorted(owners.items())
    }


def _wal_life(*, birth, params, life_id, path, steps, observe_owner_digests=False):
    from i1lab.journal import HashChainedJournal

    life = birth(life_id=life_id, wal_path=str(path), **params)
    trajectory = []
    for _ in range(steps):
        # Read-only observer, strictly outside the cognitive world step.
        before = _observer_owner_hashes(life) if observe_owner_digests else None
        history_before = life.slow_history.current_version if observe_owner_digests else None
        entry_count_before = life.journal.entry_count if observe_owner_digests else None
        receipt = life.run_step()
        if receipt.execution_status not in ("applied", "dead", "safety_block"):
            raise RuntimeError("unexpected I1 step outcome")
        trajectory.append({
            "world_step": life.scheduler.t_monde,
            "execution": receipt.execution_status,
            # Operator-only passive sensor. These fields are already computed
            # by the natural runtime and are never fed back into cognition.
            "action_primitive": receipt.command_primitive,
            "action_source": receipt.source,
            "reflex_triggered": receipt.reflex_triggered,
            "fallback_used": receipt.fallback_used,
            "cycles_used": receipt.cycles_used,
            "body": dict(life.world.telemetry()),
            "position": life.world.position.as_dict(),
            "inventory": dict(life.world.inventory()),
            "journal_head": life.journal.head_hash,
        })
        if observe_owner_digests:
            committed_refs = [
                entry.event_id
                for entry in life.journal.entries_since(entry_count_before)
                if entry.causal_event.get("kind") == "stage10_consolidation_committed"
            ]
            trajectory[-1]["owner_observation"] = {
                "before": before,
                "after": _observer_owner_hashes(life),
                "history_version_before": history_before,
                "history_version_after": life.slow_history.current_version,
                "stage10_commit_event_ids": committed_refs,
                "interpretation": "OPERATOR_OBSERVATION_NOT_CAUSAL_ATTRIBUTION",
            }
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
        "effective_sleep_fatigue_weight": life._stage10_config.sleep.fatigue_weight,
        "effective_berry_b_damage": life.world.config.berry_effects["berry_b"].integrity_delta,
        "effective_geographic_novelty_weight": life._stage11_config.geographic.novelty_weight,
        "effective_geographic_policy_version": life._stage11_config.geographic.version,
        "effective_affordance_policy": next((x for x in life._i1_model_contract
            if isinstance(x, str) and x.startswith("i1-unknown-action-affordance-")), None),
        "effective_sleep_fatigue_gain": life._stage10_config.sleep.fatigue_gain,
        "effective_sleep_consolidation_weight": life._stage10_config.sleep.consolidation_weight,
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


def execute(*, preset_name, seed, steps, lives, custody, output_dir,
            observe_owner_digests=False, experimental_fatigue_weight=None,
            world_variant=0, geographic_novelty_weight=None,
            research_positive_lived_floor=False, experimental_berry_b_damage=None):
    if (type(seed) is not int or not 0 <= seed <= 2**32 - 1
            or type(steps) is not int or not 1 <= steps <= MAX_STEPS
            or type(lives) is not int or not 1 <= lives <= MAX_LIVES
            or custody not in {"wal", "m11"}):
        raise ValueError("out-of-bounds seed, steps, lives or custody")
    if observe_owner_digests and custody != "wal":
        raise ValueError("owner observer is only implemented for immutable WAL")
    if (experimental_fatigue_weight is not None
            and (type(experimental_fatigue_weight) is not float
                 or experimental_fatigue_weight not in RESEARCH_WEIGHTS
                 or custody != "wal")):
        raise ValueError("isolated scientific fatigue arms require WAL and exact registered weights")
    if experimental_berry_b_damage not in (None, 0.0, -10.0, -100.0):
        raise ValueError("unknown preregistered berry toxicity")
    if type(research_positive_lived_floor) is not bool:
        raise ValueError("research positive-evidence mode must be bool")
    if geographic_novelty_weight not in GEOGRAPHIC_NOVELTY_WEIGHTS:
        raise ValueError("registered geographic novelty arm is mandatory")
    if custody != "wal":
        raise ValueError("geographic intervention requires immutable mortal WAL")
    if type(world_variant) is not int or not 0 <= world_variant <= 1_000_000:
        raise ValueError("invalid environment variation index")
    preset, base_digest = load_preset(preset_name)
    preset, digest = _vary_preset_layout(preset, base_digest, world_variant)
    output_dir = Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError("a world run must use a fresh output directory")
    output_dir.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "individual-zero-i1-world-run/v1",
        "engine": "I1",
        "model": "i1lab.i1_natural_runtime.I1Runtime",
        "source": {"preset": preset_name, "sha256": digest,
                   "base_preset_sha256": base_digest,
                   "world_variant": world_variant,
                   "variation_policy": "i1-longlife-layout-v1",
                   "description": preset["description"]},
        "run": {"seed": seed, "requested_steps": steps,
                "requested_lives": lives, "custody": custody,
                "git_head": None,
                "observe_owner_digests": bool(observe_owner_digests),
                "experimental_fatigue_weight": experimental_fatigue_weight,
                "world_variant": world_variant,
                "geographic_novelty_weight": geographic_novelty_weight,
                "geographic_policy": GEO_POLICY,
                "research_positive_lived_floor": research_positive_lived_floor,
                "experimental_berry_b_damage": experimental_berry_b_damage,
                "research_floor_policy": (
                    "i1-research-positive-lived-floor-v1" if research_positive_lived_floor
                    else "control-canonical-I1-affordance-evidence")},
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
            if research_positive_lived_floor:
                # Fresh research process: version and override only this I1
                # evaluator. Canonical actor source and I0 remain untouched.
                from i1_research_lived_evidence_floor import install_research_positive_floor
                install_research_positive_floor()
            if experimental_fatigue_weight is not None:
                # Research-only in-memory override, before any birth and in
                # a separate process per arm. Never modify canonical source.
                import i1lab.i1_natural_sleep as sleep_policy
                sleep_policy.FATIGUE_WEIGHT = experimental_fatigue_weight
                sleep_policy.POLICY += "-longlife-research-wf-" + str(experimental_fatigue_weight).replace(".", "p")

            params, initial_local = _birth_parameters(preset)
            if experimental_berry_b_damage is not None:
                from i1lab.world import BerryEffect
                cfg = params["world_config"]
                effects = dict(cfg.berry_effects)
                old = effects["berry_b"]
                effects["berry_b"] = BerryEffect(
                    food_gain=old.food_gain,
                    integrity_delta=experimental_berry_b_damage,
                )
                updated = replace(
                    cfg,
                    version=cfg.version + "+i1-berry-b-toxicity-research-v1:"
                    + str(experimental_berry_b_damage),
                    berry_effects=effects,
                )
                updated.validate()
                params["world_config"] = updated
            params = _research_geographic_birth(params, geographic_novelty_weight)
            report["environment"] = {
                "spawn": preset["spawn"],
                "initial_body": preset["initial_body"],
                "layout": preset["layout"],  # External operator ONLY.
                "world_physics_digest": params["world_config"].digest(),
                "initial_local_perception": initial_local,
                "privileged_environment_not_given_to_policy": True,
            }
            for i in range(lives):
                life_id = "i1:longlife:%s:v%d:seed%d:born%d" % (
                    preset_name, world_variant, seed, i,
                )
                suffix = ".sqlite" if custody == "m11" else ".wal"
                path = output_dir / ("life-%02d" % (i + 1) + suffix)
                if path.exists():
                    raise FileExistsError("refusing to overwrite a durable identity")
                if custody == "wal":
                    life = _wal_life(
                        birth=birth_i1, params=params, life_id=life_id,
                        path=path, steps=steps,
                        observe_owner_digests=observe_owner_digests,
                    )
                else:
                    life = _m11_life(
                        birth=birth_i1_m11, params=params, life_id=life_id,
                        path=path, steps=steps,
                    )
                expected_damage = (
                    -100.0 if experimental_berry_b_damage is None
                    else experimental_berry_b_damage
                )
                if life["effective_berry_b_damage"] != expected_damage:
                    raise AssertionError("effective born berry_b toxicity mismatch")
                if (custody == "wal" and life["effective_geographic_novelty_weight"]
                        != geographic_novelty_weight):
                    raise AssertionError("actual born I1 geographic novelty mismatch")
                expected_floor = "i1-research-positive-lived-floor-v1"
                effective = life["effective_affordance_policy"] or ""
                if (expected_floor in effective) != research_positive_lived_floor:
                    raise AssertionError("actual I1 affordance policy differs from research arm")
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
    parser.add_argument("--world-variant", type=int, default=0,
                        help="prebirth independent resource-layout draw index")
    parser.add_argument("--geographic-novelty-weight", type=float,
                        required=False, choices=GEOGRAPHIC_NOVELTY_WEIGHTS,
                        help="prebirth sensitivity arm; never an action dispatch")
    parser.add_argument("--experimental-berry-b-damage", type=float,
                        choices=(0.0, -10.0, -100.0), default=None,
                        help="I1-only prebirth research effect, not innate knowledge")
    parser.add_argument("--research-positive-lived-floor", action="store_true",
                        help="isolated post-living-positive-TD non-attenuation ablation")
    parser.add_argument("--experimental-fatigue-weight", type=float,
                        choices=RESEARCH_WEIGHTS, default=None,
                        help="research-only WAL arm; birth-only in-memory weight override")
    parser.add_argument(
        "--observe-owner-digests", action="store_true",
        help="operator-only before/after owner state hashes, WAL only; no motor feedback",
    )
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
            observe_owner_digests=args.observe_owner_digests,
            experimental_fatigue_weight=args.experimental_fatigue_weight,
            world_variant=args.world_variant,
            geographic_novelty_weight=args.geographic_novelty_weight,
            research_positive_lived_floor=args.research_positive_lived_floor,
            experimental_berry_b_damage=args.experimental_berry_b_damage,
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
