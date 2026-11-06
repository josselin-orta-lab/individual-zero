"""P5d original-only paid eating-option diagnostic; never runs a life.

The original file is independently checked before any analysis. This reads
only already-paid option scores from the external observer, not Mind/World.
Resource-only score ranks cannot explain competition with rest or movement.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import sys

from i3.lab.p5d_custody import read_raw, verify_original

SCHEMA = "i3-p5d-original-eating-choice-posthoc/v1"
MOTOR_EAT_ENERGY = 0.5  # i3.modules.body.ACTION_COSTS["manger"]
VETO_INTEGRITY = 10.0   # i3.modules.mind.VETO_INTEGRITY


def classify_step(step):
    """Classify already-observed data; no counterfactual decision or score."""
    inventory = dict(step["capture_inventory"])
    scores = step["paid_resource_scores"]
    meals = [s for s in scores if s["option"].startswith("manger:")]
    if not inventory:
        if meals:
            raise ValueError("scored eating without carried food")
        return None
    if len(meals) > len(inventory):
        raise ValueError("more meal scores than distinct carried foods")
    ids = [s["option"] for s in meals]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate paid meal option")
    if step["resource_options_scored"] != len(scores):
        raise ValueError("unpaid resource score")
    if step["action"] == "manger" and not meals:
        raise ValueError("physical eating without paid plan")
    if step["chosen_option"] in ids and step["action"] != "manger":
        raise ValueError("chosen direct eating and different physical motor")
    energy_after_decision = (step["body_before_decision"][0]
                             - step["paid_decision_energy"])
    # This necessary motor-price test is not proof that the option won
    # or was rejected by the full controller (unobserved internal rank).
    affordable = energy_after_decision + 1e-10 >= MOTOR_EAT_ENERGY
    integrity_above_veto = step["body_before_decision"][3] > VETO_INTEGRITY
    top_resource = bool(meals and all(
        max(s["total_score"] for s in scores) - m["total_score"] <= 1e-9
        for m in meals))
    return {
        "meal_options_scored": len(meals),
        "funded_meal_option": bool(meals),
        "funded_decision": step["decision_funding"] == "FUNDED",
        "action_admitted": step["decision_outcome"] == "action_admitted",
        "selected_direct_meal": step["chosen_option"] in ids,
        "physically_ate": step["action"] == "manger",
        "meal_best_among_resource_scores_only": top_resource,
        "energy_for_meal_after_paid_decision": affordable,
        "integrity_above_innate_veto_threshold": integrity_above_veto,
        "meal_positive_curiosity_computed": sum(
            m["curiosity_computed"] > 0.0 for m in meals),
        "meal_curiosity_applied": sum(
            m["curiosity_applied"] > 0.0 for m in meals),
        "meal_negative_risk_applied": sum(m["risk_applied"] < 0 for m in meals),
        "chosen_action": step["action"],
    }


def analyze_original(path):
    raw = read_raw(path)
    # Validates raw digest, all 24 identities, full paid phase receipts,
    # first-person inventory conservation and no postmortem learning.
    verify_original(raw)
    data = json.loads(raw)
    counts = {mode: Counter() for mode in ("normal", "discard_curiosity_bonus")}
    by_life = []
    for life in data["receipts"]:
        mode = life["mode"]
        local = Counter()
        actions = Counter()
        for step in life["steps"]:
            obs = classify_step(step)
            if obs is None:
                continue
            local["carrying_steps"] += 1
            actions[str(obs["chosen_action"])] += 1
            for k, v in obs.items():
                if k == "chosen_action":
                    continue
                if k == "meal_options_scored":
                    local[k] += v
                else:
                    local[k] += int(v)
        for k, n in local.items():
            counts[mode][k] += n
        for action, n in actions.items():
            counts[mode]["chosen_action:" + action] += n
        by_life.append({
            "mode": mode,
            "development_index": life["development_index"],
            "genome_seed": life["genome_seed"],
            "carrying_steps": local["carrying_steps"],
            "meal_options_scored": local["meal_options_scored"],
            "selected_direct_meals": local["selected_direct_meal"],
            "physically_ate": local["physically_ate"],
        })
    for mode, c in counts.items():
        if c["selected_direct_meal"] != c["physically_ate"]:
            raise ValueError("meal choice and physical eating mismatch")
        if c["funded_meal_option"] > c["carrying_steps"]:
            raise ValueError("more paid meal steps than opportunities")
    return {
        "schema": SCHEMA,
        "status": "POSTHOC_ORIGINAL_DEVELOPMENT_ONLY_ZERO_NEW_LIVES",
        "original_raw_sha256": sha256(raw).hexdigest(),
        "aggregate": {k: dict(v) for k, v in counts.items()},
        "per_life": sorted(by_life, key=lambda x:
                           (x["development_index"], x["genome_seed"], x["mode"])),
        "limitations": {
            "full_candidate_scores": "NOT_RECORDED: rest, movement, exploration",
            "competition_accumulators": "NOT_RECORDED",
            "controller_winner_before_admission": "NOT_RECORDED",
            "innate_food_veto_for_each_option": "NOT_RECORDED",
            "interpretation": "Resource-only rank does not establish why an option was not chosen; costs and lived minds diverge.",
        },
    }


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5d_posthoc_eating original.json[.gz]")
    print(json.dumps(analyze_original(argv[1]), sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv)
