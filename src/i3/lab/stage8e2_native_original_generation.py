"""Stage8-E2 native engineering generation: original gzip custody.

No CLI or workflow is enabled. A caller must independently publish a frozen
preexposure allocation and provide a source-exact clean checkout. Every
offspring genome must already have been checked against its sealed parent
generation before this component is called. No science admission is possible.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8e2_native_preflight as N
from i3.lab import p2_ecologies as F0
from i3.lab import stage6_light_prospective_ecologies as ECO
from i3.modules import genome as G

SCHEMA = "i3-stage8e2-native-technical-generation/v0"
PROTOCOL = "i3-stage8e2-gamma-factorial-P1.3-funded-v2-technical/v0"
SHA40 = re.compile(r"[0-9a-f]{40}\\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\\Z")


def _check_source(head: str, source_sha: str) -> None:
    if (type(head) is not str or not SHA40.fullmatch(head)
            or type(source_sha) is not str or not SHA64.fullmatch(source_sha)):
        raise PermissionError("frozen source pins required")
    from i3.runtime.provenance import source_snapshot
    checkout = Path(__file__).resolve().parents[3]
    actual = subprocess.run(["git", "rev-parse", "HEAD"], cwd=checkout,
                            capture_output=True, text=True, check=True, timeout=15)
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=checkout, capture_output=True, text=True,
                            check=True, timeout=15)
    snapshot = source_snapshot()
    if (actual.stdout.strip() != head or status.stdout.strip()
            or snapshot.get("git_head") != head
            or snapshot.get("sha256") != source_sha
            or snapshot.get("working_tree_dirty") is not False):
        raise PermissionError("native engine checkout not the frozen clean source")


def generation_cases(root: str, generation: int, genomes: dict,
                     source_sha: str) -> list[dict]:
    """Exact native World and genotype commitments for one generation."""
    P._root(root)
    if type(generation) is not int or generation not in (0, 1, 2):
        raise ValueError("unknown native generation")
    arms = ("shared",) if generation == 0 else (
        P.G1_ARMS if generation == 1 else P.G2_ARMS)
    expected = {(p, arm, s) for p in range(P.POPULATIONS)
                for arm in arms for s in range(P.FOUNDERS)}
    if (type(genomes) is not dict or set(genomes) != expected
            or type(source_sha) is not str or not SHA64.fullmatch(source_sha)):
        raise ValueError("incomplete native generation genotype/source")
    digests = {key: G.digest(G.validate(value)) for key, value in genomes.items()}
    worlds = {(p, family, repeat): N._world_row(root, p, generation, family, repeat)
              for p in range(P.POPULATIONS)
              for family in P.WORLD_FAMILIES for repeat in range(P.WORLD_REPEATS)}
    result = []
    for p in range(P.POPULATIONS):
        for arm in arms:
            for slot in range(P.FOUNDERS):
                for family in P.WORLD_FAMILIES:
                    for repeat in range(P.WORLD_REPEATS):
                        key = (p, generation, arm, slot, family, repeat)
                        w = worlds[p, family, repeat]
                        result.append({
                            "population": p, "generation": generation,
                            "arm": arm, "slot": slot,
                            "family": family, "repeat": repeat,
                            "world_seed": w["world_seed"],
                            "world_sha256": w["world_sha256"],
                            "life_seed": N._seed(root, "identity", "life", *key),
                            "genome_sha256": digests[p, arm, slot],
                            "source_sha256": source_sha,
                        })
    total = P.EXPECTED_G0 if generation == 0 else (
        P.EXPECTED_G1 if generation == 1 else P.EXPECTED_G2)
    if len(result) != total or len({
        (r["population"], r["generation"], r["arm"], r["slot"],
         r["family"], r["repeat"]) for r in result}) != total:
        raise ValueError("incomplete or duplicated native generation cases")
    return result


def execute_technical_generation(*, root: str, generation: int,
                                 genomes: dict, source_git_head: str,
                                 source_files_sha256: str, preflight: dict,
                                 custody_dir: str) -> dict:
    """Run authentic I3 P1.3 reference lives and archive original JSON gzip.

    Each generation is a separately claimed, irreversible directory. This is
    deliberately not a full study runner: parental seals must be authenticated
    before supplying G1/G2, and it does not admit or launch scientific science.
    """
    if sys.version_info[:2] not in ((3, 11), (3, 12)):
        raise PermissionError("native technical Python 3.11/3.12 required")
    _check_source(source_git_head, source_files_sha256)
    N.verify_native_preflight(root, expected=preflight)
    from i3.lab import two_phase_panel as TP
    from i3.runtime.life import run_life

    cases = generation_cases(root, generation, genomes, source_files_sha256)
    path = Path(custody_dir)
    checkout = Path(__file__).resolve().parents[3]
    if (type(custody_dir) is not str or not path.is_absolute()
            or str(path.resolve()) != custody_dir
            or path.resolve().is_relative_to(checkout.resolve())):
        raise PermissionError("custody must be a canonical path outside source")
    path.mkdir()  # irreversible no-retry claim; rejects existing directory
    claim = {
        "schema": SCHEMA, "status": "ENGINEERING_CLAIMED_NO_RETRY",
        "generation": generation, "source_git_head": source_git_head,
        "source_files_sha256": source_files_sha256,
        "preflight_sha256": preflight["manifest_sha256"],
        "cases": len(cases), "scientific_admission": False,
    }
    with (path / "CLAIM.json").open("xb") as fh:
        fh.write(json.dumps(claim, sort_keys=True, separators=(",", ":")).encode())
        fh.flush()
    try:
        def one(case):
            genome = genomes[case["population"], case["arm"], case["slot"]]
            spec = ECO.world_for_stage6(case["family"], case["world_seed"])
            if F0.fingerprint(spec) != case["world_sha256"]:
                raise ValueError("prospective physical WorldSpec drift")
            life = run_life(genome, spec, case["life_seed"], P.HORIZON,
                            keep_trace=True, protocol=PROTOCOL,
                            decision_policy="reference")
            if (life.get("genome") != case["genome_sha256"]
                    or life.get("steps_lived", 0) not in range(1, P.HORIZON + 1)
                    or life.get("terminal") not in ("dead", "censored")):
                raise ValueError("foreign or incomplete native life")
            return life

        manifest = TP.generate(cases, one, path / f"G{generation}")
        if (manifest["status"] != "GENERATED"
                or manifest["generated"] != len(cases)):
            raise RuntimeError("native life failed: no retry")
        # Rehash every gzip and decoded body before any downstream scoring.
        count = 0
        for identity, life in TP.load_sealed(path / f"G{generation}"):
            expected = cases[count]
            if identity != expected or life.get("genome") != expected["genome_sha256"]:
                raise ValueError("original native life mismatch")
            count += 1
        if count != len(cases):
            raise ValueError("missing original life")
        manifest_bytes = (path / f"G{generation}" / "MANIFEST.json").read_bytes()
        outcome = {
            "schema": SCHEMA, "status": "GENERATION_ORIGINALS_REHASHED_NO_SCIENCE",
            "generation": generation, "original_lives": count,
            "manifest_sha256": sha256(manifest_bytes).hexdigest(),
            "scientific_admission": False, "no_retry": True,
        }
        with (path / "RECEIPT.json").open("xb") as fh:
            fh.write(json.dumps(outcome, sort_keys=True, separators=(",", ":")).encode())
        return outcome
    except BaseException as exc:
        with (path / "FAILURE.json").open("xb") as fh:
            fh.write(json.dumps({
                "schema": SCHEMA, "status": "TECHNICAL_NO_VERDICT_NO_RETRY",
                "generation": generation, "error_type": type(exc).__name__,
                "scientific_admission": False, "no_retry": True,
            }, sort_keys=True, separators=(",", ":")).encode())
        raise
