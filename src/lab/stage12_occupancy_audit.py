"""Independent offline verification of charged Stage12 S_t module occupancy.

The audit reads the exhaustive *technical export* only. It reconstructs
visible Gatekeeper selected references from earlier bus admission witnesses,
not a WorldBody oracle or a live cognitive instance. A valid hash chain by
itself does not certify the truth of a claimed occupancy metric.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import isclose
from typing import Mapping

from i0.config import MVP_PHASE1_PRODUCER_ORDER
from i0.modules.stage12_occupancy import module_occupancy_entropy
from .independent_journal_audit import audit_export_bytes


@dataclass(frozen=True, slots=True)
class Stage12OccupancyAudit:
    head_hash: str
    occurrences: int
    evaluated_cycles: int
    deferred_cycles: int
    charged_uc: int
    empty_st_cycles: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-st-occupancy-audit-v1",
            "head_hash": self.head_hash,
            "occurrences": self.occurrences,
            "evaluated_cycles": self.evaluated_cycles,
            "deferred_cycles": self.deferred_cycles,
            "charged_uc": self.charged_uc,
            "empty_st_cycles": self.empty_st_cycles,
            "provenance": "admitted_bus_to_retained_st_to_charged_receipt",
            "oracle_truth_verified": False,
        }


def audit_stage12_occupancy(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12OccupancyAudit:
    """Require a prior S_t and exactly one matching UC debit for every result.

    Successful samples represent real S_t versions, not new physical steps.
    Several consecutive S_t versions may occur within one physical step.
    """
    base = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count,
    )
    producers = tuple(MVP_PHASE1_PRODUCER_ORDER)
    emitter_by_ref: dict[str, str] = {}
    st: dict[tuple[int, str, int], tuple[int, str, dict[str, int], int]] = {}
    charges: dict[tuple[int, str, int], list[tuple[int, dict]]] = {}
    receipts: dict[tuple[int, str, int], list[tuple[int, str, dict]]] = {}

    for index, raw in enumerate(content.split(b"\n")):
        event = json.loads(raw)["causal_event"]
        kind = event.get("kind")
        if kind == "bus_message_admitted":
            if event.get("emitter") != "bus":
                raise ValueError("untrusted bus admission emitter")
            data = event.get("data")
            msg = data.get("message") if type(data) is dict else None
            payload = msg.get("payload") if type(msg) is dict else None
            if type(payload) is dict and "id" in payload:
                ref, emitter = payload["id"], msg.get("producer")
                if (type(ref) is not str or not ref
                        or type(emitter) is not str or emitter not in producers):
                    raise ValueError("invalid producer witness")
                prior = emitter_by_ref.get(ref)
                if prior is not None and prior != emitter:
                    raise ValueError("contribution changed producer ownership")
                emitter_by_ref[ref] = emitter
            continue

        if kind not in (
            "s_t_published", "compute_charge",
            "stage12_st_module_occupancy_published",
            "stage12_st_occupancy_deferred",
        ):
            continue
        data = event.get("data")
        t, attempt, cycle = (
            event.get("t_monde"), event.get("attempt_ref"), event.get("cycle"),
        )
        if (event.get("emitter") != "stage4-runtime"
                or type(t) is not int or t < 1
                or type(attempt) is not str or not attempt
                or type(cycle) is not int or cycle < 1
                or type(data) is not dict):
            raise ValueError("noncanonical S_t or Stage12 metric receipt")
        key = (t, attempt, cycle)

        if kind == "s_t_published":
            refs = data.get("competitive_refs")
            version = data.get("version")
            if (type(refs) is not list
                    or any(type(ref) is not str or not ref for ref in refs)
                    or len(refs) != len(set(refs))
                    or type(version) is not str or not version
                    or key in st):
                raise ValueError("ambiguous or invalid published S_t")
            counts = {producer: 0 for producer in producers}
            for ref in refs:
                emitter = emitter_by_ref.get(ref)
                if emitter not in counts:
                    raise ValueError("S_t reference lacks earlier admitted producer")
                counts[emitter] += 1
            st[key] = (index, version, counts, len(refs))
        elif kind == "compute_charge":
            if data.get("operation") != "stage12_occupancy_entropy":
                continue
            if data.get("module") != "metacognition_health":
                raise ValueError("Stage12 occupancy charged to the wrong owner")
            if (type(data.get("requested_uc")) is not int
                    or data["requested_uc"] < 1
                    or type(data.get("accepted")) is not bool):
                raise ValueError("invalid Stage12 occupancy UC debit")
            if data["accepted"] and data.get("reason") is not None:
                raise ValueError("accepted occupancy charge gives refusal reason")
            charges.setdefault(key, []).append((index, data))
        else:
            receipts.setdefault(key, []).append((index, kind, data))

    if set(charges) != set(receipts):
        raise ValueError("missing Stage12 occupancy debit or result")
    evaluated = deferred = charged_uc = empty_st = 0
    fixed_cost: int | None = None
    fixed_threshold: float | None = None
    for key, rows in charges.items():
        publications = receipts[key]
        if len(rows) != 1 or len(publications) != 1 or key not in st:
            raise ValueError("ambiguous or missing Stage12 occupancy source")
        (sindex, st_version, source_counts, source_count) = st[key]
        cindex, debit = rows[0]
        rindex, kind, data = publications[0]
        if sindex >= cindex or cindex >= rindex:
            raise ValueError("S_t occupancy receipt predates source or debit")
        if data.get("st_version") != st_version or data.get("world_step") != key[0]:
            raise ValueError("occupancy receipt references incorrect S_t")
        if debit["accepted"]:
            if kind != "stage12_st_module_occupancy_published":
                raise ValueError("accepted occupancy charge lacks measurement")
            if (data.get("schema") != "stage12-st-module-occupancy-v1"
                    or data.get("operator_only_diagnostic") is not True
                    or type(data.get("charged_uc")) is not int
                    or data["charged_uc"] != debit["requested_uc"]
                    or data.get("module_universe") != list(producers)
                    or type(data.get("module_universe_size")) is not int
                    or data["module_universe_size"] != len(producers)):
                raise ValueError("uncanonical or uncharged module occupancy")
            expected_counts = {p: n for p, n in source_counts.items() if n}
            if data.get("module_counts") != expected_counts:
                raise ValueError("module occupancy diverges from admitted S_t")
            warning = data.get("warning_fraction")
            if type(warning) not in (int, float):
                raise ValueError("invalid occupancy threshold")
            reference = module_occupancy_entropy(
                source_counts, warning_fraction=warning,
                module_universe_size=len(producers),
            )
            if (data.get("status") != reference.status
                    or data.get("low_entropy") is not reference.low_entropy
                    or type(data.get("occupied_slots")) is not int
                    or data["occupied_slots"] != source_count
                    or type(data.get("distinct_modules")) is not int
                    or data["distinct_modules"] != reference.distinct_modules):
                raise ValueError("forged S_t occupancy classification")
            received = data.get("normalized_entropy")
            expected = reference.normalized_entropy
            if ((expected is None and received is not None)
                    or (expected is not None and (
                        type(received) not in (float, int)
                        or not isclose(received, expected, rel_tol=0, abs_tol=1e-12)
                    ))):
                raise ValueError("incorrect normalized occupancy entropy")
            if fixed_threshold is None:
                fixed_threshold = warning
            elif fixed_threshold != warning:
                raise ValueError("occupancy threshold changed within a life")
            if fixed_cost is None:
                fixed_cost = debit["requested_uc"]
            elif fixed_cost != debit["requested_uc"]:
                raise ValueError("occupancy UC cost changed within a life")
            evaluated += 1
            charged_uc += debit["requested_uc"]
            if reference.status == "unavailable_empty_st":
                empty_st += 1
        else:
            if (kind != "stage12_st_occupancy_deferred"
                    or data.get("policy_version") != "stage12-st-module-occupancy-v1"
                    or data.get("diagnostic_incomplete") is not True
                    or type(debit.get("reason")) is not str
                    or not debit["reason"]
                    or debit["reason"] != data.get("reason")):
                raise ValueError("refused occupancy charge lacks exact deferral")
            deferred += 1
    return Stage12OccupancyAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        evaluated_cycles=evaluated, deferred_cycles=deferred,
        charged_uc=charged_uc, empty_st_cycles=empty_st,
    )
