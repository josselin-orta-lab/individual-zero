"""Read-only independent Stage7 persistence audit from immutable native gzip lives.

No import from i3, no WorldSpec creation, no engine or mutation calls. This
verifier can be run on downloaded *unmodified* scientific archive contents
after the one-shot Stage7 study has completed. It reads all 11,520 original
lives and recalculates the prespecified population-level outcome independently
of the experiment's in-process reducer.

This checks SHA256 custody, recorded native provenance, within-generation
pairing, trace length, steps lived, censoring, settled energy/vigilance and
the frozen G2 sign result. It does NOT independently replay motor physics,
confirm OS entropy or prove populations are statistically independent.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import re

NPOP, NSLOTS, HORIZON = 16, 24, 400
FAMILIES = ("stable", "depletion", "pulse")
ARMS = ("selected", "random_parent")
PHASES = ("G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
          "SELECT_G2", "G2", "SEAL_G2", "R_FINAL")
PLAN_SCHEMA = "i3-stage7-heritable-persistence-prospective-science-plan/v1"
REPORT_SCHEMA = "i3-stage7-internal-prospective-persistence-result/v1"
STATUS_POS = "PERSISTENCE_G2_ADVANTAGE_REPRODUCIBLE_F0"
STATUS_NEG = "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0"
PATH_PATTERN = re.compile(r"life-[0-9]{3,5}\.json\.gz\Z")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_bytes())


def _hash(value: object) -> bool:
    return type(value) is str and HASH_PATTERN.fullmatch(value) is not None


def _same_float(actual, expected: float) -> bool:
    return (type(actual) in (int, float) and
            math.isfinite(actual) and
            math.isclose(actual, expected, abs_tol=1e-10, rel_tol=0))


def validate_plan(plan: dict) -> dict:
    if (type(plan) is not dict or plan.get("schema") != PLAN_SCHEMA or
            plan.get("scientific_admission") is not True or
            plan.get("planned_lives") != 11520 or
            plan.get("planned_worlds") != 288 or
            plan.get("preexposure_scientific_verdict") != "NOT_ISSUED" or
            plan.get("source_of_scope") !=
            "ADR-0022_DIRECT_OWNER_REQUEST_2026-11-16"):
        raise ValueError("foreign or incomplete Stage7 prospective scientific plan")
    plan_digest = plan.get("allocation_sha256")
    if (not _hash(plan_digest) or
            digest(canonical({k: v for k, v in plan.items()
                              if k != "allocation_sha256"})) != plan_digest):
        raise ValueError("prospective allocation has changed after publication")
    method = plan.get("frozen_method", {})
    if (method.get("primary_sign_threshold") != 13 or
            method.get("primary_generation") != 2 or
            method.get("horizon") != 400 or
            method.get("primary_direction") != "positive_only" or
            method.get("one_sided_exact_tail") !=
            {"numerator": 697, "denominator": 65536} or
            method.get("population_is_only_independent_unit") is not True or
            method.get("G0_replayed_across_arms") is not False or
            method.get("cross_generation_raw_changes_are_environment_confoundable")
            is not True):
        raise ValueError("frozen Stage7 primary or G0/G1 interpretation changed")
    if not _hash(plan.get("source_files_sha256")):
        raise ValueError("no frozen source-map digest")
    worlds = plan.get("worlds")
    if type(worlds) is not list or len(worlds) != 288:
        raise ValueError("world allocation missing")
    lookup = {}
    for w in worlds:
        key = (w.get("population"), w.get("generation"),
               w.get("family"), w.get("repeat"))
        if (type(w.get("population")) is not int or
                type(w.get("generation")) is not int or
                type(w.get("repeat")) is not int or
                not 0 <= w["population"] < 16 or
                w["generation"] not in (0, 1, 2) or
                w["family"] not in FAMILIES or
                w["repeat"] not in (0, 1) or
                key in lookup):
            raise ValueError("missing, duplicated or foreign World opportunity")
        lookup[key] = w
    if (set(lookup) != {(p, g, f, r) for p in range(16)
                        for g in range(3) for f in FAMILIES
                        for r in (0, 1)}):
        raise ValueError("not 288 unique population/geography opportunities")
    for name in ("world_index", "world_seed", "life_seed"):
        seeds = [w.get(name) for w in worlds]
        if (any(type(s) is not int for s in seeds) or
                len(set(seeds)) != len(seeds)):
            raise ValueError("duplicate or malformed prospective World seed namespace")
    return lookup


def _identity_check(identity: dict, generation: int, plan: dict,
                    worlds: dict) -> tuple:
    if type(identity) is not dict or set(identity) != {
            "population", "generation", "arm", "slot", "family", "repeat",
            "logical_world", "world_seed", "life_seed", "genome_sha256",
            "world_sha256", "source_sha256"}:
        raise ValueError("native life identity ABI differs from prospective plan")
    p, g, arm, slot = (identity[k] for k in
                       ("population", "generation", "arm", "slot"))
    f, r = identity["family"], identity["repeat"]
    expected_arms = ("shared",) if generation == 0 else ARMS
    if (type(p) is not int or type(g) is not int or
            type(slot) is not int or type(r) is not int or
            not 0 <= p < 16 or g != generation or
            arm not in expected_arms or not 0 <= slot < 24 or
            f not in FAMILIES or r not in (0, 1) or
            not _hash(identity["genome_sha256"]) or
            not _hash(identity["world_sha256"]) or
            identity["source_sha256"] != plan["source_files_sha256"]):
        raise ValueError("cross-population or foreign source/genotype identity")
    world = worlds[p, generation, f, r]
    if any(identity[k] != world[k] for k in
           ("logical_world", "world_seed", "life_seed")):
        raise ValueError("live World or life seed differs from frozen allocation")
    return p, g, arm, slot, f, r


def _life_check(life: dict, identity: dict, plan: dict) -> tuple[int, bool]:
    if type(life) is not dict:
        raise ValueError("missing native life object")
    step = life.get("steps_lived")
    terminal = life.get("terminal")
    trace = life.get("trace")
    manifest = life.get("manifest", {})
    source = manifest.get("source", {})
    billing = life.get("cognitive_accounting", {})
    totals = billing.get("totals", {})
    if (type(step) is not int or not 1 <= step <= HORIZON or
            life.get("horizon") != HORIZON or
            terminal not in ("dead", "censored") or
            (terminal == "censored") != (step == HORIZON) or
            type(trace) is not list or len(trace) != step or
            life.get("genome") != identity["genome_sha256"] or
            life.get("life_seed") != identity["life_seed"] or
            manifest.get("world_sha256") != identity["world_sha256"] or
            manifest.get("protocol") != plan["protocol"] or
            manifest.get("execution_model") != "i3-funded-v2" or
            source.get("sha256") != plan["source_files_sha256"] or
            source.get("git_head") != plan["source_git_head"] or
            source.get("working_tree_dirty") is not False or
            type(life.get("death_causes")) is not list or
            bool(life["death_causes"]) != (terminal == "dead") or
            billing.get("status") != "SETTLED_FOR_DECLARED_WORK" or
            billing.get("shortfall_steps") != 0 or
            set(totals) != {"energy", "vigilance"} or
            any(type(totals[ch]) is not dict or
                type(totals[ch].get("unpaid")) not in (int, float) or
                not math.isfinite(totals[ch]["unpaid"]) or
                totals[ch]["unpaid"] > 1e-12
                for ch in ("energy", "vigilance"))):
        raise ValueError("native life, body, funding, source or horizon mismatch")
    return step, terminal == "censored"


def scan_sealed_generation(root: Path, generation: int, plan: dict,
                           worlds: dict):
    """Stream and verify each compressed original independently, once."""
    folder = root / f"G{generation}"
    data = (folder / "MANIFEST.json").read_bytes()
    if digest(data) != (folder / "MANIFEST.sha256").read_text().strip():
        raise ValueError("generation manifest SHA mismatch")
    manifest = json.loads(data)
    expected_count = 2304 if generation == 0 else 4608
    if (manifest.get("status") != "GENERATED" or
            manifest.get("planned") != expected_count or
            manifest.get("generated") != expected_count or
            len(manifest.get("files", [])) != expected_count or
            manifest.get("failure") is not None):
        raise ValueError("generation incomplete, failed or status altered")
    counts = defaultdict(lambda: [0, 0, 0])  # lives, steps, censored
    seen = set()
    genomes, context_worlds = {}, {}
    for i, entry in enumerate(manifest["files"]):
        file = entry.get("file")
        if (type(file) is not str or not PATH_PATTERN.fullmatch(file) or
                file != f"life-{i:03d}.json.gz" or
                not _hash(entry.get("sha256")) or
                not _hash(entry.get("uncompressed_sha256"))):
            raise ValueError("unsafe, reordered or invalid original path")
        identity = entry["identity"]
        key = _identity_check(identity, generation, plan, worlds)
        if key in seen:
            raise ValueError("original life coordinate duplicated")
        seen.add(key)
        genotype_key = key[:4]
        if genotype_key in genomes and genomes[genotype_key] != identity["genome_sha256"]:
            raise ValueError("one individual has multiple genotypes")
        genomes[genotype_key] = identity["genome_sha256"]
        ctx_key = (key[0], key[1], key[4], key[5])
        if (ctx_key in context_worlds and
                context_worlds[ctx_key] != identity["world_sha256"]):
            raise ValueError("arms were not paired on identical WorldSpec")
        context_worlds[ctx_key] = identity["world_sha256"]
        compressed = (folder / file).read_bytes()
        if digest(compressed) != entry["sha256"]:
            raise ValueError("gzip native original SHA mismatch")
        raw = gzip.decompress(compressed)
        if digest(raw) != entry["uncompressed_sha256"]:
            raise ValueError("uncompressed original SHA mismatch")
        payload = json.loads(raw)
        if payload.get("identity") != identity:
            raise ValueError("sealed original identity disagrees with manifest")
        lived, survived = _life_check(payload["life"], identity, plan)
        row = counts[(key[0], key[2])]
        row[0] += 1
        row[1] += lived
        row[2] += survived
    expected = {(p, arm) for p in range(16)
                for arm in (("shared",) if generation == 0 else ARMS)}
    if set(counts) != expected or any(c[0] != 144 for c in counts.values()):
        raise ValueError("not exactly 144 paired original lives per population and arm")
    expected_keys = {(p, generation, arm, slot, family, repeat)
                     for p in range(16)
                     for arm in (("shared",) if generation == 0 else ARMS)
                     for slot in range(24) for family in FAMILIES
                     for repeat in (0, 1)}
    if seen != expected_keys:
        raise ValueError("missing one or more ecological founder opportunities")
    return {key: {"lives": value[0], "steps": value[1],
                  "censored": value[2]} for key, value in counts.items()}


def _assert_report(result: dict, plan: dict, root: Path, primary: dict):
    if (result.get("schema") != REPORT_SCHEMA or
            result.get("plan_sha256") != plan["allocation_sha256"] or
            result.get("source_git_head") != plan["source_git_head"] or
            result.get("full_original_lives") != 11520 or
            result.get("population_units") != 16 or
            result.get("status") != primary["status"]):
        raise ValueError("reported result is foreign or disagrees with original-life signs")
    analysis = result.get("scientific_analysis", {})
    published = analysis.get("primary", {})
    generations = analysis.get("generation_population_originals")
    if (type(generations) is not list or len(generations) != 16 or
            {row.get("population") for row in generations} != set(range(16))):
        raise ValueError("not all 16 unique population-level generation summaries")
    if (analysis.get("status") != primary["status"] or
            analysis.get("population_unit_count") != 16 or
            analysis.get("primary_positive_threshold") != 13 or
            published.get("positive") != primary["positive"] or
            published.get("negative") != primary["negative"] or
            published.get("zero") != primary["zero"] or
            published.get("threshold_met") is not primary["threshold_met"] or
            not _same_float(published.get("mean_paired_difference_steps"),
                            primary["mean_paired_difference_steps"]) or
            len(published.get("per_population_steps", [])) != 16):
        raise ValueError("frozen G2 analysis not reproduced from sealed originals")
    if any(not _same_float(a,b) for a,b in
           zip(published["per_population_steps"],primary["per_population_steps"])):
        raise ValueError("one or more published population contrasts changed")
    if (result.get("fixed_method") != plan["frozen_method"] or
            not _hash(result.get("full_science_original_sha256")) or
            digest((root / "R_FINAL_PERSISTENCE_SCIENCE.json").read_bytes())
            != result["full_science_original_sha256"]):
        raise ValueError("final original R is not digest-bound to the report")


def primary_from_counts(g2: dict) -> dict:
    expected = {(p, arm) for p in range(16) for arm in ARMS}
    if set(g2) != expected or any(g2[k]["lives"] != 144
                                  for k in expected):
        raise ValueError("incomplete G2 population-level paired originals")
    numerators = [g2[p, "selected"]["steps"] -
                  g2[p, "random_parent"]["steps"] for p in range(16)]
    positive = sum(n > 0 for n in numerators)
    negative = sum(n < 0 for n in numerators)
    passed = positive >= 13 and sum(numerators) > 0
    return {
        "status": (STATUS_POS if passed else STATUS_NEG),
        "positive": positive,
        "negative": negative,
        "zero": 16-positive-negative,
        "threshold_met": passed,
        "per_population_steps": [n/144 for n in numerators],
        "mean_paired_difference_steps": sum(numerators)/(16*144),
    }


def _verify_phases(root: Path, report: dict) -> str:
    chain = (root / "PHASES.jsonl").read_bytes().splitlines()
    if len(chain) != len(PHASES):
        raise ValueError("nine phases not complete")
    last = None
    for i, data in enumerate(chain):
        row = json.loads(data)
        if (row.get("ordinal") != i or row.get("phase") != PHASES[i] or
                row.get("previous_sha256") != last):
            raise ValueError("phase sequence or predecessor invalid")
        h = row.get("chain_sha256")
        if (not _hash(h) or digest(canonical({k: v for k, v in row.items()
                                             if k != "chain_sha256"})) != h):
            raise ValueError("phase chain hash invalid")
        p = row["phase"]
        file = (root / f"{p.split('_')[1] if p.startswith('SEAL_') else p}"
                / "MANIFEST.json" if p.startswith("SEAL_") or
                p in ("G0", "G1", "G2") else
                root / (f"{p}.json" if p != "R_FINAL" else
                        "R_FINAL_PERSISTENCE_SCIENCE.json"))
        if digest(file.read_bytes()) != row["payload_sha256"]:
            raise ValueError("phase SHA does not bind archived payload bytes")
        last = h
    if report.get("phase_chain_sha256") != last:
        raise ValueError("reported chain tip differs from nine native phases")
    return last


def audit_full(plan_file: str, archive_root: str, result_file: str) -> dict:
    """No mutation, no import from the Stage7 runner and no experimental action."""
    plan = read_json(Path(plan_file))
    root = Path(archive_root).resolve()
    if not root.is_dir() or Path(archive_root).is_symlink():
        raise ValueError("missing or symlinked extracted original archive")
    # Offline audits operate on an *extracted copy* of GitHub Actions artifacts.
    # Its current directory is not the runner's original /tmp path.
    # Bind custody through the frozen plan + original CLAIM instead.
    worlds = validate_plan(plan)
    claim = read_json(root / "CLAIM.json")
    if (claim.get("plan_sha256") != plan["allocation_sha256"] or
            claim.get("archive_root") != plan["archive_root"] or
            claim.get("scientific") is not True or
            claim.get("status") != "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL" or
            (root / "FAILURE.json").exists()):
        raise ValueError("science plan not irreversibly claimed or failed")
    report = read_json(Path(result_file))
    seals = {g: scan_sealed_generation(root, g, plan, worlds)
             for g in (0, 1, 2)}
    computed = primary_from_counts(seals[2])
    _assert_report(report, plan, root, computed)
    last = _verify_phases(root, report)
    analysis = report["scientific_analysis"]
    for row in analysis["generation_population_originals"]:
        p = row["population"]
        for g in (0, 1, 2):
            for arm in (("shared",) if g == 0 else ARMS):
                original = seals[g][p, arm]
                presented = row[f"G{g}_{arm}"]
                if (presented["total_steps"] != original["steps"] or
                        presented["survivors_at_horizon"] != original["censored"] or
                        presented["original_lives"] != original["lives"] or
                        not _same_float(presented["mean_steps"],
                                        original["steps"]/144) or
                        not _same_float(presented["horizon_survival_fraction"],
                                        original["censored"]/144)):
                    raise ValueError("G0/G1/G2 reported survival totals differ from originals")
    return {
        "schema": "i3-stage7-independent-read-only-original-reduction/v1",
        "status": "READ_ONLY_REPRODUCTION_OK",
        "scientific_status": computed["status"],
        "source_git_head": plan["source_git_head"],
        "plan_sha256": plan["allocation_sha256"],
        "original_lives_rehashed": 11520,
        "population_units": 16,
        "phase_chain_sha256": last,
        "primary": computed,
        "audit_limit": "NO_MOTOR_REPLAY_NO_INDEPENDENT_ENTROPY_ATTESTATION",
        "new_lives_created": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("science_plan")
    parser.add_argument("original_archive")
    parser.add_argument("science_result")
    args = parser.parse_args()
    print(json.dumps(audit_full(args.science_plan, args.original_archive,
                                args.science_result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
