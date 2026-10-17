"""Retrospective public Stage11 trace at the first observed route divergence.

Lab-only inspection of already published technical events AFTER each completed
step. Never used by cognition, action selection or an injected safety oracle.
No inference of causal learning from an isolated decision difference.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .snapshots import SnapshotType
from .stage11_routed_junction_probe import build_public_route_runtime
from .stage11_transient_hidden_route_probe import (
    PROTOCOL as PARENT_PROTOCOL, schedule_for,
)

PROTOCOL = "stage11-public-transient-route-divergence-trace-dev-v1"
VARIANTS = ("control", "hidden_transient")
PLANNING_UC = 4
EXPLORATION_UC = 4
STEPS = 10
SNAPSHOT_STEPS = (4, 5)

# Immutable public dev reference, from CI #38134913304 on 00619fec... .
# This is a software reproduction guard, never a scientific Golden.
PREVIOUS_JOURNAL_SHA256 = {
    "control": "97ce45cb83a16329442d4da94bdde4ecc8d7346c2bebb0ae5dca04a9d234ad41",
    "hidden_transient": "a93ef4d2326eea618be7a47a4db8ab7957c2678cd88fa07040fff15ff413fd6e",
}
TRACE_KINDS_STEP5 = frozenset({
    "stage11_geographic_option_proposed",
    "stage11_intrinsic_evaluation",
    "stage8_option_evaluation",
    "competition_cycle",
    "stage11_geographic_preflight_consulted",
    "stage11_geographic_budget_deferred",
    "stage11_geographic_planning_unavailable",
    "stage11_route_search",
    "compute_charge",
    "s_t_published",
    "command_admitted",
    "command_vetoed",
})
FIELDS_BY_KIND = {
    "stage11_geographic_option_proposed": (
        "target_ref", "option_ref", "source", "destination", "direction",
    ),
    "stage11_intrinsic_evaluation": (
        "option_ref", "status", "intrinsic_value", "P15_intrinsic_weight",
    ),
    "stage8_option_evaluation": (
        "option_ref", "status", "learned_value_status", "learned_value",
        "simulated_value_status", "simulated_value",
    ),
    "stage11_geographic_preflight_consulted": (
        "raw_frontier_count", "admissible_frontier_count",
        "inadmissible_directions_count", "charged_uc",
    ),
    "stage11_geographic_budget_deferred": (
        "failed_operation", "reason", "world_step",
    ),
    "stage11_geographic_planning_unavailable": ("target_ref", "reason"),
    "stage11_route_search": ("route_found", "world_step", "charged_operation"),
    "s_t_published": ("version", "competitive_refs"),
    "compute_charge": (
        "module", "operation", "count", "requested_uc",
        "accepted", "reason",
    ),
    "command_admitted": (
        "option_ref", "source", "primitive", "reason", "rule_id",
    ),
    "command_vetoed": (
        "option_ref", "source", "primitive", "reason", "rule_id",
    ),
}
COMPETITION_TRACE_FIELDS = (
    "option_ref", "accumulator_before", "accumulator_after",
    "threshold", "evidence", "crossed",
)


@dataclass(frozen=True, slots=True)
class RouteDivergenceTraceResult:
    protocol_version: str
    parent_protocol_version: str
    classification: str
    variant: str
    planning_uc: int
    exploration_uc: int
    prior_result_journal_sha256: str
    reproduced_journal_sha256: str
    snapshot_ids_and_hashes: tuple[tuple[int, str, str], ...]
    initial_perception_prefix_sha256: str
    first_four_actions: tuple[tuple[str, str | None, str | None, str], ...]
    step5_action: tuple[str, str | None, str | None, str]
    integrity_after_steps_3_to_5: tuple[tuple[int, float], ...]
    modulation_profiles_after_steps_3_to_5: tuple[tuple[int, str], ...]
    modulation_transitions_steps_3_to_5: tuple[dict[str, object], ...]
    step5_causal_events: tuple[dict[str, object], ...]
    step5_geographic_options_proposed: int
    step5_geographic_options_evaluated: int
    step5_geographic_accumulator_crossings: int
    heldout: bool = False
    scientific_verdict: None = None

    def to_dict(self):
        data = asdict(self)
        data["evidence_sha256"] = sha256_hex(canonical_causal_bytes(data))
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def run_public_route_divergence_trace(*, variant: str) -> RouteDivergenceTraceResult:
    if variant not in VARIANTS:
        raise ValueError("unregistered public first-divergence variant")
    runtime = build_public_route_runtime(
        layout_variant="junction_open", survey_refresh=True,
        planning_uc=PLANNING_UC, exploration_uc=EXPLORATION_UC,
        scenario_events=schedule_for(variant),
    )
    actions = []
    integrity = []
    profiles = []
    records = []
    manager = runtime.stage3.substrate.snapshots
    for step in range(1, STEPS + 1):
        o = runtime.run_step()
        actions.append((
            o.execution_status, o.command_primitive, o.option_ref, o.source,
        ))
        if step in (3, 4, 5):
            integrity.append((step, float(runtime.world.body.integrity)))
            profiles.append((step, runtime.modulation.profile))
        if step in SNAPSHOT_STEPS:
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id=runtime.individual_id,
                t_monde=step, cycle=0, attempt_ref=None,
                owners=runtime.causal_owners,
                versions={"stage11": runtime._stage11_config.version},
            )
            if not manager.verify(record.id):
                raise AssertionError("failed to verify declared boundary snapshot")
            records.append((step, record.id, record.sha256))
    if not runtime.journal.verify():
        raise AssertionError("technical trace chain invalid")
    journal_digest = sha256_hex(runtime.journal.canonical_bytes())
    if journal_digest != PREVIOUS_JOURNAL_SHA256[variant]:
        raise AssertionError("earlier public ten-step journal did not reproduce")

    all_events = tuple(entry.causal_event for entry in runtime.journal.entries)
    perceptions = tuple(
        e["data"] for e in all_events
        if e.get("kind") == "perceptual_capture"
    )
    if len(perceptions) != STEPS:
        raise AssertionError("missing physical perceptual events")
    step5 = []
    transitions = []
    for event in all_events:
        kind, time = event.get("kind"), event.get("t_monde")
        if kind == "stage11_modulation_transition" and time in (3, 4, 5):
            transitions.append({
                "world_step": time,
                "cycle": event.get("cycle"),
                "before": event["data"]["before"],
                "after": event["data"]["after"],
            })
        if time != 5 or kind not in TRACE_KINDS_STEP5:
            continue
        data = event.get("data", {})
        if kind == "compute_charge" and data.get("module") != "planning":
            continue
        if kind == "competition_cycle":
            # Only existing registered options appear in the actual
            # competition trace; no counterfactual option is invented.
            selected = {
                "traces": [
                    {k: trace[k] for k in COMPETITION_TRACE_FIELDS}
                    for trace in data.get("traces", ())
                    if "geographic:" in trace["option_ref"]
                    or trace["option_ref"] == "permanent:attendre"
                ],
            }
        else:
            selected = {
                k: data[k] for k in FIELDS_BY_KIND.get(kind, ())
                if k in data
            }
        step5.append({
            "kind": kind,
            "cycle": event.get("cycle"),
            "data": selected,
        })

    proposed = sum(
        event["kind"] == "stage11_geographic_option_proposed"
        for event in step5
    )
    evaluated = sum(
        event["kind"] == "stage8_option_evaluation"
        and "geographic:" in event["data"].get("option_ref", "")
        for event in step5
    )
    crossings = sum(
        trace["crossed"] is True
        for event in step5
        if event["kind"] == "competition_cycle"
        for trace in event["data"]["traces"]
        if "geographic:" in trace["option_ref"]
    )
    return RouteDivergenceTraceResult(
        protocol_version=PROTOCOL, parent_protocol_version=PARENT_PROTOCOL,
        classification="public_postresult_development_diagnostic_not_heldout",
        variant=variant, planning_uc=PLANNING_UC,
        exploration_uc=EXPLORATION_UC,
        prior_result_journal_sha256=PREVIOUS_JOURNAL_SHA256[variant],
        reproduced_journal_sha256=journal_digest,
        snapshot_ids_and_hashes=tuple(records),
        initial_perception_prefix_sha256=sha256_hex(
            canonical_causal_bytes(perceptions[:2])
        ),
        first_four_actions=tuple(actions[:4]), step5_action=actions[4],
        integrity_after_steps_3_to_5=tuple(integrity),
        modulation_profiles_after_steps_3_to_5=tuple(profiles),
        modulation_transitions_steps_3_to_5=tuple(transitions),
        step5_causal_events=tuple(step5),
        step5_geographic_options_proposed=proposed,
        step5_geographic_options_evaluated=evaluated,
        step5_geographic_accumulator_crossings=crossings,
    )


if __name__ == "__main__":
    for variant_name in VARIANTS:
        print(
            "stage11_public_route_divergence_trace="
            + run_public_route_divergence_trace(
                variant=variant_name,
            ).to_json()
        )
