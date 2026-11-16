"""Stage8-A: source-locked prospective mean lifetime under parental selection.

Two independent 16-population native G/S/R panels form 32 population units.
The trusted native P1.3 funded-v2 motor and genome-v4 engine are unchanged.
Each subpanel runs with the already-tested *technical* Stage7 transport; a
NEW, separately admitted Stage8 envelope owns scientific inference. Thus no
Stage7 scientific verdict is recycled or silently reclassified.

Allocation/verification/reduction are PURE, never spawn a life. Exposure is
a single-use, source-exact atomic archive claim. No reruns, no seed cherry-pick.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import hmac
import json
import math
import os
from pathlib import Path
import secrets
import sys

from i3.lab import stage7_persistence_transport as P
from i3.lab import stage6_light_native_gsr_transport as S
from i3.lab import stage6_light_native_g0_transport as G0

SCHEMA_TECH = "i3-stage8a-mean-persistence-engineering-plan/v1"
SCHEMA_SCIENCE = "i3-stage8a-mean-persistence-science-plan/v1"
RECEIPT = "i3-stage8a-complete-native-rehearsal-receipt/v1"
TECH_PASS = "STAGE8A_FULL_NATIVE_ENGINEERING_SEALED_NO_SCIENCE"
SCIENCE_PASS = "STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0"
SCIENCE_NO = "STAGE8A_MEAN_ADVANTAGE_NOT_DEMONSTRATED_F0"
PROVENANCE = "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"
T_CRIT_31_975 = 2.0395134463964077
METHOD = {
    "schema": "i3-stage8a-frozen-mean-persistence/v1",
    "direction": "selected_mean_G2_lived_steps_greater_than_uniform_parent",
    "population_units": 32, "panels": 2, "populations_per_panel": 16,
    "genomes_per_population": 24, "life_opportunities": 6,
    "horizon": 400, "G0_common_once": True,
    "G1_G2_arm_pairing": True, "motor": "P1.3 funded-v2 reference",
    "genome": "native-v4-scale-0.1-no-memory",
    "selected_parent_rank_weight": "24..1 sealed survival counts then lived steps",
    "control": "uniform-parent-score-blind",
    "primary": "mean_over_32_populations_of_G2_selected_minus_random_mean_lived_steps",
    "primary_test": "one-sided Student t lower confidence bound > 0",
    "alpha_one_sided": 0.025, "t_critical_df31": T_CRIT_31_975,
    "zero_sd": "NO_CONFIRMATORY_CLAIM",
    "primary_threshold": "strictly positive lower bound at 97.5% one-sided",
    "null_negative_and_censored_originals_retained": True,
    "independent_unit": "population; no individual or World pseudo-replication",
    "G0_to_G1_to_G2_raw_trends_are_descriptive_only": True,
    "ecologies": ["stable", "depletion", "pulse"],
    "family_modifiers": "descriptive_only",
    "per_population_sign_counts": "secondary_not_confirmatory",
    "parent_diversity": "secondary_not_confirmatory",
    "science_is_new": True, "no_stage7_root_or_life_reuse": True,
}
LIVES_PER_PANEL = 11520
LIVES_PER_COMPLETE_RUN = 23040
EXPECTED_PHASES = 18


def _new_file(path: str | Path, item: dict) -> None:
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(item, f, sort_keys=True, ensure_ascii=False,
                  allow_nan=False, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def _sha_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _seed_commitment(panels: list[dict]) -> str:
    return S._sha([{
        key: panel[key] for key in ("root_hex", "worlds", "founders", "draws")
    } for panel in panels])


def _receipt_check(r: object, head: str, sources: str) -> None:
    if type(r) is not dict or set(r) != {"3.11", "3.12"}:
        raise PermissionError("two FULL, NEW, Stage8 3.11/3.12 technical receipts required")
    keys = {"schema", "status", "python_version", "workflow_run_id",
            "source_git_head", "source_files_sha256", "allocation_sha256",
            "seed_commitment_sha256", "archive_root", "panel_receipt_sha256",
            "archived_lives", "phase_count", "scientific_admission",
            "no_retry", "job_name"}
    seeds, allocs, roots = set(), set(), set()
    for ver in ("3.11", "3.12"):
        obj = r[ver]
        if (type(obj) is not dict or set(obj) != keys or
                obj["schema"] != RECEIPT or obj["status"] != TECH_PASS or
                obj["python_version"] != ver or
                obj["source_git_head"] != head or
                obj["source_files_sha256"] != sources or
                obj["archived_lives"] != LIVES_PER_COMPLETE_RUN or
                obj["phase_count"] != EXPECTED_PHASES or
                obj["scientific_admission"] is not False or
                obj["no_retry"] is not True or
                obj["job_name"] != "engineering-" + ver or
                type(obj["workflow_run_id"]) is not int or
                obj["workflow_run_id"] <= 0 or
                any(type(obj[k]) is not str or
                    G0.DIGEST.fullmatch(obj[k]) is None for k in
                    ("allocation_sha256", "seed_commitment_sha256",
                     "panel_receipt_sha256")) or
                type(obj["archive_root"]) is not str or
                not obj["archive_root"].startswith("/")):
            raise PermissionError("engineering receipt cannot admit Stage8 science")
        seeds.add(obj["seed_commitment_sha256"])
        allocs.add(obj["allocation_sha256"])
        roots.add(obj["archive_root"])
    if len(seeds) != 2 or len(allocs) != 2 or len(roots) != 2:
        raise PermissionError("two independent full-scale engineering roots required")


def make_plan(root_hex: str, head: str, sources: str, archive_root: str,
              *, scientific: bool = False, rehearsals: dict | None = None) -> dict:
    """Allocate 32 genuinely new populations in two disjoint native panels.

    A new, exclusive Stage8 root/HMAC domain is fed to the source-exact
    Stage7 *technical* engine as a data generator. Prior Stage7 experiment
    outcomes never enter the new samples or Stage8 estimand.
    """
    G0._hex(root_hex, G0.DIGEST, "new Stage8 OS root")
    if type(scientific) is not bool:
        raise PermissionError("science admission must be boolean")
    if scientific:
        _receipt_check(rehearsals, head, sources)
        owner = json.loads(G0.DIRECTION.read_bytes())
        allowed = owner.get("applies_to", {})
        requirements = owner.get("prospective_execution_requirements", {})
        if (allowed.get("scientific_prospective_experiments_authorized") is not True
                or requirements.get("run_specific_admission_manifest_required") is not True
                or requirements.get("all_originals_favorable_adverse_null_required") is not True
                or requirements.get(
                    "complete_source_exact_engineering_rehearsal_for_stage6_science_required")
                    is not True):
            raise PermissionError("ADR-0022 owner direction insufficient for new Stage8 science")
    elif rehearsals is not None:
        raise PermissionError("engineering cannot embed scientific receipts")
    if (type(archive_root) is not str or not archive_root.startswith("/")
            or Path(archive_root).resolve().as_posix() != archive_root
            or Path(archive_root).resolve().is_relative_to(G0.ROOT.resolve())):
        raise PermissionError("science originals must be at one canonical outside-source path")

    key = bytes.fromhex(root_hex)
    panels = []
    for index in range(2):
        fresh = hmac.new(key,
                         b"i3-stage8a-distinct-panel-v1/" +
                         str(index).encode("ascii"), sha256).hexdigest()
        child = str(Path(archive_root) / f"PANEL_{index}")
        panels.append(P.make_plan(fresh, head, sources, child, science=False))
    if panels[0]["root_hex"] == panels[1]["root_hex"]:
        raise ValueError("Stage8 duplicated subpanel entropy")
    # HMAC separation and explicit verification, never reroll a colliding plan.
    used = set()
    for p in panels:
        ids = [v[k] for v in p["worlds"]
               for k in ("world_index", "world_seed", "life_seed")]
        ids += [v["genome_seed"] for v in p["founders"]]
        ids += [v[k] for v in p["draws"]
                for k in ("parent_draw_seed", "mutation_seed")]
        if len(ids) != len(set(ids)) or any(i in used for i in ids):
            raise ValueError("cross-panel seed collision: do not cherry-pick a new root")
        used.update(ids)
    if scientific:
        fresh_commitment = _seed_commitment(panels)
        if (fresh_commitment in
                {r["seed_commitment_sha256"] for r in rehearsals.values()} or
                archive_root in {r["archive_root"] for r in rehearsals.values()}):
            raise PermissionError("science must be distinct from both rehearsals")
    plan = {
        "schema": SCHEMA_SCIENCE if scientific else SCHEMA_TECH,
        "status": ("STAGE8A_SCIENCE_ALLOCATED_NOT_EXPOSED" if scientific
                   else "STAGE8A_ENGINEERING_ALLOCATED_NOT_EXPOSED"),
        "root_hex": root_hex, "source_git_head": head,
        "source_files_sha256": sources,
        "archive_root": archive_root, "panels": panels,
        "frozen_method": METHOD,
        "scientific_admission": scientific,
        "owner_scope": "ADR-0022_NEW_PROSPECTIVE_LAB_SOURCE_LOCKED",
        "planned_original_lives": LIVES_PER_COMPLETE_RUN,
        "planned_worlds": 576,
        "engineering_full_scale_receipts": rehearsals if scientific else None,
        "scientific_verdict_before_exposure": "NOT_ISSUED",
        "no_retry": True, "originals_existing_at_allocation": 0,
        "provenance": PROVENANCE,
        "Stage6_and_Stage7_originals_not_reused": True,
    }
    plan["allocation_sha256"] = S._sha(plan)
    return plan


def verify_plan(plan: object) -> dict:
    if (type(plan) is not dict or
            plan.get("schema") not in (SCHEMA_TECH, SCHEMA_SCIENCE)):
        raise PermissionError("not a separate source-locked Stage8 allocation")
    expected = make_plan(
        plan.get("root_hex"), plan.get("source_git_head"),
        plan.get("source_files_sha256"), plan.get("archive_root"),
        scientific=(plan["schema"] == SCHEMA_SCIENCE),
        rehearsals=plan.get("engineering_full_scale_receipts"))
    if S._canonical(plan) != S._canonical(expected):
        raise PermissionError("altered method, parent stream, World or admission evidence")
    return plan


def reduce_population_mean(differences: list[float]) -> dict:
    """Single frozen one-sided population-cluster t interval; no World opened."""
    if (type(differences) is not list or len(differences) != 32 or
            any(type(d) not in (float, int) or not math.isfinite(d)
                for d in differences)):
        raise ValueError("exactly 32 finite, population-level G2 contrasts required")
    values = [float(x) for x in differences]
    mu = math.fsum(values) / 32
    sd = math.sqrt(math.fsum((d-mu)**2 for d in values) / 31)
    se = sd / math.sqrt(32)
    bound = mu-T_CRIT_31_975*se
    passed = sd > 0 and mu > 0 and bound > 0
    return {
        "schema": "i3-stage8a-frozen-mean-population-inference/v1",
        "status": SCIENCE_PASS if passed else SCIENCE_NO,
        "n_populations": 32,
        "mean_difference_steps": mu,
        "sample_sd_between_populations": sd,
        "standard_error": se,
        "t_critical_df31_one_sided_975": T_CRIT_31_975,
        "one_sided_97_5_percent_lower_bound_steps": bound,
        "positive": sum(d > 0 for d in values),
        "negative": sum(d < 0 for d in values),
        "zero": sum(d == 0 for d in values),
        "primary_success": passed,
        "zero_sd_not_confirmatory": True,
        "population_contrasts_steps": values,
        "assumptions": "population_independence_and_t_interval_approximation_unproven",
        "not_a_test_of_universal_lineage_advantage": True,
    }


def _native_lifetime(life: dict, identity: dict, panel: dict) -> tuple[int, bool]:
    """Preserve genuine deaths at step 400 distinctly from censored survivors."""
    if type(life) is not dict:
        raise ValueError("missing original native organism")
    lived = life.get("steps_lived")
    terminal = life.get("terminal")
    meta = life.get("manifest", {})
    source = meta.get("source", {})
    funding = life.get("cognitive_accounting", {})
    if (type(lived) is not int or not 1 <= lived <= S.HORIZON or
            life.get("horizon") != S.HORIZON or
            terminal not in ("dead", "censored") or
            (terminal == "censored" and lived != S.HORIZON) or
            life.get("genome") != identity["genome_sha256"] or
            life.get("life_seed") != identity["life_seed"] or
            meta.get("world_sha256") != identity["world_sha256"] or
            meta.get("protocol") != panel["protocol"] or
            source.get("git_head") != panel["source_git_head"] or
            source.get("sha256") != panel["source_files_sha256"] or
            funding.get("status") != "SETTLED_FOR_DECLARED_WORK" or
            funding.get("shortfall_steps") != 0 or
            type(life.get("trace")) is not list or
            len(life["trace"]) != lived):
        raise ValueError("native lifetime, death/censoring or cognition differs")
    return lived, terminal == "censored"


def _scan_panel(panel: dict, root: Path, offset: int) -> tuple[dict, dict]:
    """Read original gzip lives, verifying every enrolled coordinate and body.

    One genotype is evaluated on six original F0 opportunities; only its
    population (not 144 individual lives) may enter Stage8 inference.
    """
    from i3.lab import two_phase_panel as TP

    overall, ecologies = {}, {}
    for g in (0, 1, 2):
        by_arm = defaultdict(lambda: [0, 0, 0])
        by_family = defaultdict(lambda: [0, 0, 0])
        seen = set()
        opportunities = {}
        for identity, life in TP.load_sealed(root / f"G{g}"):
            pop = identity["population"]
            arm = identity["arm"]
            slot = identity["slot"]
            family = identity["family"]
            repeat = identity["repeat"]
            key = (pop, arm, slot, family, repeat)
            if (type(pop) is not int or not 0 <= pop < 16 or
                    arm not in (("shared",) if g == 0 else S.ARMS) or
                    type(slot) is not int or not 0 <= slot < 24 or
                    family not in S.FAMILIES or
                    repeat not in (0, 1) or key in seen or
                    identity["generation"] != g or
                    identity["source_sha256"] != panel["source_files_sha256"]):
                raise ValueError("native life has missing/duplicate/foreign population identity")
            seen.add(key)
            opp = (pop, family, repeat)
            worldsha = identity["world_sha256"]
            if opp in opportunities and opportunities[opp] != worldsha:
                raise ValueError("unpaired WorldSpec across selected/random descendants")
            opportunities[opp] = worldsha
            lived, censored = _native_lifetime(life, identity, panel)
            selected = (pop + offset, g, arm)
            cell = by_arm[selected]
            cell[0] += 1; cell[1] += lived; cell[2] += censored
            fcell = by_family[(pop+offset, g, arm, family)]
            fcell[0] += 1; fcell[1] += lived; fcell[2] += censored
        expected = 2304 if g == 0 else 4608
        if len(seen) != expected:
            raise ValueError("lost native life in original generation")
        expected_arm = {(p+offset, g, arm) for p in range(16)
                        for arm in (("shared",) if g == 0 else S.ARMS)}
        if (set(by_arm) != expected_arm or
                any(v[0] != 144 for v in by_arm.values()) or
                any(v[0] != 48 for v in by_family.values())):
            raise ValueError("not 144 lives/pop/arm (or 48 per F0 family)")
        overall.update(by_arm); ecologies.update(by_family)
    return overall, ecologies


def _ancestry_check(panel: dict, root: Path) -> dict:
    """Reproduce native mutation and parent ranks from 11,520 originals."""
    from i3.lab import stage6_light_original_selection_bridge as bridge
    founders = json.loads((root / "FOUNDERS.json").read_bytes())
    picks = [json.loads((root / f"SELECT_G{g}.json").read_bytes())
             for g in (1, 2)]
    offspring = [entry for pick in picks for entry in pick["offspring"]]
    draws = [entry for pick in picks for entry in pick["draws"]]
    cases = {}
    for g in (0, 1, 2):
        genomes = {
            (entry["population"], "shared", entry["slot"]): entry["genome"]
            for entry in founders
        } if g == 0 else {
            (entry["population"], entry["arm"], entry["slot"]): entry["genome"]
            for entry in picks[g-1]["offspring"]
        }
        cases[g] = S.native_archive_cases(panel, g, genomes)
    report = bridge.inspect_original_selection(
        {g: root / f"G{g}" for g in range(3)}, cases, founders,
        offspring, draws, expected_protocol=panel["protocol"],
        source_pin=panel["source_files_sha256"],
        source_head=panel["source_git_head"])
    if (report["original_lives_structurally_checked"] != 11520 or
            report["claimed_parent_draws_reproduced"] != 1536 or
            report["offspring_mutations_reproduced"] != 1536):
        raise ValueError("incomplete parent/mutation verification")
    unique = {}
    for g, pick in zip((1, 2), picks):
        for pop in range(16):
            for arm in S.ARMS:
                parents = [r["parent_slot"] for r in pick["draws"]
                           if r["population"] == pop and r["arm"] == arm]
                if len(parents) != 24:
                    raise ValueError("missing family diversity observations")
                unique[pop, g, arm] = len(set(parents))
    return {"original_audit": report, "distinct_parent_counts": unique}


def _science_reduce(plan: dict, root: Path) -> dict:
    summary, families, diversity, audits = {}, {}, {}, []
    for i, panel in enumerate(plan["panels"]):
        folder = root / f"PANEL_{i}"
        s, e = _scan_panel(panel, folder, i*16)
        summary.update(s)
        families.update(e)
        a = _ancestry_check(panel, folder)
        audits.append(a["original_audit"])
        diversity.update({(pop+i*16, g, arm): cnt
                          for (pop, g, arm), cnt in
                          a["distinct_parent_counts"].items()})
    diffs = []
    populations = []
    for pop in range(32):
        baseline = summary[pop, 0, "shared"]
        s1 = summary[pop, 1, "selected"]; r1 = summary[pop, 1, "random_parent"]
        s2 = summary[pop, 2, "selected"]; r2 = summary[pop, 2, "random_parent"]
        primary = (s2[1]-r2[1]) / 144
        diffs.append(primary)
        f = {}
        for family in S.FAMILIES:
            selected = families[pop, 2, "selected", family]
            control = families[pop, 2, "random_parent", family]
            f[family] = {
                "selected_minus_random_mean_steps": (selected[1]-control[1])/48,
                "selected_horizon_fraction": selected[2]/48,
                "random_horizon_fraction": control[2]/48,
            }
        populations.append({
            "population": pop, "panel": pop//16,
            "G0_mean_steps": baseline[1]/144,
            "G1_selected_mean_steps": s1[1]/144,
            "G1_random_mean_steps": r1[1]/144,
            "G2_selected_mean_steps": s2[1]/144,
            "G2_random_mean_steps": r2[1]/144,
            "G1_selected_minus_random_steps": (s1[1]-r1[1])/144,
            "G2_selected_minus_random_steps": primary,
            "G2_selected_horizon_survival": s2[2]/144,
            "G2_random_horizon_survival": r2[2]/144,
            "G2_parent_diversity_selected": diversity[pop,2,"selected"],
            "G2_parent_diversity_random": diversity[pop,2,"random_parent"],
            "G2_families_descriptive": f,
        })
    metric = reduce_population_mean(diffs)
    return {
        "status": metric["status"], "primary": metric,
        "all_population_statistics": populations,
        "native_original_lives_rechecked": LIVES_PER_COMPLETE_RUN,
        "native_parent_draws_reproduced":
            sum(a["claimed_parent_draws_reproduced"] for a in audits),
        "native_mutations_reproduced":
            sum(a["offspring_mutations_reproduced"] for a in audits),
        "horizon": 400,
        "stage7_gene_and_sign_verdicts_unchanged": True,
        "raw_intergeneration_changes_are_not_causal": True,
    }


def run_once(plan: dict, archive_root: str, published_sha: str) -> dict:
    verify_plan(plan)
    if (archive_root != plan["archive_root"] or
            published_sha != plan["allocation_sha256"]):
        raise PermissionError("not the source-locked prepublished Stage8 allocation")
    G0._verify_checkout(plan["panels"][0])
    root = Path(archive_root).resolve()
    if str(root) != archive_root or root.is_relative_to(G0.ROOT.resolve()):
        raise PermissionError("cannot run within source checkout or symlink path")
    # This parent-root claim ensures neither a partial two-panel engineering
    # rehearsal nor a scientific result can be rerun under the same plan.
    root.mkdir()  # no exist_ok: first exposure exclusively claims this root
    _new_file(root / "CLAIM.json", {
        "schema": "i3-stage8a-irreversible-one-shot-claim/v1",
        "allocation_sha256": published_sha, "source_git_head":
            plan["source_git_head"], "scientific": plan["scientific_admission"],
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL"})
    cores = []
    try:
        for i, panel in enumerate(plan["panels"]):
            _new_file(root / f"PANEL_{i}_PLAN.json", panel)
            core = P.run_full(panel, panel["archive_root"],
                              panel["allocation_sha256"])
            _new_file(root / f"PANEL_{i}_CORE.json", core)
            cores.append(core)
        if len(cores) != 2 or sum(c["original_lives"] for c in cores) != 23040:
            raise ValueError("two full 11520-life native panels required")
        final = None
        if plan["scientific_admission"]:
            final = {
                "schema": "i3-stage8a-mean-science-original/v1",
                "source_git_head": plan["source_git_head"],
                "source_files_sha256": plan["source_files_sha256"],
                "plan_sha256": published_sha,
                "rehearsals_sha256": S._sha(
                    plan["engineering_full_scale_receipts"]),
                "frozen_method": METHOD,
                "result": _science_reduce(plan, root),
                "panel_cores": cores,
                "original_native_lives": 23040,
                "provenance": PROVENANCE,
                "stage2_scientific_verdict": "NOT_ISSUED"}
            _new_file(root / "SCIENCE_FINAL.json", final)
        return {
            "schema": "i3-stage8a-one-shot-run-completed/v1",
            "status": final["result"]["status"] if final else TECH_PASS,
            "scientific_admission": plan["scientific_admission"],
            "source_git_head": plan["source_git_head"],
            "plan_sha256": published_sha,
            "original_lives": 23040,
            "panel_chain_sha256": [c["phase_chain_sha256"] for c in cores],
            "science_final_sha256": _sha_file(root / "SCIENCE_FINAL.json")
                                    if final else None,
            "no_retry": True,
        }
    except BaseException as exc:
        _new_file(root / "FAILURE.json", {
            "schema": "i3-stage8a-native-defect/v1",
            "status": "TECHNICAL_NO_VERDICT_NO_RETRY",
            "error_type": type(exc).__name__,
            "panels_completed": len(cores),
            "no_retry": True})
        raise


def technical_receipt(plan_path: str, original_root: str,
                      core_path: str, version: str, run_id: int) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    if plan["scientific_admission"] is not False:
        raise PermissionError("not technical Stage8 evidence")
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    if (str(root.resolve()) != plan["archive_root"] or
            core["status"] != TECH_PASS or
            core["scientific_admission"] is not False or
            core["original_lives"] != 23040 or
            core["plan_sha256"] != plan["allocation_sha256"] or
            (root / "FAILURE.json").exists() or
            version not in ("3.11", "3.12") or
            type(run_id) is not int or run_id <= 0):
        raise ValueError("not a complete 32-population technical rehearsal")
    details = []
    for i in range(2):
        p = plan["panels"][i]
        pr = P.technical_receipt(
            str(root / f"PANEL_{i}_PLAN.json"), p["archive_root"],
            str(root / f"PANEL_{i}_CORE.json"), version, run_id)
        if (pr["allocation_sha256"] != p["allocation_sha256"] or
                pr["lives_archived"] != 11520 or
                pr["last_chain_sha256"] != core["panel_chain_sha256"][i]):
            raise ValueError("one technical panel failed original/chain validation")
        details.append(pr)
    return {
        "schema": RECEIPT, "status": TECH_PASS,
        "python_version": version, "workflow_run_id": run_id,
        "source_git_head": plan["source_git_head"],
        "source_files_sha256": plan["source_files_sha256"],
        "allocation_sha256": plan["allocation_sha256"],
        "seed_commitment_sha256": _seed_commitment(plan["panels"]),
        "archive_root": plan["archive_root"],
        "panel_receipt_sha256": S._sha(details),
        "archived_lives": 23040, "phase_count": 18,
        "scientific_admission": False, "no_retry": True,
        "job_name": "engineering-" + version,
    }


def scientific_receipt(plan_path: str, original_root: str, core_path: str) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    if plan["scientific_admission"] is not True:
        raise PermissionError("science requires both source-exact technical receipts")
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    final = json.loads((root / "SCIENCE_FINAL.json").read_bytes())
    if (str(root.resolve()) != plan["archive_root"] or
            (root / "FAILURE.json").exists() or
            core["status"] not in (SCIENCE_PASS, SCIENCE_NO) or
            core["original_lives"] != 23040 or
            core["plan_sha256"] != plan["allocation_sha256"] or
            core["scientific_admission"] is not True or
            core["science_final_sha256"] != _sha_file(root / "SCIENCE_FINAL.json") or
            final["frozen_method"] != METHOD or
            final["plan_sha256"] != plan["allocation_sha256"] or
            final["result"]["status"] != core["status"] or
            final["result"]["native_original_lives_rechecked"] != 23040 or
            final["result"]["native_parent_draws_reproduced"] != 3072 or
            final["result"]["native_mutations_reproduced"] != 3072):
        raise ValueError("Stage8 mean science envelope is not sealed or source-bound")
    for i in range(2):
        expected = plan["panels"][i]
        if (json.loads((root / f"PANEL_{i}_PLAN.json").read_bytes()) != expected or
                final["panel_cores"][i] !=
                json.loads((root / f"PANEL_{i}_CORE.json").read_bytes())):
            raise ValueError("scientific nested panel original altered")
        P.technical_receipt(str(root / f"PANEL_{i}_PLAN.json"),
                            expected["archive_root"],
                            str(root / f"PANEL_{i}_CORE.json"),
                            "3.11", 1)
    # Recompute mean analysis from native original-life data, without reroll.
    reproduced = _science_reduce(plan, root)
    if S._canonical(reproduced) != S._canonical(final["result"]):
        raise ValueError("original lives contradict published mean persistence")
    return {
        "schema": "i3-stage8a-mean-persistence-internal-result/v1",
        "status": final["result"]["status"],
        "science_plan_sha256": plan["allocation_sha256"],
        "science_original_sha256": _sha_file(root / "SCIENCE_FINAL.json"),
        "source_git_head": plan["source_git_head"],
        "population_units": 32, "original_native_lives": 23040,
        "primary": final["result"]["primary"],
        "all_population_statistics": final["result"]["all_population_statistics"],
        "provenance": PROVENANCE,
        "Stage2_scientific_GO": False,
    }


def main() -> None:
    args = sys.argv
    if len(args) == 6 and args[1] == "allocate":
        _, _, head, sources, out, archive = args
        p = make_plan(secrets.token_hex(32), head, sources, archive)
        _new_file(out, p)
        print(json.dumps({"status": p["status"], "plan_sha256":
                          p["allocation_sha256"], "new_lives": 0}))
    elif len(args) == 7 and args[1] == "allocate-science":
        _, _, head, sources, out, archive, receipt_file = args
        r = json.loads(Path(receipt_file).read_bytes())
        p = make_plan(secrets.token_hex(32), head, sources, archive,
                      scientific=True, rehearsals=r)
        _new_file(out, p)
        print(json.dumps({"status": p["status"], "plan_sha256":
                          p["allocation_sha256"], "new_lives": 0}))
    elif len(args) == 3 and args[1] == "verify":
        p = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps({"status": p["status"], "plan_sha256": p["allocation_sha256"]}))
    elif len(args) == 5 and args[1] in ("run-engineering", "run-science"):
        p = verify_plan(json.loads(Path(args[2]).read_bytes()))
        if (args[1] == "run-science") != p["scientific_admission"]:
            raise PermissionError("wrong Stage8 evidence admission entrypoint")
        print(json.dumps(run_once(p, args[3], args[4]), sort_keys=True))
    elif len(args) == 8 and args[1] == "rehearsal-receipt":
        _, _, plan, root, core, dest, version, run_id = args
        r = technical_receipt(plan, root, core, version, int(run_id))
        _new_file(dest, r)
        print(json.dumps({"status": r["status"], "lives": r["archived_lives"]}))
    elif len(args) == 5 and args[1] == "combine":
        _, _, r311, r312, dest = args
        r = {"3.11": json.loads(Path(r311).read_bytes()),
             "3.12": json.loads(Path(r312).read_bytes())}
        _receipt_check(r, r["3.11"]["source_git_head"],
                       r["3.11"]["source_files_sha256"])
        _new_file(dest, r)
        print(json.dumps({"status": "STAGE8A_TWO_FULL_REHEARSALS_ACCEPTED"}))
    elif len(args) == 6 and args[1] == "science-receipt":
        _, _, plan, root, core, dest = args
        r = scientific_receipt(plan, root, core)
        _new_file(dest, r)
        print(json.dumps({"status": r["status"], "populations": 32,
                          "mean_steps": r["primary"]["mean_difference_steps"],
                          "lower_bound": r["primary"]["one_sided_97_5_percent_lower_bound_steps"],
                          "positive": r["primary"]["positive"],
                          "negative": r["primary"]["negative"]}, sort_keys=True))
    else:
        raise SystemExit("Stage8A: allocate|verify|run-engineering|rehearsal-receipt|combine|allocate-science|run-science|science-receipt")


if __name__ == "__main__":
    main()
