"""Independent, fail-closed Stage12 diagnostic receipt audit.

The technical hash-chain audit is necessary but cannot prove a diagnostic
observation actually consumed a metacognitive UC debit. This read-only
operator-side verifier pairs each Stage12 diagnostic result with exactly one
earlier charge on the same Scheduler attempt and cognitive cycle. It never
constructs I0, accesses Oracle/Bench or reconstructs an executable life.

Until individual lived outcome/agency evidence is journaled and audited by
a versioned contract, a non-null attribution-bias diagnosis is *unsupported*.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Mapping

from .independent_journal_audit import audit_export_bytes


@dataclass(frozen=True, slots=True)
class Stage12DiagnosticAudit:
    head_hash: str
    occurrences: int
    world_steps_closed: int
    diagnostic_samples: int
    deferred_samples: int
    charged_uc: int
    policy_version: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-diagnostic-audit-v1",
            "verified": True,
            "head_hash": self.head_hash,
            "occurrences": self.occurrences,
            "world_steps_closed": self.world_steps_closed,
            "diagnostic_samples": self.diagnostic_samples,
            "deferred_samples": self.deferred_samples,
            "charged_uc": self.charged_uc,
            "policy_version": self.policy_version,
            "attribution_verification": "unavailable_no_audited_lived_pairs",
            "physical_truth_verified": False,
        }


def audit_stage12_diagnostics(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12DiagnosticAudit:
    """Audit one immutable full-life export, never count speculative results.

    All accepted or refused `stage12_diagnostic_sample` debit attempts must
    have one correctly ordered publication or explicit deferral. One accepted
    sample per world step, no extra source observations and no arbitrary
    attribution-label promotion are permitted. The independent full-journal
    auditor remains responsible for chain, WorldBody step/death and isolation.
    """
    base = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count,
    )
    charges: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    receipts: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    seen_steps: set[int] = set()
    policy_version: str | None = None
    charged_cost: int | None = None
    most_recent_samples = 0
    observed_accepted_samples = 0
    diagnostic_window: int | None = None
    legacy_counter_mode = False
    previous_sample_step = 0

    for index, raw in enumerate(content.split(b"\n")):
        event = json.loads(raw)["causal_event"]
        kind = event.get("kind")
        if kind not in (
            "compute_charge", "stage12_lived_diagnostics_published",
            "stage12_lived_diagnostics_deferred",
        ):
            continue
        data = event.get("data")
        if kind == "compute_charge":
            if not isinstance(data, dict) or data.get("operation") != "stage12_diagnostic_sample":
                continue
            if data.get("module") != "metacognition_health":
                raise ValueError("Stage12 diagnostic charged to the wrong owner")
        t, attempt, cycle = (
            event.get("t_monde"), event.get("attempt_ref"), event.get("cycle")
        )
        if (event.get("emitter") != "stage4-runtime"
                or type(t) is not int or t < 1
                or type(attempt) is not str or not attempt
                or type(cycle) is not int or cycle < 1
                or type(data) is not dict):
            raise ValueError("Stage12 receipt lacks canonical cognitive origin")
        key = (t, attempt, cycle)
        if kind == "compute_charge":
            cost = data.get("requested_uc")
            if (type(cost) is not int or cost < 1
                    or type(data.get("accepted")) is not bool):
                raise ValueError("Stage12 diagnostic debit has invalid UC semantics")
            if data["accepted"] and data.get("reason") is not None:
                raise ValueError("accepted diagnostic debit reports refusal")
            charges.setdefault(key, []).append((index, data))
        else:
            if data.get("world_step") != t:
                raise ValueError("Stage12 diagnostic publication has wrong physical time")
            receipts.setdefault(key, []).append((index, event))
            if kind == "stage12_lived_diagnostics_published":
                if t in seen_steps:
                    raise ValueError("duplicate Stage12 physical observation")
                seen_steps.add(t)
                if (data.get("operator_only_diagnostic") is not True
                        or type(data.get("charged_diagnostic_uc")) is not int
                        or data["charged_diagnostic_uc"] < 1
                        or type(data.get("progress_observed")) is not bool):
                    raise ValueError("fabricated or uncharged Stage12 diagnostic")
                for field in ("stagnation", "reasoning_loop", "low_context_entropy"):
                    if data.get(field) is not None and type(data[field]) is not bool:
                        raise ValueError("invalid tri-state metacognitive diagnosis")
                if data.get("attribution_bias") is not None:
                    # At present the live runtime does not publish auditable
                    # unique outcome/agency pair provenance. No source-backed
                    # non-null label can be verified, so fail closed.
                    raise ValueError("unverified lived attribution bias claim")
                # The live detector exposes the number in its *bounded*
                # evidence window, not a lifetime counter. Old v1.3.1
                # exports without diagnostic_window remain verifiable only
                # until the first plateau; the auditor must never infer a
                # smaller window from a potentially forged counter.
                supplied_window = data.get("diagnostic_window")
                if supplied_window is None:
                    if diagnostic_window is not None:
                        raise ValueError("diagnostic window disappeared within one life")
                    legacy_counter_mode = True
                    expected_count = most_recent_samples + 1
                else:
                    if (type(supplied_window) is not int or supplied_window < 1
                            or legacy_counter_mode):
                        raise ValueError("invalid or mixed diagnostic window contract")
                    if diagnostic_window is None:
                        diagnostic_window = supplied_window
                    elif diagnostic_window != supplied_window:
                        raise ValueError("diagnostic window changed within one life")
                    expected_count = min(observed_accepted_samples + 1, diagnostic_window)
                count = data.get("evidence_samples")
                if type(count) is not int or count != expected_count:
                    raise ValueError("metacognitive diagnostic sample count drift")
                if t <= previous_sample_step:
                    raise ValueError("Stage12 diagnostic world step did not advance")
                most_recent_samples = count
                observed_accepted_samples += 1
                previous_sample_step = t
                version = data.get("diagnostic_policy_version")
                if type(version) is not str or not version.strip():
                    raise ValueError("unversioned Stage12 diagnosis")
                if policy_version is None:
                    policy_version = version
                elif policy_version != version:
                    raise ValueError("detector policy changed within one life")
            else:
                if data.get("diagnostic_incomplete") is not True:
                    raise ValueError("refused diagnostic charge reported as complete")

    if set(charges) != set(receipts):
        raise ValueError("missing diagnostic charge or closure")
    successful = refused = total_uc = 0
    for key, cs in charges.items():
        rs = receipts[key]
        if len(cs) != 1 or len(rs) != 1:
            raise ValueError("ambiguous or duplicate Stage12 diagnostic debit")
        cindex, charge = cs[0]
        rindex, receipt = rs[0]
        if cindex >= rindex:
            raise ValueError("Stage12 diagnostic receipt predates its compute charge")
        kind = receipt["kind"]
        d = receipt["data"]
        if charge["accepted"]:
            if kind != "stage12_lived_diagnostics_published":
                raise ValueError("accepted diagnostic debit lacks one lived sample")
            if d["charged_diagnostic_uc"] != charge["requested_uc"]:
                raise ValueError("Stage12 diagnostic cost mismatch")
            if charged_cost is None:
                charged_cost = charge["requested_uc"]
            elif charged_cost != charge["requested_uc"]:
                raise ValueError("unversioned change of Stage12 diagnostic UC cost")
            total_uc += charge["requested_uc"]
            successful += 1
        else:
            if (kind != "stage12_lived_diagnostics_deferred"
                    or type(charge.get("reason")) is not str
                    or not charge["reason"]
                    or d.get("reason") != charge["reason"]):
                raise ValueError("refused diagnostic debit lacks matching deferral")
            refused += 1

    return Stage12DiagnosticAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        world_steps_closed=base.world_steps_closed,
        diagnostic_samples=successful, deferred_samples=refused,
        charged_uc=total_uc, policy_version=policy_version,
    )
