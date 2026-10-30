"""Independent A2-R Stage8 Q/simulation -> Competition-evidence replay.

Consumes ONLY already authenticated M11 occurrences and a fully cold
reconstructed 12-feature Q replay. Calibration MUST come from a pristine
birth reconstructed from the pinned source, never the life report.

This validates the actual blending equation of Stage8, not merely that a
reported Stage8 evidence field was copied verbatim into Competition.
It DOES NOT prove that a changed motor decision was caused solely by Q,
nor establish a confirmatory exposure or a general L3 benefit.
"""
from __future__ import annotations

from math import isfinite, tanh
from i1_a2r_m11_cold import numeric

_REQUIRED = frozenset((
    "option_ref", "learning_signature", "status",
    "learned_value_status", "learned_value",
    "simulated_value_status", "simulated_value", "evidence",
    "equipment_version", "q_version",
))
_SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
_TOL = 2e-9


def _equal(left, right):
    a, b = numeric(left), numeric(right)
    return abs(a - b) <= _TOL * max(1.0, abs(a), abs(b))


def _calibration(calibration):
    if type(calibration) is not dict or set(calibration) != {
            "version", "n0", "evidence_scale", "extrinsic_gain"}:
        raise ValueError("missing pinned Stage8 blend configuration")
    if type(calibration["version"]) is not str or not calibration["version"]:
        raise ValueError("missing pinned Stage8 version")
    parameters = {k: numeric(calibration[k]) for k in (
        "n0", "evidence_scale", "extrinsic_gain")}
    if any(v <= 0 for v in parameters.values()):
        raise ValueError("invalid pinned Stage8 blending parameters")
    return parameters


def expected_stage8_evidence(data, *, update_count, calibration, td_version):
    """Recalculate exact I1 Stage8 output from two first-person valuations.

    The cumulative TD update count is reconstructed from the journal,
    never read from an operator-supplied indication in the Stage8 event.
    """
    p = _calibration(calibration)
    if (type(data) is not dict or not _REQUIRED <= set(data)
            or type(update_count) is not int or update_count < 0
            or type(td_version) is not str or not td_version
            or data["q_version"] != td_version
            or type(data["equipment_version"]) is not str
            or not data["equipment_version"]
            or type(data["option_ref"]) is not str or not data["option_ref"]
            or type(data["learning_signature"]) is not str
            or not data["learning_signature"]):
        raise ValueError("Stage8 evidence event not from frozen native schema")

    learned = data["learned_value_status"] == "learned"
    unlearned = data["learned_value_status"] == "unlearned"
    if not (learned or unlearned) or learned != (update_count > 0):
        raise ValueError("Stage8 learned Q status not justified by TD history")
    if learned:
        q = numeric(data["learned_value"])
    elif data["learned_value"] is not None:
        raise ValueError("unlearned Stage8 published a numeric Q")
    sim_status = data["simulated_value_status"]
    if sim_status not in ("computed", "unavailable"):
        raise ValueError("unknown Stage6 simulated value status")
    simulated = sim_status == "computed"
    if simulated:
        sim = numeric(data["simulated_value"])
    elif data["simulated_value"] is not None:
        raise ValueError("unavailable simulation published a numeric value")

    if not learned and not simulated:
        if data["status"] != "not_evaluated" or data["evidence"] is not None:
            raise ValueError("Stage8 no-Q/no-simulation must have no evidence")
        return None
    if data["status"] != "evaluated":
        raise ValueError("Stage8 returned unevaluated evidence despite Q/simulation")
    if learned and simulated:
        weight = update_count / (update_count + p["n0"])
        ext = weight * q + (1 - weight) * sim
    elif learned:
        ext = q
    else:
        ext = sim
    expected = max(-1., min(1., p["extrinsic_gain"] *
                             tanh(ext / p["evidence_scale"])))
    if not _equal(data["evidence"], expected):
        raise ValueError("published Stage8 evidence diverges from reconstructed Q/simulation")
    return expected


def attest_native_stage8(events, *, q_replay, calibration, td_version):
    """Reconcile every native Stage8 output against TD update chronology.

    The replay must already have been validated against the signed final M11
    TD owner. This function is not a signature checker; its input is expected
    from a separate cold ledger audit, not the birth's report.json.
    """
    _calibration(calibration)
    if (type(events) is not list or type(q_replay) is not dict
            or q_replay.get("scope") != _SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or q_replay.get("adaptive_learning_go") != "NOT_ESTABLISHED"
            or type(q_replay.get("stage8_observations")) is not list
            or type(q_replay.get("td_recurrences")) is not list):
        raise ValueError("Stage8 audit needs fully cold-verified native Q replay")

    published = {}
    for row in q_replay["stage8_observations"]:
        if type(row) is not dict:
            raise ValueError("malformed Q replay Stage8 observation")
        key = (row.get("step"), row.get("cycle"), row.get("option"))
        if (type(key[0]) is not int or type(key[1]) is not int
                or type(key[2]) is not str or key in published):
            raise ValueError("duplicated Stage8 key in cold Q replay")
        published[key] = row
    # A learned local affordance uses I1's 25% prior / 75% Q adapter,
    # NOT Stage8's ordinary Q-only equation. Native local occurrences
    # stay unverified until their separate source-born formula is checked.
    local_sources = set()
    for event in events:
        if type(event) is not dict:
            raise ValueError("malformed M11 event")
        if event.get("kind") not in (
                "i1_local_opportunity_proposed",
                "i1_unknown_affordance_proposed"):
            continue
        data = event.get("data")
        if type(data) is not dict:
            raise ValueError("malformed M11 affordance origin")
        key = (event.get("t_monde"), event.get("cycle"),
               data.get("option_ref"))
        if (type(key[0]) is not int or type(key[1]) is not int
                or type(key[2]) is not str or not key[2]
                or key in local_sources):
            raise ValueError("duplicated or invalid local affordance origin")
        local_sources.add(key)
    # The native Stage8 payload contains NO intrinsic_status/intrinsic_value.
    # Stage11 writes a separate provenance event only AFTER Competition
    # has processed Stage8's output. Treat that event as the source of
    # the intrinsic classification, never a missing Stage8 field.
    intrinsic_sources = set()
    stage8_positions = {}
    competition_positions = {}
    for position, event in enumerate(events):
        kind = event.get("kind")
        if kind not in ("stage8_option_evaluation", "competition_cycle",
                        "stage11_intrinsic_evaluation"):
            continue
        data = event.get("data")
        step, cycle = event.get("t_monde"), event.get("cycle")
        if type(step) is not int or type(cycle) is not int or type(data) is not dict:
            raise ValueError("invalid M11 Stage8/Competition/Stage11 occurrence")
        if kind == "competition_cycle":
            pair = (step, cycle)
            if pair in competition_positions:
                raise ValueError("duplicate native Competition occurrence")
            competition_positions[pair] = position
            continue
        option = data.get("option_ref")
        if type(option) is not str or not option:
            raise ValueError("invalid native intrinsic/Stage8 option")
        key = (step, cycle, option)
        if kind == "stage8_option_evaluation":
            if key in stage8_positions:
                raise ValueError("duplicate native Stage8 occurrence")
            stage8_positions[key] = position
        else:
            if key in intrinsic_sources:
                raise ValueError("duplicate native Stage11 intrinsic occurrence")
            intrinsic_sources.add(key)
            if (data.get("status") not in ("evaluated", "not_evaluated")
                    or type(data.get("signal_ids")) is not list
                    or type(data.get("intrinsic_producers")) is not list):
                raise ValueError("invalid Stage11 intrinsic provenance")
    for key in intrinsic_sources:
        step, cycle, _ = key
        if (key not in published or key not in stage8_positions
                or (step, cycle) not in competition_positions):
            raise ValueError("orphan Stage11 intrinsic evaluation")
        original = stage8_positions[key]
        competing = competition_positions[(step, cycle)]
        intrinsic_position = next(
            i for i, e in enumerate(events)
            if e.get("kind") == "stage11_intrinsic_evaluation"
            and (e.get("t_monde"), e.get("cycle"),
                 e["data"]["option_ref"]) == key)
        if not original < competing < intrinsic_position:
            raise ValueError("Stage11 intrinsic provenance is not after Competition")
        if key in local_sources:
            raise ValueError("local affordance was also credited as Stage11 intrinsic")

    td_by_step = {}
    for item in q_replay["td_recurrences"]:
        if type(item) is not dict or type(item.get("step")) is not int:
            raise ValueError("malformed cold TD recurrence")
        step = item["step"]
        if step in td_by_step:
            raise ValueError("duplicate TD update at same physical step")
        td_by_step[step] = item

    counts = {}
    observed = set()
    verified = learned_reads = blended_reads = 0
    td_seen = set()
    unsupported = []
    for event in events:
        if type(event) is not dict:
            raise ValueError("malformed authenticated M11 event")
        kind = event.get("kind")
        if kind == "td_update_published":
            t = event.get("t_monde")
            item = td_by_step.get(t)
            if item is None or t in td_seen:
                raise ValueError("unauthenticated TD update count")
            td_seen.add(t)
            signatures = item.get("signatures_updated")
            if (type(signatures) not in (tuple, list)
                    or len(signatures) != len(set(signatures))
                    or type(event.get("data")) is not dict
                    or list(signatures) != event["data"].get("updated_signatures")):
                raise ValueError("TD signature counts diverge from cold Q replay")
            for sig in signatures:
                if type(sig) is not str or not sig:
                    raise ValueError("invalid native TD signature")
                counts[sig] = counts.get(sig, 0) + 1
        elif kind == "stage8_option_evaluation":
            data = event.get("data")
            if type(data) is not dict:
                raise ValueError("invalid Stage8 journal payload")
            key = (event.get("t_monde"), event.get("cycle"),
                   data.get("option_ref"))
            row = published.get(key)
            if row is None or key in observed:
                raise ValueError("Stage8 event not matched to the cold Q replay")
            observed.add(key)
            signature = data.get("learning_signature")
            if (signature != row.get("signature")
                    or data.get("learned_value_status") != row.get("status")):
                raise ValueError("Stage8 evidence signature/status mismatches cold Q")
            if row.get("q") is None:
                if data.get("learned_value") is not None:
                    raise ValueError("Stage8 Q differs from independently replayed value")
            elif not _equal(row["q"], data.get("learned_value")):
                raise ValueError("Stage8 numeric Q differs from cold native Q")
            count = counts.get(signature, 0)
            # An already-learned local Q must never be mistaken for the
            # normal Stage8 Q-only formula; intrinsic/unidentified producers
            # cannot silently inherit a normal Stage8 verification either.
            is_local = key in local_sources
            is_intrinsic = key in intrinsic_sources
            other_family = (
                is_local or is_intrinsic
                or (data["status"] == "evaluated" and count == 0
                    and data["simulated_value_status"] != "computed")
            )
            if other_family:
                if data["status"] == "evaluated":
                    if data["evidence"] is None:
                        raise ValueError("unreplayed native evidence missing")
                    value = numeric(data["evidence"])
                    if not -1. <= value <= 1.:
                        raise ValueError("native evidence outside bounds")
                elif (data["status"] != "not_evaluated"
                      or data["evidence"] is not None or is_local):
                    raise ValueError("unreplayed native evidence/status invalid")
                family = ("local_affordance" if is_local else
                          "intrinsic_or_unknown" if is_intrinsic else
                          "external_adapter")
                unsupported.append({"step":key[0], "cycle":key[1],
                                    "option":key[2], "family":family,
                                    "stage11_separate_event":is_intrinsic})
            else:
                expected_stage8_evidence(
                    data, update_count=count,
                    calibration=calibration, td_version=td_version)
                learned_reads += count > 0
                blended_reads += (count > 0 and
                                  data["simulated_value_status"] == "computed")
                verified += 1

    if observed != set(published) or td_seen != set(td_by_step):
        raise ValueError("cold Q recurrence or Stage8 evidence missing from journal")
    if q_replay.get("q_update_counts") != counts:
        raise ValueError("final Q update-count map differs from Stage8 chronology")
    return {
        "scope": "A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3",
        "stage8_evaluations_recomputed": verified,
        "stage8_other_evaluations_unreplayed": len(unsupported),
        "stage8_other_evaluation_examples": unsupported[:8],
        "unreplayed_evaluations": unsupported,
        "all_native_evidence_recomputed": len(unsupported) == 0,
        "learned_q_reads_recomputed": learned_reads,
        "q_simulation_blends_recomputed": blended_reads,
        "stage11_post_competition_occurrences": len(intrinsic_sources),
        "td_updates_counted": len(td_seen),
        "same_full_m11_q_replay": True,
        "preregistered_mechanism_exposed": False,
        "general_L3": "NOT_ESTABLISHED",
    }
