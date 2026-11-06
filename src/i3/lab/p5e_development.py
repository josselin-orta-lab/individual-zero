"""P5e fixed 24-life engineering pilot on NEW DEVELOPMENT worlds only.

This script has no genetic selection, no hidden-world truth in Mind, no
fitness tuning, no retries and no access to validation/reserve. Scores and
competition entries are copied from original prepaid Mind decisions.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import sys

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

SCHEMA = "i3-p5e-full-competition-development/v1"
INDEX_BASE = 38
HORIZON = 120
GENES = (901, 902)
MODES = ("normal", "discard_curiosity_bonus")


def manifest():
    alloc = [
        {"family": family, "development_index": INDEX_BASE + 2 * f + rep,
         "life_seed": 860000 + INDEX_BASE + 2 * f + rep}
        for f, family in enumerate(p2_ecologies.FAMILIES)
        for rep in (0, 1)
    ]
    out = {
        "schema": SCHEMA, "cohort": "DEVELOPMENT_ONLY",
        "allocation": alloc, "genome_seeds": list(GENES),
        "score_modes": list(MODES), "horizon": HORIZON,
        "validation": "NOT_OPENED", "reserve": "LOCKED",
        "purpose": "FULL_ALREADY_FUNDED_COMPETITION_READOUT",
        "selection": "NOT_OPENED"}
    out["sha256"] = sha256(json.dumps(
        out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return out


def classify_step(step):
    """Classify an actual paid witness without re-evaluating options."""
    scores = step["paid_option_scores"]
    comp = step["competition"]
    inventory = dict(step["inventory_before_decision"])
    result = Counter()
    if not inventory:
        return result
    result["carried_food_steps"] = 1
    meals = [s for s in scores if s["option"].startswith("manger:")]
    if not meals:
        result["no_paid_meal_option"] = 1
        return result
    result["paid_meal_opportunity_steps"] = 1
    if comp is None:
        raise RuntimeError("a paid meal requires actual competition")
    if comp["status"] not in ("ACTION_ADMITTED", "ALL_CONTROLS_REJECTED"):
        raise RuntimeError("undefined competition state")
    if len(meals) != len(set(s["option"] for s in meals)):
        raise RuntimeError("duplicate meal scores")
    meal_ids = {m["option"] for m in meals}
    score_max = max(s["total_score"] for s in scores)
    best_meal = max(m["total_score"] for m in meals)
    if best_meal >= score_max - 1e-9:
        result["meal_raw_top_or_tied_full"] = 1
    else:
        result["higher_scoring_nonmeal"] = 1
    winner = comp["winner_before_control"]
    if winner in meal_ids:
        result["meal_won_competition_before_control"] = 1
    else:
        result["nonmeal_won_competition_before_control"] = 1
        if result["meal_raw_top_or_tied_full"]:
            result["meal_top_but_other_competition_winner"] = 1
    mech = comp["selection_mechanism"]
    if mech not in ("threshold_crossing", "raw_score_fallback"):
        raise RuntimeError("unknown real competition mechanism")
    result["winner_by_" + mech] = 1
    if winner in meal_ids:
        result["meal_winner_by_" + mech] = 1
    attempts = comp["control_attempts"]
    if any(v["option"] in meal_ids and not v["admitted"] for v in attempts):
        result["meal_controller_rejected"] = 1
    selected = comp["final_admitted_option"]
    if selected in meal_ids:
        result["meal_admitted_after_control"] = 1
        if step["physical_action"] != "manger":
            raise RuntimeError("admitted direct meal did not eat")
    if step["physical_action"] == "manger":
        if selected not in meal_ids:
            raise RuntimeError("meal motor lacks admitted paid direct option")
        result["real_eating_actions"] = 1
    if selected in ("attendre", "dormir"):
        result["rest_selected_over_meal"] = 1
    elif selected and selected.startswith(("move:", "explorer:")):
        result["movement_or_exploration_selected_over_meal"] = 1
    elif selected and selected.startswith("collecter"):
        result["collection_selected_over_carried_meal"] = 1
    elif selected and selected.startswith(("goto-", "boire")):
        result["other_resource_selected_over_meal"] = 1
    elif selected is None:
        result["all_motors_rejected"] = 1
    # Consistency checks on recorded payer: includes option pricing from
    # real Mind.decide; never imply a counterfactual energy charge.
    if comp["paid_competition_cycles"] > step["paid_decision_work"]["cycles"]:
        raise RuntimeError("competition work was not paid")
    if result["real_eating_actions"] and not result["paid_meal_opportunity_steps"]:
        raise RuntimeError("unpaid eating")
    return result


def summarize(life):
    rows = life["observer_full_competition"]["steps"]
    if len(rows) != life["steps_lived"]:
        raise RuntimeError("missing original competition step")
    if life["cognitive_accounting"]["shortfall_steps"] or life["cognitive_accounting"]["pending_replays"]:
        raise RuntimeError("unpaid or pending cognition")
    for c in ("energy", "vigilance"):
        receipt = life["cognitive_accounting"]["totals"][c]
        if abs(receipt["requested"] - receipt["paid"]) > 1e-7 or receipt["unpaid"]:
            raise RuntimeError("unpaid cognitive channel")
    out = Counter()
    for step in rows:
        out.update(classify_step(step))
        if step["decision_outcome"] == "no_processing_budget":
            out["no_processing_budget_steps"] += 1
        if step["decision_outcome"] == "no_funded_score":
            out["no_funded_score_steps"] += 1
    if out["carried_food_steps"] != (
            out["paid_meal_opportunity_steps"] + out["no_paid_meal_option"]):
        raise RuntimeError("carried opportunities are not partitioned")
    if out["paid_meal_opportunity_steps"] != (
            out["meal_raw_top_or_tied_full"] + out["higher_scoring_nonmeal"]):
        raise RuntimeError("raw rank not partitioned")
    if out["paid_meal_opportunity_steps"] != (
            out["meal_won_competition_before_control"] +
            out["nonmeal_won_competition_before_control"]):
        raise RuntimeError("competition not partitioned")
    if out["real_eating_actions"] != life["meals"]:
        raise RuntimeError("eating witness disagrees with executed meals")
    return dict(out)


def run():
    plan = manifest()
    expected = [(r["development_index"], gene, mode) for r in plan["allocation"]
                for gene in GENES for mode in MODES]
    receipts = []
    for assignment in plan["allocation"]:
        idx = assignment["development_index"]
        if idx < 38 or idx > 43:
            raise RuntimeError("attempt to open a disallowed development index")
        spec = p2_ecologies.world_for(assignment["family"], "development", idx)
        for gene in GENES:
            genome = generation_zero(gene)
            for mode in MODES:
                original = run_life(
                    genome, spec, assignment["life_seed"], HORIZON,
                    protocol=SCHEMA, score_addend_mode=mode,
                    observer_full_competition=True)
                count = summarize(original)
                receipts.append({
                    "family": assignment["family"],
                    "development_index": idx,
                    "genome_seed": gene, "life_seed": assignment["life_seed"],
                    "mode": mode, "world_sha256": original["manifest"]["world_sha256"],
                    "genome_sha256": original["genome"],
                    "manifest_id": original["manifest_id"],
                    "trace_head": original["trace_head"],
                    "evidence_head": original["evidence_head"],
                    "terminal": original["terminal"],
                    "death_causes": original["death_causes"],
                    "steps_lived": original["steps_lived"],
                    "paid_work": original["cognitive_accounting"],
                    "counts": count,
                    "competition_steps": original["observer_full_competition"]["steps"],
                })
    actual = [(r["development_index"], r["genome_seed"], r["mode"]) for r in receipts]
    if actual != expected or len(set(actual)) != 24:
        raise RuntimeError("incomplete or duplicate original development allocation")
    for idx in range(38, 44):
        for seed in GENES:
            rows = [r for r in receipts if r["development_index"] == idx and
                    r["genome_seed"] == seed]
            if len(rows) != 2 or rows[0]["world_sha256"] != rows[1]["world_sha256"] or (
                    rows[0]["genome_sha256"] != rows[1]["genome_sha256"]):
                raise RuntimeError("paired world/genome mismatch")
    summary = {}
    for mode in MODES:
        rows = [r for r in receipts if r["mode"] == mode]
        counts = Counter()
        for row in rows:
            counts.update(row["counts"])
        summary[mode] = {
            "lives": len(rows),
            "censored_at_120": sum(r["terminal"] == "censored" for r in rows),
            "death_causes": dict(Counter(
                c for r in rows for c in r["death_causes"])),
            "lived_steps": sum(r["steps_lived"] for r in rows),
            "counts": dict(counts),
            "paid_energy": sum(r["paid_work"]["totals"]["energy"]["paid"] for r in rows),
            "paid_vigilance": sum(r["paid_work"]["totals"]["vigilance"]["paid"] for r in rows),
        }
    return {
        "schema": SCHEMA,
        "status": "FIRST_ORIGINAL_DEVELOPMENT_ONLY_NOT_HELDOUT_NOT_CAUSAL",
        "manifest": plan, "summary": summary, "receipts": receipts,
        "validation": "NOT_OPENED", "reserve": "LOCKED",
        "independent_populations": 0,
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--manifest"]:
        print(json.dumps(manifest(), sort_keys=True, indent=2))
    elif sys.argv[1:] == ["--run-development"]:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        raise SystemExit("usage: python -m i3.lab.p5e_development --manifest | --run-development")
