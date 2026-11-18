"""Stage8-C three-arm G0/G1/G2 native ENGINEERING transport.

This new source/seed domain cannot run Stage8-C science. It generates only
two separate sealed technical rehearsals; a future source-locked science
release requires both complete receipts and a distinct allocation.

S = persistence-ranked parents; M = EXACT matched reproduction multiplicities
with independently permuted identities; U = score-blind uniform parents.
The born organism always uses unmodified P1.3 funded-v2 World/motor/cognition.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import hmac
import json
import math
import os
from pathlib import Path
import random
import secrets
import sys

from i3.lab import stage6_light_native_g0_transport as G0
from i3.lab import stage6_light_native_gsr_transport as S
from i3.lab import stage8a_mean_persistence as A
from i3.lab import stage8c_parent_multiplicity_control as M

PANEL_SCHEMA = "i3-stage8c-three-arm-native-panel-engineering/v1"
PLAN_SCHEMA = "i3-stage8c-three-arm-native-technical-plan/v1"
PROTOCOL = "i3-stage8c-three-arm-P1.3-funded-v2-engineering/v1"
RECEIPT_SCHEMA = "i3-stage8c-three-arm-complete-technical-receipt/v1"
TECH_PASS = "STAGE8C_THREE_ARM_FULL_ENGINEERING_SEALED_NO_SCIENCE"
PROVENANCE = "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"
ARMS = ("selected", "matched_multiplicity", "random_parent")
PANELS = 2
POPULATIONS = 32
PANEL_LIVES = (2304, 6912, 6912)
TOTAL_LIVES = 32256
MUTATIONS = 4608
HOLDOUT_WORLDS = 192
CRIT_DF31 = 2.0395134463964077
METHOD = {
    "schema": "i3-stage8c-frozen-three-arm-G2-persistence/v1",
    "question": "does G2 persistence-ranking advantage survive exact parental multiplicity matching",
    "population_units": 32, "genomes_per_population": 24,
    "arms": list(ARMS), "G0_common": True,
    "world_families": list(S.FAMILIES), "repetitions_per_family": 2,
    "worlds_reserved_before_G0": True, "G2_holdouts": HOLDOUT_WORLDS,
    "horizon": 400, "dead_at_400_is_not_censored": True,
    "selected_parent_selection": "sealed_G0_G1_censored_then_steps_then_slot_rank_24_to_1",
    "matched_control": "selected_slots_HMAC_independent_bijection_into_OWN_parent_arm",
    "matched_exact_occupancy_multiset_per_population_per_generation": True,
    "uniform_control": "score_blind_uniform_parent_with_replacement",
    "mutation": "native_genome_v4_scale_0.1_own_independent_seeds",
    "motor_and_cognitive_costs": "unchanged_P1.3_funded_v2",
    "genetic_memory_inheritance": False,
    "primary_estimand": "mean_over_32_population_G2_mean_steps_selected_minus_matched",
    "primary_test": "one_sided_Student_lower_97.5_percent_confidence_bound_above_zero",
    "alpha_one_sided": 0.025, "df": 31,
    "t_critical": CRIT_DF31, "strict_lower_bound": 0,
    "sd_zero": "NO_POSITIVE_CLAIM", "population_only_inference": True,
    "secondary": ["selected_minus_uniform", "matched_minus_uniform",
                  "genomic_pairwise_diversity", "parental_entropy",
                  "G2_horizon_censored", "all_adverse_and_null_populations"],
    "planning_minimum_relevant_effect_steps": 10,
    "historical_S_minus_U_population_sd_steps": 18.012228691488342,
    "S_minus_M_SD_NOT_MEASURED": True,
    "historical_sd_not_a_validated_power_estimate_for_S_minus_M": True,
    "nonretry": True, "no_science_or_world_admission_from_rehearsal": True,
}
PHASES = S.PHASES


def _write_new(path: Path, payload: object) -> None:
    with path.open("xb") as fh:
        fh.write(S._canonical(payload))
        fh.flush()
        os.fsync(fh.fileno())


def _sha_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _validate_plan_path(path: str) -> None:
    if (type(path) is not str or not path.startswith("/") or
            str(Path(path).resolve()) != path or
            Path(path).resolve().is_relative_to(G0.ROOT.resolve())):
        raise PermissionError("absolute canonical custody path outside source required")


def make_panel(root: str, head: str, source: str, archive_root: str) -> dict:
    """Pure extended native Stage6 allocation in a new Stage8-C domain."""
    native = S.make_plan(root, head, source, archive_root)
    key = bytes.fromhex(root)
    selections = []
    extras = []
    for p in range(S.POPS):
        for g in (1, 2):
            secret = hmac.new(key, f"i3-stage8c-matched-key-v1/{p}/{g}".encode("ascii"),
                              sha256).hexdigest()
            selections.append({"population": p, "generation": g, "key_hex": secret})
            for slot in range(S.SLOTS):
                domain = f"i3-stage8c-only-M/{p}/{g}/{slot}"
                extras.append({
                    "population": p, "generation": g,
                    "arm": "matched_multiplicity", "slot": slot,
                    "parent_draw_seed": S._seed(key, "parent_draw_seed", domain),
                    "mutation_seed": S._seed(key, "mutation_seed", domain),
                })
    native["draws"].extend(extras)
    native.update({
        "schema": PANEL_SCHEMA, "protocol": PROTOCOL,
        "status": "STAGE8C_ENGINEERING_ALLOCATED_NOT_EXPOSED",
        "matched_permutations": selections,
        "frozen_method_sha256": S._sha(METHOD),
        "lives_per_generation": list(PANEL_LIVES),
        "planned_lives": sum(PANEL_LIVES),
        "scientific_admission": False,
        "science_decision_authorized": False,
        "no_retry": True,
    })
    all_numbers = [r[k] for r in native["worlds"]
                   for k in ("world_index", "world_seed", "life_seed")]
    all_numbers += [r["genome_seed"] for r in native["founders"]]
    all_numbers += [r[k] for r in native["draws"]
                    for k in ("parent_draw_seed", "mutation_seed")]
    if (len(native["worlds"]) != 288 or len(native["founders"]) != 384
            or len(native["draws"]) != 2304 or
            len(all_numbers) != len(set(all_numbers)) or
            len(set(s["key_hex"] for s in selections)) != 32):
        raise ValueError("duplicate or incomplete Stage8-C native allocation")
    native["allocation_sha256"] = S._sha(
        {k: v for k, v in native.items() if k != "allocation_sha256"})
    return native


def make_plan(root: str, head: str, source: str, archive_root: str) -> dict:
    """Pure two-panel 32-population plan; no birth or World constructed."""
    G0._hex(root, G0.DIGEST, "fresh Stage8-C OS root")
    G0._hex(head, G0.COMMIT, "frozen Stage8-C Git HEAD")
    G0._hex(source, G0.DIGEST, "frozen I3 Python source files SHA")
    _validate_plan_path(archive_root)
    key = bytes.fromhex(root)
    panels = []
    all_numbers = set()
    for i in range(PANELS):
        panel_root = hmac.new(
            key, f"i3-stage8c-disjoint-panel-v1/{i}".encode("ascii"),
            sha256).hexdigest()
        p = make_panel(panel_root, head, source, f"{archive_root}/PANEL_{i}")
        numbers = [w[k] for w in p["worlds"]
                   for k in ("world_index", "world_seed", "life_seed")]
        numbers += [r["genome_seed"] for r in p["founders"]]
        numbers += [r[k] for r in p["draws"]
                    for k in ("parent_draw_seed", "mutation_seed")]
        if all_numbers.intersection(numbers):
            raise ValueError("Stage8-C cross-panel seed collision, discard root")
        all_numbers.update(numbers)
        panels.append(p)
    reserved = [{
        "panel": i, "population": i*S.POPS+w["population"],
        "family": w["family"], "repeat": w["repeat"],
        "world_index": w["world_index"], "world_seed": w["world_seed"],
        "life_seed": w["life_seed"],
    } for i, panel in enumerate(panels) for w in panel["worlds"]
       if w["generation"] == 2]
    if (len(reserved) != HOLDOUT_WORLDS or len({
            (w["population"], w["family"], w["repeat"]) for w in reserved
            }) != HOLDOUT_WORLDS):
        raise ValueError("Stage8-C G2 holdout missing or reused")
    plan = {
        "schema": PLAN_SCHEMA, "status": "STAGE8C_FULL_TECHNICAL_ALLOCATED_NO_SCIENCE",
        "root_hex": root, "source_git_head": head,
        "source_files_sha256": source, "archive_root": archive_root,
        "panels": panels, "frozen_method": METHOD,
        "g2_heldout_worlds_reserved": reserved,
        "g2_heldout_worlds_sha256": S._sha(reserved),
        "planned_original_lives": TOTAL_LIVES,
        "planned_worlds": 576, "planned_mutations": MUTATIONS,
        "scientific_admission": False, "science_generation_disabled": True,
        "owner_scope": "ADR-0022_STAGE8C_NEW_FULL_SCALE_TECHNICAL_ONLY",
        "no_retry": True, "originals_existing_at_allocation": 0,
        "provenance": PROVENANCE,
        "previous_stage6_7_8a_8b_allocations_not_reused": True,
    }
    plan["allocation_sha256"] = S._sha(plan)
    return plan


def verify_plan(plan: object) -> dict:
    if (type(plan) is not dict or plan.get("schema") != PLAN_SCHEMA
            or plan.get("scientific_admission") is not False
            or plan.get("science_generation_disabled") is not True):
        raise PermissionError("Stage8-C is technical only: no scientific admission")
    expected = make_plan(plan.get("root_hex"), plan.get("source_git_head"),
                         plan.get("source_files_sha256"), plan.get("archive_root"))
    if S._canonical(plan) != S._canonical(expected):
        raise PermissionError("Stage8-C altered source, seeds, controls or method")
    return plan


def generation_cases(panel: dict, generation: int, genomes: dict) -> list[dict]:
    """Pure allocation of exactly all original opportunities, not Worlds."""
    if type(generation) is not int or generation not in (0, 1, 2):
        raise ValueError("G must be 0, 1 or 2")
    arms = ("shared",) if generation == 0 else ARMS
    expected = {(p, arm, slot) for p in range(S.POPS)
                for arm in arms for slot in range(S.SLOTS)}
    if set(genomes) != expected:
        raise ValueError("Stage8-C genome set missing an arm/slot")
    worlds = {(w["population"], w["generation"], w["family"], w["repeat"]): w
              for w in panel["worlds"] if w["generation"] == generation}
    if len(worlds) != 96:
        raise ValueError("incomplete precommitted World opportunities")
    from i3.modules.genome import digest, validate
    cases = []
    for pop in range(S.POPS):
        for arm in arms:
            for slot in range(S.SLOTS):
                genome_sha = digest(validate(genomes[pop, arm, slot]))
                for family in S.FAMILIES:
                    for repeat in (0, 1):
                        w = worlds[pop, generation, family, repeat]
                        cases.append({
                            "population": pop, "generation": generation,
                            "arm": arm, "slot": slot, "family": family,
                            "repeat": repeat, "logical_world": w["logical_world"],
                            "world_index": w["world_index"],
                            "world_seed": w["world_seed"],
                            "life_seed": w["life_seed"],
                            "genome_sha256": genome_sha,
                        })
    if len(cases) != PANEL_LIVES[generation]:
        raise ValueError("Stage8-C incomplete G0/G1/G2 case matrix")
    return cases


def native_cases(panel: dict, g: int, genomes: dict) -> list[dict]:
    """Produce original-life identity with shared WorldSpec fingerprint."""
    from i3.lab import p2_ecologies
    from i3.lab import stage6_light_prospective_ecologies as eco
    cases = generation_cases(panel, g, genomes)
    sha = {}
    for case in cases:
        k = (case["population"], case["family"], case["repeat"])
        if k not in sha:
            sha[k] = p2_ecologies.fingerprint(
                eco.world_for_stage6(case["family"], case["world_seed"]))
    return [{
        **{k: v for k, v in c.items() if k != "world_index"},
        "world_sha256": sha[c["population"], c["family"], c["repeat"]],
        "source_sha256": panel["source_files_sha256"],
    } for c in cases]


def reduce_sealed_generation(panel: dict, g: int, root: Path,
                             cases: list[dict], genomes: dict) -> dict:
    """Independently hash originals, validate native bodies, preserve all deaths."""
    from i3.lab import two_phase_panel as TP
    from i3.lab import stage6_light_native_custody_preflight as C
    expected = {(c["population"], c["generation"], c["arm"], c["slot"],
                 c["family"], c["repeat"]): c for c in cases}
    if len(cases) != PANEL_LIVES[g] or len(expected) != len(cases):
        raise ValueError("duplicate expected original-life opportunity")
    seen = set()
    sums = defaultdict(lambda: [0, 0, 0])
    paired = {}
    for identity, life in TP.load_sealed(root / f"G{g}"):
        k = (identity["population"], identity["generation"], identity["arm"],
             identity["slot"], identity["family"], identity["repeat"])
        if (k in seen or k not in expected or identity != expected[k]
                or identity["source_sha256"] != panel["source_files_sha256"]):
            raise ValueError("missing, duplicate or foreign original")
        seen.add(k)
        C._check_native_life(identity, life, panel["source_files_sha256"],
                             panel["source_git_head"], panel["protocol"])
        lived = life.get("steps_lived")
        if (type(life.get("trace")) is not list or
                len(life["trace"]) != lived or
                life["manifest"]["genome"] != genomes[k[0], k[2], k[3]]):
            raise ValueError("native trace or own inherited genome mismatch")
        opportunity = (k[0], k[4], k[5])
        if (opportunity in paired and
                paired[opportunity] != identity["world_sha256"]):
            raise ValueError("arms were not exposed to exactly paired Worlds")
        paired[opportunity] = identity["world_sha256"]
        cell = sums[k[0], k[2], k[3]]
        cell[0] += life["terminal"] == "censored"
        cell[1] += lived
        cell[2] += 1
    if (seen != set(expected) or set(sums) != set(genomes) or
            any(v[2] != 6 for v in sums.values()) or
            len(paired) != 96):
        raise ValueError("unsealed, unbalanced or incomplete three-arm originals")
    return {k: (v[0], v[1]) for k, v in sums.items()}


def choose_three_arm_children(panel: dict, g: int, prior: dict,
                              sealed_fitness: dict, seal: str) -> tuple[dict, list]:
    """S scores sealed; M/U never read fitness. Rebuild native v4 parentage."""
    from i3.modules.genome import digest, mutate, validate
    if g not in (1, 2) or type(seal) is not str or G0.DIGEST.fullmatch(seal) is None:
        raise ValueError("invalid sealed parental generation")
    previous = ("shared",) if g == 1 else ARMS
    expected = {(p, a, s) for p in range(S.POPS)
                for a in previous for s in range(S.SLOTS)}
    if set(prior) != expected or set(sealed_fitness) != expected:
        raise ValueError("wrong or unsealed parent generation")
    drawmap = {(r["population"], r["generation"], r["arm"], r["slot"]): r
               for r in panel["draws"] if r["generation"] == g}
    keys = {(v["population"], v["generation"]): v["key_hex"]
            for v in panel["matched_permutations"]}
    if len(drawmap) != S.POPS*len(ARMS)*S.SLOTS or len(keys) != 32:
        raise ValueError("not all parent/mutation opportunities were frozen")
    out, receipts = {}, []
    for p in range(S.POPS):
        selected_slots = []
        for arm in ("selected", "random_parent"):
            prev = "shared" if g == 1 else arm
            if arm == "selected":
                scores = {s: sealed_fitness[p, prev, s] for s in range(S.SLOTS)}
                rank = sorted(range(S.SLOTS),
                              key=lambda s: (-scores[s][0], -scores[s][1], s))
            for slot in range(S.SLOTS):
                row = drawmap[p, g, arm, slot]
                rng = random.Random(row["parent_draw_seed"])
                parent_slot = (rng.choices(rank, weights=range(S.SLOTS, 0, -1),
                                           k=1)[0] if arm == "selected"
                               else rng.randrange(S.SLOTS))
                if arm == "selected":
                    selected_slots.append(parent_slot)
                parent = validate(prior[p, prev, parent_slot])
                child = validate(mutate(parent, row["mutation_seed"], scale=.1))
                out[p, arm, slot] = child
                receipts.append({
                    "schema": "i3-stage8c-parent-receipt/v1",
                    "population": p, "generation": g, "arm": arm,
                    "parent_generation_arm": prev,
                    "slot": slot, "parent_slot": parent_slot,
                    "draw_seed": row["parent_draw_seed"],
                    "mutation_seed": row["mutation_seed"],
                    "parent_genome_sha256": digest(parent),
                    "offspring_genome_sha256": digest(child),
                    "prior_generation_manifest_sha256": seal,
                })
        native_parents = {s: prior[p, ("shared" if g == 1 else
                                      "matched_multiplicity"), s]
                          for s in range(S.SLOTS)}
        mutations = [drawmap[p, g, "matched_multiplicity", s]["mutation_seed"]
                     for s in range(S.SLOTS)]
        children, m_receipts = M.build_matched_offspring(
            selected_slots, native_parents, mutations,
            parent_generation_arm=("shared" if g == 1 else "matched_multiplicity"),
            population=p, generation=g, key=bytes.fromhex(keys[p, g]),
            prior_manifest_sha256=seal)
        for slot in range(S.SLOTS):
            out[p, "matched_multiplicity", slot] = children[slot]
        if (sorted(Counter(v["parent_slot"] for v in receipts
                           if v["population"] == p and v["generation"] == g
                           and v["arm"] == "selected").values()) !=
                sorted(Counter(v["parent_slot"] for v in m_receipts).values())):
            raise ValueError("matched parent reproduction concentration diverged")
        receipts.extend(m_receipts)
    if len(out) != S.POPS*len(ARMS)*S.SLOTS or len(receipts) != len(out):
        raise ValueError("missing new G1/G2 three-arm descendants")
    return out, receipts


def _fitness_sha(all_fitness: dict) -> str:
    return S._sha([[g, p, a, s, v[0], v[1]]
                   for (g, p, a, s), v in sorted(all_fitness.items())])


def _phase_digest(root: Path) -> str:
    rows = (root / "PHASES.jsonl").read_bytes().splitlines()
    if len(rows) != len(PHASES):
        raise ValueError("one of the 9 sealed G/S/R phases is absent")
    last = None
    for i, raw in enumerate(rows):
        row = json.loads(raw)
        phase = PHASES[i]
        if phase in ("G0", "G1", "G2", "SEAL_G0", "SEAL_G1", "SEAL_G2"):
            payload = root / f"G{phase[-1]}" / "MANIFEST.json"
        elif phase in ("SELECT_G1", "SELECT_G2"):
            payload = root / f"{phase}.json"
        else:
            payload = root / "R_FINAL_ENGINEERING.json"
        if (row.get("phase") != phase or row.get("ordinal") != i or
                row.get("previous_sha256") != last or
                row.get("payload_sha256") != _sha_file(payload) or
                row.get("chain_sha256") != S._sha(
                    {k: v for k, v in row.items() if k != "chain_sha256"})):
            raise ValueError("Stage8-C source-bound original phase chain broken")
        last = row["chain_sha256"]
    return last


def _panel_execute(panel: dict) -> dict:
    """Irreversible 16-population native engineering claim."""
    from i3.lab import two_phase_panel as TP
    from i3.lab import stage6_light_prospective_ecologies as eco
    from i3.runtime.life import run_life
    from i3.modules.genome import digest
    root = Path(panel["archive_root"])
    root.mkdir()  # Claim even if an early phase fails: no retry.
    _write_new(root / "CLAIM.json", {
        "schema": "i3-stage8c-panel-one-shot-claim/v1",
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
        "plan_sha256": panel["allocation_sha256"],
        "scientific_admission": False, "source_git_head": panel["source_git_head"]})
    phases, totals, fitness_all = [], [], {}
    genomes = S.founder_genomes(panel)
    founders = [{
        "population": r["population"], "slot": r["slot"],
        "genome_seed": r["genome_seed"],
        "genome": genomes[r["population"], "shared", r["slot"]],
        "genome_sha256": digest(genomes[r["population"], "shared", r["slot"]]),
    } for r in panel["founders"]]
    _write_new(root / "FOUNDERS.json", founders)
    try:
        for g in (0, 1, 2):
            cases = native_cases(panel, g, genomes)
            def one(case):
                spec = eco.world_for_stage6(case["family"], case["world_seed"])
                genome = genomes[case["population"], case["arm"], case["slot"]]
                life = run_life(genome, spec, case["life_seed"], S.HORIZON,
                                keep_trace=True, protocol=panel["protocol"],
                                decision_policy="reference")
                if life.get("genome") != case["genome_sha256"]:
                    raise RuntimeError("born native genotype not frozen genotype")
                return life
            generated = TP.generate(cases, one, root / f"G{g}")
            if (generated["status"] != "GENERATED" or
                    generated["generated"] != PANEL_LIVES[g]):
                raise RuntimeError("incomplete native original G: NO_RETRY")
            original_sha = _sha_file(root / f"G{g}" / "MANIFEST.json")
            phases = S._append_phase(root, f"G{g}", original_sha, phases)
            original_fitness = reduce_sealed_generation(
                panel, g, root, cases, genomes)
            for (p, arm, slot), score in original_fitness.items():
                fitness_all[g, p, arm, slot] = score
            phases = S._append_phase(root, f"SEAL_G{g}", original_sha, phases)
            totals.append({"generation": g, "lives": PANEL_LIVES[g],
                           "manifest_sha256": original_sha})
            if g in (0, 1):
                next_g = g + 1
                children, receipts = choose_three_arm_children(
                    panel, next_g, genomes, original_fitness, original_sha)
                claims = [{
                    "population": p, "arm": a, "slot": s,
                    "genome": children[p, a, s], "genome_sha256": digest(children[p, a, s]),
                } for p in range(S.POPS) for a in ARMS for s in range(S.SLOTS)]
                target = root / f"SELECT_G{next_g}.json"
                _write_new(target, {
                    "schema": "i3-stage8c-sealed-three-arm-parentage/v1",
                    "generation": next_g, "prior_generation_manifest_sha256": original_sha,
                    "draws": receipts, "offspring": claims,
                })
                phases = S._append_phase(root, f"SELECT_G{next_g}",
                                         _sha_file(target), phases)
                genomes = children
        reduced = {"schema": "i3-stage8c-full-native-rehearsal-end/v1",
                   "status": TECH_PASS,
                   "science_result_disclosed": False,
                   "scientific_admission": False,
                   "original_lives": sum(v["lives"] for v in totals),
                   "generation_seals": totals,
                   "reduction_sha256": _fitness_sha(fitness_all),
                   "no_retry": True}
        final = root / "R_FINAL_ENGINEERING.json"
        _write_new(final, reduced)
        phases = S._append_phase(root, "R_FINAL", _sha_file(final), phases)
        if len(phases) != 9:
            raise RuntimeError("not all 9 native stages sealed")
        return {"status": TECH_PASS, "original_lives": sum(PANEL_LIVES),
                "phase_chain_sha256": phases[-1]["chain_sha256"],
                "plan_sha256": panel["allocation_sha256"],
                "scientific_admission": False}
    except BaseException as exc:
        _write_new(root / "FAILURE.json", {
            "schema": "i3-stage8c-failure-v1", "status": "TECHNICAL_NO_VERDICT_NO_RETRY",
            "error_type": type(exc).__name__, "phase_index": len(phases),
            "no_retry": True})
        raise


def run_engineering(plan: dict, destination: str, expected_sha: str) -> dict:
    verify_plan(plan)
    if destination != plan["archive_root"] or expected_sha != plan["allocation_sha256"]:
        raise PermissionError("source-frozen published plan required to claim original archive")
    G0._verify_checkout(plan["panels"][0])
    root = Path(destination)
    root.mkdir()  # Single attempt. NO exist_ok or replacement roots.
    _write_new(root / "CLAIM.json", {
        "schema": "i3-stage8c-full-technical-claim/v1",
        "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
        "allocation_sha256": plan["allocation_sha256"],
        "source_git_head": plan["source_git_head"],
        "scientific_admission": False})
    cores = []
    try:
        for i, panel in enumerate(plan["panels"]):
            _write_new(root / f"PANEL_{i}_PLAN.json", panel)
            core = _panel_execute(panel)
            _write_new(root / f"PANEL_{i}_CORE.json", core)
            cores.append(core)
        if len(cores) != PANELS or sum(x["original_lives"] for x in cores) != TOTAL_LIVES:
            raise RuntimeError("not two complete 16-population three-arm panels")
        return {
            "schema": "i3-stage8c-two-panel-technical-core/v1",
            "status": TECH_PASS, "source_git_head": plan["source_git_head"],
            "plan_sha256": plan["allocation_sha256"],
            "g2_holdout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
            "panel_chain_sha256": [x["phase_chain_sha256"] for x in cores],
            "original_lives": TOTAL_LIVES,
            "scientific_admission": False, "science_decision_disclosed": False,
            "no_retry": True}
    except BaseException as exc:
        _write_new(root / "FAILURE.json", {
            "schema": "i3-stage8c-technical-abort/v1",
            "status": "TECHNICAL_NO_VERDICT_NO_RETRY", "error_type": type(exc).__name__,
            "panels_completed": len(cores), "no_retry": True})
        raise


def _panel_reaudit(panel: dict, root: Path) -> dict:
    """Full original gzip rehash plus own-arm genealogy reconstruction."""
    from i3.modules.genome import digest
    if ((root / "FAILURE.json").exists() or
            json.loads((root / "CLAIM.json").read_bytes()).get("plan_sha256") !=
            panel["allocation_sha256"]):
        raise ValueError("invalid technical one-shot custody")
    observed_founders = json.loads((root / "FOUNDERS.json").read_bytes())
    genomes = S.founder_genomes(panel)
    expected_founders = [{
        "population": v["population"], "slot": v["slot"],
        "genome_seed": v["genome_seed"],
        "genome": genomes[v["population"], "shared", v["slot"]],
        "genome_sha256": digest(genomes[v["population"], "shared", v["slot"]]),
    } for v in panel["founders"]]
    if observed_founders != expected_founders:
        raise ValueError("founder genomes changed")
    fitness_all = {}
    for g in (0, 1, 2):
        cases = native_cases(panel, g, genomes)
        fitness = reduce_sealed_generation(panel, g, root, cases, genomes)
        for (p, a, s), value in fitness.items():
            fitness_all[g, p, a, s] = value
        seal = _sha_file(root / f"G{g}/MANIFEST.json")
        if g < 2:
            nextg = g + 1
            children, receipts = choose_three_arm_children(
                panel, nextg, genomes, fitness, seal)
            observed = json.loads((root / f"SELECT_G{nextg}.json").read_bytes())
            expected = {
                "schema": "i3-stage8c-sealed-three-arm-parentage/v1",
                "generation": nextg, "prior_generation_manifest_sha256": seal,
                "draws": receipts,
                "offspring": [{
                    "population": p, "arm": a, "slot": s,
                    "genome": children[p, a, s],
                    "genome_sha256": digest(children[p, a, s]),
                } for p in range(S.POPS) for a in ARMS for s in range(S.SLOTS)],
            }
            if S._canonical(observed) != S._canonical(expected):
                raise ValueError("sealed selections or mutations not reproducible")
            genomes = children
    final = json.loads((root / "R_FINAL_ENGINEERING.json").read_bytes())
    if (final.get("status") != TECH_PASS or
            final.get("scientific_admission") is not False or
            final.get("science_result_disclosed") is not False or
            final.get("original_lives") != sum(PANEL_LIVES) or
            final.get("reduction_sha256") != _fitness_sha(fitness_all)):
        raise ValueError("technical reduction differs from sealed originals")
    return {"original_lives": sum(PANEL_LIVES),
            "phase_chain_sha256": _phase_digest(root)}


def technical_receipt(plan_path: str, original_root: str, core_path: str,
                      version: str, run_id: int) -> dict:
    plan = verify_plan(json.loads(Path(plan_path).read_bytes()))
    root = Path(original_root)
    core = json.loads(Path(core_path).read_bytes())
    if (str(root.resolve()) != plan["archive_root"] or
            version not in ("3.11", "3.12") or
            type(run_id) is not int or run_id <= 0 or
            (root / "FAILURE.json").exists() or
            core.get("status") != TECH_PASS or
            core.get("plan_sha256") != plan["allocation_sha256"] or
            core.get("g2_holdout_worlds_sha256") != plan["g2_heldout_worlds_sha256"] or
            core.get("original_lives") != TOTAL_LIVES or
            core.get("scientific_admission") is not False or
            core.get("science_decision_disclosed") is not False):
        raise ValueError("not a complete source-locked Stage8-C technical rehearsal")
    sealed = []
    for i, panel in enumerate(plan["panels"]):
        if json.loads((root / f"PANEL_{i}_PLAN.json").read_bytes()) != panel:
            raise ValueError("source-exact panel allocation changed")
        audit = _panel_reaudit(panel, root / f"PANEL_{i}")
        previous_core = json.loads((root / f"PANEL_{i}_CORE.json").read_bytes())
        if (audit["phase_chain_sha256"] != core["panel_chain_sha256"][i] or
                previous_core["phase_chain_sha256"] != audit["phase_chain_sha256"] or
                previous_core["original_lives"] != sum(PANEL_LIVES) or
                previous_core["status"] != TECH_PASS):
            raise ValueError("one technical panel not sealed or reaudited")
        sealed.append(audit)
    return {
        "schema": RECEIPT_SCHEMA, "status": TECH_PASS,
        "python_version": version, "workflow_run_id": run_id,
        "source_git_head": plan["source_git_head"],
        "source_files_sha256": plan["source_files_sha256"],
        "allocation_sha256": plan["allocation_sha256"],
        "archive_root": plan["archive_root"],
        "g2_holdout_worlds_sha256": plan["g2_heldout_worlds_sha256"],
        "root_commitment_sha256": S._sha([x["root_hex"] for x in plan["panels"]]),
        "panel_audit_sha256": S._sha(sealed),
        "native_original_lives_rehashed": TOTAL_LIVES,
        "native_mutations_reproduced": MUTATIONS,
        "phase_count": len(PHASES)*PANELS,
        "scientific_admission": False, "no_retry": True,
        "provenance": PROVENANCE,
    }


def combine_receipts(r311: dict, r312: dict) -> dict:
    expected = {
        "schema", "status", "python_version", "workflow_run_id",
        "source_git_head", "source_files_sha256", "allocation_sha256",
        "archive_root", "g2_holdout_worlds_sha256",
        "root_commitment_sha256", "panel_audit_sha256",
        "native_original_lives_rehashed", "native_mutations_reproduced",
        "phase_count", "scientific_admission", "no_retry", "provenance",
    }
    receipts = {"3.11": r311, "3.12": r312}
    for version, r in receipts.items():
        if (type(r) is not dict or set(r) != expected or
                r["schema"] != RECEIPT_SCHEMA or r["status"] != TECH_PASS or
                r["python_version"] != version or
                r["native_original_lives_rehashed"] != TOTAL_LIVES or
                r["native_mutations_reproduced"] != MUTATIONS or
                r["phase_count"] != 18 or
                r["scientific_admission"] is not False or
                r["no_retry"] is not True or r["provenance"] != PROVENANCE or
                type(r["workflow_run_id"]) is not int or
                r["workflow_run_id"] <= 0 or
                any(type(r[k]) is not str or G0.DIGEST.fullmatch(r[k]) is None
                    for k in ("source_files_sha256", "allocation_sha256",
                              "g2_holdout_worlds_sha256", "root_commitment_sha256",
                              "panel_audit_sha256")) or
                type(r["source_git_head"]) is not str or
                G0.COMMIT.fullmatch(r["source_git_head"]) is None):
            raise PermissionError("not two fully sealed 32-population Stage8-C technical receipts")
    if (r311["workflow_run_id"] != r312["workflow_run_id"] or
            r311["source_git_head"] != r312["source_git_head"] or
            r311["source_files_sha256"] != r312["source_files_sha256"] or
            any(r311[k] == r312[k] for k in
                ("allocation_sha256", "root_commitment_sha256",
                 "g2_holdout_worlds_sha256", "archive_root"))):
        raise PermissionError("not independent technical roots on one frozen Git source")
    return {
        "schema": "i3-stage8c-both-complete-technical-rehearsals/v1",
        "status": "STAGE8C_TWO_TECHNICAL_REPETITIONS_COMPLETE_NO_SCIENCE",
        "source_git_head": r311["source_git_head"],
        "source_files_sha256": r311["source_files_sha256"],
        "workflow_run_id": r311["workflow_run_id"],
        "engineering_rehearsal_receipts_sha256": S._sha(receipts),
        "native_original_lives_rehashed": 2*TOTAL_LIVES,
        "scientific_admission": False,
        "science_lives_generated": 0,
        "stage2_scientific_verdict": "NOT_ISSUED",
        "provenance": PROVENANCE,
    }


def reduce_primary_g2(differences: list[float]) -> dict:
    """Frozen analysis function, PURE; NO science admission or native life."""
    if (type(differences) is not list or len(differences) != POPULATIONS or
            any(type(x) not in (int, float) or not math.isfinite(x)
                for x in differences)):
        raise ValueError("exactly 32 finite population-level S-M contrasts required")
    xs = [float(x) for x in differences]
    m = math.fsum(xs)/POPULATIONS
    sd = math.sqrt(math.fsum((x-m)**2 for x in xs)/(POPULATIONS-1))
    lower = m - CRIT_DF31*sd/math.sqrt(POPULATIONS)
    return {
        "status": ("STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0"
                   if sd > 0 and lower > 0 else
                   "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0"),
        "population_units": POPULATIONS, "mean_G2_S_minus_M_steps": m,
        "sd_G2_S_minus_M_steps": sd,
        "one_sided_97_5_percent_lower_bound_steps": lower,
        "positive_populations": sum(x > 0 for x in xs),
        "negative_populations": sum(x < 0 for x in xs),
        "zero_populations": sum(x == 0 for x in xs),
        "all_population_contrasts": xs,
        "condition": "population_independence_and_t_approximation_unproven",
    }


def main() -> None:
    args = sys.argv
    if len(args) == 6 and args[1] == "allocate-engineering":
        _, _, head, sources, dest, original = args
        plan = make_plan(secrets.token_hex(32), head, sources, original)
        _write_new(Path(dest), plan)
        print(json.dumps({"status": plan["status"], "plan_sha256": plan["allocation_sha256"],
                          "original_lives_generated": 0}))
    elif len(args) == 3 and args[1] == "verify":
        p = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps({"status": p["status"], "allocation_sha256": p["allocation_sha256"]}))
    elif len(args) == 5 and args[1] == "run-engineering":
        plan = verify_plan(json.loads(Path(args[2]).read_bytes()))
        print(json.dumps(run_engineering(plan, args[3], args[4]), sort_keys=True))
    elif len(args) == 8 and args[1] == "rehearsal-receipt":
        _, _, plan, original, core, dest, version, run_id = args
        receipt = technical_receipt(plan, original, core, version, int(run_id))
        _write_new(Path(dest), receipt)
        print(json.dumps({"status": receipt["status"],
                          "native_original_lives_rehashed": TOTAL_LIVES}))
    elif len(args) == 5 and args[1] == "combine-rehearsals":
        _, _, path311, path312, dest = args
        a = json.loads(Path(path311).read_bytes())
        b = json.loads(Path(path312).read_bytes())
        result = combine_receipts(a, b)
        _write_new(Path(dest), result)
        print(json.dumps({"status": result["status"], "science_lives_generated": 0}))
    else:
        raise SystemExit(
            "Stage8C technical-only: allocate-engineering|verify|run-engineering|rehearsal-receipt|combine-rehearsals")


if __name__ == "__main__":
    main()
