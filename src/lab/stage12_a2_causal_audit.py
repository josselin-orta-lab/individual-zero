"""Read-only A2 temporal and causal-provenance audit (issue #110).

This auditor is NOT part of I0. It validates an external intervention, its
receipt, the actually admitted command, the physical transition and I0's
separately authored lived judgement. Rehashing alone is not a semantic proof.
Never import WorldBody, the I0 cognition, Oracle, or Bench.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .determinism import deterministic_id
from .independent_journal_audit import audit_export_bytes
from .stage12_first_person_agency_audit import audit_stage12_first_person_agency
from .stage12_attribution_pair_audit import audit_stage12_attribution_pairs

_A2_REASON = "witnessed_new_goal_relevant_obstruction_after_commitment"
_OFFSETS = {
    "north": (0, -1), "south": (0, 1),
    "east": (1, 0), "west": (-1, 0),
}


@dataclass(frozen=True, slots=True)
class Stage12A2CausalAudit:
    head_hash: str
    occurrences: int
    admitted_external_obstacle_batches: int
    correctly_ordered_interventions: int
    experienced_blocked_movements: int
    verified_a2_subjective_world_judgements: int
    matching_failure_world_pairs: int
    applied_failure_world_pairs: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-a2-independent-causal-provenance-v1",
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "physical_causation_scope": (
                "logged_intervention_and_world_transition_consistency_only"
            ),
            "oracle_used": False,
            "subjective_judgement_injected": False,
            "scientific_generalization_proven": False,
        }


def _scenario_key(event: dict) -> tuple[str, str, int, int]:
    if (event.get("emitter") != "scenario"
            or type(event.get("scenario_id")) is not str
            or not event["scenario_id"]
            or type(event.get("scenario_version")) is not str
            or not event["scenario_version"]
            or type(event.get("t_monde")) is not int
            or event["t_monde"] < 1
            or type(event.get("sequence")) is not int
            or event["sequence"] < 0):
        raise ValueError("A2 external input lacks scenario source and time")
    return (event["scenario_id"], event["scenario_version"],
            event["t_monde"], event["sequence"])


def audit_stage12_a2_causal_link(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12A2CausalAudit:
    anchors = dict(expected_head=expected_head, expected_count=expected_count)
    base = audit_export_bytes(content, **anchors)
    # These two auditors independently verify that all agency judgements
    # match actual authorized sensory receipts, UC debits and goal outcomes.
    cognitive = audit_stage12_first_person_agency(content, **anchors)
    pairs = audit_stage12_attribution_pairs(content, **anchors)
    if base.head_hash != cognitive.head_hash or base.head_hash != pairs.head_hash:
        raise ValueError("A2 audit did not read the same trusted journal")
    rows = [json.loads(raw) for raw in content.splitlines()]
    events = [row["causal_event"] for row in rows]

    received: dict[tuple[str, str, int, int], tuple[int, dict]] = {}
    applied: dict[tuple[str, str, int, int], int] = {}
    for i, (row, event) in enumerate(zip(rows, events)):
        if event.get("kind") not in (
            "external_input_received", "external_input_applied"
        ) or event.get("phase") != "after_admission":
            continue
        key = _scenario_key(event)
        if event["kind"] == "external_input_received":
            payload = event.get("payload")
            if (event.get("operation") != "set_obstacle"
                    or type(payload) is not dict
                    or set(payload) != {"position", "active"}
                    or payload["active"] is not True
                    or type(payload["position"]) is not dict
                    or set(payload["position"]) != {"x", "y"}
                    or any(type(payload["position"][v]) is not int
                           for v in ("x", "y"))
                    or key in received):
                raise ValueError("duplicate or invalid external A2 obstacle proposal")
            expected = deterministic_id("journal-event-v1", "scenario", *key)
            if row["event_id"] != expected:
                raise ValueError("A2 scenario received event ID mismatch")
            received[key] = (i, payload)
        else:
            if key in applied or row["event_id"] != deterministic_id(
                "journal-event-v1", "scenario", *key, "applied"
            ):
                raise ValueError("A2 applied receipt duplicated or unbound")
            applied[key] = i

    # A forged omitted phase cannot silently turn an A2 receipt into a legacy
    # before-step receipt. Both halves of an after-admission pair must match.
    for i, event in enumerate(events):
        if event.get("kind") not in (
            "external_input_received", "external_input_applied"
        ) or event.get("emitter") != "scenario":
            continue
        key = _scenario_key(event)
        if key in received or key in applied:
            if event.get("phase") != "after_admission":
                raise ValueError("A2 external receipt has contradictory phase")

    commands: dict[int, list[tuple[int, dict]]] = {}
    admissions: dict[int, list[tuple[int, dict]]] = {}
    transitions: dict[int, list[tuple[int, dict]]] = {}
    for i, event in enumerate(events):
        t = event.get("t_monde")
        if type(t) is not int:
            continue
        kind = event.get("kind")
        if kind == "command_experienced":
            commands.setdefault(t, []).append((i, event))
        elif kind == "command_admitted":
            admissions.setdefault(t, []).append((i, event))
        elif kind == "world_transition_experienced":
            transitions.setdefault(t, []).append((i, event))

    ordered_steps: dict[int, tuple[dict, dict, dict]] = {}
    for key, (received_at, payload) in received.items():
        applied_at = applied.get(key)
        if applied_at is None or not received_at < applied_at:
            raise ValueError("A2 external input lacks later applied receipt")
        step = key[2]
        cs = commands.get(step, ())
        ts = transitions.get(step, ())
        if (len(cs) != 1 or len(ts) != 1
                or not cs[0][0] < received_at < applied_at < ts[0][0]):
            raise ValueError("A2 intervention not between real send and transition")
        cmd = cs[0][1]
        trans = ts[0][1]
        if (cmd.get("emitter") != "action_control"
                or cmd.get("attempt_ref") != trans.get("attempt_ref")
                or not any(
                    i < cs[0][0]
                    and a.get("attempt_ref") == cmd.get("attempt_ref")
                    and a.get("data", {}).get("command_hash")
                       == cmd.get("command_hash")
                    for i, a in admissions.get(step, ())
                )):
            raise ValueError("A2 intervention lacks verified Action Control admission")
        if step in ordered_steps:
            raise ValueError("multiple A2 obstacle operations confound one step")
        ordered_steps[step] = (payload, cmd, trans)
    if set(received) != set(applied):
        raise ValueError("A2 applied event has no matching prior proposal")

    commitments: dict[str, tuple[int, dict, dict]] = {}
    for i, event in enumerate(events):
        if event.get("kind") == "stage12_goal_agency_precommitted":
            d = event.get("data")
            if isinstance(d, dict) and type(d.get("assessment_ref")) is str:
                if d["assessment_ref"] in commitments:
                    raise ValueError("duplicated A2 cognitive source")
                commitments[d["assessment_ref"]] = (i, d, event)

    seen: set[str] = set()
    world_count = 0
    blocked_movement_count = 0
    pair_count = 0
    applied_pair_count = 0
    for i, (row, event) in enumerate(zip(rows, events)):
        if (event.get("kind") != "stage12_goal_agency_judgement"
                or not isinstance(event.get("data"), dict)):
            continue
        d = event["data"]
        if d.get("reason") != _A2_REASON:
            continue
        if d.get("subjective_agency") != "world":
            raise ValueError("A2 obstacle reason has non-world classification")
        commitment_ref = d.get("assessment_ref")
        if commitment_ref not in commitments or commitment_ref in seen:
            raise ValueError("A2 judgement lacks unique original commitment")
        seen.add(commitment_ref)
        j, source, e0 = commitments[commitment_ref]
        t = source.get("sent_world_step")
        if (not j < i or type(t) is not int
                or d.get("observed_world_step") != t + 1
                or source.get("spatial_prepassable") is not True
                or source.get("mechanism") != "witnessed_goal_spatial_target_v1"
                or source.get("spatial_direction") not in _OFFSETS
                or t not in ordered_steps):
            raise ValueError("A2 world judgement lacks correct precommit/intervention")
        payload, cmd, transition = ordered_steps[t]
        direction = source["spatial_direction"]
        sx, sy = source.get("start_position", [None, None])
        dx, dy = _OFFSETS[direction]
        expected = {"x": sx + dx, "y": sy + dy}
        if (source.get("spatial_target_x") != expected["x"]
                or source.get("spatial_target_y") != expected["y"]
                or payload["position"] != expected
                or cmd.get("primitive") != "se_deplacer"
                or cmd.get("parameters", {}).get("direction") != direction
                or cmd.get("command_hash") != source.get("command_hash")
                or transition.get("position_after") != {"x": sx, "y": sy}
                or transition.get("effects", {}).get("movement") != "blocked"
                or "scenario_forced_failure" in transition.get("effects", {})):
            raise ValueError("A2 physical transition does not support new obstacle")
        captures = [e for e in events if (
            e.get("kind") == "perceptual_capture"
            and e.get("t_monde") == t + 1
            and e.get("emitter") == "stage3-runtime"
        )]
        if len(captures) != 1:
            raise ValueError("A2 interpretation has no unique later perception")
        cells = captures[0].get("data", {}).get("agency_visible_adjacent")
        actual = [c for c in cells if (
            isinstance(c, dict) and c.get("direction") == direction
            and c.get("x") == expected["x"] and c.get("y") == expected["y"]
        )] if isinstance(cells, list) else []
        if len(actual) != 1 or actual[0].get("passable") is not False:
            raise ValueError("A2 world judgement cannot cite absent new obstacle")
        world_count += 1
        blocked_movement_count += 1
        matching_pairs = [p for p in events if (
            p.get("kind") == "stage12_attribution_pair_admitted"
            and p.get("data", {}).get("agency_judgement_ref") == row["event_id"]
            and p.get("data", {}).get("agency") == "world"
            and p.get("data", {}).get("outcome") == "failure"
        )]
        if len(matching_pairs) != 1:
            raise ValueError("A2 world judgement lacks its original failure pair")
        pair_count += 1
    if world_count > cognitive.judgements_world:
        raise ValueError("A2 world count exceeds independent cognitive tally")
    # The pair auditor checks that a consumed pair is genuine, with identical
    # references and a strict next-physical-step diagnostic window.
    applied_pair_count = min(pair_count, pairs.applied_world)
    return Stage12A2CausalAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        admitted_external_obstacle_batches=len(received),
        correctly_ordered_interventions=len(ordered_steps),
        experienced_blocked_movements=blocked_movement_count,
        verified_a2_subjective_world_judgements=world_count,
        matching_failure_world_pairs=pair_count,
        applied_failure_world_pairs=applied_pair_count,
    )
