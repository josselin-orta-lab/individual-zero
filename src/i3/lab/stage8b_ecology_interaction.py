"""Stage8-B prospective test: does selection advantage interact with F0 ecology?

Source-locked, single-use *new* G0/G1/G2 lineage experiment. 32 fresh
populations, each with three precommitted F0 evaluation families and
two reserved World opportunities per family. In each generation selected
and score-blind random parents share the SAME world opportunities. G2
heldout Worlds are allocated before the first birth but are never
consulted in G0/G1 parental selection.

The existing Stage8-A transport generates real native originals, but
its old mean-persistence scientific decision is NEVER reused as Stage8-B
inference. This module publishes a new frozen 2-df population-cluster
omnibus test, only after two full independent technical rehearsals.
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

from i3.lab import stage8a_mean_persistence as A
from i3.lab import stage6_light_native_gsr_transport as S
from i3.lab import stage6_light_native_g0_transport as G0

SCHEMA_E = "i3-stage8b-ecology-interaction-engineering/v1"
SCHEMA_S = "i3-stage8b-ecology-interaction-science/v1"
RECEIPT = "i3-stage8b-ecology-full-rehearsal/v1"
TECH_PASS = "STAGE8B_FULL_NATIVE_ECOLOGY_ENGINEERING_SEALED"
SCIENCE_PASS = "STAGE8B_SELECTION_BY_ECOLOGY_INTERACTION_F0"
SCIENCE_NO = "STAGE8B_NO_INTERACTION_DEMONSTRATED_F0"
PROVENANCE = "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"
PRIOR_STAGE8A_SCIENCE_PLAN = (
    "dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660"
)
POPULATIONS = 32
LIVES = 23040
PHASE_COUNT = 18
ALPHA = 0.025
METHOD = {
    "schema": "i3-stage8b-frozen-ecology-omnibus/v1",
    "question": "is_G2_parent_selection_advantage_heterogeneous_across_F0_ecologies",
    "families": ["stable", "depletion", "pulse"],
    "effect_per_population_family": (
        "mean_steps_G2_selected_48_lives_minus_random_parent_48_lives"
    ),
    "paired_ecology_contrasts": [
        "depletion_minus_stable", "pulse_minus_stable",
    ],
    "primary": "two_dimensional_population_level_Hotelling_T_squared",
    "null": "mean_G2_selection_effect_equal_in_all_three_F0_families",
    "alternative": "at_least_one_family_differs_two_sided_omnibus",
    "alpha_omnibus": ALPHA,
    "n_population_units": POPULATIONS,
    "df1": 2,
    "df2": 30,
    "f_reduction": "F = (n-2)*T_squared/(2*(n-1))",
    "f_survival_df1_2": "P(F_2_30>=F)=(1+2*F/30)**(-15)",
    "covariance_singular": "NO_INTERACTION_DEMONSTRATED",
    "population_is_only_statistical_unit": True,
    "family_label_randomization": False,
    "independent_population_assumption": "required_not_proved",
    "multivariate_normal_approximation": "required_not_proved",
    "subgroup_pairwise_tests": "descriptive_not_confirmatory",
    "per_population_sign_counts": "descriptive_not_confirmatory",
    "genetic_parent_diversity": "descriptive_not_causal",
    "P1_3_funded_v2_motor_unchanged": True,
    "genome_v4_mutation_scale": 0.1,
    "cognition_energy_vigilance_paid": True,
    "inherit_only_genome_no_memory": True,
    "horizon": 400,
    "deaths_at_horizon_distinct_from_censored_survivors": True,
    "G0_one_shared_arm": True,
    "G1_G2_selected_vs_random_parent_pairing": True,
    "generations_use_different_world_seeds": True,
    "G2_worlds_precommitted_and_blind_to_parent_fitness": True,
    "two_opportunities_each_family": True,
    "previous_Stage6_Stage7_Stage8A_originals_closed": True,
    "new_scientific_plans_require_both_complete_rehearsals": True,
}
# New holdout needs its own domain, in addition to the inner Stage8A/7/6
# already source-separated allocation domains.
DOMAIN = b"i3-stage8b-new-ecology-heldout-v1/inner-transport"


def _write_new(path: str | Path, payload: dict) -> None:
    with Path(path).open("x", encoding="utf-8") as target:
        json.dump(payload, target, indent=2, sort_keys=True,
                  ensure_ascii=False, allow_nan=False)
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _inner_seed_commitment(inner: dict) -> str:
    return A._seed_commitment(inner["panels"])


def _receipt_check(rehearsals: object, head: str, source_sha: str) -> None:
    if type(rehearsals) is not dict or set(rehearsals) != {"3.11", "3.12"}:
        raise PermissionError("two distinct Stage8-B FULL engineering receipts required")
    keys = {"schema", "status", "python_version", "source_git_head",
            "source_files_sha256", "allocation_sha256", "seed_commitment_sha256",
            "G2_holdout_worlds_sha256", "archive_root",
            "underlying_native_receipt_sha256", "archived_lives", "phase_count",
            "scientific_admission", "no_retry", "workflow_run_id", "job_name"}
    allocations, seeds, worlds, archives, runs = set(), set(), set(), set(), set()
    for version in ("3.11", "3.12"):
        r = rehearsals[version]
        if (type(r) is not dict or set(r) != keys
                or r["schema"] != RECEIPT or r["status"] != TECH_PASS
                or r["python_version"] != version
                or r["source_git_head"] != head
                or r["source_files_sha256"] != source_sha
                or r["archived_lives"] != LIVES
                or r["phase_count"] != PHASE_COUNT
                or r["scientific_admission"] is not False
                or r["no_retry"] is not True
                or type(r["workflow_run_id"]) is not int
                or r["workflow_run_id"] <= 0
                or r["job_name"] != "engineering-" + version
                or type(r["archive_root"]) is not str
                or not r["archive_root"].startswith("/")
                or any(type(r[k]) is not str or G0.DIGEST.fullmatch(r[k]) is None
                       for k in ("allocation_sha256", "seed_commitment_sha256",
                                 "G2_holdout_worlds_sha256",
                                 "underlying_native_receipt_sha256"))):
            raise PermissionError("rehearsal is incomplete, foreign, or off-source")
        allocations.add(r["allocation_sha256"])
        seeds.add(r["seed_commitment_sha256"])
        worlds.add(r["G2_holdout_worlds_sha256"])
        archives.add(r["archive_root"])
        runs.add(r["workflow_run_id"])
    if (len(allocations) != 2 or len(seeds) != 2 or len(worlds) != 2
            or len(archives) != 2 or len(runs) != 1):
        raise PermissionError("engineering roots, Worlds or workflow run disagree")


def _g2_holdout(inner: dict) -> list[dict]:
    worlds = []
    all_seeds = set()
    for panel_i, panel in enumerate(inner["panels"]):
        for w in panel["worlds"]:
            seed = w["world_seed"]
            if seed in all_seeds:
                raise ValueError("overlapping World seeds across generations or populations")
            all_seeds.add(seed)
            if w["generation"] != 2:
                continue
            worlds.append({
                "panel": panel_i,
                "population": 16 * panel_i + w["population"],
                "family": w["family"], "repeat": w["repeat"],
                "world_index": w["world_index"],
                "world_seed": w["world_seed"], "life_seed": w["life_seed"],
            })
    coordinates = {(x["population"], x["family"], x["repeat"]) for x in worlds}
    if (len(worlds) != 192 or len(coordinates) != 192
            or coordinates != {
                (p, f, r) for p in range(POPULATIONS)
                for f in S.FAMILIES for r in (0, 1)}):
        raise ValueError("new G2 holdout is incomplete or duplicated")
    return worlds


def make_plan(root_hex: str, head: str, source_sha: str, archive_root: str,
              *, science: bool = False, rehearsals: dict | None = None) -> dict:
    """Pure allocation. G2 ecological holdouts are part of the published plan."""
    key = bytes.fromhex(G0._hex(root_hex, G0.DIGEST, "Stage8B new root"))
    if type(science) is not bool:
        raise PermissionError("Stage8B scientific admission must be explicit")
    if science:
        _receipt_check(rehearsals, head, source_sha)
        # The owner ADR permits separate internal prospective laboratory science;
        # technical completion is necessary but never substitutes owner authority.
        owner = json.loads(G0.DIRECTION.read_bytes())
        allowed = owner.get("applies_to", {})
        req = owner.get("prospective_execution_requirements", {})
        if (allowed.get("scientific_prospective_experiments_authorized") is not True
                or req.get("run_specific_admission_manifest_required") is not True
                or req.get("all_originals_favorable_adverse_null_required") is not True
                or req.get("complete_source_exact_engineering_rehearsal_for_stage6_science_required")
                is not True):
            raise PermissionError("owner prospective research authority missing")
    elif rehearsals is not None:
        raise PermissionError("engineering cannot present science receipts")
    derived = hmac.new(key, DOMAIN, sha256).hexdigest()
    inner_root = archive_root + "/NATIVE_ORIGINALS"
    inner = A.make_plan(derived, head, source_sha, inner_root, scientific=False)
    reserved = _g2_holdout(inner)
    commitment = S._sha(reserved)
    if science and (commitment in {x["G2_holdout_worlds_sha256"]
                                  for x in rehearsals.values()}
                    or _inner_seed_commitment(inner) in {
                        x["seed_commitment_sha256"] for x in rehearsals.values()}
                    or archive_root in {x["archive_root"] for x in rehearsals.values()}):
        raise PermissionError("science cannot reuse rehearsal entropy or archive")
    payload = {
        "schema": SCHEMA_S if science else SCHEMA_E,
        "status": ("STAGE8B_SCIENCE_ALLOCATED_NOT_EXPOSED" if science
                   else "STAGE8B_ENGINEERING_ALLOCATED_NOT_EXPOSED"),
        "root_hex": root_hex, "archive_root": archive_root,
        "source_git_head": head, "source_files_sha256": source_sha,
        "scientific_admission": science,
        "frozen_method": METHOD,
        "g2_holdout_reserved_worlds": reserved,
        "g2_holdout_worlds_sha256": commitment,
        "inner_native_technical_plan": inner,
        "inner_native_technical_plan_sha256": inner["allocation_sha256"],
        "all_seed_commitment_sha256": _inner_seed_commitment(inner),
        "prior_stage8a_plan_sha256_for_nonreplay": PRIOR_STAGE8A_SCIENCE_PLAN,
        "planned_lives": LIVES, "planned_worlds": 576,
        "planned_g2_holdout_worlds": len(reserved),
        "planned_g2_native_lives": 9216,
        "all_originals_at_allocation": 0,
        "preexposure_scientific_verdict": "NOT_ISSUED",
        "engineering_receipts": rehearsals if science else None,
        "no_retry": True,
        "provenance": PROVENANCE,
        "Stage6_Stage7_Stage8A_lives_not_reused": True,
        "scope": "ADR-0022_NEW_PROSPECTIVE_ECOLOGY_INTERACTION_F0_ONLY",
    }
    payload["allocation_sha256"] = S._sha(payload)
    return payload


def verify_plan(plan: object) -> dict:
    if type(plan) is not dict or plan.get("schema") not in {SCHEMA_E, SCHEMA_S}:
        raise PermissionError("not a Stage8-B source-locked pre-exposure plan")
    exact = make_plan(
        plan.get("root_hex"), plan.get("source_git_head"),
        plan.get("source_files_sha256"), plan.get("archive_root"),
        science=(plan["schema"] == SCHEMA_S),
        rehearsals=plan.get("engineering_receipts"))
    if S._canonical(plan) != S._canonical(exact):
        raise PermissionError("frozen ecology, reserved Worlds or source were modified")
    return plan


def omnibus(family_effects: list[dict]) -> dict:
    """Frozen two-sided 2-df Hotelling test, 32 population vectors, no lives.

    H0: E[D_depletion-D_stable]=E[D_pulse-D_stable]=0.
    Under independent multivariate-normal population vectors, statistic
    maps to F(2,30). No family is selected after observing its effect.
    """
    if type(family_effects) is not list or len(family_effects) != POPULATIONS:
        raise ValueError("primary requires exactly 32 population-level vectors")
    vectors = []
    data = []
    for entry in family_effects:
        if (type(entry) is not dict or set(entry) != set(S.FAMILIES)
                or any(type(v) not in (int, float) or not math.isfinite(v)
                       for v in entry.values())):
            raise ValueError("missing, infinite or extra family effects")
        d = {f: float(entry[f]) for f in S.FAMILIES}
        data.append(d)
        vectors.append((d["depletion"]-d["stable"],
                        d["pulse"]-d["stable"]))
    x = [v[0] for v in vectors]
    y = [v[1] for v in vectors]
    mx = math.fsum(x)/POPULATIONS
    my = math.fsum(y)/POPULATIONS
    sxx = math.fsum((v-mx)**2 for v in x)/(POPULATIONS-1)
    syy = math.fsum((v-my)**2 for v in y)/(POPULATIONS-1)
    sxy = math.fsum((a-mx)*(b-my) for a,b in vectors)/(POPULATIONS-1)
    determinant = sxx*syy-sxy*sxy
    valid = (sxx > 0 and syy > 0 and
             determinant > max(sxx*syy*1e-12, 1e-15))
    if valid:
        t2 = POPULATIONS*(syy*mx*mx - 2*sxy*mx*my + sxx*my*my)/determinant
        t2 = max(0.0, t2)
        f = (POPULATIONS-2)*t2/(2*(POPULATIONS-1))
        # Exact F(2, n-2) survival function; no scipy dependency.
        p = (1.0 + 2*f/(POPULATIONS-2))**(-(POPULATIONS-2)/2)
    else:
        t2, f, p = None, None, 1.0  # never claim a PASS on singular covariance
    means = {family: math.fsum(row[family] for row in data)/POPULATIONS
             for family in S.FAMILIES}
    positive = {family: sum(row[family] > 0 for row in data)
                for family in S.FAMILIES}
    passed = valid and p < ALPHA
    # Secondary simultaneous bookkeeping only: no pairwise test can
    # substitute for the one preregistered omnibus decision.
    pairwise_descriptive = {}
    for label, left, right in (
        ("depletion_minus_stable", "depletion", "stable"),
        ("pulse_minus_stable", "pulse", "stable"),
        ("pulse_minus_depletion", "pulse", "depletion"),
    ):
        values = [row[left] - row[right] for row in data]
        mean = math.fsum(values) / POPULATIONS
        sd = math.sqrt(math.fsum((v-mean)**2 for v in values)/(POPULATIONS-1))
        halfwidth = 2.0395134463964077*sd/math.sqrt(POPULATIONS)
        pairwise_descriptive[label] = {
            "mean_steps": mean,
            "sd_between_populations": sd,
            "descriptive_95_percent_interval": [mean-halfwidth, mean+halfwidth],
            "positive": sum(v>0 for v in values),
            "negative": sum(v<0 for v in values),
            "zero": sum(v==0 for v in values),
            "multiplicity_adjusted_confirmatory_test": False,
        }
    return {
        "schema": "i3-stage8b-population-cluster-omnibus-result/v1",
        "status": SCIENCE_PASS if passed else SCIENCE_NO,
        "primary_success": passed, "n_populations": POPULATIONS,
        "family_mean_selection_advantage_steps": means,
        "family_positive_population_counts": positive,
        "two_family_contrasts_means": {
            "depletion_minus_stable": mx, "pulse_minus_stable": my},
        "pairwise_descriptive_not_confirmatory": pairwise_descriptive,
        "sample_covariance_2_by_2": [[sxx,sxy],[sxy,syy]],
        "covariance_identifiable": valid,
        "hotelling_t_squared": t2, "f_df2_30": f,
        "p_value_two_sided_omnibus": p,
        "alpha_fixed": ALPHA,
        "primary_population_vectors": vectors,
        "effects_per_population": data,
        "assumptions": ("independent_population_clusters_and_multivariate_"
                        "normal_Hotelling_approximation_not_independently_proved"),
        "no_ecology_family_is_independently_confirmed": True,
        "Stage8A_mean_primary_not_reused": True,
    }


def _reduce_originals(plan: dict, root: Path) -> dict:
    """Separate Stage8-B inferential decision after full native audit.

    A._science_reduce performs complete native original/parent/mutation
    checks and exposes all 32 descriptive family effects. Its Stage8-A
    mean-status field is deliberately DISCARDED, never a Stage8-B gate.
    """
    inner = plan["inner_native_technical_plan"]
    audited = A._science_reduce(inner, root / "NATIVE_ORIGINALS")
    if (audited.get("native_original_lives_rechecked") != LIVES or
            audited.get("native_parent_draws_reproduced") != 3072 or
            audited.get("native_mutations_reproduced") != 3072):
        raise ValueError("native genealogy or original count was not reproduced")
    rows = audited.get("all_population_statistics")
    if (type(rows) is not list or len(rows) != POPULATIONS or
            {x.get("population") for x in rows} != set(range(POPULATIONS))):
        raise ValueError("not exactly 32 unique population-level results")
    by_pop = {x["population"]: x for x in rows}
    family_effects = []
    published = []
    for p in range(POPULATIONS):
        row = by_pop[p]
        families = row.get("G2_families_descriptive")
        if type(families) is not dict or set(families) != set(S.FAMILIES):
            raise ValueError("missing one of three frozen F0 family summaries")
        effects = {
            f: families[f]["selected_minus_random_mean_steps"]
            for f in S.FAMILIES
        }
        observed_global = row["G2_selected_minus_random_steps"]
        if not math.isclose(math.fsum(effects.values())/3,
                            observed_global, rel_tol=0, abs_tol=1e-9):
            raise ValueError("G2 family effects cannot reproduce original G2 total")
        family_effects.append(effects)
        published.append(row)
    primary = omnibus(family_effects)
    return {
        "status": primary["status"],
        "primary": primary,
        "all_32_population_observed_statistics": published,
        "all_native_lives_reverified": LIVES,
        "parent_draws_reproduced": 3072,
        "mutations_reproduced": 3072,
        "G2_reserve_worlds_binding": plan["g2_holdout_worlds_sha256"],
        "prior_results_not_used_as_scientific_samples": True,
        "no_gene_mechanism_or_ecological_generalization_claim": True,
    }


def run_once(plan: dict, original_root: str, published_sha: str) -> dict:
    verify_plan(plan)
    if (original_root != plan["archive_root"] or
            published_sha != plan["allocation_sha256"]):
        raise PermissionError("prepublished Stage8B method or archive path changed")
    inner = plan["inner_native_technical_plan"]
    G0._verify_checkout(inner["panels"][0])
    root = Path(original_root).resolve()
    if str(root) != original_root or root.is_relative_to(G0.ROOT.resolve()):
        raise PermissionError("archive must be outside clean source checkout")
    root.mkdir()  # atomic NO_RETRY claim, cannot reroll after partial failures
    _write_new(root / "CLAIM.json", {
        "schema": "i3-stage8b-claim-no-retry/v1",
        "source_sha": plan["source_git_head"],
        "allocation_sha256": plan["allocation_sha256"],
        "science": plan["scientific_admission"],
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
    })
    try:
        _write_new(root / "INNER_PLAN.json", inner)
        core = A.run_once(inner, inner["archive_root"], inner["allocation_sha256"])
        if (core["original_lives"] != LIVES
                or core["status"] != A.TECH_PASS
                or core["plan_sha256"] != inner["allocation_sha256"]
                or len(core["panel_chain_sha256"]) != 2):
            raise ValueError("two 16-population native panels must complete")
        _write_new(root / "INNER_CORE.json", core)
        analysis = None
        if plan["scientific_admission"]:
            analysis = _reduce_originals(plan, root)
            _write_new(root / "SCIENCE_FINAL.json", {
                "schema": "i3-stage8b-scientific-original/v1",
                "source_git_head": plan["source_git_head"],
                "plan_sha256": plan["allocation_sha256"],
                "inner_plan_sha256": inner["allocation_sha256"],
                "g2_holdout_worlds_sha256": plan["g2_holdout_worlds_sha256"],
                "engineering_receipts_sha256": S._sha(plan["engineering_receipts"]),
                "frozen_method": METHOD, "analysis": analysis,
                "original_native_lives": LIVES, "provenance": PROVENANCE,
                "Stage2_scientific_GO": False,
            })
        return {
            "schema": "i3-stage8b-completed-transport/v1",
            "status": analysis["status"] if analysis else TECH_PASS,
            "scientific_admission": plan["scientific_admission"],
            "source_git_head": plan["source_git_head"],
            "plan_sha256": plan["allocation_sha256"],
            "inner_plan_sha256": inner["allocation_sha256"],
            "original_lives": LIVES,
            "g2_holdout_worlds_sha256": plan["g2_holdout_worlds_sha256"],
            "inner_panel_chain_sha256": core["panel_chain_sha256"],
            "science_original_sha256": _hash_file(root / "SCIENCE_FINAL.json")
                                      if analysis is not None else None,
            "no_retry": True,
        }
    except BaseException as exc:
        _write_new(root / "FAILURE.json", {
            "schema": "i3-stage8b-terminal-technical-fault/v1",
            "status": "TECHNICAL_NO_VERDICT_NO_RETRY",
            "exception_type": type(exc).__name__,
            "originals_may_have_been_exposed": True,
            "no_retry": True,
        })
        raise


def technical_receipt(plan_path: str, original_root: str, core_path: str,
                      version: str, run_id: int) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    inner = plan["inner_native_technical_plan"]
    if (plan["scientific_admission"] is not False
            or str(root.resolve()) != plan["archive_root"]
            or (root / "FAILURE.json").exists()
            or core.get("status") != TECH_PASS
            or core.get("plan_sha256") != plan["allocation_sha256"]
            or core.get("original_lives") != LIVES
            or core.get("g2_holdout_worlds_sha256") != plan["g2_holdout_worlds_sha256"]
            or core.get("inner_panel_chain_sha256") !=
               json.loads((root / "INNER_CORE.json").read_bytes()).get("panel_chain_sha256")
            or version not in ("3.11", "3.12")
            or type(run_id) is not int or run_id <= 0
            or json.loads((root / "INNER_PLAN.json").read_bytes()) != inner):
        raise ValueError("not a complete Stage8-B 32-population rehearsal")
    below = A.technical_receipt(
        str(root / "INNER_PLAN.json"), inner["archive_root"],
        str(root / "INNER_CORE.json"), version, run_id)
    if (below["archived_lives"] != LIVES
            or below["phase_count"] != PHASE_COUNT
            or below["panel_receipt_sha256"] is None
            or below["allocation_sha256"] != inner["allocation_sha256"]):
        raise ValueError("not all native original phases are sealed")
    return {
        "schema": RECEIPT, "status": TECH_PASS,
        "python_version": version, "workflow_run_id": run_id,
        "source_git_head": plan["source_git_head"],
        "source_files_sha256": plan["source_files_sha256"],
        "allocation_sha256": plan["allocation_sha256"],
        "seed_commitment_sha256": plan["all_seed_commitment_sha256"],
        "G2_holdout_worlds_sha256": plan["g2_holdout_worlds_sha256"],
        "archive_root": plan["archive_root"],
        "underlying_native_receipt_sha256": S._sha(below),
        "archived_lives": LIVES, "phase_count": PHASE_COUNT,
        "scientific_admission": False, "no_retry": True,
        "job_name": "engineering-" + version,
    }


def scientific_receipt(plan_path: str, original_root: str, core_path: str) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    inner = plan["inner_native_technical_plan"]
    raw = root / "SCIENCE_FINAL.json"
    final = json.loads(raw.read_bytes())
    if (plan["scientific_admission"] is not True
            or str(root.resolve()) != plan["archive_root"]
            or (root / "FAILURE.json").exists()
            or core.get("status") not in (SCIENCE_PASS, SCIENCE_NO)
            or core.get("original_lives") != LIVES
            or core.get("plan_sha256") != plan["allocation_sha256"]
            or core.get("g2_holdout_worlds_sha256") != plan["g2_holdout_worlds_sha256"]
            or core.get("science_original_sha256") != _hash_file(raw)
            or final["plan_sha256"] != plan["allocation_sha256"]
            or final["frozen_method"] != METHOD
            or final["g2_holdout_worlds_sha256"] != plan["g2_holdout_worlds_sha256"]
            or final["analysis"]["status"] != core["status"]
            or final["analysis"]["all_native_lives_reverified"] != LIVES
            or final["analysis"]["parent_draws_reproduced"] != 3072
            or final["analysis"]["mutations_reproduced"] != 3072
            or json.loads((root / "INNER_PLAN.json").read_bytes()) != inner):
        raise ValueError("original scientific ecology evidence invalid")
    A.technical_receipt(str(root / "INNER_PLAN.json"), inner["archive_root"],
                        str(root / "INNER_CORE.json"), "3.11", 1)
    reproduced = _reduce_originals(plan, root)
    if S._canonical(reproduced) != S._canonical(final["analysis"]):
        raise ValueError("frozen interaction reduction not reproduced from originals")
    return {
        "schema": "i3-stage8b-internal-ecology-omnibus-result/v1",
        "status": final["analysis"]["status"],
        "source_git_head": plan["source_git_head"],
        "science_plan_sha256": plan["allocation_sha256"],
        "science_original_sha256": _hash_file(raw),
        "g2_holdout_worlds_sha256": plan["g2_holdout_worlds_sha256"],
        "population_units": POPULATIONS,
        "original_native_lives": LIVES,
        "primary": reproduced["primary"],
        "all_population_statistics": reproduced["all_32_population_observed_statistics"],
        "provenance": PROVENANCE,
        "Stage2_scientific_GO": False,
    }


def main() -> None:
    args = sys.argv
    if len(args) == 6 and args[1] == "allocate":
        _, _, head, sources, dest, original = args
        p = make_plan(secrets.token_hex(32), head, sources, original)
        _write_new(dest, p)
        print(json.dumps({"status": p["status"], "sha": p["allocation_sha256"],
                          "new_native_lives": 0}))
    elif len(args) == 7 and args[1] == "allocate-science":
        _, _, head, sources, dest, original, receipts = args
        r = json.loads(Path(receipts).read_bytes())
        p = make_plan(secrets.token_hex(32), head, sources, original,
                      science=True, rehearsals=r)
        _write_new(dest, p)
        print(json.dumps({"status": p["status"], "sha": p["allocation_sha256"],
                          "new_native_lives": 0}))
    elif len(args) == 3 and args[1] == "verify":
        p = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps({"status": p["status"], "sha": p["allocation_sha256"]}))
    elif len(args) == 5 and args[1] in ("run-engineering","run-science"):
        p = verify_plan(json.loads(Path(args[2]).read_bytes()))
        if (args[1] == "run-science") != p["scientific_admission"]:
            raise PermissionError("incorrect Stage8B science admission entrypoint")
        print(json.dumps(run_once(p, args[3], args[4]), sort_keys=True))
    elif len(args) == 8 and args[1] == "rehearsal-receipt":
        _, _, plan, root, core, dest, version, run_id = args
        r = technical_receipt(plan, root, core, version, int(run_id))
        _write_new(dest, r)
        print(json.dumps({"status": r["status"], "original_lives": LIVES}))
    elif len(args) == 5 and args[1] == "combine":
        _, _, r311, r312, dest = args
        rr = {"3.11": json.loads(Path(r311).read_bytes()),
              "3.12": json.loads(Path(r312).read_bytes())}
        _receipt_check(rr, rr["3.11"]["source_git_head"],
                       rr["3.11"]["source_files_sha256"])
        _write_new(dest, rr)
        print(json.dumps({"status": "STAGE8B_TWO_COMPLETE_REHEARSALS_ADMITTED"}))
    elif len(args) == 6 and args[1] == "science-receipt":
        _, _, plan, root, core, dest = args
        result = scientific_receipt(plan, root, core)
        _write_new(dest, result)
        print(json.dumps({
            "status": result["status"],
            "population_units": result["population_units"],
            "p_value": result["primary"]["p_value_two_sided_omnibus"],
            "family_means": result["primary"]["family_mean_selection_advantage_steps"],
        }, sort_keys=True))
    else:
        raise SystemExit("Stage8B: allocate|verify|run-engineering|rehearsal-receipt|combine|allocate-science|run-science|science-receipt")


if __name__ == "__main__":
    main()
