"""Stage7 native selection experiment: inherited persistence, NOT gene drift.

Separate one-shot prospective protocol from closed Stage6 (2026-11-15).
No native World or organism is created by import, allocate, or verify.
No inherited memories or new action policy: same P1.3 funded-v2 motor.
Only G2 selected-vs-random *paired by population and World* is primary.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import sys

from i3.lab import stage6_light_native_gsr_transport as S
from i3.lab import stage6_light_native_g0_transport as G0

SCHEMA_E = "i3-stage7-heritable-persistence-engineering-plan/v1"
SCHEMA_S = "i3-stage7-heritable-persistence-prospective-science-plan/v1"
PROTOCOL_E = "i3-stage7-persistence-engineering-funded-v2/v1"
PROTOCOL_S = "i3-stage7-persistence-science-funded-v2/v1"
RECEIPT = "i3-stage7-persistence-full-rehearsal/v1"
SCOPE = "F0_NATIVE_INHERITED_PERSISTENCE_NOT_GENERALIZATION"
CUTOFF = 13
FIXED_METHOD = {
    "outcome": "steps_lived_with_terminal_censoring",
    "horizon": 400, "primary_generation": 2,
    "primary_estimand": "within_population_G2_selected_minus_random_mean_steps",
    "primary_direction": "positive_only", "primary_sign_threshold": CUTOFF,
    "null_sign_model": "independent_equiprobable_population_signs_unproven",
    "one_sided_exact_tail": {"numerator": 697, "denominator": 65536},
    "secondary": ["G0_shared_mean_steps",
                  "G1_selected_minus_random_mean_steps",
                  "G2_minus_G1_paired_advantage",
                  "generation_specific_full_horizon_survivor_fraction",
                  "selected_minus_G0_raw_change",
                  "random_parent_minus_G0_raw_change"],
    "zero_differences_count_as_positive": False,
    "population_is_only_independent_unit": True,
    "G0_replayed_across_arms": False,
    "cross_generation_raw_changes_are_environment_confoundable": True,
    "lineage_genotype_only_no_memory_inheritance": True,
    "reference_motor": "P1.3-funded-v2",
    "selection": "sealed_censored_count_then_steps_then_slot_linear_24_to_1",
    "control": "uniform_parent_score_blind",
    "founder_genomes": 384, "world_opportunities": 288,
    "lives_by_generation": [2304, 4608, 4608],
    "world_families": list(S.FAMILIES),
    "world_opportunities_per_genome": 6,
    "mutation_scale": 0.1,
    "archive_all_deaths_censored_and_nulls": True,
}
RUN_STATUSES = {
    "PERSISTENCE_G2_ADVANTAGE_REPRODUCIBLE_F0",
    "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0",
}
REHEARSAL_PASS = "PERSISTENCE_FULL_GSR_ENGINEERING_SEALED_NO_SCIENCE"


def _write_new(path: str | Path, item: dict) -> None:
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(item, f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def _receipt_check(rehearsals: object, head: str, source_hash: str) -> None:
    """Read-only strict two-interpreter technical receipt requirement.

    Equal source + complete archives are required; neither source tests nor
    old 15-Nov Stage6 engineering receipts can be used for new Stage7 science.
    """
    if type(rehearsals) is not dict or set(rehearsals) != {"3.11", "3.12"}:
        raise PermissionError("both NEW full Stage7 engineering rehearsals are required")
    keys = {"schema", "status", "python_version", "source_git_head",
            "source_files_sha256", "allocation_sha256", "archive_root",
            "last_chain_sha256", "result_file_sha256", "lives_archived",
            "worlds_planned", "phase_count", "scientific_admission",
            "no_retry", "workflow_run_id", "job_name",
            "allocation_seed_commitment_sha256"}
    distinct_allocations, distinct_archives, distinct_seeds = set(), set(), set()
    for version in ("3.11", "3.12"):
        r = rehearsals[version]
        if type(r) is not dict or set(r) != keys:
            raise PermissionError("foreign or missing engineering custody fields")
        if (r["schema"] != RECEIPT or r["status"] != REHEARSAL_PASS
                or r["python_version"] != version
                or r["source_git_head"] != head
                or r["source_files_sha256"] != source_hash
                or r["lives_archived"] != 11520
                or r["worlds_planned"] != 288 or r["phase_count"] != 9
                or r["scientific_admission"] is not False
                or r["no_retry"] is not True
                or r["job_name"] != f"engineering-{version}"
                or type(r["workflow_run_id"]) is not int
                or r["workflow_run_id"] <= 0
                or any(type(r[x]) is not str or
                       G0.DIGEST.fullmatch(r[x]) is None
                       for x in ("allocation_sha256", "last_chain_sha256",
                                 "result_file_sha256",
                                 "allocation_seed_commitment_sha256"))
                or type(r["archive_root"]) is not str
                or not r["archive_root"].startswith("/")):
            raise PermissionError("rehearsal is incomplete, foreign, or off-source")
        distinct_allocations.add(r["allocation_sha256"])
        distinct_archives.add(r["archive_root"])
        distinct_seeds.add(r["allocation_seed_commitment_sha256"])
    if (len(distinct_allocations) != 2 or len(distinct_archives) != 2
            or len(distinct_seeds) != 2):
        raise PermissionError("two genuinely different full engineering allocations required")


def make_plan(root_hex: str, source_git_head: str, source_files_sha256: str,
              archive_root: str, *, science: bool = False,
              rehearsals: dict | None = None) -> dict:
    """Pure, deterministic and tamper-checkable plan, before any exposure."""
    if type(science) is not bool:
        raise PermissionError("science mode must be explicit boolean")
    # Fresh 256-bit root is generated outside this function. Domain transform
    # distinguishes these new seeds from the spent Stage6 experiment.
    raw = G0._hex(root_hex, G0.DIGEST, "fresh Stage7 seed root")
    derived = sha256(b"i3-stage7-new-research-root/v1:" +
                     bytes.fromhex(raw)).hexdigest()
    p = S.make_plan(derived, source_git_head, source_files_sha256, archive_root)
    del p["allocation_sha256"]
    if science:
        _receipt_check(rehearsals, source_git_head, source_files_sha256)
        direction = json.loads(G0.DIRECTION.read_bytes())
        allowed = direction["applies_to"]
        required = direction["prospective_execution_requirements"]
        if (allowed.get("scientific_prospective_experiments_authorized") is not True
                or allowed.get("stage6_light_gsr_lineage_exception_adr0017_accepted") is not True
                or required.get("complete_source_exact_engineering_rehearsal_for_stage6_science_required") is not True
                or required.get("run_specific_admission_manifest_required") is not True
                or required.get("all_originals_favorable_adverse_null_required") is not True):
            raise PermissionError("owner prospective research scope is not admissible")
        if archive_root in {r["archive_root"] for r in rehearsals.values()}:
            raise PermissionError("scientific originals cannot overwrite engineering")
        candidate_seed_commitment = S._sha({
            k: p[k] for k in ("root_hex", "worlds", "founders", "draws")})
        if candidate_seed_commitment in {
                r["allocation_seed_commitment_sha256"]
                for r in rehearsals.values()}:
            raise PermissionError("science must have new seeds, not just a new archive name")
    else:
        if rehearsals is not None:
            raise PermissionError("engineering must never accept researcher science evidence")
    p.update({
        "schema": SCHEMA_S if science else SCHEMA_E,
        "protocol": PROTOCOL_S if science else PROTOCOL_E,
        "status": ("PROSPECTIVE_PERSISTENCE_SCIENCE_ALLOCATED_NOT_EXPOSED"
                   if science else
                   "PERSISTENCE_ENGINEERING_ALLOCATED_NOT_EXPOSED"),
        "research_scope": SCOPE,
        "stage7_input_root_hex": raw,
        "scientific_admission": science,
        "frozen_method": FIXED_METHOD,
        "prior_stage6_20261115_observations_not_reused": True,
        "engineering_full_scale_receipts": rehearsals if science else None,
        "preexposure_scientific_verdict": "NOT_ISSUED",
        "source_of_scope": "ADR-0022_DIRECT_OWNER_REQUEST_2026-11-16",
    })
    p["allocation_sha256"] = S._sha(p)
    return p


def verify_plan(plan: object) -> dict:
    if type(plan) is not dict or plan.get("schema") not in (SCHEMA_E, SCHEMA_S):
        raise PermissionError("not a new prospective Stage7 persistence allocation")
    science = plan["schema"] == SCHEMA_S
    expected = make_plan(
        plan.get("stage7_input_root_hex"), plan.get("source_git_head"),
        plan.get("source_files_sha256"), plan.get("archive_root"),
        science=science, rehearsals=plan.get("engineering_full_scale_receipts"))
    if S._canonical(expected) != S._canonical(plan):
        raise PermissionError("altered prospective plan, seed, fixed method or source")
    return plan


def reduce_generation(generation: int, fitness: dict) -> dict:
    """Physical 400-step outcomes, one indiv. averaged across 6 opportunities.

    No individual is treated as an independent replicate in the final test.
    """
    if type(generation) is not int or generation not in (0, 1, 2):
        raise ValueError("invalid generation")
    arms = ("shared",) if generation == 0 else S.ARMS
    expected = {(p, arm, slot) for p in range(S.POPS)
                for arm in arms for slot in range(S.SLOTS)}
    if set(fitness) != expected:
        raise ValueError("not exactly 24 complete genomes per population/arm")
    result = {}
    for p in range(S.POPS):
        for arm in arms:
            values = [fitness[p, arm, s] for s in range(S.SLOTS)]
            if any((type(x) is not tuple or len(x) != 2 or
                    type(x[0]) is not int or type(x[1]) is not int or
                    not 0 <= x[0] <= 6 or
                    not 6 <= x[1] <= 6 * S.HORIZON)
                   for x in values):
                raise ValueError("malformed original survival or lifetime")
            censored_count = sum(x[0] for x in values)
            total_steps = sum(x[1] for x in values)
            result[p, arm] = {
                "original_lives": 144,
                "mean_steps": total_steps / 144,
                "total_steps": total_steps,
                "survivors_at_horizon": censored_count,
                "horizon_survival_fraction": censored_count / 144,
            }
    if len(result) != S.POPS * len(arms):
        raise ValueError("incomplete per-generation persistence measurement")
    return result


def persistence_analysis(generations: dict) -> dict:
    """Pre-exposure fixed population-clustered, one-sided persistence contrast.

    Raw G0→G1 and G1→G2 differences are reported but NOT causal because
    World seeds change between generations. Within-generation paired arms
    share the same WorldSpec/life_seed for each 6-way opportunity.
    """
    if type(generations) is not dict or set(generations) != {0, 1, 2}:
        raise ValueError("all three sealed generations are necessary")
    expected = {
        0: {(p, "shared") for p in range(S.POPS)},
        1: {(p, arm) for p in range(S.POPS) for arm in S.ARMS},
        2: {(p, arm) for p in range(S.POPS) for arm in S.ARMS},
    }
    for g in range(3):
        if set(generations[g]) != expected[g]:
            raise ValueError("missing or extra population/arm measurement")
        for item in generations[g].values():
            if (type(item) is not dict or
                    set(item) != {"original_lives", "mean_steps",
                                  "total_steps", "survivors_at_horizon",
                                  "horizon_survival_fraction"} or
                    item["original_lives"] != 144 or
                    type(item["total_steps"]) is not int or
                    not 144 <= item["total_steps"] <= 144 * S.HORIZON or
                    type(item["survivors_at_horizon"]) is not int or
                    not 0 <= item["survivors_at_horizon"] <= 144 or
                    item["mean_steps"] != item["total_steps"] / 144 or
                    item["horizon_survival_fraction"] !=
                    item["survivors_at_horizon"] / 144):
                raise ValueError("corrupt summary; use only complete sealed lives")
    primary, g1, incremental, s2, descriptive, by_pop = [], [], [], [], [], []
    for p in range(S.POPS):
        b = generations[0][p, "shared"]
        a1 = generations[1][p, "selected"]
        r1 = generations[1][p, "random_parent"]
        a2 = generations[2][p, "selected"]
        r2 = generations[2][p, "random_parent"]
        d1 = a1["mean_steps"] - r1["mean_steps"]
        d2 = a2["mean_steps"] - r2["mean_steps"]
        h = a2["horizon_survival_fraction"] - r2["horizon_survival_fraction"]
        primary.append(d2); g1.append(d1)
        incremental.append(d2 - d1); s2.append(h)
        by_pop.append({
            "population": p, "G0_shared": b,
            "G1_selected": a1, "G1_random_parent": r1,
            "G2_selected": a2, "G2_random_parent": r2,
            "G1_selected_minus_random_steps": d1,
            "G2_selected_minus_random_steps": d2,
            "G2_minus_G1_advantage_steps": d2 - d1,
            "G2_selected_minus_random_horizon_survival_fraction": h,
            "G1_selected_minus_G0_raw_steps": a1["mean_steps"] - b["mean_steps"],
            "G1_random_minus_G0_raw_steps": r1["mean_steps"] - b["mean_steps"],
            "G2_selected_minus_G0_raw_steps": a2["mean_steps"] - b["mean_steps"],
            "G2_random_minus_G0_raw_steps": r2["mean_steps"] - b["mean_steps"],
        })
    plus = sum(v > 0 for v in primary)
    minus = sum(v < 0 for v in primary)
    status = ("PERSISTENCE_G2_ADVANTAGE_REPRODUCIBLE_F0"
              if plus >= CUTOFF and sum(primary) > 0
              else "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0")
    return {
        "schema": "i3-stage7-persistence-population-reducer/v1",
        "status": status, "population_unit_count": S.POPS,
        "horizon": S.HORIZON, "primary_positive_threshold": CUTOFF,
        "primary": {
            "name": FIXED_METHOD["primary_estimand"],
            "direction": "selected_more_persistent",
            "per_population_steps": primary, "positive": plus,
            "negative": minus, "zero": S.POPS-plus-minus,
            "mean_paired_difference_steps": sum(primary) / S.POPS,
            "one_sided_exact_tail_for_13": {"numerator": 697, "denominator": 65536},
            "threshold_met": plus >= CUTOFF and sum(primary) > 0,
        },
        "secondary": {
            "G1_selected_minus_random_steps": g1,
            "G2_minus_G1_paired_advantage_steps": incremental,
            "G2_selected_minus_random_survival_fraction": s2,
            "G1_positive_population_count": sum(x > 0 for x in g1),
            "G2_incremental_positive_population_count":
                sum(x > 0 for x in incremental),
        },
        "generation_population_originals": by_pop,
        "design": {
            "G0_one_shared_evaluation": True,
            "G1_and_G2_arms_paired_within_generation": True,
            "G0_to_G1_to_G2_raw_steps_causal_comparison": False,
            "heritable_genotypes_only": True,
            "evolutionary_performance_not_universal_organism_survival": True,
            "secondary_signals_confirmatory": False,
        },
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
    }


def _phase_chain_check(path: Path, last: str) -> None:
    lines = (path / "PHASES.jsonl").read_bytes().splitlines()
    if len(lines) != len(S.PHASES):
        raise ValueError("not nine complete native G/S/R phases")
    prev = None
    for i, raw in enumerate(lines):
        row = json.loads(raw)
        if row["ordinal"] != i or row["phase"] != S.PHASES[i] or row["previous_sha256"] != prev:
            raise ValueError("broken G/S/R phase order or predecessor")
        digest = row["chain_sha256"]
        if digest != S._sha({k: v for k, v in row.items()
                            if k != "chain_sha256"}):
            raise ValueError("tampered G/S/R phase seal")
        prev = digest
    if prev != last:
        raise ValueError("final phase chain head not matched to run receipt")


def run_full(plan: dict, archive_root: str, published_plan_sha: str) -> dict:
    """Source-exact 11,520 actual native lives; no retry, no outcome reroll.

    Engineering and science use identical P1.3 native life/World and selection;
    only science discloses the predeclared population-level performance result.
    """
    verify_plan(plan)
    science = plan["schema"] == SCHEMA_S
    if (published_plan_sha != plan["allocation_sha256"] or
            archive_root != plan["archive_root"]):
        raise PermissionError("fixed pre-exposure plan SHA or archive path differs")
    root = Path(archive_root).resolve()
    if root.is_relative_to(G0.ROOT.resolve()) or str(root) != archive_root:
        raise PermissionError("science cannot write inside or symlink to checkout")
    G0._verify_checkout(plan)  # before World is imported or any birth
    root.mkdir()  # atomic no-retry claim; archive must not already exist
    with (root / "CLAIM.json").open("xb") as f:
        f.write(S._canonical({
            "schema": "i3-stage7-one-shot-claim/v1",
            "plan_sha256": plan["allocation_sha256"],
            "archive_root": archive_root,
            "scientific": science,
            "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
        }))
        f.flush()
        os.fsync(f.fileno())
    from i3.lab import two_phase_panel as TP
    from i3.lab import stage6_light_prospective_ecologies as ecology
    from i3.lab import stage6_light_native_custody_preflight as custody
    from i3.lab import stage6_light_original_selection_bridge as bridge
    from i3.runtime.life import run_life
    from i3.modules.genome import digest as genome_digest

    phases, seals, stats = [], [], {}
    cases_all, descendants_all, draws_all = {}, [], []
    try:
        genomes = S.founder_genomes(plan)
        founders = [{
            "population": item["population"], "slot": item["slot"],
            "seed": item["genome_seed"],
            "genome": genomes[item["population"], "shared", item["slot"]],
            "genome_sha256": genome_digest(
                genomes[item["population"], "shared", item["slot"]]),
        } for item in plan["founders"]]
        with (root / "FOUNDERS.json").open("xb") as f:
            f.write(S._canonical(founders))
            f.flush()
            os.fsync(f.fileno())

        for g in (0, 1, 2):
            cases = S.native_archive_cases(plan, g, genomes)
            cases_all[g] = cases
            archive = root / f"G{g}"

            def one(case):
                spec = ecology.world_for_stage6(case["family"], case["world_seed"])
                genome = genomes[case["population"], case["arm"], case["slot"]]
                life = run_life(genome, spec, case["life_seed"], S.HORIZON,
                                keep_trace=True, protocol=plan["protocol"],
                                decision_policy="reference")
                if life["genome"] != case["genome_sha256"]:
                    raise ValueError("native organism genome differs from frozen original")
                return life

            generation = TP.generate(cases, one, archive)
            if (generation["status"] != "GENERATED"
                    or generation["generated"] != S.EXPECTED_GENERATION[g]):
                raise ValueError("original count or technical generation failed")
            digest = sha256((archive / "MANIFEST.json").read_bytes()).hexdigest()
            phases = S._append_phase(root, f"G{g}", digest, phases)
            original_audit = custody.inspect_sealed_generation(
                archive, g, cases, expected_protocol=plan["protocol"],
                source_pin=plan["source_files_sha256"],
                source_head=plan["source_git_head"])
            if (original_audit["checked_native_records"] != len(cases) or
                    original_audit["original_manifest_sha256"] != digest):
                raise ValueError("original native trace/World/funding audit rejected")
            fitness = S._summary_scores(
                TP.load_sealed(archive), g, cases, genomes,
                plan["source_files_sha256"], plan["source_git_head"],
                plan["protocol"])
            if sha256((archive / "MANIFEST.json").read_bytes()).hexdigest() != digest:
                raise ValueError("originals changed during generation sealing")
            phases = S._append_phase(root, f"SEAL_G{g}", digest, phases)
            stats[g] = reduce_generation(g, fitness)
            seals.append({"generation": g, "lives": len(cases),
                          "manifest_sha256": digest})
            if g < 2:
                children, draws = S.choose_descendants(plan, g+1, genomes,
                                                       fitness, digest)
                allocation = {
                    (r["population"], r["generation"], r["arm"], r["slot"]): r
                    for r in plan["draws"] if r["generation"] == g+1
                }
                offspring = [{
                    "population": d["population"], "generation": d["generation"],
                    "arm": d["arm"], "slot": d["slot"],
                    "parent_slot": d["parent_slot"],
                    "mutation_seed": allocation[d["population"], d["generation"],
                                                d["arm"], d["slot"]]["mutation_seed"],
                    "parent_genome_sha256": d["parent_genome_sha256"],
                    "genome": children[d["population"], d["arm"], d["slot"]],
                    "genome_sha256": d["offspring_genome_sha256"],
                } for d in draws]
                payload = {
                    "schema": "i3-stage7-parent-and-inheritance-claim/v1",
                    "generation": g+1, "prior_generation_sha256": digest,
                    "draws": draws, "offspring": offspring,
                }
                target = root / f"SELECT_G{g+1}.json"
                with target.open("xb") as f:
                    f.write(S._canonical(payload))
                    f.flush()
                    os.fsync(f.fileno())
                phases = S._append_phase(
                    root, f"SELECT_G{g+1}", sha256(target.read_bytes()).hexdigest(),
                    phases)
                draws_all.extend(draws); descendants_all.extend(offspring)
                genomes = children
            else:
                result = persistence_analysis(stats)
                if science:
                    parent_audit = bridge.inspect_original_selection(
                        {i: root / f"G{i}" for i in range(3)},
                        cases_all, founders, descendants_all, draws_all,
                        expected_protocol=plan["protocol"],
                        source_pin=plan["source_files_sha256"],
                        source_head=plan["source_git_head"])
                    if (parent_audit["original_lives_structurally_checked"] != 11520 or
                            parent_audit["claimed_parent_draws_reproduced"] != 1536 or
                            parent_audit["offspring_mutations_reproduced"] != 1536):
                        raise ValueError("parent or inherited genome is not original-bound")
                    final = {
                        "schema": "i3-stage7-persistence-scientific-result/v1",
                        "status": result["status"],
                        "fixed_method": FIXED_METHOD,
                        "analysis": result,
                        "source_git_head": plan["source_git_head"],
                        "source_files_sha256": plan["source_files_sha256"],
                        "plan_sha256": plan["allocation_sha256"],
                        "rehearsals_sha256": S._sha(plan["engineering_full_scale_receipts"]),
                        "native_lineage_audit": parent_audit,
                        "generation_seals": seals,
                        "original_lives": sum(x["lives"] for x in seals),
                        "scientific_admission": True,
                        "stage2_scientific_verdict": "NOT_ISSUED",
                        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
                    }
                    target = root / "R_FINAL_PERSISTENCE_SCIENCE.json"
                else:
                    # No engineering result direction exposed prior to science.
                    final = {
                        "schema": "i3-stage7-persistence-technical-result/v1",
                        "status": REHEARSAL_PASS,
                        "analysis_sha256": S._sha(result),
                        "generation_seals": seals,
                        "original_lives": sum(x["lives"] for x in seals),
                        "scientific_admission": False,
                        "scientific_result_disclosed": False,
                    }
                    target = root / "R_FINAL_PERSISTENCE_ENGINEERING.json"
                with target.open("xb") as f:
                    f.write(S._canonical(final))
                    f.flush()
                    os.fsync(f.fileno())
                phases = S._append_phase(
                    root, "R_FINAL", sha256(target.read_bytes()).hexdigest(),
                    phases)
        if len(phases) != len(S.PHASES):
            raise ValueError("nine-phase G/S/R transport incomplete")
        return {
            "schema": "i3-stage7-persistence-run-completed/v1",
            "status": result["status"] if science else REHEARSAL_PASS,
            "source_git_head": plan["source_git_head"],
            "source_files_sha256": plan["source_files_sha256"],
            "plan_sha256": plan["allocation_sha256"],
            "phase_chain_sha256": phases[-1]["chain_sha256"],
            "original_lives": sum(x["lives"] for x in seals),
            "scientific_admission": science, "no_retry": True,
        }
    except BaseException as exc:
        with (root / "FAILURE.json").open("xb") as f:
            f.write(S._canonical({
                "schema": "i3-stage7-irreversible-run-failure/v1",
                "status": "SCIENTIFIC_DEFECT_NO_RETRY"
                          if science else "ENGINEERING_DEFECT_NO_RETRY",
                "completed_phases": len(phases),
                "error_type": type(exc).__name__, "no_retry": True,
            }))
            f.flush()
            os.fsync(f.fileno())
        raise


def _verify_receipt_phases(root: Path, output: dict, final: dict, plan: dict) -> None:
    _phase_chain_check(root, output["phase_chain_sha256"])
    if (output["original_lives"] != 11520 or
            final["original_lives"] != 11520 or
            output["plan_sha256"] != plan["allocation_sha256"] or
            output["source_git_head"] != plan["source_git_head"] or
            output["source_files_sha256"] != plan["source_files_sha256"] or
            (root / "FAILURE.json").exists()):
        raise ValueError("not a complete source-exact native persistence transport")
    seals = final["generation_seals"]
    if (len(seals) != 3 or
            [s["generation"] for s in seals] != [0, 1, 2] or
            [s["lives"] for s in seals] != [2304, 4608, 4608]):
        raise ValueError("not all three generations sealed")
    for seal in seals:
        g = seal["generation"]
        if sha256((root / f"G{g}/MANIFEST.json").read_bytes()).hexdigest() != seal["manifest_sha256"]:
            raise ValueError("sealed original generation manifest changed")


def technical_receipt(plan_path: str, archive: str, core_path: str,
                      version: str, run_id: int) -> dict:
    p = verify_plan(json.loads(Path(plan_path).read_bytes()))
    if p["schema"] != SCHEMA_E or version not in ("3.11", "3.12"):
        raise PermissionError("foreign Stage7 engineering evidence")
    root = Path(archive).resolve()
    if str(root) != p["archive_root"] or not root.is_dir():
        raise ValueError("wrong source-bound engineering archive root")
    result_path = root / "R_FINAL_PERSISTENCE_ENGINEERING.json"
    core = json.loads(Path(core_path).read_bytes())
    final = json.loads(result_path.read_bytes())
    _verify_receipt_phases(root, core, final, p)
    if (core["status"] != REHEARSAL_PASS or
            core["scientific_admission"] is not False or
            final["status"] != REHEARSAL_PASS or
            final["scientific_admission"] is not False or
            final["scientific_result_disclosed"] is not False or
            not G0.DIGEST.fullmatch(final["analysis_sha256"])
            or type(run_id) is not int or run_id <= 0):
        raise ValueError("invalid engineering complete-pass claim")
    return {
        "schema": RECEIPT, "status": REHEARSAL_PASS,
        "python_version": version,
        "source_git_head": p["source_git_head"],
        "source_files_sha256": p["source_files_sha256"],
        "allocation_sha256": p["allocation_sha256"],
        "allocation_seed_commitment_sha256": S._sha({
            k: p[k] for k in ("root_hex", "worlds", "founders", "draws")}),
        "archive_root": str(root),
        "last_chain_sha256": core["phase_chain_sha256"],
        "result_file_sha256": sha256(result_path.read_bytes()).hexdigest(),
        "lives_archived": core["original_lives"], "worlds_planned": 288,
        "phase_count": 9, "scientific_admission": False, "no_retry": True,
        "workflow_run_id": run_id, "job_name": f"engineering-{version}",
    }


def scientific_receipt(plan_path: str, archive: str, core_path: str) -> dict:
    p = verify_plan(json.loads(Path(plan_path).read_bytes()))
    if p["schema"] != SCHEMA_S:
        raise PermissionError("scientific admission requires separate new Stage7 plan")
    root = Path(archive).resolve()
    if str(root) != p["archive_root"] or not root.is_dir():
        raise PermissionError("science may only open the precommitted archive root")
    result_path = root / "R_FINAL_PERSISTENCE_SCIENCE.json"
    core = json.loads(Path(core_path).read_bytes())
    final = json.loads(result_path.read_bytes())
    _verify_receipt_phases(root, core, final, p)
    a = final["analysis"]
    if (core["status"] not in RUN_STATUSES or
            final["status"] != core["status"] or a["status"] != core["status"]
            or core["scientific_admission"] is not True or
            final["scientific_admission"] is not True or
            final["fixed_method"] != FIXED_METHOD
            or a["population_unit_count"] != 16
            or final["plan_sha256"] != p["allocation_sha256"]
            or final["source_git_head"] != p["source_git_head"]):
        raise ValueError("wrong frozen persistence scientific result")
    if (a["primary"]["name"] != FIXED_METHOD["primary_estimand"]
            or a["primary_positive_threshold"] != CUTOFF
            or len(a["primary"]["per_population_steps"]) != 16
            or len(a["generation_population_originals"]) != 16
            or len(a["secondary"]["G1_selected_minus_random_steps"]) != 16
            or len(a["secondary"]["G2_minus_G1_paired_advantage_steps"]) != 16
            or a["primary"]["positive"] +
               a["primary"]["negative"] +
               a["primary"]["zero"] != 16
            or a["primary"]["threshold_met"] is not (a["primary"]["positive"] >= 13
                    and sum(a["primary"]["per_population_steps"]) > 0)):
        raise ValueError("incomplete or forged 16-population persistence reducer")
    # Recompute the entire population reducer from the published three
    # generation summaries; tampered signs, zeros or means fail the receipt.
    reconstructed = {0: {}, 1: {}, 2: {}}
    for row in a["generation_population_originals"]:
        pidx = row["population"]
        if type(pidx) is not int or not 0 <= pidx < 16:
            raise ValueError("invalid population identity")
        reconstructed[0][pidx, "shared"] = row["G0_shared"]
        for g in (1, 2):
            for arm in S.ARMS:
                reconstructed[g][pidx, arm] = row[f"G{g}_{arm}"]
    if S._canonical(persistence_analysis(reconstructed)) != S._canonical(a):
        raise ValueError("population-level survival reducer differs from source data")
    bridge = final["native_lineage_audit"]
    if (bridge["original_lives_structurally_checked"] != 11520 or
            bridge["claimed_parent_draws_reproduced"] != 1536 or
            bridge["offspring_mutations_reproduced"] != 1536):
        raise ValueError("scientific lineage not attached to all sealed originals")
    return {
        "schema": "i3-stage7-internal-prospective-persistence-result/v1",
        "status": core["status"],
        "source_git_head": p["source_git_head"],
        "plan_sha256": p["allocation_sha256"],
        "full_original_lives": 11520,
        "population_units": 16,
        "phase_chain_sha256": core["phase_chain_sha256"],
        "full_science_original_sha256": sha256(result_path.read_bytes()).hexdigest(),
        "fixed_method": FIXED_METHOD,
        "scientific_analysis": a,
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
        "stage2_scientific_verdict": "NOT_ISSUED",
        "I3_active_engine_promotion": False,
    }


def main() -> None:
    a = sys.argv
    if len(a) == 6 and a[1] == "allocate":
        _, _, head, source_hash, out, archive = a
        p = make_plan(secrets.token_hex(32), head, source_hash, archive)
        _write_new(out, p)
        print(json.dumps({"status": p["status"], "plan_sha256": p["allocation_sha256"],
                          "actual_lives": 0}, sort_keys=True))
    elif len(a) == 7 and a[1] == "allocate-science":
        _, _, head, source_hash, out, archive, receipts_file = a
        p = make_plan(secrets.token_hex(32), head, source_hash, archive,
                      science=True, rehearsals=json.loads(
                          Path(receipts_file).read_bytes()))
        _write_new(out, p)
        print(json.dumps({"status": p["status"], "plan_sha256": p["allocation_sha256"],
                          "actual_lives": 0}, sort_keys=True))
    elif len(a) == 3 and a[1] == "verify":
        p = verify_plan(json.loads(Path(a[2]).read_bytes()))
        print(json.dumps({"status": p["status"], "plan_sha256": p["allocation_sha256"]}))
    elif len(a) == 5 and a[1] in ("run-engineering", "run-science"):
        p = verify_plan(json.loads(Path(a[2]).read_bytes()))
        if (a[1] == "run-science") != (p["schema"] == SCHEMA_S):
            raise PermissionError("engineering/science entrypoint scope mismatch")
        print(json.dumps(run_full(p, a[3], a[4]), sort_keys=True))
    elif len(a) == 8 and a[1] == "rehearsal-receipt":
        _, _, plan, archive, core, dest, version, runid = a
        r = technical_receipt(plan, archive, core, version, int(runid))
        _write_new(dest, r)
        print(json.dumps({"status": r["status"], "version": version,
                          "original_lives": r["lives_archived"]}, sort_keys=True))
    elif len(a) == 5 and a[1] == "combine":
        _, _, file311, file312, out = a
        rr = {"3.11": json.loads(Path(file311).read_bytes()),
              "3.12": json.loads(Path(file312).read_bytes())}
        _receipt_check(rr, rr["3.11"]["source_git_head"],
                       rr["3.11"]["source_files_sha256"])
        _write_new(out, rr)
        print(json.dumps({"status": "STAGE7_TWO_FULL_REHEARSALS_VERIFIED"}))
    elif len(a) == 6 and a[1] == "science-receipt":
        _, _, plan, archive, core, out = a
        r = scientific_receipt(plan, archive, core)
        _write_new(out, r)
        print(json.dumps({
            "status": r["status"],
            "primary_signs": {
                k: r["scientific_analysis"]["primary"][k]
                for k in ("positive", "negative", "zero")},
            "population_units": 16,
        }, sort_keys=True))
    else:
        raise SystemExit("Stage7: allocate|verify|run-engineering|rehearsal-receipt|combine|allocate-science|run-science|science-receipt")


if __name__ == "__main__":
    main()
