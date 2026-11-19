"""Post hoc Stage8-D diversity on SEALED Stage8-C genomes; NO World or births.

This is descriptive only. It first calls the pre-verdict, frozen independent
Stage8-C auditor to verify all 32,256 original gzip lives and all pedigrees.
Only then does it inspect the already verified G1/G2 SELECT_G records.
Genetic distances are continuous-parameter distances, NOT heterozygosity.
No confirmatory gene, survival, ecological or Stage2 verdict is computed.
"""
from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import sys

from i3.lab import stage8c_independent_original_audit as A
from i3.modules import genome as G

SCHEMA = "i3-stage8d-posthoc-genome-diversity-readonly/v1"
STATUS = "STAGE8D_POSTHOC_ORIGINAL_BOUND_DESCRIPTIVE_COMPLETE"
ARMS = A.ARMS
POPULATIONS = A.POPULATIONS
SLOTS = 24
PAIRS = 276
GENES = tuple(G.BOUNDS)
GENS = (1, 2)
SOURCE = A.ORIGINAL_HEAD
RUN_ID = A.ORIGINAL_RUN_ID
PREVERDICT_AUDITOR = "23d0e3eabff0042123c84f4b292a2e4c72cfcc8f"


def _finite_float(v: object) -> float:
    if type(v) not in (int, float) or not math.isfinite(v):
        raise ValueError("invalid finite numerical evidence")
    return float(v)


def normalized_genome(genome: dict) -> tuple[float, ...]:
    """Fixed v4 gene order and per-gene declared bounds, never fitted values."""
    G.validate(genome)
    return tuple(
        (float(genome["genes"][name]) - lo)/(hi - lo)
        for name, (lo, hi) in G.BOUNDS.items()
    )


def pairwise_rms_diversity(genomes: list[dict] | tuple[dict, ...]) -> float:
    """Exactly 276 individual-pair distances aggregated into ONE population value."""
    if type(genomes) not in (list, tuple) or len(genomes) != SLOTS:
        raise ValueError("exactly 24 native v4 genomes per population and arm")
    vectors = [normalized_genome(g) for g in genomes]
    distances = []
    for i in range(SLOTS):
        for j in range(i+1, SLOTS):
            distances.append(math.sqrt(math.fsum(
                (x-y)**2 for x, y in zip(vectors[i], vectors[j])
            )/len(GENES)))
    if len(distances) != PAIRS:
        raise AssertionError("missing pairwise genetic comparisons")
    return math.fsum(distances)/PAIRS


def parent_occupancy(slots: list[int] | tuple[int, ...]) -> dict:
    """Source is the 24 SEALED G1/G2 parent-slot receipts."""
    if (type(slots) not in (list, tuple) or len(slots) != SLOTS
            or any(type(x) is not int or not 0 <= x < SLOTS for x in slots)):
        raise ValueError("incomplete or invalid parent-slot allocation")
    counts = Counter(slots)
    proportions = [n/SLOTS for n in counts.values()]
    return {
        "distinct_parents": len(counts),
        "multiplicity_multiset": sorted(counts.values()),
        "entropy_nats": -math.fsum(q*math.log(q) for q in proportions),
    }


def _selection_records(path: Path, generation: int) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or redirected sealed SELECT_G archive")
    event = json.loads(path.read_bytes())
    if (type(event) is not dict
            or event.get("schema") != "i3-stage8c-sealed-three-arm-parentage/v1"
            or event.get("generation") != generation
            or type(event.get("draws")) is not list
            or type(event.get("offspring")) is not list
            or len(event["draws"]) != 1152
            or len(event["offspring"]) != 1152):
        raise ValueError("incomplete original parental event")
    expected = {(p, arm, s) for p in range(16)
                for arm in ARMS for s in range(SLOTS)}
    drawn, born = {}, {}
    for r in event["draws"]:
        if type(r) is not dict or not all(k in r for k in
                ("population", "arm", "slot", "parent_slot")):
            raise ValueError("malformed original parent receipt")
        key = (r["population"], r["arm"], r["slot"])
        if key in drawn or type(r["parent_slot"]) is not int or not 0 <= r["parent_slot"] < SLOTS:
            raise ValueError("duplicate or invalid archived parent")
        drawn[key] = r["parent_slot"]
    for r in event["offspring"]:
        if type(r) is not dict or not all(k in r for k in
                ("population", "arm", "slot", "genome", "genome_sha256")):
            raise ValueError("malformed original offspring")
        key = (r["population"], r["arm"], r["slot"])
        if key in born:
            raise ValueError("duplicated G1/G2 offspring")
        G.validate(r["genome"])
        if r["genome_sha256"] != G.digest(r["genome"]):
            raise ValueError("archived offspring v4 genome digest mismatch")
        born[key] = r["genome"]
    if set(drawn) != expected or set(born) != expected:
        raise ValueError("incomplete 16-population, three-arm archived genetics")
    return {"drawn": drawn, "born": born}


def _panel_diversity(folder: Path) -> list[dict]:
    """No genealogy regeneration; only read SELECT records already re-audited."""
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("missing original scientific panel")
    generation = {
        g: _selection_records(folder/f"SELECT_G{g}.json", g) for g in GENS
    }
    rows = []
    for p in range(16):
        out = {"population_local": p, "generation": {}}
        for g in GENS:
            draw = generation[g]["drawn"]
            born = generation[g]["born"]
            geno, occupancy = {}, {}
            for arm in ARMS:
                ordered_genomes = [born[p, arm, slot] for slot in range(SLOTS)]
                ordered_parents = [draw[p, arm, slot] for slot in range(SLOTS)]
                geno[arm] = pairwise_rms_diversity(ordered_genomes)
                occupancy[arm] = parent_occupancy(ordered_parents)
            s = occupancy["selected"]
            m = occupancy["matched_multiplicity"]
            if (s["multiplicity_multiset"] != m["multiplicity_multiset"]
                    or s["distinct_parents"] != m["distinct_parents"]
                    or not math.isclose(s["entropy_nats"], m["entropy_nats"],
                                     abs_tol=1e-12, rel_tol=0)):
                raise ValueError("S/M population parental concentration diverged")
            out["generation"][f"G{g}"] = {
                "genome_pairwise_normalized_rms_mean_by_arm": geno,
                "parent_occupancy_by_arm": occupancy,
                "genome_diversity_S_minus_M": geno["selected"]-geno["matched_multiplicity"],
                "pair_comparisons_per_arm": PAIRS,
            }
        rows.append(out)
    return rows


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("missing population-level data")
    return math.fsum(values)/len(values)


def _sample_sd(values: list[float]) -> float:
    if len(values) < 2:
        raise ValueError("not enough population units")
    mean = _mean(values)
    return math.sqrt(math.fsum((v-mean)**2 for v in values)/(len(values)-1))


def pearson_descriptive(xs: list[float], ys: list[float]) -> float | None:
    """Population-level association only, deliberately no p-value or test."""
    if len(xs) != POPULATIONS or len(ys) != POPULATIONS:
        raise ValueError("32 population paired observations required")
    x = [_finite_float(v) for v in xs]
    y = [_finite_float(v) for v in ys]
    xm, ym = _mean(x), _mean(y)
    xx = math.fsum((v-xm)**2 for v in x)
    yy = math.fsum((v-ym)**2 for v in y)
    if xx <= 0 or yy <= 0:
        return None
    return math.fsum((a-xm)*(b-ym) for a,b in zip(x,y))/math.sqrt(xx*yy)


def _assert_preverdict_audit(actual: dict, earlier: dict) -> None:
    if (type(earlier) is not dict
            or earlier.get("status") != "READ_ONLY_32K_ORIGINALS_REPRODUCED"
            or earlier.get("scientific_status") != A.SUCCESS
            or earlier.get("run_id") != RUN_ID
            or earlier.get("source_git_head") != SOURCE
            or earlier.get("independent_audit_git_head") != PREVERDICT_AUDITOR
            or earlier.get("native_original_lives_rehashed") != 32256
            or earlier.get("mutated_parentage_reconstructed") != 4608
            or earlier.get("population_units") != POPULATIONS
            or earlier.get("new_lives") != 0
            or earlier.get("new_worlds") != 0):
        raise ValueError("wrong, unsealed or unreviewed independent original audit")
    for k in ("science_allocation_sha256", "heldout_worlds_sha256",
              "phase_chains_verified", "all_population_contrasts",
              "mean_G2_S_minus_M_steps",
              "one_sided_97_5_percent_lower_bound_steps"):
        if actual.get(k) != earlier.get(k):
            raise ValueError("preverdict independent original evidence does not match")


def _from_verified_panels(original_root: Path, evidence: dict) -> dict:
    """Pure post-audit measurements; no generator, World, genome mutation or life."""
    if (type(evidence) is not dict
            or evidence.get("status") != "READ_ONLY_32K_ORIGINALS_REPRODUCED"
            or evidence.get("native_original_lives_rehashed") != 32256
            or evidence.get("mutated_parentage_reconstructed") != 4608
            or evidence.get("population_units") != POPULATIONS
            or type(evidence.get("all_population_contrasts")) is not list
            or len(evidence["all_population_contrasts"]) != POPULATIONS):
        raise ValueError("independent original gzip evidence is mandatory")
    rows = []
    for panel in range(2):
        folder = original_root/"NATIVE_ORIGINALS"/f"PANEL_{panel}"
        for r in _panel_diversity(folder):
            p = panel*16+r.pop("population_local")
            r["population"] = p
            r["G2_S_minus_M_steps"] = _finite_float(evidence["all_population_contrasts"][p])
            r["G2_S_minus_M_outcome"] = (
                "adverse" if r["G2_S_minus_M_steps"] < 0
                else "favorable" if r["G2_S_minus_M_steps"] > 0
                else "null"
            )
            rows.append(r)
    rows.sort(key=lambda r:r["population"])
    if [r["population"] for r in rows] != list(range(POPULATIONS)):
        raise ValueError("missing population genomic diversity profile")
    g2_differences = [r["generation"]["G2"]["genome_diversity_S_minus_M"] for r in rows]
    effects = [r["G2_S_minus_M_steps"] for r in rows]
    adverse = [r for r in rows if r["G2_S_minus_M_steps"] < 0]
    by_generation = {}
    for g in GENS:
        label = f"G{g}"
        by_generation[label] = {
            arm: {
                "mean_across_32_population_diversities": _mean([
                    r["generation"][label]["genome_pairwise_normalized_rms_mean_by_arm"][arm]
                    for r in rows]),
                "population_sd_of_diversity": _sample_sd([
                    r["generation"][label]["genome_pairwise_normalized_rms_mean_by_arm"][arm]
                    for r in rows]),
            } for arm in ARMS
        }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "interpretation": "EXPLORATORY_POSTHOC_ASSOCIATIONS_NOT_CONFIRMATORY",
        "scientific_status_unchanged": evidence["scientific_status"],
        "original_run_id": RUN_ID,
        "original_source_git_head": SOURCE,
        "science_allocation_sha256": evidence["science_allocation_sha256"],
        "preverdict_independent_audit_git_head": PREVERDICT_AUDITOR,
        "native_original_lives_reverified": evidence["native_original_lives_rehashed"],
        "native_mutated_parentage_reconstructed": evidence["mutated_parentage_reconstructed"],
        "population_units": POPULATIONS,
        "G2_genomes_per_population_per_arm": SLOTS,
        "genetic_pair_distances_per_population_per_arm": PAIRS,
        "gene_bound_normalization": list(GENES),
        "G1_G2_diversity_by_arm": by_generation,
        "G2_S_minus_M_diversity_mean": _mean(g2_differences),
        "G2_S_minus_M_diversity_population_sd": _sample_sd(g2_differences),
        "G2_S_minus_M_diversity_vs_lifetime_Pearson_population_only":
            pearson_descriptive(g2_differences, effects),
        "G2_S_minus_M_lifetime_mean_preserved": _mean(effects),
        "adverse_population_ids": [r["population"] for r in adverse],
        "adverse_population_count": len(adverse),
        "adverse_G2_genetic_diversity_difference_mean": (
            _mean([r["generation"]["G2"]["genome_diversity_S_minus_M"]
                   for r in adverse]) if adverse else None),
        "all_32_population_profiles": rows,
        "new_lives": 0, "new_worlds": 0,
        "limits": ("GENOTYPIC_DISTANCE_NOT_HETEROZYGOSITY;"
                   "NO_GENE_CAUSALITY_OR_SURVIVAL_MECHANISM;"
                   "NO_INDEPENDENCE_PROOF_OR_GENERALIZATION_BEYOND_F0;"
                   "NO_POSTHOC_CONFIRMATORY_P_VALUES"),
    }


def audit_full(science_plan: str, science_originals: str,
               preverdict_report: str) -> dict:
    """Re-hash ALL gzip once via archived independent auditor, then describe genomes."""
    root = Path(science_originals)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("missing immutable original science archive")
    original = A.audit(science_plan, science_originals)
    earlier_path = Path(preverdict_report)
    if not earlier_path.is_file() or earlier_path.is_symlink():
        raise ValueError("missing frozen independent audit receipt")
    _assert_preverdict_audit(original, json.loads(earlier_path.read_bytes()))
    return _from_verified_panels(root, original)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "read-only: python -m i3.lab.stage8d_genomic_diversity_readonly "
            "SCIENCE_PLAN.json ORIGINALS_ROOT INDEPENDENT_ORIGINAL_AUDIT.json")
    result = audit_full(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
