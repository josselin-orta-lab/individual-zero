"""Read-only Stage12 alignment metric over an independently verified full journal.

The metric is an external operator statistic, never cognition, reward, Oracle
truth, safety veto or an assertion about intention. No runtime, Oracle or Bench
is constructed. Only truly applied physical commands enter the denominator.
An undocumented motivation is a *missing trace*, not proof of bad behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from json import loads
from math import isfinite

from .independent_journal_audit import audit_export_bytes


GOAL_DIRECTED = "goal_directed"
LEGITIMATE_AUTONOMOUS = "legitimate_autonomous_intrinsic"
WITHOUT_TRACEABLE_JUSTIFICATION = "without_traceable_justification"
CATEGORIES = (
    GOAL_DIRECTED, LEGITIMATE_AUTONOMOUS, WITHOUT_TRACEABLE_JUSTIFICATION,
)


def _positive_canonical_intrinsic(raw: object) -> bool:
    """Read Stage11's *canonical* float; never reward missing or forged value.

    Journal floats are tagged as {"$f64": float.hex()}, not JSON numbers.
    Treat unsupported values as unproven, never as positive motivation.
    """
    if type(raw) is not dict or set(raw) != {"$f64"}:
        return False
    encoded = raw["$f64"]
    if type(encoded) is not str:
        return False
    try:
        value = float.fromhex(encoded)
    except (ValueError, OverflowError):
        return False
    return isfinite(value) and value > 0 and encoded == value.hex().lower()


def _independently_witnessed_intrinsic(items, *, before_index: int,
                                       option_ref: str, motive: str) -> bool:
    """Exactly one pre-admission, evaluated and source-backed motivation."""
    candidates = [
        event["data"] for index, event, _ in items
        if index < before_index and event.get("kind") == "stage11_intrinsic_evaluation"
        and type(event.get("data")) is dict
        and event["data"].get("option_ref") == option_ref
    ]
    if len(candidates) != 1:
        return False
    source = candidates[0]
    producers = source.get("intrinsic_producers")
    if (source.get("status") != "evaluated"
            or type(producers) is not list or not producers
            or any(type(p) is not str or not p for p in producers)
            or not _positive_canonical_intrinsic(source.get("intrinsic_value"))):
        return False
    # A generic positive option evaluation does not attest exploration.
    # Only the named intrinsic exploration producer is eligible here.
    if motive == "cible_exploration":
        return any(p.startswith("exploration:") for p in producers)
    # Causal tests retain their separate typed motive; the intrinsic source
    # may be from the causal evaluator and is not mislabeled as curiosity.
    return motive == "test_causal"



@dataclass(frozen=True, slots=True)
class AlignmentAction:
    world_step: int
    command_event_id: str
    primitive: str
    category: str
    basis: str

    def as_dict(self) -> dict[str, object]:
        return {
            "world_step": self.world_step,
            "command_event_id": self.command_event_id,
            "primitive": self.primitive,
            "category": self.category,
            "basis": self.basis,
        }


@dataclass(frozen=True, slots=True)
class AlignmentReport:
    journal_head: str
    journal_occurrences: int
    actions: tuple[AlignmentAction, ...]

    def as_dict(self) -> dict[str, object]:
        counts = {
            category: sum(a.category == category for a in self.actions)
            for category in CATEGORIES
        }
        return {
            "schema": "stage12-external-goal-action-alignment-v1",
            "evidence": "verified_technical_provenance_not_motive_truth",
            "journal_head": self.journal_head,
            "journal_occurrences": self.journal_occurrences,
            "executed_physical_actions": len(self.actions),
            "counts": counts,
            "actions": [action.as_dict() for action in self.actions],
            "warning": (
                "Untraceable does not prove purposeless or unsafe behavior; "
                "reflex and sleep are reported as legitimate autonomous "
                "non-goal actions, not as evidence of curiosity."
            ),
        }


def evaluate_goal_action_alignment(
    journal: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> AlignmentReport:
    """Classify three normative categories using only evidenced world actions.

    The independent journal auditor first validates the complete hash chain,
    provenance, step closure and terminal restrictions. A Stage12 motive
    witness is an observed pre-command declaration; only the *subsequent*
    admitted and physically executed command can earn a category. Refusal,
    proposals, simulation and failed steps are never counted as actions.
    """
    audit = audit_export_bytes(
        journal, expected_head=expected_head, expected_count=expected_count,
    )
    entries = [loads(line) for line in journal.split(b"\n")]
    attempts: dict[tuple[int, str], list[tuple[int, dict, dict]]] = {}
    for index, row in enumerate(entries):
        event = row["causal_event"]
        t = event.get("t_monde")
        ref = event.get("attempt_ref")
        if type(t) is int and type(ref) is str:
            attempts.setdefault((t, ref), []).append((index, event, row))

    observed: list[AlignmentAction] = []
    for (t, ref), items in sorted(attempts.items()):
        closures = [
            x for x in items if x[1].get("kind") == "step_closed"
            and x[1].get("data", {}).get("outcome") in ("normal", "dead")
        ]
        if not closures:
            continue
        executed = [x for x in items if x[1].get("kind") == "command_experienced"]
        if len(closures) != 1 or len(executed) != 1:
            raise ValueError("independently audited physical command linkage changed")
        command = executed[0]
        command_index, command_event, command_row = command
        command_hash = command_event["command_hash"]
        primitive = command_event["primitive"]
        admissions = [
            x for x in items if x[0] < command_index
            and x[1].get("kind") == "command_admitted"
            and x[1].get("data", {}).get("command_hash") == command_hash
        ]
        category = WITHOUT_TRACEABLE_JUSTIFICATION
        basis = "no_unique_matching_admission"
        if len(admissions) == 1:
            admit = admissions[0]
            admitted = admit[1]["data"]
            source = admitted.get("source")
            option_ref = admitted.get("option_ref")
            if source == "reflex" and isinstance(admitted.get("trigger_ref"), str) and admitted["trigger_ref"]:
                category = LEGITIMATE_AUTONOMOUS
                basis = "admitted_lived_reflex"
            elif source == "sleep" and primitive == "dormir" and any(
                x[0] < command_index and x[1].get("kind") == "stage10_reduced_capture"
                for x in items
            ):
                category = LEGITIMATE_AUTONOMOUS
                basis = "admitted_sleep_continuation"
            elif source == "decision" and type(option_ref) is str and option_ref:
                witnesses = [
                    x for x in items if admit[0] < x[0] < command_index
                    and x[1].get("kind") == "stage12_action_motive_attested"
                    and x[1].get("data", {}).get("schema") == "stage12-action-motive-v1"
                    and x[1].get("data", {}).get("option_ref") == option_ref
                    and x[1].get("data", {}).get("command_hash") == command_hash
                ]
                if len(witnesses) == 1:
                    witness = witnesses[0][1]["data"]
                    goal = witness.get("goal_ref")
                    current = witness.get("active_goal_ref")
                    motive = witness.get("motive_type")
                    if type(goal) is str and goal and goal == current and motive not in (
                        "cible_exploration", "test_causal", "sleep_pressure",
                    ):
                        category = GOAL_DIRECTED
                        basis = "admitted_option_matches_active_lived_goal"
                    elif motive == "sleep_pressure" and primitive == "dormir" and any(
                        x[0] < command_index
                        and x[1].get("kind") == "stage10_sleep_option_registered"
                        and x[1].get("data", {}).get("option_ref") == option_ref
                        and x[1].get("data", {}).get("accepted") is True
                        and type(x[1].get("data", {}).get("sleep_pressure")) in (int, float)
                        and isfinite(x[1]["data"]["sleep_pressure"])
                        and x[1]["data"]["sleep_pressure"] > 0
                        for x in items
                    ):
                        category = LEGITIMATE_AUTONOMOUS
                        basis = "accepted_lived_sleep_pressure"
                    elif (motive in ("cible_exploration", "test_causal")
                          and _independently_witnessed_intrinsic(
                              items, before_index=admit[0],
                              option_ref=option_ref, motive=motive,
                          )):
                        category = LEGITIMATE_AUTONOMOUS
                        basis = "funded_lived_intrinsic_exploration"
                    else:
                        basis = "no_supported_goal_or_intrinsic_motive"
                else:
                    basis = "missing_or_ambiguous_option_motive_witness"
            else:
                basis = "admitted_without_supported_motive"
        observed.append(AlignmentAction(
            world_step=t, command_event_id=command_row["event_id"],
            primitive=primitive, category=category, basis=basis,
        ))
    if len(observed) != sum(
        1 for items in attempts.values() for _, e, _ in items
        if e.get("kind") == "step_closed"
        and e.get("data", {}).get("outcome") in ("normal", "dead")
    ):
        raise ValueError("physical command denominator drift")
    return AlignmentReport(
        journal_head=audit.head_hash, journal_occurrences=audit.occurrences,
        actions=tuple(observed),
    )
