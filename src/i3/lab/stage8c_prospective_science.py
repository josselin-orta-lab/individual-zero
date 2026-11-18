"""Stage8-C prospective SCIENTIFIC envelope over exact native 3-arm transport.

This source code must exist and be committed BEFORE any new engineering life.
On the scientific source HEAD, two new full 3.11/3.12 rehearsals are required;
older receipts from a prior HEAD cannot be silently recycled. The admitted
science plan is distinct from the technical data generator and prepublished
before the first scientific life. NO earlier study original is replayed.
"""
from __future__ import annotations

from hashlib import sha256
import hmac
import json
import math
import os
from pathlib import Path
import secrets
import sys

from i3.lab import stage8c_three_arm_transport as T
from i3.lab import stage6_light_native_g0_transport as G0
from i3.lab import stage6_light_native_gsr_transport as S

SCHEMA = "i3-stage8c-new-prospective-science-envelope/v1"
SCIENCE_PASS = "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0"
SCIENCE_NO = "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0"
SOURCE_DOMAIN = b"i3-stage8c-new-prospective-science-data-generator/v1"
PROVENANCE = "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"
TECH_LIVES = T.TOTAL_LIVES
PRIMARY = {
    "schema": "i3-stage8c-frozen-scientific-inference-v1",
    "primary_estimand": T.METHOD["primary_estimand"],
    "n_population_units": 32,
    "paired_G2_S_minus_M": True,
    "test": T.METHOD["primary_test"],
    "alpha_one_sided": 0.025,
    "t_critical_df31": T.CRIT_DF31,
    "success": "one_sided_97_5_percent_lower_bound_strictly_positive",
    "zero_sample_variance": "NO_CONFIRMATORY_CLAIM",
    "technical_outcomes_not_used_for_inference": True,
    "G0_common_G1_G2_separate_3_arms": True,
    "randomized_worlds_reserved_before_birth": True,
    "world_genome_and_motor_frozen": True,
    "no_individual_or_world_pseudoreplication": True,
    "exploratory_genomic_mechanism_not_established_by_mean_effect": True,
    "scope": "F0_only",
    "nonretry": True,
}


def _save_new(path: Path, value: object) -> None:
    with path.open("xb") as fh:
        fh.write(S._canonical(value))
        fh.flush()
        os.fsync(fh.fileno())


def _file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _technical_gate(receipts: object, head: str, source_sha: str) -> dict:
    if type(receipts) is not dict or set(receipts) != {"3.11", "3.12"}:
        raise PermissionError("exactly two distinct new exact-source engineering receipts")
    gate = T.combine_receipts(receipts["3.11"], receipts["3.12"])
    if (gate["source_git_head"] != head or
            gate["source_files_sha256"] != source_sha or
            gate["native_original_lives_rehashed"] != 2 * TECH_LIVES or
            gate["scientific_admission"] is not False or
            gate["science_lives_generated"] != 0):
        raise PermissionError("two complete stage8C rehearsals MUST match science HEAD")
    return gate


def _owner_authority() -> None:
    # Original Stage6 method must remain deny-all. ADR-0022 separately allows
    # NEW bounded prospective research, not retries of old allocations.
    G0._pins()
    owner = json.loads(G0.DIRECTION.read_bytes())
    apply = owner.get("applies_to", {})
    req = owner.get("prospective_execution_requirements", {})
    if (apply.get("scientific_prospective_experiments_authorized") is not True or
            apply.get("previously_consumed_worlds_allowed") is not False or
            apply.get("legacy_cohort_replay_allowed") is not False or
            req.get("run_specific_admission_manifest_required") is not True or
            req.get("all_originals_favorable_adverse_null_required") is not True or
            req.get("complete_source_exact_engineering_rehearsal_for_stage6_science_required")
            is not True):
        raise PermissionError("no prospective source-specific owner research scope")


def make_plan(root_hex: str, head: str, source_sha: str, archive_root: str,
              receipts: dict) -> dict:
    """Pure prospective admission; verify source + both technical seals."""
    G0._hex(root_hex, G0.DIGEST, "fresh science OS root")
    G0._hex(head, G0.COMMIT, "new Stage8C science source commit")
    G0._hex(source_sha, G0.DIGEST, "new Stage8C source digest")
    T._validate_plan_path(archive_root)
    gate = _technical_gate(receipts, head, source_sha)
    _owner_authority()
    science_root = hmac.new(bytes.fromhex(root_hex), SOURCE_DOMAIN, sha256).hexdigest()
    nested = T.make_plan(
        science_root, head, source_sha, archive_root + "/NATIVE_ORIGINALS")
    if (nested["scientific_admission"] is not False or
            nested["planned_original_lives"] != TECH_LIVES or
            nested["frozen_method"] != T.METHOD):
        raise PermissionError("unexpected native source or changed genome/World/motor")
    if (nested["g2_heldout_worlds_sha256"] in
            {r["g2_holdout_worlds_sha256"] for r in receipts.values()} or
            S._sha([p["root_hex"] for p in nested["panels"]]) in
            {r["root_commitment_sha256"] for r in receipts.values()}):
        raise PermissionError("science entropy cannot replay a technical source")
    for r in receipts.values():
        technical_root = Path(r["archive_root"])
        science_path = Path(archive_root)
        if (science_path == technical_root or
                science_path.is_relative_to(technical_root) or
                technical_root.is_relative_to(science_path)):
            raise PermissionError("science custody must be disjoint from engineering")
    payload = {
        "schema": SCHEMA, "status": "STAGE8C_SCIENCE_ALLOCATED_NOT_EXPOSED",
        "scientific_admission": True, "no_retry": True,
        "root_hex": root_hex, "source_git_head": head,
        "source_files_sha256": source_sha, "archive_root": archive_root,
        "frozen_method": T.METHOD, "frozen_scientific_inference": PRIMARY,
        "native_original_data_generator_plan": nested,
        "nested_plan_sha256": nested["allocation_sha256"],
        "g2_heldout_worlds_sha256": nested["g2_heldout_worlds_sha256"],
        "engineering_receipts": receipts,
        "engineering_gate_sha256": S._sha(gate),
        "preexposure_scientific_result": "NOT_ISSUED",
        "scientific_lives_existing_at_allocation": 0,
        "planned_native_original_lives": TECH_LIVES,
        "planned_worlds": nested["planned_worlds"],
        "planned_g2_heldout_worlds": T.HOLDOUT_WORLDS,
        "planned_mutations": T.MUTATIONS,
        "study_scope": "F0_NEW_32_POPULATIONS_G2_SCORE_IDENTITY_ONLY",
        "prior_Stage6_Stage7_Stage8A_Stage8B_and_Stage8C_technical_lives_excluded": True,
        "provenance": PROVENANCE, "stage2_scientific_verdict": "NOT_ISSUED",
    }
    payload["allocation_sha256"] = S._sha(payload)
    return payload


def verify_plan(plan: object) -> dict:
    if (type(plan) is not dict or plan.get("schema") != SCHEMA or
            plan.get("scientific_admission") is not True or
            plan.get("no_retry") is not True or
            plan.get("preexposure_scientific_result") != "NOT_ISSUED"):
        raise PermissionError("missing admitted Stage8-C new scientific preexposure plan")
    expected = make_plan(
        plan.get("root_hex"), plan.get("source_git_head"),
        plan.get("source_files_sha256"), plan.get("archive_root"),
        plan.get("engineering_receipts"))
    if S._canonical(expected) != S._canonical(plan):
        raise PermissionError("tampered scientific method, root, World or receipts")
    return plan


def _science_reduce(plan: dict, root: Path) -> dict:
    """Reread SEALED ORIGINAL gzip lives; never infer from technical aggregates."""
    inner = plan["native_original_data_generator_plan"]
    all_rows = []
    all_d = []
    total = 0
    audited_mutations = 0
    for panel_i, panel in enumerate(inner["panels"]):
        p_root = root / "NATIVE_ORIGINALS" / f"PANEL_{panel_i}"
        # The full independent native-structure and mutation reconstruction
        # is an essential gate, not a replacement for G2 lived-step reduction.
        evidence = T._panel_reaudit(panel, p_root)
        if (evidence["original_lives"] != sum(T.PANEL_LIVES) or
                evidence["phase_chain_sha256"] != json.loads(
                    (root / "NATIVE_ORIGINALS" /
                     f"PANEL_{panel_i}_CORE.json").read_bytes())["phase_chain_sha256"]):
            raise ValueError("native original SHA/sealed lineage is invalid")
        audited_mutations += 2 * S.POPS * len(T.ARMS) * S.SLOTS
        total += evidence["original_lives"]
        genomes = S.founder_genomes(panel)
        for g in (0, 1, 2):
            cases = T.native_cases(panel, g, genomes)
            fitness = T.reduce_sealed_generation(panel, g, p_root, cases, genomes)
            if g < 2:
                children, parent_receipts = T.choose_three_arm_children(
                    panel, g + 1, genomes, fitness,
                    T._sha_file(p_root / f"G{g}" / "MANIFEST.json"))
                if len(parent_receipts) != S.POPS * len(T.ARMS) * S.SLOTS:
                    raise ValueError("foreign G1/G2 parental archive")
                genomes = children
            else:
                for p in range(S.POPS):
                    population = panel_i * S.POPS + p
                    steps = {}
                    censored = {}
                    for arm in T.ARMS:
                        values = [fitness[p, arm, slot] for slot in range(S.SLOTS)]
                        steps[arm] = math.fsum(v[1] for v in values) / (S.SLOTS * 6)
                        censored[arm] = sum(v[0] for v in values) / (S.SLOTS * 6)
                    d_sm = steps["selected"] - steps["matched_multiplicity"]
                    d_su = steps["selected"] - steps["random_parent"]
                    d_mu = steps["matched_multiplicity"] - steps["random_parent"]
                    all_rows.append({
                        "population": population,
                        "G2_mean_lived_steps": steps,
                        "G2_horizon_censored_fraction": censored,
                        "G2_S_minus_M_steps": d_sm,
                        "G2_S_minus_U_steps_descriptive": d_su,
                        "G2_M_minus_U_steps_descriptive": d_mu,
                        "G2_six_world_opportunities_per_genome": True,
                    })
                    all_d.append(d_sm)
    if (len(all_rows) != T.POPULATIONS or
            [row["population"] for row in all_rows] !=
            list(range(T.POPULATIONS)) or
            total != TECH_LIVES or audited_mutations != T.MUTATIONS):
        raise ValueError("incomplete 32-population or native-lineage science")
    primary = T.reduce_primary_g2(all_d)
    return {
        "schema": "i3-stage8c-new-prospective-g2-inference-from-originals/v1",
        "status": primary["status"],
        "primary": primary,
        "all_32_population_analyses": all_rows,
        "secondary_descriptive": {
            "mean_G2_S_minus_U_steps": math.fsum(
                x["G2_S_minus_U_steps_descriptive"] for x in all_rows) / T.POPULATIONS,
            "mean_G2_M_minus_U_steps": math.fsum(
                x["G2_M_minus_U_steps_descriptive"] for x in all_rows) / T.POPULATIONS,
        },
        "native_original_lives_rehashed": total,
        "native_mutations_reconstructed": audited_mutations,
        "scientific_pseudoreplication": False,
        "F0_only": True,
        "original_null_adverse_and_terminal_lives_retained": True,
        "mechanistic_genome_causality_not_demonstrated": True,
    }


def run_science(plan: dict, archive_root: str, published_sha: str) -> dict:
    verify_plan(plan)
    if (archive_root != plan["archive_root"] or
            published_sha != plan["allocation_sha256"]):
        raise PermissionError("exact prepublished SCIENCE allocation required")
    inner = plan["native_original_data_generator_plan"]
    G0._verify_checkout(inner["panels"][0])
    root = Path(archive_root)
    root.mkdir()  # irreversible one-shot outer claim
    _save_new(root / "CLAIM.json", {
        "schema": "i3-stage8c-new-prospective-science-claim/v1",
        "scientific_admission": True,
        "plan_sha256": published_sha,
        "source_git_head": plan["source_git_head"],
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
    })
    try:
        _save_new(root / "INNER_PLAN.json", inner)
        # Stage8-C technical transport is solely the native data generator;
        # an outer, separately admitted envelope makes the scientific claim.
        # This is NOT a replay of either consumed technical allocation.
        core = T.run_engineering(inner, inner["archive_root"],
                                 inner["allocation_sha256"])
        if (core["status"] != T.TECH_PASS or
                core["original_lives"] != TECH_LIVES or
                core["scientific_admission"] is not False):
            raise ValueError("new source-exact native GSR generated incompletely")
        _save_new(root / "INNER_CORE.json", core)
        result = _science_reduce(plan, root)
        final = {
            "schema": "i3-stage8c-new-prospective-science-original/v1",
            "status": result["status"], "scientific_admission": True,
            "plan_sha256": published_sha,
            "source_git_head": plan["source_git_head"],
            "source_files_sha256": plan["source_files_sha256"],
            "frozen_method": T.METHOD,
            "frozen_scientific_inference": PRIMARY,
            "preexposure_g2_worlds_sha256": plan["g2_heldout_worlds_sha256"],
            "both_engineering_receipts_sha256": S._sha(plan["engineering_receipts"]),
            "original_native_lives": TECH_LIVES,
            "all_original_data_generator_core": core,
            "result": result,
            "provenance": PROVENANCE,
            "stage2_scientific_verdict": "NOT_ISSUED",
            "no_retry": True,
        }
        _save_new(root / "SCIENCE_FINAL.json", final)
        return {
            "schema": "i3-stage8c-new-prospective-science-one-shot-core/v1",
            "status": result["status"],
            "scientific_admission": True, "source_git_head": plan["source_git_head"],
            "plan_sha256": published_sha,
            "science_original_sha256": _file_sha(root / "SCIENCE_FINAL.json"),
            "g2_heldout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
            "native_original_lives_rehashed": TECH_LIVES,
            "native_mutations_reconstructed": T.MUTATIONS,
            "no_retry": True,
        }
    except BaseException as err:
        _save_new(root / "FAILURE.json", {
            "schema": "i3-stage8c-science-technical-failure/v1",
            "status": "TECHNICAL_NO_VERDICT_NO_RETRY",
            "error_type": type(err).__name__, "no_retry": True,
        })
        raise


def scientific_receipt(plan_path: str, original_root: str,
                       core_path: str) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    raw = root / "SCIENCE_FINAL.json"
    if (str(root.resolve()) != plan["archive_root"] or
            (root / "FAILURE.json").exists() or
            not raw.is_file() or
            core.get("status") not in (SCIENCE_PASS, SCIENCE_NO) or
            core.get("scientific_admission") is not True or
            core.get("native_original_lives_rehashed") != TECH_LIVES or
            core.get("native_mutations_reconstructed") != T.MUTATIONS or
            core.get("plan_sha256") != plan["allocation_sha256"] or
            core.get("g2_heldout_worlds_sha256") != plan["g2_heldout_worlds_sha256"] or
            core.get("science_original_sha256") != _file_sha(raw)):
        raise ValueError("not a complete, sealed, original prospective science result")
    final = json.loads(raw.read_bytes())
    nested = plan["native_original_data_generator_plan"]
    inner_plan_path = root / "INNER_PLAN.json"
    inner_core_path = root / "INNER_CORE.json"
    if (json.loads(inner_plan_path.read_bytes()) != nested or
            final["status"] != core["status"] or
            final["scientific_admission"] is not True or
            final["frozen_method"] != T.METHOD or
            final["frozen_scientific_inference"] != PRIMARY or
            final["plan_sha256"] != plan["allocation_sha256"] or
            final["preexposure_g2_worlds_sha256"] != plan["g2_heldout_worlds_sha256"] or
            final["both_engineering_receipts_sha256"] != S._sha(
                plan["engineering_receipts"]) or
            final["original_native_lives"] != TECH_LIVES or
            final["all_original_data_generator_core"] !=
            json.loads(inner_core_path.read_bytes())):
        raise ValueError("altered sealed scientific envelope or native custody")
    # This deliberately DOES NOT confer scientific meaning on the inner
    # engineering status: independent outer preexposure admission owns it.
    T.technical_receipt(str(inner_plan_path), nested["archive_root"],
                        str(inner_core_path), "3.11", 1)
    reproduced = _science_reduce(plan, root)
    if S._canonical(reproduced) != S._canonical(final["result"]):
        raise ValueError("published science differs from native original gzip lives")
    if reproduced["status"] != core["status"]:
        raise ValueError("scientific status changed after exposure")
    return {
        "schema": "i3-stage8c-new-prospective-internal-scientific-receipt/v1",
        "status": core["status"], "source_git_head": plan["source_git_head"],
        "science_plan_sha256": plan["allocation_sha256"],
        "science_original_sha256": _file_sha(raw),
        "g2_heldout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
        "native_original_lives_rehashed": TECH_LIVES,
        "native_mutations_reconstructed": T.MUTATIONS,
        "population_units": T.POPULATIONS,
        "primary": reproduced["primary"],
        "all_population_statistics": reproduced["all_32_population_analyses"],
        "provenance": PROVENANCE,
        "Stage2_scientific_GO": False,
    }


def main() -> None:
    args = sys.argv
    if len(args) == 7 and args[1] == "allocate-science":
        _, _, head, source_sha, path, original, receipts_path = args
        r = json.loads(Path(receipts_path).read_bytes())
        plan = make_plan(secrets.token_hex(32), head, source_sha, original, r)
        _save_new(Path(path), plan)
        print(json.dumps({
            "status": plan["status"], "sha": plan["allocation_sha256"],
            "new_scientific_lives": 0,
        }, sort_keys=True))
    elif len(args) == 3 and args[1] == "verify":
        plan = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps({
            "status": plan["status"], "sha": plan["allocation_sha256"],
        }, sort_keys=True))
    elif len(args) == 5 and args[1] == "run-science":
        plan = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps(run_science(plan, args[3], args[4]), sort_keys=True))
    elif len(args) == 6 and args[1] == "science-receipt":
        _, _, plan, originals, core, dest = args
        result = scientific_receipt(plan, originals, core)
        _save_new(Path(dest), result)
        print(json.dumps({
            "status": result["status"], "population_units": result["population_units"],
            "native_original_lives_rehashed": result["native_original_lives_rehashed"],
        }, sort_keys=True))
    elif len(args) == 5 and args[1] == "combine":
        _, _, p311, p312, dest = args
        r = {"3.11": json.loads(Path(p311).read_bytes()),
             "3.12": json.loads(Path(p312).read_bytes())}
        T.combine_receipts(r["3.11"], r["3.12"])
        _save_new(Path(dest), r)
        print(json.dumps({"status": "STAGE8C_TWO_FULL_TECHNICAL_RECEIPTS_ADMITTED"}))
    else:
        raise SystemExit("Stage8C science: combine|allocate-science|verify|run-science|science-receipt")


if __name__ == "__main__":
    main()
