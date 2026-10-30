"""Read-only A2-R native geographic offer to Stage11 intrinsic occurrence join.

Only authentic inputs from three independent cold M11 audits and a source
pinned birth are permitted by caller. This join proves no Action Control
admissibility, no Q causal mediation, and no L3.
"""
from __future__ import annotations
from math import isfinite

_GEO="A2R_PHYSICAL_GEOGRAPHIC_VISIT_REPLAY_NOT_L3"
_INTRINSIC="A2R_STAGE11_PARTIAL_SOURCE_INTRINSIC_ARITHMETIC_NOT_L3"
_JOIN="A2R_STAGE11_SOURCE_FORMULA_JOIN_NOT_L3"
_ALLOWED=("exploration:p48_geographic","exploration:p48_instrumental")


def _key(value):
    if (type(value) is not dict or
            type(value.get("step")) is not int or value["step"] < 1 or
            type(value.get("cycle")) is not int or value["cycle"] < 1 or
            type(value.get("option")) is not str or not value["option"]):
        raise ValueError("invalid native event key")
    return (value["step"],value["cycle"],value["option"])


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("invalid native event count")
    return value


def reconcile_geographic_intrinsic(*, geography, intrinsic, stage11_join):
    """Join source-born frontier magnitude to a separately replayed offer.

    Matching an unvisited destination is NOT proof it is safe/passable.
    Missing Stage11 history remains quarantined, even for matching formulas.
    """
    if any(type(x) is not dict for x in (geography,intrinsic,stage11_join)):
        raise ValueError("cold M11 evidence required")
    if (geography.get("scope") != _GEO or intrinsic.get("scope") != _INTRINSIC
            or stage11_join.get("scope") != _JOIN):
        raise ValueError("cold M11 audit version mismatch")
    for x in (geography,intrinsic,stage11_join):
        if (x.get("study_admissible") is not False or
                x.get("preregistered_mechanism_exposed") is not False or
                x.get("general_L3") != "NOT_ESTABLISHED"):
            raise ValueError("technical proof falsely promoted to L3")
    if (geography.get("historic_visits_match_sealed_final_owner") is not True
            or geography.get("per_neighbor_creature_absence_attested") is not False
            or geography.get("action_control_admissibility_replayed") is not False
            or geography.get("all_intrinsic_owner_history_replayed") is not False
            or intrinsic.get("all_stage11_intrinsic_state_independently_replayed") is not False
            or intrinsic.get("frontier_admissibility_independently_replayed") is not False
            or stage11_join.get("all_stage11_intrinsic_causes_proven") is not False):
        raise ValueError("expected unproven native causal history was promoted")
    offers=geography.get("frontier_occurrences")
    verified=intrinsic.get("intrinsic_magnitude_verified")
    missing=intrinsic.get("unreconstructed_owner_intrinsic")
    if any(type(x) is not list for x in (offers,verified,missing)):
        raise ValueError("truncated native occurrence list")
    if (_count(geography.get("direct_frontier_candidates_checked")) != len(offers)
            or _count(intrinsic.get("direct_frontier_intrinsic_recomputed")) != len(verified)
            or _count(intrinsic.get("unreconstructed_owner_intrinsic_occurrences")) != len(missing)):
        raise ValueError("native occurrence roster mismatch")
    total=_count(intrinsic.get("stage11_intrinsic_occurrences"))
    if (total != len(verified)+len(missing)
            or _count(stage11_join.get("stage11_original_events_reconciled")) != total
            or _count(stage11_join.get("direct_frontier_formula_checked_not_novelty")) != len(verified)
            or _count(stage11_join.get("owner_history_missing_occurrences")) != len(missing)
            or _count(stage11_join.get("still_quarantined_without_frontier_admissibility")) != total):
        raise ValueError("Stage11 census differs from source-born owner")
    indexed={}
    cue_count=0
    for row in offers:
        key=_key(row)
        if (key in indexed or
                not key[2].startswith("option:geographic:frontier:") or
                row.get("not_previously_registered") is not True or
                type(row.get("perceptual_passability_checked")) is not bool):
            raise ValueError("duplicated or falsified physical frontier")
        indexed[key]=row
        cue_count+=row["perceptual_passability_checked"]
    if (_count(geography.get("direct_frontier_passability_cues_checked")) != cue_count
            or _count(geography.get("direct_frontier_passability_cues_absent")) != len(offers)-cue_count):
        raise ValueError("passability cue count differs from raw M11")
    matched={}
    for row in verified:
        key=_key(row)
        mag,score=row.get("recomputed_intrinsic"),row.get("recomputed_evidence")
        if (key not in indexed or key in matched or
                row.get("producer") not in _ALLOWED or
                type(mag) not in (int,float) or not isfinite(mag) or not 0 < mag <= 1 or
                type(score) not in (int,float) or not isfinite(score) or not -1 <= score <= 1):
            raise ValueError("source-born intrinsic frontier not grounded in physical M11")
        matched[key]=row
    seen=set(matched)
    for row in missing:
        key=_key(row)
        if (key in seen or type(row.get("reason")) is not str or not row["reason"]):
            raise ValueError("duplicate or missing unexplained Stage11 owner history")
        seen.add(key)
    return {
        "scope":"A2R_COLD_GEOGRAPHIC_INTRINSIC_OCCURRENCE_JOIN_NOT_L3",
        "physical_frontiers_from_signed_visits":len(indexed),
        "direct_intrinsic_magnitudes_matched":len(matched),
        "matched_with_passability_cue":sum(indexed[k]["perceptual_passability_checked"] for k in matched),
        "historical_intrinsic_gaps":len(missing),
        "still_quarantined":total,
        "frontier_physical_admissibility_proven":False,
        "action_control_causal_mediation_proven":False,
        "study_admissible":False,
        "preregistered_mechanism_exposed":False,
        "general_L3":"NOT_ESTABLISHED",
    }
