"""Prospective Stage8-E causal L2 operator, SOFTWARE ONLY, never runs World.

Reciprocal locus-value exchange on two born G2 genomes before their own
first-person lives, with identity-preserving sham sibling controls.
All genes except the nominated one remain exactly as sealed.
No locus is nominated here and no population, seed or World is allocated.
"""
from __future__ import annotations

from copy import deepcopy

from i3.modules import genome as G

SCHEMA = "i3-stage8e-reciprocal-single-locus-swap-design/v0"
EXCLUDED_ORDER_COUPLED = frozenset(("gamma1", "gamma2", "gamma3"))


def eligible_genes() -> tuple[str, ...]:
    """Independent v4 coordinates; gamma horizons require separate joint design."""
    return tuple(name for name in G.GENE_ORDER
                 if name not in EXCLUDED_ORDER_COUPLED)


def reciprocal_allele_swap(selected: dict, matched: dict, *, gene: str) -> dict:
    """Prepare four V4 genome copies, no mutation, physics, memory or birth.

    S/M_SHAM preserve the input exactly. S/M_SWAP exchange precisely gene's
    finite declared value, all other channels untouched. A causal experiment
    needs fresh source-pinned Worlds, a prespecified gene and blinded analysis;
    this pure operator alone does not produce a scientific outcome.
    """
    if type(gene) is not str or gene not in eligible_genes():
        raise ValueError("non-independent, unknown or unregistered v4 locus")
    G.validate(selected)
    G.validate(matched)
    shams = (deepcopy(selected), deepcopy(matched))
    swaps = (deepcopy(selected), deepcopy(matched))
    swaps[0]["genes"][gene], swaps[1]["genes"][gene] = (
        shams[1]["genes"][gene], shams[0]["genes"][gene])
    for g in (*shams, *swaps):
        G.validate(g)
    if (any(swaps[0]["genes"][k] != shams[0]["genes"][k]
            or swaps[1]["genes"][k] != shams[1]["genes"][k]
            for k in G.GENE_ORDER if k != gene)
            or swaps[0]["genes"][gene] != shams[1]["genes"][gene]
            or swaps[1]["genes"][gene] != shams[0]["genes"][gene]):
        raise AssertionError("reciprocal swap changed another genomic coordinate")
    return {
        "schema": SCHEMA,
        "locus": gene,
        "S_sham": shams[0],
        "M_sham": shams[1],
        "S_swap": swaps[0],
        "M_swap": swaps[1],
        "sha256": {
            "S_sham": G.digest(shams[0]),
            "M_sham": G.digest(shams[1]),
            "S_swap": G.digest(swaps[0]),
            "M_swap": G.digest(swaps[1]),
        },
        "no_births": True,
    }

# A jointly exchanged triple retains gamma1 <= gamma2 <= gamma3 exactly.
# This is one *block* intervention, never evidence about gamma3 alone.
GAMMA_HORIZONS = ("gamma1", "gamma2", "gamma3")
BLOCK_SCHEMA = "i3-stage8e-reciprocal-gamma-horizon-block-design/v0"


def reciprocal_gamma_horizon_block_swap(selected: dict, matched: dict) -> dict:
    """Joint gamma1/gamma2/gamma3 swap; no selectively invalid G2 child.

    The ordered triple is one coherent intervention. Each sham is an exact
    copy of its born genotype, whereas its swapped sibling differs only by
    all three gamma horizons copied from the opposite arm. This may isolate
    an effect of the BLOCK in a future randomized, source-sealed study but
    cannot identify gamma3 as the unique causal contributor.
    """
    G.validate(selected)
    G.validate(matched)
    shams = (deepcopy(selected), deepcopy(matched))
    swaps = (deepcopy(selected), deepcopy(matched))
    for gene in GAMMA_HORIZONS:
        swaps[0]["genes"][gene] = shams[1]["genes"][gene]
        swaps[1]["genes"][gene] = shams[0]["genes"][gene]
    for g in (*shams, *swaps):
        G.validate(g)
    for gene in G.GENE_ORDER:
        if gene in GAMMA_HORIZONS:
            if (swaps[0]["genes"][gene] != shams[1]["genes"][gene]
                    or swaps[1]["genes"][gene] != shams[0]["genes"][gene]):
                raise AssertionError("gamma block was only partially exchanged")
        elif (swaps[0]["genes"][gene] != shams[0]["genes"][gene]
                or swaps[1]["genes"][gene] != shams[1]["genes"][gene]):
            raise AssertionError("non-gamma gene changed by horizon block")
    return {
        "schema": BLOCK_SCHEMA,
        "loci_jointly_intervened": list(GAMMA_HORIZONS),
        "S_sham": shams[0], "M_sham": shams[1],
        "S_swap": swaps[0], "M_swap": swaps[1],
        "sha256": {name:G.digest(genome) for name,genome in (
            ("S_sham",shams[0]),("M_sham",shams[1]),
            ("S_swap",swaps[0]),("M_swap",swaps[1]))},
        "no_births": True,
    }
