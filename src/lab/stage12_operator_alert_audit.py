"""Independent, read-only audit of persistent Stage12 operator warning receipts.

Imports no i0, WorldBody, Oracle or Bench runtime. A verified hash-chain
alone is not sufficient: recompute episode timing from the real dated,
individually charged Stage12 diagnostic publications. Silence is meaningful:
missing required alerts and synthetic unearned alerts both fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from .independent_journal_audit import audit_export_bytes


_WARNING_KEYS = ("stagnation", "reasoning_loop", "low_context_entropy", "attribution_bias")


@dataclass(frozen=True, slots=True)
class Stage12OperatorAlertAudit:
    head_hash: str
    occurrences: int
    examined_samples: int
    emitted_alerts: int
    counts_by_signal: dict[str, int]
    policy_version: str | None
    persistence_world_steps: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-operator-alert-audit-v1",
            "verified": True,
            "head_hash": self.head_hash,
            "occurrences": self.occurrences,
            "examined_samples": self.examined_samples,
            "emitted_alerts": self.emitted_alerts,
            "counts_by_signal": dict(self.counts_by_signal),
            "policy_version": self.policy_version,
            "persistence_world_steps": self.persistence_world_steps,
            "warning": (
                "Alerts are reproducible trace diagnostics, not evidence "
                "of scientific validity or of objective physical causation."
            ),
        }


def audit_stage12_operator_alerts(
    journal: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12OperatorAlertAudit:
    base = audit_export_bytes(
        journal, expected_head=expected_head, expected_count=expected_count,
    )
    charges: dict[tuple[int, str, int], tuple[int, dict]] = {}
    pending_charge_closure: tuple[int, str, int] | None = None
    diagnostics: set[tuple[int, str, int]] = set()
    deferred: set[tuple[int, str, int]] = set()
    pending: dict[tuple[int, str, int, str], dict[str, object]] = {}
    policy: str | None = None
    detector_version: str | None = None
    threshold: int | None = None
    diagnostic_window: int | None = None
    previous_step = 0
    observed_sample_count = 0
    streaks = {name: 0 for name in _WARNING_KEYS}
    firsts: dict[str, int | None] = {name: None for name in _WARNING_KEYS}
    counts = {name: 0 for name in _WARNING_KEYS}

    for index, raw in enumerate(journal.split(b"\n")):
        event = json.loads(raw)["causal_event"]
        kind = event.get("kind")
        if pending_charge_closure is not None:
            # The implementation's charge receipt is adjacent to its own
            # terminal publication/deferral, with no unrelated causal
            # occurrence allowed in between. A forged late receipt would
            # otherwise appear to satisfy charge accounting retrospectively.
            receipt_key = (
                event.get("t_monde"), event.get("attempt_ref"), event.get("cycle"),
            )
            if (kind not in (
                    "stage12_lived_diagnostics_published",
                    "stage12_lived_diagnostics_deferred",
                ) or receipt_key != pending_charge_closure):
                raise ValueError("Stage12 diagnostic receipt is not immediately after its debit")
            pending_charge_closure = None
        if pending and kind != "stage12_operator_alert":
            # Operator alerts are written immediately after the *paid*
            # diagnostic while its phase is open. Any intervening causal
            # event could hide a delayed/post-terminal forged warning.
            raise ValueError("missing operator alert before next causal event")
        if kind not in ("compute_charge", "stage12_lived_diagnostics_published",
                        "stage12_lived_diagnostics_deferred",
                        "stage12_operator_alert"):
            continue
        data = event.get("data")
        if (type(data) is not dict
                or event.get("emitter") != "stage4-runtime"
                or type(event.get("t_monde")) is not int
                or event["t_monde"] < 1
                or type(event.get("cycle")) is not int
                or event["cycle"] < 1
                or type(event.get("attempt_ref")) is not str
                or not event["attempt_ref"]):
            raise ValueError("noncanonical Stage12 operator alert provenance")
        key = (event["t_monde"], event["attempt_ref"], event["cycle"])
        if kind == "compute_charge":
            if data.get("operation") != "stage12_diagnostic_sample":
                continue
            if (data.get("module") != "metacognition_health"
                    or type(data.get("accepted")) is not bool
                    or type(data.get("requested_uc")) is not int
                    or data["requested_uc"] < 1
                    or key in charges):
                raise ValueError("invalid or duplicate charged Stage12 diagnostic")
            charges[key] = (index, data)
            pending_charge_closure = key
            continue
        if kind == "stage12_lived_diagnostics_deferred":
            previous_charge = charges.get(key)
            if (key in deferred or key in diagnostics
                    or previous_charge is None or previous_charge[0] >= index
                    or previous_charge[1]["accepted"] is not False
                    or type(previous_charge[1].get("reason")) is not str
                    or not previous_charge[1]["reason"]
                    or data.get("world_step") != key[0]
                    or data.get("diagnostic_incomplete") is not True
                    or data.get("reason") != previous_charge[1]["reason"]):
                raise ValueError("unmatched deferred Stage12 diagnostic charge")
            deferred.add(key)
            continue
        if kind == "stage12_lived_diagnostics_published":
            # Every alert is published immediately after the diagnostic
            # from which it was derived, before any later physical sample.
            if pending:
                raise ValueError("missing operator alert before the next lived sample")
            t, attempt, cycle = key
            if key in diagnostics or key in deferred or t <= previous_step:
                raise ValueError("duplicated or out-of-order lived warning step")
            diagnostics.add(key)
            charge = charges.get(key)
            if (charge is None or charge[0] >= index
                    or charge[1]["accepted"] is not True
                    or charge[1].get("reason") is not None
                    or type(data.get("charged_diagnostic_uc")) is not int
                    or data["charged_diagnostic_uc"] != charge[1]["requested_uc"]
                    or data.get("world_step") != t
                    or data.get("operator_only_diagnostic") is not True
                    or type(data.get("evidence_samples")) is not int):
                raise ValueError("operator warning lacks one paid lived diagnostic")
            current_version = data.get("operator_alert_policy_version")
            current_detector = data.get("diagnostic_policy_version")
            current_threshold = data.get("operator_alert_persistence_steps")
            current_window = data.get("diagnostic_window")
            if (type(current_version) is not str or not current_version
                    or type(current_detector) is not str or not current_detector
                    or type(current_threshold) is not int or current_threshold < 2
                    or type(current_window) is not int or current_window < 1):
                raise ValueError("invalid operator warning persistence policy")
            if policy is None:
                policy, detector_version, threshold, diagnostic_window = (
                    current_version, current_detector, current_threshold,
                    current_window,
                )
            elif (policy, detector_version, threshold, diagnostic_window) != (
                current_version, current_detector, current_threshold,
                current_window,
            ):
                raise ValueError("operator alert policy changed during one life")
            if data["evidence_samples"] != min(observed_sample_count + 1, current_window):
                raise ValueError("bounded diagnostic evidence counter is not reproducible")
            bias = data.get("attribution_bias")
            # A success/failure attribution still has no independently
            # attested lived verification pairs (#110). A forged non-null
            # pattern must not become an apparently valid operator alarm.
            if bias is not None:
                raise ValueError("unverified lived attribution diagnostic")
            states = {
                "stagnation": data.get("stagnation"),
                "reasoning_loop": data.get("reasoning_loop"),
                "low_context_entropy": data.get("low_context_entropy"),
                "attribution_bias": (
                    None if bias is None
                    else bias in ("self_serving_pattern", "self_blame_pattern")
                ),
            }
            if any(type(v) not in (bool, type(None)) for v in states.values()):
                raise ValueError("non-tristate lived Stage12 operator signal")
            gap = previous_step and t != previous_step + 1
            for signal in _WARNING_KEYS:
                if states[signal] is not True:
                    streaks[signal] = 0
                    firsts[signal] = None
                    continue
                if gap or streaks[signal] == 0:
                    streaks[signal] = 1
                    firsts[signal] = t
                elif streaks[signal] < threshold:
                    streaks[signal] += 1
                if (streaks[signal] == threshold
                        and t == firsts[signal] + threshold - 1):
                    expected = {
                        "schema": "stage12-persistent-operator-alert-v1",
                        "signal": signal,
                        "first_world_step": firsts[signal],
                        "world_step": t,
                        "consecutive_world_steps": threshold,
                        "policy_version": current_version,
                        "evidence_samples": data["evidence_samples"],
                        "operator_only_alert": True,
                        "diagnostic_policy_version": current_detector,
                    }
                    pending[(t, attempt, cycle, signal)] = expected
            previous_step = t
            observed_sample_count += 1
            continue
        # An alert must match the most recent paid diagnostic's exact
        # physical step and be present once, never after later evidence.
        t, attempt, cycle = key
        signal = data.get("signal")
        if type(signal) is not str or signal not in _WARNING_KEYS:
            raise ValueError("unknown Stage12 alert source signal")
        source_key = (t, attempt, cycle, signal)
        if not pending or next(iter(pending)) != source_key:
            raise ValueError("out-of-order or unexpected Stage12 operator alert")
        expected = pending.pop(source_key, None)
        if expected is None or data != expected:
            raise ValueError("unearned, duplicate or forged Stage12 operator alert")
        counts[signal] += 1

    if pending:
        raise ValueError("missing operator alert for persistent lived warning")
    if pending_charge_closure is not None:
        raise ValueError("unclosed Stage12 diagnostic charge")
    if set(charges) != diagnostics | deferred:
        raise ValueError("unclosed Stage12 diagnostic charge or missing deferral")
    return Stage12OperatorAlertAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        examined_samples=len(diagnostics), emitted_alerts=sum(counts.values()),
        counts_by_signal=counts, policy_version=policy,
        persistence_world_steps=threshold,
    )
