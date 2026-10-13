"""Standalone GA-06 semantic pair verifier and bounded detector recomputation.

A rehashed journal is not physical truth. Reconstruct *both* independently
recorded first-person and goal-progress sources, the paid join, and diagnostic
application without importing I0, WorldBody, Oracle or Bench.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .independent_journal_audit import audit_export_bytes
from .stage12_goal_progress_audit import audit_stage12_goal_progress, _number
from .stage12_first_person_agency_audit import audit_stage12_first_person_agency

_PAIR = "stage12-goal-outcome-agency-pair-v1"


@dataclass(frozen=True, slots=True)
class Stage12AttributionPairAudit:
    head_hash: str
    occurrences: int
    admitted_pairs: int
    deferred_joins: int
    applied_pairs: int
    missed_pairs: int
    join_uc: int
    rejected_join_uc: int
    # (world step, admitted output or None) for paid diagnostic samples.
    diagnostic_labels: tuple[tuple[int, str | None], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-outcome-agency-pair-audit-v1",
            **{k: getattr(self, k) for k in self.__dataclass_fields__
               if k != "diagnostic_labels"},
            "diagnostic_labels": [
                {"world_step": t, "attribution_bias": label}
                for t, label in self.diagnostic_labels
            ],
            "causal_truth_established": False,
        }


def audit_stage12_attribution_pairs(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12AttributionPairAudit:
    anchors = dict(expected_head=expected_head, expected_count=expected_count)
    base = audit_export_bytes(content, **anchors)
    progress = audit_stage12_goal_progress(content, **anchors)
    agency = audit_stage12_first_person_agency(content, **anchors)
    if base.head_hash != progress.head_hash or base.head_hash != agency.head_hash:
        raise ValueError("attribution pair audit source custody mismatch")
    rows = [json.loads(v) for v in content.split(b"\n")]
    goals = {}
    followups = {}
    commitments = {}
    judgements = {}
    charge_by = {}
    diagnostics = []
    deferred_samples = {}
    missed = {}
    for i, row in enumerate(rows):
        e = row["causal_event"]
        kind = e.get("kind")
        data = e.get("data")
        t, attempt, cycle = e.get("t_monde"), e.get("attempt_ref"), e.get("cycle")
        if kind == "stage12_goal_progress_preregistered":
            goals[row["event_id"]] = (i, data, e)
        elif kind == "stage12_goal_progress_followup":
            followups[row["event_id"]] = (i, data, e)
        elif kind == "stage12_goal_agency_precommitted":
            commitments[data["assessment_ref"]] = (i, data, e)
        elif kind == "stage12_goal_agency_judgement":
            judgements[row["event_id"]] = (i, data, e)
        elif (kind == "compute_charge" and isinstance(data, dict)
              and data.get("operation") == "stage12_attribution_join"):
            charge_by.setdefault((t, attempt, cycle), []).append((i, data))
        elif kind == "stage12_lived_diagnostics_published":
            diagnostics.append((i, data, e))
        elif kind == "stage12_lived_diagnostics_deferred":
            deferred_samples[(t, attempt, cycle)] = i
        elif kind == "stage12_attribution_sample_unavailable":
            missed[(t, attempt, cycle)] = (i, data)
    pairs = {}
    deferred_joins = {}
    source_intents = set()
    source_judgements = set()
    join_uc = rejected_uc = 0
    for i, row in enumerate(rows):
        e = row["causal_event"]
        kind = e.get("kind")
        if kind not in ("stage12_attribution_pair_admitted",
                        "stage12_attribution_join_deferred"):
            continue
        data = e.get("data")
        t, attempt, cycle = e.get("t_monde"), e.get("attempt_ref"), e.get("cycle")
        if (e.get("emitter") != "stage4-runtime"
                or type(t) is not int or type(cycle) is not int
                or type(attempt) is not str or not attempt
                or type(data) is not dict):
            raise ValueError("uncontracted Stage12 join receipt")
        candidates = charge_by.get((t, attempt, cycle), [])
        if len(candidates) != 1 or candidates[0][0] >= i:
            raise ValueError("attribution join missing unique prior charged work")
        cindex, charge = candidates[0]
        if (charge.get("module") != "metacognition_health"
                or type(charge.get("requested_uc")) is not int
                or charge["requested_uc"] < 1
                or type(charge.get("accepted")) is not bool):
            raise ValueError("invalid metacognitive attribution UC receipt")
        intent_ref = data.get("intent_ref")
        followup_ref = data.get("goal_followup_ref")
        judgement_ref = data.get("agency_judgement_ref")
        if (type(intent_ref) is not str or not intent_ref
                or type(followup_ref) is not str or followup_ref not in followups
                or type(judgement_ref) is not str or judgement_ref not in judgements
                or intent_ref not in goals):
            raise ValueError("attribution join requires both original verified sources")
        fi, followup, fe = followups[followup_ref]
        ji, judgement, je = judgements[judgement_ref]
        gi, goal, ge = goals[intent_ref]
        if (not gi < fi < i or not ji < i
                or fi >= cindex or ji >= cindex
                or fe.get("t_monde") != t or je.get("t_monde") != t
                or fe.get("attempt_ref") != attempt
                or je.get("attempt_ref") != attempt
                or followup.get("intent_ref") != intent_ref
                or judgement.get("intent_ref") != intent_ref
                or judgement.get("sent_world_step") != goal.get("sent_world_step")
                or judgement.get("observed_world_step") != t):
            raise ValueError("attribution join cross-source timeline mismatch")
        if (followup.get("criterion_outcome") not in ("success", "failure")
                or judgement.get("subjective_agency") not in ("self", "world")
                or judgement.get("cue_ref") is None):
            raise ValueError("unknown or unproduced result cannot enter attribution")
        if intent_ref in source_intents or judgement_ref in source_judgements:
            raise ValueError("reused lived outcome or subjective agency source")
        if kind == "stage12_attribution_join_deferred":
            if (charge["accepted"] or not isinstance(charge.get("reason"), str)
                    or data.get("reason") != charge["reason"]):
                raise ValueError("false attribution join UC refusal")
            deferred_joins[(t, attempt, cycle)] = i
            rejected_uc += charge["requested_uc"]
        else:
            if (not charge["accepted"] or data.get("version") != _PAIR
                    or data.get("observed_world_step") != t
                    or data.get("life_id") != judgement.get("life_id")
                    or data.get("life_id") is None
                    or data.get("outcome") != followup["criterion_outcome"]
                    or data.get("agency") != judgement["subjective_agency"]
                    or data.get("agency_assessment_ref")
                       != judgement["assessment_ref"]):
                raise ValueError("unsupported independent attribution pair claim")
            if (data["agency_assessment_ref"] not in commitments
                    or commitments[data["agency_assessment_ref"]][1].get("life_id")
                       != data["life_id"]):
                raise ValueError("attribution pair forged cognitive source identity")
            pairs[row["event_id"]] = (i, data, e)
            join_uc += charge["requested_uc"]
        source_intents.add(intent_ref)
        source_judgements.add(judgement_ref)
    if (sum(map(len, charge_by.values()))
            != len(pairs) + len(deferred_joins)):
        raise ValueError("orphaned or duplicated Stage12 attribution join charge")
    seen_pair_refs = set()
    sample_labels = []
    window_entries = []
    min_threshold = None
    effect_threshold = None
    last_window = None
    last_diagnostic_step = 0
    for i, data, e in diagnostics:
        t, attempt, cycle = (
            e["t_monde"], e["attempt_ref"], e["cycle"],
        )
        if (type(t) is not int or t <= last_diagnostic_step):
            raise ValueError("attribution diagnostic physical ordering invalid")
        last_diagnostic_step = t
        pair_ref = data.get("attribution_pair_ref")
        if pair_ref is not None and (
            pair_ref not in pairs or pair_ref in seen_pair_refs
        ):
            raise ValueError("forged or duplicated diagnostic attribution pair")
        if pair_ref is not None:
            prior_index, pair, pair_event = pairs[pair_ref]
            if (prior_index >= i or pair_event["t_monde"] != t - 1):
                raise ValueError("diagnostic cannot apply a late or same-step attribution")
            seen_pair_refs.add(pair_ref)
        if "attribution_pair_ref" in data:
            size = data.get("diagnostic_window")
            minimum = data.get("bias_min_outcomes_each")
            threshold = _number(data.get("attribution_bias_threshold"))
            if (type(size) is not int or size < 1
                    or type(minimum) is not int or minimum < 1
                    or threshold is None
                    or not 0 <= threshold <= 1):
                raise ValueError("invalid versioned attribution detector thresholds")
            if min_threshold is None:
                min_threshold, effect_threshold, last_window = minimum, threshold, size
            elif (min_threshold, effect_threshold, last_window) != (minimum, threshold, size):
                raise ValueError("attribution detector parameters changed midlife")
            window_entries.append(pair_ref)
            window_entries = window_entries[-size:]
            included = [pairs[ref][1] for ref in window_entries if ref is not None]
            success = [v for v in included if v["outcome"] == "success"]
            failure = [v for v in included if v["outcome"] == "failure"]
            label = None
            if len(success) >= minimum and len(failure) >= minimum:
                self_success = sum(p["agency"] == "self" for p in success) / len(success)
                self_failure = sum(p["agency"] == "self" for p in failure) / len(failure)
                delta = self_success - self_failure
                label = ("self_serving_pattern" if delta >= threshold
                         else "self_blame_pattern" if delta <= -threshold
                         else "no_detected_pattern")
            if (data.get("verified_successes") != len(success)
                    or data.get("verified_failures") != len(failure)
                    or data.get("attribution_bias") != label):
                raise ValueError("attribution detector output disagrees with verified pairs")
        else:
            if pair_ref is not None or data.get("attribution_bias") is not None:
                raise ValueError("legacy diagnostic cannot claim unverified attribution")
            label = None
        sample_labels.append((t, label))
    unavailable_refs = set()
    for key, (i, data) in missed.items():
        if (key not in deferred_samples or i <= deferred_samples[key]
                or type(data) is not dict
                or data.get("reason") != "diagnostic_uc_refused"
                or data.get("pair_ref") not in pairs
                or data["pair_ref"] in unavailable_refs or data["pair_ref"] in seen_pair_refs
                or pairs[data["pair_ref"]][2]["t_monde"] != key[0] - 1):
            raise ValueError("false or repeated missing attribution sample")
        unavailable_refs.add(data["pair_ref"])
    # Pending from last physical step is legal: no postmortem update.
    for ref, (_i, _data, event) in pairs.items():
        if (ref not in seen_pair_refs and ref not in unavailable_refs
                and base.world_steps_closed > event["t_monde"]):
            raise ValueError("admitted pair missing next-step diagnostic admission")
    return Stage12AttributionPairAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        admitted_pairs=len(pairs), deferred_joins=len(deferred_joins),
        applied_pairs=len(seen_pair_refs),
        missed_pairs=len(unavailable_refs),
        join_uc=join_uc, rejected_join_uc=rejected_uc,
        diagnostic_labels=tuple(sample_labels),
    )
