"""Independent read-only GA-03..07 first-person agency receipt auditor.

Only public canonical events. This validates coherence of subjective beliefs,
not actual physical causation. No I0 module, WorldBody, Oracle or Bench imports.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Mapping

from .determinism import canonical_causal_bytes, deterministic_id, sha256_hex
from .independent_journal_audit import audit_export_bytes
from .stage12_goal_progress_audit import audit_stage12_goal_progress

_SCHEMA = "stage12-first-person-goal-agency-v1"
_SPATIAL_SCHEMA = "stage12-first-person-goal-spatial-agency-v1"
_SPATIAL_GOAL = "stage12-lived-goal-spatial-progress-v1"
_DIRECTIONS = {"north": (0,-1), "south": (0,1), "east": (1,0), "west": (-1,0)}
_CAPTURE = "stage12-first-person-cue-v1"


@dataclass(frozen=True, slots=True)
class Stage12FirstPersonAgencyAudit:
    head_hash: str
    occurrences: int
    precommits: int
    judgements_self: int
    judgements_world: int
    judgements_unknown: int
    unavailable: int
    pending_terminal: int
    charged_uc: int
    refused_uc: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-first-person-independent-technical-audit-v1",
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "attribution_pairs_admitted": 0,
            "physical_causation_proven": False,
            "stage12_detector_calibration_proven": False,
        }


def _capture_inventory(event: dict) -> Mapping[str, int]:
    data = event.get("data")
    if (event.get("emitter") != "stage3-runtime"
            or not isinstance(data, dict)
            or data.get("agency_capture_schema") != _CAPTURE
            or type(data.get("capture_t_monde")) is not int
            or event.get("t_monde") != data["capture_t_monde"]
            or not isinstance(data.get("position"), dict)
            or type(data["position"].get("x")) is not int
            or type(data["position"].get("y")) is not int
            or type(data.get("agency_visible_inventory")) is not dict):
        raise ValueError("first-person assessment lacks independently recorded perception")
    inv = data["agency_visible_inventory"]
    if any(type(k) is not str or not k
           or type(v) is not int or v < 0 for k, v in inv.items()):
        raise ValueError("invalid first-person inventory sensory witness")
    return inv


def audit_stage12_first_person_agency(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12FirstPersonAgencyAudit:
    anchor = dict(expected_head=expected_head, expected_count=expected_count)
    base = audit_export_bytes(content, **anchor)
    # Guarantees frozen goal criterion, admitted voluntary goal motive and
    # executed command are not merely matching rehashed but unbound strings.
    goal = audit_stage12_goal_progress(content, **anchor)
    if base.head_hash != goal.head_hash:
        raise ValueError("goal-agency auditor mismatched custody")
    rows = [json.loads(r) for r in content.split(b"\n")]
    captures: dict[tuple[int, str], list[tuple[int, dict]]] = {}
    goals: dict[str, tuple[int, dict, dict]] = {}
    commands: dict[tuple[int, str], list[tuple[int, dict]]] = {}
    transitions: dict[tuple[int, str], list[tuple[int, dict]]] = {}
    charges: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    spatial_charges: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    for i, row in enumerate(rows):
        e = row["causal_event"]
        kind = e.get("kind")
        t, attempt, cycle = e.get("t_monde"), e.get("attempt_ref"), e.get("cycle")
        if kind == "perceptual_capture" and isinstance(attempt, str):
            captures.setdefault((t, attempt), []).append((i, e))
        elif kind == "stage12_goal_progress_preregistered":
            goals[row["event_id"]] = (i, e.get("data"), e)
        elif kind == "command_experienced":
            commands.setdefault((t, attempt), []).append((i, e))
        elif kind == "world_transition_experienced":
            transitions.setdefault((t, attempt), []).append((i, e))
        elif (kind == "compute_charge" and isinstance(e.get("data"), dict)
              and e["data"].get("operation") == "goal_agency_assessment"):
            charges.setdefault((t, attempt, cycle), []).append((i, e["data"]))
        elif (kind == "compute_charge" and isinstance(e.get("data"), dict)
              and e["data"].get("operation") == "goal_agency_spatial_assessment"):
            spatial_charges.setdefault((t, attempt, cycle), []).append(
                (i, e["data"])
            )
    commitments: dict[str, tuple[int, dict, dict]] = {}
    used: set[str] = set()
    seen_steps: set[int] = set()
    counts = {"self": 0, "world": 0, "unknown": 0, "unavailable": 0}
    consumed_uc = refused_uc = 0
    for i, row in enumerate(rows):
        event = row["causal_event"]
        kind = event.get("kind")
        if kind not in ("stage12_goal_agency_precommitted",
                        "stage12_goal_agency_judgement"):
            continue
        data = event.get("data")
        t, attempt, cycle = (
            event.get("t_monde"), event.get("attempt_ref"), event.get("cycle"),
        )
        if (event.get("emitter") != "stage4-runtime"
                or type(data) is not dict or type(t) is not int or t < 1
                or type(attempt) is not str or not attempt
                or type(cycle) is not int or cycle < 1
                or data.get("policy_version") not in (_SCHEMA, _SPATIAL_SCHEMA)):
            raise ValueError("uncontracted GA cognitive receipt")
        ref = data.get("assessment_ref")
        if type(ref) is not str or not ref:
            raise ValueError("first-person assessment needs unique reference")
        if kind == "stage12_goal_agency_precommitted":
            if ref in commitments or t in seen_steps:
                raise ValueError("duplicate goal agency precommit")
            if (data.get("sent_world_step") != t
                    or data.get("observe_world_step") != t + 1
                    or data.get("intent_ref") not in goals
                    or data.get("mechanism") not in (
                        "ingested_from_inventory", "unresolved",
                        "witnessed_goal_spatial_target_v1",
                    )
                    or type(data.get("life_id")) is not str
                    or not data["life_id"]
                    or type(data.get("command_hash")) is not str):
                raise ValueError("invalid GA precommit goal or life provenance")
            index_goal, goal_data, goal_event = goals[data["intent_ref"]]
            if (index_goal >= i or not isinstance(goal_data, dict)
                    or goal_event.get("t_monde") != t
                    or goal_event.get("attempt_ref") != attempt
                    or goal_data.get("goal_ref") != data.get("goal_ref")
                    or goal_data.get("option_ref") != data.get("option_ref")
                    or goal_data.get("measure") != data.get("goal_measure")
                    or goal_data.get("command_hash") != data.get("command_hash")):
                raise ValueError("GA commitment not independently anchored to goal")
            before = captures.get((t, attempt), [])
            if len(before) != 1 or before[0][0] >= i:
                raise ValueError("GA assessment lacks single earlier capture")
            inv = _capture_inventory(before[0][1])
            position = before[0][1]["data"]["position"]
            if (data.get("start_position") != [position["x"], position["y"]]
                    or type(data.get("action_primitive")) is not str
                    or not data["action_primitive"]):
                raise ValueError("GA assessment pre-action cues mismatch")
            target = data.get("action_target")
            if data["mechanism"] == "witnessed_goal_spatial_target_v1":
                if (data["policy_version"] != _SPATIAL_SCHEMA
                        or goal_data.get("contract_version") != _SPATIAL_GOAL
                        or data.get("goal_measure") != "spatial_distance"
                        or data.get("action_primitive") != "se_deplacer"
                        or data.get("action_target") is not None
                        or data.get("inventory_before") is not None
                        or data.get("spatial_direction") not in _DIRECTIONS
                        or data.get("spatial_target_kind") not in (
                            "water", "berry_a", "berry_b"
                        )
                        or any(type(data.get(k)) is not int for k in (
                            "spatial_target_x", "spatial_target_y",
                        ))
                        or type(data.get("spatial_prepassable")) is not bool):
                    raise ValueError("spatial first-person cue lacks matching goal")
                direction = data["spatial_direction"]
                dx, dy = _DIRECTIONS[direction]
                target_xy = (data["spatial_target_x"], data["spatial_target_y"])
                if (target_xy != (position["x"]+dx, position["y"]+dy)
                        or target_xy != (
                            goal_data.get("target_x"), goal_data.get("target_y")
                        )
                        or direction != goal_data.get("direction")):
                    raise ValueError("spatial agency disagrees with frozen target")
                cells = before[0][1].get("data", {}).get("agency_visible_adjacent")
                if not isinstance(cells, list):
                    raise ValueError("spatial agency lacks real visible adjacency")
                matches = [c for c in cells if (
                    isinstance(c, dict)
                    and c.get("direction") == direction
                    and (c.get("x"), c.get("y")) == target_xy
                )]
                if len(matches) != 1 or (
                    matches[0].get("passable")
                    is not data["spatial_prepassable"]
                ):
                    raise ValueError("spatial agency original passability is forged")
                observed = matches[0]
                relevant = (
                    observed.get("water_source") is True
                    if data["spatial_target_kind"] == "water"
                    else data["spatial_target_kind"] in observed.get("resources", ())
                )
                if not relevant:
                    raise ValueError("spatial agency cue not relevant to goal target")
            elif data["mechanism"] == "ingested_from_inventory":
                if (data["goal_measure"] != "food"
                        or data["action_primitive"] != "manger"
                        or target not in ("berry_a", "berry_b")
                        or type(inv.get(target)) is not int
                        or inv[target] < 1
                        or data.get("inventory_before") != inv[target]):
                    raise ValueError("GA self mechanism was not genuinely available")
            else:
                if data.get("inventory_before") is not None:
                    raise ValueError("unresolved GA cannot claim inventory evidence")
            cmd = commands.get((t, attempt), [])
            trans = transitions.get((t, attempt), [])
            if (data["mechanism"] == "witnessed_goal_spatial_target_v1"
                    and cmd and cmd[0][1].get("parameters", {}).get("direction")
                    != data["spatial_direction"]):
                raise ValueError("spatial subjective efference differs from real command")
            if (len(cmd) != 1 or len(trans) != 1
                    or not i < cmd[0][0] < trans[0][0]
                    or cmd[0][1].get("emitter") != "action_control"
                    or cmd[0][1].get("command_hash") != data["command_hash"]
                    or cmd[0][1].get("primitive") != data["action_primitive"]
                    or cmd[0][1].get("parameters", {}).get("target") != target):
                raise ValueError("GA commitment not bound to executed physical command")
            canonical_hash = sha256_hex(canonical_causal_bytes({
                "primitive": cmd[0][1]["primitive"],
                "parameters": cmd[0][1]["parameters"],
            }))
            if data["command_hash"] != canonical_hash:
                raise ValueError("GA commitment command digest inconsistent")
            commitments[ref] = (i, data, event)
            seen_steps.add(t)
        else:
            if ref not in commitments or ref in used:
                raise ValueError("missing or duplicate first-person assessment source")
            initial_index, committed, event0 = commitments[ref]
            if (initial_index >= i or data.get("intent_ref") != committed["intent_ref"]
                    or data.get("life_id") != committed["life_id"]
                    or data.get("sent_world_step") != committed["sent_world_step"]
                    or data.get("observed_world_step") != t
                    or t <= committed["sent_world_step"]
                    or data.get("subjective_agency") not in counts):
                raise ValueError("first-person GA judgement provenance mismatch")
            receipts = charges.get((t, attempt, cycle), [])
            if len(receipts) != 1 or receipts[0][0] >= i:
                raise ValueError("GA judgement lacks its independent UC charge")
            charge = receipts[0][1]
            if (charge.get("module") != "action_control"
                    or type(charge.get("requested_uc")) is not int
                    or charge["requested_uc"] < 1
                    or type(charge.get("accepted")) is not bool):
                raise ValueError("incorrectly charged first-person cognition")
            agency = data["subjective_agency"]
            spatial = committed["mechanism"] == "witnessed_goal_spatial_target_v1"
            spatial_paid = True
            if spatial:
                extra = spatial_charges.get((t, attempt, cycle), [])
                if (len(extra) != 1 or extra[0][0] >= i
                        or extra[0][1].get("module") != "action_control"
                        or type(extra[0][1].get("requested_uc")) is not int
                        or extra[0][1]["requested_uc"] < 1
                        or type(extra[0][1].get("accepted")) is not bool):
                    raise ValueError("spatial first-person calculation lacks own UC")
                spatial_paid = extra[0][1]["accepted"]
                if spatial_paid:
                    consumed_uc += extra[0][1]["requested_uc"]
                else:
                    refused_uc += extra[0][1]["requested_uc"]
            if agency == "unavailable":
                if (charge["accepted"] and spatial_paid
                        and t == committed["observe_world_step"]):
                    raise ValueError("paid on-time judgement falsely unavailable")
                if data.get("cue_ref") is not None:
                    raise ValueError("unavailable cognition claimed sensory evidence")
                if not charge["accepted"]:
                    refused_uc += charge["requested_uc"]
            else:
                if not charge["accepted"] or not spatial_paid or t != committed["observe_world_step"]:
                    raise ValueError("unpaid or late subjective agency label")
                post = captures.get((t, attempt), [])
                if len(post) != 1 or post[0][0] >= i:
                    raise ValueError("GA judgment lacks same-step legal perception")
                inv = _capture_inventory(post[0][1])
                p = post[0][1]["data"]["position"]
                expected_cue = deterministic_id(
                    "stage12-authorized-capture-cue-v1",
                    t, p["x"], p["y"], tuple(sorted(inv.items())),
                )
                if data.get("cue_ref") != expected_cue:
                    raise ValueError("GA observed sensory cue reference mismatch")
                target = committed["action_target"]
                self_supported = (
                    committed["mechanism"] == "ingested_from_inventory"
                    and type(inv.get(target)) is int
                    and inv[target] == committed["inventory_before"] - 1
                    and [p["x"], p["y"]] == committed["start_position"]
                )
                if spatial:
                    direct = committed["spatial_direction"]
                    dx, dy = _DIRECTIONS[direct]
                    before_position = committed["start_position"]
                    expected = [before_position[0]+dx, before_position[1]+dy]
                    blocked = (committed["spatial_prepassable"] is False
                               and [p["x"], p["y"]] == before_position)
                    moved = (committed["spatial_prepassable"] is True
                             and [p["x"], p["y"]] == expected)
                    correct_agency, correct_reason = (
                        ("world", "witnessed_goal_relevant_blocked_direction")
                        if blocked else
                        ("self", "witnessed_goal_relevant_efferent_displacement")
                        if moved else
                        ("unknown", "ambiguous_spatial_displacement_cue")
                    )
                    if (agency != correct_agency
                            or data.get("reason") != correct_reason):
                        raise ValueError("spatial self/world judgement contradicts original cues")
                elif self_supported:
                    if (agency != "self"
                            or data.get("reason") !=
                               "witnessed_goal_relevant_inventory_decrement"):
                        raise ValueError("GA agent self judgement not supported by cues")
                elif (agency != "unknown" or data.get("reason") not in (
                    "no_distinct_goal_relevant_agency_cue",
                    "ingestion_cue_absent_or_confounded",
                )):
                    raise ValueError("GA judgement forged external or personal blame")
                consumed_uc += charge["requested_uc"]
            counts[agency] += 1
            used.add(ref)
    # Any prior nonterminal, paid-eligible preregistration must close. A
    # terminal physical action can remain pending with no postmortem judgement.
    unresolved = 0
    closed_steps = base.world_steps_closed
    for ref, (_, commitment, _) in commitments.items():
        if ref in used:
            continue
        if closed_steps > commitment["sent_world_step"]:
            raise ValueError("missing GA judgement after new physical step")
        unresolved += 1
    if (sum(len(items) for items in spatial_charges.values())
            != sum(1 for ref in used if (
                commitments[ref][1]["mechanism"] ==
                "witnessed_goal_spatial_target_v1"
            ))):
        raise ValueError("orphaned or repeated spatial cognition charge")
    if sum(len(items) for items in charges.values()) != len(used):
        raise ValueError("orphaned or duplicate GA UC debit")
    return Stage12FirstPersonAgencyAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        precommits=len(commitments), judgements_self=counts["self"],
        judgements_world=counts["world"], judgements_unknown=counts["unknown"],
        unavailable=counts["unavailable"], pending_terminal=unresolved,
        charged_uc=consumed_uc, refused_uc=refused_uc,
    )
