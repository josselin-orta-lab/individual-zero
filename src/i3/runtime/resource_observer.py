"""P5d: read-only witness of first-person opportunities and actual resource uptake.

This is laboratory instrumentation, NOT a Mind component or a source of new
choices. Raw physical outcomes are read only after the world accepts an action.
An admitted resource command proves contact, not positive nutritional gain.
"""
from __future__ import annotations

from collections import Counter

from i3.modules.body import F, I, W

SCHEMA = "i3-p5d-resource-acquisition-observer/v1"
RESOURCE_ACTIONS = ("boire", "collecter", "manger")


def _resource_option(oid: str) -> bool:
    """Exactly mirror the existing Mind observer family classification."""
    return (oid not in ("dormir", "attendre")
            and not oid.startswith(("explorer:", "move:")))


class ResourceObserver:
    """Collect external receipts; never write World, Mind, body or work.

    prepare() is called after the original paid decision, before the world
    transaction. commit() is called only after a successful world transaction
    and learning payment. No failed action may be reported as physical contact.
    """

    def __init__(self):
        self._previously_mapped = set()
        self.steps = []

    def prepare(self, *, cap, mind, info, action, param):
        diag = info["observer"]
        newly_mapped = set(mind.hist) - self._previously_mapped
        self._previously_mapped.update(mind.hist)
        scored = [{
            "option": item["option"],
            "base_return": item["base_return"],
            "curiosity_computed": item["curiosity_bonus_computed"],
            "curiosity_applied": item["curiosity_bonus_applied"],
            "risk_computed": item["risk_penalty_computed"],
            "risk_applied": item["risk_penalty_applied"],
            "total_score": item["total_score"],
            "uncertainty": item["uncertainty"],
        } for item in diag["score_witness"]
            if _resource_option(item["option"])]
        if len(scored) != diag["scored_families"]["resource"]:
            raise RuntimeError("P5d resource witness does not match paid options")
        here = cap["here"]
        return {
            "step": len(self.steps) + 1,
            "body_before_decision": list(cap["body"]),
            "personal_position": list(mind.pos),
            "new_personally_mapped_cells": len(newly_mapped),
            "total_personally_mapped_cells": len(self._previously_mapped),
            # The first-person input to Mind, not an inspection of hidden
            # stocks or token effects. Neighbor input can be perceptually
            # missed by Mind; it is labelled as capture, not a belief.
            "capture_here_water": bool(here[0]),
            "capture_here_food_tokens": list(here[1]),
            "capture_neighbor_water_cells": sum(
                bool(cell[0]) for cell in cap["neighbors"] if cell is not None),
            "capture_neighbor_food_cells": sum(
                bool(cell[1]) for cell in cap["neighbors"] if cell is not None),
            "capture_inventory": [list(item) for item in cap["inventory"]],
            "capture_food": cap["body"][F],
            "capture_water": cap["body"][W],
            "personally_computed_urgency": info.get("urgency"),
            "decision_funding": info["funding"],
            "decision_outcome": diag["decision_outcome"],
            "resource_options_offered": diag["offered_families"]["resource"],
            "resource_options_scored": diag["scored_families"]["resource"],
            "paid_resource_scores": scored,
            "chosen_option": info["option"],
            "action": action,
            "param": param,
            "_pre_inventory": dict(cap["inventory"]),
        }

    def commit(self, pending, *, world, physical_body, dead, phases):
        """Record transactionally admitted contact and physical uptake.

        Water/food uptake is the observed change above the passive metabolic
        decay baseline, after clipping at 0 and 100. This can be zero or
        negative despite a valid source contact. It is not a hidden source
        gain read by Mind, nor a causal estimate against a counterfactual life.
        """
        event = dict(pending)
        before_inventory = event.pop("_pre_inventory")
        after_inventory = dict(world.capture()["inventory"])
        action, token = event["action"], event["param"]
        inventory_change = (after_inventory.get(token, 0)
                            - before_inventory.get(token, 0)
                            if action in ("collecter", "manger") else None)
        pre_body = event["body_before_decision"]
        water_uptake = (physical_body[W] -
                        max(0.0, pre_body[W] - world.laws.water_decay)
                        if action == "boire" else None)
        food_uptake = (physical_body[F] -
                       max(0.0, pre_body[F] - world.laws.food_decay)
                       if action == "manger" else None)
        event.update({
            "physical_resource_attempt": action in RESOURCE_ACTIONS,
            # World.step rejects absent/depleted stock transactionally.
            "physical_resource_contact": action in RESOURCE_ACTIONS,
            "inventory_token_change": inventory_change,
            "collected_inventory": action == "collecter" and inventory_change == 1,
            "consumed_inventory": action == "manger" and inventory_change == -1,
            "water_uptake_above_decay": water_uptake,
            "food_uptake_above_decay": food_uptake,
            "positive_water_uptake": water_uptake is not None and water_uptake > 1e-9,
            "positive_food_uptake": food_uptake is not None and food_uptake > 1e-9,
            "eating_integrity_delta": (physical_body[I] - pre_body[I]
                                       if action == "manger" else None),
            "body_after_physics": list(physical_body),
            "body_after_paid_learning": list(world.body),
            "world_position_observer_only": list(world.pos),
            "death_causes": list(dead),
            "paid_decision_work": dict(phases["decision"]["work"]),
            "paid_learning_work": dict(phases["learning"]["work"]),
            "paid_decision_energy":
                phases["decision"]["accounting"]["energy"]["paid"],
            "paid_decision_vigilance":
                phases["decision"]["accounting"]["vigilance"]["paid"],
            "paid_learning_energy":
                phases["learning"]["accounting"]["energy"]["paid"],
            "paid_learning_vigilance":
                phases["learning"]["accounting"]["vigilance"]["paid"],
        })
        self.steps.append(event)

    def report(self):
        actions = Counter(s["action"] for s in self.steps
                          if s["action"] in RESOURCE_ACTIONS)
        return {
            "schema": SCHEMA,
            "status": "EXTERNAL_READ_ONLY_NOT_SCIENTIFIC_VALIDATION",
            "steps": self.steps,
            "summary": {
                "lived_steps": len(self.steps),
                "resource_options_offered": sum(
                    s["resource_options_offered"] for s in self.steps),
                "resource_options_scored": sum(
                    s["resource_options_scored"] for s in self.steps),
                "physical_resource_commands": dict(sorted(actions.items())),
                "physical_resource_contacts": sum(
                    s["physical_resource_contact"] for s in self.steps),
                "collected_inventory": sum(
                    s["collected_inventory"] for s in self.steps),
                "consumed_inventory": sum(
                    s["consumed_inventory"] for s in self.steps),
                "positive_water_uptakes": sum(
                    s["positive_water_uptake"] for s in self.steps),
                "positive_food_uptakes": sum(
                    s["positive_food_uptake"] for s in self.steps),
                "new_personally_mapped_cells": sum(
                    s["new_personally_mapped_cells"] for s in self.steps),
            },
        }
