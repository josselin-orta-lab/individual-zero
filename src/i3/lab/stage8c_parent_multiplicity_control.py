"""Stage8-C design-only parent-concentration control; no World or births.

A blinded parent-slot relabelling keeps the *exact* multiplicities from one
reference 24-offspring draw, but breaks the mapping to ranked parent identity.
It does not match genome diversity, heritable causal effects or fitness.
Only a new prospective source-locked study can test those hypotheses.
"""
from __future__ import annotations

from collections import Counter
import hmac

PARENT_SLOTS = 24
CHILDREN = 24
SCHEMA = "i3-stage8c-parent-multiplicity-control/v0"


def _validate_design(population: int, generation: int, key: bytes) -> None:
    if (type(population) is not int or population < 0 or
            type(generation) is not int or generation not in (1, 2) or
            type(key) is not bytes or len(key) != 32):
        raise ValueError("invalid independent Stage8-C design coordinates or key")


def _draw_index(key: bytes, domain: bytes, upper: int) -> int:
    """HMAC-SHA256 rejection sampling, avoiding modulo bias in shuffles."""
    ceiling = (1 << 256) - ((1 << 256) % upper)
    counter = 0
    while True:
        block = hmac.digest(key, domain + b"/" + str(counter).encode("ascii"), "sha256")
        candidate = int.from_bytes(block, "big")
        if candidate < ceiling:
            return candidate % upper
        counter += 1


def blinded_permutation(*, population: int, generation: int, key: bytes) -> tuple[int, ...]:
    """Deterministic, seeded bijection on parent slots, not fitness ranking."""
    _validate_design(population, generation, key)
    domain = f"{SCHEMA}/population={population}/generation={generation}".encode("ascii")
    slots = list(range(PARENT_SLOTS))
    for index in range(PARENT_SLOTS - 1, 0, -1):
        j = _draw_index(key, domain + b"/index=" + str(index).encode("ascii"), index + 1)
        slots[index], slots[j] = slots[j], slots[index]
    return tuple(slots)


def matched_parent_draws(
    reference_slots: tuple[int, ...] | list[int],
    *,
    population: int,
    generation: int,
    key: bytes,
) -> tuple[int, ...]:
    """Return a score-blind parent sequence preserving exact draw multiplicity.

    Intended Stage8-C control: each selected parent index is relabelled via one
    preallocated, independent bijection. Callers must use the CONTROL arm's
    OWN parent genomes for the returned slots, never selected-arm genomes.
    A random bijection removes the association with *identity* in expectation;
    it cannot guarantee an observed zero score correlation or genomic matching.
    """
    if (type(reference_slots) not in (tuple, list) or
            len(reference_slots) != CHILDREN or
            any(type(slot) is not int or not 0 <= slot < PARENT_SLOTS
                for slot in reference_slots)):
        raise ValueError("expected exactly 24 valid parent-slot draws")
    mapping = blinded_permutation(population=population, generation=generation, key=key)
    matched = tuple(mapping[slot] for slot in reference_slots)
    if (len(matched) != CHILDREN or
            sorted(Counter(matched).values()) !=
            sorted(Counter(reference_slots).values())):
        raise AssertionError("parent multiplicity invariant violated")
    return matched

def build_matched_offspring(
    reference_slots: tuple[int, ...] | list[int],
    control_parent_genomes: dict[int, dict],
    mutation_seeds: tuple[int, ...] | list[int],
    *,
    parent_generation_arm: str,
    population: int,
    generation: int,
    key: bytes,
    prior_manifest_sha256: str,
) -> tuple[dict[int, dict], list[dict]]:
    """Construct only genotype-v4 descendants for the blind CONTROL arm.

    This is a pure pre-exposure engineering adapter, NOT a native birth:
    no World is opened, no survival score is read, no run_life is called.
    The caller must authenticate the parental generation and plan's
    independent mutation seeds before invoking it. No parent object mutates.
    """
    from i3.modules.genome import digest, mutate, validate
    import hashlib
    import json
    import re

    # Validate all inputs before deriving any offspring genotypes.
    if (type(prior_manifest_sha256) is not str or
            re.fullmatch(r"[0-9a-f]{64}", prior_manifest_sha256) is None):
        raise ValueError("missing or invalid sealed parental manifest digest")
    if (type(generation) is not int or generation not in (1, 2) or
            parent_generation_arm != ("shared" if generation == 1 else "matched_multiplicity")):
        raise ValueError("control parent generation/arm provenance mismatch")
    if (type(control_parent_genomes) is not dict or
            len(control_parent_genomes) != PARENT_SLOTS or
            any(type(s) is not int for s in control_parent_genomes) or
            set(control_parent_genomes) != set(range(PARENT_SLOTS))):
        raise ValueError("control arm needs exactly its own 24 parent slots")
    if (type(mutation_seeds) not in (list, tuple) or
            len(mutation_seeds) != CHILDREN or
            any(type(s) is not int or not (6 << 60) <= s < (7 << 60)
                for s in mutation_seeds) or
            len(set(mutation_seeds)) != CHILDREN):
        raise ValueError("24 distinct precommitted native mutation seeds required")
    parent_digests = {}
    for slot in range(PARENT_SLOTS):
        parent_digests[slot] = digest(validate(control_parent_genomes[slot]))
    matched = matched_parent_draws(
        reference_slots, population=population, generation=generation, key=key)
    stream_sha256 = hashlib.sha256(json.dumps(
        reference_slots, separators=(",", ":")).encode("ascii")).hexdigest()
    children, receipts = {}, []
    for child_slot, parent_slot in enumerate(matched):
        parent = control_parent_genomes[parent_slot]
        child = validate(mutate(parent, mutation_seeds[child_slot], scale=0.1))
        children[child_slot] = child
        receipts.append({
            "schema": "i3-stage8c-multiplicity-matched-parent-receipt/v0",
            "population": population,
            "generation": generation,
            "arm": "matched_multiplicity",
            "parent_generation_arm": parent_generation_arm,
            "selected_reference_slots_sha256": stream_sha256,
            "slot": child_slot,
            "parent_slot": parent_slot,
            "parent_genome_sha256": parent_digests[parent_slot],
            "offspring_genome_sha256": digest(child),
            "mutation_seed": mutation_seeds[child_slot],
            "prior_generation_manifest_sha256": prior_manifest_sha256,
        })
    return children, receipts
