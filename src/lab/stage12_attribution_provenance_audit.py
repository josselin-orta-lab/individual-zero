"""Independent issue-110 provenance gate; never convert P-47 into objective agency."""
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
        }


def audit_stage12_attribution_provenance(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12AttributionProvenanceAudit:
    anchors = dict(expected_head=expected_head, expected_count=expected_count)
    base = audit_export_bytes(content, **anchors)
    goal = audit_stage12_goal_progress(content, **anchors)
    diag = audit_stage12_diagnostics(content, **anchors)
    if base.head_hash != goal.head_hash or base.head_hash != diag.head_hash:
        raise ValueError("attribution audit custody mismatch")
    comparisons = {"self_compatible": 0, "world_justified": 0, "uncertain": 0}
    published = 0
    for line in content.split(b"\n"):
        event = json.loads(line)["causal_event"]
        kind, data = event.get("kind"), event.get("data")
        if kind == "stage12_lived_diagnostics_published":
            published += 1
            if not isinstance(data, dict) or data.get("attribution_bias") is not None:
                raise ValueError("unsupported attribution diagnosis")
            if any(key in data for key in (
                "outcome", "agency", "attribution_ref", "verification_origin",
                "attribution_pairs", "verified_successes", "verified_failures",
            )):
                raise ValueError("uncontracted attribution source")
        elif kind == "agency_comparison":
            if not isinstance(data, dict) or data.get("attribution") not in comparisons:
                raise ValueError("unrecognized P-47 source semantics")
            comparisons[data["attribution"]] += 1
        elif kind in (
            "stage12_attribution_pair_admitted",
            "stage12_subjective_agency_judgement",
            "stage12_attribution_evidence_verified",
        ):
            raise ValueError("uncontracted subjective agency source")
    if published != diag.diagnostic_samples:
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
