"""P5d fixed DEVELOPMENT-only 24-life resource acquisition diagnostic.

Six unused *development* keys 32..37, two engineering genotypes, two paid
curiosity-score arms; this is mechanism debugging, not independent science.
No selection, validation, reserve or retrospective survival-score tuning.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import sys

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

SCHEMA = "i3-p5d-resource-acquisition-development/v1"
MODES = ("normal", "discard_curiosity_bonus")
GENOME_SEEDS = (901, 902)
HORIZON = 120
INDEX_BASE = 32


def manifest():
    allocation = [
        {"family": family, "development_index": INDEX_BASE + 2 * f + repeat,
         "life_seed": 860000 + INDEX_BASE + 2 * f + repeat}
        for f, family in enumerate(p2_ecologies.FAMILIES)
        for repeat in (0, 1)]
    plan = {
        "schema": SCHEMA, "cohort": "DEVELOPMENT_ONLY",
        "allocation": allocation, "genome_seeds": list(GENOME_SEEDS),
        "modes": list(MODES), "horizon": HORIZON,
        "validation": "NOT_OPENED", "reserve": "LOCKED"}
    plan["sha256"] = sha256(json.dumps(
        plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return plan


def _first_difference(left, right, keys):
    for i in range(max(len(left), len(right))):
        a = left[i] if i < len(left) else None
        b = right[i] if i < len(right) else None
        if a is None or b is None or any(a[k] != b[k] for k in keys):
            return i + 1
    return None


def _paired_chronology(left, right):
    """Pre-action scores are comparable only while paths remain paired.

    A body match is necessary but NOT proof of equal private minds; option
    comparisons require both a genuinely funded common option and the same
    pre-decision body. Stop interpreting paid scores after first action change.
    Later divergence in uptake/body/funding is descriptive only.
    """
    first_action = _first_difference(left, right, ("action", "param"))
    boundary = min(len(left), len(right))
    if first_action is not None:
        boundary = min(boundary, first_action)
    first_offer = first_scored = first_paid_score = None
    matched_paid_options = 0
    matched_body_steps = 0
    for i in range(boundary):
        a, b = left[i], right[i]
        if a["body_before_decision"] != b["body_before_decision"]:
            continue
        matched_body_steps += 1
        if first_offer is None and (
                a["resource_options_offered"] != b["resource_options_offered"]):
            first_offer = i + 1
        if first_scored is None and (
                a["resource_options_scored"] != b["resource_options_scored"]):
            first_scored = i + 1
        by_a = {w["option"]: w for w in a["paid_resource_scores"]}
        by_b = {w["option"]: w for w in b["paid_resource_scores"]}
        for option in by_a.keys() & by_b.keys():
            matched_paid_options += 1
            if (first_paid_score is None and
                    abs(by_a[option]["total_score"] -
                        by_b[option]["total_score"]) > 1e-9):
                first_paid_score = i + 1
    return {
        "first_resource_offer_count_difference_same_body_before_action_change":
            first_offer,
        "first_resource_scored_count_difference_same_body_before_action_change":
            first_scored,
        "first_shared_paid_resource_option_score_difference_same_body_before_action_change":
            first_paid_score,
        "matched_pre_decision_body_steps": matched_body_steps,
        "matched_paid_resource_option_observations": matched_paid_options,
        "first_chosen_option_difference":
            _first_difference(left, right, ("chosen_option",)),
        "first_physical_action_difference": first_action,
        "first_resource_contact_difference":
            _first_difference(left, right, ("physical_resource_contact",)),
        "first_positive_uptake_difference":
            _first_difference(left, right,
                              ("positive_water_uptake", "positive_food_uptake")),
        "first_physical_body_difference":
            _first_difference(left, right, ("body_after_physics",)),
        "first_funding_difference":
            _first_difference(left, right, ("decision_funding",)),
    }

def _receipt(life, allocation, genome_seed, mode):
    obs = life["observer_resource_acquisition"]
    steps = obs["steps"]
    if len(steps) != life["steps_lived"]:
        raise RuntimeError("observer omitted a lived step")
    total = life["cognitive_accounting"]
    if total["shortfall_steps"] or total["pending_replays"]:
        raise RuntimeError("unpaid decision or replay")
    for channel in ("energy", "vigilance"):
        bill = total["totals"][channel]
        if abs(bill["requested"] - bill["paid"]) > 1e-8 or bill["unpaid"]:
            raise RuntimeError("unpaid cognitive channel")
    if obs["summary"]["physical_resource_contacts"] != sum(
            life["actions"].get(a, 0) for a in ("boire", "manger", "collecter")):
        raise RuntimeError("resource contact counter disagrees with physical actions")
    for row in steps:
        for phase in ("decision", "learning"):
            for channel in ("energy", "vigilance"):
                cost = row["paid_" + phase + "_" + channel]
                if cost < 0:
                    raise RuntimeError("negative paid work")
    return {
        "mode": mode, "family": allocation["family"],
        "development_index": allocation["development_index"],
        "life_seed": allocation["life_seed"], "genome_seed": genome_seed,
        "world_sha256": life["manifest"]["world_sha256"],
        "genome_sha256": life["genome"], "trace_head": life["trace_head"],
        "evidence_head": life["evidence_head"],
        "terminal": life["terminal"], "death_causes": life["death_causes"],
        "steps_lived": life["steps_lived"], "inactive_steps": total["inactive_steps"],
        "paid_energy": total["totals"]["energy"]["paid"],
        "paid_vigilance": total["totals"]["vigilance"]["paid"],
        "summary": obs["summary"],
        # Original first-person capture and lab-only outcomes; no mind input.
        "steps": steps,
    }


def run():
    plan = manifest()
    receipts, histories = [], {}
    for allocation in plan["allocation"]:
        idx = allocation["development_index"]
        if not INDEX_BASE <= idx < INDEX_BASE + 6:
            raise RuntimeError("not an approved development index")
        spec = p2_ecologies.world_for(
            allocation["family"], "development", idx)
        for genome_seed in GENOME_SEEDS:
            genome = generation_zero(genome_seed)
            for mode in MODES:
                life = run_life(
                    genome, spec, allocation["life_seed"], HORIZON,
                    protocol=SCHEMA, score_addend_mode=mode,
                    observer_resource_acquisition=True)
                receipt = _receipt(life, allocation, genome_seed, mode)
                receipts.append(receipt)
                histories[(idx, genome_seed, mode)] = receipt["steps"]
    if len(receipts) != 24:
        raise RuntimeError("incomplete development life panel")
    summary = {}
    for mode in MODES:
        rows = [r for r in receipts if r["mode"] == mode]
        action_counts = Counter()
        for row in rows:
            action_counts.update(row["summary"]["physical_resource_commands"])
        summary[mode] = {
            "lives": len(rows),
            "censored_at_120": sum(r["terminal"] == "censored" for r in rows),
            "death_causes": dict(Counter(
                cause for r in rows for cause in r["death_causes"])),
            "steps_lived": sum(r["steps_lived"] for r in rows),
            "inactive_steps": sum(r["inactive_steps"] for r in rows),
            "resource_options_offered": sum(
                r["summary"]["resource_options_offered"] for r in rows),
            "resource_options_scored": sum(
                r["summary"]["resource_options_scored"] for r in rows),
            "physical_resource_commands": dict(sorted(action_counts.items())),
            "collected_inventory": sum(
                r["summary"]["collected_inventory"] for r in rows),
            "positive_water_uptakes": sum(
                r["summary"]["positive_water_uptakes"] for r in rows),
            "positive_food_uptakes": sum(
                r["summary"]["positive_food_uptakes"] for r in rows),
            "paid_energy": sum(r["paid_energy"] for r in rows),
            "paid_vigilance": sum(r["paid_vigilance"] for r in rows),
        }
    paired = []
    for allocation in plan["allocation"]:
        for seed in GENOME_SEEDS:
            key = (allocation["development_index"], seed)
            left, right = (
                histories[(*key, mode)] for mode in MODES)
            paired.append({
                "development_index": key[0], "genome_seed": seed,
                **_paired_chronology(left, right),
            })
    return {
        "schema": SCHEMA, "manifest": plan,
        "status": "DEVELOPMENT_ONLY_NOT_HELDOUT_NOT_CAUSAL_MEDIATION",
        "summary": summary, "paired_chronology": paired,
        "receipts": receipts,
        "validation": "NOT_OPENED", "reserve": "LOCKED"}


if __name__ == "__main__":
    if sys.argv[1:] == ["--manifest"]:
        print(json.dumps(manifest(), sort_keys=True, indent=2))
    elif sys.argv[1:] == ["--run-development"]:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        raise SystemExit(
            "usage: python -m i3.lab.p5d_development --manifest | --run-development")
