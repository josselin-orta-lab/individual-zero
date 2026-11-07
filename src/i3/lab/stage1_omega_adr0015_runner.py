"""Source-locked sharded runner for the Stage-1 omega ADR-0015 gate.

Importing this module never imports World/runtime and never executes a life.
Execution functions are explicit and are NOT wired to GitHub Actions here.

Selection: 16 complete shards = 8 populations x 2 selected architectures.
Validation: 24 complete shards = 8 populations x 3 arms.
No aggregate can be produced from a successful subset.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i3.lab import stage0_design as S
from i3.lab import stage1_omega_adr0015_design as D
from i3.modules.genome import digest

SCHEMA = "i3-stage1-omega-adr0015-runner/v1"
PROTOCOL = "i3-stage1-omega-adr0015-v1"
WORLDGEN_BLOB = "7d6548662664afbab28627ea432977a9d658af79"
SELECTION_SHARD = "i3-stage1-omega-selection-shard/v1"
SELECTION_AGGREGATE = "i3-stage1-omega-selection-aggregate/v1"
VALIDATION_SHARD = "i3-stage1-omega-validation-shard/v1"
VALIDATION_AGGREGATE = "i3-stage1-omega-validation-aggregate/v1"


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False)


def digest_json(value):
    return sha256(canonical(value).encode()).hexdigest()


def protocol_manifest():
    data = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "gate_design_schema": D.SCHEMA,
        "gate_design_sha256": D.plan()["sha256"],
        "selection_shards": [
            {"population": p, "arm": arm}
            for p in range(D.POPULATIONS)
            for arm in ("reference", "candidate")
        ],
        "validation_shards": [
            {"population": p, "arm": arm}
            for p in range(D.POPULATIONS)
            for arm in D.ARMS
        ],
        "selection_lives_per_shard": D.CANDIDATES * len(D.FAMILIES) * D.REPEATS,
        "validation_main_lives_per_shard": D.KEEP * len(D.FAMILIES) * D.REPEATS,
        "validation_rank0_replays_per_shard": len(D.FAMILIES) * D.REPEATS,
        "original_custody": "GZIP_CANONICAL_JSON_BEFORE_REDUCTION",
        "selection_barrier": "ALL_16_COMPLETE_BEFORE_ANY_RANKING",
        "validation_barrier": "ALL_24_COMPLETE_BEFORE_GATE",
        "retry_policy": "NO_RETRY_NO_REPLACEMENT",
        "reserve_policy": "SEALED",
        "full_competition_observer": True,
        "validation_depletion_resource_observer": True,
    }
    data["sha256"] = digest_json(data)
    return data


def _git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def validate_launch(expected_sha, expected_protocol):
    """Reject source/protocol/generator drift before any runtime import."""
    if (type(expected_sha) is not str or len(expected_sha) != 40
            or any(c not in "0123456789abcdef" for c in expected_sha)
            or _git("rev-parse", "HEAD") != expected_sha):
        raise ValueError("exact execution source SHA required")
    if expected_protocol != protocol_manifest()["sha256"]:
        raise ValueError("prospective protocol digest mismatch")
    if _git(
            "status", "--porcelain", "--untracked-files=all", "--",
            "src/i3", "tests/i3"):
        raise ValueError("dirty I3 source")
    if _git("rev-parse", "HEAD:src/i3/lab/p2_ecologies.py") != S.ECOLOGY_BLOB:
        raise ValueError("P2 ecology source drift")
    if _git("rev-parse", "HEAD:src/i3/lab/worldgen.py") != WORLDGEN_BLOB:
        raise ValueError("P2 world generator drift")


def _validate_population(population):
    if type(population) is not int or not 0 <= population < D.POPULATIONS:
        raise ValueError("population must be 0..7")
    return population


def _selection_arm(arm):
    if arm not in ("reference", "candidate"):
        raise ValueError("selection arm must be reference/candidate")
    return arm


def _validation_arm(arm):
    if arm not in D.ARMS:
        raise ValueError("validation arm must be reference/candidate/omega_zero")
    return arm


def _policy(arm):
    return (
        D.REFERENCE_POLICY if arm == "reference"
        else D.CANDIDATE_POLICY)


def selection_cases(population, arm):
    population = _validate_population(population)
    arm = _selection_arm(arm)
    worlds = [
        row for row in S.world_rows("selection")
        if row["population"] == population
    ]
    cases = []
    for seed in D.founder_seeds(population):
        for world in worlds:
            cases.append({
                "case_id": (
                    f"selection-p{population}-{arm}-g{seed}-"
                    f"{world['family']}-{world['index']}"),
                "phase": "selection",
                "population": population,
                "arm": arm,
                "policy": _policy(arm),
                "family": world["family"],
                "world_index": world["index"],
                "world_seed": world["world_seed"],
                "life_seed": world["life_seed"],
                "founder_seed": seed,
                "genome_digest": digest(D.genome_for_arm(arm, seed)),
                "horizon": D.HORIZON,
            })
    if len(cases) != D.CANDIDATES * len(D.FAMILIES) * D.REPEATS:
        raise RuntimeError("selection shard size drift")
    return tuple(cases)


def _selected_for(selection_aggregate, arm, population):
    if (type(selection_aggregate) is not dict
            or selection_aggregate.get("schema") != SELECTION_AGGREGATE
            or selection_aggregate.get("protocol_sha256")
            != protocol_manifest()["sha256"]):
        raise ValueError("valid immutable selection aggregate required")
    try:
        values = selection_aggregate["selected"][arm][str(population)]
    except (KeyError, TypeError) as exc:
        raise ValueError("missing selected population") from exc
    values = tuple(values)
    if len(values) != D.KEEP or len(set(values)) != D.KEEP:
        raise ValueError("invalid selected genome set")
    return values


def validation_cases(population, arm, selection_aggregate):
    population = _validate_population(population)
    arm = _validation_arm(arm)
    selected_key = "reference" if arm == "reference" else "candidate"
    selected = _selected_for(selection_aggregate, selected_key, population)
    worlds = [
        row for row in S.world_rows("validation")
        if row["population"] == population
    ]
    cases = []
    for rank, seed in enumerate(selected):
        for world in worlds:
            cases.append({
                "case_id": (
                    f"validation-p{population}-{arm}-rank{rank}-g{seed}-"
                    f"{world['family']}-{world['index']}"),
                "phase": "validation",
                "population": population,
                "arm": arm,
                "policy": _policy(arm),
                "family": world["family"],
                "world_index": world["index"],
                "world_seed": world["world_seed"],
                "life_seed": world["life_seed"],
                "founder_seed": seed,
                "selected_rank": rank,
                "genome_digest": digest(D.genome_for_arm(arm, seed)),
                "horizon": D.HORIZON,
            })
    if len(cases) != D.KEEP * len(D.FAMILIES) * D.REPEATS:
        raise RuntimeError("validation shard size drift")
    return tuple(cases)


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (canonical(value) + "\n").encode()
    path.write_bytes(data)
    return sha256(data).hexdigest()


def _archive_original(folder, name, life):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    raw = (canonical(life) + "\n").encode()
    data = gzip.compress(raw, compresslevel=9, mtime=0)
    path = folder / (name + ".json.gz")
    path.write_bytes(data)
    return {
        "file": path.name,
        "gzip_sha256": sha256(data).hexdigest(),
        "canonical_json_sha256": sha256(raw).hexdigest(),
        "bytes_gzip": len(data),
        "bytes_json": len(raw),
    }


def _life_summary(life, paid):
    competition = life.get("observer_full_competition")
    if (type(competition) is not dict
            or len(competition.get("steps", ())) != life["steps_lived"]):
        raise ValueError("full Competition observer incomplete")
    frontier = life.get("frontier_information")
    return {
        "terminal": paid["terminal"],
        "steps_lived": paid["steps_lived"],
        "world_sha256": paid["world_sha256"],
        "source_sha256": paid["source_sha256"],
        "trace_head": paid["trace_head"],
        "evidence_head": paid["evidence_head"],
        "inactive_steps": paid["inactive_steps"],
        "paid": dict(paid["paid"]),
        "competition_steps": len(competition["steps"]),
        "cognitive_shortfall_steps":
            life["cognitive_accounting"]["shortfall_steps"],
        "frontier_information": (
            dict(frontier) if isinstance(frontier, dict) else None),
    }


def _run_case(case, output_dir, expected_source_pin=None, *, replay=False):
    """Run and archive exactly one predeclared life, then reduce it."""
    from i3.lab import p2_ecologies
    from i3.lab.stage0_energy import energy_receipt
    from i3.lab.stage0_revision import revision_receipt
    from i3.runtime.life import run_life

    genome = D.genome_for_arm(case["arm"], case["founder_seed"])
    if digest(genome) != case["genome_digest"]:
        raise RuntimeError("case genome digest drift")
    world = p2_ecologies.world_for(
        case["family"], case["phase"], case["world_index"])
    resource = (
        case["phase"] == "validation"
        and case["family"] == "depletion")
    life = run_life(
        genome, world, case["life_seed"], case["horizon"],
        keep_trace=True,
        observer_full_competition=True,
        observer_mind_digest=True,
        observer_resource_acquisition=resource,
        decision_policy=case["policy"],
        protocol=PROTOCOL)

    suffix = "-replay" if replay else ""
    original = _archive_original(
        Path(output_dir) / "original",
        case["case_id"] + suffix, life)

    source_pin = life["manifest"]["source"]["sha256"]
    if expected_source_pin is not None and source_pin != expected_source_pin:
        raise ValueError("runtime source pin changed inside study")
    paid = energy_receipt(
        life, expected_protocol=PROTOCOL,
        expected_source_sha256=source_pin)
    summary = _life_summary(life, paid)

    revision = None
    if resource:
        revision = revision_receipt(
            life, expected_protocol=PROTOCOL,
            expected_source_sha256=source_pin)

    return {
        "case": dict(case),
        "original": original,
        "summary": summary,
        "revision": revision,
    }, source_pin


def run_selection_shard(population, arm, output_dir, *,
                        expected_sha, expected_protocol):
    validate_launch(expected_sha, expected_protocol)
    population = _validate_population(population)
    arm = _selection_arm(arm)
    output_dir = Path(output_dir)
    cases = selection_cases(population, arm)
    rows = []
    source_pin = None
    try:
        for case in cases:
            result, source_pin = _run_case(
                case, output_dir, source_pin)
            paid = result["summary"]
            rows.append({
                "gate": {
                    "candidate_seed": case["founder_seed"],
                    "world_index": case["world_index"],
                    "terminal": paid["terminal"],
                    "steps_lived": paid["steps_lived"],
                    "genome_digest": case["genome_digest"],
                },
                "family": case["family"],
                "world_seed": case["world_seed"],
                "life_seed": case["life_seed"],
                "world_sha256": paid["world_sha256"],
                "source_sha256": paid["source_sha256"],
                "competition_steps": paid["competition_steps"],
                "cognitive_shortfall_steps":
                    paid["cognitive_shortfall_steps"],
                "paid": paid["paid"],
                "inactive_steps": paid["inactive_steps"],
                "frontier_information": paid["frontier_information"],
                "original": result["original"],
            })
    except Exception as exc:
        failure = {
            "schema": SELECTION_SHARD,
            "status": "ENGINEERING_FAILURE_NOT_A_DEATH",
            "population": population,
            "arm": arm,
            "completed": len(rows),
            "expected": len(cases),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        _write_json(output_dir / "FAILURE.json", failure)
        raise

    report = {
        "schema": SELECTION_SHARD,
        "status": "COMPLETE",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_manifest()["sha256"],
        "execution_sha": expected_sha,
        "source_sha256": source_pin,
        "population": population,
        "arm": arm,
        "expected_lives": len(cases),
        "completed_lives": len(rows),
        "receipts": rows,
    }
    _write_json(output_dir / "selection-shard.json", report)
    return report


def _complete_shards(shards, schema, expected_keys):
    if not isinstance(shards, (list, tuple)):
        raise ValueError("shard list required")
    by_key = {}
    protocol_sha = protocol_manifest()["sha256"]
    execution_sha = source_pin = None
    for shard in shards:
        if (type(shard) is not dict or shard.get("schema") != schema
                or shard.get("status") != "COMPLETE"
                or shard.get("protocol_sha256") != protocol_sha):
            raise ValueError("incomplete/foreign shard")
        key = (shard["population"], shard["arm"])
        if key in by_key or key not in expected_keys:
            raise ValueError("duplicate/foreign shard key")
        by_key[key] = shard
        if execution_sha is None:
            execution_sha = shard["execution_sha"]
            source_pin = shard["source_sha256"]
        elif (shard["execution_sha"] != execution_sha
              or shard["source_sha256"] != source_pin):
            raise ValueError("shards do not share exact execution source")
    if set(by_key) != set(expected_keys):
        raise ValueError("all shards required; no successful-subset aggregation")
    return by_key, execution_sha, source_pin


def aggregate_selection(shards):
    expected = {
        (p, arm)
        for p in range(D.POPULATIONS)
        for arm in ("reference", "candidate")
    }
    by_key, execution_sha, source_pin = _complete_shards(
        shards, SELECTION_SHARD, expected)

    selected = {"reference": {}, "candidate": {}}
    rankings = {"reference": {}, "candidate": {}}
    world_hashes = {}
    observer_valid = True
    no_shortfall = True
    for p in range(D.POPULATIONS):
        for arm in ("reference", "candidate"):
            shard = by_key[(p, arm)]
            receipts = shard["receipts"]
            if len(receipts) != D.CANDIDATES * len(D.FAMILIES) * D.REPEATS:
                raise ValueError("selection shard receipt count drift")
            gate_rows = [row["gate"] for row in receipts]
            ranked = D.rank_selection(p, arm, gate_rows)
            selected[arm][str(p)] = list(ranked)
            rankings[arm][str(p)] = list(ranked)
            for row in receipts:
                key = (p, row["gate"]["world_index"])
                world_hashes.setdefault(key, set()).add(row["world_sha256"])
                observer_valid &= (
                    row["competition_steps"] == row["gate"]["steps_lived"])
                no_shortfall &= row["cognitive_shortfall_steps"] == 0

    if any(len(values) != 1 for values in world_hashes.values()):
        raise ValueError("selection world differs across candidates/arms")
    if not observer_valid or not no_shortfall:
        raise ValueError("selection custody floor failed")

    # Descriptive G0 architecture comparison on matched founder/world panels.
    matched = {}
    for p in range(D.POPULATIONS):
        by_arm_seed = {}
        for arm in ("reference", "candidate"):
            for row in by_key[(p, arm)]["receipts"]:
                seed = row["gate"]["candidate_seed"]
                by_arm_seed.setdefault((arm, seed), [0, 0])
                by_arm_seed[(arm, seed)][0] += (
                    row["gate"]["terminal"] == "censored")
                by_arm_seed[(arm, seed)][1] += row["gate"]["steps_lived"]
        beats = ties = losses = 0
        for seed in D.founder_seeds(p):
            ref = tuple(by_arm_seed[("reference", seed)])
            cand = tuple(by_arm_seed[("candidate", seed)])
            if cand > ref:
                beats += 1
            elif cand == ref:
                ties += 1
            else:
                losses += 1
        matched[str(p)] = {
            "candidate_founders_better_than_reference": beats,
            "ties": ties,
            "candidate_founders_worse_than_reference": losses,
        }

    report = {
        "schema": SELECTION_AGGREGATE,
        "status": "COMPLETE_SELECTION_READY_FOR_VALIDATION",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_manifest()["sha256"],
        "execution_sha": execution_sha,
        "source_sha256": source_pin,
        "selected": selected,
        "rankings": rankings,
        "matched_g0_descriptive": matched,
        "world_lock": True,
        "observer_valid": observer_valid,
        "no_cognitive_shortfall": no_shortfall,
    }
    report["sha256"] = digest_json(report)
    return report


def _replay_equal(first, second):
    keys = (
        "trace_head", "evidence_head", "terminal",
        "steps_lived", "world_sha256")
    return (
        all(first["summary"][key] == second["summary"][key] for key in keys)
        and first["summary"]["paid"] == second["summary"]["paid"]
        and first["summary"]["inactive_steps"]
        == second["summary"]["inactive_steps"])


def run_validation_shard(population, arm, selection_aggregate, output_dir, *,
                         expected_sha, expected_protocol):
    validate_launch(expected_sha, expected_protocol)
    population = _validate_population(population)
    arm = _validation_arm(arm)
    if selection_aggregate.get("execution_sha") != expected_sha:
        raise ValueError("selection aggregate came from different source")
    output_dir = Path(output_dir)
    cases = validation_cases(population, arm, selection_aggregate)
    selected_key = "reference" if arm == "reference" else "candidate"
    selected = _selected_for(selection_aggregate, selected_key, population)
    rank0 = selected[0]
    rows = []
    replay_rows = []
    source_pin = selection_aggregate["source_sha256"]
    try:
        for case in cases:
            result, observed_source = _run_case(
                case, output_dir, source_pin)
            if observed_source != source_pin:
                raise ValueError("validation source differs from selection")
            summary = result["summary"]
            revision = result["revision"]
            rows.append({
                "gate": {
                    "arm": arm,
                    "population": population,
                    "family": case["family"],
                    "world_index": case["world_index"],
                    "founder_seed": case["founder_seed"],
                    "genome_digest": case["genome_digest"],
                    "terminal": summary["terminal"],
                    "steps_lived": summary["steps_lived"],
                    "revision_status": (
                        revision["status"] if revision is not None else None),
                    "revision_latency": (
                        revision["latency_from_available_steps"]
                        if revision is not None else None),
                },
                "world_seed": case["world_seed"],
                "life_seed": case["life_seed"],
                "world_sha256": summary["world_sha256"],
                "source_sha256": summary["source_sha256"],
                "competition_steps": summary["competition_steps"],
                "cognitive_shortfall_steps":
                    summary["cognitive_shortfall_steps"],
                "paid": summary["paid"],
                "inactive_steps": summary["inactive_steps"],
                "frontier_information": summary["frontier_information"],
                "revision": revision,
                "original": result["original"],
            })

            if case["founder_seed"] == rank0:
                replay, replay_source = _run_case(
                    case, output_dir, source_pin, replay=True)
                if replay_source != source_pin:
                    raise ValueError("replay source drift")
                equal = _replay_equal(result, replay)
                replay_rows.append({
                    "world_index": case["world_index"],
                    "founder_seed": rank0,
                    "identical": equal,
                    "original": replay["original"],
                })
                if not equal:
                    raise ValueError("rank-0 exact replay mismatch")
    except Exception as exc:
        failure = {
            "schema": VALIDATION_SHARD,
            "status": "ENGINEERING_FAILURE_NOT_A_DEATH",
            "population": population,
            "arm": arm,
            "completed_main": len(rows),
            "expected_main": len(cases),
            "completed_replays": len(replay_rows),
            "expected_replays": len(D.FAMILIES) * D.REPEATS,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        _write_json(output_dir / "FAILURE.json", failure)
        raise

    report = {
        "schema": VALIDATION_SHARD,
        "status": "COMPLETE",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_manifest()["sha256"],
        "execution_sha": expected_sha,
        "source_sha256": source_pin,
        "selection_sha256": selection_aggregate["sha256"],
        "population": population,
        "arm": arm,
        "selected_seeds": list(selected),
        "expected_main_lives": len(cases),
        "completed_main_lives": len(rows),
        "expected_replays": len(D.FAMILIES) * D.REPEATS,
        "completed_replays": len(replay_rows),
        "receipts": rows,
        "rank0_replays": replay_rows,
    }
    _write_json(output_dir / "validation-shard.json", report)
    return report


def aggregate_validation(selection_aggregate, shards):
    expected = {
        (p, arm)
        for p in range(D.POPULATIONS)
        for arm in D.ARMS
    }
    by_key, execution_sha, source_pin = _complete_shards(
        shards, VALIDATION_SHARD, expected)
    if (selection_aggregate.get("schema") != SELECTION_AGGREGATE
            or selection_aggregate.get("sha256")
            != digest_json({
                k: v for k, v in selection_aggregate.items()
                if k != "sha256"
            })
            or selection_aggregate.get("protocol_sha256")
            != protocol_manifest()["sha256"]
            or selection_aggregate.get("execution_sha") != execution_sha
            or selection_aggregate.get("source_sha256") != source_pin):
        raise ValueError("selection aggregate source/digest mismatch")

    selected_reference = {
        p: tuple(selection_aggregate["selected"]["reference"][str(p)])
        for p in range(D.POPULATIONS)
    }
    selected_candidate = {
        p: tuple(selection_aggregate["selected"]["candidate"][str(p)])
        for p in range(D.POPULATIONS)
    }
    gate_rows = []
    world_hashes = {}
    observer_valid = True
    no_shortfall = True
    replay_identical = True

    for p in range(D.POPULATIONS):
        for arm in D.ARMS:
            shard = by_key[(p, arm)]
            if shard["selection_sha256"] != selection_aggregate["sha256"]:
                raise ValueError("validation shard used different selected set")
            expected_selected = (
                selected_reference[p] if arm == "reference"
                else selected_candidate[p])
            if tuple(shard["selected_seeds"]) != expected_selected:
                raise ValueError("validation selected-seed order drift")
            if (shard["completed_main_lives"]
                    != D.KEEP * len(D.FAMILIES) * D.REPEATS
                    or shard["completed_replays"]
                    != len(D.FAMILIES) * D.REPEATS):
                raise ValueError("incomplete validation shard")
            for row in shard["receipts"]:
                gate_rows.append(row["gate"])
                key = (p, row["gate"]["world_index"])
                world_hashes.setdefault(key, set()).add(row["world_sha256"])
                observer_valid &= (
                    row["competition_steps"]
                    == row["gate"]["steps_lived"])
                no_shortfall &= row["cognitive_shortfall_steps"] == 0
            replay_identical &= all(
                row["identical"] for row in shard["rank0_replays"])

    world_lock = all(len(values) == 1 for values in world_hashes.values())
    custody = {
        "source_lock": True,
        "world_lock": world_lock,
        "observer_valid": observer_valid,
        "no_cognitive_shortfall": no_shortfall,
        "rank0_replay_identical": replay_identical,
    }
    gate = D.analyze_gate(
        selected_reference, selected_candidate, gate_rows, custody)

    # Compact actual-cost descriptors, never a causal mediation claim.
    arm_cost = {}
    for arm in D.ARMS:
        rows = [
            row for (p, a), shard in by_key.items() if a == arm
            for row in shard["receipts"]
        ]
        steps = sum(row["gate"]["steps_lived"] for row in rows)
        paid_energy = fsum(row["paid"]["energy"] for row in rows)
        paid_vigilance = fsum(row["paid"]["vigilance"] for row in rows)
        inactive = sum(row["inactive_steps"] for row in rows)
        arm_cost[arm] = {
            "lives": len(rows),
            "lived_steps": steps,
            "paid_energy": paid_energy,
            "paid_vigilance": paid_vigilance,
            "paid_energy_per_lived_step":
                paid_energy / steps if steps else None,
            "paid_vigilance_per_lived_step":
                paid_vigilance / steps if steps else None,
            "inactive_steps": inactive,
            "inactive_fraction": inactive / steps if steps else None,
        }

    report = {
        "schema": VALIDATION_AGGREGATE,
        "status": "COMPLETE_GATE_ARITHMETIC",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_manifest()["sha256"],
        "execution_sha": execution_sha,
        "source_sha256": source_pin,
        "selection_sha256": selection_aggregate["sha256"],
        "custody": custody,
        "gate": gate,
        "validation_cost_descriptive": arm_cost,
        "scientific_verdict": (
            "PASS_FROZEN_STAGE1_OMEGA_GATE"
            if gate["would_pass_if_receipts_are_authentic"]
            else "FAIL_FROZEN_STAGE1_OMEGA_GATE"),
        "scope": (
            "F0_ADR0015_STAGE1_OMEGA_GATE_NOT_GENERAL_I3_GO"),
    }
    report["sha256"] = digest_json(report)
    return report


def _read_json(path):
    return json.loads(Path(path).read_text())


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("plan")
    show.add_argument("--json", action="store_true")

    sel = sub.add_parser("selection-shard")
    sel.add_argument("population", type=int)
    sel.add_argument("arm", choices=("reference", "candidate"))
    sel.add_argument("output")
    sel.add_argument("--expected-sha", required=True)
    sel.add_argument("--expected-protocol", required=True)

    val = sub.add_parser("validation-shard")
    val.add_argument("population", type=int)
    val.add_argument("arm", choices=D.ARMS)
    val.add_argument("selection_json")
    val.add_argument("output")
    val.add_argument("--expected-sha", required=True)
    val.add_argument("--expected-protocol", required=True)

    args = parser.parse_args(argv)
    if args.command == "plan":
        value = protocol_manifest()
        print(json.dumps(value, indent=2 if args.json else None, sort_keys=True))
        return 0
    if args.command == "selection-shard":
        run_selection_shard(
            args.population, args.arm, args.output,
            expected_sha=args.expected_sha,
            expected_protocol=args.expected_protocol)
        return 0
    if args.command == "validation-shard":
        run_validation_shard(
            args.population, args.arm, _read_json(args.selection_json),
            args.output, expected_sha=args.expected_sha,
            expected_protocol=args.expected_protocol)
        return 0
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
