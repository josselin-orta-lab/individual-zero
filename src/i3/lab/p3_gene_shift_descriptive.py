"""Read-only descriptive gene-shift reduction on the archived P3 lineage.

No World, Mind, run_life or new life: the 144 archived P3 genomes are
reconstructed from their archived seeds and parent links and must reproduce
the archived digests. The reduction rule was frozen before any gene value
was read, in
``docs/studies/stage6-light-preparation/P3_GENE_SHIFT_DESCRIPTIVE_PREFLIGHT_2026-11-13.md``.

DESCRIPTIVE ONLY. Four populations cannot support an inference: the only
admissible wording is "sign agreement k/4". Never a scientific verdict.
"""
from __future__ import annotations

import gzip
from hashlib import sha256
import json
from math import fsum, isfinite, sqrt
from pathlib import Path

from i3.modules.genome import (
    HISTORICAL_V3_BOUNDS,
    HISTORICAL_V3_GENE_ORDER,
    digest_historical_v3,
    historical_v3_generation_zero,
    historical_v3_mutate,
)

SCHEMA = "i3-p3-gene-shift-descriptive/v1"
PREFLIGHT_COMMIT = "fdc9c0f7da478a0196bf28ef010bdc0c1e875eed"
STUDY = (Path(__file__).resolve().parents[1] / "docs" / "studies"
         / "p3-mutation-pilot")
ARCHIVE = STUDY / "selection-full.json.gz"
FROZEN_G2 = STUDY / "G2_GENOMES.json"
# SHA-256 of the UNCOMPRESSED original (ORIGINAL_SHA256SUMS.txt).
ARCHIVE_SHA256 = "e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e"
FROZEN_G2_SHA256 = "6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419"
ARCHIVE_SCHEMA = "i3-p3-mutation-pilot-v1"
SOURCE_SHA = "52476fec3f39a7fd70bf611877b01d9c13d26009"
TOTAL_LIVES = 864

ARMS = ("selected", "random_parent")
POPULATIONS = 4
GENERATIONS = 3
GENOTYPES = 6
MUTATION_SCALE = 0.1  # p3_schedule.MUTATION_SCALE at the P3 source

PRIMARY = "beta_u_eff"
SECONDARY = "beta_u"
NEUTRAL_MARKERS = ("temperament.affiliation", "temperament.reward_sensitivity")
QUANTITIES = tuple(HISTORICAL_V3_GENE_ORDER) + (PRIMARY,)
EPS = 1e-12
DIGITS = 9


class IntegrityError(ValueError):
    """Fail closed: no gene value may be published after this error."""


def _fail(message: str):
    raise IntegrityError("INTEGRITY_FAIL: " + message)


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def _r(value: float) -> float:
    if not isfinite(value):
        _fail("nonfinite reduction value")
    return round(value, DIGITS)


def load_archive(path: Path, expected_sha256: str, *,
                 expected_source_sha: str = SOURCE_SHA,
                 expected_total_lives: int = TOTAL_LIVES) -> dict:
    """Read the sealed original and refuse any source drift."""
    raw = gzip.open(path, "rb").read()
    if sha256(raw).hexdigest() != expected_sha256:
        _fail("archive SHA-256 differs from the pinned original")
    archive = json.loads(raw)
    if (type(archive) is not dict
            or archive.get("schema") != ARCHIVE_SCHEMA
            or archive.get("source_sha") != expected_source_sha
            or archive.get("total_lives") != expected_total_lives
            or type(archive.get("populations")) is not list
            or len(archive["populations"]) != POPULATIONS):
        _fail("archive identity fields are not the P3 original")
    return archive


def reconstruct(archive: dict) -> tuple[dict, int]:
    """Rebuild every genome from seeds and parent links; verify digests.

    Returns ``({(population, arm, generation): {slot: row}}, verified)``
    where each row has ``genome`` and ``parent_slot``.
    """
    cells: dict = {}
    verified = 0
    for p, pop in enumerate(archive["populations"]):
        if pop.get("population") != p or len(pop.get("generations", ())) != GENERATIONS:
            _fail("population or generation layout differs")
        for g, gen in enumerate(pop["generations"]):
            if gen.get("generation") != g or set(gen.get("arms", ())) != set(ARMS):
                _fail("generation or arm layout differs")
            for arm in ARMS:
                rows = gen["arms"][arm]
                if (type(rows) is not list or len(rows) != GENOTYPES
                        or sorted(r.get("slot") for r in rows) != list(range(GENOTYPES))):
                    _fail("each cell needs exactly six unique slots")
                cell = {}
                for row in rows:
                    if g == 0:
                        if row.get("parent_slot") is not None:
                            _fail("generation zero cannot have a parent")
                        genome = historical_v3_generation_zero(row["genome_seed"])
                    else:
                        parent_row = cells[(p, arm, g - 1)].get(row.get("parent_slot"))
                        if parent_row is None:
                            _fail("parent slot is absent from the prior generation")
                        parent = parent_row["genome"]
                        if digest_historical_v3(parent) != row.get("parent_genome_sha256"):
                            _fail("archived parent digest is not reproduced")
                        genome = historical_v3_mutate(
                            parent, row["mutation_seed"], scale=MUTATION_SCALE)
                    if digest_historical_v3(genome) != row.get("genome_sha256"):
                        _fail("archived genome digest is not reproduced")
                    verified += 1
                    cell[row["slot"]] = {"genome": genome,
                                         "parent_slot": row.get("parent_slot")}
                cells[(p, arm, g)] = cell
        for slot in range(GENOTYPES):
            if (cells[(p, ARMS[0], 0)][slot]["genome"]
                    != cells[(p, ARMS[1], 0)][slot]["genome"]):
                _fail("generation zero differs between the paired arms")
    return cells, verified


def check_frozen_g2(cells: dict, path: Path, expected_sha256: str) -> int:
    """Cross-check reconstructed G2 genomes against the frozen G2 record."""
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != expected_sha256:
        _fail("frozen G2 record SHA-256 differs from the pinned original")
    frozen = json.loads(raw)
    entries = frozen.get("genomes")
    if type(entries) is not list or len(entries) != POPULATIONS * len(ARMS) * GENOTYPES:
        _fail("frozen G2 record layout differs")
    matched = 0
    for entry in entries:
        key = (entry.get("population"), entry.get("arm"), GENERATIONS - 1)
        row = cells.get(key, {}).get(entry.get("slot"))
        if (row is None or row["genome"] != entry.get("genome")
                or digest_historical_v3(row["genome"]) != entry.get("genome_sha256")):
            _fail("frozen G2 genome is not reproduced by the reconstruction")
        matched += 1
    return matched


def quantities(genome: dict) -> dict:
    """Frozen quantities: 30 bound-normalized genes plus expressed curiosity."""
    genes = genome["genes"]
    out = {}
    for name in HISTORICAL_V3_GENE_ORDER:
        lo, hi = HISTORICAL_V3_BOUNDS[name]
        out[name] = (genes[name] - lo) / (hi - lo)
    # Expressed curiosity weight of the reference (mind.py, Mind.__init__).
    out[PRIMARY] = genes["beta_u"] * (1.0 + 0.5 * genes["temperament.exploration"])
    return out


def summarize(values: list) -> dict:
    """Per-population values -> frozen descriptive summary (no inference)."""
    n = len(values)
    mean = fsum(values) / n
    sd = sqrt(fsum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
    return {
        "per_population": [_r(v) for v in values],
        "positive": sum(1 for v in values if v > EPS),
        "negative": sum(1 for v in values if v < -EPS),
        "zero": sum(1 for v in values if abs(v) <= EPS),
        "mean": _r(mean), "sample_sd": _r(sd),
        "min": _r(min(values)), "max": _r(max(values)),
    }


def _cell_means(cells: dict) -> dict:
    means = {}
    for key, cell in cells.items():
        rows = [quantities(cell[slot]["genome"]) for slot in range(GENOTYPES)]
        means[key] = {q: fsum(r[q] for r in rows) / GENOTYPES for q in QUANTITIES}
    return means


def _bounds(cells: dict) -> dict:
    out = {}
    for name in HISTORICAL_V3_GENE_ORDER:
        lo, hi = HISTORICAL_V3_BOUNDS[name]
        per_arm = {}
        for arm in ARMS:
            shares = []
            for g in range(GENERATIONS):
                values = [cells[(p, arm, g)][slot]["genome"]["genes"][name]
                          for p in range(POPULATIONS) for slot in range(GENOTYPES)]
                at = sum(1 for v in values if abs(v - lo) <= EPS or abs(v - hi) <= EPS)
                shares.append(_r(at / len(values)))
            per_arm[arm] = shares
        out[name] = per_arm
    return out


def _genealogy(cells: dict) -> dict:
    out = {}
    last = GENERATIONS - 1
    for arm in ARMS:
        rows = []
        for p in range(POPULATIONS):
            ancestors = []
            for slot in range(GENOTYPES):
                current = slot
                for g in range(last, 0, -1):
                    current = cells[(p, arm, g)][current]["parent_slot"]
                ancestors.append(current)
            counts = sorted((ancestors.count(a) for a in set(ancestors)), reverse=True)
            rows.append({
                "population": p,
                "distinct_g0_ancestors": len(set(ancestors)),
                "top_ancestor_share": _r(counts[0] / GENOTYPES),
                "distinct_g1_parents": len({
                    cells[(p, arm, last)][s]["parent_slot"] for s in range(GENOTYPES)}),
            })
        out[arm] = rows
    return out


def reduce(cells: dict) -> dict:
    """Apply the frozen reduction rule to verified genomes."""
    means = _cell_means(cells)
    last = GENERATIONS - 1
    table = {}
    for q in QUANTITIES:
        entry = {}
        for g in range(1, GENERATIONS):
            entry[f"contrast_g{g}"] = summarize([
                means[(p, "selected", g)][q] - means[(p, "random_parent", g)][q]
                for p in range(POPULATIONS)])
        entry["drift_g0_to_g2"] = {
            arm: [_r(means[(p, arm, last)][q] - means[(p, arm, 0)][q])
                  for p in range(POPULATIONS)] for arm in ARMS}
        entry["cell_means"] = {
            arm: [[_r(means[(p, arm, g)][q]) for g in range(GENERATIONS)]
                  for p in range(POPULATIONS)] for arm in ARMS}
        table[q] = entry
    return {"quantities": table, "bounds": _bounds(cells),
            "genealogy": _genealogy(cells)}


def audit(archive_path: Path = ARCHIVE, expected_sha256: str = ARCHIVE_SHA256,
          frozen_g2_path: Path | None = FROZEN_G2,
          frozen_g2_sha256: str = FROZEN_G2_SHA256, *,
          expected_source_sha: str = SOURCE_SHA,
          expected_total_lives: int = TOTAL_LIVES) -> dict:
    """One frozen read-only reduction; raises IntegrityError before any value."""
    archive = load_archive(archive_path, expected_sha256,
                           expected_source_sha=expected_source_sha,
                           expected_total_lives=expected_total_lives)
    cells, verified = reconstruct(archive)
    if verified != POPULATIONS * GENERATIONS * len(ARMS) * GENOTYPES:
        _fail("not every archived genome was verified")
    frozen = (check_frozen_g2(cells, frozen_g2_path, frozen_g2_sha256)
              if frozen_g2_path is not None else None)
    reduction = reduce(cells)
    report = {
        "schema": SCHEMA,
        "status": "P3_GENE_SHIFT_DESCRIPTIVE_READ_COMPLETE",
        "scientific_verdict": "NOT_ISSUED",
        "inference": "NONE_FOUR_POPULATIONS_DESCRIPTIVE_ONLY",
        "preflight_commit": PREFLIGHT_COMMIT,
        "archive_sha256": expected_sha256,
        "archive_source_sha": expected_source_sha,
        "genomes_verified": verified,
        "frozen_g2_genomes_matched": frozen,
        "generation_zero_identical_between_arms": True,
        "populations": POPULATIONS, "generations": GENERATIONS,
        "genotypes_per_cell": GENOTYPES, "arms": list(ARMS),
        "worlds_opened": 0, "lives_created": 0, "lives_rerun": 0,
        "primary_quantity": PRIMARY, "secondary_quantity": SECONDARY,
        "neutral_markers": list(NEUTRAL_MARKERS),
        "reduction": reduction,
    }
    report["digest_sha256"] = sha256(_canonical(report).encode("utf-8")).hexdigest()
    return report


def main() -> int:
    print(_canonical(audit()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
