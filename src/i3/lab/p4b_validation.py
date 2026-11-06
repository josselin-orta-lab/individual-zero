"""P4b first-principles paid outcome-learning intervention, separate from P4a.

Normal and shadow-discard modes run on the same world/body/life seed with
identical pricing. The shadow really computes the prepaid learning update
on a detached copy, discards it, and retains perception/spatial bookkeeping.
No learned-map or episodic state passes between births. The experiment cannot
claim that removing outcome learning removes ALL spatial learning.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from i3.lab import p2_ecologies, p3_schedule, p4a_validation, p4b_schedule
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot

PROTOCOL = p4b_schedule.PROTOCOL
MODES = p4b_schedule.MODES


def _head_sha():
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                            capture_output=True, text=True, timeout=5, check=True)
    return result.stdout.strip()


def _preflight():
    if _head_sha() != os.environ.get("I3_P4B_SOURCE_SHA", ""):
        raise RuntimeError("P4b source is not preregistered")
    schedule = p4b_schedule.manifest()
    if schedule["sha256"] != os.environ.get("I3_P4B_SCHEDULE_SHA", ""):
        raise RuntimeError("P4b fresh worlds and seed schedule not registered")
    if os.environ.get("I3_P4B_APPROVED_PROTOCOL", "") != PROTOCOL:
        raise RuntimeError("P4b launch protocol not authorized")
    genomes = p4a_validation.verify_frozen_genomes()
    return schedule, genomes


def _receipt(life, *, world_hash, genome_hash, mode, population, arm, slot,
             family, repeat, index, seed):
    if (life["learning_intervention"] != mode or
        life["genome"] != genome_hash or
        life["manifest"]["world_sha256"] != world_hash or
        life["life_seed"] != seed or
        life["horizon"] != p4b_schedule.HORIZON):
        raise RuntimeError("P4b opportunity or intervention drift")
    acc = life["cognitive_accounting"]
    if (acc["status"] != "SETTLED_FOR_DECLARED_WORK" or
        acc["shortfall_steps"] or acc["pending_replays"] or
        any(acc["totals"][ch]["unpaid"] for ch in ("energy", "vigilance"))):
        raise RuntimeError("unpaid cognition in learning intervention")
    for ch in ("energy", "vigilance"):
        v = acc["totals"][ch]
        if abs(v["requested"] - v["paid"]) > 1e-9:
            raise RuntimeError("mismatched charge")
    if mode == "shadow_discard" and life["retained_outcome_learning_updates"]:
        raise RuntimeError("shadow learned updates leaked into durable mind state")
    censored = life["terminal"] == "censored"
    if ((censored and life["steps_lived"] != p4b_schedule.HORIZON) or
        ((not censored) and not life["death_causes"]) or
        not life["manifest_id"] or not life["evidence_head"]):
        raise RuntimeError("incorrect terminal or missing evidence")
    if not (life["outcome_model_sha256"] and life["spatial_beliefs_sha256"]):
        raise RuntimeError("missing individual observer signature")
    return {
        "population": population, "arm": arm, "slot": slot,
        "family": family, "repeat": repeat, "mode": mode,
        "validation_world_index": index, "life_seed": seed,
        "genome_sha256": genome_hash, "world_sha256": world_hash,
        "source_sha256": life["manifest"]["source"]["sha256"],
        "manifest_id": life["manifest_id"], "evidence_head": life["evidence_head"],
        "terminal": life["terminal"], "death_causes": life["death_causes"],
        "censored": censored, "steps_lived": life["steps_lived"],
        "paid_energy": acc["totals"]["energy"]["paid"],
        "paid_vigilance": acc["totals"]["vigilance"]["paid"],
        "inactive_steps": acc["inactive_steps"],
        "learning_computations": acc["learning_updates"],
        "retained_outcome_updates": life["retained_outcome_learning_updates"],
        "shadow_discarded_updates": life["shadow_discarded_outcome_updates"],
        "outcome_model_sha256": life["outcome_model_sha256"],
        "spatial_beliefs_sha256": life["spatial_beliefs_sha256"],
    }


def run():
    schedule, genomes = _preflight()
    receipts, source_hashes = [], set()
    for w in schedule["allocation"]:
        p, fam, repeat, index, seed = (
            w["population"], w["family"], w["repeat"],
            w["index"], w["life_seed"])
        # No P4b world before all source, allocation and G2 locks pass.
        spec = p2_ecologies.world_for(fam, "validation", index)
        world_hash = digest(world_snapshot(spec))
        for arm in p4b_schedule.ARMS:
            for slot in range(p4b_schedule.GENOTYPES):
                row = genomes[(p, arm, slot)]
                for mode in MODES:
                    life = run_life(row["genome"], spec, seed,
                                    p4b_schedule.HORIZON, protocol=PROTOCOL,
                                    learning_mode=mode, observer_mind_digest=True)
                    r = _receipt(life, world_hash=world_hash,
                                 genome_hash=row["genome_sha256"], mode=mode,
                                 population=p, arm=arm, slot=slot,
                                 family=fam, repeat=repeat, index=index, seed=seed)
                    source_hashes.add(r["source_sha256"])
                    receipts.append(r)
    if len(receipts) != p4b_schedule.LIVES or len(source_hashes) != 1:
        raise RuntimeError("incomplete or cross-source learning intervention")
    original = {
        "schema": PROTOCOL, "source_sha": _head_sha(),
        "schedule_sha256": schedule["sha256"],
        "g2_canonical_sha256": p4b_schedule.p4a_schedule.G2_CANONICAL_SHA256,
        "status": "P4B_PAID_OUTCOME_LEARNING_ONLY_NO_P4_RESERVE",
        "total_lives": len(receipts),
        "lives": receipts,
    }
    original["sha256"] = sha256(json.dumps(
        original, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return original


def summarize(original):
    populations = []
    for p in range(p4b_schedule.POPULATIONS):
        groups = {}
        for mode in MODES:
            lives = [x for x in original["lives"]
                     if x["population"] == p and x["mode"] == mode]
            groups[mode] = {
                "survivors": sum(x["censored"] for x in lives),
                "deaths": sum(not x["censored"] for x in lives),
                "paid_energy": round(sum(x["paid_energy"] for x in lives), 5),
                "paid_vigilance": round(sum(x["paid_vigilance"] for x in lives), 5),
                "inactive_steps": sum(x["inactive_steps"] for x in lives),
                "retained_outcome_updates": sum(x["retained_outcome_updates"] for x in lives),
                "shadow_discarded_updates": sum(x["shadow_discarded_updates"] for x in lives),
            }
        # Same genome, distinct experiences: compare repeat 0 vs repeat 1 in
        # the normal mode. This is a descriptive memory divergence check,
        # NOT proof of consciousness or of memory's survival benefit.
        different_models = comparable_pairs = 0
        for arm in p4b_schedule.ARMS:
            for slot in range(p4b_schedule.GENOTYPES):
                for family in p4b_schedule.FAMILIES:
                    pairs = [x for x in original["lives"]
                             if x["population"] == p and x["arm"] == arm
                             and x["slot"] == slot and x["family"] == family
                             and x["mode"] == "normal"]
                    pairs = sorted(pairs, key=lambda x: x["repeat"])
                    if len(pairs) != 2:
                        raise ValueError("missing matched history replicate")
                    if pairs[0]["genome_sha256"] != pairs[1]["genome_sha256"]:
                        raise ValueError("history subjects have different genomes")
                    comparable_pairs += 1
                    different_models += (pairs[0]["outcome_model_sha256"] !=
                                         pairs[1]["outcome_model_sha256"])
        populations.append({
            "population": p, "modes": groups,
            "normal_minus_shadow_censored": (
                groups["normal"]["survivors"] -
                groups["shadow_discard"]["survivors"]),
            "same_genome_different_history_pairs": comparable_pairs,
            "pairs_with_distinct_retained_outcome_models": different_models,
        })
    return {
        "schema": PROTOCOL, "source_sha": original["source_sha"],
        "schedule_sha256": original["schedule_sha256"],
        "original_sha256": original["sha256"], "total_lives": original["total_lives"],
        "status": original["status"], "populations": populations,
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        data = p4b_schedule.manifest()
        genomes = p4a_validation.verify_frozen_genomes()
        print(json.dumps({
            "schema": PROTOCOL, "status": "NO_P4B_WORLD_OPENED",
            "schedule_sha256": data["sha256"],
            "fresh_worlds": len(data["allocation"]),
            "genotypes": len(genomes), "lives": data["total_lives"]}, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--run":
        target = Path(sys.argv[2])
        if target.exists():
            raise FileExistsError("refuse to overwrite P4b original evidence")
        outcome = run()
        target.write_text(json.dumps(outcome, sort_keys=True, indent=2) + "\n")
        print(json.dumps(summarize(outcome), sort_keys=True, indent=2))
    else:
        raise SystemExit("usage: python -m i3.lab.p4b_validation --preflight | --run ORIGINAL.json")
