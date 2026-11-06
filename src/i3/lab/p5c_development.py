"""P5c fixed DEVELOPMENT-only score addend diagnostic, never scientific evidence.

Paired G0 engineering genomes on six development ecology instances,
without touching any selection/validation/reserve world. Records all
executed/prepaid score components as external read-only observer evidence.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import sys

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

SCHEMA = "i3-p5c-paid-score-addends-development-v1"
MODES = ("normal", "discard_curiosity_bonus",
         "discard_risk_penalty", "discard_both_bonus_terms")
GENOME_SEEDS = (901, 902)
FAMILIES = p2_ecologies.FAMILIES
REPEATS = (0, 1)
HORIZON = 120
INDEX_BASE = 26


def manifest():
    allocation = [
        {"family": family, "repeat": repeat,
         "development_index": INDEX_BASE + 2 * i + repeat,
         "life_seed": 660000 + INDEX_BASE + 2 * i + repeat}
        for i, family in enumerate(FAMILIES) for repeat in REPEATS
    ]
    data = {
        "schema": SCHEMA, "modes": list(MODES),
        "genome_seeds": list(GENOME_SEEDS),
        "cohort": "DEVELOPMENT_ONLY",
        "allocation": allocation, "horizon": HORIZON,
        "validation": "NOT_OPENED", "reserve": "LOCKED",
    }
    data["sha256"] = sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return data


def _scoring_trace(life):
    history = []
    for row in life["trace"]:
        obs = row["info"]["observer"]
        witness = obs["score_witness"]
        if len(witness) != obs["scored_options"]:
            raise RuntimeError("unfunded option score witness")
        for w in witness:
            if abs(w["total_score"] - w["base_return"] -
                   w["curiosity_bonus_applied"] -
                   w["risk_penalty_applied"]) > 1e-8:
                raise RuntimeError("inconsistent applied P5c score")
        history.append({
            "action": row["action"], "param": row["param"],
            "pre_body": list(obs["pre_body"]),
            "scores": {w["option"]: {
                "base": w["base_return"],
                "curiosity_calculated": w["curiosity_bonus_computed"],
                "risk_calculated": w["risk_penalty_computed"],
                "curiosity_applied": w["curiosity_bonus_applied"],
                "risk_applied": w["risk_penalty_applied"],
                "total": w["total_score"]}
                for w in witness},
            "paid_decision_energy":
                row["funding_phases"]["decision"]["accounting"]["energy"]["paid"],
            "paid_decision_vigilance":
                row["funding_phases"]["decision"]["accounting"]["vigilance"]["paid"],
            "funding": row["info"]["funding"],
        })
    return history


def _paired(first, second):
    """Same paid option at same body up to first different physical action."""
    score = component = action = None
    opportunities = 0
    for i in range(min(len(first), len(second))):
        a, b = first[i], second[i]
        if a["pre_body"] == b["pre_body"]:
            for option in a["scores"].keys() & b["scores"].keys():
                x, y = a["scores"][option], b["scores"][option]
                opportunities += 1
                if component is None and any(
                    abs(x[k] - y[k]) > 1e-9
                    for k in ("curiosity_applied", "risk_applied")):
                    component = i + 1
                if score is None and abs(x["total"] - y["total"]) > 1e-9:
                    score = i + 1
        if (a["action"], a["param"]) != (b["action"], b["param"]):
            action = i + 1
            break
    return {
        "first_component_change": component,
        "first_score_change": score,
        "first_action_change": action,
        "matched_paid_option_observations": opportunities,
    }


def run():
    schedule = manifest()
    histories, receipts = {}, []
    for allocated in schedule["allocation"]:
        family = allocated["family"]
        idx = allocated["development_index"]
        if not 26 <= idx < 32:
            raise RuntimeError("invalid development index")
        spec = p2_ecologies.world_for(family, "development", idx)
        for genome_seed in GENOME_SEEDS:
            genome = generation_zero(genome_seed)
            for mode in MODES:
                life = run_life(
                    genome, spec, allocated["life_seed"], HORIZON,
                    protocol=SCHEMA, keep_trace=True,
                    score_addend_mode=mode,
                    observer_decision_diagnostics=True)
                acc = life["cognitive_accounting"]
                if (acc["shortfall_steps"] != 0 or acc["pending_replays"] != 0):
                    raise RuntimeError("unpaid cognitive work")
                for ch in ("energy", "vigilance"):
                    paid = acc["totals"][ch]
                    if (abs(paid["requested"] - paid["paid"]) > 1e-8 or
                        paid["unpaid"] != 0):
                        raise RuntimeError("unpaid work or fake charge")
                for step in life["trace"]:
                    for phase in ("decision", "learning"):
                        for ch in ("energy", "vigilance"):
                            bill = step["funding_phases"][phase]["accounting"][ch]
                            if (abs(bill["requested"] - bill["paid"]) > 1e-8 or
                                bill["unpaid"] != 0):
                                raise RuntimeError("unpaid phase work")
                    if step["dead"] and any(
                            step["funding_phases"]["learning"]["work"].values()):
                        raise RuntimeError("postmortem learning")
                history = _scoring_trace(life)
                histories[(idx, genome_seed, mode)] = history
                receipts.append({
                    "family": family, "development_index": idx,
                    "genome_seed": genome_seed, "mode": mode,
                    "life_seed": allocated["life_seed"],
                    "world_sha256": life["manifest"]["world_sha256"],
                    "evidence_head": life["evidence_head"],
                    "terminal": life["terminal"],
                    "steps": life["steps_lived"],
                    "inactive": acc["inactive_steps"],
                    "paid_energy": acc["totals"]["energy"]["paid"],
                    "paid_vigilance": acc["totals"]["vigilance"]["paid"],
                    "admitted": life["observer_decision_diagnostics"]["action_admitted"],
                    "no_processing_budget":
                        life["observer_decision_diagnostics"]["no_processing_budget"],
                    "effect_learning_updates": acc["learning_updates"],
                })
    if len(receipts) != 48:
        raise RuntimeError("missing development lives")
    comparison, paired = {}, {}
    for mode in MODES:
        rows = [r for r in receipts if r["mode"] == mode]
        comparison[mode] = {
            "lives": len(rows),
            "censored_at_120": sum(r["terminal"] == "censored" for r in rows),
            "steps_lived": sum(r["steps"] for r in rows),
            "inactive_steps": sum(r["inactive"] for r in rows),
            "paid_energy": round(sum(r["paid_energy"] for r in rows), 6),
            "paid_vigilance": round(sum(r["paid_vigilance"] for r in rows), 6),
            "admitted": sum(r["admitted"] for r in rows),
            "no_processing_budget": sum(r["no_processing_budget"] for r in rows),
        }
    for mode in MODES[1:]:
        rows = []
        for allocation in schedule["allocation"]:
            for genome_seed in GENOME_SEEDS:
                idx = allocation["development_index"]
                rows.append(_paired(
                    histories[(idx, genome_seed, "normal")],
                    histories[(idx, genome_seed, mode)]))
        paired[mode] = {
            "pairs": len(rows),
            "score_divergent_pairs": sum(r["first_score_change"] is not None for r in rows),
            "action_divergent_pairs": sum(r["first_action_change"] is not None for r in rows),
            "component_divergent_pairs": sum(
                r["first_component_change"] is not None for r in rows),
            "first_score_change": min(
                (r["first_score_change"] for r in rows
                 if r["first_score_change"] is not None), default=None),
            "first_action_change": min(
                (r["first_action_change"] for r in rows
                 if r["first_action_change"] is not None), default=None),
        }
    return {
        "schema": SCHEMA,
        "status": "ENGINEERING_DEVELOPMENT_ONLY_NOT_HELDOUT_SCIENCE",
        "manifest_sha256": schedule["sha256"],
        "comparison": comparison, "paired": paired,
        "receipts": receipts, "validation": "NOT_OPENED", "reserve": "LOCKED",
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--manifest"]:
        print(json.dumps(manifest(), sort_keys=True, indent=2))
    elif sys.argv[1:] == ["--run-development"]:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        raise SystemExit(
            "usage: python -m i3.lab.p5c_development --manifest | --run-development")
