"""Stage8-E2 full G0/G1/G2 native *technical* transport, no science.

Source-bound, one-shot and original-gzip gated. No run starts on import or
during the pure allocation plan. For a real full technical rehearsal, first
publish the plan bytes and digest *before* the first G0 native birth. A failed
or partial campaign is terminal for its root (NO_RETRY).

The two separately sealed Python technical runs are NOT scientific outcomes.
A third prospective science allocation is a different, unimplemented gate.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import sys

from i3.lab import stage6_light_native_g0_transport as AUTH
from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8e2_native_preflight as N
from i3.lab import stage8e2_native_original_generation as LIVE
from i3.lab import stage8e2_independent_original_audit as ORIGINAL
from i3.lab import stage8e2_parent_fitness_gate as FITNESS
from i3.lab import stage8e2_lineage_preflight as LINEAGE
from i3.lab import stage8e2_independent_parentage_audit as PARENTAGE
from i3.lab import stage8e2_g2_factorial_genomes as GAMMA
from i3.modules import genome as G

PLAN_SCHEMA = "i3-stage8e2-full-native-technical-preexposure/v0"
PHASES = (
    "G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
    "SELECT_G2", "G2", "SEAL_G2", "R_FINAL",
)
TECH_PASS = "STAGE8E2_FULL_NATIVE_TECHNICAL_ORIGINALS_SEALED_NO_SCIENCE"
FAIL = "TECHNICAL_NO_VERDICT_NO_RETRY"
HEXSHA = re.compile(r"[0-9a-f]{64}\Z")
HEXHEAD = re.compile(r"[0-9a-f]{40}\Z")
LIVES_BY_GEN = {0: P.EXPECTED_G0, 1: P.EXPECTED_G1, 2: P.EXPECTED_G2}
MUTATIONS = 2 * 2 * P.POPULATIONS * P.FOUNDERS
METHOD = {
    "schema": "i3-stage8e2-gamma-block-technical-method/v0",
    "study": "new_population_F0_only", "population_units": 64,
    "founders_per_population": 24, "world_families": list(P.WORLD_FAMILIES),
    "repetitions_per_family": 2, "horizon": 400,
    "generation_g0": "common_independent_v4_founders",
    "generation_g1": "persistence_ranked_S_vs_blind_multiplicity_matched_M",
    "generation_g2": "S_sham_M_sham_S_swap_M_swap_reciprocal_gamma123",
    "primary_future_estimand": "(S_sham-M_sham)-(S_swap-M_swap)",
    "primary_future_population_units": 64,
    "two_sided_alpha": 0.025, "two_sided_t_critical_df63": 2.2962367715148795,
    "individual_motors": "reference_P1.3_funded_v2_no_forced_action",
    "original_per_life_gzip_sha256_and_raw_sha256": True,
    "G1_requires_sealed_audited_G0_originals": True,
    "G2_requires_sealed_audited_G1_originals": True,
    "science_results_from_technical_runs": False,
    "no_retry": True,
}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _write_new(path: Path, value: object) -> str:
    raw = _canonical(value)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return sha256(raw).hexdigest()


def _outside_repo(path: str) -> None:
    checkout = Path(__file__).resolve().parents[3]
    if (type(path) is not str or not path.startswith("/")
            or str(Path(path).resolve()) != path
            or Path(path).resolve().is_relative_to(checkout.resolve())):
        raise PermissionError("native archive must be canonical and outside repository")


def _founders(root: str) -> tuple[dict, list]:
    founders = {}
    rows = []
    for p in range(P.POPULATIONS):
        for slot in range(P.FOUNDERS):
            seed = N._seed(root, "founder", "founder", p, slot)
            rows.append({"population": p, "slot": slot, "genome_seed": seed})
            founders[p, "shared", slot] = G.generation_zero(seed)
    if len(founders) != 1536 or len({r["genome_seed"] for r in rows}) != 1536:
        raise ValueError("duplicate or incomplete v4 founder allocation")
    return founders, rows


def make_plan(root: str, git_head: str, source_sha256: str,
              archive_root: str) -> dict:
    """Pure allocation, no native birth, no World actor, no scientific result."""
    P._root(root)
    if (type(git_head) is not str or not HEXHEAD.fullmatch(git_head)
            or type(source_sha256) is not str or not HEXSHA.fullmatch(source_sha256)):
        raise ValueError("exact Git and Python source pins required")
    _outside_repo(archive_root)
    method_sha, owner_direction_sha = AUTH._pins()
    preflight = N.verify_native_preflight(root)
    founder_rows = [
        [p, slot, N._seed(root, "founder", "founder", p, slot)]
        for p in range(P.POPULATIONS) for slot in range(P.FOUNDERS)
    ]
    mutate_rows, draw_rows, permutation_rows = [], [], []
    for generation in (1, 2):
        for p in range(P.POPULATIONS):
            permutation_rows.append(
                [generation, p, P.derive(root, "parent-permutation", p, generation)])
            for arm in P.G1_ARMS:
                for slot in range(P.FOUNDERS):
                    mutate_rows.append([generation, p, arm, slot,
                        LINEAGE._seed(root, "mutation", p, generation, arm, slot)])
                    if arm == "S":
                        draw_rows.append([generation, p, slot,
                            LINEAGE._seed(root, "selection", p, generation, arm, slot)])
    native_values = [r[2] for r in founder_rows]
    native_values.extend(r[4] for r in mutate_rows)
    native_values.extend(r[3] for r in draw_rows)
    if (len(founder_rows) != 1536 or len(mutate_rows) != MUTATIONS
            or len(draw_rows) != MUTATIONS // 2 or len(permutation_rows) != 128
            or len(native_values) != len(set(native_values))):
        raise ValueError("missing/colliding parent, mutation, founder or draw entropy")
    payload = {
        "schema": PLAN_SCHEMA, "status": "TECHNICAL_PREEXPOSURE_NOT_RUN",
        "scientific_admission": False, "no_retry": True,
        "source_git_head": git_head, "source_files_sha256": source_sha256,
        "root_hex": root, "archive_root": archive_root,
        "owner_direction_sha256": owner_direction_sha,
        "historical_method_sha256": method_sha,
        "frozen_method": METHOD, "frozen_method_sha256": _digest(METHOD),
        "native_preflight": preflight,
        "g2_heldout_worlds_sha256": _digest(preflight["g2_worldspecs"]),
        "founder_allocation_sha256": _digest(founder_rows),
        "mutation_allocation_sha256": _digest(mutate_rows),
        "selection_allocation_sha256": _digest(draw_rows),
        "permutation_allocation_sha256": _digest(permutation_rows),
        "founders": len(founder_rows),
        "native_worldspecs": preflight["all_worldspec_count"],
        "planned_mutations": MUTATIONS, "planned_lives": P.EXPECTED_TOTAL,
        "planned_lives_by_generation": [LIVES_BY_GEN[g] for g in range(3)],
        "planned_original_gzip": P.EXPECTED_TOTAL,
        "parental_original_scores_only": True, "technical_outcomes_not_science": True,
        "science_verdict_before_exposure": "NOT_ISSUED",
    }
    payload["allocation_sha256"] = _digest(payload)
    return payload


def verify_plan(plan: object) -> dict:
    if (type(plan) is not dict or plan.get("schema") != PLAN_SCHEMA
            or plan.get("status") != "TECHNICAL_PREEXPOSURE_NOT_RUN"
            or plan.get("no_retry") is not True
            or plan.get("scientific_admission") is not False
            or plan.get("science_verdict_before_exposure") != "NOT_ISSUED"):
        raise PermissionError("foreign, scientific or previously exposed plan")
    expected = make_plan(plan.get("root_hex"), plan.get("source_git_head"),
                         plan.get("source_files_sha256"), plan.get("archive_root"))
    if _canonical(expected) != _canonical(plan):
        raise PermissionError("source, physical worlds, genetic entropy or method drift")
    return plan


def _append_phase(root: Path, phase: str, artifact: Path, previous: list) -> list:
    if phase != PHASES[len(previous)] or not artifact.is_file():
        raise ValueError("incomplete or reordered Stage8-E2 phase")
    if artifact.is_symlink():
        raise ValueError("phase proof cannot be a symlink")
    row = {
        "phase": phase, "sequence": len(previous),
        "artifact": str(artifact.relative_to(root)),
        "file_sha256": sha256(artifact.read_bytes()).hexdigest(),
        "previous_chain_sha256": previous[-1]["chain_sha256"] if previous else None,
    }
    row["chain_sha256"] = _digest(row)
    with (root / "PHASES.jsonl").open("ab") as handle:
        handle.write(_canonical(row) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    previous.append(row)
    return previous


def _records(genomes: dict) -> list[dict]:
    return [{"population": p, "arm": arm, "slot": slot,
             "genome": genome, "genome_sha256": G.digest(genome)}
            for (p, arm, slot), genome in sorted(genomes.items())]


def _assert_technical_environment(plan: dict) -> None:
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        raise PermissionError("only CPython 3.11/3.12 technical cohort runner")
    LIVE._check_source(plan["source_git_head"], plan["source_files_sha256"])


def run_technical(plan_path: str, expected_plan_sha256: str) -> dict:
    """Execute a full one-shot TECHNICAL 64,512-life cohort, no science.

    Caller MUST first externally publish the plan hash before first birth.
    A fresh archive claim is created atomically, never overwritten or retried.
    """
    path = Path(plan_path)
    if (type(plan_path) is not str or not path.is_absolute()
            or path.is_symlink() or not path.is_file()
            or type(expected_plan_sha256) is not str
            or not HEXSHA.fullmatch(expected_plan_sha256)):
        raise PermissionError("missing prior immutable preexposure plan receipt")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected_plan_sha256:
        raise PermissionError("plan bytes differ from prepublished SHA256")
    plan = verify_plan(json.loads(raw))
    if raw != _canonical(plan):
        raise PermissionError("published preexposure plan must use canonical bytes")
    if plan_path == plan["archive_root"]:
        raise PermissionError("plan source must be outside native archive")
    _assert_technical_environment(plan)
    destination = Path(plan["archive_root"])
    if path.resolve().is_relative_to(destination.resolve()):
        raise PermissionError("preexposure plan cannot be inside output archive")
    if not destination.parent.is_dir():
        raise PermissionError("archive parent must already exist")
    destination.mkdir()  # Irreversible claim, never exist_ok
    _write_new(destination / "FROZEN_PLAN.json", plan)
    _write_new(destination / "CLAIM.json", {
        "schema": PLAN_SCHEMA + "/claim",
        "preexposure_file_sha256": expected_plan_sha256,
        "plan_sha256": plan["allocation_sha256"],
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
        "source_git_head": plan["source_git_head"],
        "scientific_admission": False,
    })
    phases = []
    totals = []
    genomes, founders = _founders(plan["root_hex"])
    _write_new(destination / "FOUNDERS.json", founders)
    try:
        for g in (0, 1, 2):
            cases = LIVE.generation_cases(plan["root_hex"], g, genomes,
                                          plan["source_files_sha256"])
            receipt = LIVE.execute_technical_generation(
                root=plan["root_hex"], generation=g, genomes=genomes,
                source_git_head=plan["source_git_head"],
                source_files_sha256=plan["source_files_sha256"],
                preflight=plan["native_preflight"],
                custody_dir=str(destination / f"PHYSICAL_G{g}"),
                published_plan_path=plan_path,
                published_plan_file_sha256=expected_plan_sha256,
            )
            gen_dir = destination / f"PHYSICAL_G{g}"
            phases = _append_phase(destination, f"G{g}", gen_dir / "RECEIPT.json", phases)
            original = ORIGINAL.audit_original_generation(
                gen_dir / f"G{g}", cases,
                source_pin=plan["source_files_sha256"],
                source_head=plan["source_git_head"], protocol=LIVE.PROTOCOL,
                generation=g,
            )
            if (receipt["manifest_sha256"] != original["original_manifest_sha256"]
                    or receipt["original_lives"] != LIVES_BY_GEN[g]
                    or original["original_lives_verified"] != LIVES_BY_GEN[g]):
                raise ValueError("incomplete or conflicting original-level generation")
            seal_path = destination / f"SEAL_G{g}.json"
            _write_new(seal_path, {
                "schema": PLAN_SCHEMA + "/generation-seal",
                "generation": g, "original_manifest_sha256": receipt["manifest_sha256"],
                "independent_original_audit_sha256": _digest({
                    k: v for k, v in original.items() if k != "six_life_rows"}),
                "verified_original_lives": original["original_lives_verified"],
                "source_git_head": plan["source_git_head"],
                "preexposure_allocation_sha256": plan["allocation_sha256"],
            })
            phases = _append_phase(destination, f"SEAL_G{g}", seal_path, phases)
            totals.append({"generation": g, "original_lives": original["original_lives_verified"],
                           "manifest_sha256": original["original_manifest_sha256"]})
            if g < 2:
                # The ONLY parent fitness source is the independently verified
                # original gzip lives. No values from upcoming G1/G2 are read.
                scores = FITNESS.summarize_authenticated_lives(
                    original["six_life_rows"], g)
                next_g = g + 1
                base, draws = LINEAGE.make_descendants(
                    plan["root_hex"], next_g, genomes, scores,
                    original["original_manifest_sha256"])
                independent = PARENTAGE.verify_parentage(
                    plan["root_hex"], next_g, genomes, scores, base, draws,
                    original["original_manifest_sha256"])
                if independent["mutations_reconstructed"] != 3072:
                    raise ValueError("uncertified S/M hereditary reconstruction")
                if next_g == 2:
                    pairs = {(p, slot): {"S": base[p, "S", slot],
                                         "M": base[p, "M", slot]}
                             for p in range(P.POPULATIONS)
                             for slot in range(P.FOUNDERS)}
                    children = GAMMA.assemble_g2(pairs)
                    check = GAMMA.independent_genotype_audit(pairs, children)
                    if check["g2_genome_copies"] != 6144:
                        raise ValueError("incomplete gamma factorial")
                else:
                    children = base
                    check = None
                selected_path = destination / f"SELECT_G{next_g}.json"
                _write_new(selected_path, {
                    "schema": PLAN_SCHEMA + "/selection",
                    "generation": next_g,
                    "prior_original_manifest_sha256": original["original_manifest_sha256"],
                    "prior_generation_seal_sha256": sha256(seal_path.read_bytes()).hexdigest(),
                    "fitness_from_originals_sha256": _digest(
                        [[p, arm, slot, v[0], v[1]]
                         for (p, arm, slot), v in sorted(scores.items())]),
                    "independent_parentage": independent,
                    "parent_draws": draws,
                    "mutated_descendants": _records(base),
                    "gamma_four_arm_check": check,
                    "live_generation_genomes": _records(children),
                    "scientific_admission": False,
                })
                phases = _append_phase(destination, f"SELECT_G{next_g}",
                                       selected_path, phases)
                genomes = children
        if sum(x["original_lives"] for x in totals) != P.EXPECTED_TOTAL:
            raise ValueError("incomplete native three-generation originals")
        final_path = destination / "R_FINAL_ENGINEERING.json"
        _write_new(final_path, {
            "schema": PLAN_SCHEMA + "/final-technical",
            "status": TECH_PASS, "original_lives": P.EXPECTED_TOTAL,
            "g0_g1_g2_original_manifest_sha256": totals,
            "independent_parentage_reconstructed": MUTATIONS,
            "science_result_disclosed": False,
            "scientific_admission": False, "no_retry": True,
        })
        phases = _append_phase(destination, "R_FINAL", final_path, phases)
        if len(phases) != len(PHASES):
            raise RuntimeError("nine required Stage8-E2 phases missing")
        result = {
            "schema": PLAN_SCHEMA + "/technical-receipt",
            "status": TECH_PASS,
            "source_git_head": plan["source_git_head"],
            "source_files_sha256": plan["source_files_sha256"],
            "python_version": ".".join(map(str, sys.version_info[:2])),
            "allocation_sha256": plan["allocation_sha256"],
            "root_commitment_sha256": plan["native_preflight"]["root_commitment_sha256"],
            "g2_heldout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
            "archive_root": str(destination),
            "original_lives_audited": P.EXPECTED_TOTAL,
            "mutations_reconstructed": MUTATIONS,
            "phase_count": len(phases),
            "phase_chain_sha256": phases[-1]["chain_sha256"],
            "scientific_admission": False, "no_retry": True,
        }
        _write_new(destination / "TECHNICAL_RECEIPT.json", result)
        return result
    except BaseException as exc:
        _write_new(destination / "FAILURE.json", {
            "schema": PLAN_SCHEMA + "/failure",
            "status": FAIL, "phase_index": len(phases),
            "error_type": type(exc).__name__,
            "no_retry": True, "scientific_admission": False,
        })
        raise


def main() -> None:
    """Explicit manual engineering entrypoint; never a background workflow."""
    if len(sys.argv) == 6 and sys.argv[1] == "allocate":
        _, _, git_head, source_sha, archive_root, plan_path = sys.argv
        candidate = make_plan(secrets.token_hex(32), git_head, source_sha, archive_root)
        digest = _write_new(Path(plan_path), candidate)
        print(json.dumps({
            "preexposure_file_sha256": digest,
            "allocation_sha256": candidate["allocation_sha256"],
            "technical_only": True, "new_lives": 0,
        }, sort_keys=True))
    elif len(sys.argv) == 4 and sys.argv[1] == "run":
        result = run_technical(sys.argv[2], sys.argv[3])
        print(json.dumps(result, sort_keys=True))
    else:
        raise SystemExit(
            "usage: allocate GIT_HEAD SOURCE_SHA ABS_ARCHIVE_DIR ABS_PLAN_PATH"
            " | run ABS_PLAN_PATH PUBLISHED_PLAN_FILE_SHA256"
        )


if __name__ == "__main__":
    main()
