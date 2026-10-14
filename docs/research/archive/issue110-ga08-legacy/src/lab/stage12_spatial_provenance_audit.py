"""Independent GA-08 semantic auditor over immutable public causal receipts.

Does not import I0, oracle, simulator or WorldBody. A correctly rehashed
journal can still be semantically false and must be rejected. Technical
consistency is not an independent physical-causation ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import json

from .determinism import canonical_causal_bytes, deterministic_id, sha256_hex
from .independent_journal_audit import audit_export_bytes

SPATIAL = "stage12-spatial-subcriterion-ga08-v1"
CAPTURE = "stage12-ga08-local-adjacent-v1"
DIRECTIONS = {"north": (0, -1), "south": (0, 1),
              "east": (1, 0), "west": (-1, 0)}


@dataclass(frozen=True, slots=True)
class Stage12SpatialProvenanceAudit:
    head_hash: str
    occurrences: int
    preregistered: int
    verified_successes: int
    verified_failures: int
    unknown_outcomes: int
    judgements_self: int
    judgements_world: int
    judgements_unknown: int
    agency_unavailable: int
    charged_agency_uc: int
    refused_agency_uc: int
    pending_at_terminal: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-spatial-provenance-audit-v1",
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "subjective_causality_not_physical_truth": True,
        }


def _value(v):
    if type(v) is dict and set(v) == {"$f64"} and type(v["$f64"]) is str:
        try:
            n = float.fromhex(v["$f64"])
        except (ValueError, OverflowError):
            return None
        return n if n.hex() == v["$f64"] and isfinite(n) else None
    return float(v) if type(v) in (float, int) and isfinite(v) else None


def _position(v):
    if (type(v) is dict and set(v) == {"x", "y"}
            and all(type(v[k]) is int for k in ("x", "y"))):
        return (v["x"], v["y"])
    return None


def _coords(v):
    if type(v) is list and len(v) == 2 and all(type(x) is int for x in v):
        return tuple(v)
    return None


def _capture_adjacent(event):
    d = event.get("data")
    if (event.get("emitter") != "stage3-runtime" or type(d) is not dict
            or d.get("spatial_capture_version") != CAPTURE
            or d.get("capture_t_monde") != event.get("t_monde")
            or _position(d.get("position")) is None
            or type(d.get("agency_visible_adjacent")) is not list
            or len(d["agency_visible_adjacent"]) != 4):
        raise ValueError("GA08 lacks unique authenticated local perception receipt")
    cells = d["agency_visible_adjacent"]
    seen = set()
    for c in cells:
        if (type(c) is not dict
                or set(c) != {"direction", "x", "y", "passable",
                              "water_source", "resources"}
                or c["direction"] not in DIRECTIONS
                or c["direction"] in seen
                or type(c["x"]) is not int or type(c["y"]) is not int
                or type(c["passable"]) is not bool
                or type(c["water_source"]) is not bool
                or type(c["resources"]) is not list
                or any(type(k) is not str for k in c["resources"])):
            raise ValueError("GA08 forged or duplicate adjacent spatial cell")
        seen.add(c["direction"])
        ox, oy = _position(d["position"])
        dx, dy = DIRECTIONS[c["direction"]]
        if (c["x"], c["y"]) != (ox + dx, oy + dy):
            raise ValueError("GA08 cell position contradicts captured locality")
    if seen != set(DIRECTIONS):
        raise ValueError("GA08 source omitted visible directions")
    return cells


def audit_stage12_spatial_provenance(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12SpatialProvenanceAudit:
    base = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count,
    )
    rows = [json.loads(b) for b in content.split(b"\n")]
    events = [row["causal_event"] for row in rows]
    def origin(e):
        return (e.get("t_monde"), e.get("attempt_ref"))
    def unique(records, key, name):
        values = records.get(key, [])
        if len(values) != 1:
            raise ValueError("GA08 expected unique " + name)
        return values[0]
    def index_by_kind(kind):
        out = {}
        for i, e in enumerate(events):
            if e.get("kind") == kind:
                out.setdefault(origin(e), []).append((i, e))
        return out

    captures = index_by_kind("perceptual_capture")
    commands = index_by_kind("command_experienced")
    transitions = index_by_kind("world_transition_experienced")
    motives = index_by_kind("stage12_action_motive_attested")
    samples = index_by_kind("stage12_lived_diagnostics_published")
    delayed = index_by_kind("stage12_lived_diagnostics_deferred")
    agency_charges = {}
    diagnostic_charges = {}
    for i, e in enumerate(events):
        if e.get("kind") != "compute_charge" or type(e.get("data")) is not dict:
            continue
        op = e["data"].get("operation")
        if op == "goal_agency_assessment":
            agency_charges.setdefault((*origin(e), e.get("cycle")), []).append((i, e["data"]))
        if op == "stage12_diagnostic_sample":
            diagnostic_charges.setdefault((*origin(e), e.get("cycle")), []).append((i, e["data"]))
    intents = {}
    commits = {}
    followups = {}
    judgements = {}
    for i, (row, e) in enumerate(zip(rows, events)):
        d = e.get("data")
        if type(d) is not dict:
            continue
        if e.get("kind") == "stage12_goal_progress_preregistered" and d.get("contract_version") == SPATIAL:
            intents[row["event_id"]] = (i, e, d)
        elif e.get("kind") == "stage12_goal_progress_followup" and d.get("contract_version") == SPATIAL:
            followups.setdefault(d.get("intent_ref"), []).append((i, e, d))
        elif e.get("kind") == "stage12_goal_agency_precommitted" and d.get("policy_version") == SPATIAL:
            commits.setdefault(d.get("intent_ref"), []).append((i, e, d))
        elif e.get("kind") == "stage12_goal_agency_judgement" and d.get("policy_version") == SPATIAL:
            judgements.setdefault(d.get("intent_ref"), []).append((i, e, d))
    if not intents and (commits or followups or judgements):
        raise ValueError("GA08 provenance without original spatial intention")
    if any(k not in intents for groups in (commits, followups, judgements) for k in groups):
        raise ValueError("GA08 orphaned first-person or progress receipt")
    seen_world = set()
    seen_assessment = set()
    found = {"success": 0, "failure": 0, "unknown": 0}
    beliefs = {"self": 0, "world": 0, "unknown": 0, "unavailable": 0}
    charged = refused = terminal = 0
    for intent_ref, (i, pre_event, d) in intents.items():
        t, attempt = origin(pre_event)
        cycle = pre_event.get("cycle")
        if (pre_event.get("emitter") != "stage4-runtime"
                or type(t) is not int or t < 1
                or type(attempt) is not str or not attempt
                or type(cycle) is not int or cycle < 1
                or t in seen_world
                or set(d) != {
                    "contract_version", "life_id", "goal_ref", "option_ref",
                    "command_hash", "measure", "value_before",
                    "sent_world_step", "observe_world_step",
                    "origin", "target", "direction", "target_kind",
                    "distance_before", "destination_passable_before",
                }
                or any(type(d.get(k)) is not str or not d[k]
                       for k in ("life_id", "goal_ref", "option_ref", "command_hash"))
                or d.get("measure") != "spatial_distance"
                or _value(d.get("value_before")) != 1.0
                or d.get("distance_before") != 1
                or d.get("sent_world_step") != t
                or d.get("observe_world_step") != t + 1
                or d.get("direction") not in DIRECTIONS
                or d.get("target_kind") not in ("food", "water")
                or type(d.get("destination_passable_before")) is not bool):
            raise ValueError("GA08 invalid pre-action spatial criterion")
        seen_world.add(t)
        ori, target = _coords(d["origin"]), _coords(d["target"])
        if ori is None or target is None:
            raise ValueError("GA08 spatial origin/target not canonical")
        dx, dy = DIRECTIONS[d["direction"]]
        if (ori[0] + dx, ori[1] + dy) != target:
            raise ValueError("GA08 command does not point at witnessed goal")
        pre_capture_i, pre_capture = unique(captures, (t, attempt), "pre-action perception")
        if pre_capture_i >= i or _position(pre_capture.get("data", {}).get("position")) != ori:
            raise ValueError("GA08 pre-action perception contradicts frozen origin")
        cells = _capture_adjacent(pre_capture)
        selected = [c for c in cells if c["direction"] == d["direction"]]
        if len(selected) != 1:
            raise ValueError("GA08 missing exact attempted destination")
        cell = selected[0]
        if ((cell["x"], cell["y"]) != target
                or cell["passable"] != d["destination_passable_before"]
                or ((cell["water_source"] if d["target_kind"] == "water" else
                     any(k in ("berry_a", "berry_b") for k in cell["resources"])) is not True)):
            raise ValueError("GA08 obstacle or resource target not originally perceived")
        motive = [
            (mi, me.get("data")) for mi, me in motives.get((t, attempt), [])
            if me.get("cycle") == cycle
        ]
        if not any(mi < i and type(md) is dict
                   and md.get("motive_type") == "active_goal"
                   and md.get("goal_ref") == d["goal_ref"]
                   and md.get("active_goal_ref") == d["goal_ref"]
                   and md.get("option_ref") == d["option_ref"]
                   and md.get("command_hash") == d["command_hash"]
                   for mi, md in motive):
            raise ValueError("GA08 is not authentically goal-directed")
        ci, command = unique(commands, (t, attempt), "applied Action Control command")
        ti, transition = unique(transitions, (t, attempt), "physical WorldBody transition")
        if (not i < ci < ti
                or command.get("emitter") != "action_control"
                or command.get("primitive") != "se_deplacer"
                or command.get("parameters") != {"direction": d["direction"]}
                or command.get("command_hash") != d["command_hash"]
                or d["command_hash"] != sha256_hex(canonical_causal_bytes({
                    "primitive": "se_deplacer", "parameters": {"direction": d["direction"]},
                }))
                # Canonical WorldBody transition exports position_after,
                # not a pre-state. The independently captured pre-action
                # position above is the authenticated physical-step baseline.
                or origin(transition) != (t, attempt)):
            raise ValueError("GA08 precommit not bound to a truly dispatched movement")
        receipts = diagnostic_charges.get((t, attempt, cycle), [])
        if (len(receipts) != 1 or not receipts[0][0] < i
                or receipts[0][1].get("module") != "metacognition_health"
                or receipts[0][1].get("accepted") is not True
                or type(receipts[0][1].get("requested_uc")) is not int
                or receipts[0][1]["requested_uc"] < 2
                or not any(si < i for si, _ in samples.get((t, attempt), []))):
            raise ValueError("GA08 spatial preregistration work was not paid")
        claims = commits.get(intent_ref, [])
        if len(claims) != 1:
            raise ValueError("GA08 goal needs one distinct Action Control precommit")
        ai, ae, ad = claims[0]
        if (ae.get("emitter") != "stage4-runtime"
                or origin(ae) != (t, attempt)
                or ae.get("cycle") != cycle
                or not i < ai < ci
                or ad.get("policy_version") != SPATIAL
                or ad.get("intent_ref") != intent_ref
                or ad.get("life_id") != d["life_id"]
                or ad.get("goal_ref") != d["goal_ref"]
                or ad.get("option_ref") != d["option_ref"]
                or ad.get("command_hash") != d["command_hash"]
                or ad.get("sent_world_step") != t
                or ad.get("origin") != d["origin"]
                or ad.get("target") != d["target"]
                or ad.get("direction") != d["direction"]
                or ad.get("target_kind") != d["target_kind"]
                or ad.get("distance_before") != 1
                or ad.get("destination_passable_before") != d["destination_passable_before"]
                or type(ad.get("assessment_ref")) is not str
                or not ad["assessment_ref"]
                or ad["assessment_ref"] in seen_assessment):
            raise ValueError("GA08 first-person intent not independent or incorrectly bound")
        seen_assessment.add(ad["assessment_ref"])
        # The independent owner receipts, not the detector, establish each
        # source; neither owner gets the other's classification.
        fs = followups.get(intent_ref, [])
        js = judgements.get(intent_ref, [])
        if len(fs) > 1 or len(js) > 1:
            raise ValueError("GA08 duplicated goal closure or subjective judgement")
        if not fs or not js:
            later_diag = [
                e for e in events if e.get("t_monde", 0) > t
                and e.get("kind") in (
                    "stage12_lived_diagnostics_published",
                    "stage12_lived_diagnostics_deferred",
                )
            ]
            if later_diag:
                raise ValueError("GA08 pending evidence remained after waking diagnostic")
            terminal += 1
            continue
        fi, follow_event, follow = fs[0]
        ji, judge_event, judge = js[0]
        ft, fa = origin(follow_event)
        jt, ja = origin(judge_event)
        if (follow_event.get("emitter") != "stage4-runtime"
                or judge_event.get("emitter") != "stage4-runtime"
                or not i < ji < fi
                or fi <= ti
                or ft != jt or fa != ja
                or ft <= t
                or follow.get("intent_ref") != intent_ref
                or follow.get("sent_world_step") != t
                or follow.get("observed_world_step") != ft
                or follow.get("measure") != "spatial_distance"
                or _value(follow.get("value_before")) != 1.0
                or judge.get("assessment_ref") != ad["assessment_ref"]
                or judge.get("life_id") != d["life_id"]
                or judge.get("sent_world_step") != t
                or judge.get("observed_world_step") != jt):
            raise ValueError("GA08 second-phase followup/judgement mismatch")
        aci, _ = unique(captures, (ft, fa), "new lived post-command capture")
        if aci >= ji:
            raise ValueError("GA08 judgement was not based on live perception")
        after_event = unique(captures, (ft, fa), "post-step capture")[1]
        post = _position(after_event.get("data", {}).get("position"))
        if post is None:
            raise ValueError("GA08 invalid post-action position")
        _capture_adjacent(after_event)
        expected_cue = deterministic_id(
            "stage12-ga08-perception-cue-v1", ft, post[0], post[1],
            tuple(
                (c["direction"], c["x"], c["y"], c["passable"],
                 c["water_source"], tuple(c["resources"]))
                for c in after_event["data"]["agency_visible_adjacent"]
            ),
        )
        charge_rows = agency_charges.get((jt, ja, judge_event.get("cycle")), [])
        if (len(charge_rows) != 1 or charge_rows[0][0] >= ji
                or charge_rows[0][1].get("module") != "action_control"
                or type(charge_rows[0][1].get("requested_uc")) is not int
                or charge_rows[0][1]["requested_uc"] < 1
                or type(charge_rows[0][1].get("accepted")) is not bool):
            raise ValueError("GA08 subjective judgement not independently charged")
        debit = charge_rows[0][1]
        if (not debit["accepted"] or jt != t + 1):
            expected_agency = "unavailable"
            expected_reason = ("agency_uc_refused" if not debit["accepted"]
                               else "agency_observation_missed")
            expected_ref = None
            if not debit["accepted"]:
                refused += debit["requested_uc"]
        else:
            expected_ref = expected_cue
            if d["destination_passable_before"] and post == target:
                expected_agency = "self"
                expected_reason = "witnessed_goal_relevant_efferent_displacement"
            elif not d["destination_passable_before"] and post == ori:
                expected_agency = "world"
                expected_reason = "witnessed_goal_relevant_blocked_destination"
            else:
                expected_agency = "unknown"
                expected_reason = "ambiguous_or_confounded_spatial_cue"
            charged += debit["requested_uc"]
        if (judge.get("subjective_agency") != expected_agency
                or judge.get("reason") != expected_reason
                or judge.get("cue_ref") != expected_ref):
            raise ValueError("GA08 forged self/world blame or unavailable evidence")
        beliefs[expected_agency] += 1
        # The Metacognition followup cannot read Action Control's verdict.
        # Verify its independent spatial distance and unchanged due window.
        diags = samples.get((ft, fa), [])
        deferred = delayed.get((ft, fa), [])
        if (len(diags) + len(deferred) != 1
                or (diags + deferred)[0][0] >= fi):
            raise ValueError("GA08 followup lacks canonical diagnostic UC receipt")
        if deferred or ft != t + 1:
            expected_outcome = "unknown"
            expected_reason = "unavailable_or_late_observation"
            distance = None
        else:
            distance = abs(post[0] - target[0]) + abs(post[1] - target[1])
            expected_outcome = "success" if distance < 1 else "failure"
            expected_reason = ("strict_perceptual_distance_decrease"
                               if distance < 1 else "no_strict_perceptual_distance_decrease")
            if _position(transition.get("position_after")) != post:
                raise ValueError("GA08 outcome contradicts recorded physical consequence")
        if (follow.get("criterion_outcome") != expected_outcome
                or follow.get("reason") != expected_reason
                or (None if distance is None else float(distance))
                   != _value(follow.get("value_after"))):
            raise ValueError("GA08 goal result contradicts independent distance evidence")
        found[expected_outcome] += 1
    return Stage12SpatialProvenanceAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        preregistered=len(intents), verified_successes=found["success"],
        verified_failures=found["failure"], unknown_outcomes=found["unknown"],
        judgements_self=beliefs["self"], judgements_world=beliefs["world"],
        judgements_unknown=beliefs["unknown"],
        agency_unavailable=beliefs["unavailable"],
        charged_agency_uc=charged, refused_agency_uc=refused,
        pending_at_terminal=terminal,
    )
