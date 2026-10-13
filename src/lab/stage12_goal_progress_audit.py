"""Read-only audit of Stage12 preregistered one-step *goal progress*.

The audit reconstructs the conditional outcome from a frozen pre-action
criterion, a true physical transition and I0's later lived body observation.
It verifies the claimed comparison against a recorded WorldBody result, but
not independent physical truth, subjective agency or complete goal success.
No I0 cognition, Oracle, Bench or live runtime is loaded.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .independent_journal_audit import audit_export_bytes


_VERSION = "stage12-lived-goal-progress-one-step-v1"
_MEASURES = frozenset({"water", "food", "energy", "integrity"})
_SPATIAL_VERSION = "stage12-lived-goal-spatial-progress-v1"
_SPATIAL_MEASURE = "spatial_distance"
_DIRS = {"north": (0,-1), "south": (0,1), "east": (1,0), "west": (-1,0)}


def _number(value: object) -> float | None:
    """Read a number from exact canonical causal JSON, including $f64 hex.

    The runtime stores floats as {"$f64":"0x...p+..."}; json.loads
    deliberately does NOT decode that into Python floats. Reject malformed
    tags, noncanonical hex spellings, booleans and nonfinite values.
    """
    if type(value) is dict:
        if set(value) != {"$f64"} or type(value["$f64"]) is not str:
            return None
        try:
            number = float.fromhex(value["$f64"])
        except (OverflowError, ValueError):
            return None
        if number.hex().lower() != value["$f64"]:
            return None
    elif type(value) in (int, float):
        try:
            number = float(value)
        except (OverflowError, ValueError):
            return None
    else:
        return None
    return number if isfinite(number) and number >= 0 else None


@dataclass(frozen=True, slots=True)
class Stage12GoalProgressAudit:
    head_hash: str
    occurrences: int
    preregistered: int
    verified_strict_gains: int
    verified_no_gains: int
    unavailable: int
    unresolved_at_terminal: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-goal-progress-audit-v1",
            "contract_version": _VERSION,
            "technical_comparison_verified": True,
            "preregistered_one_step_criteria": self.preregistered,
            "verified_one_step_resource_gains": self.verified_strict_gains,
            "verified_one_step_no_gains": self.verified_no_gains,
            "unavailable_next_step_observations": self.unavailable,
            "unresolved_at_terminal": self.unresolved_at_terminal,
            "complete_goal_achievement_verified": False,
            "subjective_agency_attribution_verified": False,
            "independent_physical_truth_attested": False,
            "head_hash": self.head_hash,
            "occurrences": self.occurrences,
        }


def audit_stage12_goal_progress(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12GoalProgressAudit:
    base = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count,
    )
    intents: dict[str, tuple[int, dict, dict]] = {}
    observed: set[str] = set()
    success = failure = unknown = 0
    transitions: dict[int, tuple[int, dict]] = {}
    motives: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    commands: dict[tuple[int, str], list[tuple[int, dict]]] = {}
    captures: dict[tuple[int, str], list[int]] = {}
    diagnostic_receipts: dict[tuple[int, str, int], list[tuple[int, str]]] = {}
    spatial_charges: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    diagnostic_steps: set[int] = set()
    records = [json.loads(line)["causal_event"] for line in content.split(b"\n")]
    identities = [json.loads(line)["event_id"] for line in content.split(b"\n")]

    for index, event in enumerate(records):
        kind = event.get("kind")
        t = event.get("t_monde")
        if kind == "world_transition_experienced":
            if type(t) is not int or t in transitions:
                raise ValueError("duplicate or noncanonical physical transition")
            transitions[t] = (index, event)
        elif kind == "command_experienced":
            if (type(t) is not int or type(event.get("attempt_ref")) is not str):
                raise ValueError("invalid physical command provenance")
            commands.setdefault((t, event["attempt_ref"]), []).append((index, event))
        elif kind == "perceptual_capture":
            if (type(t) is not int or type(event.get("attempt_ref")) is not str):
                raise ValueError("invalid lived capture provenance")
            captures.setdefault((t, event["attempt_ref"]), []).append(index)
        elif (kind == "compute_charge"
              and isinstance(event.get("data"), dict)
              and event["data"].get("operation") ==
                  "stage12_spatial_goal_preregistration"):
            spatial_charges.setdefault(
                (t, event.get("attempt_ref"), event.get("cycle")), [],
            ).append((index, event["data"]))
        elif kind == "stage12_action_motive_attested":
            if (type(t) is not int or type(event.get("cycle")) is not int
                    or type(event.get("attempt_ref")) is not str):
                raise ValueError("invalid pre-action motive provenance")
            motives.setdefault(
                (t, event["attempt_ref"], event["cycle"]), [],
            ).append((index, event.get("data")))
        elif kind in (
            "stage12_lived_diagnostics_published",
            "stage12_lived_diagnostics_deferred",
        ):
            if (type(t) is not int or type(event.get("attempt_ref")) is not str
                    or type(event.get("cycle")) is not int):
                raise ValueError("invalid diagnostic origin for goal followup")
            diagnostic_steps.add(t)
            diagnostic_receipts.setdefault(
                (t, event["attempt_ref"], event["cycle"]), [],
            ).append((index, kind))

    for index, event in enumerate(records):
        kind = event.get("kind")
        if kind not in (
            "stage12_goal_progress_preregistered",
            "stage12_goal_progress_followup",
        ):
            continue
        t = event.get("t_monde")
        cycle = event.get("cycle")
        attempt = event.get("attempt_ref")
        data = event.get("data")
        if (event.get("emitter") != "stage4-runtime"
                or type(t) is not int or t < 1
                or type(cycle) is not int or cycle < 1
                or type(attempt) is not str or not attempt
                or type(data) is not dict
                or data.get("contract_version") not in (_VERSION, _SPATIAL_VERSION)):
            raise ValueError("invalid Stage12 goal-progress event provenance")
        if kind == "stage12_goal_progress_followup" and (
            data["contract_version"] != (
                intents.get(data.get("intent_ref"), (None, {}, None))[1].get(
                    "contract_version")
            )
        ):
            raise ValueError("goal followup contract version does not match its source")
        # Version-specific semantic validation continues below.
        if kind == "stage12_goal_progress_preregistered":
            ref = identities[index]
            if ref in intents or any(row[1]["sent_world_step"] == t for row in intents.values()):
                raise ValueError("duplicate goal-progress precommit")
            if data.get("sent_world_step") != t:
                raise ValueError("invalid frozen goal-progress sent time")
            if (type(data.get("observe_world_step")) is not int
                    or data["observe_world_step"] != t + 1):
                raise ValueError("invalid frozen goal-progress observation deadline")
            spatial = data["contract_version"] == _SPATIAL_VERSION
            if (type(data.get("measure")) is not str
                    or data["measure"] not in (
                        {_SPATIAL_MEASURE} if spatial else _MEASURES
                    )):
                raise ValueError("invalid frozen goal-progress measure")
            if spatial:
                spatial_debits = spatial_charges.get((t, attempt, cycle), [])
                if (len(spatial_debits) != 1
                        or spatial_debits[0][0] >= index
                        or spatial_debits[0][1].get("module")
                           != "metacognition_health"
                        or spatial_debits[0][1].get("accepted") is not True
                        or type(spatial_debits[0][1].get("requested_uc")) is not int
                        or spatial_debits[0][1]["requested_uc"] < 1):
                    raise ValueError("spatial criterion lacks independently paid UC")
                if (set(data) != {
                    "contract_version", "goal_ref", "option_ref",
                    "command_hash", "measure", "value_before",
                    "sent_world_step", "observe_world_step", "life_id",
                    "start_x", "start_y", "target_x", "target_y",
                    "target_kind", "direction",
                } or type(data["life_id"]) is not str or not data["life_id"]
                        or type(data["direction"]) is not str
                        or data["direction"] not in _DIRS
                        or data["target_kind"] not in ("water", "berry_a", "berry_b")
                        or any(type(data[key]) is not int for key in (
                            "start_x", "start_y", "target_x", "target_y"
                        ))
                        or _number(data.get("value_before")) != 1.0):
                    raise ValueError("malformed spatial pre-action target or identity")
                dx, dy = _DIRS[data["direction"]]
                if (data["target_x"], data["target_y"]) != (
                        data["start_x"]+dx, data["start_y"]+dy):
                    raise ValueError("spatial criterion target not along intended movement")
                pre = captures.get((t, attempt), [])
                if len(pre) != 1 or pre[0] >= index:
                    raise ValueError("spatial criterion lacks unique pre-action perception")
                source = records[pre[0]]
                pos = source.get("data", {}).get("position")
                candidates = source.get("data", {}).get("agency_visible_adjacent")
                if (not isinstance(pos, dict)
                        or (pos.get("x"), pos.get("y"))
                           != (data["start_x"], data["start_y"])
                        or not isinstance(candidates, list)):
                    raise ValueError("spatial criterion lacks a witnessed initial position")
                matches = [cell for cell in candidates if (
                    isinstance(cell, dict)
                    and cell.get("direction") == data["direction"]
                    and (cell.get("x"), cell.get("y")) == (
                        data["target_x"], data["target_y"]
                    )
                )]
                if len(matches) != 1:
                    raise ValueError("spatial criterion lacks unique visible target direction")
                witness = matches[0]
                relevant = (witness.get("water_source") is True
                            if data["target_kind"] == "water"
                            else data["target_kind"] in witness.get("resources", ()))
                if not relevant:
                    raise ValueError("spatial target does not occur in I0's earlier perception")
            if _number(data.get("value_before")) is None:
                raise ValueError("invalid frozen goal-progress starting body value")
            for field in ("goal_ref", "option_ref", "command_hash"):
                if type(data.get(field)) is not str or not data[field]:
                    raise ValueError("invalid frozen goal-progress " + field)
            possible = motives.get((t, attempt, cycle), [])
            if not any(
                mindex < index and isinstance(mdata, dict)
                and mdata.get("command_hash") == data["command_hash"]
                and mdata.get("option_ref") == data["option_ref"]
                and mdata.get("goal_ref") == data["goal_ref"]
                and mdata.get("active_goal_ref") == data["goal_ref"]
                and mdata.get("motive_type") == "active_goal"
                for mindex, mdata in possible
            ):
                raise ValueError("goal criterion lacks an independently declared active motive")
            if t not in transitions or transitions[t][0] <= index:
                raise ValueError("goal criterion was not preregistered before physical command")
            command_receipts = commands.get((t, attempt), [])
            if (len(command_receipts) != 1
                    or command_receipts[0][0] <= index
                    or command_receipts[0][0] >= transitions[t][0]
                    or command_receipts[0][1].get("emitter") != "action_control"
                    or command_receipts[0][1].get("command_hash") != data["command_hash"]
                    or transitions[t][1].get("attempt_ref") != attempt):
                raise ValueError("goal precommit does not match the physically executed command")
            command = command_receipts[0][1]
            primitive, parameters = command.get("primitive"), command.get("parameters")
            if (type(primitive) is not str or not primitive
                    or type(parameters) is not dict):
                raise ValueError("physically executed command has invalid public fields")
            # Event-to-event equality is insufficient: an attacker who
            # rehashes motive, intent and command receipts together could
            # otherwise substitute an invented command hash. Verify that
            # the digest agrees with the *publicly recorded* command bytes.
            # This does not establish independent physical-world truth.
            if spatial and (primitive != "se_deplacer"
                            or parameters.get("direction") != data["direction"]):
                raise ValueError("spatial criterion is not the executed movement")
            expected_command_hash = sha256_hex(canonical_causal_bytes({
                "primitive": primitive, "parameters": parameters,
            }))
            if expected_command_hash != data["command_hash"]:
                raise ValueError("physically executed command digest mismatch")
            intents[ref] = (index, data, event)
        else:
            ref = data.get("intent_ref")
            if type(ref) is not str or ref not in intents or ref in observed:
                raise ValueError("missing or reused goal-progress source intent")
            source_index, intent, source_event = intents[ref]
            if (index <= source_index
                    or data.get("sent_world_step") != intent["sent_world_step"]
                    or data.get("observed_world_step") != t
                    or data.get("measure") != intent["measure"]
                    or _number(data.get("value_before")) is None
                    or _number(data["value_before"]) != _number(intent["value_before"])
                    or t <= intent["sent_world_step"]):
                raise ValueError("goal followup does not match frozen pre-action criterion")
            observed_captures = captures.get((t, attempt), [])
            diag = diagnostic_receipts.get((t, attempt, cycle), [])
            if (len(observed_captures) != 1
                    or observed_captures[0] >= index
                    or len(diag) != 1 or diag[0][0] >= index):
                raise ValueError("goal followup lacks one prior lived capture and diagnostic receipt")
            if (diag[0][1] == "stage12_lived_diagnostics_deferred") != (
                    data.get("reason") == "diagnostic_uc_not_available"):
                raise ValueError("goal followup does not match charged diagnostic availability")
            before = _number(intent["value_before"])
            if before is None:
                raise ValueError("invalid frozen goal-progress baseline")
            after = _number(data.get("value_after"))
            outcome = data.get("criterion_outcome")
            reason = data.get("reason")
            if outcome == "unknown":
                if (after is not None or reason not in (
                        "diagnostic_uc_not_available",
                        "one_step_observation_window_missed",
                        "lived_measure_unavailable")):
                    raise ValueError("unsupported unavailable goal-progress outcome")
                if (t == intent["observe_world_step"]
                        and reason == "one_step_observation_window_missed"):
                    raise ValueError("false missed-window claim")
                unknown += 1
            else:
                if after is None or before is None:
                    raise ValueError("goal outcome lacks admitted observable measurement")
                if intent["contract_version"] == _SPATIAL_VERSION:
                    expected_success = after < before
                    expected_reason = (
                        "measured_spatial_progress" if expected_success
                        else "no_measured_spatial_progress"
                    )
                else:
                    expected_success = after > before
                    expected_reason = (
                        "measured_strict_gain" if expected_success
                        else "no_measured_strict_gain"
                    )
                if (t != intent["observe_world_step"] or after is None
                        or reason != expected_reason
                        or outcome != ("success" if expected_success else "failure")):
                    raise ValueError("goal outcome contradicts preregistered criterion")
                transition_index, transition = transitions[intent["sent_world_step"]]
                if intent["contract_version"] == _SPATIAL_VERSION:
                    perceptual_data = records[observed_captures[0]].get("data", {})
                    observed_pos = perceptual_data.get("position")
                    physical_pos = transition.get("position_after")
                    if (not isinstance(observed_pos, dict)
                            or not isinstance(physical_pos, dict)
                            or any(type(pos.get(key)) is not int for pos in (
                                observed_pos, physical_pos
                            ) for key in ("x", "y"))
                            or observed_pos != physical_pos):
                        raise ValueError("spatial followup lacks independently witnessed new position")
                    observed_physical = float(
                        abs(observed_pos["x"] - intent["target_x"])
                        + abs(observed_pos["y"] - intent["target_y"])
                    )
                else:
                    physical = transition.get("body_after", {})
                    observed_physical = _number(
                        physical.get(intent["measure"]) if isinstance(physical, dict) else None
                    )
                if observed_physical is None or observed_physical != after:
                    raise ValueError("goal followup diverges from committed lived state")
                if transition_index <= source_index or transition_index >= index:
                    raise ValueError("goal outcome/physical transition ordering violation")
                if outcome == "success":
                    success += 1
                else:
                    failure += 1
            observed.add(ref)

    # A future charged diagnostic must close an earlier precommit (even if
    # evidence is unavailable). A death or operator-stop may leave the very
    # last intention terminal, without creating postmortem cognition.
    unresolved = 0
    for ref, (_, data, _) in intents.items():
        if ref in observed:
            continue
        if any(step > data["sent_world_step"] for step in diagnostic_steps):
            raise ValueError("missing goal-progress closure despite later diagnostic")
        unresolved += 1

    return Stage12GoalProgressAudit(
        head_hash=base.head_hash,
        occurrences=base.occurrences,
        preregistered=len(intents),
        verified_strict_gains=success,
        verified_no_gains=failure,
        unavailable=unknown,
        unresolved_at_terminal=unresolved,
    )
