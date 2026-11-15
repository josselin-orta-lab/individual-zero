"""Native I3 Stage6-light full G/S/R ENGINEERING transport, not science.

ADR-0022 permits prospective laboratory research without external witnesses.
This candidate prepares a source-locked, one-shot 11,520-life full *technical*
rehearsal, using genuine I3 P1.3 funded-v2 minds/Worlds. No full rehearsal is
started on import, in tests, by allocating, or by opening a PR. Scientific
admission requires a separate, prospective source-locked method after both
Python 3.11 and 3.12 full-scale engineering rehearsals actually pass.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import random
import secrets
import sys

from . import stage6_light_native_g0_transport as G0

SCHEMA = "i3-stage6-light-native-gsr-engineering-plan/v1"
PROTOCOL = "i3-stage6-light-native-gsr-engineering-funded-v2/v1"
SCIENCE_SCHEMA = "i3-stage6-light-native-gsr-science-plan/v1"
SCIENCE_PROTOCOL = "i3-stage6-light-native-gsr-science-funded-v2/v1"
PHASES = ("G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
          "SELECT_G2", "G2", "SEAL_G2", "R_FINAL")
ARMS = ("selected", "random_parent")
FAMILIES = ("stable", "depletion", "pulse")
POPS, SLOTS, HORIZON = 16, 24, 400
BASES = {key: i << 60 for i, key in enumerate(
    ("world_index", "world_seed", "life_seed", "genome_seed",
     "parent_draw_seed", "mutation_seed"), start=1)}
MASK = (1 << 60) - 1
EXPECTED_GENERATION = (2304, 4608, 4608)
SCIENTIFIC_ADMISSION = False


def _canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(data: object) -> str:
    return sha256(_canonical(data)).hexdigest()


def _seed(root: bytes, domain: str, parts: str) -> int:
    encoded = f"i3-stage6-gsr-engineering-v1/{domain}/{parts}".encode("ascii")
    return BASES[domain] + (int.from_bytes(
        hmac.new(root, encoded, sha256).digest()[:8], "big") & MASK)


def make_plan(root_hex: str, source_git_head: str, source_files_sha256: str,
              archive_root: str) -> dict:
    """Pure deterministic allocation; no World, birth or full study starts."""
    G0._hex(root_hex, G0.DIGEST, "new engineering root")
    G0._hex(source_git_head, G0.COMMIT, "pinned commit")
    G0._hex(source_files_sha256, G0.DIGEST, "pinned source map")
    method_sha, direction_sha = G0._pins()
    if (type(archive_root) is not str or not archive_root.startswith("/")
            or Path(archive_root).resolve().as_posix() != archive_root
            or Path(archive_root).resolve().is_relative_to(G0.ROOT.resolve())):
        raise PermissionError("archive_root must be a canonical absolute path outside checkout")
    root = bytes.fromhex(root_hex)
    worlds = []
    for p in range(POPS):
        for g in range(3):
            for f, family in enumerate(FAMILIES):
                for repeat in range(2):
                    key = f"{p}/{g}/{family}/{repeat}"
                    worlds.append({
                        "population": p, "generation": g, "family": family,
                        "repeat": repeat,
                        "logical_world": ((p*3+g)*3+f)*2+repeat,
                        "world_index": _seed(root, "world_index", key),
                        "world_seed": _seed(root, "world_seed", key),
                        "life_seed": _seed(root, "life_seed", key),
                    })
    founders = [
        {"population": p, "slot": slot,
         "genome_seed": _seed(root, "genome_seed", f"{p}/{slot}")}
        for p in range(POPS) for slot in range(SLOTS)
    ]
    draws = [
        {"population": p, "generation": g, "arm": arm, "slot": slot,
         "parent_draw_seed": _seed(root, "parent_draw_seed",
                                  f"{p}/{g}/{arm}/{slot}"),
         "mutation_seed": _seed(root, "mutation_seed",
                               f"{p}/{g}/{arm}/{slot}")}
        for p in range(POPS) for g in (1, 2) for arm in ARMS
        for slot in range(SLOTS)
    ]
    seeds = [r[k] for r in worlds
             for k in ("world_index", "world_seed", "life_seed")]
    seeds.extend(r["genome_seed"] for r in founders)
    seeds.extend(r[k] for r in draws
                 for k in ("parent_draw_seed", "mutation_seed"))
    if (len(worlds) != 288 or len(founders) != 384 or len(draws) != 1536
            or len(seeds) != len(set(seeds))
            or any(type(seed) is not int or seed < 1 << 60
                   or seed >= 7 << 60 for seed in seeds)):
        raise ValueError("collision or invalid namespace: discard entire allocation root")
    plan = {
        "schema": SCHEMA, "protocol": PROTOCOL,
        "status": "FULL_ENGINEERING_ALLOCATED_NOT_EXPOSED",
        "reference": "P1.3 funded-v2", "decision_policy": "reference",
        "root_hex": root_hex, "archive_root": archive_root,
        "source_git_head": source_git_head,
        "source_files_sha256": source_files_sha256,
        "method_sha256": method_sha, "owner_direction_sha256": direction_sha,
        "worlds": worlds, "founders": founders, "draws": draws,
        "phases": list(PHASES), "horizon": HORIZON,
        "lives_per_generation": list(EXPECTED_GENERATION),
        "planned_lives": sum(EXPECTED_GENERATION), "planned_worlds": 288,
        "no_retry": True, "scientific_admission": False,
        "external_custody": False,
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
        "actual_lives_at_allocation": 0,
    }
    plan["allocation_sha256"] = _sha(plan)
    return plan


def verify_plan(plan: object) -> dict:
    if type(plan) is not dict or plan.get("schema") != SCHEMA:
        raise PermissionError("missing or foreign prospective engineering plan")
    expected = make_plan(plan.get("root_hex"), plan.get("source_git_head"),
                         plan.get("source_files_sha256"), plan.get("archive_root"))
    if _canonical(plan) != _canonical(expected):
        raise PermissionError("tampered or broadened source/seed/method plan")
    return plan


def _check_rehearsals(receipts: dict, head: str, source_sha: str) -> None:
    """Two distinct, source-exact FULL rehearsal receipts, not toy CI."""
    if type(receipts) is not dict or set(receipts) != {"3.11", "3.12"}:
        raise PermissionError("both full-scale Python rehearsal receipts required")
    keys = {"schema", "status", "python_version", "source_git_head",
            "source_files_sha256", "allocation_sha256", "last_chain_sha256",
            "lives_archived", "planned_worlds", "phase_count",
            "archive_sha256", "reduction_sha256", "science_admission",
            "no_retry", "workflow_run_id", "job_name"}
    allocations = set()
    for version in ("3.11", "3.12"):
        r = receipts[version]
        if type(r) is not dict or set(r) != keys:
            raise PermissionError("missing or extra full rehearsal evidence")
        if (r["schema"] != "i3-stage6-rehearsal-receipt/v1" or
                r["status"] != "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE" or
                r["python_version"] != version or
                r["source_git_head"] != head or
                r["source_files_sha256"] != source_sha or
                r["lives_archived"] != 11520 or r["planned_worlds"] != 288 or
                r["phase_count"] != 9 or
                r["science_admission"] is not False or
                r["no_retry"] is not True or
                type(r["workflow_run_id"]) is not int or
                r["workflow_run_id"] <= 0 or
                r["job_name"] != f"engineering-{version}" or
                any(type(r[k]) is not str or
                    G0.DIGEST.fullmatch(r[k]) is None
                    for k in ("allocation_sha256", "last_chain_sha256",
                              "archive_sha256", "reduction_sha256"))):
            raise PermissionError("full rehearsals do not prove source-exact technical readiness")
        allocations.add(r["allocation_sha256"])
    if len(allocations) != 2:
        raise PermissionError("two independent rehearsal root allocations required")


def make_science_plan(root_hex: str, source_git_head: str,
                      source_files_sha256: str, archive_root: str,
                      rehearsals: dict) -> dict:
    """One distinct, prospective internally attested scientific allocation.

    The frozen legacy Stage6 method remains deny-all, but ADR-0022 already
    authorizes separately source-locked prospective laboratory science.
    """
    _check_rehearsals(rehearsals, source_git_head, source_files_sha256)
    owner = json.loads(G0.DIRECTION.read_bytes())
    allowed = owner.get("applies_to", {})
    needs = owner.get("prospective_execution_requirements", {})
    if (allowed.get("scientific_prospective_experiments_authorized") is not True
            or allowed.get("stage6_light_gsr_lineage_exception_adr0017_accepted") is not True
            or needs.get("run_specific_admission_manifest_required") is not True
            or needs.get("complete_source_exact_engineering_rehearsal_for_stage6_science_required") is not True
            or needs.get("all_originals_favorable_adverse_null_required") is not True):
        raise PermissionError("owner research direction does not permit native Stage6 science")
    p = make_plan(root_hex, source_git_head, source_files_sha256,
                  archive_root)
    if p["allocation_sha256"] in {r["allocation_sha256"]
                                  for r in rehearsals.values()}:
        raise PermissionError("science must have fresh independent allocation")
    del p["allocation_sha256"]
    p.update({
        "schema": SCIENCE_SCHEMA,
        "protocol": SCIENCE_PROTOCOL,
        "status": "PROSPECTIVE_SCIENCE_ALLOCATED_NOT_EXPOSED",
        "scientific_admission": True,
        "science_scope": "F0_ONLY_DIRECTIONAL_PARAMETER_NOT_SURVIVAL_ADVANTAGE",
        "fixed_primary": "beta_u_eff",
        "fixed_sign_threshold": 13,
        "fixed_neutral_sentinels": [
            "omega", "temperament.affiliation",
            "temperament.reward_sensitivity"],
        "fixed_neutral_invalid_at": 2,
        "engineering_full_scale_receipts": rehearsals,
        "scientific_verdict_before_exposure": "NOT_ISSUED",
        "source_of_science_authorization": "ADR-0022_SEPARATE_SCOPE",
    })
    p["allocation_sha256"] = _sha(p)
    return p


def verify_science_plan(plan: object) -> dict:
    if type(plan) is not dict or plan.get("schema") != SCIENCE_SCHEMA:
        raise PermissionError("no separate source-locked science admission plan")
    expected = make_science_plan(
        plan.get("root_hex"), plan.get("source_git_head"),
        plan.get("source_files_sha256"), plan.get("archive_root"),
        plan.get("engineering_full_scale_receipts"))
    if _canonical(expected) != _canonical(plan):
        raise PermissionError("changed science source, method, seeds or rehearsal evidence")
    return plan



def founder_genomes(plan: dict) -> dict:
    """Only innate v4 genes, never inherited memory or World facts."""
    from i3.modules.genome import generation_zero, validate
    genomes = {(r["population"], "shared", r["slot"]):
               validate(generation_zero(r["genome_seed"]))
               for r in plan["founders"]}
    if len(genomes) != 384:
        raise ValueError("duplicate G0 founder identity")
    return genomes


def generation_cases(plan: dict, generation: int, genomes: dict) -> list[dict]:
    if type(generation) is not int or generation not in (0, 1, 2):
        raise ValueError("invalid lineage generation")
    from i3.modules.genome import digest as genome_digest, validate
    worlds = {(w["population"], w["generation"], w["family"], w["repeat"]): w
              for w in plan["worlds"] if w["generation"] == generation}
    if len(worlds) != 96:
        raise ValueError("not exactly 96 distinct G opportunities")
    arms = ("shared",) if generation == 0 else ARMS
    expected = {(p, arm, slot) for p in range(POPS)
                for arm in arms for slot in range(SLOTS)}
    if set(genomes) != expected:
        raise ValueError("genome matrix is incomplete, duplicated or foreign")
    cases = []
    for p in range(POPS):
        for arm in arms:
            for slot in range(SLOTS):
                genome = validate(genomes[p, arm, slot])
                for family in FAMILIES:
                    for repeat in range(2):
                        w = worlds[p, generation, family, repeat]
                        cases.append({
                            "population": p, "generation": generation,
                            "arm": arm, "slot": slot, "family": family,
                            "repeat": repeat, "logical_world": w["logical_world"],
                            "world_index": w["world_index"],
                            "world_seed": w["world_seed"], "life_seed": w["life_seed"],
                            "genome_sha256": genome_digest(genome),
                        })
    if len(cases) != EXPECTED_GENERATION[generation]:
        raise ValueError("exact frozen life coverage not constructed")
    return cases




def native_archive_cases(plan: dict, generation: int,
                         genomes: dict) -> list[dict]:
    """Materialize exactly the immutable native-original custody identity ABI.

    This is live engineering only, after the source-exact no-retry archive claim.
    No operator-supplied fitness or hidden information is introduced.
    """
    from i3.lab import p2_ecologies
    from i3.lab import stage6_light_prospective_ecologies as stage6_ecologies
    logical_cases = generation_cases(plan, generation, genomes)
    digests = {}
    for case in logical_cases:
        key = (case["population"], case["family"], case["repeat"])
        if key not in digests:
            spec = stage6_ecologies.world_for_stage6(
                case["family"], case["world_seed"])
            digests[key] = p2_ecologies.fingerprint(spec)
    return [
        {**{k: v for k, v in row.items() if k != "world_index"},
         "world_sha256": digests[row["population"], row["family"], row["repeat"]],
         "source_sha256": plan["source_files_sha256"]}
        for row in logical_cases
    ]

def choose_descendants(plan: dict, next_generation: int, prior: dict,
                       persistence: dict, prior_manifest_sha256: str) -> tuple[dict, list[dict]]:
    """Predeclared linear-rank persistence vs score-blind uniform parents.

    The random_parent branch has no access to, and does not query,
    persistence scores. The caller must first authenticate/seal G originals.
    """
    if type(next_generation) is not int or next_generation not in (1, 2):
        raise ValueError("only G0->G1 or G1->G2 is permitted")
    if (type(prior_manifest_sha256) is not str or
            G0.DIGEST.fullmatch(prior_manifest_sha256) is None):
        raise ValueError("missing prior-generation sealed original SHA")
    from i3.modules.genome import validate, mutate, digest as genome_digest
    prior_arm = ("shared",) if next_generation == 1 else ARMS
    expected = {(p, arm, slot) for p in range(POPS)
                for arm in prior_arm for slot in range(SLOTS)}
    if set(prior) != expected:
        raise ValueError("incomplete or foreign parental genomes")
    if set(persistence) != expected:
        raise ValueError("persistence derived from wrong sealed generation")
    lookup = {(r["population"], r["generation"], r["arm"], r["slot"]): r
              for r in plan["draws"] if r["generation"] == next_generation}
    if len(lookup) != POPS*len(ARMS)*SLOTS:
        raise ValueError("incomplete frozen draw/mutation allocation")
    children, receipts = {}, []
    for p in range(POPS):
        for arm in ARMS:
            prev = "shared" if next_generation == 1 else arm
            if arm == "selected":
                # Read each prior individual's sealed persistence exactly once.
                # Random-parent branch never touches this table or cache.
                score_cache = {s: persistence[p, prev, s]
                               for s in range(SLOTS)}
                ranking = sorted(range(SLOTS), key=lambda s: (
                    -score_cache[s][0], -score_cache[s][1], s))
            for slot in range(SLOTS):
                row = lookup[p, next_generation, arm, slot]
                rng = random.Random(row["parent_draw_seed"])
                if arm == "selected":
                    parent_slot = rng.choices(
                        ranking, weights=range(SLOTS, 0, -1), k=1)[0]
                else:
                    parent_slot = rng.randrange(SLOTS)
                parent = validate(prior[p, prev, parent_slot])
                child = mutate(parent, row["mutation_seed"], scale=0.1)
                validate(child)
                children[p, arm, slot] = child
                receipts.append({
                    "schema": "i3-stage6-parent-draw-supplied-claim/v1",
                    "population": p, "generation": next_generation,
                    "arm": arm, "slot": slot, "parent_slot": parent_slot,
                    "parent_genome_sha256": genome_digest(parent),
                    "offspring_genome_sha256": genome_digest(child),
                    "draw_seed": row["parent_draw_seed"],
                    "prior_generation_manifest_sha256": prior_manifest_sha256,
                })
    if len(children) != 768 or len(receipts) != 768:
        raise RuntimeError("missing selected or random-parent offspring")
    return children, receipts


def _summary_scores(rows, generation: int,
                    expected_cases: list[dict], genomes: dict,
                    source_sha: str, source_head: str,
                    protocol: str) -> dict:
    """Reduce only sealed original persistence, never output fitness to operator."""
    from i3.modules.genome import digest as genome_digest
    from i3.lab import p2_ecologies
    from i3.lab import stage6_light_prospective_ecologies as stage6_ecologies
    expected = {(r["population"], r["generation"], r["arm"], r["slot"],
                 r["family"], r["repeat"]): r for r in expected_cases}
    if len(expected) != EXPECTED_GENERATION[generation]:
        raise ValueError("case plan has missing or repeated life")
    observed, sums = set(), defaultdict(lambda: [0, 0, 0])
    world_fingerprints = {}
    count = 0
    for case, life in rows:
        count += 1
        key = (case["population"], case["generation"], case["arm"], case["slot"],
               case["family"], case["repeat"])
        if key not in expected or key in observed or case != expected[key]:
            raise ValueError("corrupted original case binding")
        observed.add(key)
        ancestor = genomes[case["population"], case["arm"], case["slot"]]
        manifest = life.get("manifest", {})
        source = manifest.get("source", {})
        billing = life.get("cognitive_accounting", {})
        paid = billing.get("totals", {})
        opportunity = (case["population"], case["family"], case["repeat"])
        if opportunity not in world_fingerprints:
            spec = stage6_ecologies.world_for_stage6(
                case["family"], case["world_seed"])
            world_fingerprints[opportunity] = p2_ecologies.fingerprint(spec)
        if (life.get("genome") != genome_digest(ancestor)
                or manifest.get("genome") != ancestor
                or manifest.get("world_sha256") != world_fingerprints[opportunity]
                or manifest.get("world_sha256") != case["world_sha256"]
                or manifest.get("execution_model") != "i3-funded-v2"
                or manifest.get("protocol") != protocol
                or source.get("sha256") != source_sha
                or source.get("git_head") != source_head
                or source.get("working_tree_dirty") is not False
                or life.get("life_seed") != case["life_seed"]
                or billing.get("status") != "SETTLED_FOR_DECLARED_WORK"
                or billing.get("shortfall_steps") != 0
                or set(paid) != {"energy", "vigilance"}
                or any(paid[c].get("unpaid", float("inf")) > 1e-12
                       for c in ("energy", "vigilance"))
                or not 0 < life.get("steps_lived", 0) <= HORIZON
                or life.get("terminal") not in ("dead", "censored")
                or (life["terminal"] == "censored" and life["steps_lived"] != HORIZON)
                or type(life.get("death_causes")) is not list
                or bool(life["death_causes"]) != (life["terminal"] == "dead")
                or type(life.get("trace")) is not list):
            raise ValueError("untrusted native source, funding, World, trace or death")
        bucket = sums[case["population"], case["arm"], case["slot"]]
        bucket[0] += life["terminal"] == "censored"
        bucket[1] += life["steps_lived"]
        bucket[2] += 1
    if count != len(expected) or observed != set(expected):
        raise ValueError("original coverage incomplete")
    if set(sums) != set(genomes) or any(v[2] != 6 for v in sums.values()):
        raise ValueError("not all six original contexts are present per genome")
    return {key: (value[0], value[1]) for key, value in sums.items()}


def _metric(genome: dict, key: str) -> float:
    g = genome["genes"]
    return (g["beta_u"] * (1 + .5*g["temperament.exploration"])
            if key == "beta_u_eff" else g[key])


def final_contrasts(genomes: dict) -> dict:
    """Frozen 16 population contrasts, with neutral sentinel invalidation."""
    keys = ("beta_u_eff", "omega", "temperament.affiliation",
            "temperament.reward_sensitivity")
    if set(genomes) != {(p, arm, s) for p in range(POPS)
                       for arm in ARMS for s in range(SLOTS)}:
        raise ValueError("G2 genome population is incomplete")
    contrasts = {}
    for key in keys:
        values = []
        for p in range(POPS):
            a = sum(_metric(genomes[p, "selected", s], key)
                    for s in range(SLOTS))/SLOTS
            b = sum(_metric(genomes[p, "random_parent", s], key)
                    for s in range(SLOTS))/SLOTS
            values.append(a-b)
        plus = sum(x > 0 for x in values)
        minus = sum(x < 0 for x in values)
        contrasts[key] = {"values": values, "plus": plus,
                          "minus": minus, "zero": POPS-plus-minus,
                          "direction_concordant": max(plus, minus) >= 13}
    neutral_alert_count = sum(
        contrasts[k]["direction_concordant"] for k in keys[1:])
    invalid = neutral_alert_count >= 2
    return {
        "schema": "i3-stage6-light-frozen-population-sign-analysis/v1",
        "unit": "population", "populations": POPS,
        "threshold": 13, "contrast": contrasts,
        "two_sided_sign_null": {
            "numerator": 1394, "denominator": 65536,
            "requires": "INDEPENDENT_SYMMETRIC_NONZERO_SIGNS_NOT_PROVEN"},
        "neutral_marker_alert_count": neutral_alert_count,
        "neutral_marker_alert": neutral_alert_count >= 1,
        "invalid_neutral_markers": invalid,
        "status": ("STAGE6_LIGHT_INVALID" if invalid else
                   "STAGE6_LIGHT_SIGN_CONCORDANCE_PASS"
                   if contrasts["beta_u_eff"]["direction_concordant"]
                   else "STAGE6_LIGHT_NO_SIGN_CONCORDANCE"),
        "inference": "F0_ONLY_NO_GENERAL_SURVIVAL_ADVANTAGE",
    }


def _append_phase(root: Path, phase: str, payload_sha: str,
                  current: list[dict]) -> list[dict]:
    if phase != PHASES[len(current)]:
        raise RuntimeError("phase chronology violation: no retry")
    previous = current[-1]["chain_sha256"] if current else None
    row = {"ordinal": len(current), "phase": phase,
           "payload_sha256": payload_sha, "previous_sha256": previous}
    row["chain_sha256"] = _sha(row)
    with (root / "PHASES.jsonl").open("ab") as f:
        f.write(_canonical(row) + b"\n")
        f.flush()
        os.fsync(f.fileno())
    return [*current, row]


def run_full(plan: dict, destination: str | Path, published_plan_sha: str) -> dict:
    """One-shot full native G/S/R with an explicit separate science plan.

    The science plan is source-bound to two completed rehearsals and must be
    precommitted; legacy method v1 is never promoted into a science permit.
    """
    scientific = type(plan) is dict and plan.get("schema") == SCIENCE_SCHEMA
    if scientific:
        verify_science_plan(plan)
    else:
        verify_plan(plan)
    if published_plan_sha != plan["allocation_sha256"]:
        raise PermissionError("missing exact published pre-exposure plan digest")
    root = Path(destination).resolve()
    if (root.is_relative_to(G0.ROOT.resolve())
            or str(root) != plan["archive_root"]):
        raise PermissionError("archive path must equal precommitted fixed destination")
    G0._verify_checkout(plan)  # no World imported until after checkout guard
    # One fixed, precommitted path: cannot use another folder to retry this plan.
    root.mkdir()  # no exist_ok, atomic claim; parent must already exist
    receipt = {"schema": ("i3-stage6-native-gsr-science-claim/v1" if scientific
                          else "i3-stage6-native-gsr-engineering-claim/v1"),
               "plan_sha256": plan["allocation_sha256"],
               "source_git_head": plan["source_git_head"],
               "archive_root": plan["archive_root"],
               "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL"}
    with (root / "CLAIM.json").open("xb") as f:
        f.write(_canonical(receipt))
        f.flush()
        os.fsync(f.fileno())
    from i3.lab import two_phase_panel as TP, p2_ecologies
    from i3.lab import stage6_light_prospective_ecologies as stage6_ecologies
    from i3.runtime.life import run_life
    from i3.modules.genome import digest as genome_digest
    from i3.lab import stage6_light_native_custody_preflight as native_audit
    phases, outcomes = [], []
    original_cases = {}
    offspring_all = []
    parent_draws_all = []
    genomes = founder_genomes(plan)
    # Pre-birth, derivable native v4 founder material for detached lineage audit.
    from i3.modules.genome import digest as frozen_genome_digest
    founder_index = [
        {"population": row["population"], "slot": row["slot"],
         "seed": row["genome_seed"],
         "genome": genomes[row["population"], "shared", row["slot"]],
         "genome_sha256": frozen_genome_digest(
             genomes[row["population"], "shared", row["slot"]])}
        for row in plan["founders"]
    ]
    with (root / "FOUNDERS.json").open("xb") as f:
        f.write(_canonical(founder_index))
        f.flush()
        os.fsync(f.fileno())
    try:
        for g in range(3):
            cases = native_archive_cases(plan, g, genomes)
            original_cases[g] = cases
            archive = root / f"G{g}"
            def one(case: dict) -> dict:
                spec = stage6_ecologies.world_for_stage6(
                    case["family"], case["world_seed"])
                genome = genomes[case["population"], case["arm"], case["slot"]]
                life = run_life(genome, spec, case["life_seed"], HORIZON,
                                keep_trace=True, protocol=plan["protocol"],
                                decision_policy="reference")
                if (life["genome"] != case["genome_sha256"]
                        or genome_digest(genome) != case["genome_sha256"]):
                    raise RuntimeError("native birth/genotype differs from frozen case")
                return life
            generation = TP.generate(cases, one, archive)
            if (generation["status"] != "GENERATED"
                    or generation["generated"] != EXPECTED_GENERATION[g]):
                raise RuntimeError("native generation failed: NO_RETRY")
            digest = sha256((archive / "MANIFEST.json").read_bytes()).hexdigest()
            phases = _append_phase(root, f"G{g}", digest, phases)
            audited = native_audit.inspect_sealed_generation(
                archive, g, cases, expected_protocol=plan["protocol"],
                source_pin=plan["source_files_sha256"],
                source_head=plan["source_git_head"])
            if (audited["checked_native_records"] != len(cases) or
                    audited["original_manifest_sha256"] != digest):
                raise ValueError("native original structural audit mismatch")
            # An intact sealed G is required before S can even read persistence.
            # Stream full native traces one original at a time: never keep
            # thousands of 400-step objects resident in rehearsal memory.
            fitness = _summary_scores(TP.load_sealed(archive), g, cases, genomes,
                                      plan["source_files_sha256"],
                                      plan["source_git_head"],
                                      plan["protocol"])
            if sha256((archive / "MANIFEST.json").read_bytes()).hexdigest() != digest:
                raise RuntimeError("G manifest changed during G seal")
            phases = _append_phase(root, f"SEAL_G{g}", digest, phases)
            outcomes.append({"generation": g, "lives": len(cases),
                             "seal_sha256": digest})
            if g < 2:
                children, parent_receipts = choose_descendants(
                    plan, g+1, genomes, fitness, digest)
                allocation = {(r["population"], r["generation"], r["arm"], r["slot"]): r
                              for r in plan["draws"] if r["generation"] == g+1}
                offspring_claims = [{
                    "population": d["population"], "generation": d["generation"],
                    "arm": d["arm"], "slot": d["slot"],
                    "parent_slot": d["parent_slot"],
                    "mutation_seed": allocation[d["population"], d["generation"],
                                                 d["arm"], d["slot"]]["mutation_seed"],
                    "parent_genome_sha256": d["parent_genome_sha256"],
                    "genome": children[d["population"], d["arm"], d["slot"]],
                    "genome_sha256": d["offspring_genome_sha256"],
                } for d in parent_receipts]
                offspring_all.extend(offspring_claims)
                parent_draws_all.extend(parent_receipts)
                payload = {"schema": "i3-stage6-native-parent-receipts/v1",
                           "generation": g+1, "prior_generation_sha256": digest,
                           "draws": parent_receipts, "offspring": offspring_claims}
                target = root / f"SELECT_G{g+1}.json"
                with target.open("xb") as f:
                    f.write(_canonical(payload))
                    f.flush()
                    os.fsync(f.fileno())
                phases = _append_phase(root, f"SELECT_G{g+1}",
                                       sha256(target.read_bytes()).hexdigest(),
                                       phases)
                genomes = children
            else:
                final = final_contrasts(genomes)
                if scientific:
                    from i3.lab import stage6_light_original_selection_bridge as bridge
                    # Full blinded archival join after G2 is sealed: parents,
                    # source-bound WorldSpec, mutation and seed draws all rechecked.
                    audit = bridge.inspect_original_selection(
                        {j: root / f"G{j}" for j in range(3)},
                        original_cases, founder_index,
                        offspring_all, parent_draws_all,
                        expected_protocol=plan["protocol"],
                        source_pin=plan["source_files_sha256"],
                        source_head=plan["source_git_head"])
                    if (audit["original_lives_structurally_checked"] != 11520 or
                            audit["claimed_parent_draws_reproduced"] != 1536 or
                            audit["offspring_mutations_reproduced"] != 1536):
                        raise RuntimeError("full precommitted lineage audit failed")
                    result = {
                        "schema": "i3-stage6-light-prospective-science-result/v1",
                        "status": final["status"],
                        "source_git_head": plan["source_git_head"],
                        "source_files_sha256": plan["source_files_sha256"],
                        "preexposure_allocation_sha256": plan["allocation_sha256"],
                        "scientific_scope": plan["science_scope"],
                        "rehearsal_receipts_sha256": _sha(
                            plan["engineering_full_scale_receipts"]),
                        "original_lives": sum(i["lives"] for i in outcomes),
                        "generation_seals": outcomes,
                        "frozen_analysis": final,
                        "native_original_selection_audit": audit,
                        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
                        "stage2_scientific_verdict": "NOT_ISSUED",
                        "scientific_admission": True}
                    target = root / "R_FINAL_SCIENCE.json"
                else:
                    # Technical R computes only a sealed digest. Never reveal
                    # engineering contrast signs before the science exposure.
                    result = {
                        "schema": "i3-stage6-gsr-engineering-result/v1",
                        "status": "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE",
                        "original_lives": sum(i["lives"] for i in outcomes),
                        "generation_seals": outcomes,
                        "reduction_sha256": _sha(final),
                        "science_decision_disclosed": False,
                        "scientific_admission": False,
                        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED"}
                    target = root / "R_FINAL_ENGINEERING.json"
                with target.open("xb") as f:
                    f.write(_canonical(result))
                    f.flush()
                    os.fsync(f.fileno())
                phases = _append_phase(root, "R_FINAL",
                                       sha256(target.read_bytes()).hexdigest(),
                                       phases)
        if len(phases) != len(PHASES):
            raise RuntimeError("incomplete nine-phase Stage6 engineering process")
        return {"status": (final["status"] if scientific
                           else "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE"),
                "source_git_head": plan["source_git_head"],
                "allocation_sha256": plan["allocation_sha256"],
                "last_chain_sha256": phases[-1]["chain_sha256"],
                "lives_archived": sum(i["lives"] for i in outcomes),
                "science_admission": scientific,
                "no_retry": True}
    except BaseException as exc:
        # Never relabel an incomplete generation as a death or repeat it.
        failure = {"schema": "i3-stage6-native-gsr-abort/v1",
                   "status": ("SCIENTIFIC_EXECUTION_DEFECT_NO_RETRY"
                              if scientific else
                              "ENGINEERING_FAILURE_NOT_A_DEATH_NO_RETRY"),
                   "phase_index": len(phases),
                   "error_type": type(exc).__name__, "no_retry": True}
        with (root / "FAILURE.json").open("xb") as f:
            f.write(_canonical(failure))
            f.flush()
            os.fsync(f.fileno())
        raise


def main() -> None:
    if len(sys.argv) == 6 and sys.argv[1] == "allocate":
        _, _, head, source_hash, output, archive = sys.argv
        plan = make_plan(secrets.token_hex(32), head, source_hash, archive)
        with Path(output).open("x", encoding="utf-8") as f:
            json.dump(plan, f, sort_keys=True, indent=2)
            f.write("\n")
        print(json.dumps({"status": plan["status"],
                          "allocation_sha256": plan["allocation_sha256"],
                          "worlds": 0, "lives": 0}, sort_keys=True))
    elif len(sys.argv) == 7 and sys.argv[1] == "allocate-science":
        _, _, head, source_hash, output, archive, rehearsals_file = sys.argv
        receipts = json.loads(Path(rehearsals_file).read_text(encoding="utf-8"))
        plan = make_science_plan(secrets.token_hex(32), head, source_hash,
                                 archive, receipts)
        with Path(output).open("x", encoding="utf-8") as f:
            json.dump(plan, f, sort_keys=True, indent=2)
            f.write("\n")
        print(json.dumps({"status": plan["status"],
                          "allocation_sha256": plan["allocation_sha256"],
                          "worlds_opened": 0, "lives_created": 0}))
    elif len(sys.argv) == 3 and sys.argv[1] == "verify-science":
        plan = verify_science_plan(json.loads(Path(sys.argv[2]).read_text()))
        print(json.dumps({"status": plan["status"],
                          "allocation_sha256": plan["allocation_sha256"],
                          "lives_planned": plan["planned_lives"]}))
    elif len(sys.argv) == 5 and sys.argv[1] == "run-science":
        plan = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        verify_science_plan(plan)
        print(json.dumps(run_full(plan, sys.argv[3], sys.argv[4]), sort_keys=True))
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        plan = verify_plan(json.loads(Path(sys.argv[2]).read_text()))
        print(json.dumps({"status": plan["status"],
                          "planned_lives": plan["planned_lives"],
                          "allocation_sha256": plan["allocation_sha256"]}))
    elif len(sys.argv) == 5 and sys.argv[1] == "run-engineering":
        plan = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(json.dumps(run_full(plan, sys.argv[3], sys.argv[4]), sort_keys=True))
    else:
        raise SystemExit("usage: allocate HEAD SOURCE_SHA PLAN.json ABS_ARCHIVE_PATH | verify PLAN.json | run-engineering PLAN.json DIR SHA | allocate-science HEAD SOURCE_SHA PLAN.json ABS_ARCHIVE_PATH REHEARSALS.json | verify-science PLAN.json | run-science PLAN.json DIR SHA")


if __name__ == "__main__":
    main()
