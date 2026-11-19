"""Stage8-E2 *cold* archive audit after downloading ALL original gzip.

Does not import the native generation runner, the lineage builder or the
technical transport. Reconstructs every expected identity from the sealed
preexposure seeds, native F0 WorldSpecs, and archived born v4 genotypes;
verifies every gzip original including trace/evidence chains, then verifies
the nine-phase SHA chain and upstream sealed parental/offspring claims.

No simulation or scientific inference. The SHA plan must have been published
before G0 exposure, not just placed into the archive after the fact.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8e2_native_preflight as N
from i3.lab import stage8e2_independent_original_audit as AUDIT
from i3.lab import stage8e2_parent_fitness_gate as FITNESS
from i3.lab import stage8e2_independent_parentage_audit as PARENTAGE
from i3.lab import stage8e2_g2_factorial_genomes as GAMMA
from i3.modules import genome as G

SCHEMA = "i3-stage8e2-cold-independent-originals-and-ancestry/v0"
PLAN_SCHEMA = "i3-stage8e2-full-native-technical-preexposure/v0"
TECH_PASS = "STAGE8E2_FULL_NATIVE_TECHNICAL_ORIGINALS_SEALED_NO_SCIENCE"
PHASES = (
    "G0", "SEAL_G0", "SELECT_G1", "G1", "SEAL_G1",
    "SELECT_G2", "G2", "SEAL_G2", "R_FINAL",
)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
PROTOCOL = "i3-stage8e2-gamma-factorial-P1.3-funded-v2-technical/v0"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return sha256(canonical(value)).hexdigest()


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked archive claim")
    return json.loads(path.read_bytes())


def _records(rows: object, arms: tuple) -> dict:
    if type(rows) is not list:
        raise ValueError("missing archived genotype records")
    out = {}
    for r in rows:
        if (type(r) is not dict
                or set(r) != {"population", "arm", "slot", "genome", "genome_sha256"}
                or type(r["population"]) is not int or not 0 <= r["population"] < 64
                or r["arm"] not in arms or type(r["slot"]) is not int
                or not 0 <= r["slot"] < 24):
            raise ValueError("foreign archived descendant genotype")
        key = (r["population"], r["arm"], r["slot"])
        if key in out or G.digest(G.validate(r["genome"])) != r["genome_sha256"]:
            raise ValueError("repeated or edited archived genotype")
        out[key] = r["genome"]
    if len(out) != 64 * len(arms) * 24:
        raise ValueError("missing archived native genome")
    return out


def expected_originals(root: str, generation: int, genomes: dict,
                       source_sha: str) -> list[dict]:
    """Own expected-identity reconstruction, no Stage8-E2 runner imported."""
    arms = ("shared",) if generation == 0 else (
        ("S", "M") if generation == 1 else P.G2_ARMS)
    if set(genomes) != {(p, a, s) for p in range(64)
                       for a in arms for s in range(24)}:
        raise ValueError("impossible native original genotype matrix")
    result = []
    for p in range(64):
        for family in P.WORLD_FAMILIES:
            for rep in (0, 1):
                physical = N._world_row(root, p, generation, family, rep)
                for arm in arms:
                    for slot in range(24):
                        key = (p, generation, arm, slot, family, rep)
                        result.append({
                            "population": p, "generation": generation,
                            "arm": arm, "slot": slot, "family": family,
                            "repeat": rep,
                            "world_seed": physical["world_seed"],
                            "world_sha256": physical["world_sha256"],
                            "life_seed": N._seed(root, "identity", "life", *key),
                            "genome_sha256": G.digest(genomes[p, arm, slot]),
                            "source_sha256": source_sha,
                        })
    expected_count = (P.EXPECTED_G0, P.EXPECTED_G1, P.EXPECTED_G2)[generation]
    if len(result) != expected_count:
        raise ValueError("incomplete cold original identity plan")
    return result


def verify_phase_chain(root: Path, plan: dict) -> list:
    phase_file = root / "PHASES.jsonl"
    if phase_file.is_symlink() or not phase_file.is_file():
        raise ValueError("phase chain missing")
    phases = [json.loads(line) for line in phase_file.read_bytes().splitlines()]
    if len(phases) != len(PHASES):
        raise ValueError("incomplete nine-phase archive chain")
    last_sha = None
    for i, row in enumerate(phases):
        phase = PHASES[i]
        rel = row.get("artifact")
        if (type(rel) is not str or rel.startswith("/")
                or ".." in Path(rel).parts
                or row.get("phase") != phase
                or row.get("sequence") != i
                or row.get("previous_chain_sha256") != last_sha):
            raise ValueError("reordered/redirected phase evidence")
        artifact = root / rel
        if (artifact.is_symlink() or not artifact.is_file()
                or not artifact.resolve().is_relative_to(root.resolve())
                or sha256(artifact.read_bytes()).hexdigest() != row.get("file_sha256")
                or digest({k: v for k, v in row.items() if k != "chain_sha256"})
                    != row.get("chain_sha256")):
            raise ValueError("altered phase-chain proof or artifact")
        last_sha = row["chain_sha256"]
    receipt = load(root / "TECHNICAL_RECEIPT.json")
    if (receipt.get("phase_chain_sha256") != last_sha
            or receipt.get("status") != TECH_PASS
            or receipt.get("scientific_admission") is not False
            or receipt.get("source_git_head") != plan["source_git_head"]
            or receipt.get("source_files_sha256") != plan["source_files_sha256"]
            or receipt.get("allocation_sha256") != plan["allocation_sha256"]):
        raise ValueError("foreign final technical phase chain or source receipt")
    return phases


def cold_audit(plan_path: str, plan_file_sha256: str, original_root: str) -> dict:
    """Full read-only G0/G1/G2 review after artifact download, no birth."""
    path = Path(plan_path)
    root = Path(original_root)
    if (not path.is_file() or path.is_symlink() or
            root.is_symlink() or not root.is_dir()
            or type(plan_file_sha256) is not str
            or not HEX64.fullmatch(plan_file_sha256)):
        raise ValueError("missing external frozen plan or original zip extraction")
    data = path.read_bytes()
    if sha256(data).hexdigest() != plan_file_sha256:
        raise ValueError("externally published preexposure SHA differs")
    plan = json.loads(data)
    if (type(plan) is not dict or plan.get("schema") != PLAN_SCHEMA
            or data != canonical(plan)
            or digest({k: v for k, v in plan.items()
                       if k != "allocation_sha256"}) != plan.get("allocation_sha256")
            or type(plan.get("source_git_head")) is not str
            or not HEX40.fullmatch(plan["source_git_head"])
            or type(plan.get("source_files_sha256")) is not str
            or not HEX64.fullmatch(plan["source_files_sha256"])
            or plan.get("scientific_admission") is not False
            or plan.get("planned_lives") != P.EXPECTED_TOTAL
            or plan.get("planned_mutations") != 6144):
        raise ValueError("foreign frozen prospective allocation")
    if (root / "FROZEN_PLAN.json").read_bytes() != data
            or load(root / "CLAIM.json").get("plan_sha256") != plan["allocation_sha256"]):
        raise ValueError("original custody not bound to frozen allocation")
    N.verify_native_preflight(plan["root_hex"], expected=plan["native_preflight"])
    phases = verify_phase_chain(root, plan)
    founder_rows = load(root / "FOUNDERS.json")
    if type(founder_rows) is not list or len(founder_rows) != 1536:
        raise ValueError("missing native G0 founder provenance")
    founders = {}
    for row in founder_rows:
        if (type(row) is not dict or set(row) != {
                "population", "slot", "genome_seed"}):
            raise ValueError("invalid G0 founder row")
        p, slot, seed = row["population"], row["slot"], row["genome_seed"]
        if (type(p) is not int or not 0 <= p < 64
                or type(slot) is not int or not 0 <= slot < 24
                or seed != N._seed(plan["root_hex"], "founder", "founder", p, slot)
                or (p, "shared", slot) in founders):
            raise ValueError("G0 founder seed not precommitted")
        founders[p, "shared", slot] = G.generation_zero(seed)
    genomes = founders
    seen = 0
    previous_scores = None
    previous_manifest = None
    all_original_sha = []
    parentage_sha = []
    for generation in range(3):
        if generation > 0:
            selected = load(root / f"SELECT_G{generation}.json")
            if (selected.get("generation") != generation
                    or selected.get("prior_original_manifest_sha256") != previous_manifest
                    or selected.get("scientific_admission") is not False):
                raise ValueError("child selection not tied to audited parent archive")
            prior_genomes = genomes
            children = _records(selected["mutated_descendants"], ("S", "M"))
            parentage = PARENTAGE.verify_parentage(
                plan["root_hex"], generation, prior_genomes,
                previous_scores, children, selected["parent_draws"],
                previous_manifest)
            if parentage != selected.get("independent_parentage"):
                raise ValueError("parentage recomputation not in selection receipt")
            parentage_sha.append(digest(parentage))
            if generation == 2:
                records = _records(selected["live_generation_genomes"], P.G2_ARMS)
                pairs = {(p, slot): {
                    "S": children[p, "S", slot],
                    "M": children[p, "M", slot],
                } for p in range(64) for slot in range(24)}
                expected_gamma = GAMMA.independent_genotype_audit(pairs, records)
                if expected_gamma != selected.get("gamma_four_arm_check"):
                    raise ValueError("gamma block intervention not independently reconstructible")
                genomes = records
            else:
                records = _records(selected["live_generation_genomes"], ("S", "M"))
                if records != children:
                    raise ValueError("G1 born children differ from mutated S/M offspring")
                genomes = records
        cases = expected_originals(plan["root_hex"], generation, genomes,
                                   plan["source_files_sha256"])
        physical = root / f"PHYSICAL_G{generation}" / f"G{generation}"
        audited = AUDIT.audit_original_generation(
            physical, cases, source_pin=plan["source_files_sha256"],
            source_head=plan["source_git_head"], protocol=PROTOCOL,
            generation=generation)
        seal = load(root / f"SEAL_G{generation}.json")
        if (seal.get("generation") != generation
                or seal.get("original_manifest_sha256") != audited["original_manifest_sha256"]
                or seal.get("verified_original_lives") != len(cases)
                or seal.get("independent_original_audit_sha256") != digest({
                    k: v for k, v in audited.items() if k != "six_life_rows"
                })):
            raise ValueError("individual original seal differs on cold audit")
        seen += audited["original_lives_verified"]
        all_original_sha.append(audited["original_manifest_sha256"])
        previous_manifest = audited["original_manifest_sha256"]
        if generation < 2:
            previous_scores = FITNESS.summarize_authenticated_lives(
                audited["six_life_rows"], generation)
    if seen != P.EXPECTED_TOTAL:
        raise ValueError("incomplete original gzip archive")
    receipt = load(root / "TECHNICAL_RECEIPT.json")
    if (receipt.get("original_lives_audited") != seen
            or receipt.get("mutations_reconstructed") != 6144
            or receipt.get("phase_count") != 9):
        raise ValueError("technical receipt disagrees with independently audited originals")
    return {
        "schema": SCHEMA,
        "status": "ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE",
        "source_git_head": plan["source_git_head"],
        "source_files_sha256": plan["source_files_sha256"],
        "allocation_sha256": plan["allocation_sha256"],
        "original_lives_rehashed": seen,
        "g0_g1_g2_manifest_sha256": all_original_sha,
        "parentage_audit_sha256": parentage_sha,
        "phase_chain_sha256": phases[-1]["chain_sha256"],
        "scientific_admission": False,
    }


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: PREEXPOSURE_PLAN PUBLISHED_PLAN_FILE_SHA256 EXTRACTED_ORIGINAL_DIR")
    print(json.dumps(cold_audit(sys.argv[1], sys.argv[2], sys.argv[3]),
                     sort_keys=True))


if __name__ == "__main__":
    main()
