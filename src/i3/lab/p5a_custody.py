"""Read-only P5a evidence custodian: never executes a new life/world.

This program checks the original signed scientific outcome against the
prospective allocation, frozen G2 genotypes, phase-paid work and pairing,
then recomputes the preregistered four-population analysis.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

from i3.lab import p4a_validation, p5a_schedule, p5a_screen

EXPECTED_SOURCE_SHA = "ee2e97b1949fd94548fe6c5908ff411d37cb3f76"
EXPECTED_SCHEDULE_SHA = "2e176df5c1ebf9435d2ad4d83e97334d63634024ead074781eed3841b846bb7a"
EXPECTED_COUNT = 1152
MODES = p5a_schedule.MODES


def verify_original(out: dict) -> dict:
    schedule = p5a_schedule.manifest()
    if schedule["sha256"] != EXPECTED_SCHEDULE_SHA:
        raise ValueError("original schedule contract changed")
    if (out.get("schema") != p5a_schedule.PROTOCOL or
        out.get("source_sha") != EXPECTED_SOURCE_SHA or
        out.get("schedule_sha256") != EXPECTED_SCHEDULE_SHA or
        out.get("status") != "P5A_COMPONENT_SCREEN_NO_P4_RESERVE" or
        out.get("frozen_g2_sha256") != p5a_schedule.p4a_schedule.G2_CANONICAL_SHA256 or
        out.get("total_lives") != EXPECTED_COUNT or
        len(out.get("lives", ())) != EXPECTED_COUNT):
        raise ValueError("incomplete original or incorrect protocol")
    raw = {k: v for k, v in out.items() if k != "sha256"}
    if sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != out["sha256"]:
        raise ValueError("original canonical payload SHA-256 mismatch")
    genomes = p4a_validation.verify_frozen_genomes()
    allocation = {(x["population"], x["family"], x["repeat"]): x
                  for x in schedule["allocation"]}
    keys = set()
    opportunities = {}
    source_sha = set()
    for receipt in out["lives"]:
        p, arm, slot = (receipt["population"], receipt["arm"], receipt["slot"])
        family, repeat, mode = (receipt["family"], receipt["repeat"], receipt["mode"])
        if (type(p) is not int or
            type(slot) is not int or type(repeat) is not int or
            not 0 <= p < p5a_schedule.POPULATIONS or
            arm not in p5a_schedule.ARMS or
            not 0 <= slot < p5a_schedule.GENOTYPES or
            family not in p5a_schedule.FAMILIES or
            not 0 <= repeat < p5a_schedule.REPEATS or
            mode not in MODES):
            raise ValueError("unregistered genotype or experimental condition")
        key = (p, arm, slot, family, repeat, mode)
        if key in keys:
            raise ValueError("duplicated life identity")
        keys.add(key)
        w = allocation[(p, family, repeat)]
        if (receipt["validation_world_index"] != w["index"] or
            receipt["life_seed"] != w["life_seed"] or
            receipt["genome_sha256"] != genomes[(p, arm, slot)]["genome_sha256"] or
            not receipt["evidence_head"] or not receipt["manifest_id"] or
            not receipt["trace_head"]):
            raise ValueError("world, seed, genotype or witness altered")
        opportunity = (receipt["world_sha256"], receipt["life_seed"])
        if (p, family, repeat) in opportunities and opportunities[(p, family, repeat)] != opportunity:
            raise ValueError("paired initial opportunity not identical")
        opportunities[(p, family, repeat)] = opportunity
        source_sha.add(receipt["source_sha256"])
        steps = receipt["steps_lived"]
        dead = receipt["terminal"] == "dead"
        if (type(steps) is not int or not 1 <= steps <= p5a_schedule.HORIZON or
            receipt["terminal"] not in ("dead", "censored") or
            receipt["censored"] == dead or
            (not dead and steps != p5a_schedule.HORIZON) or
            bool(receipt["death_causes"]) != dead):
            raise ValueError("fabricated death or censoring")
        if (type(receipt["inactive_steps"]) is not int or
            not 0 <= receipt["inactive_steps"] <= steps):
            raise ValueError("invalid physical inactivity")
        if (receipt["learning_computations"] < 0 or
            receipt["replays_executed"] < 0 or
            receipt["replays_executed"] != receipt["phase_work"]["learning"]["replays"]):
            raise ValueError("incorrect paid replay execution")
        for ch in ("energy", "vigilance"):
            amount = receipt["paid"][ch]
            phase_sum = sum(receipt["phase_paid"][phase][ch]
                            for phase in ("decision", "learning"))
            if amount < 0 or abs(amount - phase_sum) > 1e-7:
                raise ValueError("unreconciled per-life cognition payment")
        for phase in ("decision", "learning"):
            for key_work in ("cycles", "simulated_steps", "memory_items", "replays"):
                v = receipt["phase_work"][phase][key_work]
                if type(v) is not int or v < 0:
                    raise ValueError("noninteger or negative actual work")
    if (len(keys) != EXPECTED_COUNT or len(opportunities) != 24 or
        len({w for w, seed in opportunities.values()}) != 24 or
        len(source_sha) != 1 or
        len({r["evidence_head"] for r in out["lives"]}) != EXPECTED_COUNT):
        raise ValueError("missing or overlapping original scientific evidence")
    result = p5a_screen.summarize(out)
    for group in result["populations"]:
        for mode in MODES:
            if group["modes"][mode]["censored"] + group["modes"][mode]["dead"] != 72:
                raise ValueError("incomplete population-level result")
    return {
        "protocol": p5a_schedule.PROTOCOL,
        "status": "ORIGINAL_VERIFIED_NO_NEW_LIVES",
        "source_sha": EXPECTED_SOURCE_SHA,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA,
        "original_canonical_sha256": out["sha256"],
        "total_lives": EXPECTED_COUNT,
        "worlds": len(opportunities),
        "paired_genomes_modes": EXPECTED_COUNT // len(MODES),
        "comparisons": result["contrasts"],
        "population_results": result["populations"],
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5a_custody ORIGINAL.json")
    original = json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(verify_original(original), indent=2, sort_keys=True))
