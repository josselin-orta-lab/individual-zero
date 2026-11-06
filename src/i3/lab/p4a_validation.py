"""P4a: one preregistered held-out evaluation of ALL 48 frozen P3 G2 genomes.

Use --preflight for a pure, no-world inspection; --run is fail-closed unless
the current exact Git commit, allocation digest, frozen genome artifact, and
prospective protocol have been locked by a prior merged registration.
P4b learning interventions and P4 reserve are outside this executable.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from i3.lab import p2_ecologies, p3_schedule, p4a_schedule
from i3.modules.genome import digest as genome_digest, validate
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot

PROTOCOL = p4a_schedule.PROTOCOL
G2_PATH = (Path(__file__).resolve().parents[1] /
           "docs/studies/p3-mutation-pilot/G2_GENOMES.json")


def _head_sha() -> str:
    root = Path(__file__).resolve().parents[3]
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                               capture_output=True, text=True, check=True, timeout=5)
    return completed.stdout.strip()


def verify_frozen_genomes(path: Path = G2_PATH) -> dict:
    """Verify BOTH raw artifact and canonical contents before using any genotype."""
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != p4a_schedule.G2_FILE_SHA256:
        raise ValueError("P3 frozen G2 raw file differs from registered artifact")
    obj = json.loads(raw)
    claimed = obj.get("sha256")
    payload = {k: v for k, v in obj.items() if k != "sha256"}
    if (sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
               ).hexdigest() != p4a_schedule.G2_CANONICAL_SHA256 or
        claimed != p4a_schedule.G2_CANONICAL_SHA256):
        raise ValueError("P3 G2 canonical evidence checksum mismatch")
    if (obj.get("source_sha") != "52476fec3f39a7fd70bf611877b01d9c13d26009" or
        obj.get("selection_lives_verified") != 864 or
        obj.get("world_keys_verified") != 72 or
        obj.get("generation") != 2 or obj.get("reserve") != "LOCKED" or
        obj.get("validation") != "NOT_RUN" or len(obj.get("genomes", ())) != 48):
        raise ValueError("unrecognized P3 G2 custody provenance")
    indexed = {}
    for row in obj["genomes"]:
        key = (row["population"], row["arm"], row["slot"])
        if (key in indexed or
            type(row["population"]) is not int or
            not 0 <= row["population"] < p4a_schedule.POPULATIONS or
            row["arm"] not in p4a_schedule.ARMS or
            type(row["slot"]) is not int or
            not 0 <= row["slot"] < p4a_schedule.GENOTYPES):
            raise ValueError("duplicate or invalid frozen genotype identity")
        validate(row["genome"])
        if genome_digest(row["genome"]) != row["genome_sha256"]:
            raise ValueError("frozen genotype digest mismatch")
        indexed[key] = row
    expected = {
        (p, arm, s) for p in range(p4a_schedule.POPULATIONS)
        for arm in p4a_schedule.ARMS for s in range(p4a_schedule.GENOTYPES)
    }
    if set(indexed) != expected:
        raise ValueError("incomplete G2 set")
    return indexed


def launch_preflight() -> tuple[dict, dict]:
    """No validation world may be constructed before all locks pass."""
    head = _head_sha()
    if head != os.environ.get("I3_P4A_SOURCE_SHA", ""):
        raise RuntimeError("P4a exact source commit was not locked")
    schedule = p4a_schedule.schedule_manifest()
    if schedule["sha256"] != os.environ.get("I3_P4A_SCHEDULE_SHA", ""):
        raise RuntimeError("P4a schedule not prospectively sealed")
    if os.environ.get("I3_P4A_APPROVED_PROTOCOL", "") != PROTOCOL:
        raise RuntimeError("P4a protocol not prospectively approved")
    frozen = verify_frozen_genomes()
    return schedule, frozen


def _life_receipt(outcome: dict, *, population: int, arm: str, slot: int,
                  family: str, repeat: int, index: int, gsha: str) -> dict:
    ca = outcome["cognitive_accounting"]
    if (ca["status"] != "SETTLED_FOR_DECLARED_WORK" or
        ca["shortfall_steps"] != 0 or ca["pending_replays"] != 0):
        raise RuntimeError("incomplete cognition payment")
    for ch in ("energy", "vigilance"):
        bill = ca["totals"][ch]
        if (bill["unpaid"] != 0 or abs(bill["paid"] - bill["requested"]) > 1e-9):
            raise RuntimeError("unpaid cognitive charge in held-out result")
    censored = outcome["terminal"] == "censored"
    if (outcome["terminal"] not in ("dead", "censored") or
        censored != (outcome["steps_lived"] == p4a_schedule.HORIZON and
                     not outcome["death_causes"]) or
        not 1 <= outcome["steps_lived"] <= p4a_schedule.HORIZON or
        (not censored and not outcome["death_causes"])):
        raise RuntimeError("invalid physical death or censoring")
    if outcome["genome"] != gsha or not outcome["manifest_id"] or not outcome["evidence_head"]:
        raise RuntimeError("missing genome or evidence provenance")
    return {
        "population": population, "arm": arm, "slot": slot, "family": family,
        "repeat": repeat, "validation_world_index": index,
        "life_seed": outcome["life_seed"], "world_sha256": outcome["manifest"]["world_sha256"],
        "source_sha256": outcome["manifest"]["source"]["sha256"],
        "genome_sha256": gsha, "manifest_id": outcome["manifest_id"],
        "evidence_head": outcome["evidence_head"],
        "terminal": outcome["terminal"], "death_causes": outcome["death_causes"],
        "steps_lived": outcome["steps_lived"], "censored": censored,
        "paid_energy": ca["totals"]["energy"]["paid"],
        "paid_vigilance": ca["totals"]["vigilance"]["paid"],
        "inactive_steps": ca["inactive_steps"],
        "learning_updates": ca["learning_updates"],
        "replays_executed": ca["replays_executed"],
    }


def run() -> dict:
    schedule, genomes = launch_preflight()
    results = []
    source_hashes = set()
    for allocation in schedule["allocation"]:
        p, family, repeat, index, seed = (
            allocation["population"], allocation["family"], allocation["repeat"],
            allocation["world_index"], allocation["life_seed"])
        # This is the FIRST held-out world opening, after every launch lock.
        spec = p2_ecologies.world_for(family, "validation", index)
        initial_hash = digest(world_snapshot(spec))
        for arm in p4a_schedule.ARMS:
            for slot in range(p4a_schedule.GENOTYPES):
                row = genomes[(p, arm, slot)]
                outcome = run_life(row["genome"], spec, seed, p4a_schedule.HORIZON,
                                   protocol=PROTOCOL)
                receipt = _life_receipt(outcome, population=p, arm=arm, slot=slot,
                                        family=family, repeat=repeat, index=index,
                                        gsha=row["genome_sha256"])
                if receipt["world_sha256"] != initial_hash or receipt["life_seed"] != seed:
                    raise RuntimeError("unequal initial world or seed")
                source_hashes.add(receipt["source_sha256"])
                results.append(receipt)
    if len(results) != p4a_schedule.LIVES or len(source_hashes) != 1:
        raise RuntimeError("held-out life count or source parity failed")
    out = {
        "schema": PROTOCOL, "source_sha": _head_sha(),
        "schedule_sha256": schedule["sha256"],
        "p3_g2_custody_sha256": p4a_schedule.G2_CANONICAL_SHA256,
        "status": "P4A_VALIDATION_ONLY_P4B_AND_RESERVE_NOT_RUN",
        "total_lives": len(results), "source_sha256": next(iter(source_hashes)),
        "lives": results,
    }
    out["sha256"] = sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return out


def summarize(out: dict) -> dict:
    populations = []
    for p in range(p4a_schedule.POPULATIONS):
        arms = {}
        for arm in p4a_schedule.ARMS:
            lives = [row for row in out["lives"]
                     if row["population"] == p and row["arm"] == arm]
            arms[arm] = {
                "survivors": sum(row["censored"] for row in lives),
                "deaths": sum(not row["censored"] for row in lives),
                "lived_steps": sum(row["steps_lived"] for row in lives),
                "paid_energy": round(sum(row["paid_energy"] for row in lives), 5),
                "paid_vigilance": round(sum(row["paid_vigilance"] for row in lives), 5),
                "inactive_steps": sum(row["inactive_steps"] for row in lives),
            }
        populations.append({"population": p, "arms": arms,
                            "selected_minus_random_survivors":
                            arms["selected"]["survivors"] -
                            arms["random_parent"]["survivors"]})
    return {
        "schema": PROTOCOL, "total_lives": out["total_lives"],
        "schedule_sha256": out["schedule_sha256"],
        "source_sha": out["source_sha"], "original_evidence_sha256": out["sha256"],
        "population_results": populations,
        "status": out["status"],
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        schedule = p4a_schedule.schedule_manifest()
        indexed = verify_frozen_genomes()
        print(json.dumps({
            "schema": PROTOCOL, "status": "NO_VALIDATION_WORLD_OPENED",
            "schedule_sha256": schedule["sha256"],
            "validation_world_keys": len(schedule["allocation"]),
            "frozen_g2_genomes_verified": len(indexed),
            "max_lives": p4a_schedule.LIVES}, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--run":
        destination = Path(sys.argv[2])
        if destination.exists():
            raise FileExistsError("refuse to overwrite P4a evidence")
        original = run()
        destination.write_text(json.dumps(original, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summarize(original), indent=2, sort_keys=True))
    else:
        raise SystemExit("usage: python -m i3.lab.p4a_validation --preflight | --run ORIGINAL.json")
