"""Stage8-E: exploratory locus-by-locus associations from sealed Stage8-C lives.

Reads only existing, source-bound G1/G2 offspring genomes, after Stage8-D has
reverified all 32,256 gzip originals and Stage8-C's pre-verdict audit.
Never imports the native generator, chooses a parent, runs a World or life.
Across-gene rankings are descriptive; no p-values or causal discovery claims.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

from i3.lab import stage8d_genomic_diversity_readonly as D
from i3.modules import genome as G

SCHEMA = "i3-stage8e-existing-original-locus-association/v1"
STATUS = "STAGE8E_POSTHOC_LOCI_DESCRIBED_NO_CAUSAL_VERDICT"
GENES = tuple(G.BOUNDS)
ARMS = D.ARMS
GENS = (1, 2)
POPULATIONS = D.POPULATIONS
SLOTS = D.SLOTS
SOURCE = D.SOURCE
RUN_ID = D.RUN_ID


def _finite(value: object) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("non-finite or nonnumeric population value")
    return float(value)


def _mean(seq) -> float:
    values = [_finite(v) for v in seq]
    if not values:
        raise ValueError("empty population group")
    return math.fsum(values)/len(values)


def _sd(seq) -> float:
    values = [_finite(v) for v in seq]
    if len(values) < 2:
        raise ValueError("at least two independent populations required")
    m = _mean(values)
    return math.sqrt(math.fsum((v-m)**2 for v in values)/(len(values)-1))


def _corr(xs, ys) -> float | None:
    """Pearson at the POPULATION level, not genome/pair/life level."""
    if len(xs) != len(ys) or len(xs) < 3:
        raise ValueError("paired population observations required")
    x, y = [_finite(v) for v in xs], [_finite(v) for v in ys]
    mx, my = _mean(x), _mean(y)
    xx = math.fsum((v-mx)**2 for v in x)
    yy = math.fsum((v-my)**2 for v in y)
    if xx <= 1e-24 or yy <= 1e-24:
        return None
    return max(-1., min(1., math.fsum(
        (u-mx)*(v-my) for u,v in zip(x,y))/math.sqrt(xx*yy)))


def _panel_gene_means(folder: Path) -> dict:
    """Read ONLY selections already certified by full original-level audit."""
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("invalid original native panel")
    means = {}
    for gen in GENS:
        rows = D._selection_records(folder/f"SELECT_G{gen}.json", gen)
        born = rows["born"]
        for local in range(16):
            for arm in ARMS:
                values = [D.normalized_genome(born[local,arm,s])
                          for s in range(SLOTS)]
                means[local,gen,arm] = tuple(
                    _mean([v[j] for v in values]) for j in range(len(GENES)))
    if len(means) != 16*len(GENS)*len(ARMS):
        raise ValueError("incomplete native genetic source panel")
    return means


def _original_gene_means(root: Path) -> dict:
    result = {}
    for panel in range(2):
        folder = root/"NATIVE_ORIGINALS"/f"PANEL_{panel}"
        for (local,g,arm),values in _panel_gene_means(folder).items():
            key = (16*panel+local,g,arm)
            if key in result:
                raise ValueError("duplicate sealed genetic population")
            result[key] = values
    return result


def from_population_means(profiles: list[dict], gene_means: dict) -> dict:
    """Pure associative reduction with fixed 32 population units.

    Gene-level mean-of-24 is a population summary, not 24 observations;
    no gene was selected, tested or optimized on these outcomes in advance.
    """
    if (type(profiles) is not list or len(profiles) != POPULATIONS or
            any(type(row) is not dict for row in profiles) or
            [row.get("population") for row in profiles] != list(range(POPULATIONS))):
        raise ValueError("32 exact source-ordered population profiles required")
    expected = {(p,g,arm) for p in range(POPULATIONS)
                for g in GENS for arm in ARMS}
    if type(gene_means) is not dict or set(gene_means) != expected:
        raise ValueError("missing, foreign or duplicated population-arm-gen profiles")
    for key,values in gene_means.items():
        if (type(values) not in (tuple,list) or len(values)!=len(GENES)
                or any(not 0 <= _finite(v) <= 1 for v in values)):
            raise ValueError("genome coordinate out of declared normalized bounds")
    outcomes = [_finite(row["G2_S_minus_M_steps"]) for row in profiles]
    adverse = [p for p,v in enumerate(outcomes) if v < 0]
    if adverse != [0,1,3,11,16,18,19,24,28,31]:
        raise ValueError("Stage8-C source-locked negative populations changed")
    gene_rows = []
    all_profiles = [{"population":p, "G2_S_minus_M_steps":outcomes[p],
                     "G1_S_minus_M_normalized_by_gene":{},
                     "G2_S_minus_M_normalized_by_gene":{}}
                    for p in range(POPULATIONS)]
    for j, gene in enumerate(GENES):
        g1 = [gene_means[p,1,"selected"][j]-
              gene_means[p,1,"matched_multiplicity"][j]
              for p in range(POPULATIONS)]
        g2 = [gene_means[p,2,"selected"][j]-
              gene_means[p,2,"matched_multiplicity"][j]
              for p in range(POPULATIONS)]
        corr = _corr(g2,outcomes)
        jackknife = [
            _corr(g2[:p]+g2[p+1:],outcomes[:p]+outcomes[p+1:])
            for p in range(POPULATIONS)
        ]
        valid = [v for v in jackknife if v is not None]
        same = (sum((v > 0)==(corr > 0) for v in valid)/len(valid)
                if corr is not None and valid else None)
        for p in range(POPULATIONS):
            all_profiles[p]["G1_S_minus_M_normalized_by_gene"][gene] = g1[p]
            all_profiles[p]["G2_S_minus_M_normalized_by_gene"][gene] = g2[p]
        gene_rows.append({
            "gene": gene,
            "G1_mean_S_minus_M_normalized": _mean(g1),
            "G2_mean_S_minus_M_normalized": _mean(g2),
            "G2_population_sd_S_minus_M_normalized": _sd(g2),
            "G2_population_delta_vs_persistence_Pearson": corr,
            "leave_one_population_out_correlation_min": min(valid) if valid else None,
            "leave_one_population_out_correlation_max": max(valid) if valid else None,
            "leave_one_population_out_sign_agreement_fraction": same,
            "G2_adverse_mean_S_minus_M_normalized":
                _mean([g2[p] for p in adverse]),
            "G2_favorable_mean_S_minus_M_normalized":
                _mean([g2[p] for p in range(POPULATIONS) if p not in adverse]),
        })
    ranked = sorted(
        gene_rows, key=lambda r: (
            r["G2_population_delta_vs_persistence_Pearson"] is None,
            -abs(r["G2_population_delta_vs_persistence_Pearson"])
              if r["G2_population_delta_vs_persistence_Pearson"] is not None else 0.,
            r["gene"]))
    for rank,row in enumerate(ranked,1):
        row["exploratory_absolute_correlation_rank"] = rank
    return {
        "gene_count": len(GENES),
        "gene_order_declared": list(GENES),
        "ranked_gene_associations": ranked,
        "all_32_population_gene_profiles": all_profiles,
        "population_units": POPULATIONS,
        "G2_outcome_mean_steps": _mean(outcomes),
        "adverse_population_ids": adverse,
        "new_lives": 0,
        "new_worlds": 0,
        "statistical_scope": ("32_POPULATION_CLUSTERS_ONLY;"
                              "ALL_GENES_DISCOVERY_MULTIPLE_COMPARISONS;"
                              "DESCRIPTIVE_PEARSON_AND_JACKKNIFE_NO_P_VALUES;"
                              "NO_CAUSAL_GENE_OR_GENERALIZATION_CLAIM"),
    }


def audit_full(plan: str, originals: str, pre_verdict: str) -> dict:
    """Stage8-D original-level rehash first, then extra read of sealed genes."""
    source_root = Path(originals)
    # D audits the sealed 32,256 gzip bodies AND the immutable pre-verdict audit.
    existing = D.audit_full(plan, originals, pre_verdict)
    if (existing.get("status") != D.STATUS
            or existing.get("native_original_lives_reverified") != 32256
            or existing.get("native_mutated_parentage_reconstructed") != 4608
            or existing.get("population_units") != POPULATIONS
            or existing.get("scientific_status_unchanged") !=
            "STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0"):
        raise ValueError("Stage8-C original evidence was not independently verified")
    association = from_population_means(
        existing["all_32_population_profiles"],
        _original_gene_means(source_root))
    if not math.isclose(association["G2_outcome_mean_steps"],
                        existing["G2_S_minus_M_lifetime_mean_preserved"],
                        abs_tol=1e-10,rel_tol=0):
        raise ValueError("native G2 persistence changed while reading genomes")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "original_run_id": RUN_ID,
        "original_source_git_head": SOURCE,
        "science_allocation_sha256": existing["science_allocation_sha256"],
        "preverdict_independent_audit_git_head": D.PREVERDICT_AUDITOR,
        "native_original_lives_reverified": existing["native_original_lives_reverified"],
        "mutated_parentage_reconstructed": existing["native_mutated_parentage_reconstructed"],
        "scientific_status_unchanged": existing["scientific_status_unchanged"],
        "G2_global_diversity_S_minus_M_mean_preserved":
            existing["G2_S_minus_M_diversity_mean"],
        "G2_global_diversity_Pearson_preserved":
            existing["G2_S_minus_M_diversity_vs_lifetime_Pearson_population_only"],
        **association,
    }


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("read-only Stage8-E: SCIENCE_PLAN.json ORIGINALS_ROOT PREVERDICT_AUDIT.json")
    print(json.dumps(audit_full(*sys.argv[1:]),sort_keys=True,allow_nan=False))


if __name__ == "__main__":
    main()
