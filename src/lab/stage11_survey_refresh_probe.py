"""Opt-in Stage11 physical survey refresh comparison, development evidence only.

Every route candidate comes from already-paid local Perception survey history.
External creature/danger changes are journaled Lab input, never cognition data.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import _positions
from .stage11_routed_junction_probe import build_public_route_runtime
from .stage11_stale_route_safety_probe import VARIANTS, registered_events

PROTOCOL = "stage11-public-survey-refresh-dev-v1"


@dataclass(frozen=True, slots=True)
class PublicSurveyRefreshTrace:
    protocol_version: str
    classification: str
    variant: str
    refresh_surveys: bool
    exploration_uc: int | None
    steps: int
    input_sha256: str
    initial_local_sha256: str
    snapshot_schema: str
    observed_positions: tuple[tuple[int, int], ...]
    confirmed_visit_sites: tuple[tuple[int, int], ...]
    actions: tuple[tuple[str, str | None, str | None], ...]
    action_sources: tuple[str, ...]
    recorded_survey_steps: tuple[int, ...]
    survey_revisions: tuple[dict[str, object], ...]
    route_candidate_steps: tuple[int, ...]
    route_candidate_step_cycles: tuple[tuple[int, int], ...]
    route_proposal_steps: tuple[int, ...]
    applied_route_steps: tuple[int, ...]
    applied_route_into_occupied_neighbor: int
    externally_applied_operations: tuple[str, ...]
    seen_return_junction_after_dead_end: bool
    captured_southern_alternative: bool
    danger_damage_total: float
    final_integrity: float
    accepted_exploration_observe_uc: int
    rejected_exploration_observe_uc: int
    accepted_route_search_uc: int
    journal_sha256: str
    journal_head: str
    exploration_state_sha256: str
    heldout: bool = False
    scientific_verdict: None = None

    def to_json(self):
        payload = asdict(self)
        payload["evidence_sha256"] = sha256_hex(canonical_causal_bytes(payload))
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def run_public_survey_refresh(
    *, variant: str, refresh_surveys: bool,
    exploration_uc: int | None = None, steps: int = 10,
) -> PublicSurveyRefreshTrace:
    if (
        variant not in VARIANTS
        or type(refresh_surveys) is not bool
        or type(steps) is not int or steps != 10
        or (
            exploration_uc is not None
            and (type(exploration_uc) is not int or exploration_uc not in (0, 4))
        )
    ):
        raise ValueError("only prospectively registered public survey cases")
    schedule = registered_events(variant)
    runtime = build_public_route_runtime(
        scenario_events=schedule,
        survey_refresh=refresh_surveys,
        exploration_uc=exploration_uc,
    )
    initial_local = runtime.world.capture_local(t_monde=1).as_dict()
    input_hash = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL,
        "variant": variant,
        "refresh_surveys": refresh_surveys,
        "exploration_uc": exploration_uc,
        "steps": steps,
        "layout": runtime.world._layout.as_dict(),
        "world": runtime.world.config.as_dict(),
        "scenario": [e.as_dict() for e in schedule],
        "stage11_config_version": runtime._stage11_config.version,
        "geographic_config_version": runtime.exploration.geographic.config.version,
        "budget_version": runtime._config.compute_budget.version,
        "equipment_version": runtime.equipment.version,
    }))
    outcomes = tuple(runtime.run_step() for _ in range(steps))
    if not runtime.journal.verify():
        raise AssertionError("invalid survey-refresh canonical journal")
    observations = _positions(runtime)
    if len(observations) != steps:
        raise AssertionError("missing step-opening physical Perception capture")
    geo = runtime.exploration.geographic
    state = runtime.exploration.export_causal_state()
    visits = tuple(sorted(
        (int(x), int(y)) for x, y, _ in geo.export_causal_state()["visits"]
    ))
    if set(visits) != set(observations):
        raise AssertionError("owner credited an unobserved geographic site")
    entries = tuple(e.causal_event for e in runtime.journal.entries)
    external_received = tuple(
        e for e in entries if e.get("kind") == "external_input_received"
    )
    external_applied = tuple(
        e for e in entries if e.get("kind") == "external_input_applied"
    )
    if (
        len(external_received) != len(schedule)
        or len(external_applied) != len(schedule)
        or tuple(e["operation"] for e in external_received)
        != tuple(e.operation for e in schedule)
        or tuple(e["t_monde"] for e in external_received)
        != tuple(e.t_monde for e in schedule)
        or tuple(e["t_monde"] for e in external_applied)
        != tuple(e.t_monde for e in schedule)
    ):
        raise AssertionError("external physical inputs missing or out of order")
    # 'operation' belongs to received records; applied records attest that
    # the already declared input was enacted, not a second command source.
    for original in schedule:
        received_indices = tuple(i for i, row in enumerate(entries)
                                 if row.get("kind") == "external_input_received"
                                 and row["t_monde"] == original.t_monde)
        applied_indices = tuple(i for i, row in enumerate(entries)
                                if row.get("kind") == "external_input_applied"
                                and row["t_monde"] == original.t_monde)
        if (len(received_indices) != 1 or len(applied_indices) != 1
            or received_indices[0] >= applied_indices[0]):
            raise AssertionError("external input applied before received")
    survey_events = tuple(
        (index, e) for index, e in enumerate(entries)
        if e.get("kind") == "stage11_route_survey_recorded"
    )
    revision_events = []
    for i, e in survey_events:
        data = e["data"]
        if refresh_surveys:
            if data.get("hidden_world_oracle_used") is not False:
                raise AssertionError("route survey must exclude Lab-only world truth")
            if data.get("survey_revision") is True:
                if (
                    data["prior_observed_world_step"] >= e["t_monde"]
                    or data["previous_free_neighbors"]
                    == data["observed_free_neighbors"]
                    or data["position"] != list(observations[e["t_monde"] - 1])
                ):
                    raise AssertionError("invalid physical survey revision provenance")
                charges = tuple(
                    x for x in entries[:i]
                    if x.get("kind") == "compute_charge"
                    and x.get("t_monde") == e["t_monde"]
                    and x.get("cycle") == e.get("cycle")
                    and x.get("data", {}).get("module") == "exploration"
                    and x.get("data", {}).get("operation") == "exploration_observe"
                    and x["data"].get("accepted") is True
                )
                if not charges:
                    raise AssertionError("uncharged Phase-1 survey revision")
                revision_events.append({
                    "world_step": e["t_monde"],
                    "cycle": e["cycle"],
                    "position": data["position"],
                    "old_neighbors": data["previous_free_neighbors"],
                    "new_neighbors": data["observed_free_neighbors"],
                    "old_observed_step": data["prior_observed_world_step"],
                    "source": data["source"],
                })
        elif "survey_revision" in data:
            raise AssertionError("v2 baseline must not contain v3 revisions")

    transitions = tuple(
        x for x in entries if x.get("kind") == "world_transition_experienced"
    )
    if len(transitions) != steps:
        raise AssertionError("missing physical transitions")
    occupied_steps = set()
    creature_present = False
    for step in range(1, steps + 1):
        for event in external_received:
            if event["t_monde"] == step:
                if event["operation"] == "place_creature":
                    creature_present = True
                elif event["operation"] == "remove_creature":
                    creature_present = False
        if creature_present:
            occupied_steps.add(step)
    applied_routes = tuple(
        step for step, outcome in enumerate(outcomes, 1)
        if outcome.execution_status == "applied"
        and "frontier_route:" in (outcome.option_ref or "")
    )
    route_into_creature = sum(
        step in occupied_steps
        and ":via:3:2:" in (outcomes[step-1].option_ref or "")
        for step in applied_routes
    )
    if route_into_creature:
        raise AssertionError("routed action entered an observed occupied cell")
    after_end = (
        observations[observations.index((4, 2)) + 1:]
        if (4, 2) in observations else ()
    )

    def paid(module, operation, *, accepted):
        return sum(
            int(event["data"]["requested_uc"]) for event in entries
            if event.get("kind") == "compute_charge"
            and event.get("data", {}).get("module") == module
            and event["data"].get("operation") == operation
            and event["data"].get("accepted") is accepted
        )

    return PublicSurveyRefreshTrace(
        protocol_version=PROTOCOL,
        classification="public_development_only_not_heldout",
        variant=variant, refresh_surveys=refresh_surveys,
        exploration_uc=exploration_uc, steps=steps,
        input_sha256=input_hash,
        initial_local_sha256=sha256_hex(canonical_causal_bytes(initial_local)),
        snapshot_schema=geo.export_causal_state()["schema"],
        observed_positions=observations, confirmed_visit_sites=visits,
        actions=tuple((
            outcome.execution_status, outcome.command_primitive,
            outcome.option_ref,
        ) for outcome in outcomes),
        action_sources=tuple(outcome.source for outcome in outcomes),
        recorded_survey_steps=tuple(e["t_monde"] for _, e in survey_events),
        survey_revisions=tuple(revision_events),
        route_candidate_steps=tuple(
            e["t_monde"] for e in entries
            if e.get("kind") == "stage11_route_search"
            and e["data"]["route_found"] is True
        ),
        route_candidate_step_cycles=tuple(
            (e["t_monde"], e["cycle"]) for e in entries
            if e.get("kind") == "stage11_route_search"
            and e["data"]["route_found"] is True
        ),
        route_proposal_steps=tuple(
            e["t_monde"] for e in entries
            if e.get("kind") == "stage11_geographic_option_proposed"
            and e["data"].get("source") == "frozen_prior_observed_frontier_route"
        ),
        applied_route_steps=applied_routes,
        applied_route_into_occupied_neighbor=route_into_creature,
        externally_applied_operations=tuple(
            e["operation"] for e in external_received
        ),
        seen_return_junction_after_dead_end=(2, 2) in after_end,
        captured_southern_alternative=any(
            p in {(2, 3), (2, 4)} for p in after_end
        ),
        danger_damage_total=sum(
            float(x["effects"].get("danger_zone_damage", 0.0))
            for x in transitions
        ),
        final_integrity=float(runtime.world.body.integrity),
        accepted_exploration_observe_uc=paid(
            "exploration", "exploration_observe", accepted=True
        ),
        rejected_exploration_observe_uc=paid(
            "exploration", "exploration_observe", accepted=False
        ),
        accepted_route_search_uc=paid(
            "planning", "geographic_route_search", accepted=True
        ),
        journal_sha256=sha256_hex(runtime.journal.canonical_bytes()),
        journal_head=runtime.journal.head_hash,
        exploration_state_sha256=sha256_hex(canonical_causal_bytes(state)),
    )


if __name__ == "__main__":
    for label in VARIANTS:
        for enabled in (False, True):
            print("stage11_public_survey_refresh=" + run_public_survey_refresh(
                variant=label, refresh_surveys=enabled,
            ).to_json())
