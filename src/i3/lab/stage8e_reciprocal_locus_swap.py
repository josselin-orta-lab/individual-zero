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
