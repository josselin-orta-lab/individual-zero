"""Independent read-only P5b original evidence custody. Opens NO study worlds."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from i3.lab import p4a_validation, p5b_schedule, p5b_heldout

SOURCE_SHA = "11bd249d269116a720e503bc56e9b1244e91aea9"
SCHEDULE_SHA = "663e258b3c35e5b8d2f60d437e7ecc3079484dfe07f956d9d50bf775f69a66d1"
MODES = p5b_schedule.READOUTS
WORK = ("cycles", "simulated_steps", "memory_items", "replays")
CHANNELS = ("energy", "vigilance")
PHASES = ("decision", "learning")


def verify(original: dict) -> dict:
    schedule = p5b_schedule.manifest()
    if schedule["sha256"] != SCHEDULE_SHA:
        raise ValueError("registered P5b source schedule mutated")
    if (original.get("schema") != p5b_schedule.PROTOCOL or
        original.get("source_sha") != SOURCE_SHA or
        original.get("schedule_sha256") != SCHEDULE_SHA or
        original.get("frozen_g2_sha256") != p5b_schedule.p4a_schedule.G2_CANONICAL_SHA256 or
        original.get("status") != "P5B_READOUT_HELDOUT_NO_RESERVE" or
        original.get("total_lives") != p5b_schedule.LIVES or
        len(original.get("lives", ())) != p5b_schedule.LIVES):
        raise ValueError("P5b original study provenance or count mismatch")
    canonical = sha256(json.dumps(
        {k: v for k, v in original.items() if k != "sha256"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if original.get("sha256") != canonical:
        raise ValueError("unaltered P5b canonical original checksum mismatch")

    genes = p4a_validation.verify_frozen_genomes()
    allocation = {(a["population"], a["family"], a["repeat"]): a
                  for a in schedule["exposure"]}
    identifiers, world_receipts, source_digests = set(), {}, set()
    by_population = {p: {mode: 0 for mode in MODES}
                     for p in range(p5b_schedule.POPULATIONS)}
    for life in original["lives"]:
        p, arm, slot, fam, rep, mode = (life[k] for k in (
            "population", "arm", "slot", "family", "repeat", "mode"))
        if (type(p) is not int or not 0 <= p < p5b_schedule.POPULATIONS or
            arm not in p5b_schedule.ARMS or
            type(slot) is not int or not 0 <= slot < p5b_schedule.GENOTYPES or
            fam not in p5b_schedule.FAMILIES or
            type(rep) is not int or not 0 <= rep < p5b_schedule.REPEATS or
            mode not in MODES):
            raise ValueError("unregistered life identity")
        key = (p, arm, slot, fam, rep, mode)
        if key in identifiers:
            raise ValueError("duplicate P5b experimental life identity")
        identifiers.add(key)
        w = allocation[(p, fam, rep)]
        gene = genes[(p, arm, slot)]
        if (life["validation_world_index"] != w["index"] or
            life["life_seed"] != w["life_seed"] or
            life["genome_sha256"] != gene["genome_sha256"] or
            not life["world_sha256"] or
            not life["manifest_id"] or not life["trace_head"] or
            not life["evidence_head"] or not life["source_sha256"]):
            raise ValueError("mismatched preregistered world/genome/seed or trace")
        source_digests.add(life["source_sha256"])
        world_key = (p, fam, rep)
        physical_opportunity = (life["world_sha256"], life["life_seed"])
        if (world_key in world_receipts and
            world_receipts[world_key] != physical_opportunity):
            raise ValueError("paired modes saw different physical world opportunities")
        world_receipts[world_key] = physical_opportunity
        steps = life["steps_lived"]
        dead = life["terminal"] == "dead"
        if (type(steps) is not int or not 1 <= steps <= p5b_schedule.HORIZON or
            life["terminal"] not in ("dead", "censored") or
            life["censored"] != (not dead) or
            (not dead and (steps != p5b_schedule.HORIZON or life["death_causes"])) or
            (dead and not life["death_causes"]) or
            type(life["inactive_steps"]) is not int or
            not 0 <= life["inactive_steps"] <= steps):
            raise ValueError("falsified terminal or duration")
        by_population[p][mode] += int(life["censored"])
        statuses = life["decision_status"]
        if (set(statuses) != {"no_processing_budget", "no_funded_score",
                             "control_rejected", "action_admitted"} or
            any(type(v) is not int or v < 0 for v in statuses.values()) or
            sum(statuses.values()) != steps):
            raise ValueError("invalid observer event ledger")
        for phase in PHASES:
            if set(life["phase_work"][phase]) != set(WORK):
                raise ValueError("missing work vector")
            if any(type(v) is not int or v < 0
                   for v in life["phase_work"][phase].values()):
                raise ValueError("invalid paid work counter")
        if life["replays_executed"] != life["phase_work"]["learning"]["replays"]:
            raise ValueError("fabricated replay count")
        for ch in CHANNELS:
            paid = life["paid"][ch]
            amount = sum(life["phase_paid"][phase][ch] for phase in PHASES)
            if paid < 0 or abs(paid-amount) > 1e-7:
                raise ValueError("unreconciled energy/vigilance phase")
        early = life["early_witness"]
        if len(early) != min(steps, p5b_schedule.MECHANISTIC_WINDOW):
            raise ValueError("truncated or fabricated early-decision witness")
        for index, step in enumerate(early):
            if (step["t"] != index+1 or len(step["pre_body"]) != 5 or
                step["funding"] not in (
                    "FUNDED", "NO_PROCESSING_BUDGET",
                    "NO_FUNDED_SCORE", "NO_FUNDED_MOTOR")):
                raise ValueError("invalid early opportunity witness")
            for score in step["scores"]:
                if (not score["option"] or
                    abs(score["base_return"] + score["bonus"] -
                        score["score"]) > 1e-7):
                    raise ValueError("fabricated funded candidate score")
    if (len(identifiers) != p5b_schedule.LIVES or
        len(world_receipts) != 24 or
        len({x[0] for x in world_receipts.values()}) != 24 or
        len(source_digests) != 1):
        raise ValueError("incomplete or inconsistent original science custody")
    for p in by_population:
        for mode in MODES:
            if sum(1 for r in original["lives"] if
                   r["population"] == p and r["mode"] == mode) != 72:
                raise ValueError("invalid population/mode assignment")
    summary = p5b_heldout.summarize(original)
    if (len(summary["populations"]) != 4 or
        set(summary["contrasts"]) != set(MODES[1:])):
        raise ValueError("analysis no longer follows original registration")
    return {
        "protocol": p5b_schedule.PROTOCOL,
        "status": "ORIGINAL_VERIFIED_NO_NEW_LIVES",
        "raw_canonical_sha256": original["sha256"],
        "source_sha": SOURCE_SHA, "schedule_sha256": SCHEDULE_SHA,
        "worlds": len(world_receipts), "original_lives": len(identifiers),
        "paired_genome_world_keys": len(identifiers) // len(MODES),
        "survivors_by_population": by_population,
        "analysis": summary,
        "limitation": "n4_population_inference_not_independent_lives",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5b_custody ORIGINAL.json")
    original = json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(verify(original), sort_keys=True, indent=2))
