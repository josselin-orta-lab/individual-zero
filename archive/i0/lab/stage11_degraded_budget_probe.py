"""Bounded public Stage-11 strict UC exhaustion diagnostic.

This fixed software fixture never replaces the canonical safety source,
Equipment or Perception. Tests require no hidden world, oracle, reward or
scientific inference. All charge failures are preserved as journal events.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import START_BODY, _positions
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime

PROTOCOL = "stage11-public-strict-geographic-budget-dev-v3"
VARIANTS = ("planning_0", "planning_1", "planning_3", "exploration_0")


@dataclass(frozen=True, slots=True)
class PublicStrictBudgetResult:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    config_version: str
    planning_envelope_uc: int
    exploration_envelope_uc: int
    budget_config_version: str
    accepted_preflight_uc: int
    rejected_preflight_attempts: int
    charged_preflight_consultations: int
    preflight_charge_order_violations: int
    accepted_build_uc: int
    rejected_build_attempts: int
    rejected_exploration_attempts: int
    budget_deferred_operations: tuple[str, ...]
    malformed_defer_events: int
    applied_geographic_commands: int
    physically_perceived_distinct_sites: int
    confirmed_geographic_sites: int
    remaining_offered_targets: int
    rejected_requested_uc: int
    journal_sha256: str
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self):
        data = asdict(self)
        data["evidence_sha256"] = sha256_hex(canonical_causal_bytes(data))
        return data

    def to_json(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))


def _strict_stage11_config(ref, *, variant: str):
    if variant not in VARIANTS:
        raise ValueError("undeclared strict UC software fixture")
    cfg = ref._stage11_config
    stage9 = cfg.stage9
    stage8 = stage9.stage8
    stage7 = stage8.stage7
    stage6 = stage7.stage6
    stage4 = stage6.stage4
    original = stage4.compute_budget
    planning = int(variant.split("_")[1]) if variant.startswith("planning_") else 20
    exploration = 0 if variant == "exploration_0" else cfg.exploration_envelope_uc
    configured_budget = replace(
        original,
        version=original.version + "+strict-geography-" + variant + "-v1",
        module_envelopes={
            **original.module_envelopes,
            "planning": planning,
        },
    )
    return replace(
        cfg, version=cfg.version + "+strict-geography-" + variant + "-v1",
        exploration_envelope_uc=exploration,
        stage9=replace(
            stage9, stage8=replace(
                stage8, stage7=replace(
                    stage7, stage6=replace(
                        stage6, stage4=replace(
                            stage4, compute_budget=configured_budget,
                        ),
                    ),
                ),
            ),
        ),
    )


def run_public_strict_geographic_budget(
    *, variant: str, steps: int = 3,
) -> PublicStrictBudgetResult:
    if variant not in VARIANTS or type(steps) is not int or steps != 3:
        raise ValueError("strict UC fixtures require exactly three public steps")
    reference = build_stage11_reference_runtime(enable_geography=True)
    cfg = _strict_stage11_config(reference, variant=variant)
    runtime = Stage11Runtime(
        world_config=replace(
            reference.world.config, initial_body=START_BODY,
        ),
        layout=reference.world._layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=reference._canonical_safety._innate,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=cfg,
        equipment=reference.equipment,
    )
    outputs = [runtime.run_step() for _ in range(steps)]
    if not runtime.journal.verify():
        raise AssertionError("unverified strict-budget software journal")
    events = [row.causal_event for row in runtime.journal.entries]
    charges = [
        row["data"] for row in events if row.get("kind") == "compute_charge"
    ]

    def charged(operation, accepted):
        return [
            row for row in charges
            if row["operation"] == operation and row["accepted"] is accepted
        ]

    deferred = [
        row["data"] for row in events
        if row.get("kind") == "stage11_geographic_budget_deferred"
    ]
    consulted = [
        (index, row) for index, row in enumerate(events)
        if row.get("kind") == "stage11_geographic_preflight_consulted"
    ]
    order_violations = 0
    for index, entry in consulted:
        data = entry["data"]
        preceding_phase_opens = [
            prior for prior in events[:index]
            if prior.get("kind") == "phase_opened"
            and prior.get("t_monde") == entry["t_monde"]
            and prior.get("cycle") == entry.get("cycle")
        ]
        previous_charges = [
            prior for prior in events[:index]
            if prior.get("kind") == "compute_charge"
            and prior.get("t_monde") == entry["t_monde"]
            and prior.get("cycle") == entry.get("cycle")
            and prior.get("data", {}).get("module") == "planning"
            and prior.get("data", {}).get("operation")
            == "geographic_admissibility_preflight"
            and prior["data"].get("accepted") is True
        ]
        if (
            len(previous_charges) != 1
            or not preceding_phase_opens
            or preceding_phase_opens[-1].get("phase") != 1
            or data.get("boundary") != "phase1_planning_after_accepted_charge"
            or data.get("charged_operation")
            != "geographic_admissibility_preflight"
            or data.get("charged_module") != "planning"
            or data.get("charged_uc") != 1
            or data.get("source") != "action_control.verifier_admissibilite"
            or data.get("safety_policy_modified") is not False
        ):
            order_violations += 1
    if len(consulted) != len(charged(
        "geographic_admissibility_preflight", True,
    )):
        order_violations += 1
    if order_violations:
        raise AssertionError(
            "early safety preflight was not charged before consultation"
        )

    malformed = sum(
        row.get("reason") != "incomplete_budget"
        or row.get("source") != "compute_budget"
        or row.get("new_targets_designated") is not False
        or row.get("safety_decision") is not None
        or row.get("novelty_absence_claim") is not False
        or row.get("physical_visits_preserved") is not True
        for row in deferred
    )
    physical = _positions(runtime)
    visited = runtime.exploration.geographic.export_causal_state()["visits"]
    if set(physical) != {tuple(row[:2]) for row in visited}:
        raise AssertionError("strict budget lost physically observed sites")
    moves = [
        output for output in outputs
        if output.execution_status == "applied"
        and output.option_ref is not None
        and output.option_ref.startswith("option:geographic:")
    ]
    return PublicStrictBudgetResult(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps, config_version=cfg.version,
        planning_envelope_uc=runtime._config.compute_budget.module_envelopes["planning"],
        exploration_envelope_uc=runtime._config.compute_budget.module_envelopes["exploration"],
        budget_config_version=runtime._config.compute_budget.version,
        accepted_preflight_uc=sum(
            row["requested_uc"] for row in charged(
                "geographic_admissibility_preflight", True,
            )
        ),
        rejected_preflight_attempts=len(charged(
            "geographic_admissibility_preflight", False,
        )),
        charged_preflight_consultations=len(consulted),
        preflight_charge_order_violations=order_violations,
        accepted_build_uc=sum(row["requested_uc"] for row in charged(
            "planning_build", True,
        )),
        rejected_build_attempts=len(charged("planning_build", False)),
        rejected_exploration_attempts=len(charged(
            "exploration_observe", False,
        )),
        budget_deferred_operations=tuple(
            row["failed_operation"] for row in deferred
        ),
        malformed_defer_events=malformed,
        applied_geographic_commands=len(moves),
        physically_perceived_distinct_sites=len(set(physical)),
        confirmed_geographic_sites=runtime.exploration.geographic.distinct_sites,
        remaining_offered_targets=len(runtime.exploration.geographic.offered),
        rejected_requested_uc=sum(
            row["requested_uc"] for row in charges if row["accepted"] is False
        ),
        journal_sha256=runtime.journal.head_hash,
    )


if __name__ == "__main__":
    for variant_name in VARIANTS:
        print(run_public_strict_geographic_budget(
            variant=variant_name,
        ).to_json())
