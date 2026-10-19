#!/usr/bin/env python3
"""Read-only #317 analysis: contact, co-location, and later memory learning.

An independently authenticated WAL is required. Contact co-location is NOT
entity causality; a later learned Q evaluation is NOT proof of an affordance.
Never mutate an individual's memory, physics or WAL.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from audit_i1_spatial_navigation_314 import audit as verify_wal, _position


def _number(value):
    if type(value) in (int, float):
        v = float(value)
    elif isinstance(value, dict) and set(value) == {"$f64"}:
        v = float.fromhex(value["$f64"])
    else:
        raise ValueError("missing or invalid witnessed body number")
    from math import isfinite
    if not isfinite(v):
        raise ValueError("nonfinite witnessed number")
    return v


def classify(events):
    """Synthetic-safe classifier; only audit() authenticates physical evidence."""
    attempts = defaultdict(list)
    evaluations = defaultdict(list)
    updates = defaultdict(list)
    for i, e in enumerate(events):
        t, attempt = e.get("t_monde"), e.get("attempt_ref")
        if type(t) is int and isinstance(attempt, str):
            attempts[(t, attempt)].append((i, e))
        if e.get("kind") == "stage8_option_evaluation":
            d = e.get("data")
            if (type(t) is int and isinstance(d, dict)
                and isinstance(d.get("learning_signature"), str)
                and d["learning_signature"].startswith("memory_place_return:")
                and d.get("learned_value_status") == "learned"
                and d.get("learned_value") is not None):
                evaluations[d["learning_signature"]].append((t, i))
        if e.get("kind") == "td_update_published":
            d = e.get("data")
            if type(t) is int and isinstance(d, dict):
                signed = d.get("updated_signatures")
                if isinstance(signed, list):
                    for signature in signed:
                        if isinstance(signature, str):
                            updates[signature].append((t, i))
    totals = Counter()
    examples = []
    for (t, attempt), rows in sorted(attempts.items()):
        kinds = defaultdict(list)
        for i, e in rows:
            kinds[e.get("kind")].append((i, e))
        if not kinds["command_experienced"]:
            continue
        command = kinds["command_experienced"]
        if len(command) != 1 or command[0][1].get("primitive") not in {
            "boire", "manger", "collecter"
        }:
            continue
        totals["possible_contact_commands"] += 1
        required = ("perceptual_capture", "command_admitted",
                    "world_transition_experienced", "step_closed")
        if any(len(kinds[k]) != 1 for k in required):
            totals["unverifiable_contacts"] += 1
            continue
        cap_idx, cap = kinds["perceptual_capture"][0]
        adm_idx, adm = kinds["command_admitted"][0]
        cmd_idx, cmd = command[0]
        tr_idx, transition = kinds["world_transition_experienced"][0]
        close_idx, closure = kinds["step_closed"][0]
        admission = adm.get("data", {})
        closing = closure.get("data", {})
        if (not cap_idx < adm_idx < cmd_idx < tr_idx < close_idx
            or not isinstance(admission, dict)
            or admission.get("command_hash") != cmd.get("command_hash")
            or admission.get("primitive") != cmd.get("primitive")
            or not isinstance(closing, dict)
            or closing.get("outcome") != "normal"
            or closing.get("world_advance_count") != 1
            or closing.get("applied_command_count") != 1):
            totals["unverifiable_contacts"] += 1
            continue
        position = _position(cap.get("data", {}).get("position"))
        after_position = _position(transition.get("position_after"))
        before = cap.get("data", {}).get("dual_scope_visible_body")
        after = transition.get("body_after")
        if (position is None or position != after_position
            or not isinstance(before, dict) or not isinstance(after, dict)
            or any(k not in before or k not in after
                   for k in ("energy", "food", "water", "integrity"))):
            totals["unverifiable_contacts"] += 1
            continue
        change = {k: _number(after[k]) - _number(before[k])
                  for k in ("energy", "food", "water", "integrity")}
        # A site may contain several visible entities. These are first-person
        # observations, not action beneficiaries. Retain the entity *type*
        # for generic target matching, never an innate nutrition lookup.
        local_types = {}
        for i, row in kinds["i1_entity_place_observed"]:
            data = row.get("data")
            if (i >= cmd_idx or not isinstance(data, dict)
                or data.get("source") != "perceptual_capture"
                or _position(data.get("position")) != position
                or not isinstance(data.get("entity_id"), str)
                or not isinstance(data.get("entity_type"), str)):
                continue
            eid, kind = data["entity_id"], data["entity_type"]
            if eid in local_types and local_types[eid] != kind:
                raise ValueError("contradictory entity type in one physical capture")
            local_types[eid] = kind
        visible = sorted(local_types)
        effects = transition.get("effects")
        if not isinstance(effects, dict):
            totals["unverifiable_contacts"] += 1
            continue
        # A consumption of carried inventory is NOT contact with an entity
        # co-located at the eating position. A successful collection has a
        # directly witnessed resource type, but does not prove it nourishes
        # the body. A drink observes environmental action without a unique
        # entity reference in the physical command. No branch assigns value.
        action_kind = cmd["primitive"]
        direct = []
        association = "colocation_only"
        if action_kind == "manger":
            totals["inventory_mediated_ingestions"] += 1
            association = "carried_inventory_not_site_cause"
        elif action_kind == "boire":
            totals["environmental_drink_without_entity_id"] += 1
            association = "environmental_action_no_entity_id"
        elif action_kind == "collecter":
            collected = effects.get("collected")
            target = cmd.get("parameters", {}).get("target")
            if (isinstance(collected, dict)
                and isinstance(collected.get("kind"), str)
                and collected.get("kind") == target
                and type(collected.get("quantity")) is int
                and collected["quantity"] > 0):
                direct = sorted(
                    eid for eid, kind in local_types.items()
                    if kind == collected["kind"])
            if len(direct) == 1:
                totals["collection_with_unique_witnessed_type"] += 1
                association = "collected_type_witnessed_no_benefit_inference"
            else:
                totals["collection_without_unique_witnessed_type"] += 1
                association = "collected_target_ambiguous_or_unwitnessed"
        totals["physically_certified_contacts"] += 1
        if not visible:
            totals["no_colocated_sighting"] += 1
        elif len(visible) == 1:
            totals["one_colocated_sighting"] += 1
        else:
            totals["multiple_colocated_sightings"] += 1
        later = sorted((step, entity)
                       for entity in visible
                       for step, _ in evaluations.get(
                           "memory_place_return:" + entity, ())
                       if step > t)
        if later:
            totals["contacts_with_later_learned_memory_evaluation"] += 1
        # A later learned Q read may reflect an update which took place
        # BEFORE this contact. A new post-contact TD update still credits an
        # *action* or eligibility trace, not a destination's utility.
        fresh_td = sorted(
            (step, ref) for ref in visible
            for step, _ in updates.get("memory_place_return:" + ref, ())
            if step > t
        )
        prior_td = any(
            step < t for ref in visible
            for step, _ in updates.get("memory_place_return:" + ref, ())
        )
        if fresh_td:
            totals["contacts_followed_by_memory_td_update"] += 1
        if prior_td and later:
            totals["contacts_with_preexisting_memory_td_and_later_read"] += 1
        if direct and any(
            step > t for entity in direct for step, _ in
            evaluations.get("memory_place_return:" + entity, ())
        ):
            totals["witnessed_collection_with_later_learned_memory_evaluation"] += 1
        if change["water"] > 0:
            totals["positive_water_delta"] += 1
        if change["food"] > 0:
            totals["positive_food_delta"] += 1
        if len(examples) < 20:
            examples.append({
                "world_step": t, "primitive": cmd["primitive"],
                "position": list(position), "colocated_entities": visible,
                "physical_effects": effects,
                "observed_body_delta": {k: round(v, 8) for k, v in change.items()},
                "direct_target_witnesses": direct,
                "association_status": association,
                "later_learned_memory_evaluation": bool(later),
                "post_contact_td_action_update": bool(fresh_td),
                "preexisting_td_action_update": prior_td,
                "entity_causal_benefit": "not_established",
            })
    return {
        "schema": "i1-317-physical-contact-association-v3",
        "counters": {key: totals[key] for key in (
            "possible_contact_commands", "unverifiable_contacts",
            "physically_certified_contacts", "no_colocated_sighting",
            "one_colocated_sighting", "multiple_colocated_sightings",
            "contacts_with_later_learned_memory_evaluation",
            "positive_water_delta", "positive_food_delta",
            "inventory_mediated_ingestions",
            "environmental_drink_without_entity_id",
            "collection_with_unique_witnessed_type",
            "collection_without_unique_witnessed_type",
            "witnessed_collection_with_later_learned_memory_evaluation",
            "contacts_followed_by_memory_td_update",
            "contacts_with_preexisting_memory_td_and_later_read")},
        "examples": examples,
        "entity_causal_learning_proven": False,
        "limitation": "Authenticated co-location, physical benefit and later TD "
                      "association do not by themselves prove entity causality.",
    }


def audit(path: Path):
    """Certify and interpret precisely the same immutable evidence bytes.

    An original WAL may be extended or replaced by a running birth. Never
    authenticate one file snapshot and classify a second read of its path.
    The #314 auditor authenticates its own identical sealed snapshot.
    """
    if not path.is_file() or path.is_symlink():
        raise ValueError("WAL must be a regular existing file")
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    with TemporaryDirectory(prefix="i1-317-contact-seal-") as folder:
        sealed = Path(folder) / "sealed-evidence.wal"
        sealed.write_bytes(raw)
        proof = verify_wal(sealed)
    if (proof["independent_hash_chain_verified"] is not True
        or not isinstance(proof.get("journal_head"), str)):
        raise ValueError("unauthenticated WAL")
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    if len(events) != proof["journal_entries"]:
        raise ValueError("authenticated WAL event count mismatch")
    result = classify(events)
    result.update({"journal_head": proof["journal_head"],
                   "journal_entries": proof["journal_entries"],
                   "source_sha256": digest,
                   "independent_hash_chain_verified": True})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.wal)
    data = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError("never overwrite a prior scientific report")
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
