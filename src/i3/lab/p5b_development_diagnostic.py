"""P5b DEVELOPMENT-only deterministic causal-interface diagnostics.

No scientific cohort, no validation/reserve world, no genetic selection.
Runs small G0 engineering fixtures solely to locate decision/funding collapse.
Results NEVER count as heldout evidence or authorize tuning to P5a outcomes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import sys

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero, digest as genome_digest
from i3.runtime.life import run_life

SCHEMA = "i3-p5b-development-readout-diagnostics-v1"
MODES = ("full", "blind_predictions", "blind_sources", "blind_all")
GENOME_SEEDS = (901, 902)
FAMILIES = p2_ecologies.FAMILIES
REPEATS = (0, 1)
HORIZON = 120
# The first 18 development indices have earlier engineering uses; these
# six distinct engineering keys are chosen without consulting P5a lives.
INDEX_BASE = 20


def manifest():
    allocations = [
        {"family": family, "repeat": repeat,
         "development_index": INDEX_BASE + i * len(REPEATS) + repeat,
         "life_seed": 460000 + INDEX_BASE + i * len(REPEATS) + repeat}
        for i, family in enumerate(FAMILIES) for repeat in REPEATS
    ]
    data = {
        "schema": SCHEMA, "modes": list(MODES),
        "genome_seeds": list(GENOME_SEEDS),
        "genome_policy": "generation_zero_no_selection",
        "horizon": HORIZON,
        "allocations": allocations,
        "study_cohort": "DEVELOPMENT_ONLY",
        "validation": "NOT_OPENED", "reserve": "LOCKED",
    }
    data["sha256"] = sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data


def run():
    plan = manifest()
    receipts = []
    for allocation in plan["allocations"]:
        family, index = allocation["family"], allocation["development_index"]
        if not 20 <= index < 26:
            raise RuntimeError("non-development index")
        spec = p2_ecologies.world_for(family, "development", index)
        for gene_seed in GENOME_SEEDS:
            genome = generation_zero(gene_seed)
            for mode in MODES:
                life = run_life(
                    genome, spec, allocation["life_seed"], HORIZON,
                    protocol=SCHEMA,
                    effect_readout=mode, observer_decision_diagnostics=True)
                acc = life["cognitive_accounting"]
                for channel in ("energy", "vigilance"):
                    bill = acc["totals"][channel]
                    if (bill["unpaid"] > 1e-9 or
                        abs(bill["requested"] - bill["paid"]) > 1e-9):
                        raise RuntimeError("unpaid cognitive work")
                if acc["shortfall_steps"] or acc["pending_replays"]:
                    raise RuntimeError("incomplete cognitive payment")
                observer = life["observer_decision_diagnostics"]
                if (sum(observer[k] for k in
                        ("no_processing_budget", "no_funded_score",
                         "control_rejected", "action_admitted"))
                        != life["steps_lived"]):
                    raise RuntimeError("observer missed physical steps")
                for prefix in ("offered", "scored"):
                    if sum(observer[prefix+"_families"].values()) != observer[prefix+"_options"]:
                        raise RuntimeError("incorrect option-category report")
                receipts.append({
                    "mode": mode, "genome_seed": gene_seed,
                    "genome_sha256": genome_digest(genome),
                    "family": family, "development_index": index,
                    "life_seed": allocation["life_seed"],
                    "terminal": life["terminal"],
                    "censored": life["terminal"] == "censored",
                    "steps_lived": life["steps_lived"],
                    "inactive_steps": acc["inactive_steps"],
                    "energy_paid": acc["totals"]["energy"]["paid"],
                    "vigilance_paid": acc["totals"]["vigilance"]["paid"],
                    "observer": observer,
                    "actions": life["actions"],
                    "death_causes": life["death_causes"],
                    "world_sha256": life["manifest"]["world_sha256"],
                    "evidence_head": life["evidence_head"],
                })
    expected = len(FAMILIES) * len(REPEATS) * len(GENOME_SEEDS) * len(MODES)
    if len(receipts) != expected:
        raise RuntimeError("incomplete development comparison")
    results = {}
    for mode in MODES:
        rows = [x for x in receipts if x["mode"] == mode]
        decision = Counter()
        families_offered = Counter()
        families_scored = Counter()
        actions = Counter()
        for row in rows:
            actions.update(row["actions"])
            for k, v in row["observer"].items():
                if k == "offered_families":
                    families_offered.update(v)
                elif k == "scored_families":
                    families_scored.update(v)
                else:
                    decision[k] += v
        results[mode] = {
            "lives": len(rows),
            "censored": sum(x["censored"] for x in rows),
            "lived_steps": sum(x["steps_lived"] for x in rows),
            "inactive_steps": sum(x["inactive_steps"] for x in rows),
            "energy_paid": round(sum(x["energy_paid"] for x in rows), 6),
            "vigilance_paid": round(sum(x["vigilance_paid"] for x in rows), 6),
            "decision": dict(decision),
            "offered_families": dict(families_offered),
            "scored_families": dict(families_scored),
            "actions": dict(actions),
        }
    return {
        "schema": SCHEMA,
        "status": "ENGINEERING_DEVELOPMENT_ONLY_NOT_SCIENTIFIC_EVIDENCE",
        "manifest_sha256": plan["sha256"],
        "comparison": results,
        "lives": receipts,
        "validation": "NOT_OPENED",
        "reserve": "LOCKED",
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--manifest"]:
        print(json.dumps(manifest(), sort_keys=True, indent=2))
    elif sys.argv[1:] == ["--run-development"]:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        raise SystemExit(
            "usage: python -m i3.lab.p5b_development_diagnostic --manifest | --run-development")
