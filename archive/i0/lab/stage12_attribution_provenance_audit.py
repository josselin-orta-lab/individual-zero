"""Independent issue-110 attribution-source gate.

This read-only operator audit distinguishes precommitted lived goal outcomes
from P-47 prediction comparisons. No cognitive source currently produces an
independent self/world *goal-result responsibility* judgement. Therefore even
an internally consistent technical journal must not calibrate attribution_bias.
Never load I0 cognition, WorldBody, Oracle or Bench here.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .independent_journal_audit import audit_export_bytes
from .stage12_goal_progress_audit import audit_stage12_goal_progress
from .stage12_diagnostic_audit import audit_stage12_diagnostics


@dataclass(frozen=True)
class Stage12AttributionProvenanceAudit:
    head_hash: str
    occurrences: int
    verified_successes: int
    verified_failures: int
    unknown_results: int
    p47_comparisons: int
    self_compatible: int
    world_justified: int
    uncertain: int
    admitted_pairs: int
    unavailable_diagnostics: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-issue110-attribution-provenance-v1",
            **vars(self),
            "independent_subjective_agency_contract": False,
            "bias_calibration_supported": False,
            "physical_truth_verified": False,
            "operator_accepted": False,
        }


def _verify_reported_p47(
    *, index: int, event: dict, commands: dict, transitions: dict,
    captures: dict, seen_sent: set[int], seen_observed: set[int],
) -> str:
    """Validate receipt lineage, *not* the unknown physical cause.

    The journal does not expose the complete frozen P-47 prediction inputs
    as an independently attested ground truth. Consequently a structurally
    supported comparison is still NOT an admissible Stage12 agency judgement.
    """
    data = event.get("data")
    t = event.get("t_monde")
    attempt = event.get("attempt_ref")
    if (event.get("emitter") != "stage4-runtime"
            or type(t) is not int or t < 2
            or type(attempt) is not str or not attempt
            or type(data) is not dict
            or set(data) != {
                "option_ref", "sent_t_monde", "observed_t_monde",
                "status", "attribution", "effects",
            }):
        raise ValueError("P-47 comparison lacks canonical producer or schema")
    sent = data["sent_t_monde"]
    observed = data["observed_t_monde"]
    if (type(sent) is not int or sent < 1 or type(observed) is not int
            or observed != t or sent >= observed):
        raise ValueError("P-47 comparison has invalid observation time")
    if sent in seen_sent or t in seen_observed:
        raise ValueError("P-47 comparison duplicated sent or observed step")
    option = data["option_ref"]
    if option is not None and (type(option) is not str or not option):
        raise ValueError("P-47 comparison has invalid option reference")
    source_captures = captures.get((t, attempt), [])
    if len(source_captures) != 1 or source_captures[0] >= index:
        raise ValueError("P-47 comparison lacks preceding lived perception")
    prior_cmd = commands.get(sent, [])
    prior_transition = transitions.get(sent, [])
    if (len(prior_cmd) != 1 or len(prior_transition) != 1
            or not prior_cmd[0][0] < prior_transition[0][0] < index
            or prior_cmd[0][1].get("attempt_ref") !=
               prior_transition[0][1].get("attempt_ref")
            or prior_cmd[0][1].get("emitter") != "action_control"):
        raise ValueError("P-47 comparison lacks an executed prior command")
    status = data["status"]
    attribution = data["attribution"]
    effects = data["effects"]
    if (status not in ("conforming", "nonconforming", "indeterminable")
            or attribution not in (
                "self_compatible", "world_justified", "uncertain"
            )
            or type(effects) is not list or not effects
            or any(type(e) is not dict
                   or e.get("status") not in (
                       "conforming", "nonconforming", "indeterminable",
                       "expected_effect_missing",
                   ) for e in effects)):
        raise ValueError("invalid P-47 comparison effect and class")
    statuses = [e["status"] for e in effects]
    if (
        (status == "conforming"
         and (not all(s == "conforming" for s in statuses)
              or attribution != "self_compatible"))
        or (status == "nonconforming"
            and ("nonconforming" not in statuses
                 or attribution not in ("world_justified", "uncertain")))
        or (status == "indeterminable"
            and (any(s == "nonconforming" for s in statuses)
                 or attribution != "uncertain"))
    ):
        raise ValueError("P-47 comparison status/attribution contradiction")
    seen_sent.add(sent)
    seen_observed.add(t)
    return attribution


def audit_stage12_attribution_provenance(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12AttributionProvenanceAudit:
    """Audit full-life source receipts; refuse semantic promotion of P-47."""
    anchors = dict(expected_head=expected_head, expected_count=expected_count)
    base = audit_export_bytes(content, **anchors)
    goal = audit_stage12_goal_progress(content, **anchors)
    diagnostic = audit_stage12_diagnostics(content, **anchors)
    if (base.head_hash != goal.head_hash
            or base.head_hash != diagnostic.head_hash):
        raise ValueError("attribution audit custody mismatch")

    records = [json.loads(line)["causal_event"]
               for line in content.split(b"\n")]
    commands: dict[int, list[tuple[int, dict]]] = {}
    transitions: dict[int, list[tuple[int, dict]]] = {}
    captures: dict[tuple[int, str], list[int]] = {}
    for i, event in enumerate(records):
        kind = event.get("kind")
        t = event.get("t_monde")
        if kind == "command_experienced" and event.get("emitter") == "action_control":
            commands.setdefault(t, []).append((i, event))
        elif kind == "world_transition_experienced":
            transitions.setdefault(t, []).append((i, event))
        elif kind == "perceptual_capture":
            captures.setdefault((t, event.get("attempt_ref")), []).append(i)

    comparisons = {"self_compatible": 0, "world_justified": 0, "uncertain": 0}
    published = 0
    seen_sent: set[int] = set()
    seen_observed: set[int] = set()
    for index, event in enumerate(records):
        kind, data = event.get("kind"), event.get("data")
        if kind == "stage12_lived_diagnostics_published":
            published += 1
            if not isinstance(data, dict) or data.get("attribution_bias") is not None:
                raise ValueError("unverified lived attribution bias claim")
            if any(key in data for key in (
                "outcome", "agency", "attribution_ref", "verification_origin",
                "attribution_pairs", "verified_successes", "verified_failures",
            )):
                raise ValueError("uncontracted attribution source")
        elif kind == "agency_comparison":
            label = _verify_reported_p47(
                index=index, event=event, commands=commands,
                transitions=transitions, captures=captures,
                seen_sent=seen_sent, seen_observed=seen_observed,
            )
            comparisons[label] += 1
        elif type(kind) is str and (
            kind.startswith("stage12_attribution_")
            or kind.startswith("stage12_subjective_agency")
        ):
            raise ValueError("uncontracted subjective agency source")
    if published != diagnostic.diagnostic_samples:
        raise ValueError("diagnostic receipts missing")
    return Stage12AttributionProvenanceAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        verified_successes=goal.verified_strict_gains,
        verified_failures=goal.verified_no_gains,
        unknown_results=goal.unavailable,
        p47_comparisons=sum(comparisons.values()),
        self_compatible=comparisons["self_compatible"],
        world_justified=comparisons["world_justified"],
        uncertain=comparisons["uncertain"],
        admitted_pairs=0, unavailable_diagnostics=published,
    )
